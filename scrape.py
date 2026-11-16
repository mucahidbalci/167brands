"""Shopier dükkanını products.json'a aktarır. Sadece okuma yapar, yavaş çalışır."""
import json, re, asyncio, argparse
from playwright.async_api import async_playwright

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


def classify(title: str):
    t = title.lower()
    brand = next((b for b in BRANDS if b.lower() in t), "Diğer")
    cat = next((c for c, kws in CATS.items() if any(k in t for k in kws)), "Diğer")
    return brand, cat


def num(txt: str) -> int:
    d = re.sub(r"[^\d]", "", txt or "")
    return int(d) if d else 0


async def main(slug: str, out: str, max_scroll: int):
    shop = f"https://www.shopier.com/{slug}"
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
        await pg.goto(shop, wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(3500)

        found, last = {}, -1
        for _ in range(max_scroll):
            for c in await pg.query_selector_all(f'a[href*="/{slug}/"]'):
                href = await c.get_attribute("href") or ""
                m = re.search(rf"/{slug}/(\d+)", href)
                if not m or m.group(1) in found:
                    continue
                pid = m.group(1)
                text = (await c.inner_text()) or ""
                img = await c.query_selector("img")
                src = (await img.get_attribute("src")) if img else None
                if not src or "TL" not in text:
                    continue
                if src.startswith("/"):
                    src = "https://cdn.shopier.app" + src
                vals = sorted(num(x) for x in re.findall(r"([\d.]+)\s*TL", text))
                if not vals or vals[0] <= 0:
                    continue
                title = next((l.strip() for l in text.split("\n") if len(l.strip()) > 8), pid)
                found[pid] = {"id": pid, "title": title[:140], "price": vals[0],
                              "old_price": vals[-1] if len(vals) > 1 else vals[0],
                              "image": src, "url": f"{shop}/{pid}"}
            await pg.mouse.wheel(0, 4500)
            await pg.wait_for_timeout(1300)
            if len(found) == last:
                break
            last = len(found)
        await br.close()

    data = []
    for v in found.values():
        v["brand"], v["category"] = classify(v["title"])
        data.append(v)
    data.sort(key=lambda x: int(x["id"]), reverse=True)
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(data)} ürün -> {out}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--slug", default="167brands")
    a.add_argument("--out", default="products.json")
    a.add_argument("--max-scroll", type=int, default=300)
    main_args = a.parse_args()
    asyncio.run(main(main_args.slug, main_args.out, main_args.max_scroll))
