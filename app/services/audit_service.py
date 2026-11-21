from sqlalchemy.orm import Session

from app.models import AuditLog


def record_action(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    details: str,
    success: bool = True,
) -> AuditLog:
    log_entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details,
        success=success,
    )
    db.add(log_entry)
    db.flush()
    return log_entry
