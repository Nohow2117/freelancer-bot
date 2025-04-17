import sys
import time
from multilogin_profile import MultiloginHandler
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from logger_utils import setup_run_logger
import logging

# Carica variabili da .env
load_dotenv()
logger = setup_run_logger()

# Credenziali e ID profilo Multilogin
email = os.getenv("ML_EMAIL")
password = os.getenv("ML_PASSWORD")
profile_id = os.getenv("ML_PROFILE_ID")
folder_id = os.getenv("ML_FOLDER_ID")

if not all([email, password, profile_id, folder_id]):
    logging.info("Assicurati che ML_EMAIL, ML_PASSWORD, ML_PROFILE_ID, ML_FOLDER_ID siano definiti in .env.")
    sys.exit(1)

# Avvia profilo Multilogin e ottieni CDP URL
handler = MultiloginHandler(email, password)
if not handler.authenticate():
    logging.info("Autenticazione Multilogin fallita.")
    sys.exit(1)

success, cdp_url = handler.start_profile(profile_id, folder_id)
if not (success and cdp_url):
    logging.info("Impossibile avviare profilo Multilogin.")
    sys.exit(1)

# Attendi qualche secondo per sicurezza
logging.info("Attendo 3 secondi per assicurare che il profilo sia pronto...")
time.sleep(3)

# Usa Playwright per collegarsi al browser Multilogin e aprire la pagina richiesta
SEARCH_TERMS = ["support", "chat", "customer", "entry", "desk", "representative", "moderator", "clienti", "management", "transcription", "relations", "email"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    pages = context.pages
    import random
    # I termini di ricerca ora vengono scelti in ordine casuale per evitare pattern ripetuti
    for term in random.sample(SEARCH_TERMS, len(SEARCH_TERMS)):
        # Scegli dinamicamente un valore per hourlyRateMax tra 5 e 20
        hourly_rate_max = random.randint(15, 25)
        # Scegli dinamicamente un valore per hourlyRateMin tra 0 e hourly_rate_max
        hourly_rate_min = random.randint(0, hourly_rate_max)
        # Costruisci dinamicamente la URL cambiando la parola dopo users?q=, hourlyRateMax e hourlyRateMin
        FREELANCER_SEARCH_URL = f"https://www.freelancer.com/search/users?q={term}&userCountry=it&userHourlyRateMax=15&userSkills=2512,2920,671,79,399&userCountries=it&hourlyRateMax={hourly_rate_max}&hourlyRateMin={hourly_rate_min}"
        if pages:
            page = pages[0]
            logging.info("Uso la prima tab già aperta del profilo Multilogin.")
        else:
            page = context.new_page()
            logging.info("Nessuna tab trovata, ne apro una nuova.")
        page.goto(FREELANCER_SEARCH_URL)
        logging.info(f"Pagina caricata: {FREELANCER_SEARCH_URL}")
        page.wait_for_load_state('networkidle')
        logging.info(f"Pagina caricata completamente per ricerca '{term}' con hourlyRateMax={hourly_rate_max} e hourlyRateMin={hourly_rate_min}. Estraggo i link richiesti...")
        from extract_freelancer_link import process_first_freelancer_card
        process_first_freelancer_card(page)
        logging.info(f"--- Fine ciclo per ricerca '{term}' con hourlyRateMax={hourly_rate_max} e hourlyRateMin={hourly_rate_min} ---\n")
        time.sleep(2)  # Pausa tra una ricerca e l'altra
    input("Premi INVIO per chiudere...")
    browser.close()
