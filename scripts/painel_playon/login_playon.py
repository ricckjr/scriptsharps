import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Carrega .env
load_dotenv()
USERNAME = os.getenv("PLAYON_USER")
PASSWORD = os.getenv("PLAYON_PASS")
CAPMONSTER_KEY = os.getenv("CAPMONSTER_KEY")

LOGIN_URL = "https://officeplayon.com/#/login"
EXT_PATH = "/app/capmonster_extension"

def main():
    opts = Options()
    opts.binary_location = "/usr/bin/chromium"
    opts.add_argument(f"--load-extension={EXT_PATH}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.headless = False  # importante: extensão só funciona com navegador visível

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    wait = WebDriverWait(driver, 30)

    try:
        print("🌐 Acessando o site...")
        driver.get(LOGIN_URL)

        # injeta a chave CapMonster via localStorage
        print("🔑 Configurando chave da CapMonster na extensão...")
        driver.execute_script(f"""
            localStorage.setItem('capmonster_api_key', '{CAPMONSTER_KEY}');
        """)

        # recarrega a página para ativar a extensão com a chave
        driver.get(LOGIN_URL)
        time.sleep(3)

        print("👤 Preenchendo usuário e senha...")
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div/div/div/div/div[2]/form/div[1]/input'))).send_keys(USERNAME)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div/div/div[2]/form/div[2]/input').send_keys(PASSWORD)

        print("🧠 Aguardando extensão CapMonster resolver o reCAPTCHA...")
        time.sleep(15)  # tempo para a extensão agir automaticamente

        print("🚀 Clicando em 'Logar'...")
        botao_logar = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div/div/div/div/div/div/div[2]/form/div[4]/button')
        ))
        botao_logar.click()

        print("⏳ Esperando redirecionamento...")
        time.sleep(5)
        print("🔗 URL final:", driver.current_url)

    except Exception as e:
        print("❌ Erro durante o processo:", e)
        driver.save_screenshot("erro_login.png")
        print("📸 Screenshot salva como 'erro_login.png'.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
