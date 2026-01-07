import os
import json
import uuid
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime


class MeetingSummarizer:
    def __init__(self, service='openai', api_key=None):
        self.service = service
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError(f"API key required for {service}")
    
    def generate_structured_summary(
        self,
        transcript_segments: List[Dict[str, Any]],
        meeting_title: str = "Meeting",
        template: str = "general"
    ) -> Dict[str, Any]:
        full_text = self._segments_to_text(transcript_segments)
        
        if self.service == 'openai':
            return self._generate_with_openai(full_text, meeting_title, template)
        elif self.service == 'deepseek':
            return self._generate_with_deepseek(full_text, meeting_title, template)
        else:
            raise ValueError(f"Unsupported service: {self.service}")
    
    def _segments_to_text(self, segments: List[Dict[str, Any]]) -> str:
        lines = []
        for segment in segments:
            speaker = segment.get('speaker_name', 'Unknown Speaker')
            text = segment.get('text', '')
            start_time = segment.get('start_time', 0)
            
            mins = int(start_time // 60)
            secs = int(start_time % 60)
            timestamp = f"[{mins:02d}:{secs:02d}]"
            
            lines.append(f"{timestamp} {speaker}: {text}")
        
        return "\n".join(lines)
    
    def _generate_with_openai(
        self,
        full_text: str,
        meeting_title: str,
        template: str
    ) -> Dict[str, Any]:
        prompt = self._build_prompt(full_text, meeting_title, template)
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert meeting assistant that generates structured summaries.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2000
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            return self._parse_llm_response(content)
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _generate_with_deepseek(
        self,
        full_text: str,
        meeting_title: str,
        template: str
    ) -> Dict[str, Any]:
        prompt = self._build_prompt(full_text, meeting_title, template)
        
        try:
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert meeting assistant that generates structured summaries.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2000
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            return self._parse_llm_response(content)
        
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    def _build_prompt(self, full_text: str, meeting_title: str, template: str) -> str:
        template_instructions = self._get_template_instructions(template)
        
        return f"""Analyze the following meeting transcript and provide a structured summary in JSON format.

Meeting Title: {meeting_title}

{template_instructions}

Transcript:
{full_text[:10000]}

Please provide a JSON response with the following structure:
{{
  "overview": {{
    "text": "A concise 2-3 paragraph summary of the meeting covering key points, decisions, and outcomes.",
    "word_count": <number>
  }},
  "action_items": [
    {{
      "id": "unique_id",
      "text": "Specific action item description",
      "assignee": "Person's name if mentioned, or 'Unassigned'",
      "deadline": "Deadline if mentioned, or 'No deadline specified'",
      "completed": false
    }}
  ],
  "outline": [
    {{
      "topic": "Main topic discussed",
      "timestamp": <start_time_in_seconds>,
      "subtopics": ["Subtopic 1", "Subtopic 2"],
      "duration": <duration_in_seconds>
    }}
  ],
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "sentiment": "positive | neutral | negative"
}}

IMPORTANT:
- Extract ALL action items, tasks, and commitments mentioned
- Include assignee names when explicitly stated
- Include deadlines/due dates when mentioned
- Generate 3-7 main topics for the outline
- Ensure the overview is comprehensive but concise
- Return ONLY valid JSON, no additional text"""
    
    def _get_template_instructions(self, template: str) -> str:
        templates = {
            'general': 'Focus on key discussion points, decisions made, and next steps.',
            'sales': 'Focus on customer needs, objections, pricing discussions, and deal progression.',
            'engineering': 'Focus on technical decisions, architecture discussions, blockers, and implementation plans.',
            'standup': 'Focus on what was accomplished, current work, and blockers.',
            'retrospective': 'Focus on what went well, what could be improved, and action items.',
            'planning': 'Focus on goals, milestones, resource allocation, and timeline discussions.'
        }
        
        return templates.get(template, templates['general'])
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        try:
            content = content.strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            parsed = json.loads(content)
            
            for action_item in parsed.get('action_items', []):
                if 'id' not in action_item:
                    action_item['id'] = str(uuid.uuid4())
                if 'completed' not in action_item:
                    action_item['completed'] = False
            
            if 'overview' in parsed and isinstance(parsed['overview'], str):
                text = parsed['overview']
                parsed['overview'] = {
                    'text': text,
                    'word_count': len(text.split())
                }
            
            if 'overview' in parsed and isinstance(parsed['overview'], dict):
                if 'word_count' not in parsed['overview']:
                    parsed['overview']['word_count'] = len(parsed['overview']['text'].split())
            
            parsed['created_at'] = datetime.utcnow().isoformat()
            
            if 'template' not in parsed:
                parsed['template'] = 'general'
            
            return parsed
        
        except json.JSONDecodeError as e:
            return self._create_fallback_summary(content)
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")
    
    def _create_fallback_summary(self, content: str) -> Dict[str, Any]:
        return {
            'overview': {
                'text': content if content else "Failed to generate summary.",
                'word_count': len(content.split()) if content else 0
            },
            'action_items': [],
            'outline': [],
            'keywords': [],
            'sentiment': 'neutral',
            'created_at': datetime.utcnow().isoformat(),
            'template': 'general'
        }
    
    def extract_action_items(self, text: str) -> List[Dict[str, Any]]:
        prompt = f"""Extract all action items from the following text. An action item is a task, commitment, or to-do mentioned in the conversation.

Text:
{text[:5000]}

Return a JSON array of action items with this structure:
[
  {{
    "text": "Action item description",
    "assignee": "Person's name or 'Unassigned'",
    "deadline": "Deadline if mentioned or 'No deadline specified'"
  }}
]

Return ONLY the JSON array, no additional text."""
        
        try:
            if self.service == 'openai':
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-3.5-turbo',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.2,
                        'max_tokens': 1000
                    },
                    timeout=30
                )
            elif self.service == 'deepseek':
                response = requests.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'deepseek-chat',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.2,
                        'max_tokens': 1000
                    },
                    timeout=30
                )
            
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            action_items = json.loads(content)
            
            for item in action_items:
                if 'id' not in item:
                    item['id'] = str(uuid.uuid4())
                if 'completed' not in item:
                    item['completed'] = False
            
            return action_items
        
        except Exception as e:
            return []
    
    def generate_outline(
        self,
        transcript_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        full_text = self._segments_to_text(transcript_segments)
        
        prompt = f"""Analyze this meeting transcript and create a structured outline of the main topics discussed.

Transcript:
{full_text[:8000]}

Identify 3-7 main topics/themes discussed in the meeting. For each topic, provide:
- The topic name
- Approximate timestamp when it was discussed (in seconds from start)
- Duration (in seconds)
- 2-4 key subtopics or points under that topic

Return a JSON array with this structure:
[
  {{
    "topic": "Topic name",
    "timestamp": <seconds>,
    "duration": <seconds>,
    "subtopics": ["Subtopic 1", "Subtopic 2"]
  }}
]

Return ONLY the JSON array, no additional text."""
        
        try:
            if self.service == 'openai':
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-3.5-turbo',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.3,
                        'max_tokens': 1000
                    },
                    timeout=30
                )
            elif self.service == 'deepseek':
                response = requests.post(
                    'https://api.deepseek.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'deepseek-chat',
                        'messages': [{'role': 'user', 'content': prompt}],
                        'temperature': 0.3,
                        'max_tokens': 1000
                    },
                    timeout=30
                )
            
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            outline = json.loads(content)
            
            return outline
        
        except Exception as e:
            return []
