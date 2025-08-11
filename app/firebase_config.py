import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

firebase_app: Optional[firebase_admin.App] = None

def initialize_firebase():
    global firebase_app
    
    if settings.FIREBASE_CREDENTIALS_PATH:
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            firebase_app = None
    else:
        logger.warning("Firebase credentials not provided")

def verify_firebase_token(id_token: str):
    if not firebase_app:
        raise Exception("Firebase is not initialized")
    
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise

def create_firebase_user(email: str, password: str, display_name: str):
    if not firebase_app:
        return None
    
    try:
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return user.uid
    except Exception as e:
        logger.error(f"Failed to create Firebase user: {e}")
        return None
