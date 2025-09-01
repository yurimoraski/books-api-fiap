# Books API — Tech Challenge Fase 1 (MLE)

API pública para consulta de livros obtidos via **Web Scraping** do site [Books to Scrape](https://books.toscrape.com/).  
Projeto desenvolvido como parte do **Tech Challenge — Machine Learning Engineering (Fase 1)**.

---

## Descrição do Projeto e Arquitetura

O objetivo é disponibilizar dados de livros de forma estruturada, por meio de uma **API RESTful**, para uso em análises, recomendações e modelos de Machine Learning.

### Arquitetura em alto nível
1. **Web Scraping** (`scripts/scrape_books.py`): coleta de dados (título, preço, rating, disponibilidade, categoria, imagem).
2. **Armazenamento local**: dados salvos em CSV.
3. **Banco de dados + ORM (SQLAlchemy)**: persistência estruturada.
4. **API Pública (FastAPI)**: exposição de endpoints de consulta, categorias e estatísticas.
5. **Documentação interativa**: Swagger disponível em `/docs`.

> Essa arquitetura foi pensada para ser **escalável** e **reutilizável** em futuros pipelines de ML.

---

## Instalação e Configuração

Requisitos: **Python 3.10+**

```bash
# Criar e ativar ambiente virtual
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Atualizar dependências básicas
python -m pip install --upgrade pip setuptools wheel

# Instalar pacotes do projeto
pip install -r requirements.txt

# Rodar scraping inicial (exemplo com 5 livros)
python scripts/scrape_books.py --limit 5
```

---

## Execução API

```bash
# Iniciar API em modo dev
uvicorn api.main:app --reload
```

- Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para interface Swagger.
- `GET /` redireciona automaticamente para `/docs`.

---

## Documentação das Rotas da API

### Health
- `GET /api/v1/health` → Status e contagem de livros.

### Books
- `GET /api/v1/books` → Lista livros (filtros: `title`, `category`, `min`, `max`, paginação).
- `GET /api/v1/books/{id}` → Detalhes de um livro por ID.
- `GET /api/v1/books/top-rated` → Lista top livros (ordenados por rating e preço).

### Categorias
- `GET /api/v1/categories` → Lista categorias com contagem de livros.

### Estatísticas
- `GET /api/v1/stats/overview` → Estatísticas gerais: total, preço médio, distribuição de ratings.

---

## Exemplos de Requests / Responses

### Health
```bash
curl -s http://localhost:8000/api/v1/health
```
```json
{ "status": "ok", "books": 123 }
```

---

### Listar livros com filtros
```bash
curl -s "http://localhost:8000/api/v1/books?title=python&min=50&max=150&limit=5"
```
```json
[
  {
    "id": 42,
    "title": "Python Patterns",
    "category": "Programming",
    "price": 99.9,
    "rating": 4.7
  }
]
```

---

### Categorias
```bash
curl -s http://localhost:8000/api/v1/categories
```
```json
[
  { "name": "Programming", "count": 58 },
  { "name": "Fiction", "count": 35 }
]
```

---

### Estatísticas
```bash
curl -s http://localhost:8000/api/v1/stats/overview
```
```json
{
  "total_books": 123,
  "avg_price": 64.32,
  "rating_distribution": { "4.0": 28, "4.5": 42 }
}
```

---

## Conclusão

- **Pipeline completo**: Scraping → Armazenamento → API.
- **API RESTful funcional**: Atende requisitos obrigatórios e opcionais do Tech Challenge.
- **Pronta para expansão**: Pensada para integração futura com ML (recomendações e análises).

---