import streamlit as st
import requests
import pandas as pd
import time  # المكتبة المنسية
from datetime import datetime

# إعدادات API
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"
BASE_URL = "https://financialmodelingprep.com/api/v3"

# إعدادات Telegram Bot
TELEGRAM_BOT_TOKEN = "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"
TELEGRAM_CHAT_ID = "@D_Option"
STOCKS_PER_MESSAGE = 15  # عدد الأسهم في كل رسالة
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"  # تعريف كامل لرابط API

class TelegramSender:
    def __init__(self):
        self.base_url = TELEGRAM_API_URL
        self.timeout = 15
        self.delay = 1  # تأخير بين الرسائل بالثواني

    def send_message(self, text):
        try:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            response = requests.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"خطأ في إرسال الرسالة: {str(e)}")
            return {"ok": False, "description": str(e)}

def get_stock_screener(params):
    url = f"{BASE_URL}/stock-screener?apikey={API_KEY}"
    for key, value in params.items():
        if value is not None:
            url += f"&{key}={value}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"خطأ في الاتصال بAPI: {str(e)}")
        return None

def prepare_telegram_messages(df, params, custom_message):
    telegram = TelegramSender()
    messages = []
    
    # الرسالة الرئيسية
    header = f"<b>📊 {custom_message}</b>\n"
    header += f"⏳ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    header += "<b>🔍 معايير البحث:</b>\n"
    header += f"- العائد: {params['dividendYieldMoreThan']}%\n"
    header += f"- نمو الإيرادات: {params['revenueGrowthMoreThan']}%\n"
    header += f"- عدد الأسهم: {len(df)}\n\n"
    messages.append(header)
    
    # تقسيم الأسهم إلى مجموعات
    for i in range(0, len(df), STOCKS_PER_MESSAGE):
        chunk = df.iloc[i:i+STOCKS_PER_MESSAGE]
        message = f"<b>📌 مجموعة الأسهم {i//STOCKS_PER_MESSAGE + 1}</b>\n\n"
        
        for _, row in chunk.iterrows():
            stock_info = f"<code>{row.get('symbol', 'N/A')}</code> | "
            stock_info += f"{row.get('companyName', '')[:20]}...\n"
            
            if 'price' in row:
                stock_info += f"💰 ${row['price']:.2f} | "
            if 'dividendYield' in row:
                stock_info += f"📈 {row['dividendYield']:.2f}% | "
            if 'revenueGrowth' in row:
                stock_info += f"📊 {row['revenueGrowth']:.2f}%\n"
            
            message += stock_info + "――――――――――\n"
        
        messages.append(message)
        time.sleep(telegram.delay)  # استخدام التأخير هنا
    
    # الرسالة الختامية
    footer = "\n<b>📊 ملخص إحصائي:</b>\n"
    if 'dividendYield' in df.columns:
        footer += f"• متوسط العائد: {df['dividendYield'].mean():.2f}%\n"
    if 'price' in df.columns:
        footer += f"• متوسط السعر: ${df['price'].mean():.2f}\n"
    footer += "\n⚡ تم الإنشاء بواسطة Stock Screener"
    messages.append(footer)
    
    return messages

# بقية الكود كما هو ...
