import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key:
    print(f"✅ API key found: {api_key[:10]}...")
else:
    print("❌ API key NOT found!")
    print("Current directory:", os.getcwd())
    print(".env exists?", os.path.exists(".env"))