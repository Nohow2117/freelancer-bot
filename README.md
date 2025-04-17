# Freelancer Bot

Bot automatizzato per contattare freelancer su Freelancer.com in modo umano e personalizzato.

## Funzionalità principali
- Estrazione automatica dei profili freelancer dalla ricerca.
- Invio di messaggi generati dinamicamente tramite spintax (testo configurabile da `selectors.json`).
- Simulazione della scrittura "a mano", carattere per carattere.
- Tutti i parametri (selettori, messaggio, ecc.) sono configurabili da file JSON.
- Documentazione dettagliata e codice commentato.

## Requisiti
- Python 3.10+
- [Playwright](https://playwright.dev/python/)
- Multilogin (per browser automation avanzata)

## Installazione
1. Clona la repo:
   ```sh
   git clone https://github.com/Nohow2117/freelancer-bot.git
   cd freelancer-bot
   ```
2. Crea e attiva una virtualenv (opzionale ma consigliato):
   ```sh
   python -m venv venv
   # Su Windows:
   venv\Scripts\activate
   # Su Mac/Linux:
   source venv/bin/activate
   ```
3. Installa le dipendenze:
   ```sh
   pip install -r requirements.txt
   playwright install
   ```
4. Configura il file `.env` (vedi esempio `.env.example`).
5. Personalizza `selectors.json` se vuoi cambiare messaggio o selettori.

## Avvio
```sh
python main.py
```

## Note
- Il messaggio ai freelancer viene generato randomicamente tramite spintax e inviato sempre su una sola riga (tutti i ritorni a capo vengono rimossi per compatibilità massima).
- La cartella `venv/` e i file temporanei sono esclusi dalla repo.

## Licenza
MIT
