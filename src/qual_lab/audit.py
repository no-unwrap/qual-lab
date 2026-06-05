from __future__ import annotations

from datetime import datetime, timezone

from qual_lab.models import AuditEvent, AuditResult, SensitivityLevel


def build_audit_event(
    *,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str,
    sensitivity: SensitivityLevel,
    result: AuditResult = AuditResult.SUCCESS,
    details: str | None = None,
) -> AuditEvent:
    return AuditEvent(
        timestamp=datetime.now(timezone.utc),
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        sensitivity=sensitivity,
        result=result,
        details=details,
    )
