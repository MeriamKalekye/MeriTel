from flask import Flask, request, jsonify, redirect, session, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    SECRET_KEY, CORS_ORIGINS, UPLOAD_FOLDER, RECORDINGS_FOLDER,
    ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI,
    DEEPGRAM_API_KEY, ASSEMBLYAI_API_KEY, DEFAULT_TRANSCRIPTION_SERVICE,
    OPENAI_API_KEY, DEEPSEEK_API_KEY, DEFAULT_SUMMARIZATION_SERVICE
)
from storage import MeetingStorage
from platform_integrations.zoom_integration import ZoomPlatform
from word_timestamp_transcriber import WordTimestampTranscriber
from summarizer import MeetingSummarizer
from meeting_bot import BotManager
from audio_processor import AudioProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RECORDINGS_FOLDER'] = RECORDINGS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS, "allow_headers": ["Content-Type", "Authorization"], "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins=CORS_ORIGINS)

storage = MeetingStorage(data_dir='data')
bot_manager = BotManager(storage=storage)
audio_processor = AudioProcessor()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/meetings', methods=['GET'])
def list_meetings():
    filters = {}
    if request.args.get('meeting_type'):
        filters['meeting_type'] = request.args.get('meeting_type')
    if request.args.get('platform'):
        filters['platform'] = request.args.get('platform')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    
    meetings = storage.list_meetings(filters)
    return jsonify({'meetings': meetings})


