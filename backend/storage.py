import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class MeetingStorage:
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.meetings_dir = self.data_dir / 'meetings'
        self.transcripts_dir = self.data_dir / 'transcripts'
        self.summaries_dir = self.data_dir / 'summaries'
        
        self.meetings_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
    
    def create_meeting(self, meeting_data: Dict[str, Any]) -> str:
        meeting_id = str(uuid.uuid4())
        
        meeting = {
            'meeting_id': meeting_id,
            'title': meeting_data.get('title', ''),
            'description': meeting_data.get('description', ''),
            'meeting_type': meeting_data.get('meeting_type', 'physical'),
            'platform': meeting_data.get('platform'),
            'platform_meeting_id': meeting_data.get('platform_meeting_id'),
            'join_url': meeting_data.get('join_url'),
            'recording_url': meeting_data.get('recording_url'),
            'audio_file_path': meeting_data.get('audio_file_path'),
            'duration': meeting_data.get('duration', 0),
            'status': meeting_data.get('status', 'created'),
            'participants': meeting_data.get('participants', []),
            'created_at': datetime.utcnow().isoformat(),
            'started_at': meeting_data.get('started_at'),
            'ended_at': meeting_data.get('ended_at')
        }
        
        self._save_meeting(meeting_id, meeting)
        return meeting_id
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        meeting_file = self.meetings_dir / f'{meeting_id}.json'
        if not meeting_file.exists():
            return None
        
        with open(meeting_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_meeting(self, meeting_id: str, updates: Dict[str, Any]) -> bool:
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return False
        
        meeting.update(updates)
        self._save_meeting(meeting_id, meeting)
        return True
    
    def list_meetings(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meetings = []
        for meeting_file in self.meetings_dir.glob('*.json'):
            with open(meeting_file, 'r', encoding='utf-8') as f:
                meeting = json.load(f)
                
                if filters:
                    if 'meeting_type' in filters and meeting.get('meeting_type') != filters['meeting_type']:
                        continue
                    if 'platform' in filters and meeting.get('platform') != filters['platform']:
                        continue
                    if 'status' in filters and meeting.get('status') != filters['status']:
                        continue
                
                meetings.append(meeting)
        
        meetings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return meetings
    
    def delete_meeting(self, meeting_id: str) -> bool:
        meeting_file = self.meetings_dir / f'{meeting_id}.json'
        transcript_file = self.transcripts_dir / f'{meeting_id}.json'
        summary_file = self.summaries_dir / f'{meeting_id}.json'
        
        deleted = False
        if meeting_file.exists():
            meeting_file.unlink()
            deleted = True
        if transcript_file.exists():
            transcript_file.unlink()
        if summary_file.exists():
            summary_file.unlink()
        
        return deleted
    
    def save_detailed_transcript(self, meeting_id: str, transcript_data: Dict[str, Any]) -> bool:
        transcript = {
            'meeting_id': meeting_id,
            'segments': transcript_data.get('segments', []),
            'created_at': datetime.utcnow().isoformat(),
            'service': transcript_data.get('service', 'unknown')
        }
        
        for segment in transcript['segments']:
            if 'segment_id' not in segment:
                segment['segment_id'] = str(uuid.uuid4())
        
        transcript_file = self.transcripts_dir / f'{meeting_id}.json'
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        self.update_meeting(meeting_id, {
            'status': 'transcribed',
            'transcript_file_path': str(transcript_file)
        })
        return True
    
    def get_detailed_transcript(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        transcript_file = self.transcripts_dir / f'{meeting_id}.json'
        if not transcript_file.exists():
            return None
        
        with open(transcript_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_structured_summary(self, meeting_id: str, summary_data: Dict[str, Any]) -> bool:
        summary = {
            'meeting_id': meeting_id,
            'overview': summary_data.get('overview', {
                'text': '',
                'word_count': 0
            }),
            'action_items': summary_data.get('action_items', []),
            'outline': summary_data.get('outline', []),
            'keywords': summary_data.get('keywords', []),
            'sentiment': summary_data.get('sentiment', 'neutral'),
            'created_at': datetime.utcnow().isoformat(),
            'template': summary_data.get('template', 'general')
        }
        
        for action_item in summary['action_items']:
            if 'id' not in action_item:
                action_item['id'] = str(uuid.uuid4())
            if 'completed' not in action_item:
                action_item['completed'] = False
        
        summary_file = self.summaries_dir / f'{meeting_id}.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.update_meeting(meeting_id, {'status': 'completed'})
        return True
    
    def get_structured_summary(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        summary_file = self.summaries_dir / f'{meeting_id}.json'
        if not summary_file.exists():
            return None
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_action_item(self, meeting_id: str, action_item_id: str, updates: Dict[str, Any]) -> bool:
        summary = self.get_structured_summary(meeting_id)
        if not summary:
            return False
        
        for action_item in summary.get('action_items', []):
            if action_item.get('id') == action_item_id:
                action_item.update(updates)
                return self.save_structured_summary(meeting_id, summary)
        
        return False
    
    def add_participant(self, meeting_id: str, participant_data: Dict[str, Any]) -> bool:
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return False
        
        participant = {
            'id': participant_data.get('id', str(uuid.uuid4())),
            'name': participant_data.get('name', ''),
            'email': participant_data.get('email'),
            'platform_user_id': participant_data.get('platform_user_id'),
            'avatar_url': participant_data.get('avatar_url')
        }
        
        if 'participants' not in meeting:
            meeting['participants'] = []
        
        meeting['participants'].append(participant)
        self._save_meeting(meeting_id, meeting)
        return True
    
    def get_participant(self, meeting_id: str, participant_id: str) -> Optional[Dict[str, Any]]:
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        for participant in meeting.get('participants', []):
            if participant.get('id') == participant_id or participant.get('platform_user_id') == participant_id:
                return participant
        
        return None
    
    def _save_meeting(self, meeting_id: str, meeting: Dict[str, Any]):
        meeting_file = self.meetings_dir / f'{meeting_id}.json'
        with open(meeting_file, 'w', encoding='utf-8') as f:
            json.dump(meeting, f, indent=2, ensure_ascii=False)
