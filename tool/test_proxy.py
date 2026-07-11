import os
import requests
import time
from google import genai
from dotenv import load_dotenv

load_dotenv('.env')
api_key = os.getenv('GEMINI_API_KEYS').split(',')[0]

def get_proxies():
    print("Fetching free proxies...")
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=all&ssl=yes&anonymity=all"
    res = requests.get(url)
    proxies = [p for p in res.text.split("\r\n") if p]
    return proxies

proxies = get_proxies()
print(f"Found {len(proxies)} proxies. Testing...")

for p in proxies[:10]:
    print(f"Testing proxy: {p}")
    os.environ["HTTP_PROXY"] = f"http://{p}"
    os.environ["HTTPS_PROXY"] = f"http://{p}"
    
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="say hello"
        )
        print("Success! Response:", response.text)
        break
    except Exception as e:
        print("Failed:", e)
    
    # reset env
    del os.environ["HTTP_PROXY"]
    del os.environ["HTTPS_PROXY"]
