import requests
import urllib.parse

def test_pollinations_text():
    prompt = "請寫一段關於賽博龐克城市的短文，約100字。"
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    try:
        res = requests.get(url, timeout=30)
        print("Status:", res.status_code)
        print("Response:", res.text)
    except Exception as e:
        print("Error:", e)

test_pollinations_text()
