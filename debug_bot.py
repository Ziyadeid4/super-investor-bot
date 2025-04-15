import requests
import time
from datetime import datetime

bot_token = "7866537477:AAE_lT0ftBIpmq7NPBa0j8MImbihhjAkO4g"
chat_id = "390856599"

def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg}
    r = requests.post(url, data=data)
    print(f"⏱️ {datetime.now()} | Status: {r.status_code}")
    print(r.text)

while True:
    print("🔄 البوت يشتغل الآن...")
    send_to_telegram("✅ البوت يشتغل ويرسل الآن كل دقيقة")
    time.sleep(60)
