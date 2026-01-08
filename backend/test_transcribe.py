from word_timestamp_transcriber import WordTimestampTranscriber
import os

api_key = '1411be6f8f214bf5b03269600f94686f'
path = 'data/recordings/5f39bf5d-cb4b-4118-a630-c5291ae98d17_1767909529.webm'

print(f'File exists: {os.path.exists(path)}')
print(f'File size: {os.path.getsize(path)} bytes')

try:
    transcriber = WordTimestampTranscriber('assemblyai', api_key)
    result = transcriber.transcribe_with_timestamps(path)
    print(f'Transcription success: {len(result["segments"])} segments')
    print(f'First segment: {result["segments"][0] if result["segments"] else "None"}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
