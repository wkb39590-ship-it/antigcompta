from sqlalchemy.orm import Session
from models import ActionLog, Agent
import logging

logger = logging.getLogger(__name__)

def log_action(db: Session, agent: Agent, action_type: str, entity_type: str, entity_id: int = None, details: str = None):
    """
    Enregistre une action dans l'historique (Audit Trail).
    L'agent peut être None si l'action est automatique ou système.
    """
    try:
        log = ActionLog(
            cabinet_id=agent.cabinet_id if agent else None,
            agent_id=agent.id if agent else None,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"[ERROR LOGGING] Failed to log action {action_type} for {entity_type}: {str(e)}")
        db.rollback()
