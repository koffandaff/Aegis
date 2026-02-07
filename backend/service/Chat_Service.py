"""
Chat Service - Ollama Integration with Streaming
Uses Koffan/Cybiz:latest model
"""
import os
import httpx
import json
from typing import AsyncGenerator, Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session

from model.Chat_Model import ChatSession, ChatMessage
from database.repositories.activity_repository import ActivityRepository
from database.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self, sql_db: Session, chat_repo: ChatRepository):
        self.db = chat_repo  # SQL chat storage
        self.sql_db = sql_db  # SQLAlchemy session
        self.activity_repo = ActivityRepository(sql_db)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = "IHA089/drana-infinity-3b:3b"  # Use available local model
        self.timeout = 120.0  # Longer timeout for AI responses
    
    async def check_ollama_health(self) -> Dict[str, bool]:
        """Check if Ollama is running and the specific model is available"""
        if not self.ollama_url:
            print("DEBUG: OLLAMA_URL is missing or empty")
            return {"connected": False, "model_available": False}
        
        print(f"DEBUG: Checking Ollama health at {self.ollama_url}")
            
        try:
            # Bypass Ngrok browser warning
            headers = {"ngrok-skip-browser-warning": "true"}
            async with httpx.AsyncClient(timeout=90.0, headers=headers) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code != 200:
                    return {"connected": False, "model_available": False}
                
                tags = response.json().get("models", [])
                model_names = [m.get("name") for m in tags]
                
                if not model_names:
                    return {"connected": True, "model_available": False}
                
                # Check for model (handle both formats if necessary)
                model_available = any(self.model in name for name in model_names)
                
                if not model_available:
                     # Fallback to the first available model
                     print(f"Preferred model {self.model} not found. Switching to {model_names[0]}")
                     self.model = model_names[0]
                     model_available = True

                return {
                    "connected": True, 
                    "model_available": model_available,
                    "debug_url": self.ollama_url
                }
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return {"connected": False, "model_available": False, "debug_url": self.ollama_url}
    
    async def _stream_response(self, session_id: str, user_id: str, context: List[Dict], username: str) -> AsyncGenerator[str, None]:
        """Internal helper to stream response from Ollama"""
        
        # Send initial status to confirm connection is alive
        yield json.dumps({"type": "token", "content": "..."}) 

        # Build system prompt with user context
        system_prompt = f"""You are Cybiz (created by Dhruvil), the advanced AI assistant for Fsociety, a comprehensive cybersecurity platform. 
The user's name is {username}. 

About Fsociety Platform:
- **Dashboard**: Central hub for system status and quick access to tools.
- **Network Scan**: Tools for Nmap scanning (ports, services), DNS enumeration, and Whois lookups to analyze network targets.
- **Digital Footprint**: OSINT utility to analyze public exposure of domains and usernames, checking for data leaks.
- **Security Audit**: Automated security checks for web applications and infrastructure.
- **Phishing Detector**: AI-powered analysis of URLs and emails to detect malicious phishing attempts.
- **File Analysis**: Upload and scan files for malware signatures and behavior analysis.
- **VPN Configs**: Generate secure OpenVPN configurations for anonymous browsing.
- **Operation History**: Track and review all your past scans and activities.

Your Role:
- Guide users on how to use these features.
- Explain cybersecurity concepts clearly and technically.
- If asked "what is this platform?", describe Fsociety as an all-in-one security reconnaissance and analysis suite.
- Be helpful, concise, and professional. Format code with proper markdown.
"""
        
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
            headers = {"ngrok-skip-browser-warning": "true"}
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
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
                                    # SAVE BEFORE YIELDING DONE to prevent race condition
                                    if full_response:
                                        self.db.add_message(session_id, user_id, "assistant", full_response)
                                        # Log chat activity
                                        self.activity_repo.log_activity(
                                            user_id=user_id,
                                            action='chat',
                                            details={'session_id': session_id, 'length': len(full_response)}
                                        )
                                        full_response = "" # Prevent double saving
                                        
                                    yield json.dumps({"type": "done"})
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                    
        except httpx.TimeoutException:
            yield json.dumps({"error": "Ollama request timed out. The model is taking too long to respond."})
        except httpx.ConnectError:
            yield json.dumps({"error": "Connection refused. Ensure Ollama is running on port 11434."})
        except httpx.HTTPStatusError as e:
            yield json.dumps({"error": f"Ollama returned HTTP {e.response.status_code}: {e.response.text}"})
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield json.dumps({"error": f"Internal Error: {str(e)}"})

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
            # Add user message to database for existing session
            self.db.add_message(session_id, user_id, "user", message)
        else:
            # Create new session (creates message internally)
            session = self.db.create_session(user_id, message)
            session_id = session.id
            yield json.dumps({"session_id": session_id, "type": "session_created"})
        
        # Get context messages for Ollama (Increased Limit)
        context = self.db.get_context_messages(session_id, user_id, limit=200)
        
        async for chunk in self._stream_response(session_id, user_id, context, username):
            yield chunk

    async def edit_message_stream(
        self,
        user_id: str,
        session_id: str,
        message_id: str,
        new_content: str,
        username: str = "User"
    ) -> AsyncGenerator[str, None]:
        """
        Edit a user message and stream the new response
        """
        # Edit message in DB (truncates future messages)
        updated_messages = self.db.edit_message(session_id, user_id, message_id, new_content)
        
        if updated_messages is None:
            yield json.dumps({"error": "Failed to edit message"})
            return
            
        # Get updated context
        context = self.db.get_context_messages(session_id, user_id, limit=200)
        
        # Stream new response
        async for chunk in self._stream_response(session_id, user_id, context, username):
            yield chunk

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