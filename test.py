import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")  # or paste directly for test
print(f"HF_TOKEN: {'✅ Set' if HF_TOKEN else '❌ Missing'} (Length: {len(HF_TOKEN) if HF_TOKEN else 0})")
API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": "This is a startup pitch for an AI-powered healthcare platform."
}

response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

print("Status code:", response.status_code)
print("Response:", response.json())
