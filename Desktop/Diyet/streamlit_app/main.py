# Streamlit Cloud'a deploy için main dosyası
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
import base64
from io import BytesIO

# API URL'leri
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")

st.title("Diyet Foto Günlüğü")
st.write("""
Bu uygulama, Diyet Foto Günlüğü backend API'sine bağlanmaktadır.

Uygulamayı kullanmak için:
1. Backend API'yi çalıştırın (Node.js)
2. Doğru API_BASE_URL'yi çevre değişkeni olarak ayarlayın
3. Uygulamaya giriş yapın
""")

st.info("Bu uygulamayı kullanmak için Node.js backend API'yi çalıştırmalısınız. Detaylı kurulum bilgileri için README dosyasına bakın.")

# Streamlit Cloud deploy için gösterim
st.subheader("Uygulama Görünümü")
st.image("https://via.placeholder.com/800x500.png?text=Diyet+Foto+Gunlugu", caption="Uygulama görünümü")

st.write("""
## Özellikler
- Kullanıcı kimlik doğrulama (Ben/Eşim için ayrı PIN kodları)
- Fotoğraf yükleme ve EXIF tarih/saat verisi okuma
- Öğün tipi (Kahvaltı, Öğle, Akşam, Atıştırma) seçimi
- Fotoğraflara not ekleme
- Günlere göre gruplanmış diyetisyen görünümü
- PDF rapor oluşturma ve indirme
""")

st.code('''
# Backend API'yi çalıştırma
cd diyet-foto-gunlugu
npm install
npm start

# Streamlit uygulamasını çalıştırma
cd streamlit_app
streamlit run app.py
''', language='bash')

# Görsel gösterimi
st.subheader("Uygulama Ekran Görüntüleri")
cols = st.columns(2)
with cols[0]:
    st.image("https://via.placeholder.com/400x300.png?text=Login+Screen", caption="Giriş Ekranı")
    
with cols[1]:
    st.image("https://via.placeholder.com/400x300.png?text=Dietitian+View", caption="Diyetisyen Görünümü")
