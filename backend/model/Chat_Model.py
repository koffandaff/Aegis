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
# Pydantic Schemas
# ========================
