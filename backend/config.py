import os
from dotenv import load_dotenv

load_dotenv()

FLASK_ENV = os.getenv('FLASK_ENV', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/meetings.db')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
RECORDINGS_FOLDER = os.getenv('RECORDINGS_FOLDER', 'data/recordings')

ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ZOOM_REDIRECT_URI = os.getenv('ZOOM_REDIRECT_URI', 'http://localhost:5000/api/auth/zoom/callback')

GOOGLE_MEET_CLIENT_ID = os.getenv('GOOGLE_MEET_CLIENT_ID')
GOOGLE_MEET_CLIENT_SECRET = os.getenv('GOOGLE_MEET_CLIENT_SECRET')
GOOGLE_MEET_REDIRECT_URI = os.getenv('GOOGLE_MEET_REDIRECT_URI', 'http://localhost:5000/api/auth/meet/callback')

TEAMS_CLIENT_ID = os.getenv('TEAMS_CLIENT_ID')
TEAMS_CLIENT_SECRET = os.getenv('TEAMS_CLIENT_SECRET')
TEAMS_REDIRECT_URI = os.getenv('TEAMS_REDIRECT_URI', 'http://localhost:5000/api/auth/teams/callback')

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')

GOOGLE_CLOUD_SPEECH_CREDENTIALS = os.getenv('GOOGLE_CLOUD_SPEECH_CREDENTIALS')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

DEFAULT_TRANSCRIPTION_SERVICE = os.getenv('DEFAULT_TRANSCRIPTION_SERVICE', 'deepgram')
DEFAULT_SUMMARIZATION_SERVICE = os.getenv('DEFAULT_SUMMARIZATION_SERVICE', 'openai')

MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 500 * 1024 * 1024))
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'mp4', 'm4a', 'ogg', 'webm', 'flac'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}

CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
