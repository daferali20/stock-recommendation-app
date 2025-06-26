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

import html  # في الأعلى

def prepare_telegram_messages(df, params, custom_message):
    MAX_LENGTH = 4000
    messages = []

    # رأس الرسالة
    header = f"<b>📊 {html.escape(custom_message)}</b>\n"
    header += f"⏳ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    header += "<b>🔍 معايير البحث:</b>\n"
    header += f"- العائد: {params['dividendYieldMoreThan']}%\n"
    header += f"- نمو الإيرادات: {params['revenueGrowthMoreThan']}%\n"
    header += f"- عدد الأسهم: {len(df)}\n\n"

    current_message = header
for _, row in df.iterrows():
    try:
            symbol = html.escape(str(row.get("symbol", "N/A")))
            company = html.escape(str(row.get("companyName", "")))[:25]
            price = f"${row['price']:.2f}" if "price" in row else ""
            dividend = f"{row['dividendYield']:.2f}%" if "dividendYield" in row else ""
            growth = f"{row['revenueGrowth']:.2f}%" if "revenueGrowth" in row else ""
    
            stock_info = f"<code>{symbol}</code> | {company}...\n"
     if price:
                stock_info += f"💰 {price} | "
     if dividend:
                stock_info += f"📈 {dividend} | "
     if growth:
                stock_info += f"📊 {growth}\n"
            stock_info += "――――――――――\n"
    
      if len(current_message) + len(stock_info) >= MAX_LENGTH:
                messages.append(current_message.strip())
                current_message = ""

            current_message += stock_info
     except Exception as e:
            st.warning(f"⚠️ مشكلة في سطر: {e}")
            continue   


    # الرسالة الأخيرة
    if current_message.strip():
        messages.append(current_message.strip())

    # الرسالة الختامية
    footer = "\n<b>📊 ملخص إحصائي:</b>\n"
    if 'dividendYield' in df.columns:
        footer += f"• متوسط العائد: {df['dividendYield'].mean():.2f}%\n"
    if 'price' in df.columns:
        footer += f"• متوسط السعر: ${df['price'].mean():.2f}\n"
    footer += "\n⚡ تم الإنشاء بواسطة Stock Screener"
    messages.append(footer[:MAX_LENGTH])

    return messages


# واجهة Streamlit
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

# زر اختبار تيليجرام
if st.button("📨 اختبار إرسال Telegram"):
    telegram = TelegramSender()
    test_result = telegram.send_message("✅ اختبار مباشر من تطبيق Streamlit")
    st.write("📬 نتيجة الاختبار:", test_result)

# زر البحث
if st.button("🔍 بدء البحث", type="primary"):
    with st.spinner("جاري تحليل بيانات السوق..."):
        data = get_stock_screener(params)
        if data is None:
            st.error("تعذر الاتصال بمصدر البيانات")
        elif not data:
            st.warning("لا توجد نتائج مطابقة للمعايير")
        else:
            df = pd.DataFrame(data).fillna(0)
            st.success(f"✅ تم تحديد {len(df)} سهماً مؤهلاً")
            st.dataframe(df)

            telegram = TelegramSender()
            messages = prepare_telegram_messages(df, params, telegram_message)
            st.write(f"📨 عدد الرسائل المتولدة: {len(messages)}")

            # تحقق من طول الرسائل
            for i, m in enumerate(messages):
                if len(m) > 4000:
                    st.warning(f"⚠️ الرسالة {i+1} طويلة جدًا: {len(m)} حرفًا")
                    st.code(m[:500] + "...\n(تم الاقتصاص)")

            # معاينة أول رسالة
            if messages:
                st.subheader("📬 معاينة أول رسالة")
                st.code(messages[0])

            # زر إرسال أول رسالة فقط
            if st.button("📤 إرسال أول رسالة فقط"):
                result = telegram.send_message(messages[0])
                st.write("📬 نتيجة الإرسال:", result)

            # زر إرسال جميع الرسائل
            if telegram_enabled and st.button("📤 إرسال كل الرسائل إلى Telegram"):
                with st.spinner("جاري الإرسال إلى تيليجرام..."):
                    results = telegram.send_batch(messages)

                    for i, result in enumerate(results):
                        if not result.get("ok"):
                            st.error(f"❌ فشل في الرسالة {i+1}: {result.get('error')} | التفاصيل: {result.get('details')}")

                    success_count = sum(1 for r in results if r.get("ok"))
                    if success_count == len(messages):
                        st.success(f"✅ تم إرسال كل ({len(messages)}) الرسائل بنجاح!")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ تم إرسال {success_count} من {len(messages)} رسالة فقط.")
