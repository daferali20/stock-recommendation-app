import streamlit as st
import requests
import pandas as pd
from datetime import datetime

from telegram_alerts import TelegramSender  # تأكد أن هذا الملف موجود ومهيأ


# إعدادات API
API_KEY = "dIaNorTQjiQuB5D63K2d31yEW8LyxHsz"
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
        st.error(f"خطأ في الاتصال بAPI: {str(e)}")
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

# زر البحث وتحليل الأسهم
if st.button("🔍 بدء البحث", type="primary"):
    with st.spinner("جاري تحليل بيانات السوق..."):
        data = get_stock_screener(params)
        if data is None:
            st.error("❌ تعذر الاتصال بمصدر البيانات")
        elif not data:
            st.warning("⚠️ لا توجد نتائج مطابقة للمعايير")
        else:
            df = pd.DataFrame(data).fillna(0)

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

#--------------------------------


# تجهيز رسائل تيليجرام
def prepare_telegram_messages(df, params, custom_message):
    MAX_LENGTH = 3500
    messages = []

    df = df.head(5)  # أول 5 أسهم فقط
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
                current_message = header + stock_info
            else:
                current_message += stock_info
        except Exception:
            continue

    if current_message.strip():
        messages.append(current_message.strip())

    messages[-1] += "\n⚡ تم الإنشاء تلقائيًا"
    return messages

telegram = TelegramSender()

if st.button("📨 اختبار إرسال Telegram"):
    test_result = telegram.send_message("✅ اختبار مباشر من تطبيق Streamlit")
    st.write("📬 نتيجة الاختبار:", test_result)

if st.button("🔍 بدء البحث", type="primary"):
    with st.spinner("جاري تحليل بيانات السوق..."):
        all_data = []

        for symbol in symbols:
            df = get_daily_stock_data(symbol)
            if df is not None:
                latest_close = df["4. close"].iloc[-1]
                dividend_yield = round(1.5 + 1.0 * hash(symbol) % 5, 2)  # وهمي للتجربة
                revenue_growth = round(5.0 + 1.0 * hash(symbol[::-1]) % 20, 2)  # وهمي للتجربة

                if dividend_yield >= dividend and revenue_growth >= revenue_growth:
                    all_data.append({
                        "symbol": symbol,
                        "dividendYield": dividend_yield,
                        "revenueGrowth": revenue_growth,
                        "close": latest_close
                    })

        if all_data:
            df_result = pd.DataFrame(all_data)
            st.success(f"✅ تم تحديد {len(df_result)} سهمًا مؤهلًا")
            st.dataframe(df_result)

            messages = prepare_telegram_messages(df_result, params, telegram_message)
            st.session_state['messages'] = messages

            st.write(f"📨 عدد الرسائل المتولدة: {len(messages)}")
            st.subheader("📬 معاينة أول رسالة")
            st.code(messages[0])
        else:
            st.warning("⚠️ لا توجد أسهم مطابقة للمعايير.")

if 'messages' in st.session_state:
    if st.button("📤 إرسال أول رسالة فقط"):
        result = telegram.send_message(st.session_state['messages'][0])
        st.write("📬 نتيجة الإرسال:", result)

    if telegram_enabled and st.button("📤 إرسال كل الرسائل إلى Telegram"):
        with st.spinner("📡 جاري الإرسال إلى تيليجرام..."):
            results = telegram.send_batch(st.session_state['messages'])
            success_count = sum(1 for r in results if r.get("ok"))
            total = len(st.session_state['messages'])

            if success_count == total:
                st.success(f"✅ تم إرسال كل ({total}) الرسائل بنجاح!")
                st.balloons()
            else:
                st.warning(f"⚠️ تم إرسال {success_count} من {total} رسالة فقط.")
else:
    st.info("❗ الرجاء إجراء البحث أولًا لتوليد الرسائل قبل الإرسال.")
