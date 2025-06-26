import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# إعدادات API
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"
BASE_URL = "https://financialmodelingprep.com/api/v3"

# إعدادات Telegram Bot
TELEGRAM_BOT_TOKEN = "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"
TELEGRAM_CHAT_ID = "@D_Option"
STOCKS_PER_MESSAGE = 20  # عدد الأسهم في كل رسالة

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

def send_telegram_batch(messages):
    results = []
    for message in messages:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            results.append(response.json())
            time.sleep(1)  # تجنب rate limits
        except requests.exceptions.RequestException as e:
            results.append({"ok": False, "description": str(e)})
    return results

def prepare_telegram_messages(df, params, custom_message):
    messages = []
    
    # الرسالة الرئيسية
    header = f"<b>📊 {custom_message}</b>\n"
    header += f"⏳ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    header += "<b>🔍 معايير البحث:</b>\n"
    header += f"- العائد: {params['dividendYieldMoreThan']}%\n"
    header += f"- نمو الإيرادات: {params['revenueGrowthMoreThan']}%\n"
    header += f"- عدد الأسهم: {len(df)}\n\n"
    header += "<b>📈 النتائج:</b>\n\n"
    messages.append(header)
    
    # تقسيم الأسهم إلى مجموعات
    stocks_chunks = [df[i:i+STOCKS_PER_MESSAGE] for i in range(0, len(df), STOCKS_PER_MESSAGE)]
    
    for chunk in stocks_chunks:
        message = ""
        for _, row in chunk.iterrows():
            stock_info = f"<b>📌 {row.get('symbol', 'N/A')}</b>\n"
            stock_info += f"🏢 {row.get('companyName', '')[:25]}...\n"
            
            if 'price' in row:
                stock_info += f"💰 السعر: ${row['price']:.2f}\n"
            if 'dividendYield' in row:
                stock_info += f"📈 العائد: {row['dividendYield']:.2f}%\n"
            if 'revenueGrowth' in row:
                stock_info += f"📊 النمو: {row['revenueGrowth']:.2f}%\n"
            
            stock_info += "――――――――――\n"
            message += stock_info
        
        messages.append(message)
    
    # الرسالة الختامية
    footer = "\n<b>📊 ملخص إحصائي:</b>\n"
    if 'dividendYield' in df.columns:
        footer += f"• متوسط العائد: {df['dividendYield'].mean():.2f}%\n"
    if 'price' in df.columns:
        footer += f"• متوسط السعر: ${df['price'].mean():.2f}\n"
    footer += "\n⚡ تم إنشاء التقرير بواسطة Stock Screener Bot"
    messages.append(footer)
    
    return messages

# واجهة المستخدم
st.set_page_config(page_title="مصفاة الأسهم", layout="wide")
st.title('📈 مصفاة الأسهم (عائد + نمو)')
st.markdown("""
**أداة متقدمة** لاكتشاف الأسهم ذات العوائد المجزية ونمو الأرباح المستدام
""")

# إعدادات البحث
with st.sidebar:
    st.header("⚙️ ضبط المعايير")
    
    with st.expander("معايير العوائد"):
        dividend_yield = st.slider("حد أدنى للعائد (%)", 0.0, 20.0, 3.0, 0.5)
        dividend_growth = st.slider("حد أدنى لسنوات التوزيع", 0, 20, 5)
    
    with st.expander("معايير النمو"):
        revenue_growth = st.slider("نمو إيرادات سنوي (%)", 0, 100, 10)
        eps_growth = st.slider("نمو ربحية السهم (%)", -50, 100, 0)
    
    with st.expander("خيارات متقدمة"):
        market_cap = st.selectbox("حجم الشركة", ["الكبيرة فقط", "المتوسطة", "الصغيرة", "الكل"], index=0)
        exchange = st.multiselect("البورصات", ["NASDAQ", "NYSE", "AMEX"], default=["NASDAQ", "NYSE"])
    
    with st.expander("إعدادات الإرسال"):
        telegram_enabled = st.checkbox("تمكين إرسال Telegram", value=True)
        if telegram_enabled:
            st.info(f"سيتم إرسال {STOCKS_PER_MESSAGE} سهماً في كل رسالة")
            telegram_message = st.text_input("عنوان التقرير", value="تقرير الأسهم المميزة")

params = {
    "dividendYieldMoreThan": dividend_yield,
    "dividendYearsMoreThan": dividend_growth,
    "revenueGrowthMoreThan": revenue_growth,
    "epsGrowthMoreThan": eps_growth,
    "marketCapMoreThan": "1000000000" if market_cap == "الكبيرة فقط" else None,
    "exchange": ",".join(exchange) if exchange else None
}

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
            
            # عرض النتائج
            cols_to_show = ['symbol', 'companyName', 'price', 'dividendYield', 'revenueGrowth']
            cols_to_show = [col for col in cols_to_show if col in df.columns]
            
            if cols_to_show:
                display_df = df[cols_to_show].rename(columns={
                    'symbol': 'الرمز',
                    'companyName': 'الشركة',
                    'price': 'السعر',
                    'dividendYield': 'العائد%',
                    'revenueGrowth': 'نمو الإيرادات%'
                })
                
                st.dataframe(
                    display_df.style.format({
                        'السعر': '${:.2f}',
                        'العائد%': '{:.2f}%',
                        'نمو الإيرادات%': '{:.2f}%'
                    }),
                    height=600,
                    use_container_width=True
                )
                
                # خيارات التصدير
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 حفظ كملف CSV",
                        data=csv,
                        file_name=f"stocks_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime='text/csv'
                    )
                
                with col2:
                    if telegram_enabled and st.button("📤 إرسال إلى Telegram", type="secondary"):
                        with st.spinner(f"جاري إعداد {len(df)} سهماً في مجموعات..."):
                            try:
                                messages = prepare_telegram_messages(df, params, telegram_message)
                                results = send_telegram_batch(messages)
                                
                                success_count = sum(1 for r in results if r.get('ok'))
                                if success_count == len(messages):
                                    st.success(f"تم إرسال {len(messages)} رسالة بنجاح!")
                                    st.balloons()
                                else:
                                    failed = len(messages) - success_count
                                    st.warning(f"تم إرسال {success_count} رسالة، وفشل {failed}")
                            except Exception as e:
                                st.error(f"خطأ غير متوقع: {str(e)}")
            else:
                st.warning("بيانات غير كافية للعرض")

# تذييل الصفحة
st.markdown("---")
st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')} | مصدر البيانات: Financial Modeling Prep")
