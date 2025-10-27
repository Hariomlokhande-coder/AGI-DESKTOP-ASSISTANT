"""Session management for recordings."""
import json
from datetime import datetime
from ..utils.helpers import get_timestamp, save_json, load_json
from ..error_handling.logger import logger


class SessionManager:
    """Manages recording sessions."""
    
    def __init__(self, storage):
        self.storage = storage
        self.current_session = None
        self.sessions_file = storage.get_processed_file_path('sessions.json')
        self.sessions = self._load_sessions()
    
    def _load_sessions(self):
        """Load previous sessions."""
        data = load_json(self.sessions_file)
        return data if data else []
    
    def _save_sessions(self):
        """Save sessions to file."""
        save_json(self.sessions, self.sessions_file)
    
    def create_session(self):
        """Create a new recording session."""
        session_id = get_timestamp()
        self.current_session = {
            'id': session_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': 0,
            'recordings': [],
            'processed': False,
            'workflows_detected': []
        }
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def end_session(self):
        """End current recording session."""
        if self.current_session:
            self.current_session['end_time'] = datetime.now().isoformat()
            
            # Calculate duration
            start = datetime.fromisoformat(self.current_session['start_time'])
            end = datetime.fromisoformat(self.current_session['end_time'])
            self.current_session['duration'] = (end - start).total_seconds()
            
            # Save session
            self.sessions.append(self.current_session)
            self._save_sessions()
            
            logger.info(f"Ended session: {self.current_session['id']}")
            session_id = self.current_session['id']
            self.current_session = None
            return session_id
        return None
    
    def add_recording(self, recording_path):
        """Add recording to current session."""
        if self.current_session:
            self.current_session['recordings'].append(recording_path)
    
    def add_workflows(self, workflows):
        """Add detected workflows to current session."""
        if self.current_session:
            self.current_session['workflows_detected'].extend(workflows)
    
    def mark_processed(self, session_id):
        """Mark session as processed."""
        for session in self.sessions:
            if session['id'] == session_id:
                session['processed'] = True
                self._save_sessions()
                logger.info(f"Session {session_id} marked as processed")
                break
    
    def get_session(self, session_id):
        """Get session by ID."""
        for session in self.sessions:
            if session['id'] == session_id:
                return session
        return None
    
    def get_recent_sessions(self, count=10):
        """Get recent sessions."""
        return self.sessions[-count:] if len(self.sessions) > count else self.sessions
