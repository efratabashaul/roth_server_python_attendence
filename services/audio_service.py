import openai
import os
from dotenv import load_dotenv
import noisereduce as nr
import librosa
import soundfile as sf
import requests

load_dotenv()

openai.api_key = os.getenv('GPT_API_KEY')


def remove_background_noise(file_path):
    # חילוץ שם הקובץ המקורי והסיומת
    base_name = os.path.basename(file_path)  # לדוגמה: "conversation_hebrew.wav"
    file_name, file_ext = os.path.splitext(base_name)  # file_name = "conversation_hebrew", file_ext = ".wav"

    # יצירת נתיב חדש בתיקיית 'AUDIOS' עם תוספת "_clean"
    cleaned_file_name = f"{file_name}_clean{file_ext}"
    output_dir = os.path.join(os.getcwd(), "../audios")  # תיקיית AUDIOS בתיקייה הראשית
    output_path = os.path.join(output_dir, cleaned_file_name)
    # קריאת האודיו באמצעות librosa
    data, rate = librosa.load(file_path, sr=None)

    # הסרת רעשי רקע באמצעות NoiseReduce
    reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # שמירת האודיו הנקי לתוך הנתיב החדש
    sf.write(output_path, reduced_noise, rate)

    return output_path


def transcribe_audio(file_path):
    token = f"Bearer {os.getenv('GPT_API_KEY')}"  # ודא שמפתח ה-API מוגדר כראוי

    url = "https://api.openai.com/v1/audio/transcriptions"

    headers = {
        "Authorization": token  # אין צורך להגדיר Content-Type ידנית, requests יטפל בזה
    }
    prompt = f"""
        This is a conversation between a lawyer and a client about customer service issues.
        Please summarize the main points of the conversation and identify any customer concerns or legal questions.

        Conversation:
        {conversation_text}

        Summary and identified issues:
        """
    # פותחים את קובץ האודיו ושולחים את הבקשה
    with open(file_path, "rb") as file:
        files = {
            "file": (os.path.basename(file_path), file, "audio/mp3")  # סוג הקובץ - MP3 במקרה הזה
        }
        instructions = """
        הנחיות:
        1. השיחה עוסקת בעניין של אורך הקלטה.
        2. השתמש בסימני פיסוק נכונים.
        3. תכלול גם רעשים נמוכים.
        """

        data = {
            "model": "whisper-1",
            "response_format": "json",
            "language": "he",
            "timestamp_granularities": ["word"],
            "instructions": instructions  # הנחיות כאן
        }

        response = requests.post(url, headers=headers, data=data, files=files)

    # בודקים אם הבקשה הצליחה
    if response.status_code == 200:
        response_json = response.json()  # מפרשים את התשובה כ-JSON
        print(response_json)  # מדפיסים את כל התשובה
    else:
        print(f"Error: {response.status_code}, {response.text}")  # מדפיסים את השגיאה אם התשובה לא תקינה

    return response.text
    #try:
        # פותחים את קובץ האודיו

            # משתמשים ב-OpenAI API לתמלול השיחה
           # response = openai.Audio.transcribe(
            #    model="whisper-1",  # ודא שהמודל הנכון נבחר
             #   file=audio_file,
              #  response_format="text",
               # timestamp_granularities=["word"],
               # language="he"  # שפת הקלט היא עברית
            #)
            # הדפס את התגובה המתקבלת מה-API לצורך אבחון
            #print("Response from OpenAI API:", response)

            # בדיקת תגובה וחילוץ טקסט
            #if isinstance(response, dict) and 'text' in response:
            #   return response['text']
            #else:
            #   print("בעיה בקבלת התשובה מה-API. התגובה המלאה: ", response)
            #return None
  #  except openai.error.OpenAIError as e:
   #     print(f"OpenAI API error: {e}")
    #    return None
    #except Exception as e:
     #   print(f"General error during transcription: {e}")
      #  return None


# דוגמת קריאה לפונקציה
#file_path = '../audios/someone-just-made-me-very-angry-child-spoken-204916.mp3' # נתיב לקובץ האודיו שלך
file_path = '../audios/‏‏WhatsApp Ptt 2024-10-07 at 11.41.48 - עותק.mp3' # נתיב לקובץ האודיו שלך

cleaned_audio = remove_background_noise(file_path)
transcript_text = transcribe_audio(cleaned_audio)

if transcript_text:
    print("תמלול השיחה בעברית:")
    print(transcript_text)
else:
    print("הייתה בעיה בתמלול.")