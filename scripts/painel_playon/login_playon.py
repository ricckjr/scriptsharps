import os
import time
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# carrega variáveis do .env
load_dotenv()
USERNAME       = os.getenv("PLAYON_USER")
PASSWORD       = os.getenv("PLAYON_PASS")
CAPMONSTER_KEY = os.getenv("CAPMONSTER_KEY")
SITE_KEY       = os.getenv("SITE_KEY")

LOGIN_URL = "https://officeplayon.com/#/login"

def solve_recaptcha_capmonster(site_key, page_url, client_key):
    """Cria task no CapMonster e faz polling até obter o token."""
    payload = {
        "clientKey": client_key,
        "task": {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key
        }
    }
    r1 = requests.post("https://api.capmonster.cloud/createTask", json=payload).json()
    if r1.get("errorId") != 0:
        raise RuntimeError(f"createTask error: {r1}")
    task_id = r1["taskId"]

    for _ in range(20):
        time.sleep(5)
        r2 = requests.post(
            "https://api.capmonster.cloud/getTaskResult",
            json={"clientKey": client_key, "taskId": task_id}
        ).json()
        if r2.get("errorId") != 0:
            raise RuntimeError(f"getTaskResult error: {r2}")
        if r2.get("status") == "ready":
            return r2["solution"]["gRecaptchaResponse"]

    raise TimeoutError("Timeout ao resolver reCAPTCHA")

def main():
    # configura o Selenium
    opts = Options()
    # aponte para o binário do Chromium no seu sistema
    opts.binary_location = "/usr/bin/chromium-browser"  # ou "/snap/bin/chromium"

    # usa webdriver-manager para obter o chromedriver e configura o service
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=opts)

    driver.get(LOGIN_URL)
    time.sleep(2)

    # preenche usuário e senha
    driver.find_element(By.XPATH, "//input[@type='text']").send_keys(USERNAME)
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(PASSWORD)

    # resolve reCAPTCHA via CapMonster
    token = solve_recaptcha_capmonster(SITE_KEY, LOGIN_URL, CAPMONSTER_KEY)

    # injeta token no campo oculto
    driver.execute_script("""
        const fld = document.querySelector('#g-recaptcha-response');
        fld.style.display = 'block';
        fld.value = arguments[0];
        fld.style.display = 'none';
    """, token)

    # clica em “Logar”
    driver.find_element(By.XPATH, "//button[contains(.,'Logar')]").click()

    # espera e exibe URL final
    time.sleep(5)
    print("URL final:", driver.current_url)
    driver.quit()

if __name__ == "__main__":
    main()
