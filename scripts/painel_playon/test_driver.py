from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

opts = Options()
# se você não tiver display gráfico, descomente a linha abaixo:
# opts.add_argument("--headless=new")
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver  = webdriver.Chrome(service=service, options=opts)

print(">>> Driver criado, navegando para example.com ...")
driver.get("https://example.com")
print(">>> Título da página:", driver.title)

driver.quit()
