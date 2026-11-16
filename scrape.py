"""Shopier vitrinini products.json'a aktarır. Sadece okuma yapar."""
import json, re, sys, time, argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

BRANDS = ["Prada", "Moncler", "Loro Piana", "Brunello Cucinelli", "Stefano Ricci", "Kiton",
          "Tom Ford", "Berluti", "Hermes", "Dior", "Louis Vuitton", "Gucci", "Valentino",
          "Loewe", "Etro", "Fendi", "Jacquemus", "Bottega Veneta", "Amiri", "Dolce Gabbana",
          "Ami Paris", "Tiffany", "Zegna", "Burberry", "Van Cleef"]

CATS = {"Ceket / Mont": ["ceket", "mont", "kaşe", "puffer", "yelek", "trençkot"],
        "Triko / Sweat": ["triko", "kazak", "sweat", "hırka", "eşofman"],
        "Pantolon / Şort": ["pantolon", "jogger", "şort"],
        "Gömlek": ["gömlek"],
        "T-Shirt": ["t-shirt", "tişört"],
        "Ayakkabı / Terlik": ["ayakkabı", "sneaker", "terlik", "loafer", "bot"],
        "Çanta / Clutch": ["çanta", "clutch", "bag"],
        "Kemer / Cüzdan": ["kemer", "cüzdan"],
        "Güneş Gözlüğü": ["gözlük"]}


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            })
            with urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "ignore")
        except (URLError, HTTPError) as e:
            print(f"deneme {i+1} başarısız: {e}")
            time.sleep(4)
    return ""


def num(t):
    d = re.sub(r"[^\d]", "", t or "")
    return int(d) if d else 0


def classify(title):
    t = title.lower()
    brand = next((b for b in BRANDS if b.lower() in t), "Diğer")
    cat = next((c for c, kws in CATS.items() if any(k in t for k in kws)), "Diğer")
    return brand, cat


def parse(html, slug, shop):
    out, seen = [], set()
    link_re = re.compile(r'href="(?:https://www\.shopier\.com)?/' + re.escape(slug) + r'/(\d+)"')
    for m in link_re.finditer(html):
        pid = m.group(1)
        if pid in seen:
            continue
        seen.add(pid)
        block = html[m.start(): m.start() + 2600]
        img = re.search(r'(https://cdn\.shopier\.app/pictures_[^"\s]+)', block)
        alt = re.search(r'<img[^>]+alt="([^"]*)"', block)
        prices = re.findall(r'([\d.]{3,})\s*TL', block)
        if not img or not alt or not prices:
            continue
        vals = sorted(v for v in (num(p) for p in prices) if v > 0)
        if not vals:
            continue
        title = alt.group(1).strip()[:140]
        if len(title) < 8:
            continue
        brand, cat = classify(title)
        out.append({
            "id": pid,
            "title": title,
            "price": vals[0],
            "old_price": vals[-1] if len(vals) > 1 else vals[0],
            "image": img.group(1),
            "url": f"{shop}/{pid}",
            "brand": brand,
            "category": cat,
        })
    return out


def main(slug, out_path):
    shop = f"https://www.shopier.com/{slug}"
    html = fetch(shop)
    print(f"html: {len(html)} karakter")

    items = parse(html, slug, shop)
    print(f"ayrıştırılan ürün: {len(items)}")

    if not items:
        print("ÜRÜN YOK — products.json'a dokunulmadı, mevcut liste korunuyor.")
        sys.exit(1)

    items.sort(key=lambda x: int(x["id"]), reverse=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"{len(items)} ürün -> {out_path}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--slug", default="167brands")
    a.add_argument("--out", default="products.json")
    args = a.parse_args()
    main(args.slug, args.out)
