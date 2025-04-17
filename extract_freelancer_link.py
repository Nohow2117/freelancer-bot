from playwright.sync_api import Page
import time
import random

def highlight_element(element):
    """
    Evidenzia l'elemento passato contornandolo di rosso e facendolo scorrere al centro della pagina.
    Utile per vedere su quale card sta lavorando il bot.
    """
    element.evaluate("el => { el.style.outline = '2px solid red'; el.scrollIntoView({behavior: 'smooth', block: 'center'}); }")

import json
import os

def load_selectors():
    """
    Carica i selettori (XPATH e CSS) dal file selectors.json presente nella stessa cartella.
    Restituisce un dizionario con tutti i selettori usati dal bot.
    """
    with open(os.path.join(os.path.dirname(__file__), 'selectors.json'), encoding='utf-8') as f:
        return json.load(f)

from freelancer_utils import is_freelancer_already_contacted, save_freelancer_to_db, close_all_chats

def process_single_freelancer_card(page, card, selectors):
    """
    Estrae e processa una singola card di freelancer:
    - Estrae nome, username e link dalla card (con pause "umane" tra ogni step).
    - Normalizza lo username togliendo la chiocciola iniziale.
    - Controlla se il professionista è già stato contattato (usando nome, username, link) e in caso affermativo salta la card.
    - Clicca il bottone della card per aprire il modale di chat.
    - Clicca il bottone chat nel modale.
    - Trova la textarea e genera un messaggio dinamico tramite spintax letto da selectors.json (chiave freelancer_message_text).
    - Simula la scrittura a mano del messaggio, carattere per carattere, con velocità regolabile.
    - Invia il messaggio, salva i dati nel database, chiude la chat e attende tra le azioni.
    """
    # Estrai nome
    username_elem = card.query_selector(selectors["freelancer_username_selector"])
    print("Nome non trovato." if not username_elem else f"Nome: {username_elem.inner_text()}")
    time.sleep(random.uniform(0.7, 1.5))
    # Estrai username
    userid_elem = card.query_selector(selectors["freelancer_userid_selector"])
    print("Username non trovato." if not userid_elem else f"Username: {userid_elem.inner_text()}")
    time.sleep(random.uniform(0.7, 1.5))
    # Estrai link
    print("Link non trovato." if not card.get_attribute('href') else f"Link: {card.get_attribute('href')}")
    time.sleep(random.uniform(0.7, 1.2))
    nome = username_elem.inner_text() if username_elem else ""
    # Normalizza username togliendo sempre la chiocciola iniziale (per confronto e salvataggio)
    username = userid_elem.inner_text().lstrip('@') if userid_elem else ""
    link = card.get_attribute('href') if card.get_attribute('href') else ""
    db_path = os.path.join(os.path.dirname(__file__), 'sent_freelancers.json')
    # Controllo duplicati: se già contattato, salta la card
    if is_freelancer_already_contacted(nome, username, link, db_path):
        print("Professionista già presente nel database (username o link). Salto il contatto.")
        time.sleep(random.uniform(0.7, 1.2))
        return
    # Clicca il bottone della card e apri il modale
    button = card.query_selector(selectors["freelancer_card_button_selector"])
    time.sleep(random.uniform(0.7, 1.5))
    if button:
        button.click()
        print("Bottone cliccato!")
        page.wait_for_selector(selectors["freelancer_modal_selector"], timeout=5000)
        time.sleep(random.uniform(0.7, 1.2))
        # Clicca il bottone chat nel modale
        chat_btn = page.query_selector(selectors["freelancer_modal_chat_button_selector"])
        if chat_btn:
            chat_btn.click()
            print("Bottone chat cliccato!")
            time.sleep(random.uniform(0.7, 1.2))
            # Trova la textarea per il messaggio
            textarea = page.query_selector(selectors["freelancer_chat_textarea_selector"])
            if textarea:
                # Leggi lo spintax da selectors.json (chiave freelancer_message_text)
                SPINTAX_MESSAGE = selectors.get("freelancer_message_text",
                    "{Ciao|Salve}, stiamo selezionando una risorsa per il servizio clienti.")
                def parse_spintax(text):
                    """
                    Sostituisce ogni gruppo {a|b|c} con una scelta casuale tra a, b, c.
                    Supporta gruppi annidati. Sostituisce anche * con apostrofo per compatibilità JSON.
                    """
                    import re
                    pattern = re.compile(r'\{([^{}]+)\}')
                    while True:
                        match = pattern.search(text)
                        if not match:
                            break
                        options = match.group(1).split('|')
                        # Sostituisci eventuali escape * con apostrofo normale
                        options = [opt.replace('*', "'") for opt in options]
                        text = text[:match.start()] + random.choice(options) + text[match.end():]
                    return text
                # Genera il messaggio randomico
                message_text = parse_spintax(SPINTAX_MESSAGE)
                # Rimuovi tutti i caratteri di a capo per inviare un messaggio su una sola riga (più compatibile)
                message_text = message_text.replace('\n', ' ')
                # Simula la scrittura a mano, carattere per carattere (solo caratteri normali)
                SPEED_TYPING = 0.05  # secondi per carattere, modificabile dall'utente
                textarea.fill("")  # Pulisci la textarea prima di scrivere
                for char in message_text:
                    textarea.type(char, delay=int(SPEED_TYPING * 1000))  # delay in ms
                time.sleep(random.uniform(0.5, 1.2))
                textarea.press("Enter")
                print(f"Messaggio inviato simulando digitazione ({SPEED_TYPING}s/carattere)! Testo:\n{message_text}")
                # Salva il professionista nel database
                entry = {"nome": nome, "username": username, "link": link}
                save_freelancer_to_db(entry, db_path)
                print("Dati professionista salvati nel database.")
                time.sleep(random.uniform(0.7, 1.3))
                # Chiudi tutte le chat aperte
                close_all_chats(page, selectors)
            else:
                print("Textarea messaggio non trovata.")
        else:
            print("Bottone chat non trovato nel modale.")
    else:
        print("Bottone non trovato nella card.")
    # Pausa finale dopo aver processato la card
    time.sleep(random.uniform(1.0, 2.0))


def process_first_freelancer_card(page: 'Page'):
    """
    Processa tutte le card freelancer trovate, gestendo anche lo scroll infinito.
    Scrolla di 2000px ogni 5 card processate.
    """
    selectors = load_selectors()
    last_count = 0
    processed_since_scroll = 0
    while True:
        elements = page.query_selector_all(f'xpath={selectors["freelancer_card_xpath"]}')
        if not elements:
            print("Nessuna card trovata.")
            return
        # Processa solo le nuove card
        for idx, card in enumerate(elements[last_count:], start=last_count+1):
            print(f"\n--- Card {idx} ---")
            process_single_freelancer_card(page, card, selectors)
            processed_since_scroll += 1
            # Scrolla ogni 5 card processate
            if processed_since_scroll % 5 == 0:
                page.evaluate("window.scrollBy(0, 2000);")
                print("Scroll di 2000px dopo 5 card...")
                time.sleep(2.5)  # Pausa umana per attendere il caricamento
        if len(elements) == last_count:
            print("Nessuna nuova card caricata, fine dello scroll.")
            break
        last_count = len(elements)
