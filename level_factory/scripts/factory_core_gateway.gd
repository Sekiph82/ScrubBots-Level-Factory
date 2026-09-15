class_name FactoryCoreGateway
extends RefCounted

## Status-only boundary for the canonical Python Factory Core.
##
## This foundation deliberately does not invoke a process, read a workspace,
## access a provider, or manufacture a successful status. A later audited
## integration may replace the status source while keeping this contract.

enum ConnectionStatus {
	AVAILABLE,
	UNAVAILABLE,
	ERROR,
}

const CURRENT_STATUS: ConnectionStatus = ConnectionStatus.UNAVAILABLE


func status_name() -> String:
	return ConnectionStatus.keys()[CURRENT_STATUS]


func status_message() -> String:
	return "UNAVAILABLE — canonical Python Factory Core is not connected in this migration foundation."


func capability_summary() -> String:
	return "Status-only boundary; no generation, solving, validation, metrics, provider, or network capability is exposed."
