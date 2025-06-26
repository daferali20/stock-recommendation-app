import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# إعدادات API
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"
BASE_URL = "https://financialmodelingprep.com/api/v3"

# إعدادات Telegram Bot
TELEGRAM_BOT_TOKEN = "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"
TELEGRAM_CHAT_ID = "@D_Option"
STOCKS_PER_MESSAGE = 15
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

class TelegramSender:
    def __init__(self):
        self.base_url = TELEGRAM_API_URL
        self.timeout = 15
        self.delay = 1

    def send_message(self, message):
        try:
            time.sleep(self.delay)
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
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
    
    # الرسالة الختامية
    footer = "\n<b>📊 ملخص إحصائي:</b>\n"
    if 'dividendYield' in df.columns:
        footer += f"• متوسط العائد: {df['dividendYield'].mean():.2f}%\n"
    if 'price' in df.columns:
        footer += f"• متوسط السعر: ${df['price'].mean():.2f}\n"
    footer += "\n⚡ تم الإنشاء بواسطة Stock Screener"
    messages.append(footer)
    
    return messages

# واجهة Streamlit
st.set_page_config(page_title="مصفاة الأسهم", layout="wide")
st.title('📈 مصفاة الأسهم (عائد + نمو)')

# ... (بقية كود واجهة المستخدم كما هو)

if st.button("🔍 بدء البحث", type="primary"):
    with st.spinner("جاري تحليل بيانات السوق..."):
        data = get_stock_screener(params)
        
        if data is None:
            st.error("تعذر الاتصال بمصدر البيانات")
        elif not data:
            st.warning("لا توجد نتائج مطابقة للمعايير")
        else:
            df = pd.DataFrame(data)
            st.success(f"تم تحديد {len(df)} سهماً مؤهلاً")
            
            # ... (عرض النتائج كما هو)
                
                with col2:
                    if telegram_enabled and st.button("📤 إرسال إلى Telegram", type="secondary"):
                        with st.spinner(f"جاري إعداد {len(df)} سهماً في مجموعات..."):
                            try:
                                telegram = TelegramSender()
                                messages = prepare_telegram_messages(df, params, telegram_message)
                                results = telegram.send_batch(messages)
                                
                                success_count = sum(1 for r in results if r.get('ok'))
                                if success_count == len(messages):
                                    st.success(f"تم إرسال {len(messages)} رسالة بنجاح!")
                                    st.balloons()
                                else:
                                    failed = len(messages) - success_count
                                    st.warning(f"تم إرسال {success_count} رسالة، وفشل {failed}")
                            except Exception as e:
                                st.error(f"خطأ غير متوقع: {str(e)}")
