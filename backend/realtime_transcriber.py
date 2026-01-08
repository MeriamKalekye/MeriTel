import asyncio
import json
from typing import Callable, Optional, Dict, Any
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import assemblyai as aai


class RealtimeTranscriber:
    def __init__(self, service='deepgram', api_key=None):
        self.service = service.lower()
        self.api_key = api_key
        self.is_active = False
        self.on_transcript_callback = None
        
        if not self.api_key:
            raise ValueError(f"API key required for {service}")
    
    async def start_stream(self, audio_stream, on_transcript: Callable[[Dict[str, Any]], None]):
        self.on_transcript_callback = on_transcript
        self.is_active = True
        
        if self.service == 'deepgram':
            await self._stream_deepgram(audio_stream)
        elif self.service == 'assemblyai':
            await self._stream_assemblyai(audio_stream)
        else:
            raise ValueError(f"Unsupported service: {self.service}")
    
    async def _stream_deepgram(self, audio_stream):
        try:
            deepgram = DeepgramClient(self.api_key)
            
            dg_connection = deepgram.listen.live.v("1")
            
            def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                
                if len(sentence) == 0:
                    return
                
                if result.is_final:
                    words = []
                    for word_data in result.channel.alternatives[0].words:
                        words.append({
                            'word': word_data.word,
                            'start': word_data.start,
                            'end': word_data.end,
                            'confidence': word_data.confidence
                        })
                    
                    transcript_data = {
                        'type': 'final',
                        'text': sentence,
                        'words': words,
                        'is_final': True
                    }
                    
                    if self.on_transcript_callback:
                        self.on_transcript_callback(transcript_data)
                else:
                    transcript_data = {
                        'type': 'interim',
                        'text': sentence,
                        'is_final': False
                    }
                    
                    if self.on_transcript_callback:
                        self.on_transcript_callback(transcript_data)
            
            def on_error(self, error, **kwargs):
                print(f"Deepgram error: {error}")
            
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)
            
            options = LiveOptions(
                model="nova-2",
                language="en",
                smart_format=True,
                punctuate=True,
                interim_results=True
            )
            
            if dg_connection.start(options) is False:
                print("Failed to start Deepgram connection")
                return
            
            while self.is_active:
                chunk = await audio_stream.read(8192)
                if chunk:
                    dg_connection.send(chunk)
                else:
                    await asyncio.sleep(0.1)
            
            dg_connection.finish()
        
        except Exception as e:
            print(f"Deepgram streaming error: {e}")
    
    async def _stream_assemblyai(self, audio_stream):
        try:
            aai.settings.api_key = self.api_key
            
            transcriber = aai.RealtimeTranscriber(
                sample_rate=16_000,
                on_data=self._on_assemblyai_data,
                on_error=self._on_assemblyai_error,
            )
            
            transcriber.connect()
            
            while self.is_active:
                chunk = await audio_stream.read(8192)
                if chunk:
                    transcriber.stream(chunk)
                else:
                    await asyncio.sleep(0.1)
            
            transcriber.close()
        
        except Exception as e:
            print(f"AssemblyAI streaming error: {e}")
    
    def _on_assemblyai_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return
        
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            words = []
            if hasattr(transcript, 'words') and transcript.words:
                for word_data in transcript.words:
                    words.append({
                        'word': word_data.text,
                        'start': word_data.start / 1000.0,
                        'end': word_data.end / 1000.0,
                        'confidence': word_data.confidence
                    })
            
            transcript_data = {
                'type': 'final',
                'text': transcript.text,
                'words': words,
                'is_final': True
            }
            
            if self.on_transcript_callback:
                self.on_transcript_callback(transcript_data)
        else:
            transcript_data = {
                'type': 'interim',
                'text': transcript.text,
                'is_final': False
            }
            
            if self.on_transcript_callback:
                self.on_transcript_callback(transcript_data)
    
    def _on_assemblyai_error(self, error: aai.RealtimeError):
        print(f"AssemblyAI error: {error}")
    
    def stop(self):
        self.is_active = False
