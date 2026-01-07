import requests
import base64
import os
from typing import Dict, List, Any, Optional
from .base_platform import BasePlatform


class ZoomPlatform(BasePlatform):
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.base_url = "https://api.zoom.us/v2"
        self.auth_url = "https://zoom.us/oauth"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        if state:
            params['state'] = state
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{self.auth_url}/authorize?{query_string}"
    
    def authenticate(self, code: str) -> Dict[str, Any]:
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(
            f"{self.auth_url}/token",
            headers=headers,
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to authenticate with Zoom: {response.text}")
        
        token_data = response.json()
        self.access_token = token_data.get('access_token')
        
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'expires_in': token_data.get('expires_in'),
            'scope': token_data.get('scope')
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(
            f"{self.auth_url}/token",
            headers=headers,
            data=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh Zoom token: {response.text}")
        
        token_data = response.json()
        self.access_token = token_data.get('access_token')
        
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'expires_in': token_data.get('expires_in'),
            'scope': token_data.get('scope')
        }
    
    def set_access_token(self, access_token: str):
        self.access_token = access_token
    
    def get_meeting_details(self, meeting_id: str) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{self.base_url}/meetings/{meeting_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get meeting details: {response.text}")
        
        meeting_data = response.json()
        
        return {
            'platform_meeting_id': meeting_data.get('id'),
            'title': meeting_data.get('topic', 'Untitled Meeting'),
            'description': meeting_data.get('agenda', ''),
            'join_url': meeting_data.get('join_url'),
            'start_time': meeting_data.get('start_time'),
            'duration': meeting_data.get('duration', 0),
            'timezone': meeting_data.get('timezone'),
            'host_id': meeting_data.get('host_id'),
            'status': meeting_data.get('status')
        }
    
    def download_recording(self, meeting_id: str, output_path: str) -> str:
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{self.base_url}/meetings/{meeting_id}/recordings",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get recording info: {response.text}")
        
        recordings_data = response.json()
        recording_files = recordings_data.get('recording_files', [])
        
        if not recording_files:
            raise Exception("No recordings found for this meeting")
        
        audio_file = None
        for file in recording_files:
            if file.get('file_type') in ['M4A', 'MP4'] and file.get('recording_type') in ['audio_only', 'shared_screen_with_speaker_view']:
                audio_file = file
                break
        
        if not audio_file:
            audio_file = recording_files[0]
        
        download_url = audio_file.get('download_url')
        if not download_url:
            raise Exception("No download URL found for recording")
        
        download_response = requests.get(
            download_url,
            headers={'Authorization': f'Bearer {self.access_token}'},
            stream=True
        )
        
        if download_response.status_code != 200:
            raise Exception(f"Failed to download recording: {download_response.text}")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def get_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{self.base_url}/past_meetings/{meeting_id}/participants",
            headers=headers,
            params={'page_size': 300}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get participants: {response.text}")
        
        participants_data = response.json()
        participants = []
        
        for participant in participants_data.get('participants', []):
            participants.append({
                'id': participant.get('id'),
                'name': participant.get('name', 'Unknown'),
                'email': participant.get('user_email', ''),
                'platform_user_id': participant.get('user_id', ''),
                'avatar_url': None,
                'join_time': participant.get('join_time'),
                'leave_time': participant.get('leave_time'),
                'duration': participant.get('duration', 0)
            })
        
        return participants
    
    def get_meeting_recording_details(self, meeting_id: str) -> Dict[str, Any]:
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{self.base_url}/meetings/{meeting_id}/recordings",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get recording details: {response.text}")
        
        recordings_data = response.json()
        
        return {
            'meeting_id': recordings_data.get('uuid'),
            'host_id': recordings_data.get('host_id'),
            'topic': recordings_data.get('topic'),
            'start_time': recordings_data.get('start_time'),
            'duration': recordings_data.get('duration'),
            'total_size': recordings_data.get('total_size'),
            'recording_count': recordings_data.get('recording_count'),
            'recording_files': recordings_data.get('recording_files', [])
        }
