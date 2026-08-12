# Sözleşme Portföy Paneli — Masaüstü Uygulaması

Excel dosyanızı yükleyin; sözleşme portföyünüz **yenileme riski** ve **marj sağlığı**
açısından interaktif bir panoda görünsün. Uygulama, hazır dashboard'un hesap/grafik
çekirdeğini korur; üzerine **önceliklendirilmiş "Yangın Yerleri" listesi**, **dinamik
veri kalitesi** ve **sağlık/öncelik filtreleri** ekler.

- **Tek pencere masaüstü hissi** (pywebview). pywebview başlatılamazsa otomatik
  olarak yerel bir sunucuya düşer ve varsayılan tarayıcıda açılır.
- **İnternet gerektirmez.** Chart.js ve yazı tipleri (IBM Plex) uygulamanın
  içine gömülüdür.
- **Kurulum/yönetici yetkisi gerektirmez.** Taşınabilir (portable) `.exe` olarak
  paketlenebilir; klasörü kopyalayıp çalıştırmanız yeterli.

---

## 1. Hızlı başlangıç (kaynak koddan)

Gereksinim: **Python 3.11+**

### Windows
```bat
calistir.bat
```
İlk çalıştırmada sanal ortam kurar, bağımlılıkları indirir ve uygulamayı açar.

### Linux / macOS (geliştirme)
```bash
./run.sh
```

Uygulama açılınca **"📂 Excel Yükle"** düğmesine basın, `.xlsx` dosyanızı seçin;
pano verinizle birlikte gelir.

> Örnek dosya: `sample/ornek_veri.xlsx` (10 satır, tüm kenar durumları içerir).
> Yeniden üretmek için: `python sample/make_sample.py`

---

## 2. Taşınabilir .exe üretme (Windows)

```bat
derle.bat
```
veya elle:
```bat
pip install -r requirements.txt pyinstaller
pyinstaller build.spec
```

