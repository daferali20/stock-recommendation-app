import streamlit as st
import requests
import pandas as pd

API_KEY = "CVROqS2TTsTM06ZNpYQJd5C1dXg1Amuv"  # استبدل هذا بمفتاح API الخاص بك
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_stock_screener(params):
    url = f"{BASE_URL}/stock-screener?apikey={API_KEY}"
    for key, value in params.items():
        if value is not None:
            url += f"&{key}={value}"
    response = requests.get(url)
    return response.json()

st.title('🤑 مصفاة الأسهم الذكية (العائد + النمو)')
st.markdown("""
هذا التطبيق يساعدك في العثور على الأسهم التي تجمع بين **العائد الجيد** و**النمو المستدام**.
""")

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
                
                # تحديد الأعمدة المتاحة فعلياً في البيانات
                available_columns = df.columns.tolist()
                
                # قائمة بالأعمدة المطلوبة مع البدائل في حالة عدم وجودها
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
                
                # إنشاء قائمة بالأعمدة التي سيتم عرضها (الموجودة فقط في البيانات)
                columns_to_show = []
                display_columns = []
                
                for col, display_name in columns_mapping.items():
                    if col in available_columns:
                        columns_to_show.append(col)
                        display_columns.append(display_name)
                
                # تحويل الأرقام الكبيرة إلى صيغة مقروءة
                if 'marketCap' in df.columns:
                    df['marketCap'] = df['marketCap'].apply(lambda x: f"${x/1000000000:.2f}B" if x >= 1000000000 else f"${x/1000000:.2f}M")
                
                # تنسيق الأعمدة الرقمية
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
                
                # عرض النتائج
                st.success(f"تم العثور على {len(df)} سهمًا تطابق معاييرك")
                
                # عرض الجدول مع الأعمدة المتاحة فقط
                if len(columns_to_show) > 0:
                    styled_df = df[columns_to_show].rename(columns=dict(zip(columns_to_show, display_columns)))
                    
                    # تطبيق التنسيق على الأعمدة المتاحة فقط
                    if format_dict:
                        styled_df = styled_df.style.format(format_dict)
                    
                    st.dataframe(styled_df, height=600)
                    
                    # خيار التنزيل
                    csv = df[columns_to_show].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 تنزيل النتائج كملف CSV",
                        data=csv,
                        file_name='filtered_stocks.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("البيانات المسترجعة لا تحتوي على الأعمدة المطلوبة")
                
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")

st.markdown("""
### نصائح للاستخدام:
1. بعض الأسهم قد لا تحتوي على جميع بيانات العائد أو النمو
2. إذا لم تظهر بعض الأعمدة، فهذا يعني أن API لم يرجع هذه البيانات
3. جرب تعديل معايير البحث للحصول على نتائج أفضل
""")

st.markdown("---")
st.markdown("""
**مصدر البيانات:** [Financial Modeling Prep](https://financialmodelingprep.com/)
""")
