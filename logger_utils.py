import logging
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'run.log')

def setup_run_logger():
    # Ogni run: pulisci il file
    open(LOG_FILE, 'w').close()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
    )
    logging.info('--- Nuova run avviata ---')
    return logging.getLogger("run")
