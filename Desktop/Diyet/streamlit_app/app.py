import streamlit as st
import requests
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime, timedelta
import pytz
import os
import json

# Streamlit uygulama başlığı ve konfigürasyonu
st.set_page_config(
    page_title="Diyet Foto Günlüğü",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL'leri - bunları çevre değişkenlerinden alabilirsiniz
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")
AUTH_URL = f"{API_BASE_URL}/api/auth/login"
MEALS_URL = f"{API_BASE_URL}/api/meals"
REPORT_URL = f"{API_BASE_URL}/api/report/pdf"

# CSS styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .block-container {
        padding-top: 1rem;
    }
    h1 {
        color: #22c55e;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 10px 16px;
        background-color: #f3f4f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #dcfce7 !important;
        color: #166534;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .card img {
        border-radius: 5px;
        width: 100%;
    }
    .meal-meta {
        display: flex;
        justify-content: space-between;
        margin: 10px 0;
        color: #4b5563;
        font-size: 0.9rem;
    }
    .date-header {
        margin: 20px 0 10px 0;
        background: #f3f4f6;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: 500;
    }
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def format_date(dt_str):
    """Tarihi formatla: YYYY-MM-DD -> DD.MM.YYYY"""
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%d.%m.%Y')

def format_time(dt_str):
    """Saati formatla: YYYY-MM-DDTHH:MM:SS -> HH:MM"""
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    vienna_tz = pytz.timezone('Europe/Vienna')
    dt = dt.astimezone(vienna_tz)
    return dt.strftime('%H:%M')

def login():
    """Kullanıcı girişi için form"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("Diyet Foto Günlüğü")
    st.subheader("Giriş")
    
    col1, col2 = st.columns(2)
    with col1:
        user_code = st.selectbox("Kullanıcı", ["A (Ben)", "B (Eşim)"])
        user_code = user_code[0]  # Sadece ilk karakteri al (A veya B)
    
    with col2:
        pin = st.text_input("PIN Kodu", type="password")
    
    if st.button("Giriş Yap", type="primary"):
        if not pin:
            st.error("Lütfen PIN kodunu girin")
            return False
        
        try:
            response = requests.post(
                AUTH_URL,
                json={"code": user_code, "pin": pin},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["token"]
                st.session_state.user = data["user"]
                st.session_state.logged_in = True
                st.success("Giriş başarılı!")
                st.experimental_rerun()
                return True
            else:
                st.error(f"Giriş başarısız: {response.json().get('error', 'Bilinmeyen hata')}")
                return False
        except Exception as e:
            st.error(f"Bağlantı hatası: {str(e)}")
            return False
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def get_meals(start_date, end_date, user_id="all"):
    """Belirtilen tarih aralığı ve kullanıcıya göre öğünleri getir"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "userId": user_id
    }
    
    try:
        response = requests.get(MEALS_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Veri alınamadı: {response.json().get('error', 'Bilinmeyen hata')}")
            return []
    except Exception as e:
        st.error(f"Bağlantı hatası: {str(e)}")
        return []

def download_pdf_report(start_date, end_date, user_id="all"):
    """PDF raporu indir"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "userId": user_id
    }
    
    try:
        response = requests.get(REPORT_URL, headers=headers, params=params, stream=True)
        
        if response.status_code == 200:
            # PDF dosyasını base64 formatına çevir
            pdf_data = BytesIO(response.content)
            base64_pdf = base64.b64encode(pdf_data.read()).decode('utf-8')
            
            # Dosya adı oluştur
            file_name = f"diyet-rapor-{start_date}-{end_date}.pdf"
            
            # İndirme bağlantısı
            pdf_display = f'<a href="data:application/pdf;base64,{base64_pdf}" download="{file_name}" target="_blank">📥 PDF Raporunu İndir</a>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error(f"PDF oluşturulamadı: {response.json().get('error', 'Bilinmeyen hata')}")
    except Exception as e:
        st.error(f"PDF indirme hatası: {str(e)}")

def display_meals_by_date(meals):
    """Öğünleri tarihe göre grupla ve görüntüle"""
    # Tarihe göre grupla
    meals_by_date = {}
    for meal in meals:
        date = meal["taken_at"].split("T")[0]
        if date not in meals_by_date:
            meals_by_date[date] = []
        meals_by_date[date].append(meal)
    
    # Her tarih için öğünleri göster
    for date in sorted(meals_by_date.keys()):
        formatted_date = format_date(date)
        st.markdown(f"<div class='date-header'>{formatted_date}</div>", unsafe_allow_html=True)
        
        # Her gün için bir grid oluştur
        cols = st.columns(3)
        
        for i, meal in enumerate(meals_by_date[date]):
            with cols[i % 3]:
                st.markdown(f"""
                <div class='card'>
                    <img src="{meal['imageUrl']}" alt="{meal['meal_type']}">
                    <div class='meal-meta'>
                        <span>{meal['User']['name']} • {meal['meal_type']}</span>
                        <span>{format_time(meal['taken_at'])}</span>
                    </div>
                    <div>{meal['note'] or ''}</div>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Ana uygulama"""
    # Oturum kontrolü
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login()
        return
    
    # Ana uygulama arayüzü
    st.title("Diyet Foto Günlüğü")
    
    # Sekmeler
    tabs = st.tabs(["📊 Diyetisyen Görünümü", "⚙️ Ayarlar"])
    
    with tabs[0]:
        st.subheader("Diyetisyen Görünümü")
        
        # Filtreler
        col1, col2, col3 = st.columns([2, 2, 1])
        
        # Son 7 günü varsayılan olarak ayarla
        default_end = datetime.now()
        default_start = default_end - timedelta(days=7)
        
        with col1:
            start_date = st.date_input("Başlangıç Tarihi", value=default_start)
        
        with col2:
            end_date = st.date_input("Bitiş Tarihi", value=default_end)
        
        with col3:
            user_filter = st.selectbox(
                "Kullanıcı",
                ["Tümü", "A (Ben)", "B (Eşim)"],
                index=0
            )
            
            # Kullanıcı filtresi değerini hazırla
            if user_filter == "Tümü":
                user_id = "all"
            else:
                user_id = user_filter[0]  # İlk karakteri al (A veya B)
        
        # Filtreleri uygula ve verileri getir
        if st.button("Filtrele", type="primary"):
            meals = get_meals(
                start_date.isoformat(),
                end_date.isoformat(),
                user_id
            )
            
            if meals:
                # PDF raporu indir
                download_pdf_report(
                    start_date.isoformat(),
                    end_date.isoformat(),
                    user_id
                )
                
                # Öğünleri görüntüle
                display_meals_by_date(meals)
            else:
                st.info("Seçilen aralıkta kayıt bulunamadı.")
    
    with tabs[1]:
        st.subheader("Ayarlar")
        
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
