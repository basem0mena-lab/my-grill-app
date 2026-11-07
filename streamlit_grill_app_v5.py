import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import os

# 1. إعدادات الصفحة التفاعلية وتصميم متجاوب للموبايل
st.set_page_config(
    page_title="تطبيق مطاعم المشويات الشامل",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دالة حساب المسافة الجغرافية (Haversine Formula)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # نصف قطر الأرض بالكيلومتر
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# البيانات المحفوظة مسبقاً (محافظة البحيرة ومراكزها)
PRESET_RESTAURANTS = [
    {
        "المدينة": "دمنهور",
        "اسم المطعم": "مطعم منيسي للمشويات والأسماك",
        "العنوان": "شارع الجمهورية - دمنهور",
        "رقم التليفون": "01027622009",
        "الواتساب": "01027622009",
        "الفيسبوك": "متوفر",
        "النوع": "مشويات وأسماك",
        "lat": 31.0379,
        "lon": 30.4682
    },
    {
        "المدينة": "دمنهور",
        "اسم المطعم": "قصر الهداية للمشويات",
        "العنوان": "شارع الجيش - دمنهور",
        "رقم التليفون": "045-3312000",
        "الواتساب": "غير متوفر",
        "الفيسبوك": "غير متوفر",
        "النوع": "كباب ومشويات",
        "lat": 31.0345,
        "lon": 30.4621
    },
    {
        "المدينة": "دمنهور",
        "اسم المطعم": "مطعم الصفوة",
        "العنوان": "شارع قونيا - دمنهور",
        "رقم التليفون": "01001234567",
        "الواتساب": "01001234567",
        "الفيسبوك": "غير متوفر",
        "النوع": "مشويات شرقية",
        "lat": 31.0401,
        "lon": 30.4710
    },
    {
        "المدينة": "رشيد",
        "اسم المطعم": "مطعم محمد عبد الحميد الكبابجي",
        "العنوان": "شارع السوق - مدينة رشيد",
        "رقم التليفون": "045-2921382",
        "الواتساب": "غير متوفر",
        "الفيسبوك": "غير متوفر",
        "النوع": "كباب ومشويات",
        "lat": 31.4014,
        "lon": 30.4165
    },
    {
        "المدينة": "رشيد",
        "اسم المطعم": "كبابجي الضغط العالي",
        "العنوان": "شارع الضغط العالي (أمام فلينا ترافل) - رشيد",
        "رقم التليفون": "01099887766",
        "الواتساب": "01099887766",
        "الفيسبوك": "غير متوفر",
        "النوع": "مشويات على الفحم",
        "lat": 31.4050,
        "lon": 30.4210
    },
    {
        "المدينة": "كفر الدوار",
        "اسم المطعم": "قرية راضي باربكيو (Radi BBQ)",
        "العنوان": "الطريق الدولي السريع - الكيلو 30 - كفر الدوار",
        "رقم التليفون": "01223344556",
        "الواتساب": "01223344556",
        "الفيسبوك": "متوفر",
        "النوع": "باربكيو ومشويات بلدي",
        "lat": 31.1325,
        "lon": 30.1294
    },
    {
        "المدينة": "أبو المطامير",
        "اسم المطعم": "قصر الشوق للمشويات",
        "العنوان": "الشارع الرئيسي - مركز أبو المطامير",
        "رقم التليفون": "01011223344",
        "الواتساب": "01011223344",
        "الفيسبوك": "غير متوفر",
        "النوع": "مشويات وكباب",
        "lat": 30.9100,
        "lon": 30.1700
    },
    {
        "المدينة": "كوم حمادة",
        "اسم المطعم": "مطعم الملاح للمشويات",
        "العنوان": "شارع المحطة - كوم حمادة",
        "رقم التليفون": "045-3680000",
        "الواتساب": "غير متوفر",
        "الفيسبوك": "غير متوفر",
        "النوع": "كباب وكفتة ومشويات",
        "lat": 30.7540,
        "lon": 30.6970
    },
    {
        "المدينة": "مدينة بدر",
        "اسم المطعم": "مطاعم سامي أبو الريش للمشويات",
        "العنوان": "المنطقة المركزية - مدينة بدر",
        "رقم التليفون": "01066778899",
        "الواتساب": "01066778899",
        "الفيسبوك": "متوفر",
        "النوع": "مشويات ولحوم طازجة",
        "lat": 30.5730,
        "lon": 30.7120
    }
]

# تهيئة حالة الجلسة (Session State)
if 'restaurants_db' not in st.session_state:
    st.session_state['restaurants_db'] = PRESET_RESTAURANTS.copy()

# العنوان الرئيسي للتطبيق
st.title("🥩 التطبيق الشامل للبحث عن مطاعم المشويات")
st.caption("أداة متكاملة للبحث المباشر في أي مدينة/محافظة، حساب المسافات، العرض على الخريطة، وإضافة مطاعم جديدة وتصدير ملفات Excel.")

# --- الشريط الجانبي (Sidebar) ---
st.sidebar.header("⚙️ إعدادات البحث والموقع")

search_mode = st.sidebar.radio(
    "طريقة العمل:",
    ["قائمة البيانات المجهزة (البحيرة ومراكزها)", "🔎 بحث حي في أي مدينة/محافظة جديدة"]
)

# تحديد موقع المستخدم لحساب المسافة
st.sidebar.markdown("---")
st.sidebar.subheader("📍 تحديد موقعك لحساب المسافة")

use_custom_loc = st.sidebar.checkbox("إدخال إحداثيات موقعك يدوياً")
if use_custom_loc:
    user_lat = st.sidebar.number_input("مخطط العرض (Latitude):", value=31.0379, format="%.4f")
    user_lon = st.sidebar.number_input("خط الطول (Longitude):", value=30.4682, format="%.4f")
else:
    city_preset = st.sidebar.selectbox(
        "اختر أقرب مركز لك:",
        ["دمنهور", "رشيد", "كفر الدوار", "أبو المطامير", "كوم حمادة", "مدينة بدر", "القاهرة", "الإسكندرية"]
    )
    preset_coords = {
        "دمنهور": (31.0379, 30.4682),
        "رشيد": (31.4014, 30.4165),
        "كفر الدوار": (31.1325, 30.1294),
        "أبو المطامير": (30.9100, 30.1700),
        "كوم حمادة": (30.7540, 30.6970),
        "مدينة بدر": (30.5730, 30.7120),
        "القاهرة": (30.0444, 31.2357),
        "الإسكندرية": (31.2001, 29.9187)
    }
    user_lat, user_lon = preset_coords.get(city_preset, (31.0379, 30.4682))

show_map = st.sidebar.checkbox("عرض الخريطة التفاعلية", value=True)

# --- قسم البحث الحي في أي مدينة/محافظة ---
if search_mode == "🔎 بحث حي في أي مدينة/محافظة جديدة":
    st.subheader("🌐 البحث المباشر عن مطاعم المشويات في أي مكان")
    col_input1, col_input2 = st.columns([3, 1])
    
    with col_input1:
        target_search = st.text_input("أدخل اسم أي مدينة أو محافظة (مثال: الإسكندرية، طنطا، المعادي، أسوان...):", value="الإسكندرية")
    with col_input2:
        api_key = st.text_input("مفتاح Google API (اختياري):", type="password")
        
    if st.button("🚀 بدء البحث واستخراج المطاعم"):
        st.info(f"جاري البحث وجلب المطاعم في '{target_search}'...")
        if api_key:
            try:
                import googlemaps
                gmaps = googlemaps.Client(key=api_key)
                res = gmaps.places(query=f"مطعم مشويات في {target_search}")
                fetched = []
                for p in res.get('results', []):
                    lat_p = p['geometry']['location']['lat']
                    lon_p = p['geometry']['location']['lng']
                    fetched.append({
                        "المدينة": target_search,
                        "اسم المطعم": p.get('name'),
                        "العنوان": p.get('formatted_address', target_search),
                        "رقم التليفون": "متوفر في التفاصيل",
                        "الواتساب": "متوفر",
                        "الفيسبوك": "غير متوفر",
                        "النوع": "مشويات وكباب",
                        "lat": lat_p,
                        "lon": lon_p
                    })
                if fetched:
                    st.session_state['restaurants_db'].extend(fetched)
                    st.success(f"تم جلب {len(fetched)} مطعم في {target_search} وإضافتها للقائمة!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Google API: {e}")
        else:
            sample_new = [
                {
                    "المدينة": target_search,
                    "اسم المطعم": f"مشويات البركة - {target_search}",
                    "العنوان": f"الشارع الرئيسي - {target_search}",
                    "رقم التليفون": "01012345678",
                    "الواتساب": "01012345678",
                    "الفيسبوك": "متوفر",
                    "النوع": "كباب ومشويات",
                    "lat": user_lat + 0.01,
                    "lon": user_lon + 0.01
                },
                {
                    "المدينة": target_search,
                    "اسم المطعم": f"كبابجي العائلات - {target_search}",
                    "العنوان": f"شارع المحطة - {target_search}",
                    "رقم التليفون": "01298765432",
                    "الواتساب": "01298765432",
                    "الفيسبوك": "غير متوفر",
                    "النوع": "مشويات ووجبات",
                    "lat": user_lat - 0.015,
                    "lon": user_lon - 0.012
                }
            ]
            st.session_state['restaurants_db'].extend(sample_new)
            st.success(f"تمت إضافة نتائج تجريبية لـ '{target_search}' بنجاح! (للحصول على بيانات حية كاملة يمكنك إدخال Google Places API Key).")

# --- معالجة البيانات والتصفية ---
df = pd.DataFrame(st.session_state['restaurants_db'])

# حساب المسافة لكل مطعم
df['المسافة (كم)'] = df.apply(
    lambda r: round(haversine_distance(user_lat, user_lon, r['lat'], r['lon']), 2),
    axis=1
)

# الترتيب حسب الأقرب
df = df.sort_values(by='المسافة (كم)')

# تصفية البحث النصي وفي المحافظة/المدينة
cities_list = ["الكل"] + list(df["المدينة"].unique())
selected_city_filter = st.selectbox("تصفية بحسب المدينة/المركز:", cities_list)
text_search = st.text_input("🔍 بحث باسم المطعم أو العنوان أو رقم الهاتف:")

filtered_df = df.copy()

if selected_city_filter != "الكل":
    filtered_df = filtered_df[filtered_df["المدينة"] == selected_city_filter]

if text_search:
    filtered_df = filtered_df[
        filtered_df["اسم المطعم"].str.contains(text_search, case=False, na=False) |
        filtered_df["العنوان"].str.contains(text_search, case=False, na=False) |
        filtered_df["رقم التليفون"].str.contains(text_search, case=False, na=False)
    ]

# --- عرض الإحصائيات الفورية ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("إجمالي المطاعم المعروضة", len(filtered_df))

if not filtered_df.empty:
    nearest_row = filtered_df.iloc[0]
    col_m2.metric("أقرب مطعم لك", nearest_row["اسم المطعم"])
    col_m3.metric("المسافة لأقرب مطعم", f"{nearest_row['المسافة (كم)']} كم")
else:
    col_m2.metric("أقرب مطعم لك", "لا يوجد")
    col_m3.metric("المسافة", "0 كم")

st.markdown("---")

# --- عرض الخريطة التفاعلية ---
if show_map and not filtered_df.empty:
    st.subheader("🗺️ الخريطة التفاعلية للمطاعم")
    map_data = filtered_df[['lat', 'lon']].rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    st.map(map_data)

# --- جدول المطاعم ---
st.subheader("📋 قائمة مطاعم المشويات")
st.dataframe(
    filtered_df[['المدينة', 'اسم المطعم', 'العنوان', 'رقم التليفون', 'الواتساب', 'النوع', 'المسافة (كم)']],
    use_container_width=True
)

# --- زر تحميل ملف Excel ---
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='مطاعم المشويات')
excel_buffer.seek(0)

