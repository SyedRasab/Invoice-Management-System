from database import get_session
from models import AuditLog
import json

def log_action(user, action, entity_type, entity_id, details=None):
    """Log an action to the audit log"""
    session = get_session()
    try:
        log = AuditLog(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(details) if details else None
        )
        session.add(log)
        session.commit()
    except Exception as e:
        print(f"Error logging action: {e}")
    finally:
        session.close()

def get_audit_trail(entity_type=None, entity_id=None):
    """Get audit trail, optionally filtered by entity"""
    session = get_session()
    try:
        query = session.query(AuditLog)
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
            
        logs = query.order_by(AuditLog.timestamp.desc()).all()
        return [log.to_dict() for log in logs]
    finally:
        session.close()
