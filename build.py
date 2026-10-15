#!/usr/bin/env python3
"""開発者のトップページ「Saitoの個人開発アプリ」(index.html・en/index.html)を apps.json から作る。

アプリを足すときは apps.json に1件書き足して `python3 build.py` を実行する。
「アプリ一覧」には全アプリを並べ、「ピックアップ」(大きなカード)は "pickup": true(省略時true)のアプリから開くたびにランダムで1つ出す。
各項目の書き方は apps.json の四季苔を見本にする(appStore・support・privacy・screenshot・tags は省略可)。
"""
import datetime as dt, html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
X_ID = "saito_dev"  # Xのアカウント(@なし)
NEW_DAYS = 30  # 公開日("released")から何日間「NEW」を出すか
FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfMMRAh4BeQ_ZcTgsZDuV5MzYL22TjPRAj4yL7NFHdgxtLDCQ/viewform"
APPLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.6c.02 2.43 2.13 3.24 2.15 3.25-.02.06-.34 1.15-1.11 2.28-.67.98-1.36 1.95-2.45 1.97-1.07.02-1.41-.63-2.64-.63-1.22 0-1.6.61-2.62.65-1.05.04-1.85-1.06-2.52-2.04-1.37-1.99-2.42-5.62-1.01-8.07.7-1.22 1.95-1.99 3.31-2.01 1.03-.02 2.01.7 2.64.7.63 0 1.81-.86 3.05-.73.52.02 1.98.21 2.92 1.59-.08.05-1.74 1.02-1.72 3.04zM14.37 4.65c.56-.68.93-1.62.83-2.56-.8.03-1.77.53-2.35 1.21-.52.6-.97 1.56-.85 2.48.9.07 1.81-.46 2.37-1.13z"/></svg>'
XLOGO = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'

TEXT = {
    "ja": dict(lang_link=("en/", "English"), tagline="Saitoの個人開発アプリ",
               lead="都内の会社で働く、エンジニアの端くれです。仕事のかたわら、個人で iPhone アプリを作っています。",
               featured="ピックアップ", all="アプリ一覧", soon="近日公開", store="App Store で見る", support="サポート", privacy="プライバシー",
               contact="ご質問・ご意見は、フォームからお気軽にどうぞ。", form="お問い合わせ", new="NEW",
               meta="Takeshi Saito が個人で開発している iPhone アプリの一覧です。"),
    "en": dict(lang_link=("../", "日本語"), tagline="Apps by Saito",
               lead="I'm a software engineer at a company in Tokyo, building iPhone apps on my own on the side.",
               featured="Pick up", all="All apps", soon="Coming soon", store="View on the App Store", support="Support", privacy="Privacy",
               contact="Questions or feedback? Send a note through the form (Japanese form; English is welcome).", form="Contact", new="NEW",
               meta="iPhone apps made by independent developer Takeshi Saito."),
}

def e(s): return html.escape(s, quote=True)

def pickup_card(a, lang, t, pre, index):
    tags = "".join(f"<li>{e(x)}</li>" for x in a.get("tags", {}).get(lang, []))
    links = []
    if a.get("appStore"):
        links.append(f'<a class="btn btn-blue" href="{a["appStore"][lang]}">{APPLE}{t["store"]}</a>')
    else:
        links.append(f'<span class="btn btn-soon">{t["soon"]}</span>')
    if a.get("support"):
        links.append(f'<a class="btn btn-line" href="{pre}{a["support"][lang]}">{t["support"]}</a>')
    if a.get("privacy"):
        links.append(f'<a class="btn btn-line" href="{pre}{a["privacy"][lang]}">{t["privacy"]}</a>')
    shot = (f'<div class="phone"><img src="{pre}{a["screenshot"][lang]}" alt="{e(a["name"][lang])}" loading="lazy"></div>'
            if a.get("screenshot") else "")
    hidden = "" if index == 0 else " hidden"
    return f'''
  <article class="feature{'' if shot else ' no-shot'}" data-pickup{hidden}>
    <div class="feature-body">
      <div class="app-head">
        <img src="{pre}{a["icon"]}" alt="">
        <div><h2>{e(a["name"][lang])}</h2><p class="kind">{e(a["subtitle"][lang])} ・ {e(a["category"][lang])}</p></div>
      </div>
      <p class="desc">{e(a["description"][lang])}</p>
      <ul class="tags">{tags}</ul>
      <div class="links">{"".join(links)}</div>
    </div>
    {shot}
  </article>'''

