const SHOP = "https://www.shopier.com/167brands";
const PAGE = 24;
let ALL = [], shown = PAGE;
let state = { brand: "", cat: "", sort: "new" };

const money = n => n.toLocaleString("tr-TR") + " TL";
const el = id => document.getElementById(id);

function card(p) {
  const d = p.old_price > p.price ? Math.round((1 - p.price / p.old_price) * 100) : 0;
  return `<a class="p" href="${p.url}" target="_blank" rel="noopener">
    <div class="pim"><img loading="lazy" src="${p.image}" alt="${p.title}">${d ? `<span class="dsc">%${d}</span>` : ""}</div>
    <div class="pb"><div class="pbr">${p.brand}</div><h3>${p.title}</h3>
    <div class="pr"><b>${money(p.price)}</b>${d ? `<s>${money(p.old_price)}</s>` : ""}</div>
    <div class="pa">Shopier'de Gör →</div></div></a>`;
}

function apply() {
  let list = ALL.filter(p =>
    (!state.brand || p.brand === state.brand) &&
    (!state.cat || p.category === state.cat));
  if (state.sort === "asc") list.sort((a, b) => a.price - b.price);
  else if (state.sort === "desc") list.sort((a, b) => b.price - a.price);
  else list.sort((a, b) => b.id - a.id);
  return list;
}

function render() {
  const grid = el("grid");
  if (!grid) return;
  const list = apply();
  el("count").textContent = list.length + " ürün";
  grid.innerHTML = list.length
    ? list.slice(0, shown).map(card).join("")
    : `<div class="empty">Bu filtrede ürün yok. Filtreyi temizlemeyi dene.</div>`;
  el("more").hidden = list.length <= shown;
  el("title").textContent = state.brand || state.cat
    ? [state.brand, state.cat].filter(Boolean).join(" · ")
    : "Tüm ürünler";
}

function buildFilters() {
  const chips = el("brands"), sel = el("cat");
  if (!chips || !sel) return;
  const brands = [...new Set(ALL.map(p => p.brand))].filter(b => b && b !== "Diğer").sort();
  chips.innerHTML = `<span class="chip on" data-b="">Tümü</span>` +
    brands.map(b => `<span class="chip" data-b="${b}">${b}</span>`).join("");
  chips.onclick = e => {
    const t = e.target.closest(".chip");
    if (!t) return;
    chips.querySelectorAll(".chip").forEach(c => c.classList.remove("on"));
    t.classList.add("on");
    state.brand = t.dataset.b;
    shown = PAGE;
    render();
  };
  [...new Set(ALL.map(p => p.category))].filter(Boolean).sort().forEach(c => {
    sel.insertAdjacentHTML("beforeend", `<option value="${c}">${c}</option>`);
  });
  sel.onchange = () => { state.cat = sel.value; shown = PAGE; render(); };
  el("sort").onchange = e => { state.sort = e.target.value; render(); };
  el("more").onclick = () => { shown += PAGE; render(); };
}

async function boot() {
  try {
    ALL = await (await fetch("products.json")).json();
  } catch {
    document.querySelectorAll(".pg").forEach(g =>
      g.innerHTML = `<div class="empty">products.json bulunamadı. Önce <code>python scrape.py</code> çalıştır.</div>`);
    return;
  }
  ALL = ALL.filter(p => p.price > 0);

  const q = new URLSearchParams(location.search);
  state.brand = q.get("marka") || "";
  state.cat = q.get("kategori") || "";

  if (el("cnt")) el("cnt").textContent = ALL.length + " Ürün · " +
    new Set(ALL.map(p => p.category)).size + " Kategori · " +
    new Set(ALL.map(p => p.brand)).size + " Marka";

  if (el("rail")) {
    const brands = [...new Set(ALL.map(p => p.brand))].filter(b => b !== "Diğer").slice(0, 10);
    el("rail").innerHTML = brands.flatMap(b => [`<span>${b.toUpperCase()}</span>`, "<span>✦</span>"]).join("").repeat(2);
  }

  if (el("cats")) {
    const counts = {};
    ALL.forEach(p => counts[p.category] = (counts[p.category] || 0) + 1);
    el("cats").innerHTML = Object.entries(counts).slice(0, 8)
      .map(([c, n]) => `<a class="c" href="katalog.html?kategori=${encodeURIComponent(c)}"><div class="cn">Kategori</div><h3>${c}</h3><span>${n} ürün</span></a>`).join("");
  }

  if (el("feat")) el("feat").innerHTML = ALL.slice(0, 6).map(card).join("");

  buildFilters();
  render();
}

boot();
