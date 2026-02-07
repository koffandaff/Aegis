"""
Chat Router - SQLite Version

Protected API endpoints for AI Chatbot.
Uses Server-Sent Events (SSE) for streaming responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from model.Chat_Model import ChatRequest, ChatSessionResponse, ChatSessionDetail
from service.Chat_Service import ChatService
from database.engine import get_db
from database.repositories.chat_repository import ChatRepository
from routers.dependencies import get_current_user

router = APIRouter()


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Get ChatService with database session"""
    return ChatService(db, ChatRepository(db))


# ========================
# Session Endpoints
# ========================

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all chat sessions for the current user"""
    sessions = chat_service.get_user_sessions(current_user["id"])
    return sessions


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new empty chat session"""
    session = chat_service.create_session(current_user["id"])
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session.messages)
    )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get a specific chat session with all messages"""
    session = chat_service.get_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "title": session.title,
        "messages": [
            {
                "id": m.id,  # Include ID
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat() if hasattr(m.timestamp, 'isoformat') else str(m.timestamp)
            }
            for m in session.messages
        ],
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session"""
    deleted = chat_service.delete_session(session_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


class UpdateTitleRequest(BaseModel):
    title: str


@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str, 
    request: UpdateTitleRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update chat session title"""
    updated = chat_service.update_session_title(session_id, current_user["id"], request.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Title updated successfully"}


# ========================
# Chat Endpoint (SSE Streaming)
# ========================

class SendMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a message and receive streaming response via SSE.
    If session_id is None, a new session will be created.
    """
    username = current_user.get("username", "User")
    
    async def event_generator():
        async for chunk in chat_service.send_message_stream(
            user_id=current_user["id"],
            session_id=request.session_id,
            message=request.message,
            username=username
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


class EditMessageRequest(BaseModel):
    new_content: str


@router.put("/sessions/{session_id}/messages/{message_id}")
async def edit_message(
    session_id: str,
    message_id: str,
    request: EditMessageRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Edit a message and regenerate response via SSE.
    """
    username = current_user.get("username", "User")
    
    async def event_generator():
        async for chunk in chat_service.edit_message_stream(
            user_id=current_user["id"],
            session_id=session_id,
            message_id=message_id,
            new_content=request.new_content,
            username=username
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ========================
# Health Check
# ========================

@router.get("/health")
async def check_health(chat_service: ChatService = Depends(get_chat_service)):
    """Check if Ollama is running and model is available"""
    health = await chat_service.check_ollama_health()
    return {
        "ollama_connected": health["connected"],
        "model_available": health["model_available"],
        "model": chat_service.model,
        "status": "ready" if health["connected"] and health["model_available"] else "offline"
    }
