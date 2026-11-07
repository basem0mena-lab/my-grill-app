
import streamlit as st
import pandas as pd
import numpy as np
import io
import math
import os
import re

# 1. Page Config
st.set_page_config(
    page_title='دليل مطاعم المشويات - تحديد الموقع',
    page_icon='🥩',
    layout='wide',
    initial_sidebar_state='expanded'
)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

PRESET_RESTAURANTS = [
    {
        'المدينة': 'دمنهور',
        'اسم المطعم': 'مطعم منيسي للمشويات والأسماك',
        'العنوان': 'شارع الجمهورية - دمنهور',
        'رقم التليفون': '01027622009',
        'الواتساب': '01027622009',
        'الفيسبوك': 'متوفر',
        'النوع': 'مشويات وأسماك',
        'lat': 31.0379,
        'lon': 30.4682
    },
    {
        'المدينة': 'دمنهور',
        'اسم المطعم': 'قصر الهداية للمشويات',
        'العنوان': 'شارع الجيش - دمنهور',
        'رقم التليفون': '045-3312000',
        'الواتساب': 'غير متوفر',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'كباب ومشويات',
        'lat': 31.0345,
        'lon': 30.4621
    },
    {
        'المدينة': 'دمنهور',
        'اسم المطعم': 'مطعم الصفوة',
        'العنوان': 'شارع قونيا - دمنهور',
        'رقم التليفون': '01001234567',
        'الواتساب': '01001234567',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'مشويات شرقية',
        'lat': 31.0401,
        'lon': 30.4710
    },
    {
        'المدينة': 'رشيد',
        'اسم المطعم': 'مطعم محمد عبد الحميد الكبابجي',
        'العنوان': 'شارع السوق - مدينة رشيد',
        'رقم التليفون': '045-2921382',
        'الواتساب': 'غير متوفر',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'كباب ومشويات',
        'lat': 31.4014,
        'lon': 30.4165
    },
    {
        'المدينة': 'رشيد',
        'اسم المطعم': 'كبابجي الضغط العالي',
        'العنوان': 'شارع الضغط العالي (أمام فلينا ترافل) - رشيد',
        'رقم التليفون': '01099887766',
        'الواتساب': '01099887766',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'مشويات على الفحم',
        'lat': 31.4050,
        'lon': 30.4210
    },
    {
        'المدينة': 'كفر الدوار',
        'اسم المطعم': 'قرية راضي باربكيو (Radi BBQ)',
        'العنوان': 'الطريق الدولي السريع - الكيلو 30 - كفر الدوار',
        'رقم التليفون': '01223344556',
        'الواتساب': '01223344556',
        'الفيسبوك': 'متوفر',
        'النوع': 'باربكيو ومشويات بلدي',
        'lat': 31.1325,
        'lon': 30.1294
    },
    {
        'المدينة': 'أبو المطامير',
        'اسم المطعم': 'قصر الشوق للمشويات',
        'العنوان': 'الشارع الرئيسي - مركز أبو المطامير',
        'رقم التليفون': '01011223344',
        'الواتساب': '01011223344',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'مشويات وكباب',
        'lat': 30.9100,
        'lon': 30.1700
    },
    {
        'المدينة': 'كوم حمادة',
        'اسم المطعم': 'مطعم الملاح للمشويات',
        'العنوان': 'شارع المحطة - كوم حمادة',
        'رقم التليفون': '045-3680000',
        'الواتساب': 'غير متوفر',
        'الفيسبوك': 'غير متوفر',
        'النوع': 'كباب وكفتة ومشويات',
        'lat': 30.7540,
        'lon': 30.6970
    },
    {
        'المدينة': 'مدينة بدر',
        'اسم المطعم': 'مطاعم سامي أبو الريش للمشويات',
        'العنوان': 'المنطقة المركزية - مدينة بدر',
        'رقم التليفون': '01066778899',
        'الواتساب': '01066778899',
        'الفيسبوك': 'متوفر',
        'النوع': 'مشويات ولحوم طازجة',
        'lat': 30.5730,
        'lon': 30.7120
    }
]

if 'restaurants_db' not in st.session_state:
    st.session_state['restaurants_db'] = PRESET_RESTAURANTS.copy()

st.title('🥩 استكشاف وتحديد المطاعم حول أي موقع على الخريطة')
st.caption('اختر أي نقطة على الخريطة وحدد نطاق المسافة لمعرفة عدد المطاعم، أسمائها، وكافة وسائل التواصل المتاحة بها.')