Çıktı: `dist\SozlesmePortfoyPaneli\`
- **Klasörün tamamını** kopyalayın (tek dosya değil — `onedir` modu).
- `SozlesmePortfoyPaneli.exe` ile çalıştırın.
- Kurulum yok, yönetici yetkisi yok, internet yok.

`onedir` modu bilinçli tercih edildi: `onefile`'a göre antivirüs yanlış-pozitif
riski daha düşük ve ilk açılış daha hızlıdır (geçici dizine çıkarım yapmaz).
UPX sıkıştırması da AV uyumu için kapalıdır.

> **WebView2 notu:** pywebview Windows'ta Microsoft Edge **WebView2** çalışma
> zamanını kullanır. Windows 10/11'de genellikle hazırdır. Nadiren yoksa,
> uygulama otomatik olarak **tarayıcı mod(Flask)**'a düşer; yine de çalışır.

---

## 3. Beklenen Excel şeması

Kolon adları ve sırası **birebir** şöyle olmalı (başlık ilk satırda):

| # | Kolon |
|---|-------|
| 1 | Contract Number |
| 2 | Müşteri |
| 3 | Sözleşmenin Yıllık Bedeli |
| 4 | (YTD) SM% |
| 5 | (Fiscal Year) SM% |
| 6 | Sözleşme Yenileme(Başlangıç) Tarihi |
| 7 | Sözleşme Bitiş Tarihi |
| 8 | Sözleşme Yenileme Period |
| 9 | Sözleşme Bitiş Period |
| 10 | (Son Sözleşme Dönemi) SM% |
| 11–15 | 1. Yıl / 2. Yıl / 3. Yıl / 4. Yıl / 5.yıl |
| 16 | Sözleşmenin Toplam Bedeli |
| 17 | Notlar |

**Kolon adı birebir eşleşmezse**, uygulama en yakın eşleşmeyi bulup
(ör. `Musteri` → `Müşteri`, `Contract No` → `Contract Number`) **onayınızı ister**.

---

## 4. Otomatik ele alınan veri durumları

| Durum | Davranış |
|-------|----------|
| Para: `€ 40,000.00`, `₺1,200,000.00`, `40.000,00` | Sayıya çevrilir; TL satırlar `tl:true` işaretlenir ve panodaki EUR/TRY kuruyla çevrilir |
| Tarih: `01.01.2024`, `10/05/2022`, Excel datetime | Hepsi ayrıştırılır |
| SM% metin değer (`x/o` vb.) | `null` yapılır, sessizce düşürülmez — üstte uyarı olarak listelenir |
| SM% yüzde işaretli (`% 21.04%`) / yüzde-biçimli hücre | Normalize edilir (0–100 ölçeği) |
| Yıl kolonları boş | `null` |
| Bitiş < Başlangıç | `dataError:true` |
| Aynı Contract Number birden çok satırda | Satırlar **birleştirilmez**, olduğu gibi alınır |

- **`daysToEnd`, `expired`, `dataError`** alanları bilgisayarın **güncel tarihine**
  göre hesaplanır (panodaki `TODAY` da açılışta güncel tarihle değiştirilir).
- Bozuk tarih / metin SM% içeren satırlar uygulamayı **düşürmez**; her uyarı
  "hangi satır, hangi kolon" bilgisiyle panonun üstünde gösterilir.

---

## 5. 🔥 Yangın Yerleri — önceliklendirme

KPI'ların hemen altındaki panel, her sözleşmeye şeffaf bir **risk skoru (0–100)**
verir ve en yüksek skorluları **P1 / P2 / P3** önceliğiyle sıralar. Her satırda
**neden etiketleri** ve **önerilen aksiyon** yer alır.

**Risk skoru** dört bileşenden gelir:

| Bileşen | Ağırlık | Mantık |
|---------|---------|--------|
| Marj sağlığı (`son` SM%) | %55 | negatif → 1.0, `<%25` → 0.85, `<%60` → 0.4 … |
| Yenileme aciliyeti (`daysToEnd`) | %45 | ≤90 gün → 1.0, ≤183 → 0.7, ≤365 → 0.45 … |
| Marj trendi | +0.12 | `Δ (YTD−Son) < −10` ise erozyon cezası |
| Ciro büyüklüğü | çarpan | `0.45 + 0.55·√(yıllık/enBüyük)` — büyük ciro önceliği yükseltir |

Veri hatası olan (bitiş<başlangıç) satırlar taban 60 skorla işaretlenir.
**Öncelik**: skor ≥55 → **P1 (Acil)**, ≥32 → **P2 (Yüksek)**, aksi → **P3 (İzle)**.
Süresi dolmuş sözleşmeler yenileme yangını sayılmaz (ayrı DQ maddesi olur).

**Önerilen aksiyon** örnekleri: `≤90 gün` → "ACİL: yenileme görüşmesi + fiyat/marj
revizyonu"; `≤183 gün` → "Yenileme hattına al, teklif hazırla"; kritik marj →
"Marj iyileştirme: kapsam ve maliyet gözden geçir".

## 6. Filtreleme ve bubble ayrımı

Filtre barındaki **Sağlık** çipleri (Kritik / İzleme / Sağlıklı / Veri yok) çoklu
seçimlidir; risk haritası (bubble) ile yenileme ufku noktalarını **tek sağlık
sınıfına indirip net ayırt etmenizi** sağlar. **🔥 Sadece yangın yerleri** çipi
tüm panoyu öncelikli sözleşmelere daraltır. Diğer filtreler (min bedel, SM%,
yenileme penceresi, durum) Yangın Yerleri listesini de daraltır.

## 7. Pano içinden yeni dosya

Panonun sağ üstündeki **"↥ Yeni dosya yükle"** ile istediğiniz zaman farklı bir
Excel yükleyebilirsiniz. Son yüklenen dosyanın yolu hatırlanır; açılış ekranında
**"↻ Son dosyayı yeniden yükle"** seçeneği sunulur.

Ayar dosyası: `%APPDATA%\SozlesmePortfoyPaneli\config.json` (Windows).

---

## 8. Proje yapısı

```
contract-portfolio-desktop/
├── app/
│   ├── main.py       # giriş: pywebview; olmazsa Flask'a düşer
│   ├── server.py     # Flask geri-dönüş sunucusu (yalnızca 127.0.0.1)
│   ├── core.py       # ortak yükleme akışı (prepare/load)
│   ├── parser.py     # Excel -> JSON (tüm ayrıştırma kuralları)
│   ├── render.py     # şablona veri + güncel tarih enjeksiyonu
│   ├── config.py     # son dosya hatırlama (JSON)
│   └── paths.py      # geliştirme/donmuş yol çözümü
├── templates/
│   ├── dashboard_template.html  # hazır pano (yer tutucularla)
│   └── welcome.html             # karşılama + onay ekranı
├── assets/
│   ├── chart.min.js             # Chart.js 4.4.1 (yerel, offline)
│   ├── fonts.css + fonts/*.woff2 # IBM Plex (yerel, offline)
├── sample/
│   ├── make_sample.py
│   └── ornek_veri.xlsx
├── requirements.txt
├── build.spec        # PyInstaller (onedir, portable)
├── calistir.bat / derle.bat / run.sh
```

**Tasarım ilkesi:** Prototipin KPI/grafik hesap çekirdeği korundu; veri katmanı
(`__RAW_DATA__`, `__TODAY_ARGS__`, yerel varlıklar, "yeni dosya" köprüsü) enjekte
edilir. Üzerine **Yangın Yerleri (risk skoru + öncelik + aksiyon)**, **dinamik veri
kalitesi paneli** ve **sağlık/öncelik filtreleri** eklendi.

---

## 9. Veri kalitesi (tamamen dinamik)

- **"Veri kalitesi bulguları"** paneli artık **tümüyle verinizden** üretilir:
  bitiş<başlangıç kayıtları, süresi dolup listede kalanlar, mükerrer sözleşme
  numaraları, boş/okunamayan SM% (`x/o`), zarardaki sözleşmeler ve TL kayıtlar
  — hepsi gerçek isim ve sayılarla listelenir. (Önceki prototipteki sabit örnek
  adlar `A68`/`A143`/`A21–A23` kaldırıldı.)
- Ayrıca **dosya okuma sırasında** oluşan ayrıştırma uyarıları (metin SM%,
  okunamayan tarih vb.) panonun en üstünde ayrı bir şeritte, "hangi satır /
  hangi kolon" bilgisiyle gösterilir.

## 10. Bilinen notlar

- Hesaplama/grafik çekirdeği hazır prototipten korunur; üzerine Yangın Yerleri,
  dinamik DQ, sağlık filtresi ve dinamik kur notu **eklendi**.
- Risk skoru ağırlıkları `dashboard_template.html` içindeki `marginRisk` /
  `urgencyRisk` / `computeFires` fonksiyonlarında; iş kuralınıza göre kolayca
  ayarlanabilir.

---

## 11. Sık sorulanlar

**Uygulama açılmıyor / boş pencere?** WebView2 çalışma zamanı eksik olabilir;
uygulama otomatik tarayıcı moduna düşer. Düşmezse
`SPP_FORCE_FLASK=1` ortam değişkeniyle tarayıcı modunu zorlayabilirsiniz.

**Kur nasıl değişir?** Panonun sağ üstündeki **EUR/TRY kuru** kutusu. TL
sözleşmeler bu kurla anlık çevrilir.

**Verim şirket dışına gider mi?** Hayır. Her şey yereldir; Flask modunda bile
sunucu yalnızca `127.0.0.1`'e bağlanır, dışa kapalıdır.