@app.route('/api/meetings', methods=['POST'])
def create_meeting():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        meeting_id = storage.create_meeting(data)
        meeting = storage.get_meeting(meeting_id)
        return jsonify({'meeting': meeting}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/meetings/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    return jsonify({'meeting': meeting})


@app.route('/api/meetings/<meeting_id>', methods=['PATCH'])
def update_meeting(meeting_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    success = storage.update_meeting(meeting_id, data)
    if not success:
        return jsonify({'error': 'Meeting not found'}), 404
    
    meeting = storage.get_meeting(meeting_id)
    return jsonify({'meeting': meeting})


@app.route('/api/meetings/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    success = storage.delete_meeting(meeting_id)
    if not success:
        return jsonify({'error': 'Meeting not found'}), 404
    
    return jsonify({'message': 'Meeting deleted successfully'})


@app.route('/api/meetings/<meeting_id>/transcript', methods=['GET'])
def get_transcript(meeting_id):
    transcript = storage.get_detailed_transcript(meeting_id)
    if not transcript:
        return jsonify({'error': 'Transcript not found'}), 404
    
    return jsonify({'transcript': transcript})


@app.route('/api/meetings/<meeting_id>/summary', methods=['GET'])
def get_summary(meeting_id):
    summary = storage.get_structured_summary(meeting_id)
    if not summary:
        return jsonify({'error': 'Summary not found'}), 404
    
    return jsonify({'summary': summary})


@app.route('/api/meetings/<meeting_id>/action-items/<action_item_id>', methods=['PATCH'])
def update_action_item(meeting_id, action_item_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    success = storage.update_action_item(meeting_id, action_item_id, data)
    if not success:
        return jsonify({'error': 'Action item not found'}), 404
    
    summary = storage.get_structured_summary(meeting_id)
    return jsonify({'summary': summary})


@app.route('/api/meetings/<meeting_id>/recording', methods=['GET'])
def get_recording(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    audio_file_path = meeting.get('audio_file_path')
    if not audio_file_path or not os.path.exists(audio_file_path):
        return jsonify({'error': 'Recording not found'}), 404
    
    return send_file(audio_file_path, as_attachment=False)


@app.route('/api/meetings/<meeting_id>/audio', methods=['GET'])
def get_audio(meeting_id):
    return get_recording(meeting_id)


@app.route('/api/auth/zoom', methods=['GET'])
def zoom_auth():
    if not ZOOM_CLIENT_ID or not ZOOM_CLIENT_SECRET:
        return jsonify({'error': 'Zoom integration not configured'}), 500
    
    zoom = ZoomPlatform(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI)
    
    state = str(uuid.uuid4())
    session['zoom_oauth_state'] = state
    
    auth_url = zoom.get_authorization_url(state=state)
    
    return jsonify({'authorization_url': auth_url})


@app.route('/api/auth/zoom/callback', methods=['GET'])
def zoom_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({'error': 'Authorization code not provided'}), 400
    
    stored_state = session.get('zoom_oauth_state')
    if state != stored_state:
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    try:
        zoom = ZoomPlatform(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI)
        token_data = zoom.authenticate(code)
        
        session['zoom_access_token'] = token_data['access_token']
        session['zoom_refresh_token'] = token_data['refresh_token']
        session['zoom_token_expires_at'] = (
            datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        ).isoformat()
        
        frontend_redirect = request.args.get('redirect_uri', 'http://localhost:3000/meetings')
        return redirect(f"{frontend_redirect}?zoom_auth=success")
    
    except Exception as e:
        return jsonify({'error': f'Failed to authenticate with Zoom: {str(e)}'}), 500


@app.route('/api/meetings/import-zoom', methods=['POST'])
def import_zoom_meeting():
    data = request.get_json()
    
    if not data or 'meeting_id' not in data:
        return jsonify({'error': 'Meeting ID required'}), 400
    
    zoom_meeting_id = data['meeting_id']
    
    access_token = session.get('zoom_access_token')
    if not access_token:
        return jsonify({'error': 'Not authenticated with Zoom'}), 401
    
    try:
        zoom = ZoomPlatform(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI)
        zoom.set_access_token(access_token)
        
        meeting_details = zoom.get_meeting_details(zoom_meeting_id)
        
        recording_filename = f"zoom_{zoom_meeting_id}_{uuid.uuid4().hex[:8]}.m4a"
        recording_path = os.path.join(RECORDINGS_FOLDER, recording_filename)
        
        zoom.download_recording(zoom_meeting_id, recording_path)
        
        participants = zoom.get_participants(zoom_meeting_id)
        
        meeting_data = {
            'title': meeting_details['title'],
            'description': meeting_details['description'],
            'meeting_type': 'online',
            'platform': 'zoom',
            'platform_meeting_id': str(meeting_details['platform_meeting_id']),
            'join_url': meeting_details.get('join_url'),
            'audio_file_path': recording_path,
            'duration': meeting_details['duration'] * 60,
            'status': 'recorded',
            'participants': participants,
            'started_at': meeting_details.get('start_time')
        }
        
        meeting_id = storage.create_meeting(meeting_data)
        meeting = storage.get_meeting(meeting_id)
        
        return jsonify({
            'message': 'Meeting imported successfully',
            'meeting': meeting
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to import Zoom meeting: {str(e)}'}), 500


@app.route('/api/meetings/upload-recording', methods=['POST'])
def upload_recording():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    title = request.form.get('title', 'Uploaded Meeting')
    description = request.form.get('description', '')
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"upload_{uuid.uuid4().hex}_{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(file_path)
        
        meeting_data = {
            'title': title,
            'description': description,
            'meeting_type': 'online',
            'platform': 'upload',
            'audio_file_path': file_path,
            'status': 'recorded'
        }
        
        meeting_id = storage.create_meeting(meeting_data)
        meeting = storage.get_meeting(meeting_id)
        
        return jsonify({
            'message': 'Recording uploaded successfully',
            'meeting': meeting
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to upload recording: {str(e)}'}), 500


@app.route('/api/meetings/<meeting_id>/upload', methods=['POST'])
def upload_to_meeting(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"upload_{meeting_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(file_path)
        
        storage.update_meeting(meeting_id, {
            'audio_file_path': file_path,
            'status': 'recorded'
        })
        
        updated_meeting = storage.get_meeting(meeting_id)
        
        return jsonify({
            'message': 'Audio file uploaded successfully',
            'meeting': updated_meeting
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500


@app.route('/api/meetings/<meeting_id>/participants', methods=['POST'])
def add_participant(meeting_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    success = storage.add_participant(meeting_id, data)
    if not success:
        return jsonify({'error': 'Meeting not found'}), 404
    
    meeting = storage.get_meeting(meeting_id)
    return jsonify({'meeting': meeting})


@app.route('/api/meetings/<meeting_id>/transcribe', methods=['POST'])
def transcribe_meeting(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    audio_file_path = meeting.get('audio_file_path')
    if not audio_file_path or not os.path.exists(audio_file_path):
        return jsonify({'error': 'Audio file not found'}), 404
    
    data = request.get_json() or {}
    service = data.get('service', DEFAULT_TRANSCRIPTION_SERVICE)
    
    if service == 'deepgram':
        api_key = DEEPGRAM_API_KEY
    elif service == 'assemblyai':
        api_key = ASSEMBLYAI_API_KEY
    else:
        return jsonify({'error': f'Unsupported transcription service: {service}'}), 400
    
    if not api_key:
        return jsonify({'error': f'{service} API key not configured'}), 500
    
    try:
        print(f"Starting transcription for {meeting_id} using {service}")
        print(f"Audio file: {audio_file_path}")
        
        # Apply echo reduction for online meetings
        processed_audio_path = audio_file_path
        meeting_type = meeting.get('meeting_type', 'physical')
        
        if meeting_type == 'online':
            print("Applying echo reduction for online meeting...")
            try:
                temp_processed = audio_file_path.replace('.webm', '_echo_reduced.webm')
                processed_audio_path = audio_processor.process_meeting_audio(
                    audio_file_path, 
                    temp_processed, 
                    apply_echo_reduction=True
                )
                print(f"Echo reduction applied, using processed audio: {processed_audio_path}")
            except Exception as e:
                print(f"Echo reduction failed, using original audio: {str(e)}")
                processed_audio_path = audio_file_path
        
        transcriber = WordTimestampTranscriber(service=service, api_key=api_key)
        
        result = transcriber.transcribe_with_timestamps(processed_audio_path)
        print(f"Transcription completed: {len(result.get('segments', []))} segments")
        
        participants = meeting.get('participants', [])
        if participants and isinstance(participants, list) and len(participants) > 0:
            participant_dicts = []
            for i, p in enumerate(participants):
                if isinstance(p, str):
                    participant_dicts.append({'id': f'participant_{i}', 'name': p})
                elif isinstance(p, dict):
                    participant_dicts.append(p)
            
            if participant_dicts:
                result['segments'] = transcriber.map_speakers_to_participants(
                    result['segments'],
                    participant_dicts
                )
        
        transcript_data = {
            'segments': result['segments'],
            'service': service
        }
        
        storage.save_detailed_transcript(meeting_id, transcript_data)
        print(f"Transcript saved for {meeting_id}")
        
        unique_speakers = set()
        for segment in result['segments']:
            speaker = segment.get('speaker_name') or segment.get('speaker')
            print(f"DEBUG: Found speaker in segment: {speaker}")
            if speaker:
                unique_speakers.add(speaker)
        
        print(f"DEBUG: Total unique speakers found: {unique_speakers}")
        
        if unique_speakers:
            speaker_list = sorted(list(unique_speakers))
            update_result = storage.update_meeting(meeting_id, {'participants': speaker_list})
            print(f"DEBUG: Update meeting result: {update_result}")
            print(f"Updated participants with {len(speaker_list)} speakers: {speaker_list}")
            
            updated_meeting = storage.get_meeting(meeting_id)
            print(f"DEBUG: Participants after update: {updated_meeting.get('participants')}")
        
        transcript = storage.get_detailed_transcript(meeting_id)
        
        return jsonify({
            'message': 'Transcription completed successfully',
            'transcript': transcript
        }), 200
    
    except Exception as e:
        print(f"Transcription error for {meeting_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500


@app.route('/api/meetings/<meeting_id>/summarize', methods=['POST'])
def summarize_meeting(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    transcript = storage.get_detailed_transcript(meeting_id)
    if not transcript or not transcript.get('segments'):
        return jsonify({'error': 'Transcript not found or empty'}), 404
    
    data = request.get_json() or {}
    service = data.get('service', DEFAULT_SUMMARIZATION_SERVICE)
    template = data.get('template', 'general')
    
    if service == 'openai':
        api_key = OPENAI_API_KEY
    elif service == 'deepseek':
        api_key = DEEPSEEK_API_KEY
    else:
        return jsonify({'error': f'Unsupported summarization service: {service}'}), 400
    
    if not api_key:
        return jsonify({'error': f'{service} API key not configured'}), 500
    
    try:
        summarizer = MeetingSummarizer(service=service, api_key=api_key)
        
        meeting_title = meeting.get('title', 'Meeting')
        segments = transcript['segments']
        
        summary_data = summarizer.generate_structured_summary(
            transcript_segments=segments,
            meeting_title=meeting_title,
            template=template
        )
        
        summary_data['template'] = template
        summary_data['meeting_id'] = meeting_id
        
        storage.save_structured_summary(meeting_id, summary_data)
        
        saved_summary = storage.get_structured_summary(meeting_id)
        
        return jsonify({
            'message': 'Summary generated successfully',
            'summary': saved_summary
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500


@app.route('/api/meetings/<meeting_id>/summarize-structured', methods=['POST'])
def summarize_structured(meeting_id):
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    transcript = storage.get_detailed_transcript(meeting_id)
    if not transcript or not transcript.get('segments'):
        return jsonify({'error': 'Transcript not found or empty'}), 404
    
    data = request.get_json() or {}
    service = data.get('service', DEFAULT_SUMMARIZATION_SERVICE)
    template = data.get('template', 'general')
    
    if service == 'openai':
        api_key = OPENAI_API_KEY
    elif service == 'deepseek':
        api_key = DEEPSEEK_API_KEY
    else:
        return jsonify({'error': f'Unsupported summarization service: {service}'}), 400
    
    if not api_key:
        return jsonify({'error': f'{service} API key not configured'}), 500
    
    try:
        summarizer = MeetingSummarizer(service=service, api_key=api_key)
        
        meeting_title = meeting.get('title', 'Meeting')
        segments = transcript['segments']
        
        summary_data = summarizer.generate_structured_summary(
            transcript_segments=segments,
            meeting_title=meeting_title,
            template=template
        )
        
        summary_data['template'] = template
        summary_data['meeting_id'] = meeting_id
        
        storage.save_structured_summary(meeting_id, summary_data)
        
        saved_summary = storage.get_structured_summary(meeting_id)
        
        return jsonify({
            'message': 'Summary generated successfully',
            'summary': saved_summary
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Summarization failed: {str(e)}'}), 500


@app.route('/api/bots/start', methods=['POST'])
def start_bot():
    data = request.get_json()
    
    if not data or 'meeting_id' not in data or 'meeting_url' not in data:
        return jsonify({'error': 'meeting_id and meeting_url required'}), 400
    
    meeting_id = data['meeting_id']
    meeting_url = data['meeting_url']
    bot_name = data.get('bot_name', 'MeriTel Bot')
    
    meeting = storage.get_meeting(meeting_id)
    if not meeting:
        return jsonify({'error': 'Meeting not found'}), 404
    
    try:
        success = bot_manager.start_bot(meeting_id, meeting_url, bot_name)
        
        if not success:
            return jsonify({'error': 'Bot already active for this meeting'}), 400
        
        storage.update_meeting(meeting_id, {'status': 'live', 'join_url': meeting_url})
        
        return jsonify({
            'message': 'Bot started successfully',
            'meeting_id': meeting_id,
            'status': 'live'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to start bot: {str(e)}'}), 500


@app.route('/api/bots/<meeting_id>/stop', methods=['POST'])
def stop_bot(meeting_id):
    try:
        recording_path = bot_manager.stop_bot(meeting_id)
        
        if recording_path:
            storage.update_meeting(meeting_id, {
                'status': 'recorded',
                'audio_file_path': recording_path
            })
        else:
            storage.update_meeting(meeting_id, {'status': 'completed'})
        
        return jsonify({
            'message': 'Bot stopped successfully',
            'meeting_id': meeting_id,
            'recording_path': recording_path
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to stop bot: {str(e)}'}), 500


@app.route('/api/bots/<meeting_id>/status', methods=['GET'])
def get_bot_status(meeting_id):
    status = bot_manager.get_bot_status(meeting_id)
    return jsonify(status)


@app.route('/api/bots/active', methods=['GET'])
def list_active_bots():
    bots = bot_manager.list_active_bots()
    return jsonify({'bots': bots})


@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'data': 'Connected to MeriTel server'})


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")


@socketio.on('join_meeting')
def handle_join_meeting(data):
    meeting_id = data.get('meeting_id')
    if meeting_id:
        join_room(meeting_id)
        print(f"Client {request.sid} joined meeting room {meeting_id}")
        emit('joined_meeting', {'meeting_id': meeting_id})


@socketio.on('leave_meeting')
def handle_leave_meeting(data):
    meeting_id = data.get('meeting_id')
    if meeting_id:
        leave_room(meeting_id)
        print(f"Client {request.sid} left meeting room {meeting_id}")


def broadcast_transcript_update(meeting_id, transcript_data):
    socketio.emit('transcript_update', {
        'meeting_id': meeting_id,
        'transcript': transcript_data
    }, room=meeting_id)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
