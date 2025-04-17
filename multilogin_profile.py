import os
import hashlib
import requests
from urllib.parse import quote
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

MLX_AUTH_BASE_URL = "https://api.multilogin.com"
MLX_LAUNCHER_BASE_URL = "https://launcher.mlx.yt:45001/api/v2"

class MultiloginHandler:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.token = None
        self.MLX_AUTH_BASE_URL = MLX_AUTH_BASE_URL
        self.MLX_LAUNCHER_BASE_URL = MLX_LAUNCHER_BASE_URL

    def authenticate(self) -> bool:
        if not self.email or not self.password:
            print("Email e password Multilogin richiesti.")
            return False
        signin_url = f"{self.MLX_AUTH_BASE_URL}/user/signin"
        payload = {
            "email": self.email,
            "password": hashlib.md5(self.password.encode()).hexdigest(),
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = requests.post(signin_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and data['data'].get('token'):
                self.token = data['data']['token']
                print("Token ottenuto con successo.")
                return True
            print("Struttura risposta API inattesa - token non trovato")
            return False
        except Exception as e:
            print(f"Errore autenticazione: {e}")
            return False

    def start_profile(self, profile_id: str, folder_id: str) -> tuple[bool, str | None]:
        if not self.token:
            print("Token mancante. Autenticarsi prima.")
            return False, None
        profile_id_encoded = quote(profile_id, safe='')
        folder_id_encoded = quote(folder_id.strip(), safe='')
        start_url = f"{self.MLX_LAUNCHER_BASE_URL}/profile/f/{folder_id_encoded}/p/{profile_id_encoded}/start?automation_type=playwright"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            response = requests.get(start_url, headers=headers, timeout=60)
            data = response.json()
            if response.status_code == 400 and data.get("status", {}).get("error_code") == "PROFILE_ALREADY_RUNNING":
                print("Profilo già in esecuzione. Recupero porta...")
                return self.get_running_profile_port(profile_id)
            response.raise_for_status()
            if data.get("data") and data["data"].get("port"):
                port = data["data"]["port"]
                cdp_url = f"http://127.0.0.1:{port}"
                print(f"Profilo avviato. CDP URL: {cdp_url}")
                return True, cdp_url
            print("Risposta API non valida avviando profilo.")
            return False, None
        except Exception as e:
            # Se la response è disponibile, mostra il testo della risposta server
            if 'response' in locals():
                print(f"Dettaglio risposta server: {response.text}")
            print(f"Errore avvio profilo: {e}")
            return False, None

    def get_running_profile_port(self, profile_id: str) -> tuple[bool, str | None]:
        if not self.token:
            print("Token mancante.")
            return False, None
        profile_id_encoded = quote(profile_id, safe='')
        status_url = f"{self.MLX_LAUNCHER_BASE_URL}/profile/p/{profile_id_encoded}/status"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            response = requests.get(status_url, headers=headers, timeout=30)
            data = response.json()
            if data.get("data") and data["data"].get("port"):
                port = data["data"]["port"]
                cdp_url = f"http://127.0.0.1:{port}"
                print(f"Profilo già in esecuzione sulla porta {port}")
                return True, cdp_url
            return False, None
        except Exception as e:
            print(f"Errore ottenendo porta profilo: {e}")
            return False, None

if __name__ == "__main__":
    # Carica le credenziali da .env
    email = os.getenv("ML_EMAIL")
    password = os.getenv("ML_PASSWORD")
    profile_id = os.getenv("ML_PROFILE_ID")
    folder_id = os.getenv("ML_FOLDER_ID")

    if not all([email, password, profile_id, folder_id]):
        print("Assicurati che ML_EMAIL, ML_PASSWORD, ML_PROFILE_ID, ML_FOLDER_ID siano definiti in .env.")
        exit(1)

    handler = MultiloginHandler(email, password)
    if handler.authenticate():
        success, cdp_url = handler.start_profile(profile_id, folder_id)
        if success and cdp_url:
            print(f"Profilo pronto all'uso su: {cdp_url}")
        else:
            print("Impossibile avviare il profilo.")
    else:
        print("Autenticazione fallita.")
