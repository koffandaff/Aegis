from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from database.models import VPNConfig, VPNServer
from database.repositories.base import BaseRepository

class VPNRepository(BaseRepository[VPNConfig]):
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create(self, data: Dict[str, Any]) -> VPNConfig:
        config = VPNConfig(
            id=data.get("id"),
            user_id=data.get("user_id"),
            server_id=data.get("server_id"),
            config_type=data.get("config_type", "openvpn"),
            filename=data.get("filename"),
            config_content=data.get("config_content"),
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def get_by_user(self, user_id: str) -> List[VPNConfig]:
        return self.db.query(VPNConfig).filter(VPNConfig.user_id == user_id).all()
    
    def get_servers(self) -> List[VPNServer]:
        return self.db.query(VPNServer).all()
        
    def get_server(self, server_id: str) -> Optional[VPNServer]:
        return self.db.query(VPNServer).filter(VPNServer.id == server_id).first()
