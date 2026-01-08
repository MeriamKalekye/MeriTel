import os
import subprocess
import numpy as np
from pathlib import Path
from pydub import AudioSegment
import noisereduce as nr


class AudioProcessor:
    def __init__(self):
        self.temp_dir = Path('data/temp')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def process_meeting_audio(self, input_path: str, output_path: str = None) -> str:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if output_path is None:
            output_path = input_path.replace('.webm', '_processed.webm')
        
        print(f"Processing audio: {input_path}")
        
        try:
            wav_temp = str(self.temp_dir / 'temp_audio.wav')
            
            subprocess.run([
                'ffmpeg', '-i', input_path,
                '-ar', '16000',
                '-ac', '1',
                '-sample_fmt', 's16',
                '-y',
                wav_temp
            ], check=True, capture_output=True)
            
            audio = AudioSegment.from_wav(wav_temp)
            
            samples = np.array(audio.get_array_of_samples())
            
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)
            
            sample_rate = audio.frame_rate
            
            reduced_noise = nr.reduce_noise(
                y=samples,
                sr=sample_rate,
                stationary=True,
                prop_decrease=0.8
            )
            
            processed_audio = AudioSegment(
                reduced_noise.tobytes(),
                frame_rate=sample_rate,
                sample_width=2,
                channels=1
            )
            
            processed_audio = processed_audio.normalize()
            
            processed_audio = processed_audio.compress_dynamic_range(
                threshold=-20.0,
                ratio=4.0,
                attack=5.0,
                release=50.0
            )
            
            wav_processed = str(self.temp_dir / 'processed_audio.wav')
            processed_audio.export(wav_processed, format='wav')
            
            subprocess.run([
                'ffmpeg', '-i', wav_processed,
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                output_path
            ], check=True, capture_output=True)
            
            try:
                os.remove(wav_temp)
                os.remove(wav_processed)
            except:
                pass
            
            print(f"Audio processing complete: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception(f"Audio processing failed: {str(e)}")
        except Exception as e:
            print(f"Audio processing error: {str(e)}")
            raise
    
    def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
        try:
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-vn',
                '-acodec', 'libopus',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                output_path
            ], check=True, capture_output=True)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")
