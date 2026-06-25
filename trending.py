"""
GitHub Trending Scout — scrape trending repos & send to Discord
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import os
import json

WIB = timezone(timedelta(hours=7))

def scrape_trending(since="daily"):
    """Scrape GitHub Trending page."""
    url = f"https://github.com/trending?since={since}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html",
    }
    
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article.Box-row")
    
    repos = []
    for art in articles:
        h2 = art.select_one("h2 a")
        if not h2:
            continue
        
        name = h2.get_text(strip=True).replace("\n", "").replace(" ", "")
        href = "https://github.com" + h2["href"]
        
        desc_p = art.select_one("p")
        desc = desc_p.get_text(strip=True) if desc_p else ""
        
        lang_span = art.select_one("[itemprop='programmingLanguage']")
        lang = lang_span.get_text(strip=True) if lang_span else "N/A"
        
        # Stars total
        star_links = art.select("a.Link--muted")
        stars_total = star_links[0].get_text(strip=True) if star_links else "0"
        
        # Stars today/week
        span_today = art.select_one("span.d-inline-block.float-sm-right")
        stars_period = span_today.get_text(strip=True) if span_today else ""
        
        repos.append({
            "name": name,
            "url": href,
            "desc": desc[:150],
            "lang": lang,
            "stars": stars_total,
            "period_stars": stars_period,
        })
    
    return repos


def format_discord_message(daily, weekly):
    """Format trending data into Discord embed."""
    now = datetime.now(WIB)
    
    embeds = []
    
    # Daily embed
    daily_fields = []
    for i, r in enumerate(daily[:15], 1):
        value = f"⭐ {r['stars']} ({r['period_stars']})\n{r['desc'][:100]}"
        daily_fields.append({
            "name": f"{i}. [{r['name']}]({r['url']})",
            "value": value,
            "inline": False
        })
    
    embeds.append({
        "title": "🔥 GitHub Trending — Hari Ini",
        "color": 0xff6b35,
        "fields": daily_fields[:10],  # Discord limit 25 fields
        "footer": {"text": f"Generated {now.strftime('%d %b %Y %H:%M WIB')}"}
    })
    
    # Weekly embed
    weekly_fields = []
    for i, r in enumerate(weekly[:15], 1):
        value = f"⭐ {r['stars']} ({r['period_stars']})\n{r['desc'][:100]}"
        weekly_fields.append({
            "name": f"{i}. [{r['name']}]({r['url']})",
            "value": value,
            "inline": False
        })
    
    embeds.append({
        "title": "📈 GitHub Trending — Minggu Ini",
        "color": 0x4caf50,
        "fields": weekly_fields[:10],
        "footer": {"text": f"Generated {now.strftime('%d %b %Y %H:%M WIB')}"}
    })
    
    return {"embeds": embeds}


def send_discord(webhook_url, payload):
    """Send message to Discord via webhook."""
    resp = requests.post(
        webhook_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    resp.raise_for_status()
    print(f"✅ Discord message sent (status {resp.status_code})")
    return resp


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL not set")
        exit(1)
    
    print("📡 Scraping GitHub Trending...")
    
    try:
        daily = scrape_trending("daily")
        print(f"  Daily: {len(daily)} repos")
    except Exception as e:
        print(f"⚠️ Daily trending failed: {e}")
        daily = []
    
    try:
        weekly = scrape_trending("weekly")
        print(f"  Weekly: {len(weekly)} repos")
    except Exception as e:
        print(f"⚠️ Weekly trending failed: {e}")
        weekly = []
    
    if not daily and not weekly:
        print("❌ No data scraped")
        exit(1)
    
    payload = format_discord_message(daily, weekly)
    
    # Save JSON for reference
    with open("trending_output.json", "w", encoding="utf-8") as f:
        json.dump({"daily": daily, "weekly": weekly, "timestamp": datetime.now(WIB).isoformat()}, f, ensure_ascii=False, indent=2)
    
    print("📤 Sending to Discord...")
    send_discord(webhook_url, payload)
    print("✅ Done!")


if __name__ == "__main__":
    main()
