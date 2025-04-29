import requests
from ai_dev_app.constants.app_constants import AppConstants

def search_frjar_api(product_name):
    try:
        url = AppConstants.SUPPLIER_SEARCH_URL
        payload = {"search": product_name, "lang": "ENGLISH"}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
    except Exception:
        pass
    return []
