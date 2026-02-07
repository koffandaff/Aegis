"""
Chat Repository - Database operations for chat sessions and messages
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.repositories.base import BaseRepository
from database.models import ChatSession, ChatMessage


class ChatRepository(BaseRepository[ChatSession]):
    """
    Repository for ChatSession and ChatMessage operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    # ==================== Session Operations ====================
    
    def create_session(self, user_id: str, title: str = "New Chat") -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user with message counts"""
        from sqlalchemy import func
        
        # Get sessions with message counts in one query
        results = (
            self.db.query(ChatSession, func.count(ChatMessage.id).label("message_count"))
            .outerjoin(ChatMessage)
            .filter(ChatSession.user_id == user_id)
            .group_by(ChatSession.id)
            .order_by(desc(ChatSession.updated_at))
            .all()
        )
        
        sessions = []
        for session, count in results:
            sessions.append({
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": count
            })
        return sessions
    
    def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get specific session with full message history"""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    def update_session_title(self, session_id: str, user_id: str, new_title: str) -> bool:
        """Update the title of a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
            
        session.title = new_title
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    # ==================== Message Operations ====================
    
    def add_message(self, session_id: str, user_id: str, role: str, content: str) -> Optional[ChatMessage]:
        """Add a message to a session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return None
            
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Update session title if this is the first user message
        user_messages_count = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "user"
        ).count()
        
        if role == "user" and user_messages_count == 0:
            session.title = content[:30] + "..." if len(content) > 30 else content
            
        session.updated_at = datetime.now(timezone.utc)
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def edit_message(self, session_id: str, user_id: str, message_id: str, new_content: str) -> bool:
        """
        Edit a message content and remove subsequent messages.
        """
        session = self.get_session(session_id, user_id)
        if not session:
            return False
            
        # Find the message
        message = self.db.query(ChatMessage).filter(
            ChatMessage.id == message_id,
            ChatMessage.session_id == session_id
        ).first()
        
        if not message or message.role != "user":
            return False
            
        # Update content
        message.content = new_content
        
        # Remove subsequent messages
        self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id,
            ChatMessage.timestamp > message.timestamp
        ).delete()
        
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def get_context_messages(self, session_id: str, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context (Ollama format)"""
        session = self.get_session(session_id, user_id)
        if not session:
            return []
            
        # SQLAlchemy relationship handles fetching messages
        # Sort by timestamp to be sure
        messages = sorted(session.messages, key=lambda x: x.timestamp)
        recent = messages[-limit:]
        
        return [{"role": m.role, "content": m.content} for m in recent]
