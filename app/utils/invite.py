import secrets

def generate_invite_code() -> str:
    """Generate a secure random invite code for organizations"""
    return secrets.token_urlsafe(16) 