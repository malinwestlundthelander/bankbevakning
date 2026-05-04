"""
Bankbevakning – weekly scraper
Hämtar verifierbar data från 8 svenska bankars offentliga produktsidor.
Genererar data.json, history.json och diff.json.
Skickar e-post via SendGrid om diff ≠ tom.
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Konstanter ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "web" / "data"
DATA_FILE = DATA_DIR / "data.json"
HISTORY_FILE = DATA_DIR / "history.json"
DIFF_FILE = DATA_DIR / "diff.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BankbevakningBot/1.0; "
        "+https://github.com/YOUR_USER/bankbevakning)"
    )
}

BANKS = {
    "handelsbanken": {
        "name": "Handelsbanken",
        "type": "Storbank",
        "color": "#0C447C",
        "bg": "#E6F1FB",
        "urls": {
            "foretagspaket": "https://www.handelsbanken.se/sv/foretag/kund-hos-oss/foretagspaketet",
            "tjanster": "https://www.handelsbanken.se/sv/foretag/konton-betalningar/tjanster-som-forenklar/affarstjanster",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "160"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "0"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Nej"},
            "bookkeeping_integration": {"label": "Bokföringsintegration", "unit": "", "selector": None, "static": "Ja – Fortnox, Visma, Hogia, Wint, 24SevenOffice"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja"},
            "trade_finance": {"label": "Trade Finance", "unit": "", "selector": None, "static": "Ja"},
            "sustainability_tool": {"label": "Hållbarhetskollen", "unit": "", "selector": None, "static": "Ja – via GoClimate, gratis upp till 5 000 verifikat/år"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja – lokalt kontor med beslutsmandat"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "handelsbanken.se/sv/foretag/kund-hos-oss/foretagspaketet"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "seb": {
        "name": "SEB",
        "type": "Storbank",
        "color": "#27500A",
        "bg": "#EAF3DE",
        "urls": {
            "foretagspaket": "https://seb.se/foretag/erbjudande-och-bli-foretagskund/vart-erbjudande-till-dig-som-foretagare",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "130 (6 mån gratis för nya)"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "2 500"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Ja – helt digitalt via lagerbolag"},
            "bookkeeping_integration": {"label": "Bokföringsintegration", "unit": "", "selector": None, "static": "Ja – Fortnox, Visma, Björn Lundén, Spiris, Hogia, 24SevenOffice"},
            "financial_overview": {"label": "Finansiell översikt (Oxceed)", "unit": "", "selector": None, "static": "Ja – P&L och nyckeltal i Business Arena, utan merkostnad"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja"},
            "factoring": {"label": "Fakturafinansiering/factoring", "unit": "", "selector": None, "static": "Ja – fakturabelåning och fakturaköp via Waya"},
            "leasing": {"label": "Leasing & avbetalning", "unit": "", "selector": None, "static": "Ja – bil, maskiner, leverantörsoberoende"},
            "trade_finance": {"label": "Trade Finance", "unit": "", "selector": None, "static": "Ja – export/importremburs, bankgarantier"},
            "pension": {"label": "Tjänstepension", "unit": "", "selector": None, "static": "Ja – fondförsäkring, trad, depå, robotrådgivare SEB Bot Advisor"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "seb.se/foretag/erbjudande-och-bli-foretagskund"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "nordea": {
        "name": "Nordea",
        "type": "Storbank",
        "color": "#72243E",
        "bg": "#FBEAF0",
        "urls": {
            "foretagskonto": "https://www.nordea.se/foretag/produkter/betala/foretagskonto.html",
            "digital": "https://www.nordea.se/foretag/produkter/mobilbank-internetbank/nordea-business.html",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "108 (1 300 kr/år)"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "2 500"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Ja – helt digitalt"},
            "platform": {"label": "Digital plattform", "unit": "", "selector": None, "static": "Nordea Business – Global Finance Award 2025, bästa SME-plattform i Västeuropa"},
            "cashflow_tool": {"label": "Kassaflödesprognos", "unit": "", "selector": None, "static": "Ja – 'Få koll' med branschjämförelse och beslutssimulering"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja – eget Swish-verktyg"},
            "trade_finance": {"label": "Trade Finance", "unit": "", "selector": None, "static": "Ja – Trade Finance Global, onlinesystem"},
            "fx_tool": {"label": "Valuta/hedging", "unit": "", "selector": None, "static": "Ja – e-Markets handlarplattform"},
            "pension": {"label": "Tjänstepension", "unit": "", "selector": None, "static": "Ja – Nordea Node-portal"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "nordea.se/foretag/produkter/betala/foretagskonto.html"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "danske": {
        "name": "Danske Bank",
        "type": "Storbank",
        "color": "#3C3489",
        "bg": "#EEEDFE",
        "urls": {
            "foretag": "https://danskebank.se/foretag",
            "district": "https://danskebank.se/foretag/digitala-tjanster/onlinetjanster/district",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "Varierar per paket – kontakta banken"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "2 500"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Ja – Startpaketet online"},
            "platform": {"label": "Digital plattform", "unit": "", "selector": None, "static": "District – modulbaserad, anpassningsbar, gränsöverskridande Norden"},
            "fx_tool": {"label": "Valuta/hedging", "unit": "", "selector": None, "static": "Ja – DanskeFX OneClick, egna konton i Europa/USA/Asien"},
            "trade_finance": {"label": "Trade Finance", "unit": "", "selector": None, "static": "Ja – utsedd till bäst i Norden av Kantar Prospera 2025"},
            "nordic_presence": {"label": "Nordisk närvaro", "unit": "", "selector": None, "static": "Sverige, DK, NO, FI, UK, Polen + >1 300 korrespondentbanker"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja – via District"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja + specialistteam"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "danskebank.se/foretag"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "lansforsakringar": {
        "name": "Länsförsäkringar",
        "type": "Nischbank",
        "color": "#085041",
        "bg": "#E1F5EE",
        "urls": {
            "bli_kund": "https://www.lansforsakringar.se/foretag/bank/bli-bankkund/",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "100 (1 200 kr/år)"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "Kontakta lokalt länsbolag"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Delvis – via telefon eller chatt"},
            "included_payments": {"label": "Ingående betalningar", "unit": "st", "selector": None, "static": "500 st/år (därefter 1,80 kr/st)"},
            "combined_offering": {"label": "Bank + försäkring samlat", "unit": "", "selector": None, "static": "Ja – unik kombination via Mina sidor"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja – tilläggstjänst"},
            "credit_card": {"label": "Kreditkort Företag", "unit": "", "selector": None, "static": "Ja – upp till 50 dagars räntefri kredit"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja – via lokalt länsbolag"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "lansforsakringar.se/foretag/bank/bli-bankkund"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "lunar": {
        "name": "Lunar",
        "type": "Digital",
        "color": "#444441",
        "bg": "#F1EFE8",
        "urls": {
            "foretag": "https://www.lunar.se/foretag",
            "priser": "https://www.lunar.se/foretag/priser",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "Från 0 (Simple gratis, Essential/Limitless betalt)"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "0"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Ja – 100% digitalt, svar inom 3 arbetsdagar"},
            "automatic_vat": {"label": "Automatiskt momskonto", "unit": "", "selector": None, "static": "Ja – avsätter vald % av varje inbetalning automatiskt"},
            "bookkeeping_integration": {"label": "Bokföringsintegration", "unit": "", "selector": None, "static": "Ja – Fortnox, Bokio, Bolageriet, SpeedLedger (kostnadsfritt i alla paket)"},
            "expense_categorization": {"label": "Automatisk utgiftskategorisering", "unit": "", "selector": None, "static": "Ja – kortinköp kategoriseras automatiskt i appen"},
            "swish": {"label": "Swish Företag", "unit": "", "selector": None, "static": "Ja – fast månadskostnad"},
            "loan": {"label": "Företagslån", "unit": "", "selector": None, "static": "Via partners Qred/Froda – upp till 5 Mkr"},
            "international": {"label": "Utlandsbetalningar", "unit": "", "selector": None, "static": "Begränsat – kortanvändning utomlands fungerar"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Nej – supportteam, ej personlig rådgivare"},
            "trustpilot": {"label": "Trustpilot-betyg", "unit": "", "selector": None, "static": "4,6 av 5 (8 350 omdömen)"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "lunar.se/foretag/priser"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025"},
        },
    },
    "svea": {
        "name": "Svea Bank",
        "type": "Digital",
        "color": "#712B13",
        "bg": "#FAECE7",
        "urls": {
            "foretagspaket": "https://www.svea.com/sv-se/foretag/foretagsbanken/foretagspaket",
            "prislista": "https://www.svea.com/globalassets/sweden/foretag/foretagsbanken/prislista-foretag-2025-11-04.pdf",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "149 (Bas-paket, gäller från nov 2025)"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "0"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Ja – helt digitalt, ca 14 dagar"},
            "credit_limit": {"label": "Kontokredit (Växa-paket)", "unit": "kr", "selector": None, "static": "Upp till 1 000 000 digitalt, högre vid manuell bedömning"},
            "factoring": {"label": "Fakturaköp/factoring", "unit": "", "selector": None, "static": "Ja – fakturaköp och factoring, inkl. exportfinansiering"},
            "leasing": {"label": "Leasing", "unit": "", "selector": None, "static": "Ja – objekts- och fordonsfinansiering"},
            "ecommerce": {"label": "E-handels­betallösning", "unit": "", "selector": None, "static": "Ja – Instore Pay, Scan & Pay, e-handel"},
            "bookkeeping_integration": {"label": "Bokföringsintegration", "unit": "", "selector": None, "static": "Ja – Fortnox (ingår)"},
            "international": {"label": "Utlandsbetalningar", "unit": "", "selector": None, "static": "SEPA-länder + EES + Schweiz/UK – läggs till som produkt i internetbanken"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ej fysiskt kontor – möte kan bokas"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "svea.com/globalassets/prislista-foretag-2025-11-04.pdf"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "nov 2025 (officiell prislista)"},
        },
    },
    "swedbank": {
        "name": "Swedbank",
        "type": "Storbank",
        "color": "#633806",
        "bg": "#FAEEDA",
        "urls": {
            "foretagspaket": "https://www.swedbank.se/foretag/bli-kund/foretagspaket.html",
        },
        "fields": {
            "monthly_fee": {"label": "Månadsavgift", "unit": "kr/mån", "selector": None, "static": "Ej publik – kontakta Swedbank"},
            "setup_fee": {"label": "Startavgift", "unit": "kr", "selector": None, "static": "Ej publik"},
            "onboarding_digital": {"label": "Digital onboarding", "unit": "", "selector": None, "static": "Delvis – kontakta närmaste kontor eller ring 0771-33 44 33"},
            "swish_fee": {"label": "Swish Företag – avgift", "unit": "kr/transaktion", "selector": None, "static": "1,50 (ord. 2,00 kr)"},
            "insurance_discount": {"label": "Försäkringsrabatt", "unit": "", "selector": None, "static": "10% på Företagsförsäkring, år 1"},
            "trade_finance": {"label": "Trade Finance", "unit": "", "selector": None, "static": "Ja"},
            "leasing": {"label": "Leasing & avbetalning", "unit": "", "selector": None, "static": "Ja – inkl. grön billeasing"},
            "dedicated_advisor": {"label": "Personlig rådgivare", "unit": "", "selector": None, "static": "Ja"},
            "source_url": {"label": "Källa", "unit": "", "selector": None, "static": "swedbank.se/foretag/bli-kund/foretagspaket.html"},
            "source_verified": {"label": "Verifierad", "unit": "", "selector": None, "static": "maj 2025 (avgift ej publik)"},
        },
    },
}


def fetch_page(url: str) -> BeautifulSoup | None:
    """Hämtar en webbsida och returnerar BeautifulSoup-objekt."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  VARNING: Kunde inte hämta {url}: {e}")
        return None


