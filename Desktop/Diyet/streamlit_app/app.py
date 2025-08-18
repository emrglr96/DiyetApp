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

# Demo mod kontrolü
DEMO_MODE = os.environ.get("STREAMLIT_DEMO_MODE", "true").lower() == "true"

# API URL'leri
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3001")
AUTH_URL = f"{API_BASE_URL}/api/auth/login"
MEALS_URL = f"{API_BASE_URL}/api/meals"
REPORT_URL = f"{API_BASE_URL}/api/report/pdf"

# Demo veriler
DEMO_USERS = {
    "A": {"name": "Ben", "pin": "1234"},
    "B": {"name": "Eşim", "pin": "1234"}
}

DEMO_MEALS = [
    {
        "id": "1",
        "meal_type": "Kahvaltı",
        "note": "Sağlıklı kahvaltı",
        "taken_at": "2025-08-17T08:00:00Z",
        "image_key": "demo1.jpg",
        "User": {"name": "Ben", "code": "A"}
    },
    {
        "id": "2", 
        "meal_type": "Öğle",
        "note": "Hafif öğle yemeği",
        "taken_at": "2025-08-17T12:30:00Z",
        "image_key": "demo2.jpg",
        "User": {"name": "Eşim", "code": "B"}
    }
]

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
    st.title("🍽️ Diyet Foto Günlüğü")
    st.subheader("Giriş")
    
    # Demo mod kontrolü
    if DEMO_MODE:
        st.success("🚀 Demo Modu Aktif - Backend API gerekmez!")
        st.info("Demo kullanıcılar: A (Ben) ve B (Eşim), PIN: 1234")
    
    col1, col2 = st.columns(2)
    with col1:
        user_code = st.selectbox("Kullanıcı", ["A (Ben)", "B (Eşim)"])
        user_code = user_code[0]  # Sadece ilk karakteri al (A veya B)
    
    with col2:
        pin = st.text_input("PIN Kodu", type="password", value="1234")
    
    if st.button("🔑 Giriş Yap", type="primary"):
        if not pin:
            st.error("Lütfen PIN kodunu girin")
            return False
        
        # Demo mod kontrolü
        if DEMO_MODE:
            if user_code in DEMO_USERS and DEMO_USERS[user_code]["pin"] == pin:
                st.session_state.token = f"demo_token_{user_code}"
                st.session_state.user = {"name": DEMO_USERS[user_code]["name"], "code": user_code}
                st.session_state.logged_in = True
                st.success("✅ Demo giriş başarılı!")
                st.rerun()
                return True
            else:
                st.error("❌ Hatalı kullanıcı kodu veya PIN")
                return False
        
        # Gerçek API girişi
        with st.spinner("Giriş yapılıyor..."):
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
                    st.success("✅ Giriş başarılı!")
                    st.rerun()
                    return True
                else:
                    st.error(f"❌ Giriş başarısız: {response.json().get('error', 'Bilinmeyen hata')}")
                    return False
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Bağlantı hatası: {str(e)}")
                st.info("💡 Demo modu için STREAMLIT_DEMO_MODE=true ayarlayın")
                return False
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def get_meals(start_date, end_date, user_id="all"):
    """Belirtilen tarih aralığı ve kullanıcıya göre öğünleri getir"""
    if DEMO_MODE:
        # Demo verilerini al
        all_meals = DEMO_MEALS.copy()
        
        # Kullanıcının eklediği öğünleri ekle
        if 'user_meals' in st.session_state:
            all_meals.extend(st.session_state.user_meals)
        
        # Filtreleme
        filtered_meals = []
        for meal in all_meals:
            if user_id == "all" or meal["User"]["code"] == user_id:
                filtered_meals.append(meal)
        return filtered_meals
    
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
    if DEMO_MODE:
        st.info("🎯 Demo modunda PDF raporu özelliği simülasyonu")
        st.download_button(
            label="📥 Demo PDF Raporunu İndir",
            data="Demo PDF içeriği - Gerçek implementasyonda PDF oluşturulacak",
            file_name=f"demo-diyet-rapor-{start_date}-{end_date}.txt",
            mime="text/plain"
        )
        return
    
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
    if not meals:
        st.info("📭 Seçilen kriterlerde öğün bulunamadı")
        return
    
    # Tarihe göre grupla
    meals_by_date = {}
    for meal in meals:
        # taken_at'tan tarih çıkar
        taken_at = meal["taken_at"]
        if isinstance(taken_at, str):
            # ISO formatından datetime'a çevir
            dt = datetime.fromisoformat(taken_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%d.%m.%Y')
        else:
            date_str = taken_at.strftime('%d.%m.%Y')
            
        if date_str not in meals_by_date:
            meals_by_date[date_str] = []
        meals_by_date[date_str].append(meal)
    
    # Tarihleri sırala (en yeni önce)
    sorted_dates = sorted(meals_by_date.keys(), key=lambda x: datetime.strptime(x, '%d.%m.%Y'), reverse=True)
    
    for date in sorted_dates:
        st.markdown(f'<div class="date-header">📅 {date}</div>', unsafe_allow_html=True)
        
        day_meals = meals_by_date[date]
        cols = st.columns(min(len(day_meals), 3))  # Maksimum 3 sütun
        
        for i, meal in enumerate(day_meals):
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    
                    # Demo modu için placeholder resim
                    if DEMO_MODE:
                        st.image("https://via.placeholder.com/300x200/22c55e/ffffff?text=Demo+Meal", use_container_width=True)
                    else:
                        # Gerçek resim URL'si (implement edilecek)
                        st.image("https://via.placeholder.com/300x200/e5e7eb/6b7280?text=Food+Image", use_container_width=True)
                    
                    # Öğün detayları
                    st.markdown(f'<div class="meal-meta"><span><strong>{meal["meal_type"]}</strong></span><span>{format_time(meal["taken_at"])}</span></div>', unsafe_allow_html=True)
                    
                    if meal.get("note"):
                        st.write(f"💭 {meal['note']}")
                    
                    st.markdown(f"👤 **{meal['User']['name']}**")
                    st.markdown('</div>', unsafe_allow_html=True)
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
    st.title(f"🍽️ Diyet Foto Günlüğü - Hoş geldin {st.session_state.user['name']}!")
    
    if DEMO_MODE:
        st.info("🎯 Demo Modu - Örnek verilerle çalışıyor")
    
    # Sekmeler
    tabs = st.tabs(["� Veri Girişi", "�📊 Diyetisyen Görünümü", "⚙️ Ayarlar"])
    
    with tabs[0]:
        st.subheader("🍽️ Yeni Öğün Ekle")
        
        # Veri girişi formu
        with st.form("meal_form", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                meal_type = st.selectbox(
                    "🍴 Öğün Türü",
                    ["Kahvaltı", "Öğle", "Akşam", "Atıştırma"],
                    index=0
                )
                
                note = st.text_area(
                    "📝 Not (Opsiyonel)",
                    placeholder="Örn: Sağlıklı kahvaltı, az yağlı yemek...",
                    height=100
                )
            
            with col2:
                taken_at_date = st.date_input("📅 Tarih", value=datetime.now().date())
                taken_at_time = st.time_input("🕐 Saat", value=datetime.now().time())
            
            # Fotoğraf yükleme
            uploaded_file = st.file_uploader(
                "📸 Yemek Fotoğrafı Yükle",
                type=['png', 'jpg', 'jpeg'],
                help="PNG, JPG veya JPEG formatında fotoğraf yükleyebilirsiniz"
            )
            
            # Fotoğraf önizlemesi
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Yüklenen Fotoğraf", width=300)
            
            # Form gönderme butonu
            submitted = st.form_submit_button("💾 Öğünü Kaydet", type="primary")
            
            if submitted:
                if uploaded_file is None:
                    st.error("❌ Lütfen bir fotoğraf yükleyin!")
                else:
                    # Tarih ve saati birleştir
                    taken_at = datetime.combine(taken_at_date, taken_at_time)
                    
                    if DEMO_MODE:
                        # Demo modunda sadece başarı mesajı göster
                        st.success(f"✅ {meal_type} öğünü başarıyla kaydedildi!")
                        st.info(f"👤 Kullanıcı: {st.session_state.user['name']}")
                        st.info(f"📅 Tarih: {taken_at.strftime('%d.%m.%Y %H:%M')}")
                        if note:
                            st.info(f"📝 Not: {note}")
                        
                        # Demo veriye ekle (session state'te tutabiliriz)
                        if 'user_meals' not in st.session_state:
                            st.session_state.user_meals = []
                        
                        new_meal = {
                            "id": f"user_{len(st.session_state.user_meals)}",
                            "meal_type": meal_type,
                            "note": note,
                            "taken_at": taken_at.isoformat() + "Z",
                            "image_key": f"user_upload_{len(st.session_state.user_meals)}.jpg",
                            "User": st.session_state.user
                        }
                        st.session_state.user_meals.append(new_meal)
                        
                    else:
                        # Gerçek API'ye gönder
                        with st.spinner("Öğün kaydediliyor..."):
                            try:
                                # Multipart form data hazırla
                                files = {'image': uploaded_file.getvalue()}
                                data = {
                                    'mealType': meal_type,
                                    'note': note,
                                    'takenAt': taken_at.isoformat()
                                }
                                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                                
                                response = requests.post(
                                    f"{API_BASE_URL}/api/upload",
                                    files=files,
                                    data=data,
                                    headers=headers,
                                    timeout=30
                                )
                                
                                if response.status_code == 201:
                                    st.success("✅ Öğün başarıyla kaydedildi!")
                                else:
                                    st.error(f"❌ Kayıt başarısız: {response.json().get('error', 'Bilinmeyen hata')}")
                                    
                            except Exception as e:
                                st.error(f"❌ Bağlantı hatası: {str(e)}")
        
        # Kullanıcının son öğünlerini göster
        st.subheader("📋 Son Eklenen Öğünlerim")
        
        if DEMO_MODE and 'user_meals' in st.session_state and st.session_state.user_meals:
            for meal in reversed(st.session_state.user_meals[-3:]):  # Son 3 öğün
                with st.expander(f"{meal['meal_type']} - {format_date(meal['taken_at'])} {format_time(meal['taken_at'])}"):
                    if meal.get('note'):
                        st.write(f"📝 {meal['note']}")
                    st.write(f"👤 {meal['User']['name']}")
        else:
            st.info("🍽️ Henüz öğün eklenmemiş. Yukarıdaki formu kullanarak ilk öğününüzü ekleyin!")

    with tabs[1]:
        st.subheader("Diyetisyen Görünümü")
        
        # Filtreler
        col1, col2, col3 = st.columns([2, 2, 1])
        
        # Son 7 günü varsayılan olarak ayarla
        default_end = datetime.now().date()
        default_start = default_end - timedelta(days=7)
        
        with col1:
            start_date = st.date_input("📅 Başlangıç Tarihi", value=default_start)
        
        with col2:
            end_date = st.date_input("📅 Bitiş Tarihi", value=default_end)
        
        with col3:
            user_filter = st.selectbox(
                "👤 Kullanıcı",
                ["Tümü", "A (Ben)", "B (Eşim)"],
                index=0
            )
            
            # Kullanıcı filtresi değerini hazırla
            if user_filter == "Tümü":
                user_id = "all"
            else:
                user_id = user_filter[0]  # İlk karakteri al (A veya B)
        
        # Otomatik veri yükleme (Demo modunda)
        if DEMO_MODE:
            st.write("🔄 Demo veriler otomatik yükleniyor...")
            meals = get_meals(
                start_date.isoformat(),
                end_date.isoformat(),
                user_id
            )
            
            if meals:
                # PDF raporu indir butonu
                col_pdf1, col_pdf2 = st.columns([1, 2])
                with col_pdf1:
                    download_pdf_report(
                        start_date.isoformat(),
                        end_date.isoformat(),
                        user_id
                    )
                
                # Öğünleri görüntüle
                display_meals_by_date(meals)
            else:
                st.info("📭 Seçilen aralıkta kayıt bulunamadı.")
        else:
            # Gerçek mod - filtreleme butonu ile
            if st.button("🔍 Filtrele", type="primary"):
                with st.spinner("Yemekler getiriliyor..."):
                    meals = get_meals(
                        start_date.isoformat(),
                        end_date.isoformat(),
                        user_id
                    )
                    
                    if meals:
                        # PDF raporu indir
                        with st.spinner("PDF raporu hazırlanıyor..."):
                            download_pdf_report(
                                start_date.isoformat(),
                                end_date.isoformat(),
                                user_id
                            )
                        
                        # Öğünleri görüntüle
                        display_meals_by_date(meals)
                    else:
                        st.info("📭 Seçilen aralıkta kayıt bulunamadı.")

    with tabs[2]:
        st.subheader("⚙️ Ayarlar")
        
        # API URL bilgisi
        st.info(f"🔗 API URL: {API_BASE_URL}")
        st.info(f"🎯 Demo Modu: {'Aktif' if DEMO_MODE else 'Pasif'}")
        
        # Demo modu toggle
        demo_toggle = st.toggle("Demo Modu", value=DEMO_MODE)
        if demo_toggle != DEMO_MODE:
            os.environ["STREAMLIT_DEMO_MODE"] = "true" if demo_toggle else "false"
            st.info("🔄 Değişikliklerin geçerli olması için sayfayı yenileyin")
        
        # Çıkış yap
        if st.button("🚪 Çıkış Yap", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user = None
if __name__ == "__main__":
    main()
