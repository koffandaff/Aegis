"""
Chat Models and Database for AI Chatbot Feature
Uses Ollama with Koffan/Cybiz:latest model
"""
import json
import os
import uuid
import shutil
import tempfile
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========================
# Pydantic Schemas
# ========================

class ChatMessage(BaseModel):
    """Individual chat message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


class ChatSession(BaseModel):
    """Chat session with message history"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "New Chat"
    messages: List[ChatMessage] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


class ChatRequest(BaseModel):
    """Request to send a message"""
    session_id: Optional[str] = None  # If None, create new session
    message: str


class ChatSessionResponse(BaseModel):
    """Response for session info (without full messages)"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatSessionDetail(BaseModel):
    """Full session with messages"""
    id: str
    title: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# ========================
# JSON File Database
# ========================

class ChatDatabase:
    def __init__(self, db_path: str = "data/chat_sessions.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._atomic_save({"sessions": []})
    
    def _load_data(self) -> Dict:
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            
            # Migration: Ensure all messages have IDs
            modified = False
            for session in data.get("sessions", []):
                # Migrate timestamps to UTC (append Z)
                if not session.get("created_at", "").endswith("Z"):
                    session["created_at"] = session.get("created_at", datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
                    modified = True
                if not session.get("updated_at", "").endswith("Z"):
                    session["updated_at"] = session.get("updated_at", datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
                    modified = True
                    
                for msg in session.get("messages", []):
                    if "id" not in msg:
                        msg["id"] = str(uuid.uuid4())
                        modified = True
                    if not msg.get("timestamp", "").endswith("Z"):
                        msg["timestamp"] = msg.get("timestamp", datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
                        modified = True
            
            if modified:
                self._atomic_save(data)
                
            return data
        except Exception as e:
            print(f"Error loading chat database: {e}")
            return {"sessions": []}
    
    def _atomic_save(self, data: Dict):
        """Save data atomically using temp file to prevent locking issues"""
        dir_name = os.path.dirname(self.db_path)
        
        # Create temp file in same directory
        with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, indent=2, default=str)
            temp_name = tf.name
        
        try:
            # Atomic rename
            shutil.move(temp_name, self.db_path)
        except Exception as e:
            print(f"Error saving chat database: {e}")
            if os.path.exists(temp_name):
                os.remove(temp_name)
    
    # Session Operations
    
    def create_session(self, user_id: str, initial_message: str = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(user_id=user_id)
        
        if initial_message:
            session.messages.append(ChatMessage(role="user", content=initial_message))
            # Generate title from first message (first 30 chars)
            session.title = initial_message[:30] + "..." if len(initial_message) > 30 else initial_message
        
        data = self._load_data()
        data["sessions"].append(session.dict())
        self._atomic_save(data)
        
        return session
    
    def get_user_sessions(self, user_id: str) -> List[ChatSessionResponse]:
        """Get all sessions for a user (summary only)"""
        data = self._load_data()
        user_sessions = [s for s in data["sessions"] if s.get("user_id") == user_id]
        
        # Sort by updated_at descending (most recent first)
        user_sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return [
            ChatSessionResponse(
                id=s["id"],
                title=s.get("title", "Untitled"),
                created_at=s.get("created_at", datetime.now(timezone.utc)),
                updated_at=s.get("updated_at", datetime.now(timezone.utc)),
                message_count=len(s.get("messages", []))
            )
            for s in user_sessions
        ]
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get specific session with full message history"""
        data = self._load_data()
        
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                return ChatSession(**s)
        
        return None
    
    def add_message(self, session_id: str, user_id: str, role: str, content: str) -> bool:
        """Add a message to a session"""
        data = self._load_data()
        
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                message = ChatMessage(role=role, content=content)
                s["messages"].append(message.dict())
                s["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                
                # Update title if this is the first user message
                if role == "user" and len([m for m in s["messages"] if m["role"] == "user"]) == 1:
                    s["title"] = content[:30] + "..." if len(content) > 30 else content
                
                self._atomic_save(data)
                return True
        
        return False

    def edit_message(self, session_id: str, user_id: str, message_id: str, new_content: str) -> Optional[List[Dict]]:
        """
        Edit a message content and remove subsequent messages to allow regeneration.
        Returns the updated message list (up to the edited message) or None if failed.
        """
        data = self._load_data()
        
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                messages = s["messages"]
                # Find index of message to edit
                edit_index = next((i for i, m in enumerate(messages) if m.get("id") == message_id), -1)
                
                if edit_index != -1 and messages[edit_index]["role"] == "user":
                    # Update content
                    messages[edit_index]["content"] = new_content
                    # Truncate all messages after this one
                    s["messages"] = messages[:edit_index + 1]
                    s["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    
                    self._atomic_save(data)
                    return s["messages"]
                    
        return None
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session"""
        data = self._load_data()
        original_length = len(data["sessions"])
        
        data["sessions"] = [
            s for s in data["sessions"] 
            if not (s["id"] == session_id and s.get("user_id") == user_id)
        ]
        
        if len(data["sessions"]) < original_length:
            self._atomic_save(data)
            return True
        
        return False
    
    def update_session_title(self, session_id: str, user_id: str, new_title: str) -> bool:
        """Update the title of a session"""
        data = self._load_data()
        for s in data["sessions"]:
            if s["id"] == session_id and s.get("user_id") == user_id:
                s["title"] = new_title
                s["updated_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                self._atomic_save(data)
                return True
        return False
    
    def get_context_messages(self, session_id: str, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context (Ollama format)"""
        session = self.get_session(session_id, user_id)
        
        if not session:
            return []
        
        # Get last N messages
        recent = session.messages[-limit:]
        
        return [{"role": m.role, "content": m.content} for m in recent]
    
    def get_global_stats(self) -> Dict[str, int]:
        """Get global chat statistics for admin panel"""
        data = self._load_data()
        sessions = data.get("sessions", [])
        
        total_sessions = len(sessions)
        total_messages = sum(len(s.get("messages", [])) for s in sessions)
        unique_users = len(set(s.get("user_id") for s in sessions if s.get("user_id")))
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_users": unique_users
        }


# Global database instance
chat_db = ChatDatabase()
