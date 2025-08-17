# Diyet Foto Günlüğü - Streamlit Uygulaması

Bu Streamlit uygulaması, "Diyet Foto Günlüğü" Node.js API'sine bağlanarak yemek fotoğraflarını görüntüleyip, PDF raporu oluşturan bir arayüz sağlar.

## Özellikler

- Kullanıcı girişi (A/B kullanıcıları için PIN doğrulama)
- Tarih aralığı ve kullanıcı bazlı filtreleme
- Günlere göre gruplanmış yemek fotoğrafları
- PDF raporu indirme

## Kurulum ve Çalıştırma

1. Gereksinimleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Streamlit uygulamasını başlatın:
   ```
   streamlit run app.py
   ```

3. Tarayıcınızda `http://localhost:8501` adresini açın.

## Çevre Değişkenleri

- `API_BASE_URL`: Node.js API'nin çalıştığı URL (örn. http://localhost:3000)
