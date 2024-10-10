import openai
import os
from dotenv import load_dotenv
import noisereduce as nr
import librosa
import soundfile as sf
import requests
from pydub import AudioSegment
from pydub.silence import split_on_silence
load_dotenv()

openai.api_key = os.getenv('GPT_API_KEY')



def remove_background_noise(file_path):
    """
    פונקציה להסרת רעשי רקע מקובץ האודיו ושמירת הקובץ הנקי בתיקיית הפרויקט הראשית (python_server/audios)
    """
    # חילוץ שם הקובץ המקורי והסיומת
    base_name = os.path.basename(file_path)  # לדוגמה: "conversation_hebrew.wav"
    file_name, file_ext = os.path.splitext(base_name)  # file_name = "conversation_hebrew", file_ext = ".wav"

    # עלייה בתיקייה אחת למעלה כדי להגיע ל-python_server
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # תיקיית הפרויקט הראשית 'python_server'
    output_dir = os.path.join(project_root, "audios")  # תיקיית 'audios' בתוך python_server
    os.makedirs(output_dir, exist_ok=True)  # יצירת תיקייה אם לא קיימת

    # יצירת שם הקובץ הנקי
    cleaned_file_name = f"{file_name}_clean{file_ext}"
    output_path = os.path.join(output_dir, cleaned_file_name)

    # קריאת האודיו באמצעות librosa
    data, rate = librosa.load(file_path, sr=None)

    # הסרת רעשי רקע באמצעות NoiseReduce
    reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # שמירת האודיו הנקי לתוך הנתיב החדש
    sf.write(output_path, reduced_noise, rate)

    print(f"Cleaned audio saved to: {output_path}")
    return output_path


