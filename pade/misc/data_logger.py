import csv
import os
import json
import fcntl
from datetime import datetime
from pathlib import Path


def get_shared_session_id(default=None):
    """Return the runtime session id when available, otherwise fall back."""
    runtime_session_id = os.getenv("PADE_SESSION_ID")
    if runtime_session_id:
        return runtime_session_id
    if default is not None:
        return default
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class DataLogger:
    """Simple CSV-based data logger to replace database functionality."""

    SESSIONS_HEADER = ['timestamp', 'session_id', 'name', 'state']
    AGENTS_HEADER = ['timestamp', 'agent_id', 'session_id', 'name', 'state']
    MESSAGES_HEADER = [
        'timestamp', 'message_id', 'conversation_id', 'agent_id',
        'performative', 'protocol', 'sender', 'receivers',
        'content', 'ontology', 'language'
    ]
    EVENTS_HEADER = ['timestamp', 'event_type', 'agent_id', 'data']
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Different CSV files for different types of data
        self.sessions_file = self.log_dir / "sessions.csv"
        self.agents_file = self.log_dir / "agents.csv"
        self.messages_file = self.log_dir / "messages.csv"
        self.events_file = self.log_dir / "events.csv"
        
        # Initialize CSV files with headers if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize CSV files with headers."""
        # Sessions
        if not self.sessions_file.exists():
            with open(self.sessions_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.SESSIONS_HEADER)
        
        # Agents
        if not self.agents_file.exists():
            with open(self.agents_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.AGENTS_HEADER)
        
        # Messages
        if not self.messages_file.exists():
            with open(self.messages_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.MESSAGES_HEADER)
        
        # Events
        if not self.events_file.exists():
            with open(self.events_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.EVENTS_HEADER)

    def _upsert_agent_row(self, row):
        """Keep a single agent record per agent/session pair across processes."""
        with open(self.agents_file, 'r+', newline='', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.seek(0)
            reader = csv.DictReader(f)
            rows = list(reader)

            updated = False
            for existing in rows:
                if (
                    existing.get('agent_id') == row['agent_id']
                    and existing.get('session_id') == row['session_id']
                ):
                    existing.update(row)
                    updated = True
                    break

            if not updated:
                rows.append(row)

            f.seek(0)
            f.truncate()

            writer = csv.DictWriter(f, fieldnames=self.AGENTS_HEADER)
            writer.writeheader()
            writer.writerows(rows)
            f.flush()
            os.fsync(f.fileno())
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def log_session(self, session_id, name, state):
        """Log a session."""
        session_id = get_shared_session_id(session_id)
        timestamp = datetime.now().isoformat()
        with open(self.sessions_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, session_id, name, state])
    
    def log_agent(self, agent_id, session_id, name, state):
        """Log an agent."""
        session_id = get_shared_session_id(session_id)
        self._upsert_agent_row({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'session_id': session_id,
            'name': name,
            'state': state,
        })
    
    def log_message(self, message_id, conversation_id, agent_id, performative,
                    protocol, sender, receivers, content, ontology, language):
        """Log a message."""
        timestamp = datetime.now().isoformat()
        
        # Convert receivers list to string if needed
        if isinstance(receivers, list):
            receivers = ';'.join(receivers)
        
        with open(self.messages_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, message_id, conversation_id, agent_id,
                performative, protocol, sender, receivers,
                str(content), ontology or '', language or ''
            ])
    
    def log_event(self, event_type, agent_id=None, data=None):
        """Log a general event."""
        timestamp = datetime.now().isoformat()
        with open(self.events_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_type, agent_id or '', str(data) or ''])
    
    def get_messages(self, limit=None):
        """Retrieve messages (simple implementation)."""
        messages = []
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append(row)
        
        if limit:
            return messages[-limit:]
        return messages

# Singleton instance
logger = DataLogger()