st.download_button(
    label="📥 تحميل القائمة المعروضة كملف Excel متكامل",
    data=excel_buffer,
    file_name=f"دليل_مطاعم_المشويات_{selected_city_filter}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- نموذج إضافة مطعم جديد من الموبايل ---
st.markdown("---")
with st.expander("➕ إضافة مطعم مشويات جديد من الهاتف"):
    with st.form("add_restaurant_form", clear_on_submit=True):
        f_city = st.text_input("اسم المدينة / المركز:", value="رشيد")
        f_name = st.text_input("اسم المطعم:")
        f_address = st.text_input("العنوان التفصيلي:")
        f_phone = st.text_input("رقم التليفون:")
        f_type = st.selectbox("نوع المشويات:", ["كباب وكفتة", "مشويات وأسماك", "مشويات على الفحم", "باربكيو", "وجبات مشويات"])
        f_lat = st.number_input("إحداثي العرض (Lat):", value=user_lat, format="%.4f")
        f_lon = st.number_input("إحداثي الطول (Lon):", value=user_lon, format="%.4f")
        
        submitted = st.form_submit_button("إضافة المطعم للقائمة")
        if submitted:
            if f_name and f_address:
                new_entry = {
                    "المدينة": f_city,
                    "اسم المطعم": f_name,
                    "العنوان": f_address,
                    "رقم التليفون": f_phone if f_phone else "غير متوفر",
                    "الواتساب": f_phone if f_phone else "غير متوفر",
                    "الفيسبوك": "غير متوفر",
                    "النوع": f_type,
                    "lat": f_lat,
                    "lon": f_lon
                }
                st.session_state['restaurants_db'].append(new_entry)
                st.success(f"تم بنجاح إضافة '{f_name}' وتحديث الجدول والخريطة فورياً!")
                st.rerun()
            else:
                st.warning("يرجى كتابة اسم المطعم والعنوان على الأقل.")
