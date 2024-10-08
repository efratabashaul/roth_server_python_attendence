import openai
import os
from flask import Blueprint

# הגדרת קונטרולר בשם 'user'
audio_bp = Blueprint('user_bp', __name__)
# הגדר את מפתח ה-API שלך מ-OpenAI


def transcribe_audio(file_path):
    try:
        # פותחים את קובץ האודיו
        with open(file_path, 'rb') as audio_file:
            # משתמשים ב-OpenAI API לתמלול השיחה
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="he"  # קידוד לשפה עברית
            )

        return transcript['text']

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


# דוגמת קריאה לפונקציה
file_path = "conversation_hebrew.wav"  # נתיב לקובץ האודיו שלך
transcript_text = transcribe_audio(file_path)

if transcript_text:
    print("תמלול השיחה בעברית:")
    print(transcript_text)
else:
    print("הייתה בעיה בתמלול.")
