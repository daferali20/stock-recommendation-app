import streamlit as st
import requests
import pandas as pd

# عنوان API - ستحتاج إلى الحصول على مفتاح API مجاني من موقع Financial Modeling Prep
API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"  # استبدل هذا بمفتاح API الخاص بك
BASE_URL = "https://financialmodelingprep.com/api/v3"

# وظيفة لجلب بيانات الأسهم
def get_stock_screener(params):
    url = f"{BASE_URL}/stock-screener?apikey={API_KEY}"
    for key, value in params.items():
        if value is not None:
            url += f"&{key}={value}"
    response = requests.get(url)
    return response.json()

# واجهة المستخدم
st.title('🤑 مصفاة الأسهم الذكية (العائد + النمو)')
st.markdown("""
هذا التطبيق يساعدك في العثور على الأسهم التي تجمع بين **العائد الجيد** و**النمو المستدام**.
""")

# شريط جانبي للإعدادات
with st.sidebar:
    st.header("⚙️ معايير التصفية")
    
    # معايير العائد
    st.subheader("معايير العائد (Dividend)")
    dividend_yield = st.slider("العائد على التوزيعات (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)
    dividend_growth = st.slider("نمو التوزيعات على الأقل (سنوات)", min_value=0, max_value=20, value=5)
    
    # معايير النمو
    st.subheader("معايير النمو")
    revenue_growth = st.slider("نمو الإيرادات السنوي (%)", min_value=0, max_value=100, value=10)
    eps_growth = st.slider("نمو ربحية السهم (EPS) (%)", min_value=-50, max_value=100, value=0)
    
    # معايير إضافية
    st.subheader("معايير إضافية")
    market_cap = st.selectbox("حجم الشركة", options=["الكبيرة فقط", "المتوسطة", "الصغيرة", "الكل"], index=0)
    exchange = st.multiselect("البورصة", options=["NASDAQ", "NYSE", "AMEX"], default=["NASDAQ", "NYSE"])

# تحويل المعايير إلى صيغة API
market_cap_map = {
    "الكبيرة فقط": "LargeCap",
    "المتوسطة": "MidCap",
    "الصغيرة": "SmallCap",
    "الكل": None
}

params = {
    "dividendYieldMoreThan": dividend_yield,
    "dividendYearsMoreThan": dividend_growth,
    "revenueGrowthMoreThan": revenue_growth,
    "epsGrowthMoreThan": eps_growth,
    "marketCapMoreThan": "1000000000" if market_cap == "الكبيرة فقط" else None,
    "exchange": ",".join(exchange) if exchange else None
}

# زر البحث
if st.button("🔍 بحث عن الأسهم"):
    with st.spinner("جاري البحث عن أفضل الأسهم..."):
        try:
            data = get_stock_screener(params)
            
            if not data:
                st.warning("لم يتم العثور على أسهم تطابق معاييرك. حاول تخفيف المعايير.")
            else:
                df = pd.DataFrame(data)
                
                # تحديد الأعمدة المهمة
                columns_to_show = [
                    'symbol', 'companyName', 'dividendYield', 'payoutRatio', 
                    'revenueGrowth', 'epsGrowth', 'price', 'marketCap'
                ]
                
                # تحويل الأرقام الكبيرة إلى صيغة مقروءة
                df['marketCap'] = df['marketCap'].apply(lambda x: f"${x/1000000000:.2f}B" if x >= 1000000000 else f"${x/1000000:.2f}M")
                
                # عرض النتائج
                st.success(f"تم العثور على {len(df)} سهمًا تطابق معاييرك")
                st.dataframe(df[columns_to_show].rename(columns={
                    'symbol': 'الرمز',
                    'companyName': 'اسم الشركة',
                    'dividendYield': 'العائد (%)',
                    'payoutRatio': 'نسبة التوزيع',
                    'revenueGrowth': 'نمو الإيرادات',
                    'epsGrowth': 'نمو ربحية السهم',
                    'price': 'السعر',
                    'marketCap': 'القيمة السوقية'
                }).style.format({
                    'العائد (%)': '{:.2f}%',
                    'نسبة التوزيع': '{:.2f}%',
                    'نمو الإيرادات': '{:.2f}%',
                    'نمو ربحية السهم': '{:.2f}%',
                    'السعر': '${:.2f}'
                }), height=600)
                
                # خيار التنزيل
                csv = df[columns_to_show].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 تنزيل النتائج كملف CSV",
                    data=csv,
                    file_name='filtered_stocks.csv',
                    mime='text/csv'
                )
                
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

# معلومات إضافية
st.markdown("""
### نصائح للاستخدام:
1. للحصول على أسهم ذات عائد جيد، اضبط "العائد على التوزيعات" على 3% أو أكثر.
2. لأسهم النمو، ركز على "نمو الإيرادات" و"نمو ربحية السهم".
3. الأسهم التي تجمع بين الاثنين (مثل Microsoft) نادرة ولكنها ذات جودة عالية.
""")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
**مصدر البيانات:** [Financial Modeling Prep](https://financialmodelingprep.com/)
""")
