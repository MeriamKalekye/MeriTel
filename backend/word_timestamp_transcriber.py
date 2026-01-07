import os
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path


class WordTimestampTranscriber:
    def __init__(self, service='deepgram', api_key=None):
        self.service = service.lower()
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError(f"API key required for {service} transcription")
    
    def transcribe_with_timestamps(self, audio_path: str) -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if self.service == 'deepgram':
            return self._transcribe_deepgram(audio_path)
        elif self.service == 'assemblyai':
            return self._transcribe_assemblyai(audio_path)
        else:
            raise ValueError(f"Unsupported transcription service: {self.service}")
    
    def _transcribe_deepgram(self, audio_path: str) -> Dict[str, Any]:
        url = "https://api.deepgram.com/v1/listen"
        
        params = {
            'diarize': 'true',
            'punctuate': 'true',
            'utterances': 'true',
            'model': 'nova-2',
            'smart_format': 'true',
        }
        
        headers = {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': self._get_content_type(audio_path)
        }
        
        with open(audio_path, 'rb') as audio_file:
            response = requests.post(
                url,
                params=params,
                headers=headers,
                data=audio_file,
                timeout=300
            )
        
        if response.status_code != 200:
            raise Exception(f"Deepgram API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return self._format_deepgram_response(result)
    
    def _transcribe_assemblyai(self, audio_path: str) -> Dict[str, Any]:
        upload_url = "https://api.assemblyai.com/v2/upload"
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        
        headers = {
            'authorization': self.api_key,
        }
        
        with open(audio_path, 'rb') as audio_file:
            upload_response = requests.post(
                upload_url,
                headers=headers,
                data=audio_file,
                timeout=300
            )
        
        if upload_response.status_code != 200:
            raise Exception(f"AssemblyAI upload error: {upload_response.status_code} - {upload_response.text}")
        
        audio_url = upload_response.json()['upload_url']
        
        transcript_request = {
            'audio_url': audio_url,
            'speaker_labels': True,
            'punctuate': True,
            'format_text': True,
        }
        
        transcript_response = requests.post(
            transcript_url,
            headers=headers,
            json=transcript_request,
            timeout=60
        )
        
        if transcript_response.status_code != 200:
            raise Exception(f"AssemblyAI transcription error: {transcript_response.status_code} - {transcript_response.text}")
        
        transcript_id = transcript_response.json()['id']
        
        polling_url = f"{transcript_url}/{transcript_id}"
        
        while True:
            polling_response = requests.get(polling_url, headers=headers)
            result = polling_response.json()
            
            status = result['status']
            
            if status == 'completed':
                return self._format_assemblyai_response(result)
            elif status == 'error':
                raise Exception(f"AssemblyAI transcription failed: {result.get('error')}")
            
            time.sleep(3)
    
    def _format_deepgram_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        segments = []
        
        if 'results' not in response or 'utterances' not in response['results']:
            return {'segments': segments}
        
        utterances = response['results']['utterances']
        
        for utterance in utterances:
            words_data = []
            
            for word in utterance.get('words', []):
                words_data.append({
                    'word': word['word'],
                    'start': word['start'],
                    'end': word['end'],
                    'confidence': word.get('confidence', 1.0)
                })
            
            segment = {
                'speaker_id': f"speaker_{utterance.get('speaker', 0)}",
                'speaker_name': f"Speaker {utterance.get('speaker', 0)}",
                'start_time': utterance['start'],
                'end_time': utterance['end'],
                'text': utterance['transcript'],
                'confidence': utterance.get('confidence', 1.0),
                'words': words_data
            }
            
            segments.append(segment)
        
        return {'segments': segments}
    
    def _format_assemblyai_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        segments = []
        
        if 'utterances' not in response:
            return {'segments': segments}
        
        utterances = response['utterances']
        words_by_index = {word['start']: word for word in response.get('words', [])}
        
        for utterance in utterances:
            words_data = []
            
            for word in response.get('words', []):
                if word['start'] >= utterance['start'] and word['end'] <= utterance['end']:
                    words_data.append({
                        'word': word['text'],
                        'start': word['start'] / 1000.0,
                        'end': word['end'] / 1000.0,
                        'confidence': word.get('confidence', 1.0)
                    })
            
            segment = {
                'speaker_id': f"speaker_{utterance.get('speaker', 'A')}",
                'speaker_name': f"Speaker {utterance.get('speaker', 'A')}",
                'start_time': utterance['start'] / 1000.0,
                'end_time': utterance['end'] / 1000.0,
                'text': utterance['text'],
                'confidence': utterance.get('confidence', 1.0),
                'words': words_data
            }
            
            segments.append(segment)
        
        return {'segments': segments}
    
    def _get_content_type(self, audio_path: str) -> str:
        ext = Path(audio_path).suffix.lower()
        content_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.mp4': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.webm': 'audio/webm'
        }
        return content_types.get(ext, 'audio/mpeg')
    
    def map_speakers_to_participants(
        self,
        segments: List[Dict[str, Any]],
        participants: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not participants:
            return segments
        
        speaker_to_participant = {}
        unique_speakers = set(seg['speaker_id'] for seg in segments)
        
        for i, speaker_id in enumerate(sorted(unique_speakers)):
            if i < len(participants):
                speaker_to_participant[speaker_id] = participants[i]
        
        for segment in segments:
            speaker_id = segment['speaker_id']
            if speaker_id in speaker_to_participant:
                participant = speaker_to_participant[speaker_id]
                segment['speaker_id'] = participant.get('id', speaker_id)
                segment['speaker_name'] = participant.get('name', segment['speaker_name'])
        
        return segments