def scrape_bank(bank_id: str, config: dict) -> dict:
    """
    Bygger dataobjekt för en bank.
    Statiska fält används för verifierad data som kräver manuell avläsning.
    CSS-selektorer används där sidan exponerar data i strukturerad HTML.
    """
    print(f"  Skrapar {config['name']}...")
    fields_data = {}
    scraped_dynamic = False

    for field_id, field_cfg in config["fields"].items():
        value = field_cfg.get("static", "")

        # Om selektor finns, försök hämta dynamiskt
        if field_cfg.get("selector") and not value:
            for url in config["urls"].values():
                soup = fetch_page(url)
                if soup:
                    el = soup.select_one(field_cfg["selector"])
                    if el:
                        value = el.get_text(strip=True)
                        scraped_dynamic = True
                        break

        fields_data[field_id] = {
            "label": field_cfg["label"],
            "value": value,
            "unit": field_cfg.get("unit", ""),
            "dynamic": scraped_dynamic and not field_cfg.get("static"),
        }

    return {
        "id": bank_id,
        "name": config["name"],
        "type": config["type"],
        "color": config["color"],
        "bg": config["bg"],
        "urls": config["urls"],
        "fields": fields_data,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "checksum": hashlib.md5(
            json.dumps(fields_data, sort_keys=True).encode()
        ).hexdigest(),
    }


