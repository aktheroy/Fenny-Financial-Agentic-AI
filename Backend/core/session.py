import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from config import settings

logger = logging.getLogger(__name__)


class Session:
    """Represents a user conversation session"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.file_count = 0
        self.messages = []

    def update_activity(self):
        """Update the last active timestamp"""
        self.last_active = datetime.utcnow()

    def add_files(self, num_files: int) -> int:
        """Add files to the session and return new file count"""
        self.file_count += num_files
        self.update_activity()
        return self.file_count

    def get_file_count(self) -> int:
        """Get current file count"""
        return self.file_count


class SessionManager:
    """Manages user sessions"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session = Session(session_id)
        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        # Check if session has expired
        expiry_time = session.created_at + timedelta(
            hours=settings.SESSION_EXPIRY_HOURS
        )
        if datetime.utcnow() > expiry_time:
            self.delete_session(session_id)
            return None

        session.update_activity()
        return session

    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired_sessions = [
            sid
            for sid, session in self.sessions.items()
            if now > session.created_at + timedelta(hours=settings.SESSION_EXPIRY_HOURS)
        ]

        for sid in expired_sessions:
            self.delete_session(sid)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


# Global session manager instance
session_manager = SessionManager()
