# Freelancer Bot - Architecture

## Overview
Freelancer Bot is an automation tool that interacts with the Freelancer.com website through a Multilogin browser profile. Its main purpose is to extract specific data (such as username and userId) from freelancer profile cards on a search results page, simulating human-like browsing behavior.

The bot is designed for reliability, maintainability, and clarity. All selectors and configuration are externalized to a JSON file for easy updates. The codebase is organized to keep logic minimal and files focused.

---

## Main Components

### 1. main.py
- **Purpose:** Entry point for the bot. Handles Multilogin authentication, starts the Multilogin browser profile, and launches Playwright to control the browser.
- **Responsibilities:**
  - Authenticates with Multilogin using provided credentials.
  - Starts a specific Multilogin browser profile and retrieves its CDP (Chrome DevTools Protocol) URL.
  - Connects Playwright to the running browser instance.
  - Navigates to a preconfigured Freelancer.com search URL.
  - Calls the extraction logic to process freelancer cards.
  - Closes the browser session cleanly.

### 2. extract_freelancer_link.py
- **Purpose:** Contains all logic for extracting data from Freelancer profile cards.
- **Key Functions:**
  - `highlight_element(element)`: Evidenzia visivamente una card nel browser.
  - `load_selectors()`: Carica tutti i selettori e parametri (incluso il messaggio spintax) da `selectors.json`.
  - `process_single_freelancer_card(page, card, selectors)`: Estrae e processa una card, con:
    - Estrazione dati e pause "umane".
    - Controllo duplicati.
    - Click automatici su card e modale.
    - Generazione dinamica del messaggio tramite spintax letto da `selectors.json` (chiave `freelancer_message_text`).
    - Simulazione della scrittura a mano (carattere per carattere, velocità regolabile).
    - Gestione compatibile degli a capo: ogni messaggio viene inviato su una sola riga (tutti i caratteri '\n' vengono rimossi prima della scrittura), così da evitare qualsiasi problema di troncamento o invio.
    - Il testo spintax può essere mantenuto formattato e leggibile in JSON (con \n), ma il bot invierà sempre una riga unica.
    - Invio del messaggio, salvataggio e chiusura chat.
    - Funzione completamente documentata e commentata.
- **Design:**
  - Tutti i parametri e i selettori (incluso il testo spintax del messaggio) sono caricati da JSON per massima flessibilità.
  - Il messaggio può essere modificato senza toccare il codice Python: basta cambiare la chiave `freelancer_message_text` in `selectors.json`.
  - La generazione spintax garantisce messaggi sempre diversi e comportamenti "umani".
  - La funzione di parsing spintax è robusta e compatibile con JSON.
  - Tutto il codice è ampiamente commentato e facilmente estendibile.

### 3. selectors.json
- **Purpose:** Contiene tutti i selettori XPATH/CSS e ora anche il messaggio spintax (`freelancer_message_text`) usato dal bot.
- **Design:**
  - Permette di aggiornare sia i selettori che il testo dei messaggi senza modificare il codice Python.
  - Il messaggio può includere gruppi spintax annidati per massima varietà.
  - Tutto il sistema è pensato per essere facilmente aggiornabile e mantenibile anche da non sviluppatori.

---

## Workflow
1. **User runs main.py** with Multilogin credentials and profile info.
2. **main.py** authenticates, starts the Multilogin profile, and connects Playwright to the browser.
3. The bot navigates to a Freelancer.com search results page.
4. **extract_first_freelancer_links** is called:
    - Loads selectors from `selectors.json`.
    - Selects the first N freelancer cards (default 5) using the XPATH.
    - For each card:
        - Highlights the card visually in the browser.
        - Calls `process_single_freelancer_card` to extract and process the card.
        - Prints results to the console.
        - Waits for a random delay between actions to simulate human behavior.
5. The user can inspect the browser session and results in real time.

---

## File List and Responsibilities
- **main.py**: Orchestrates the bot, handles authentication, browser connection, and flow control.
- **extract_freelancer_link.py**: All scraping and highlighting logic; minimal, well-commented, and selector-agnostic.
- **selectors.json**: Central, editable config for all selectors (XPATH/CSS) used by the bot.
- **architecture.md**: This documentation file.
- **progress.md**: Step-by-step log of all development and design changes (see below).

---

## Extensibility & Maintenance
- To add/extract new fields: Add the selector to selectors.json and update the extraction loop.
- To change which cards are processed: Adjust the XPATH in selectors.json or the `n` parameter in the extraction function.
- To update for site changes: Only selectors.json usually needs to be updated.
- All code is commented for clarity.

---

## External Dependencies
- **Playwright** (Python): For browser automation.
- **Multilogin**: For anti-detect browser profiles, controlled via API.
- **Python 3.x**: Core language.

---

## Security & Reliability
- Credentials are never hardcoded; always passed securely.
- All file paths are relative or configurable.
- Minimal code per file, with clear separation of concerns.
- Human-like delays and highlighting reduce detection risk.

---

## How to Run
1. Set up Multilogin and ensure your profile is ready.
2. Configure credentials and profile info in main.py or via environment/CLI.
3. Run `main.py` in your Python environment.
4. Watch the console output and the browser for results.

---

## Troubleshooting
- If selectors break, update selectors.json.
- If you don't see highlighting, check that the XPATH selects the visible card container and that the browser is not in headless mode.
- All errors are printed clearly to the console.

---

## Contact
For further details or issues, refer to the comments in each file or contact the original developer.
