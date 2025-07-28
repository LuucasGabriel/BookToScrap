
# 📚 Projeto Books To Scrape + Power BI

Este projeto realiza **web scraping** no site [Books to Scrape](http://books.toscrape.com/), armazena os dados coletados em uma **tabela no SQL Server** e depois faz a análise visual no **Power BI**, usando medidas DAX para gerar insights como **faixa de preço**, **ranking** e **segmentação de livros baratos x caros**.

---

## 🚀 Principais etapas do script Python

### 1️⃣ Configuração do WebDriver

```py
options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1920,1080')
```

- Configura o **ChromeDriver** para rodar em **modo invisível (headless)**, sem abrir a janela do navegador.
- Define o tamanho da janela para evitar quebras de layout.

---

### 2️⃣ Navegação e scraping em múltiplas páginas

```py
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
```

- Acessa **todas as páginas do catálogo** (páginas 1, 2, 3, ...) até não encontrar mais o botão **next**.
- Para cada livro, extrai:
  - **Título**
  - **Preço**
  - **Disponibilidade**
  - **Avaliação** (1 a 5 estrelas)
  - **Link do produto**
  - **Categoria**, visitando a página individual do livro.

---

### 3️⃣ Armazenamento no SQL Server

```py
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='LivrosScraping' AND xtype='U')
CREATE TABLE LivrosScraping ( ... )
```

- Cria a tabela `LivrosScraping` **se ela ainda não existir**, com colunas para todos os campos.
- Insere os dados de cada livro com `INSERT INTO`.

---

## 📊 Análise no Power BI

Com a tabela no **SQL Server**, os dados foram importados no **Power BI**. As principais **medidas DAX** criadas foram:

### ✅ Medidas de Base

| Medida | Descrição |
| ------ | ---------- |
| **`Average`** | `AVERAGE(LivrosScraping[preco])` — calcula o preço médio dos livros. |
| **`Quantity`** | `COUNT(LivrosScraping[id])` — conta quantos livros foram coletados. |
| **`Sales`** | `SUM(LivrosScraping[preco])` — soma total de preços (proxy para receita). |
| **`Rating`** | `SUM(LivrosScraping[Avaliação])` — soma das avaliações. |

---

### ✅ Faixas de preço com SWITCH

```DAX
Faixa de Preço = 
SWITCH(
    TRUE();
    LivrosScraping[preco] <= 10; "0 - 10"; 
    LivrosScraping[preco] <= 20; "10 - 20";
    LivrosScraping[preco] <= 30;  "20 - 30";
    LivrosScraping[preco] <= 40;  "30 - 40";
    LivrosScraping[preco] <= 50; "40 - 50";
    LivrosScraping[preco] <= 60; "50 - 60";
    LivrosScraping[preco] <= 70; "60 - 70";
    LivrosScraping[preco] > 70; "70 - 80" 
)
```

- Cria **grupos de faixa de preço** para facilitar segmentações e gráficos.

---

### ✅ Produtos baratos x caros

```DAX
Barato x Caro = 
SWITCH(
    TRUE(),
    LivrosScraping[preco] <= 20, "Baratos",
    LivrosScraping[preco] <= 40, "Intermediário",
    LivrosScraping[preco] > 40, "Premium"
)
```

- Classifica cada livro como **Barato**, **Intermediário** ou **Premium**.

---

### ✅ Ranking dinâmico com ALLSELECTED

```DAX
Rank ALLSELECTED = 
VAR RNK =
    RANKX( // Rank dos melhores
        ALLSELECTED(LivrosScraping);// Faz o rank respeitando a categoria de cada ID
        [Sales];;
        Desc
    )
RETURN
IF(
    [Sales] ;
    RNK
)
```

- Cria um **ranking dinâmico** respeitando filtros (ex.: Categoria).
- Permite **ranquear livros dentro de categorias**, ou geral, conforme filtros ativos.

---

## 🎨 Tema Power BI

Para o **visual**, foi usado um tema inspirado em **tons de papel**, com cores como `#FFF8E7` (bege página) e `#A67B5B` (marrom leve).

---

## ✅ Resultado

- Dados organizados no **SQL Server**.
- Relatórios básicos e dinâmicos no **Power BI** com filtros por categoria, faixa de preço e ranking.
- Visualização clara de produtos baratos, caros, populares ou de nicho.

---

## 📌 Tecnologias usadas

- Python + Selenium + pyodbc
- SQL Server
- Power BI
- Site **Books to Scrape**

---

## 📊 Visualizações do Projeto

Abaixo estão algumas imagens do projeto para ilustrar as principais análises:

<p align="center">
  <img src="https://github.com/LuucasGabriel/BookToScrap/blob/main/Design/Captura%20de%20tela%202025-07-22%20204828.png?raw=true" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/LuucasGabriel/BookToScrap/blob/main/Design/Captura%20de%20tela%202025-07-22%20205014.png?raw=true" width="800"/>
</p>

<p align="center">
  <img src="https://github.com/LuucasGabriel/BookToScrap/blob/main/Design/Captura%20de%20tela%202025-07-22%20205255.png?raw=true" width="800"/>
</p>

### 🔗 Autor
Desenvolvido por *Lucas Gabriel* ✨
