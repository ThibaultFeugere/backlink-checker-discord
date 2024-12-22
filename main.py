import requests
from bs4 import BeautifulSoup
from discord import SyncWebhook

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1320442445443371118/eNKhd3hoK4zhIbQ8s6VQz9ba8h6NefB5hj9svOnRHYU0WJHXba7ha24807CQneKKDcPF"

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
        return False, False

    soup = BeautifulSoup(html_content, 'html.parser')
    backlinks = soup.find_all('a', href=True)

    for link in backlinks:
        if target_site in link['href']:
            is_nofollow = 'nofollow' in link.get('rel', [])
            if anchor_text in link.get_text():
                return True, True, is_nofollow
            return True, False, is_nofollow

    return False, False

def track_backlinks(backlinks_data):
    webhook = SyncWebhook.from_url(DISCORD_WEBHOOK_URL)
    webhook.send(f":hourglass: Vérification des backlinks en cours █▒▒▒▒▒▒▒▒▒ (10%)")
    for backlink in backlinks_data:
        url = backlink['url']
        target_site = backlink['target_site']
        anchor_text = backlink['anchor_text']

        print(f"Analyse de {url} pour {target_site} avec l'ancre '{anchor_text}'...")
        html_content = fetch_page_content(url)
        backlink_found, anchor_found, is_nofollow = find_backlink(html_content, target_site, anchor_text)

        if not backlink_found:
            webhook.send(f"- Backlink invalide sur {url}. L'ancre devrait être **{anchor_text}** et l'url Rotek {target_site}")
        elif not anchor_found:
            webhook.send(f"- Backlink invalide sur {url}. L'ancre **{anchor_text}** est trouvée mais pas l'URL {target_site}")
        elif is_nofollow:
            webhook.send(f"- Backlink invalide sur {url}. Le lien {target_site} sur l'ancre **{anchor_text}** est en **nofollow**.")
    webhook.send(f":white_check_mark: Vérification des backlinks terminée ██████████ (100%)")

if __name__ == "__main__":
    backlinks_data = [
         {
            'url': 'https://example.com/page1',
            'target_site': 'https://votresite.com/page1',
            'anchor_text': 'Cliquez ici'
        },
        {
            'url': 'https://example.com/page2',
            'target_site': 'https://votresite.com/page2',
            'anchor_text': 'En savoir plus'
        }
    ]

    track_backlinks(backlinks_data)
