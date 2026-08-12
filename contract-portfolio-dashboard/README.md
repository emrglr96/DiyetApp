# Sözleşme Portföy Paneli — PowerBI Prototip

Sözleşme portföyünü yenileme riski ve marj sağlığı açısından izlemek için hazırlanmış,
tek dosyalık interaktif bir PowerBI prototipi (`index.html`). Ekibin PowerBI'da nasıl
kuracağına dair rehber panelin içinde yer alır.

## Kullanım

`index.html` dosyasını herhangi bir modern tarayıcıda açın — kurulum gerekmez.
Chart.js ve fontlar CDN üzerinden yüklenir (çevrimiçi bağlantı gerektirir).

## İçerik

- **KPI kartları** — sözleşme sayısı, yıllık ciro, ciro ağırlıklı SM%, 6 ayda bitecek ciro, kritik marjlı sözleşmeler.
- **Yenileme Ufku** — önümüzdeki 24 ayın nokta grafiği (konum = bitiş tarihi, boyut = yıllık bedel, renk = marj sağlığı).
- **Pareto** — ciro konsantrasyonu (kümülatif pay çizgisiyle).
- **Risk haritası** — bedel × marj scatter (log ölçek).
- **Yenileme pipeline** — riske giren cironun 0-3 / 3-6 / 6-12 / 12+ ay dilimleri.
- **Marj dağılımı** — SM% bantlarına göre sözleşme sayısı ve ciro.
- **Sözleşme listesi** — sıralanabilir tam tablo (YTD vs son dönem trend farkıyla).
- **Veri kalitesi bulguları** — bitiş < başlangıç, süresi dolup listede kalanlar, mükerrer sözleşme numaraları, metin/boş SM% değerleri, TL kayıtları.
- **PowerBI kurulum rehberi** — her bileşenin slicer / measure / hesaplanmış kolon karşılığı.

## Notlar

- Veriler prototip amaçlı manipüle edilmiştir; referans tarihi 12.08.2026'dır.
- EUR/TRY kuru üstteki alandan değiştirilebilir (TL sözleşmeler bu kurla çevrilir).
