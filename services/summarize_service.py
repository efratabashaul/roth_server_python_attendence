from transformers import AutoTokenizer, pipeline, BertModel
import random
import torch
import pickle
import re
import os
import faiss
import numpy as np
import cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
import ssl
import re
from dateutil import parser
from datetime import datetime
from dateutil.parser import ParserError
from dotenv import load_dotenv
import openai
import asyncio
load_dotenv()

openai.api_key = os.getenv('GPT_API_KEY') # הכנס כאן את המפתח שלך


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

os.environ['CURL_CA_BUNDLE'] = ''



def main(text):
    if text is not None:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": (
                        "Please organize the following tasks in a concise and relevant manner. "
                        "Remove any irrelevant content and ensure that only actual tasks are included, "
                        "such as removing phrases like 'I drank coffee'.\n\n"
                        "If there are no valid tasks, respond with 'NO_VALID_TASKS_FOUND'.\n\n"
                        f"Tasks: {text}"
                    ),
                },
            ],
        )
        answer = completion['choices'][0]['message']['content']
        # Return a constant response if no valid tasks are found
        if "NO_VALID_TASKS_FOUND" in answer:
            return "NO_VALID_TASKS_FOUND"
        return answer
    return None

#text = "יצאתי להפסקה, וכתבתי את הפונקציה הנדרשת"
text = "ללללללל"

#text = "אני קצת שיחקתי בPLAYGROUND של GPT, סידרתי ובניתי את התיקיות של צד השרת של פייתון יצאתי להפסקה קצרה. עשיתי את המשימה של סיכום משימות העבדים בAI עי API של GPT וכעת בודקת את זה."
# result = main(text)
print("result: ")
# print(result)
#לעשות שתמיד יחזיר אותו דבר באם כתבו שטויות