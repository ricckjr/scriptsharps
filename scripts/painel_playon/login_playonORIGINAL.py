import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# Carrega variáveis de ambiente do .env
# ----------------------------------------------------------------------
load_dotenv()
USERNAME       = os.getenv("PLAYON_USER")
PASSWORD       = os.getenv("PLAYON_PASS")
CAPMONSTER_KEY = os.getenv("CAPMONSTER_KEY")
SITE_KEY       = os.getenv("SITE_KEY")

LOGIN_URL = "https://officeplayon.com/#/login"


def solve_recaptcha(site_key: str, url: str, client_key: str) -> str:
    """
    Cria uma task no CapMonster e aguarda até obter o gRecaptchaResponse.
    Retorna a string do token quando estiver pronto.
    """
    print("🔐 Enviando tarefa ao CapMonster...")
    payload = {
        "clientKey": client_key,
        "task": {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key
        }
    }
    resp1 = requests.post("https://api.capmonster.cloud/createTask", json=payload).json()
    if resp1.get("errorId", 1) != 0:
        raise RuntimeError(f"Erro ao criar task no CapMonster: {resp1}")
    task_id = resp1["taskId"]

    for attempt in range(20):
        print(f"⏳ Aguardando resolução ({attempt + 1}/20)...")
        time.sleep(5)
        resp2 = requests.post(
            "https://api.capmonster.cloud/getTaskResult",
            json={"clientKey": client_key, "taskId": task_id}
        ).json()

        if resp2.get("errorId", 1) != 0:
            raise RuntimeError(f"Erro ao obter resultado do CapMonster: {resp2}")

        if resp2.get("status") == "ready":
            print("✅ reCAPTCHA resolvido com sucesso.")
            return resp2["solution"]["gRecaptchaResponse"]

    raise TimeoutError("❌ CapMonster não respondeu a tempo.")


def main():
    # ------------------------------------------------------------------
    # Configurações do ChromeDriver / Selenium
    # ------------------------------------------------------------------
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")  # Descomente se quiser rodar sem abrir janela
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)

    try:
        print("🌐 Acessando a página de login...")
        driver.get(LOGIN_URL)
        time.sleep(2)

        # ------------------------------------------------------------------
        # 1) Preenche usuário e senha
        # ------------------------------------------------------------------
        print("👤 Preenchendo usuário e senha...")
        username_input = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Usuário"]'))
        )
        password_input = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Senha"]'))
        )
        username_input.clear()
        username_input.send_keys(USERNAME)
        password_input.clear()
        password_input.send_keys(PASSWORD)

        # ------------------------------------------------------------------
        # 2) Resolve o CAPTCHA via CapMonster
        # ------------------------------------------------------------------
        print("🧠 Resolvendo reCAPTCHA...")
        token = solve_recaptcha(SITE_KEY, LOGIN_URL, CAPMONSTER_KEY)

        # ------------------------------------------------------------------
        # 3) Injeta o token no <textarea id="g-recaptcha-response">
        # ------------------------------------------------------------------
        print("💉 Injetando token no campo 'g-recaptcha-response'...")
        driver.execute_script("""
            // Localiza (ou cria) o textarea de resposta do reCAPTCHA
            var textarea = document.getElementById('g-recaptcha-response');
            if (!textarea) {
                textarea = document.createElement('textarea');
                textarea.id = 'g-recaptcha-response';
                textarea.name = 'g-recaptcha-response';
                textarea.style.display = 'none';
                document.querySelector('form').appendChild(textarea);
            }
            // Preenche e dispara evento de mudança
            textarea.style.display = 'block';
            textarea.value = arguments[0];
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.style.display = 'none';
        """, token)
        time.sleep(2)

        # ------------------------------------------------------------------
        # 4) Entra no iframe do reCAPTCHA e clica no checkbox
        # ------------------------------------------------------------------
        print("🔍 Encontrando iframe do reCAPTCHA...")
        recaptcha_iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]'))
        )
        driver.switch_to.frame(recaptcha_iframe)
        print("✅ Dentro do iframe, clicando no checkbox do reCAPTCHA...")
        checkbox = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-anchor"]/div[1]'))
        )
        checkbox.click()
        time.sleep(2)

        # Volta ao contexto principal
        driver.switch_to.default_content()
        time.sleep(1)

        # ------------------------------------------------------------------
        # 5) Clica no botão “Logar” (XPath corrigido)
        # ------------------------------------------------------------------
        print("🚀 Clicando no botão 'Logar'...")
        # XPath que junta todo o texto interno, ignorando comentários internos
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Logar']"))
        )

        # Alternativa usando CSS selector:
        # login_button = wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary.my-4"))
        # )

        # Garante que o botão esteja visível na viewport (rolagem, se necessário)
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(0.3)

        # Tenta clicar normalmente; se não der, força via JavaScript
        try:
            login_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", login_button)

        # ------------------------------------------------------------------
        # 6) Espera alguns segundos e imprime a URL final
        # ------------------------------------------------------------------
        print("⏳ Aguardando resposta do login...")
        time.sleep(5)
        print("🔗 URL final após login:", driver.current_url)

        # ------------------------------------------------------------------
        # 7) Aguarda mais 5 segundos antes de fechar tudo
        # ------------------------------------------------------------------
        print("⏰ Esperando 5 segundos antes de finalizar...")
        time.sleep(5)

    except Exception as e:
        # Em caso de erro, captura screenshot e HTML para debug
        print("❌ Erro durante o login:", e)
        driver.save_screenshot("erro_login.png")
        print("📸 Screenshot salva como 'erro_login.png'")
        with open("erro_login.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML salvo como 'erro_login.html'")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
