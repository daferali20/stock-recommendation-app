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

def get_stock_screener(params):
    url = f"{BASE_URL}/stock-screener?apikey={API_KEY}"
    for key, value in params.items():
        if value is not None:
            url += f"&{key}={value}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"خطأ في الاتصال بAPI: {str(e)}")
        return None

def send_to_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"خطأ في إرسال الرسالة: {str(e)}")
        return {"ok": False, "description": str(e)}

def prepare_telegram_message(df, params, custom_message):
    # تحضير الرسالة الأساسية
    message = f"<b>📊 {custom_message}</b>\n"
    message += f"⏳ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # معايير البحث
    message += "<b>🔍 معايير البحث:</b>\n"
    message += f"- العائد على التوزيعات: {params['dividendYieldMoreThan']}%\n"
    message += f"- نمو الإيرادات: {params['revenueGrowthMoreThan']}%\n"
    message += f"- نمو ربحية السهم: {params['epsGrowthMoreThan']}%\n"
    message += f"- عدد الأسهم: {len(df)}\n\n"
    
    # أهم 3 أسهم
    message += "<b>🏆 أفضل الأسهم:</b>\n"
    top_stocks = df.head(3).copy()
    
    for _, row in top_stocks.iterrows():
        message += f"\n<b>📌 {row.get('symbol', 'N/A')}</b>\n"
        message += f"🏢 {row.get('companyName', '')[:30]}...\n"
        
        if 'price' in row:
            message += f"💰 السعر: ${row['price']:.2f}\n"
        if 'dividendYield' in row:
            message += f"📈 العائد: {row['dividendYield']:.2f}%\n"
        if 'revenueGrowth' in row:
            message += f"📊 نمو الإيرادات: {row['revenueGrowth']:.2f}%\n"
    
    # إحصائيات
    message += "\n<b>📈 ملخص النتائج:</b>\n"
    if 'dividendYield' in df.columns:
        avg_yield = df['dividendYield'].mean()
        message += f"• متوسط العائد: {avg_yield:.2f}%\n"
    if 'price' in df.columns:
        avg_price = df['price'].mean()
        message += f"• متوسط السعر: ${avg_price:.2f}\n"
    if 'revenueGrowth' in df.columns:
        avg_revenue = df['revenueGrowth'].mean()
        message += f"• متوسط نمو الإيرادات: {avg_revenue:.2f}%\n"
    
    message += "\n⚡ تم إنشاء التقرير بواسطة Stock Screener Bot"
    return message

# واجهة المستخدم
st.set_page_config(page_title="مصفاة الأسهم الذكية", layout="wide")
st.title('🤑 مصفاة الأسهم الذكية (العائد + النمو)')
st.markdown("""
هذا التطبيق يساعدك في العثور على الأسهم التي تجمع بين **العائد الجيد** و**النمو المستدام**.
""")

# إعدادات البحث في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ معايير التصفية")
    
    st.subheader("معايير العائد (Dividend)")
    dividend_yield = st.slider("العائد على التوزيعات (%)", 0.0, 20.0, 3.0, 0.5)
    dividend_growth = st.slider("نمو التوزيعات (سنوات)", 0, 20, 5)
    
    st.subheader("معايير النمو")
    revenue_growth = st.slider("نمو الإيرادات السنوي (%)", 0, 100, 10)
    eps_growth = st.slider("نمو ربحية السهم (EPS) (%)", -50, 100, 0)
    
    st.subheader("معايير إضافية")
    market_cap = st.selectbox("حجم الشركة", ["الكبيرة فقط", "المتوسطة", "الصغيرة", "الكل"], index=0)
    exchange = st.multiselect("البورصة", ["NASDAQ", "NYSE", "AMEX"], default=["NASDAQ", "NYSE"])
    
    st.subheader("إعدادات Telegram")
    telegram_enabled = st.checkbox("تمكين الإرسال إلى Telegram", value=True)
    if telegram_enabled:
        telegram_message = st.text_area("رسالة مخصصة", value="تقرير الأسهم المفلترة")

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
        data = get_stock_screener(params)
        
        if data is None:
            st.error("حدث خطأ في جلب البيانات. يرجى المحاولة لاحقًا.")
        elif not data:
            st.warning("لم يتم العثور على أسهم تطابق معاييرك. حاول تخفيف المعايير.")
        else:
            df = pd.DataFrame(data)
            
            # تحديد الأعمدة المتاحة
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
            
            # تصفية الأعمدة المتاحة فقط
            columns_to_show = [col for col in columns_mapping if col in available_columns]
            display_columns = [columns_mapping[col] for col in columns_to_show]
            
            # تنسيق البيانات
            if 'marketCap' in df.columns:
                df['marketCap'] = df['marketCap'].apply(lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else f"${x/1e6:.2f}M")
            
            # عرض النتائج
            st.success(f"تم العثور على {len(df)} سهمًا تطابق معاييرك")
            
            if columns_to_show:
                # إنشاء DataFrame للعرض
                display_df = df[columns_to_show].rename(columns=dict(zip(columns_to_show, display_columns)))
                
                # تنسيق الأرقام
                format_dict = {
                    'العائد (%)': '{:.2f}%',
                    'نسبة التوزيع': '{:.2f}%',
                    'نمو الإيرادات': '{:.2f}%',
                    'نمو ربحية السهم': '{:.2f}%',
                    'السعر': '${:.2f}'
                }
                
                # تطبيق التنسيق على الأعمدة المتاحة فقط
                format_dict = {k: v for k, v in format_dict.items() if k in display_df.columns}
                styled_df = display_df.style.format(format_dict)
                
                st.dataframe(styled_df, height=600, use_container_width=True)
                
                # أزرار التصدير
                col1, col2 = st.columns(2)
                with col1:
                    csv = df[columns_to_show].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 تنزيل النتائج كملف CSV",
                        data=csv,
                        file_name=f"stocks_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime='text/csv'
                    )
                
                with col2:
                    if telegram_enabled:
                        if st.button("📤 إرسال إلى Telegram"):
                            with st.spinner("جاري إعداد وإرسال التقرير..."):
                                try:
                                    message = prepare_telegram_message(df, params, telegram_message)
                                    result = send_to_telegram(message)
                                    
                                    if result.get('ok'):
                                        st.success("✅ تم إرسال التقرير إلى Telegram بنجاح!")
                                        st.balloons()
                                    else:
                                        error_msg = result.get('description', 'خطأ غير معروف')
                                        st.error(f"❌ فشل الإرسال: {error_msg}")
                                except Exception as e:
                                    st.error(f"حدث خطأ غير متوقع: {str(e)}")
            else:
                st.warning("البيانات المسترجعة لا تحتوي على الأعمدة المطلوبة")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
**مصدر البيانات:** [Financial Modeling Prep](https://financialmodelingprep.com/)  
**آخر تحديث:** {date}
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M')))
