# telegram_alerts.py
import requests
import time

class TelegramSender:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"
        self.chat_id = chat_id or "@D_Option"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.timeout = 15
        self.delay = 1

    def send_message(self, message):
        try:
            time.sleep(self.delay)
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return {"ok": True, "response": response.json()}
            else:
                return {"ok": False, "error": f"HTTP {response.status_code}", "details": response.text}
        except Exception as e:
            return {"ok": False, "error": str(e), "details": "Unexpected error"}

    def send_batch(self, messages):
        results = []
        for message in messages:
            results.append(self.send_message(message))
        return results
