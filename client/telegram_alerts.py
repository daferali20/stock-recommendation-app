import requests
import time

class TelegramSender:
    def __init__(self, bot_token, chat_id, delay=1, timeout=15):
        self.base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.chat_id = chat_id
        self.timeout = timeout
        self.delay = delay

    def send_message(self, message):
        try:
            time.sleep(self.delay)
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
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
                "details": "حدث خطأ غير متوقع"
            }

    def send_batch(self, messages):
        results = []
        for message in messages:
            result = self.send_message(message)
            results.append(result)
        return results
