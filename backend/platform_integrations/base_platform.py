from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BasePlatform(ABC):
    
    @abstractmethod
    def authenticate(self, code: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_meeting_details(self, meeting_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def download_recording(self, meeting_id: str, output_path: str) -> str:
        pass
    
    @abstractmethod
    def get_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        pass
