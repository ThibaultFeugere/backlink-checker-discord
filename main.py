import requests
import os
import csv
import io
from bs4 import BeautifulSoup
from discord import SyncWebhook

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SHEET_ID = os.getenv("SHEET_ID")

if not DISCORD_WEBHOOK_URL:
    raise ValueError("La variable d'environnement DISCORD_WEBHOOK_URL n'est pas définie.")
if not SHEET_ID:
    raise ValueError("La variable d'environnement SHEET_ID n'est pas définie.")

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

def fetch_google_sheet(sheet_id):
    """Fetch backlinks data from a public Google Sheet in CSV format."""
    try:
        response = requests.get(GOOGLE_SHEET_CSV_URL.format(sheet_id=sheet_id), timeout=10)
        response.raise_for_status()
        csv_data = response.text.splitlines()
        reader = csv.DictReader(io.StringIO(csv_data))
        return list(reader)
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des données de Google Sheet: {e}")
        return []

def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de {url}: {e}")
        return None

def find_backlink(html_content, target_site, anchor_text):
    if not html_content:
        return False, False, False

    soup = BeautifulSoup(html_content, 'html.parser')
    backlinks = soup.find_all('a', href=True)

    for link in backlinks:
        if target_site in link['href']:
            is_nofollow = 'nofollow' in link.get('rel', [])
            if anchor_text in link.get_text():
                return True, True, is_nofollow
            return True, False, is_nofollow

    return False, False, False

def track_backlinks(backlinks):
    webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
    webhook.send(f":hourglass: Vérification des backlinks en cours █▒▒▒▒▒▒▒▒▒ (10%)")
    for backlink in backlinks:
        url = backlink.get('url')
        target_site = backlink.get('target_site')
        anchor_text = backlink.get('anchor_text')

        print(f"Analyse de {url} pour {target_site} avec l'ancre '{anchor_text}'...")
        html_content = fetch_page_content(url)
        backlink_found, anchor_found, is_nofollow = find_backlink(html_content, target_site, anchor_text)

        if not backlink_found:
            webhook.send(f"- Backlink invalide sur {url}. L'URL {target_site} n'est pas trouvée sur l'ancre {anchor_text}.")
        elif not anchor_found:
            webhook.send(f"- Backlink invalide sur {url}. L'URL {target_site} est trouvée mais pas l'ancre {anchor_text}.")
        elif is_nofollow:
            webhook.send(f"- Backlink invalide sur {url}. Le lien {target_site} sur l'ancre **{anchor_text}** est en **nofollow**.")
    webhook.send(f":white_check_mark: Vérification des backlinks terminée ██████████ (100%)")

if __name__ == "__main__":
    backlinks = fetch_google_sheet(SHEET_ID)

    if backlinks:
        track_backlinks(backlinks)
    else:
        print("Aucune donnée récupérée depuis Google Sheet.")
