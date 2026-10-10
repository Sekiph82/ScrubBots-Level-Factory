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
_MANIFEST_HISTORY_KEY = "_control/manifest-history/current.json"
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
_ACCOUNT = re.compile(r"^[a-f0-9]{32}$")


class ReleaseLedgerUnavailableError(RuntimeError):
    """The remote ledger could not be read, so its state is unknown."""


class InvalidReleaseLedgerError(RuntimeError):
    """An existing remote ledger is malformed or fails replay validation."""


class ManifestHistoryUnavailableError(RuntimeError):
    """The canonical M13 manifest history could not be read or verified."""


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
        secret_value = self._env.get("R2_SECRET_ACCESS_KEY", "")
        if (not endpoint or not _valid_credential(access, 128)
                or not _valid_credential(secret_value, 256)):
            return None
        if self._client_override is not None:
            self._resolved_client = self._client_override
            return self._resolved_client
        try:
            import boto3
            from botocore.config import Config

            self._resolved_client = boto3.client(
                "s3", endpoint_url=endpoint, region_name=R2_REGION,
                aws_access_key_id=access, aws_secret_access_key=secret_value,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        except Exception:
            # SDK construction errors may contain endpoint or credential detail.
            return None
        return self._resolved_client

    def _endpoint(self) -> str | None:
        explicit = self._env.get("R2_ENDPOINT_URL", "").strip()
        if explicit:
            match = re.fullmatch(
                r"https://([a-f0-9]{32}(?:\.(?:eu|fedramp|us))?\.r2\.cloudflarestorage\.com)/?",
                explicit, re.IGNORECASE,
            )
            if match is None:
                return None
            return f"https://{match.group(1).lower()}"
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
            client = self._client()
            if client is None:
                return self._result(ProviderResultCategory.UNAVAILABLE, target_environment)
            source_stored = self._get(source)
            source_bytes = source_stored[0] if source_stored is not None else None
            if source_bytes is None or hashlib.sha256(source_bytes).hexdigest() != expected_sha256:
                return self._result(ProviderResultCategory.INTEGRITY_MISMATCH, target_environment)
            target_stored = self._get(target)
            if target_stored is not None:
                target_bytes = target_stored[0]
                if (len(target_bytes) == len(source_bytes) and target_bytes == source_bytes
                        and hashlib.sha256(target_bytes).hexdigest() == expected_sha256):
                    return self._result(ProviderResultCategory.SUCCESS, target_environment, expected_sha256)
                return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                    target_environment, hashlib.sha256(target_bytes).hexdigest())
            # Read then conditional PutObject avoids R2's beta-only CopyObject
            # destination conditionals while retaining immutable destination semantics.
            client.put_object(Bucket=R2_BUCKET, Key=target, Body=source_bytes,
                              ContentType=_content_type(target_object_key),
                              CacheControl=_cache_control(target_object_key), IfNoneMatch="*")
            return self._result(ProviderResultCategory.SUCCESS, target_environment, expected_sha256)
        except Exception as exc:
            if (_is_not_found(exc)
                    or self._error_category(exc) is ProviderResultCategory.CONFLICT_STALE_PRECONDITION):
                # A concurrent writer may have won the conditional create. Only
                # exact target bytes satisfy this retry; every other state conflicts.
                try:
                    target_stored = self._get(target)
                    if target_stored is not None:
                        target_bytes = target_stored[0]
                        if (target_bytes == source_bytes and len(target_bytes) == len(source_bytes)
                                and hashlib.sha256(target_bytes).hexdigest() == expected_sha256):
                            return self._result(ProviderResultCategory.SUCCESS, target_environment,
                                                expected_sha256)
                        return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                            target_environment, hashlib.sha256(target_bytes).hexdigest())
                except Exception:
                    return self._result(ProviderResultCategory.TRANSIENT_FAILURE, target_environment)
            return self._result(self._error_category(exc), target_environment)

    def read_release_events(self) -> tuple[ReleaseEvent, ...]:
        if self._client() is None:
            raise ReleaseLedgerUnavailableError("release ledger unavailable")
        try:
            stored = self._get(_EVENTS_KEY)
        except Exception as exc:
            raise ReleaseLedgerUnavailableError("release ledger unavailable") from exc
        if stored is None:
            return ()
        raw, _ = stored
        return self._parse_release_events(raw)

    def read_manifest_history(self):
        """Read and verify the canonical M13 exact-byte production history."""
        from .manifest_history import ManifestHistoryV1, parse_manifest_history

        if self._client() is None:
            raise ManifestHistoryUnavailableError("manifest history unavailable")
        try:
            stored = self._get(_MANIFEST_HISTORY_KEY)
            if stored is None:
                return ManifestHistoryV1()
            return parse_manifest_history(stored[0])
        except Exception as exc:
            raise ManifestHistoryUnavailableError("manifest history unavailable") from exc

    def write_manifest_history(self, history, *, expected_prior_tip_sha256: str | None,
                               current_manifest_bytes: bytes) -> ProviderResult:
        """CAS-write exact M13 history only after exact production readback."""
        from .manifest_history import (
            ManifestHistoryError, ManifestHistoryV1, parse_manifest_history, serialize_manifest_history,
            verify_manifest_history,
        )

        if (not isinstance(history, ManifestHistoryV1) or not history.records
                or type(current_manifest_bytes) is not bytes
                or history.records[-1].manifest_bytes != current_manifest_bytes
                or not verify_manifest_history(history).accepted):
            return self._result(ProviderResultCategory.INVALID_REQUEST, Environment.PRODUCTION)
        client = self._client()
        if client is None:
            return self._result(ProviderResultCategory.UNAVAILABLE, Environment.PRODUCTION)
        try:
            manifest_stored = self._get("production/manifests/current.json")
            if manifest_stored is None or manifest_stored[0] != current_manifest_bytes:
                return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                    Environment.PRODUCTION)
            current = self._get(_MANIFEST_HISTORY_KEY)
            if current is None:
                prior = ManifestHistoryV1()
                if expected_prior_tip_sha256 is not None:
                    return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                        Environment.PRODUCTION)
                kwargs: dict[str, object] = {"IfNoneMatch": "*"}
            else:
                prior = parse_manifest_history(current[0])
                if prior.tip_sha256 != expected_prior_tip_sha256:
                    return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                        Environment.PRODUCTION, prior.tip_sha256)
                kwargs = {"IfMatch": current[1]}
            if (history.records[:-1] != prior.records
                    or prior.tip_sha256 != expected_prior_tip_sha256):
                return self._result(ProviderResultCategory.CONFLICT_STALE_PRECONDITION,
                                    Environment.PRODUCTION, prior.tip_sha256)
            body = serialize_manifest_history(history)
            client.put_object(Bucket=R2_BUCKET, Key=_MANIFEST_HISTORY_KEY, Body=body,
                              ContentType="application/json", CacheControl="no-cache", **kwargs)
            return self._result(ProviderResultCategory.SUCCESS, Environment.PRODUCTION,
                                history.tip_sha256)
        except ManifestHistoryError:
            return self._result(ProviderResultCategory.INTEGRITY_MISMATCH, Environment.PRODUCTION)
        except Exception as exc:
            return self._result(self._error_category(exc), Environment.PRODUCTION)

    def append_release_event(self, event: object, *, expected_prior_sequence: int,
                             expected_prior_event_digest: str) -> ProviderResult:
        if not isinstance(event, ReleaseEvent):
            return self._result(ProviderResultCategory.INVALID_REQUEST, Environment.PRODUCTION)
        client = self._client()
        if client is None:
            return self._result(ProviderResultCategory.UNAVAILABLE, Environment.PRODUCTION)
        try:
            current = self._get(_EVENTS_KEY)
            events = self._parse_release_events(current[0]) if current is not None else ()
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
            if isinstance(exc, InvalidReleaseLedgerError):
                return self._result(ProviderResultCategory.INTEGRITY_MISMATCH, Environment.PRODUCTION)
            if isinstance(exc, ReleaseLedgerUnavailableError):
                return self._result(ProviderResultCategory.UNAVAILABLE, Environment.PRODUCTION)
            return self._result(self._error_category(exc), Environment.PRODUCTION)

    @staticmethod
    def _parse_release_events(raw: bytes) -> tuple[ReleaseEvent, ...]:
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict) or set(payload) != {"events"} or not isinstance(payload["events"], list):
                raise ValueError("invalid release ledger envelope")
            events = tuple(_event_from_dict(item) for item in payload["events"])
            if (not replay_release_events(events).accepted
                    or raw != _canonical({"events": [json.loads(serialize_release_event(item))
                                                       for item in events]})):
                raise ValueError("invalid release ledger history")
            return events
        except Exception as exc:
            raise InvalidReleaseLedgerError("release ledger invalid") from exc

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


def _valid_credential(value: object, max_length: int) -> bool:
    return (isinstance(value, str) and 16 <= len(value) <= max_length
            and all(0x21 <= ord(character) <= 0x7e for character in value))


__all__ = ["CloudflareR2Provider", "R2_BUCKET", "R2_REGION", "physical_object_key"]
