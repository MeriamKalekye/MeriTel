import asyncio
import os
import shutil
import threading
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser


class MeetingBot:
    def __init__(self, meeting_id: str, meeting_url: str, bot_name: str = "MeriTel Bot", storage=None):
        self.meeting_id = meeting_id
        self.meeting_url = meeting_url
        self.bot_name = bot_name
        self.is_running = False
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.audio_chunks = []
        self.recording_path = None
        self.start_time = None
        self.storage = storage
        
    async def start(self, on_transcript_update=None):
        self.is_running = True
        self.start_time = datetime.utcnow()
        self.audio_chunks_received = []
        
        recording_dir = Path('data/recordings')
        recording_dir.mkdir(parents=True, exist_ok=True)
        self.recording_path = recording_dir / f"{self.meeting_id}_{int(time.time())}.webm"
        
        async with async_playwright() as playwright:
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--autoplay-policy=no-user-gesture-required',
                    '--use-fake-ui-for-media-stream',
                ]
            )
            
            context = await self.browser.new_context(
                permissions=['microphone', 'camera'],
                viewport={'width': 1280, 'height': 720}
            )
            
            self.page = await context.new_page()
            
            if 'meet.google.com' in self.meeting_url:
                await self._join_google_meet()
            elif 'zoom.us' in self.meeting_url:
                await self._join_zoom()
            else:
                raise ValueError(f"Unsupported meeting platform: {self.meeting_url}")
            
            print("Bot joined meeting, starting audio capture...")
            
            if self.storage:
                meeting = self.storage.get_meeting(self.meeting_id)
                participants = meeting.get('participants', [])
                if self.bot_name not in participants:
                    participants.append(self.bot_name)
                    self.storage.update_meeting(self.meeting_id, {'participants': participants})
                    print(f"Added {self.bot_name} to participants list")
            
            await asyncio.sleep(5)
            
            await self._start_audio_capture()
            
            while self.is_running:
                await asyncio.sleep(1)
            
            try:
                print("Stopping audio capture...")
                await self._stop_audio_capture()
                
                print("Leaving meeting...")
                await self.page.close()
                await context.close()
                await self.browser.close()
                
            except Exception as e:
                print(f"Error closing browser: {e}")
                try:
                    if self.page:
                        await self.page.close()
                    if context:
                        await context.close()
                    if self.browser:
                        await self.browser.close()
                except:
                    pass
    
    async def _join_google_meet(self):
        await self.page.goto(self.meeting_url)
        print(f"Navigated to: {self.meeting_url}")
        
        await asyncio.sleep(3)
        
        try:
            name_input = await self.page.wait_for_selector('input[placeholder*="name" i]', timeout=5000)
            await name_input.fill(self.bot_name)
            print(f"Filled name: {self.bot_name}")
        except Exception as e:
            print(f"Could not fill name: {e}")
        
        try:
            turn_off_mic = await self.page.query_selector('[aria-label*="microphone" i]')
            if turn_off_mic:
                mic_state = await turn_off_mic.get_attribute('data-is-muted')
                if mic_state != 'true':
                    await turn_off_mic.click()
                    print("Turned off microphone")
        except Exception as e:
            print(f"Could not toggle mic: {e}")
        
        try:
            turn_off_camera = await self.page.query_selector('[aria-label*="camera" i]')
            if turn_off_camera:
                camera_state = await turn_off_camera.get_attribute('data-is-muted')
                if camera_state != 'true':
                    await turn_off_camera.click()
                    print("Turned off camera")
        except Exception as e:
            print(f"Could not toggle camera: {e}")
        
        await asyncio.sleep(2)
        
        try:
            join_button = await self.page.wait_for_selector('button:has-text("Ask to join")', timeout=5000)
            await join_button.click()
            print("Clicked 'Ask to join' button")
        except:
            try:
                join_button = await self.page.wait_for_selector('button:has-text("Join now")', timeout=5000)
                await join_button.click()
                print("Clicked 'Join now' button")
            except Exception as e:
                print(f"Could not find join button: {e}")
        
        await asyncio.sleep(3)
    
    async def _join_zoom(self):
        await self.page.goto(self.meeting_url)
        print(f"Navigated to: {self.meeting_url}")
        
        await asyncio.sleep(3)
        
        try:
            launch_meeting = await self.page.wait_for_selector('a[href*="zoomwebclient"]', timeout=10000)
            await launch_meeting.click()
            print("Clicked launch meeting in browser")
        except Exception as e:
            print(f"Could not launch browser meeting: {e}")
        
        await asyncio.sleep(3)
        
        try:
            name_input = await self.page.wait_for_selector('input#input-for-name', timeout=5000)
            await name_input.fill(self.bot_name)
            print(f"Filled name: {self.bot_name}")
        except Exception as e:
            print(f"Could not fill name: {e}")
        
        try:
            join_button = await self.page.wait_for_selector('button:has-text("Join")', timeout=5000)
            await join_button.click()
            print("Clicked join button")
        except Exception as e:
            print(f"Could not click join button: {e}")
        
        await asyncio.sleep(5)
        
        try:
            join_audio = await self.page.wait_for_selector('button:has-text("Join Audio by Computer")', timeout=5000)
            await join_audio.click()
            print("Clicked join audio button")
        except Exception as e:
            print(f"Could not join audio: {e}")
    
    async def _start_audio_capture(self):
        try:
            cdp = await self.page.context.new_cdp_session(self.page)
            
            await cdp.send('Page.enable')
            await cdp.send('Page.setWebLifecycleState', {'state': 'active'})
            
            result = await self.page.evaluate("""
                async () => {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ 
                            audio: {
                                echoCancellation: false,
                                noiseSuppression: false,
                                autoGainControl: false
                            } 
                        });
                        
                        window.audioRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm;codecs=opus'
                        });
                        
                        window.audioChunks = [];
                        window.audioRecorder.ondataavailable = (e) => {
                            if (e.data.size > 0) {
                                window.audioChunks.push(e.data);
                            }
                        };
                        
                        window.audioRecorder.start(1000);
                        return { success: true, message: 'Recording started' };
                    } catch (err) {
                        return { success: false, error: err.toString() };
                    }
                }
            """)
            print(f"Audio capture started: {result}")
            
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
    
    async def _stop_audio_capture(self):
        try:
            audio_data = await self.page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        if (window.audioRecorder && window.audioRecorder.state !== 'inactive') {
                            window.audioRecorder.onstop = () => {
                                if (window.audioChunks && window.audioChunks.length > 0) {
                                    const blob = new Blob(window.audioChunks, { type: 'audio/webm' });
                                    const reader = new FileReader();
                                    reader.onloadend = () => resolve(reader.result);
                                    reader.readAsDataURL(blob);
                                } else {
                                    resolve(null);
                                }
                            };
                            window.audioRecorder.stop();
                            if (window.audioRecorder.stream) {
                                window.audioRecorder.stream.getTracks().forEach(track => track.stop());
                            }
                        } else {
                            resolve(null);
                        }
                    });
                }
            """)
            
            if audio_data:
                audio_bytes = base64.b64decode(audio_data.split(',')[1])
                with open(self.recording_path, 'wb') as f:
                    f.write(audio_bytes)
                print(f"Audio saved: {self.recording_path} ({len(audio_bytes)} bytes)")
            else:
                print("No audio data captured")
                
        except Exception as e:
            print(f"Error stopping audio capture: {e}")
    
    def stop(self):
        self.is_running = False
    
    def get_recording_path(self) -> Optional[str]:
        return str(self.recording_path) if self.recording_path and os.path.exists(str(self.recording_path)) else None


class BotManager:
    def __init__(self, storage=None):
        self.active_bots: Dict[str, MeetingBot] = {}
        self.bot_threads: Dict[str, threading.Thread] = {}
        self.storage = storage
    
    def start_bot(self, meeting_id: str, meeting_url: str, bot_name: str = "MeriTel Bot") -> bool:
        if meeting_id in self.active_bots:
            return False
        
        bot = MeetingBot(meeting_id, meeting_url, bot_name, storage=self.storage)
        self.active_bots[meeting_id] = bot
        
        def run_bot():
            asyncio.run(bot.start())
        
        thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_threads[meeting_id] = thread
        thread.start()
        
        return True
    
    def stop_bot(self, meeting_id: str) -> Optional[str]:
        if meeting_id not in self.active_bots:
            return None
        
        bot = self.active_bots[meeting_id]
        bot.stop()
        
        thread = self.bot_threads.get(meeting_id)
        if thread and thread.is_alive():
            thread.join(timeout=10)
        
        recording_path = bot.get_recording_path()
        
        del self.active_bots[meeting_id]
        if meeting_id in self.bot_threads:
            del self.bot_threads[meeting_id]
        
        return recording_path
    
    def get_bot_status(self, meeting_id: str) -> Dict[str, Any]:
        if meeting_id not in self.active_bots:
            return {'status': 'inactive'}
        
        bot = self.active_bots[meeting_id]
        
        duration = 0
        if bot.start_time:
            duration = (datetime.utcnow() - bot.start_time).total_seconds()
        
        return {
            'status': 'active',
            'meeting_url': bot.meeting_url,
            'bot_name': bot.bot_name,
            'duration': duration,
            'is_recording': bot.is_running
        }
    
    def list_active_bots(self) -> Dict[str, Dict[str, Any]]:
        return {
            meeting_id: self.get_bot_status(meeting_id)
            for meeting_id in self.active_bots.keys()
        }
