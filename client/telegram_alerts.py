import requests
import time

TELEGRAM_BOT_TOKEN = "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"
TELEGRAM_CHAT_ID = "@D_Option"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

class TelegramSender:
    def __init__(self):
        self.base_url = TELEGRAM_API_URL
        self.timeout = 10
        self.delay = 1

    def send_message(self, message):
        try:
            time.sleep(self.delay)
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",  # أكثر أمانًا من HTML
                "disable_web_page_preview": True
            }
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return {"ok": True, "response": response.json()}
            else:
                return {
                    "ok": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "details": "Exception raised"
            }

    def send_batch(self, messages):
        results = []
        for message in messages:
            result = self.send_message(message)
            results.append(result)
        return results