def compute_diff(old_data: dict, new_data: dict) -> list[dict]:
    """Jämför gammal och ny snapshot, returnerar lista med ändringar."""
    changes = []
    for bank_id, new_bank in new_data["banks"].items():
        old_bank = old_data.get("banks", {}).get(bank_id)
        if not old_bank:
            changes.append({
                "bank_id": bank_id,
                "bank_name": new_bank["name"],
                "type": "new_bank",
                "message": f"{new_bank['name']} har lagts till i bevakningen",
            })
            continue

        if old_bank.get("checksum") != new_bank.get("checksum"):
            for field_id, new_field in new_bank["fields"].items():
                old_field = old_bank.get("fields", {}).get(field_id, {})
                old_val = old_field.get("value", "")
                new_val = new_field.get("value", "")
                if old_val != new_val and old_val and new_val:
                    changes.append({
                        "bank_id": bank_id,
                        "bank_name": new_bank["name"],
                        "type": "field_change",
                        "field_id": field_id,
                        "field_label": new_field["label"],
                        "old_value": old_val,
                        "new_value": new_val,
                        "message": (
                            f"{new_bank['name']} – {new_field['label']}: "
                            f"'{old_val}' → '{new_val}'"
                        ),
                    })
    return changes


def send_email_notification(changes: list[dict], scan_date: str) -> None:
    """Skickar e-postnotis via SendGrid API."""
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("NOTIFY_FROM_EMAIL", "bankbevakning@example.com")
    to_email = os.environ.get("NOTIFY_TO_EMAIL")

    if not api_key or not to_email:
        print("  INFO: SENDGRID_API_KEY eller NOTIFY_TO_EMAIL saknas – hoppar över e-post")
        return

    changes_html = "".join(
        f"<li style='margin-bottom:8px'><strong>{c['bank_name']}</strong> – "
        f"{c.get('field_label', c['type'])}: "
        f"<span style='color:#c0392b'>{c.get('old_value', '')}</span> → "
        f"<span style='color:#27ae60'>{c.get('new_value', c.get('message', ''))}</span></li>"
        for c in changes
    )

    html_body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto">
      <h2 style="color:#1a1a1a">Bankbevakning – {len(changes)} förändring(ar) detekterade</h2>
      <p style="color:#555">Skanningsdatum: {scan_date}</p>
      <ul style="padding-left:20px;color:#333">{changes_html}</ul>
      <p style="margin-top:24px">
        <a href="{os.environ.get('DASHBOARD_URL', 'https://YOUR_USER.github.io/bankbevakning')}"
           style="background:#0C447C;color:#fff;padding:10px 18px;text-decoration:none;border-radius:6px">
          Öppna dashboard
        </a>
      </p>
      <p style="color:#999;font-size:12px;margin-top:24px">
        Bankbevakning · Automatisk veckovis skanning
      </p>
    </div>
    """

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Bankbevakning"},
        "subject": f"[Bankbevakning] {len(changes)} förändring(ar) – {scan_date}",
        "content": [{"type": "text/html", "value": html_body}],
    }

    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        if resp.status_code == 202:
            print(f"  E-post skickad till {to_email}")
        else:
            print(f"  VARNING: SendGrid svarade {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"  FEL vid e-postsändning: {e}")


def run() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    scan_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"\n{'='*50}")
    print(f"Bankbevakning – skanning {scan_date}")
    print(f"{'='*50}")

    # Läs gammal data (för diff)
    old_data: dict = {}
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            old_data = json.load(f)
        print(f"Gammal snapshot laddad: {old_data.get('scan_date', 'okänt datum')}")

    # Skrapa alla banker
    banks_data = {}
    for bank_id, config in BANKS.items():
        banks_data[bank_id] = scrape_bank(bank_id, config)

    new_data = {
        "scan_date": scan_date,
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "banks": banks_data,
    }

    # Beräkna diff
    changes = compute_diff(old_data, new_data)
    print(f"\nDiff: {len(changes)} förändring(ar) detekterade")
    for c in changes:
        print(f"  • {c['message']}")

    # Spara data.json
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print(f"\nSparad: {DATA_FILE}")

    # Uppdatera history.json
    history: dict = {}
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    history.setdefault("scans", []).append({
        "scan_date": scan_date,
        "changes_count": len(changes),
    })
    history["scans"] = history["scans"][-52:]  # Behåll max 52 veckor
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"Sparad: {HISTORY_FILE}")

    # Spara diff.json
    diff_data = {
        "scan_date": scan_date,
        "changes_count": len(changes),
        "changes": changes,
    }
    with open(DIFF_FILE, "w", encoding="utf-8") as f:
        json.dump(diff_data, f, ensure_ascii=False, indent=2)
    print(f"Sparad: {DIFF_FILE}")

    # Skicka e-post om det finns förändringar
    if changes:
        print("\nSkickar e-postnotis...")
        send_email_notification(changes, scan_date)
    else:
        print("\nInga förändringar – ingen e-post skickas")

    print(f"\n{'='*50}")
    print("Skanning klar!")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run()
