import logging
from API.database import SessionLocal
from API.models import Account

logger = logging.getLogger("autoisp")

def update_account_status(account_id: int, status: str):
    """
    Update the status of an account in the database.
    """
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            old_status = account.status
            account.status = status
            db.commit()
            logger.info(f"Updated account {account_id} status: {old_status} -> {status}")
        else:
            logger.warning(f"Account {account_id} not found when trying to update status to {status}")
    except Exception as e:
        logger.error(f"Failed to update account {account_id} status: {e}")
    finally:
        db.close()
