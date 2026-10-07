"""Cloudflare R2 adapter for the provider-neutral M14 Content Pipeline.

The SDK is imported only when a configured live client is first needed. This
keeps offline tools independent of network access and makes credentials an
operator-process concern rather than serialized pipeline configuration.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from typing import Any

from .config import Environment, PRODUCTION_TARGET, STAGING_TARGET
from .provider import (
    PROVIDER_CONTRACT_VERSION,
    ProviderCapability,
    ProviderFeature,
    ProviderIdentity,
    ProviderObjectBytesResult,
    ProviderResult,
    ProviderResultCategory,
)
from .release_state import (
    ReleaseEvent,
    ReleaseState,
    replay_release_events,
    serialize_release_event,
)

R2_BUCKET = "scrubbots-content-prod"
R2_REGION = "auto"
_EVENTS_KEY = "_control/release-events/current.json"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
_ACCOUNT = re.compile(r"^[a-f0-9]{32}$")


def physical_object_key(environment: Environment, logical_key: str) -> str:
    """Map an unchanged provider-neutral object key into its locked namespace."""
    if not isinstance(environment, Environment) or not isinstance(logical_key, str):
        raise ValueError("invalid object identity")
    if (not _SAFE_KEY.fullmatch(logical_key) or "//" in logical_key
            or any(part in {".", ".."} for part in logical_key.split("/"))
            or logical_key.startswith(("staging/", "production/", "_control/"))):
        raise ValueError("invalid provider-neutral object key")
    prefix = "staging/" if environment is Environment.STAGING else "production/"
    return prefix + logical_key


def _event_from_dict(value: object) -> ReleaseEvent:
    if not isinstance(value, Mapping):
        raise ValueError("invalid release event")
    return ReleaseEvent(
        event_version=value["event_version"], sequence=value["sequence"],
        event_id=value["event_id"], transition_id=value["transition_id"],
        record_id=value["record_id"], content_id=value["content_id"],
        content_digest=value["content_digest"], environment=Environment(value["environment"]),
        from_state=ReleaseState(value["from_state"]) if value["from_state"] is not None else None,
        to_state=ReleaseState(value["to_state"]),
        expected_state=ReleaseState(value["expected_state"]) if value["expected_state"] is not None else None,
        previous_event_digest=value["previous_event_digest"],
        promotion_intent=value["promotion_intent"], source_record_id=value["source_record_id"],
        rollback_to_record_id=value["rollback_to_record_id"],
        rollback_to_content_id=value["rollback_to_content_id"],
        rollback_to_digest=value["rollback_to_digest"], event_digest=value["event_digest"],
    )


class CloudflareR2Provider:
    """S3-compatible R2 object provider; never exposes credentials in repr."""

    def __init__(self, *, client: Any | None = None, environ: Mapping[str, str] | None = None):
        self._env = dict(os.environ if environ is None else environ)
        self._client_override = client
        self._resolved_client: Any | None = None
        self._client_attempted = False

    def __repr__(self) -> str:
        return "CloudflareR2Provider(bucket='scrubbots-content-prod', credentials=redacted)"

    @property
    def identity(self) -> ProviderIdentity:
        return ProviderIdentity("cloudflare-r2", "1.0")

    @property
    def capabilities(self) -> ProviderCapability:
        features = (
            ProviderFeature.ATOMIC_MANIFEST_PUBLISH,
            ProviderFeature.CONDITIONAL_WRITE,
            ProviderFeature.INTEGRITY_VERIFY,
            ProviderFeature.OBJECT_WRITE,
            ProviderFeature.PRODUCTION_PROMOTION,
            ProviderFeature.STAGING_PUBLISH,
        )
        return ProviderCapability("cloudflare-r2-capabilities", "1.0",
                                  (Environment.PRODUCTION, Environment.STAGING), features)

    def _client(self) -> Any | None:
        if self._client_attempted:
            return self._resolved_client
        self._client_attempted = True
        endpoint = self._endpoint()
        access = self._env.get("R2_ACCESS_KEY_ID", "")
        secret = self._env.get("R2_SECRET_ACCESS_KEY", "")
        if not endpoint or not access or not secret:
            return None
        if self._client_override is not None:
            self._resolved_client = self._client_override
            return self._resolved_client
        try:
            import boto3
            from botocore.config import Config

            self._resolved_client = boto3.client(
                "s3", endpoint_url=endpoint, region_name=R2_REGION,
                aws_access_key_id=access, aws_secret_access_key=secret,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        except Exception:
            # SDK construction errors may contain endpoint or credential detail.
            return None
        return self._resolved_client

    def _endpoint(self) -> str | None:
        explicit = self._env.get("R2_ENDPOINT_URL", "").strip()
        if explicit:
            from urllib.parse import urlsplit

            parsed = urlsplit(explicit)
            if (parsed.scheme != "https" or not parsed.hostname
                    or parsed.username or parsed.password or parsed.query or parsed.fragment
                    or parsed.path not in ("", "/")
                    or not parsed.hostname.endswith(".r2.cloudflarestorage.com")):
                return None
            return f"https://{parsed.netloc}"
        account = self._env.get("R2_ACCOUNT_ID", "").strip().lower()
        return f"https://{account}.r2.cloudflarestorage.com" if _ACCOUNT.fullmatch(account) else None

    def _result(self, category: ProviderResultCategory, environment: Environment,
                digest: str | None = None) -> ProviderResult:
        return ProviderResult(PROVIDER_CONTRACT_VERSION, category, self.identity.provider_id,
                              environment, digest)

    @staticmethod
    def _error_category(exc: Exception) -> ProviderResultCategory:
        response = getattr(exc, "response", None)
        code = ""
        status = None
        if isinstance(response, Mapping):
            error = response.get("Error")
            metadata = response.get("ResponseMetadata")
            if isinstance(error, Mapping):
                code = str(error.get("Code", ""))
            if isinstance(metadata, Mapping):
                status = metadata.get("HTTPStatusCode")
        if code in {"PreconditionFailed", "ConditionalRequestConflict", "412"} or status == 412:
            return ProviderResultCategory.CONFLICT_STALE_PRECONDITION
        if code in {"AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch", "403"} or status == 403:
            return ProviderResultCategory.UNAVAILABLE
        if status == 404 or code in {"NoSuchKey", "NotFound", "404"}:
            return ProviderResultCategory.UNAVAILABLE
        return ProviderResultCategory.TRANSIENT_FAILURE

    def _get(self, physical_key: str) -> tuple[bytes, str] | None:
        client = self._client()
        if client is None:
            return None
        try:
            response = client.get_object(Bucket=R2_BUCKET, Key=physical_key)
        except Exception as exc:
            if _is_not_found(exc):
                return None
            raise
        body = response["Body"]
        data = body.read()
        etag = str(response.get("ETag", "")).strip('"')
        return data, etag

    def write_object_bytes(self, environment: Environment, object_key: str,
                           content_digest: str, content_bytes: bytes, *, if_absent: bool) -> ProviderResult:
        if (environment is not Environment.STAGING or if_absent is not True
                or type(content_bytes) is not bytes or not _SHA256.fullmatch(str(content_digest))
                or hashlib.sha256(content_bytes).hexdigest() != content_digest):
            return self._result(ProviderResultCategory.INVALID_REQUEST, environment if isinstance(environment, Environment) else Environment.STAGING)
        try:
            key = physical_object_key(environment, object_key)
        except ValueError:
            return self._result(ProviderResultCategory.INVALID_REQUEST, environment)
        client = self._client()
        if client is None:
            return self._result(ProviderResultCategory.UNAVAILABLE, environment)
        try:
            client.put_object(Bucket=R2_BUCKET, Key=key, Body=content_bytes,
                              ContentType=_content_type(object_key), CacheControl=_cache_control(object_key),
                              IfNoneMatch="*")
            return self._result(ProviderResultCategory.SUCCESS, environment, content_digest)
        except Exception as exc:
            return self._result(self._error_category(exc), environment)

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult:
        provider_id = self.identity.provider_id
        if self._client() is None:
            return ProviderObjectBytesResult(PROVIDER_CONTRACT_VERSION, ProviderResultCategory.UNAVAILABLE,
                                             provider_id, environment, object_key, None)
        try:
            key = physical_object_key(environment, object_key)
            stored = self._get(key)
            if stored is None:
                raise RuntimeError("provider unavailable")
            data, _ = stored
            return ProviderObjectBytesResult(PROVIDER_CONTRACT_VERSION, ProviderResultCategory.SUCCESS,
                                             provider_id, environment, object_key, data)
        except Exception as exc:
            return ProviderObjectBytesResult(PROVIDER_CONTRACT_VERSION, self._error_category(exc),
                                             provider_id, environment, object_key, None)

    def verify_object(self, environment: Environment, object_key: str,
                      expected_digest: str) -> ProviderResult:
        if not _SHA256.fullmatch(str(expected_digest)):
            return self._result(ProviderResultCategory.INVALID_REQUEST, environment)
        result = self.read_object_bytes(environment, object_key)
        if result.category is not ProviderResultCategory.SUCCESS or result.content_bytes is None:
            return self._result(result.category, environment)
        actual = hashlib.sha256(result.content_bytes).hexdigest()
        return self._result(ProviderResultCategory.SUCCESS if actual == expected_digest
                            else ProviderResultCategory.INTEGRITY_MISMATCH, environment, actual)

    def promote_object(self, source_environment: Environment, source_object_key: str,
                       target_environment: Environment, target_object_key: str,
                       expected_sha256: str) -> ProviderResult:
        if (source_environment is not Environment.STAGING or target_environment is not Environment.PRODUCTION
                or source_object_key != target_object_key or not _SHA256.fullmatch(str(expected_sha256))):
            return self._result(ProviderResultCategory.UNAUTHORIZED_REFERENCE,
                                target_environment if isinstance(target_environment, Environment) else Environment.PRODUCTION)
        try:
            source = physical_object_key(source_environment, source_object_key)
            target = physical_object_key(target_environment, target_object_key)
            source_bytes, source_etag = self._get(source) or (None, None)
            if source_bytes is None or hashlib.sha256(source_bytes).hexdigest() != expected_sha256:
                return self._result(ProviderResultCategory.INTEGRITY_MISMATCH, target_environment)
            client = self._client()
            if client is None:
                return self._result(ProviderResultCategory.UNAVAILABLE, target_environment)
            client.copy_object(Bucket=R2_BUCKET, Key=target,
                               CopySource={"Bucket": R2_BUCKET, "Key": source},
                               CopySourceIfMatch=source_etag, MetadataDirective="COPY",
                               IfNoneMatch="*")
            return self._result(ProviderResultCategory.SUCCESS, target_environment, expected_sha256)
        except Exception as exc:
            return self._result(self._error_category(exc), target_environment)

    def read_release_events(self) -> tuple[ReleaseEvent, ...]:
        stored = self._get(_EVENTS_KEY)
        if stored is None:
            return ()
        raw, _ = stored
        try:
            payload = json.loads(raw.decode("utf-8"))
            events = tuple(_event_from_dict(item) for item in payload["events"])
            if not replay_release_events(events).accepted:
                return ()
            return events
        except Exception:
            return ()

    def append_release_event(self, event: object, *, expected_prior_sequence: int,
                             expected_prior_event_digest: str) -> ProviderResult:
        if not isinstance(event, ReleaseEvent):
            return self._result(ProviderResultCategory.INVALID_REQUEST, Environment.PRODUCTION)
        client = self._client()
        if client is None:
            return self._result(ProviderResultCategory.UNAVAILABLE, Environment.PRODUCTION)
        try:
            current = self._get(_EVENTS_KEY)
            events = self.read_release_events()
            tip = events[-1].event_digest if events else "0" * 64
            if (len(events) != expected_prior_sequence or tip != expected_prior_event_digest
                    or event.sequence != expected_prior_sequence + 1
                    or not replay_release_events((*events, event)).accepted):
                return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                    Environment.PRODUCTION, tip)
            body = _canonical({"events": [json.loads(serialize_release_event(item))
                                           for item in (*events, event)]})
            kwargs: dict[str, object] = {"Bucket": R2_BUCKET, "Key": _EVENTS_KEY,
                                         "Body": body, "ContentType": "application/json",
                                         "CacheControl": "no-cache"}
            if current is None:
                kwargs["IfNoneMatch"] = "*"
            else:
                kwargs["IfMatch"] = current[1]
            client.put_object(**kwargs)
            return self._result(ProviderResultCategory.SUCCESS, Environment.PRODUCTION, event.event_digest)
        except Exception as exc:
            return self._result(self._error_category(exc), Environment.PRODUCTION)

    def write_manifest_conditionally(self, environment: Environment, target_id: str,
                                    object_key: str, content_digest: str, content_bytes: bytes, *,
                                    expected_prior_sha256: str | None,
                                    expected_prior_content_version: int | None = None,
                                    expected_release_state_sequence: int = 0,
                                    expected_release_state_tip_digest: str = "0" * 64,
                                    promotion_pending_event_digest: str = "") -> ProviderResult:
        if (type(content_bytes) is not bytes or hashlib.sha256(content_bytes).hexdigest() != content_digest
                or object_key != "manifests/current.json"):
            return self._result(ProviderResultCategory.INVALID_REQUEST, environment)
        staging = environment is Environment.STAGING and target_id == STAGING_TARGET.logical_target_id
        production = environment is Environment.PRODUCTION and target_id == PRODUCTION_TARGET.logical_target_id
        if not (staging or production):
            return self._result(ProviderResultCategory.UNAUTHORIZED_REFERENCE, environment)
        client = self._client()
        if client is None:
            return self._result(ProviderResultCategory.UNAVAILABLE, environment)
        try:
            key = physical_object_key(environment, object_key)
            prior = self._get(key)
            prior_bytes, etag = prior if prior is not None else (None, "")
            prior_digest = hashlib.sha256(prior_bytes).hexdigest() if prior_bytes is not None else None
            if prior_digest != expected_prior_sha256:
                return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION, environment, prior_digest)
            parsed = json.loads(content_bytes.decode("utf-8"))
            version = parsed.get("content_version")
            prior_version = None
            if prior_bytes is not None:
                try:
                    prior_version = json.loads(prior_bytes.decode("utf-8")).get("content_version")
                except Exception:
                    return self._result(ProviderResultCategory.INTEGRITY_MISMATCH, environment, prior_digest)
            if (type(version) is not int or (production and (
                    (prior_bytes is None and expected_prior_content_version is not None)
                    or (prior_bytes is not None and (type(expected_prior_content_version) is not int
                                                     or prior_version != expected_prior_content_version))
                    or (expected_prior_content_version is not None and version <= expected_prior_content_version)))):
                return self._result(ProviderResultCategory.INVALID_REQUEST, environment)
            if production:
                events = self.read_release_events()
                tip = events[-1].event_digest if events else "0" * 64
                if (len(events) != expected_release_state_sequence
                        or tip != expected_release_state_tip_digest
                        or not promotion_pending_event_digest
                        or tip != promotion_pending_event_digest):
                    return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION, environment, tip)
            kwargs: dict[str, object] = {"Bucket": R2_BUCKET, "Key": key, "Body": content_bytes,
                                         "ContentType": "application/json", "CacheControl": "no-cache"}
            kwargs["IfNoneMatch" if etag == "" else "IfMatch"] = "*" if etag == "" else etag
            client.put_object(**kwargs)
            return self._result(ProviderResultCategory.SUCCESS, environment, content_digest)
        except Exception as exc:
            return self._result(self._error_category(exc), environment)


def _content_type(key: str) -> str:
    return "application/octet-stream" if key.endswith(".scrubpack") else "application/json"


def _cache_control(key: str) -> str:
    return "public, max-age=31536000, immutable" if key.endswith(".scrubpack") else "no-cache, max-age=0, must-revalidate"


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8") + b"\n"


def _is_not_found(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    if not isinstance(response, Mapping):
        return False
    error = response.get("Error")
    metadata = response.get("ResponseMetadata")
    return ((isinstance(error, Mapping) and str(error.get("Code", "")) in {"NoSuchKey", "NotFound", "404"})
            or (isinstance(metadata, Mapping) and metadata.get("HTTPStatusCode") == 404))


__all__ = ["CloudflareR2Provider", "R2_BUCKET", "R2_REGION", "physical_object_key"]