def list_card(a, lang, t, pre):
    href = a["appStore"][lang] if a.get("appStore") else (pre + a["support"][lang] if a.get("support") else "#")
    new = ""
    if a.get("released"):
        until = dt.date.fromisoformat(a["released"]) + dt.timedelta(days=NEW_DAYS)
        if dt.date.today() < until:  # ページを作った時点で期限切れなら出さない。期限は表示時にもJavaScriptで確かめる
            new = f'<span class="new" data-until="{until.isoformat()}">{t["new"]}</span>'
    return f'''
    <a class="mini" href="{href}"><img class="ic" src="{pre}{a["icon"]}" alt="">
      <div><h3>{e(a["name"][lang])}{new}</h3>
      <p>{e(a["short"][lang])}</p><span class="meta">{e(a["category"][lang])}</span></div></a>'''

# ピックアップは "pickup": true のアプリから、開くたびにランダムで1つ表示する(JavaScriptが無い環境では最初の1つ)
PICK_SCRIPT = """<script>
(function () {
  var cards = document.querySelectorAll('[data-pickup]');
  if (cards.length >= 2) {
  var pick = Math.floor(Math.random() * cards.length);
  cards.forEach(function (c, i) { c.hidden = i !== pick; });
  }
})();
(function () {
  var today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('[data-until]').forEach(function (n) { if (today >= n.dataset.until) n.remove(); });
})();
</script>"""

def page(lang, apps):
    t = TEXT[lang]; pre = "" if lang == "ja" else "../"
    pickups = [a for a in apps if a.get("pickup", True)]
    feat = f'\n  <p class="label">{t["featured"]}</p>' + "".join(pickup_card(a, lang, t, pre, i) for i, a in enumerate(pickups))
    grid = f'\n  <p class="label">{t["all"]}</p>\n  <div class="grid">' + "".join(list_card(a, lang, t, pre) for a in apps) + "\n  </div>"
    href, label = t["lang_link"]
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["tagline"]}</title>
<meta name="description" content="{t["meta"]}">
<meta name="theme-color" content="#2563eb">
<link rel="icon" href="{pre}images/avatar.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Space+Grotesk:wght@600;700&family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}style.css">
</head>
<body>
<div class="wrap">
<header class="head">
  <a class="me" href="{pre or './'}"><img src="{pre}images/avatar.png" alt=""><span><strong>{t["tagline"]}</strong></span></a>
  <div class="head-links">
    <a class="pill" href="https://x.com/{X_ID}" aria-label="X">{XLOGO}<span>@{X_ID}</span></a>
    <a class="pill" href="{href}">{label}</a>
  </div>
</header>
<p class="lead">{t["lead"]}</p>
<main>{feat}{grid}
  <div class="contact"><p>{t["contact"]}</p><a class="btn btn-line" href="{FORM}">{t["form"]}</a></div>
</main>
<footer>© 2026 Takeshi Saito</footer>
</div>
{PICK_SCRIPT}
</body>
</html>
'''

def main():
    apps = json.loads((ROOT / "apps.json").read_text())
    out = {"ja": ROOT / "index.html", "en": ROOT / "en/index.html"}
    for lang, path in out.items():
        if path: path.parent.mkdir(exist_ok=True); path.write_text(page(lang, apps))

if __name__ == "__main__":
    main()