st.sidebar.header('📍 1. تحديد النقطة على الخريطة')

PRESET_LOCATIONS = {
    'دمنهور (عاصمة البحيرة)': (31.0379, 30.4682),
    'رشيد': (31.4014, 30.4165),
    'كفر الدوار': (31.1325, 30.1294),
    'أبو المطامير': (30.9100, 30.1700),
    'كوم حمادة': (30.7540, 30.6970),
    'مدينة بدر': (30.5730, 30.7120),
    'الإسكندرية': (31.2001, 29.9187),
    'القاهرة': (30.0444, 31.2357),
    'تحديد إحداثيات موقع خاص': None
}

selected_location_name = st.sidebar.selectbox('اختر الموقع على الخريطة:', list(PRESET_LOCATIONS.keys()))

if selected_location_name == 'تحديد إحداثيات موقع خاص':
    center_lat = st.sidebar.number_input('خط العرض (Lat):', value=31.0379, format='%.4f')
    center_lon = st.sidebar.number_input('خط الطول (Lon):', value=30.4682, format='%.4f')
else:
    center_lat, center_lon = PRESET_LOCATIONS[selected_location_name]

st.sidebar.markdown('---')
st.sidebar.header('📏 2. نطاق المسافة (كم)')
max_distance_km = st.sidebar.slider(
    'حدد نصف قطر نطاق البحث (كيلومتر):',
    min_value=1,
    max_value=50,
    value=15,
    step=1
)

df = pd.DataFrame(st.session_state['restaurants_db'])

df['المسافة (كم)'] = df.apply(
    lambda r: round(haversine_distance(center_lat, center_lon, r['lat'], r['lon']), 2),
    axis=1
)

in_range_df = df[df['المسافة (كم)'] <= max_distance_km].sort_values(by='المسافة (كم)')

st.subheader(f'📍 نتائج الموقع المحدد: {selected_location_name}')

col1, col2, col3 = st.columns(3)
col1.metric('📊 عدد المطاعم في هذا الموقع/النطاق', f'{len(in_range_df)} مطاعم')
col2.metric('📏 نطاق المسافة المحدد', f'{max_distance_km} كم')

if not in_range_df.empty:
    nearest = in_range_df.iloc[0]
    col3.metric('🥇 أقرب مطعم للموقع', f'{nearest["اسم المطعم"]} ({nearest["المسافة (كم)"]} كم)')
else:
    col3.metric('🥇 أقرب مطعم للموقع', 'لا يوجد في هذا النطاق')

st.markdown('---')

st.subheader('🗺️ خريطة المطاعم داخل النطاق المحدد')

if not in_range_df.empty:
    map_df = in_range_df[['lat', 'lon']].rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    st.map(map_df)
else:
    st.warning('⚠️ لا توجد مطاعم في هذا النطاق. قم بزيادة نطاق المسافة من الشريط الجانبي.')

st.markdown('---')
st.subheader(f'📞 تفاصيل وسائل التواصل لكل مطعم ({len(in_range_df)} مطعم)')

if in_range_df.empty:
    st.info('قم بتوسيع مسافة النطاق من الشريط الجانبي لعرض المطاعم المجاورة.')
else:
    for idx, row in in_range_df.iterrows():
        with st.expander(f'🥩 {row["اسم المطعم"]} — ({row["المدينة"]}) - يبعد {row["المسافة (كم)"]} كم', expanded=True):
            c_info1, c_info2 = st.columns(2)
            
            with c_info1:
                st.write(f'**📍 العنوان:** {row["العنوان"]}')
                st.write(f'**🔥 نوع المشويات:** {row["النوع"]}')
                st.write(f'**📏 المسافة الدقيقة:** {row["المسافة (كم)"]} كم من الموقع المحدد')
                
            with c_info2:
                st.write('**📱 وسائل التواصل المتاحة:**')
                phone = str(row['رقم التليفون'])
                st.write(f'📞 **الهاتف:** {phone}')
                wa = str(row['الواتساب'])
                st.write(f'💬 **الواتساب:** {wa}')
                fb = str(row['الفيسبوك'])
                st.write(f'🌐 **الفيسبوك:** {fb}')

st.markdown('---')
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    in_range_df.to_excel(writer, index=False, sheet_name='مطاعم النطاق المحدد')
excel_buffer.seek(0)

st.download_button(
    label=f'📥 تحميل قائمة هذا الموقع ({len(in_range_df)} مطعم) كملف Excel',
    data=excel_buffer,
    file_name=f'مطاعم_نطاق_{selected_location_name}.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
