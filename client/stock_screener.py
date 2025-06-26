import streamlit as st
import requests
import pandas as pd
import json

# إعدادات API
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"  # استبدل هذا بمفتاح API الخاص بك
BASE_URL = "https://financialmodelingprep.com/api/v3"

# إعدادات Telegram Bot
TELEGRAM_BOT_TOKEN = "6203893805:AAFX_hXijc-HVcuNV8mAJqbVMRhi95A-dZs"  # استبدل ب token بوتك
TELEGRAM_CHAT_ID = "@D_Option"  # استبدل ب chat id الخاص بك

def get_stock_screener(params):
    url = f"{BASE_URL}/stock-screener?apikey={API_KEY}"
    for key, value in params.items():
        if value is not None:
            url += f"&{key}={value}"
    response = requests.get(url)
    return response.json()

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response.json()

st.title('🤑 مصفاة الأسهم الذكية (العائد + النمو)')
st.markdown("""
هذا التطبيق يساعدك في العثور على الأسهم التي تجمع بين **العائد الجيد** و**النمو المستدام**.
""")

# إعدادات البحث في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ معايير التصفية")
    
    st.subheader("معايير العائد (Dividend)")
    dividend_yield = st.slider("العائد على التوزيعات (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)
    dividend_growth = st.slider("نمو التوزيعات على الأقل (سنوات)", min_value=0, max_value=20, value=5)
    
    st.subheader("معايير النمو")
    revenue_growth = st.slider("نمو الإيرادات السنوي (%)", min_value=0, max_value=100, value=10)
    eps_growth = st.slider("نمو ربحية السهم (EPS) (%)", min_value=-50, max_value=100, value=0)
    
    st.subheader("معايير إضافية")
    market_cap = st.selectbox("حجم الشركة", options=["الكبيرة فقط", "المتوسطة", "الصغيرة", "الكل"], index=0)
    exchange = st.multiselect("البورصة", options=["NASDAQ", "NYSE", "AMEX"], default=["NASDAQ", "NYSE"])
    
    st.subheader("إعدادات Telegram")
    telegram_enabled = st.checkbox("تمكين الإرسال إلى Telegram")
    if telegram_enabled:
        telegram_message = st.text_area("رسالة مخصصة", value="قائمة الأسهم المفلترة:")

params = {
    "dividendYieldMoreThan": dividend_yield,
    "dividendYearsMoreThan": dividend_growth,
    "revenueGrowthMoreThan": revenue_growth,
    "epsGrowthMoreThan": eps_growth,
    "marketCapMoreThan": "1000000000" if market_cap == "الكبيرة فقط" else None,
    "exchange": ",".join(exchange) if exchange else None
}

if st.button("🔍 بحث عن الأسهم"):
    with st.spinner("جاري البحث عن أفضل الأسهم..."):
        try:
            data = get_stock_screener(params)
            
            if not data:
                st.warning("لم يتم العثور على أسهم تطابق معاييرك. حاول تخفيف المعايير.")
            else:
                df = pd.DataFrame(data)
                
                available_columns = df.columns.tolist()
                columns_mapping = {
                    'symbol': 'الرمز',
                    'companyName': 'اسم الشركة',
                    'dividendYield': 'العائد (%)',
                    'payoutRatio': 'نسبة التوزيع',
                    'revenueGrowth': 'نمو الإيرادات',
                    'epsGrowth': 'نمو ربحية السهم',
                    'price': 'السعر',
                    'marketCap': 'القيمة السوقية'
                }
                
                columns_to_show = []
                display_columns = []
                
                for col, display_name in columns_mapping.items():
                    if col in available_columns:
                        columns_to_show.append(col)
                        display_columns.append(display_name)
                
                if 'marketCap' in df.columns:
                    df['marketCap'] = df['marketCap'].apply(lambda x: f"${x/1000000000:.2f}B" if x >= 1000000000 else f"${x/1000000:.2f}M")
                
                format_dict = {}
                if 'dividendYield' in df.columns:
                    format_dict['العائد (%)'] = '{:.2f}%'
                if 'payoutRatio' in df.columns:
                    format_dict['نسبة التوزيع'] = '{:.2f}%'
                if 'revenueGrowth' in df.columns:
                    format_dict['نمو الإيرادات'] = '{:.2f}%'
                if 'epsGrowth' in df.columns:
                    format_dict['نمو ربحية السهم'] = '{:.2f}%'
                if 'price' in df.columns:
                    format_dict['السعر'] = '${:.2f}'
                
                st.success(f"تم العثور على {len(df)} سهمًا تطابق معاييرك")
                
                if len(columns_to_show) > 0:
                    styled_df = df[columns_to_show].rename(columns=dict(zip(columns_to_show, display_columns)))
                    
                    if format_dict:
                        styled_df = styled_df.style.format(format_dict)
                    
                    st.dataframe(styled_df, height=600)
                    
                    # خيارات التصدير
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = df[columns_to_show].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 تنزيل النتائج كملف CSV",
                            data=csv,
                            file_name='filtered_stocks.csv',
                            mime='text/csv'
                        )
                    
                    with col2:
                        if telegram_enabled:
                            if st.button("📤 إرسال إلى Telegram"):
                                try:
                                    # تحضير الرسالة
                                    message = f"<b>{telegram_message}</b>\n\n"
                                    message += f"معايير البحث:\n"
                                    message += f"- العائد على التوزيعات: {dividend_yield}%\n"
                                    message += f"- نمو الإيرادات: {revenue_growth}%\n"
                                    message += f"- عدد الأسهم: {len(df)}\n\n"
                                    
                                    # إضافة أهم 5 أسهم
                                    top_stocks = df.head().copy()
                                    for _, row in top_stocks.iterrows():
                                        message += f"<b>{row['symbol']}</b> - {row['companyName']}\n"
                                        if 'price' in row:
                                            message += f"السعر: {row['price']}\n"
                                        if 'dividendYield' in row:
                                            message += f"العائد: {row['dividendYield']}%\n"
                                        message += "\n"
                                    
                                    message += "\nملخص النتائج:\n"
                                    if 'dividendYield' in df.columns:
                                        avg_yield = df['dividendYield'].mean()
                                        message += f"متوسط العائد: {avg_yield:.2f}%\n"
                                    if 'price' in df.columns:
                                        avg_price = df['price'].mean()
                                        message += f"متوسط السعر: ${avg_price:.2f}\n"
                                    
                                    # إرسال الرسالة
                                    result = send_to_telegram(message)
                                    if result.get('ok'):
                                        st.success("تم إرسال القائمة إلى Telegram بنجاح!")
                                    else:
                                        st.error(f"فشل الإرسال: {result.get('description', 'Unknown error')}")
                                except Exception as e:
                                    st.error(f"حدث خطأ أثناء الإرسال: {str(e)}")
                else:
                    st.warning("البيانات المسترجعة لا تحتوي على الأعمدة المطلوبة")
                
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

st.markdown("""
### تعليمات استخدام Telegram:
1. أنشئ بوت Telegram عن طريق BotFather واحصل على token
2. احصل على chat ID عن طريق إرسال رسالة للبوت ثم زيارة:
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
3. أدخل هذه المعلومات في الإعدادات الجانبية
""")

st.markdown("---")
st.markdown("""
**مصدر البيانات:** [Financial Modeling Prep](https://financialmodelingprep.com/)
""")
