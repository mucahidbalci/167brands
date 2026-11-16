# 167brands — taslak site

## Kurulum
1. `pip install playwright` sonra `playwright install chromium`
2. `python scrape.py` → products.json üretir
3. `python -m http.server 8000` → http://localhost:8000

## Güncelleme
GitHub Action her gece 03:00'te scrape.py çalıştırır, products.json commit edilir,
Vercel otomatik deploy eder.

Elle çalıştırmak için: Actions → katalog-sync → Run workflow

## Kategori düzeltme
scrape.py içindeki CATS sözlüğüne anahtar kelime ekle, tekrar çalıştır.