def transcribe_audio(file_path):
    """
    פונקציה לתמלול קובץ אודיו באמצעות OpenAI Whisper API
    """
    token = f"Bearer {os.getenv('GPT_API_KEY')}"
    url = "https://api.openai.com/v1/audio/transcriptions"

    headers = {
        "Authorization": token
    }

    with open(file_path, "rb") as file:
        files = {
            "file": (os.path.basename(file_path), file, "audio/mp3")
        }

        instructions = """
        הנחיות:
        1. מדובר בשיחת שירות לקוחות חברת עורכי דין.
        2. נא לסכם את עיקרי השיחה -תשובות הלקוח על פרטיו האישיים.
        3. השיחה נוגעת בתאונת דרכים ובמצב הרפואי של הלקוח ובמסמכים שהוא נדרש להגיש.
        4. נא לדייק בזיהוי פרטים חשובים שנוגעים למצבו המשפטי והרפואי של הלקוח.
        """

        data = {
            "model": "whisper-1",
            "response_format": "json",
            "language": "he",
          #  "instructions": instructions
        }

        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        return response_json['text']  # מחזיר את הטקסט המותמלל
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def split_and_transcribe(file_path, min_silence_len=1000, silence_thresh=-40, segment_duration=1):
    """
    פונקציה לחיתוך האודיו לפי שקטים ושליחת כל מקטע לתמלול
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist at path: {file_path}")

    # טוענים את קובץ האודיו
    try:
        file = AudioSegment.from_file(file_path)  # הספרייה תזהה אוטומטית את סוג הקובץ לפי הסיומת
        print("File loaded successfully.")
    except Exception as e:
        print(f"Failed to load file: {e}")
        return

    base_name = os.path.basename(file_path)

    file_name, file_ext = os.path.splitext(base_name)

    # חלוקת הזמן למילישניות (לפי אורך המקטע בדקות)
    segment_duration_ms = segment_duration * 60 * 1000

    # חלוקה לפי שקטים עם הגדרות מותאמות אישית
    audio_chunks = split_on_silence(
        file,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=500
    )

    # עלייה בתיקייה אחת למעלה כדי להגיע ל-python_server
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # תיקיית הפרויקט הראשית 'python_server'
    output_dir = os.path.join(project_root, "segments")  # תיקיית 'audios' בתוך python_server
    os.makedirs(output_dir, exist_ok=True)  # יצירת תיקייה אם לא קיימת

    current_segment = AudioSegment.empty()
    segment_count = 0
    transcriptions = []  # רשימת התמלולים

    for i, chunk in enumerate(audio_chunks):
        current_segment += chunk

        # אם המקטע הנוכחי הגיע לאורך שנקבע או אם זה הקטע האחרון
        if len(current_segment) >= segment_duration_ms or i == len(audio_chunks) - 1:
            segment_filename = f"{file_name}_part_{segment_count}.mp3"
            segment_path = os.path.join(output_dir, segment_filename)
            current_segment.export(segment_path, format="mp3")
            print(f"Saved segment: {segment_filename}")

            # תמלול המקטע ושמירה ברשימה
            transcription = transcribe_audio(segment_path)
            if transcription:
                transcriptions.append(transcription)

            # איפוס המקטע
            current_segment = AudioSegment.empty()
            segment_count += 1

    # איחוד כל הטקסטים מהתמלול לקובץ אחד
    full_transcription = "\n".join(transcriptions)
    return full_transcription
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



system_prompt = """
אתה הולך לקבל תמלול ראשוני של שיחה בין נציג שירות לקוחות ללקוח בחברת עורכי דין נתנאל רוט.
- נציגת שירות הלקוחות תמיד מציגה את עצמה בשם רוני ואומרת שהיא ממשרד עו"ד נתנאל רוט.
- השיחות מתחילות לעיתים קרובות במשפט כמו- 'ראיתי שפנית אלינו, אז איפה זה עומד?', וכדומה.
- נציגת שירות הלקוחות שואלת שאלות לגבי פרטים אישיים ומסמכים משפטיים של הלקוח.
- הלקוח בדרך כלל עונה על השאלות,  ושואל שאלות נוספות בנוגע למצבו המשפטי או הרפואי.
- עורך הדין עשוי להיכנס לשיחה כאשר יש שאלות מקצועיות יותר, ולספק תשובות משפטיות.
עליך לתקן את התמלול, לוודא שכל דובר ברור, ולשפר את השיחה כך שתהיה זורמת, מובנת וברורה תוך שמירה על כל המידע מהלקוח, בלי להוריד ולהוסיף כל מידע חשוב, אלא רק לתקן את מה שיש!-שמירה על המשמעות המשפטית והרפואית, תהיה מדויק כמה שאתה יכול!.
"""
def generate_corrected_transcript(temperature, system_prompt, audio_file):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": split_and_transcribe(audio_file)
            }
        ]
    )
    return response.choices[0].message.content



def main(file_path):
    corrected_text = generate_corrected_transcript(0, system_prompt, file_path)
    if corrected_text:
        print("תמלול השיחה בעברית:")
        print(corrected_text)
    else:
        print("הייתה בעיה בתמלול.")
    return corrected_text

# דוגמת קריאה לפונקציה
#file_path = '../audios/someone-just-made-me-very-angry-child-spoken-204916.mp3' # נתיב לקובץ האודיו שלך
#file_path = '../audios/‏‏WhatsApp Ptt 2024-10-07 at 11.41.48 - עותק.mp3' # נתיב לקובץ האודיו שלך
#file_path='../audios/202410071259060283eqvcg0klhg3372-vc1531-p0EOP1MD-972547421225.mp3'#יחסית טוב אסם
#file_path = '../audios/2024100712285802830w0uxl0cfspn6k-vc1531-p0EOP1MD-972542279791.mp3'#יחסית טוב תבדוק עם העורך דין-ביקור אתמול
#file_path='../audios/202410071234220283je478f0a5jmzgu-vc1531-p0EOP1MD-972509031043.mp3'#-5 סגמנטים
#file_path='../audios/2024100807193102833nhp1i0x9fj5cn-vc1531-p0EOP1MD-972542044385.mp3'#-מלחמה
#file_path='../audios/202410080643070283053esj0e5jffrf-vc1531-p0EOP1MD-972523103311.mp3'
#file_path='../audios/202410080643070283053esj0e5jffrf-vc1531-p0EOP1MD-972523103311.wav'
#file_path='../audios/2024100807300802836mny90ik9d2ptz-vc1531-p0EOP1MD-972585519001.mp3'#כתף-יחסית טוב
#file_path='../audios/20241007124551028321pi0hyjxu76ym-vc1531-p0EOP1MD-972586869132.mp3'#7 יחסית טוב עו"ד
#cleaned_audio = remove_background_noise(file_path)
#main(file_path)

