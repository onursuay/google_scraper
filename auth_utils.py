"""User authentication — Supabase `users` table + bcrypt."""
import logging
import bcrypt
from marketing.db import sb_select, sb_insert, sb_update

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def get_user_by_email(email: str) -> dict | None:
    try:
        rows = sb_select("users", {"email": f"eq.{email.lower().strip()}", "select": "*"})
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"get_user_by_email: {e}")
        return None


def get_user_by_id(user_id: str) -> dict | None:
    try:
        rows = sb_select("users", {"id": f"eq.{user_id}", "select": "*"})
        return rows[0] if rows else None
    except Exception as e:
        logger.warning(f"get_user_by_id: {e}")
        return None


def create_user(name: str, email: str, company: str = "", phone: str = "", password: str = "") -> dict:
    if get_user_by_email(email):
        return {"error": "Bu e-posta adresi zaten kayıtlı."}
    try:
        rows = sb_insert("users", {
            "full_name":     name.strip(),
            "email":         email.lower().strip(),
            "password_hash": hash_password(password),
            "company":       company.strip(),
            "phone":         phone.strip(),
        })
        return rows[0] if rows else {"error": "Kayıt oluşturulamadı."}
    except Exception as e:
        logger.error(f"create_user: {e}")
        return {"error": "Kayıt sırasında bir hata oluştu."}


def update_user(user_id: str, data: dict) -> dict:
    from datetime import datetime, timezone
    allowed = {"full_name", "company", "phone"}
    payload = {k: v for k, v in data.items() if k in allowed}
    if not payload:
        return {}
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        rows = sb_update("users", {"id": f"eq.{user_id}"}, payload)
        return rows[0] if rows else {}
    except Exception as e:
        logger.error(f"update_user: {e}")
        return {}


def update_password(user_id: str, new_password: str) -> bool:
    from datetime import datetime, timezone
    try:
        sb_update("users", {"id": f"eq.{user_id}"}, {
            "password_hash": hash_password(new_password),
            "updated_at":    datetime.now(timezone.utc).isoformat(),
        })
        return True
    except Exception:
        return False


def get_initials(name: str) -> str:
    parts = (name or "?").strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    s = name.strip()
    return (s[:2] if len(s) >= 2 else s + "?")[:2].upper()
