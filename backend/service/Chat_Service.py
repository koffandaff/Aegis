"""
Chat Service - Ollama Integration with Streaming
Uses Koffan/Cybiz:latest model
"""
import httpx
import json
from typing import AsyncGenerator, Optional, Dict, List
from datetime import datetime

from model.Chat_Model import ChatDatabase, ChatSession, ChatMessage


class ChatService:
    def __init__(self, db: ChatDatabase):
        self.db = db
        self.ollama_url = "http://localhost:11434"
        self.model = "IHA089/drana-infinity-3b:3b"  # Use available local model
        self.timeout = 120.0  # Longer timeout for AI responses
    
    async def check_ollama_health(self) -> Dict[str, bool]:
        """Check if Ollama is running and the specific model is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code != 200:
                    return {"connected": False, "model_available": False}
                
                tags = response.json().get("models", [])
                model_names = [m.get("name") for m in tags]
                
                # Check for model (handle both formats if necessary)
                model_available = any(self.model in name for name in model_names)
                
                return {
                    "connected": True, 
                    "model_available": model_available
                }
        except:
            return {"connected": False, "model_available": False}
    
    async def send_message_stream(
        self, 
        user_id: str, 
        session_id: Optional[str], 
        message: str,
        username: str = "User"
    ) -> AsyncGenerator[str, None]:
        """
        Send message to Ollama and stream the response.
        Yields JSON chunks with 'content' or 'done' fields.
        """
        # Get or create session
        if session_id:
            session = self.db.get_session(session_id, user_id)
            if not session:
                yield json.dumps({"error": "Session not found"})
                return
        else:
            # Create new session
            session = self.db.create_session(user_id, message)
            session_id = session.id
            yield json.dumps({"session_id": session_id, "type": "session_created"})
        
        # Add user message to database
        self.db.add_message(session_id, user_id, "user", message)
        
        # Get context messages for Ollama
        context = self.db.get_context_messages(session_id, user_id, limit=10)
        
        # Build system prompt with user context
        system_prompt = f"You are Cybiz built by Dhruvil, an AI assistant for the Fsociety cybersecurity platform. The user's name is {username}. Be helpful, concise, and technical when discussing security topics. Format code with proper markdown code blocks."
        
        # Prepare Ollama request
        ollama_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *context
            ],
            "stream": True
        }
        
        full_response = ""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/api/chat",
                    json=ollama_payload
                ) as response:
                    if response.status_code != 200:
                        yield json.dumps({"error": f"Ollama error: {response.status_code}"})
                        return
                    
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                
                                if "message" in data and "content" in data["message"]:
                                    content = data["message"]["content"]
                                    full_response += content
                                    yield json.dumps({"content": content, "type": "token"})
                                
                                if data.get("done", False):
                                    yield json.dumps({"type": "done"})
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                
                # Save assistant response to database
                if full_response:
                    self.db.add_message(session_id, user_id, "assistant", full_response)
                    # Log chat activity
                    from model.Auth_Model import db as auth_db
                    auth_db.log_activity(
                        user_id=user_id,
                        action='chat',
                        details={'session_id': session_id, 'message_preview': message[:50]}
                    )
                    
        except httpx.TimeoutException:
            yield json.dumps({"error": "Ollama request timed out"})
        except httpx.ConnectError:
            yield json.dumps({"error": "Cannot connect to Ollama. Is it running?"})
        except Exception as e:
            yield json.dumps({"error": str(e)})
    
    # Session Management
    
    def get_user_sessions(self, user_id: str):
        """Get all chat sessions for a user"""
        return self.db.get_user_sessions(user_id)
    
    def get_session(self, session_id: str, user_id: str):
        """Get specific session with messages"""
        return self.db.get_session(session_id, user_id)
    
    def create_session(self, user_id: str):
        """Create new empty session"""
        return self.db.create_session(user_id)
    
    def delete_session(self, session_id: str, user_id: str):
        """Delete a session"""
        return self.db.delete_session(session_id, user_id)

    def update_session_title(self, session_id: str, user_id: str, new_title: str):
        """Update a session title"""
        return self.db.update_session_title(session_id, user_id, new_title)


# Global service instance
from model.Chat_Model import chat_db
chat_service = ChatService(chat_db)
