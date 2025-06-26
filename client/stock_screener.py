import streamlit as st
import requests
import pandas as pd
import html
from datetime import datetime
from telegram_alerts import TelegramSender  # استيراد الكلاس الخارجي

# إعدادات API
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"
BASE_URL = "https://financialmodelingprep.com/api/v3"

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
        st.error(f"خطأ في الاتصال بـ API: {str(e)}")
        return None

def prepare_telegram_messages(df, params, custom_message):
    MAX_LENGTH = 3500
    messages = []

    df = df.head(5)  # فقط أول 5 أسهم

    header = f"📊 {custom_message}\n"
    header += f"⏳ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    header += f"🔍 الشروط: عائد > {params['dividendYieldMoreThan']}%، نمو > {params['revenueGrowthMoreThan']}%\n\n"

    current_message = header
    for _, row in df.iterrows():
        try:
            symbol = str(row.get("symbol", "N/A"))
            dividend = f"{row.get('dividendYield', 0):.2f}%"
            growth = f"{row.get('revenueGrowth', 0):.2f}%"

            stock_info = f"{symbol} | عائد: {dividend} | نمو: {growth}\n"

            if len(current_message) + len(stock_info) > MAX_LENGTH:
                messages.append(current_message.strip())
                current_message = ""

            current_message += stock_info
        except Exception as e:
            continue

    if current_message.strip():
        messages.append(current_message.strip())

    footer = "\n⚡ تم الإنشاء تلقائيًا"
    messages.append(footer)

    return messages

# ---------------- Streamlit UI ----------------

st.set_page_config(page_title="مصفاة الأسهم", layout="wide")
st.title("📈 مصفاة الأسهم (عائد + نمو)")

col1, col2 = st.columns(2)

with col1:
    dividend = st.slider("🔹 الحد الأدنى للعائد (%)", 0.0, 10.0, 3.0, 0.1)

with col2:
    revenue_growth = st.slider("🔹 الحد الأدنى لنمو الإيرادات (%)", 0.0, 50.0, 10.0, 0.5)

telegram_enabled = st.checkbox("📩 تفعيل الإرسال إلى تيليجرام", value=True)
telegram_message = st.text_input("💬 رسالة مخصصة لتيليجرام", "الأسهم ذات عائد مرتفع ونمو جيد")

params = {
    "dividendYieldMoreThan": 0.0,  # اجعلها 0 لتضمن ظهور بيانات
    "revenueGrowthMoreThan": 0.0,
    "limit": 10,
    "exchange": "NASDAQ"
}


# إنشاء كائن TelegramSender
# تعريف كائن التليجرام مرة واحدة
telegram = TelegramSender()

# زر إرسال أول رسالة فقط
if messages and st.button("📤 إرسال أول رسالة فقط"):
    with st.spinner("📤 جاري إرسال الرسالة الأولى..."):
        result = telegram.send_message(messages[0])
        if result.get("ok"):
            st.success("✅ تم إرسال الرسالة بنجاح!")
        else:
            st.error(f"❌ فشل الإرسال: {result.get('error')} | التفاصيل: {result.get('details')}")

# زر إرسال كل الرسائل
if telegram_enabled and st.button("📤 إرسال كل الرسائل إلى Telegram"):
    with st.spinner("📡 جاري الإرسال إلى تيليجرام..."):
        results = telegram.send_batch(messages)
        success_count = sum(1 for r in results if r.get("ok"))

        if success_count == len(messages):
            st.success(f"✅ تم إرسال كل ({len(messages)}) الرسائل بنجاح!")
            st.balloons()
        else:
            st.warning(f"⚠️ تم إرسال {success_count} من {len(messages)} رسالة فقط.")
            for i, result in enumerate(results):
                if not result.get("ok"):
                    st.error(f"❌ فشل في الرسالة {i+1}: {result.get('error')} | التفاصيل: {result.get('details')}")
