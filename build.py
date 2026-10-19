#!/usr/bin/env python3
"""開発者のトップページ「Saitoの個人開発アプリ」(index.html・en/index.html)を apps.json から作る。

アプリを足すときは apps.json に1件書き足して `python3 build.py` を実行する。
アプリは apps.json の順に、画面の枠と説明を左右交互に並べる。
各項目の書き方は apps.json の四季苔を見本にする(appStore・support・privacy・screenshot・tags・released は省略可)。
"""
import datetime as dt, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
X_ID = "saito_dev"  # Xのアカウント(@なし)
NEW_DAYS = 30  # 公開日("released")から何日間「NEW」を出すか
FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfMMRAh4BeQ_ZcTgsZDuV5MzYL22TjPRAj4yL7NFHdgxtLDCQ/viewform"
THEME = "#2c2a27"  # style.css の --paper と同じ色

TEXT = {
    "ja": dict(lang_link=("en/", "English"), title="Saitoの個人開発アプリ", heading="Saitoの<br>個人開発アプリ",
               lead="都内の会社で働く、エンジニアの端くれです。仕事のかたわら、個人で iPhone アプリを作っています。",
               nav_apps="アプリ", soon="近日公開", store="App Store で見る", support="サポート", privacy="プライバシー",
               contact_title="お問い合わせ", contact="ご質問・ご意見は、フォームからお気軽にどうぞ。", form="お問い合わせフォーム",
               new="NEW", screen="の画面", meta="Takeshi Saito が個人で開発している iPhone アプリの一覧です。"),
    "en": dict(lang_link=("../", "日本語"), title="Apps by Saito", heading="Apps<br>by Saito",
               lead="I'm a software engineer at a company in Tokyo, building iPhone apps on my own on the side.",
               nav_apps="Apps", soon="Coming soon", store="View on the App Store", support="Support", privacy="Privacy",
               contact_title="Contact", contact="Questions or feedback? Send a note through the form (Japanese form; English is welcome).",
               form="Contact form", new="NEW", screen=" screen", meta="iPhone apps made by independent developer Takeshi Saito."),
}

def e(s): return html.escape(s, quote=True)

def new_badge(a, t):
    if not a.get("released"):
        return ""
    until = dt.date.fromisoformat(a["released"]) + dt.timedelta(days=NEW_DAYS)
    if dt.date.today() >= until:  # ページを作った時点で期限切れなら出さない。期限は表示時にもJavaScriptで確かめる
        return ""
    return f'<span class="new" data-until="{until.isoformat()}">{t["new"]}</span>'

def app_section(a, lang, t, pre, index):
    name = e(a["name"][lang])
    if a.get("screenshot"):
        visual = f'<img class="phone" src="{pre}{a["screenshot"][lang]}" alt="{name}{t["screen"]}" loading="lazy">'
    else:
        visual = f'<img class="big-icon" src="{pre}{a["icon"]}" alt="">'
    tags = "".join(f"<span>{e(x)}</span>" for x in a.get("tags", {}).get(lang, []))
    links = []
    if a.get("appStore"):
        links.append(f'<a href="{a["appStore"][lang]}">{t["store"]}<span>↗</span></a>')
    else:
        links.append(f'<span class="soon">{t["soon"]}</span>')
    if a.get("support"):
        links.append(f'<a class="sub" href="{pre}{a["support"][lang]}">{t["support"]}</a>')
    if a.get("privacy"):
        links.append(f'<a class="sub" href="{pre}{a["privacy"][lang]}">{t["privacy"]}</a>')
    return f'''
    <article class="app reveal">
      <div class="shot">
        <span class="num mincho">{index:02d}</span>
        {visual}
      </div>
      <div class="text">
        <p class="kind">{e(a["category"][lang])}{new_badge(a, t)}</p>
        <h2 class="mincho"><img src="{pre}{a["icon"]}" alt="">{name}</h2>
        <p class="sub">{e(a["subtitle"][lang])}</p>
        <p class="desc">{e(a["description"][lang])}</p>
        {f'<p class="tags">{tags}</p>' if tags else ''}
        <div class="links">{"".join(links)}</div>
      </div>
    </article>'''

SCRIPT = """<script>
(() => {
  // NEW の印：期限を過ぎていたら消す
  const today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('[data-until]').forEach(n => { if (today >= n.dataset.until) n.remove(); });

  // 見出しを一文字ずつに分け、墨がにじむように出す
  const h1 = document.querySelector('.hero h1');
  let i = 0;
  [...h1.childNodes].forEach(n => {
    if (n.nodeType !== 3) return;
    const frag = document.createDocumentFragment();
    [...n.textContent].forEach(c => {
      const sp = document.createElement('span');
      sp.className = 'ch'; sp.textContent = c; sp.style.setProperty('--i', i++);
      frag.append(sp);
    });
    n.replaceWith(frag);
  });
  h1.style.setProperty('--n', i);

  // 各段がスクロールでふわっと出る
  const els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { threshold: .12 });
    els.forEach(el => io.observe(el));
  } else {
    els.forEach(el => el.classList.add('in'));
  }

  // 枠の上をカーソルの光がなでる
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.shot').forEach(el => el.addEventListener('pointermove', ev => {
    const r = el.getBoundingClientRect();
    el.style.setProperty('--mx', (ev.clientX - r.left) + 'px');
    el.style.setProperty('--my', (ev.clientY - r.top) + 'px');
  }));
})();
</script>"""

def page(lang, apps):
    t = TEXT[lang]; pre = "" if lang == "ja" else "../"
    sections = "".join(app_section(a, lang, t, pre, i + 1) for i, a in enumerate(apps))
    href, label = t["lang_link"]
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["title"]}</title>
<meta name="description" content="{t["meta"]}">
<meta name="theme-color" content="{THEME}">
<link rel="icon" href="{pre}images/avatar.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}style.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<div class="wrap">
  <header>
    <a class="me" href="{pre or './'}"><img src="{pre}images/avatar.png" alt=""><span>Saito</span></a>
    <nav>
      <a href="#apps">{t["nav_apps"]}</a>
      <a href="#contact" class="hide-sp">{t["contact_title"]}</a>
      <a href="https://x.com/{X_ID}">X</a>
      <a href="{href}">{label}</a>
    </nav>
  </header>

  <section class="hero">
    <p class="eyebrow">SAITO — INDIE iPHONE APPS</p>
    <h1 class="mincho">{t["heading"]}<em>.</em></h1>
    <p>{t["lead"]}</p>
  </section>

  <main id="apps">{sections}
  </main>

  <section class="contact reveal" id="contact">
    <div>
      <h2 class="mincho">{t["contact_title"]}</h2>
      <p>{t["contact"]}</p>
    </div>
    <div class="links"><a href="{FORM}">{t["form"]}<span>↗</span></a></div>
  </section>

  <footer>
    <span class="mincho">{t["title"]}</span>
    <span>© 2026 Takeshi Saito</span>
  </footer>
</div>
{SCRIPT}
</body>
</html>
'''

def main():
    apps = json.loads((ROOT / "apps.json").read_text())
    out = {"ja": ROOT / "index.html", "en": ROOT / "en/index.html"}
    for lang, path in out.items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(page(lang, apps))

if __name__ == "__main__":
    main()
