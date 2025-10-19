from flask import current_app

def is_admin_email(email: str) -> bool:
    """Checks if email belongs to admin domain"""

    if not email or '@' not in email:
        return False
    
    try:
        domain = email.split('@')[-1].lower()
        admin_domains = current_app.config.get('ADMIN_DOMAINS', [])
        return domain in [d.lower() for d in admin_domains]
    except Exception:
        return False