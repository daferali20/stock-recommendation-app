import streamlit as st
import requests
import pandas as pd
import html
from datetime import datetime

from telegram_alerts import TelegramSender  # تأكد أن هذا الملف موجود ومهيأ

# إعدادات API


# إعدادات Alpha Vantage
API_KEY = "S6G0CLDFPAW2NKNA"  # استبدل هذا بالمفتاح الحقيقي
BASE_URL = "https://www.alphavantage.co/query"

# دالة للحصول على بيانات يومية للسهم من Alpha Vantage
def get_daily_stock_data(symbol):
    url = f"{BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=compact"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "Time Series (Daily)" in data:
            df = pd.DataFrame(data['Time Series (Daily)']).T
            df = df.astype(float)
            df.index = pd.to_datetime(df.index)
            return df
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"خطأ في الاتصال بـ Alpha Vantage API: {str(e)}")
        return None

def prepare_telegram_messages(df, params, custom_message):
    MAX_LENGTH = 3500
    messages = []

    # فقط أول 5 أسهم
    df = df.head(5)

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
                messages.append(current_message)
                current_message = ""

            current_message += stock_info
        except Exception:
            continue

    if current_message.strip():
        messages.append(current_message.strip())

    footer = "\n⚡ تم الإنشاء تلقائيًا"
    messages.append(footer)

    return messages

# --- واجهة Streamlit ---
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
    "dividendYieldMoreThan": dividend,
    "revenueGrowthMoreThan": revenue_growth,
    "limit": 100,
    "exchange": "NASDAQ"
}

# أنشئ كائن TelegramSender مرة واحدة
telegram = TelegramSender()

# زر اختبار تيليجرام
if st.button("📨 اختبار إرسال Telegram"):
    test_result = telegram.send_message("✅ اختبار مباشر من تطبيق Streamlit")
    st.write("📬 نتيجة الاختبار:", test_result)

if st.button("🔍 بدء البحث", type="primary"):
    with st.spinner("جاري تحليل بيانات السوق..."):
        df_dict = {}
        for symbol in symbols:
            df = get_daily_stock_data(symbol)
            if df is not None:
                df_dict[symbol] = df

            # تنظيف الأعمدة النصية لتجنب أخطاء pyarrow
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)

            st.success(f"✅ تم تحديد {len(df)} سهماً مؤهلاً")
            st.dataframe(df)

            # توليد الرسائل وتخزينها في حالة الجلسة
            st.session_state['messages'] = prepare_telegram_messages(df, params, telegram_message)
            st.write(f"📨 عدد الرسائل المتولدة: {len(st.session_state['messages'])}")

            st.subheader("📬 معاينة أول رسالة")
            st.code(st.session_state['messages'][0])

# أزرار إرسال الرسائل فقط إذا تم توليدها مسبقاً
if 'messages' in st.session_state:
    if st.button("📤 إرسال أول رسالة فقط"):
        result = telegram.send_message(st.session_state['messages'][0])
        st.write("📬 نتيجة الإرسال:", result)

    if telegram_enabled and st.button("📤 إرسال كل الرسائل إلى Telegram"):
        with st.spinner("📡 جاري الإرسال إلى تيليجرام..."):
            results = telegram.send_batch(st.session_state['messages'])
            success_count = sum(1 for r in results if r.get("ok"))

            if success_count == len(st.session_state['messages']):
                st.success(f"✅ تم إرسال كل ({len(st.session_state['messages'])}) الرسائل بنجاح!")
                st.balloons()
            else:
                st.warning(f"⚠️ تم إرسال {success_count} من {len(st.session_state['messages'])} رسالة فقط.")
else:
    st.info("❗ الرجاء إجراء البحث أولاً لتوليد الرسائل قبل الإرسال.")
