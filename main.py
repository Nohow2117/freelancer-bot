import sys
import time
from multilogin_profile import MultiloginHandler
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

# Credenziali e ID profilo Multilogin
email = os.getenv("ML_EMAIL")
password = os.getenv("ML_PASSWORD")
profile_id = os.getenv("ML_PROFILE_ID")
folder_id = os.getenv("ML_FOLDER_ID")

if not all([email, password, profile_id, folder_id]):
    print("Assicurati che ML_EMAIL, ML_PASSWORD, ML_PROFILE_ID, ML_FOLDER_ID siano definiti in .env.")
    sys.exit(1)

# Avvia profilo Multilogin e ottieni CDP URL
handler = MultiloginHandler(email, password)
if not handler.authenticate():
    print("Autenticazione Multilogin fallita.")
    sys.exit(1)

success, cdp_url = handler.start_profile(profile_id, folder_id)
if not (success and cdp_url):
    print("Impossibile avviare profilo Multilogin.")
    sys.exit(1)

# Attendi qualche secondo per sicurezza
print("Attendo 3 secondi per assicurare che il profilo sia pronto...")
time.sleep(3)

# Usa Playwright per collegarsi al browser Multilogin e aprire la pagina richiesta
SEARCH_TERMS = ["support", "chat", "customer", "entry", "desk", "representative", "moderator", "clienti", "management", "transcription", "relations", "email"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    pages = context.pages
    import random
    for term in SEARCH_TERMS:
        # Scegli dinamicamente un valore per hourlyRateMax tra 5 e 20
        hourly_rate_max = random.randint(15, 25)
        # Scegli dinamicamente un valore per hourlyRateMin tra 0 e hourly_rate_max
        hourly_rate_min = random.randint(0, hourly_rate_max)
        # Costruisci dinamicamente la URL cambiando la parola dopo users?q=, hourlyRateMax e hourlyRateMin
        FREELANCER_SEARCH_URL = f"https://www.freelancer.com/search/users?q={term}&userCountry=it&userHourlyRateMax=15&userSkills=2512,2920,671,79,399&userCountries=it&hourlyRateMax={hourly_rate_max}&hourlyRateMin={hourly_rate_min}"
        if pages:
            page = pages[0]
            print("Uso la prima tab già aperta del profilo Multilogin.")
        else:
            page = context.new_page()
            print("Nessuna tab trovata, ne apro una nuova.")
        page.goto(FREELANCER_SEARCH_URL)
        print(f"Pagina caricata: {FREELANCER_SEARCH_URL}")
        page.wait_for_load_state('networkidle')
        print(f"Pagina caricata completamente per ricerca '{term}' con hourlyRateMax={hourly_rate_max} e hourlyRateMin={hourly_rate_min}. Estraggo i link richiesti...")
        from extract_freelancer_link import process_first_freelancer_card
        process_first_freelancer_card(page)
        print(f"--- Fine ciclo per ricerca '{term}' con hourlyRateMax={hourly_rate_max} e hourlyRateMin={hourly_rate_min} ---\n")
        time.sleep(2)  # Pausa tra una ricerca e l'altra
    input("Premi INVIO per chiudere...")
    browser.close()
