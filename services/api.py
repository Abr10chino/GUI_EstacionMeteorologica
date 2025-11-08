import requests
from .config import BASE_URL, TIMEOUT

def getLecturas(limit=20, fecha=None):
    try:
        params = {"limit": limit}
        if fecha:
            params["fecha"] = fecha
        response = requests.get(f"{BASE_URL}/lecturas", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print("Error al conectar con el servidor:", e)
        return []