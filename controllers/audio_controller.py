from flask import Blueprint,request, jsonify
from services.audio_service import main
audio_bp = Blueprint('audio_bp', __name__)
import os

@audio_bp.route('/audio', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # שמירת הקובץ לנתיב המתאים בתיקיית audios
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audio_dir = os.path.join(project_root, "audios")
    os.makedirs(audio_dir, exist_ok=True)
    file_path = os.path.join(audio_dir, file.filename)
    file.save(file_path)

    # הרצת הפונקציה על הקובץ שנשמר
    result = main(file_path)
    return jsonify({"message": "Task summarized successfully", "summary": result}), 200