import pyodbc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# --- CONFIGURA O DRIVER ---
options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1920,1080')

service = Service('') #Caminho para o seu chromedriver
driver = webdriver.Chrome(service=service, options=options)

# --- COMEÇA DA PÁGINA INICIAL ---
base_url = 'http://books.toscrape.com/catalogue/page-1.html'
driver.get(base_url)
time.sleep(2)

resultados = []

while True:
    time.sleep(2)

    livros = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod')

    for livro in livros:
        titulo = livro.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('title')
        preco = livro.find_element(By.CLASS_NAME, 'price_color').text
        disponibilidade = livro.find_element(By.CLASS_NAME, 'availability').text.strip()
        avaliacao = livro.find_element(By.CLASS_NAME, 'star-rating').get_attribute('class').split()[-1]
        link_relativo = livro.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('href')

        # Visita página individual do livro para pegar categoria
        driver.get(link_relativo)
        breadcrumb = driver.find_element(By.CSS_SELECTOR, 'ul.breadcrumb li:nth-child(3) a').text   

        resultados.append((titulo, preco, disponibilidade, avaliacao, link_relativo, breadcrumb))

        # Volta para a lista
        driver.back()

    print(f"📚 Livros coletados até agora: {len(resultados)}")

    # Tenta achar botão "next"
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'li.next a')
        next_page_url = next_button.get_attribute('href')
        driver.get(next_page_url)
    except:
        print("✅ Todas as páginas foram coletadas!")
        break

driver.quit()

print(f"✅ Total de livros coletados: {len(resultados)}")

# --- CONEXÃO SQL SERVER ---
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};' #Verififcar o numero da versão, digite na barra de pesquisar no Google: chrome://version
    'SERVER=seu_server;'
    'DATABASE=nome_do_seu_banco;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)

cursor = conn.cursor()

# --- CRIA TABELA SE NÃO EXISTIR ---
cursor.execute("""
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='LivrosScraping' AND xtype='U')
CREATE TABLE LivrosScraping (
    id INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(255),
    preco NVARCHAR(50),
    disponibilidade NVARCHAR(50),
    avaliacao NVARCHAR(20),
    link NVARCHAR(255),
    categoria NVARCHAR(100)
)
""")
conn.commit()

# --- INSERE DADOS ---
for titulo, preco, disponibilidade, avaliacao, link, categoria in resultados:
    cursor.execute("""
    INSERT INTO LivrosScraping (titulo, preco, disponibilidade, avaliacao, link, categoria)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (titulo, preco, disponibilidade, avaliacao, link, categoria))

conn.commit()
conn.close()

print("✅ Todos os livros salvos no SQL Server com sucesso!")
