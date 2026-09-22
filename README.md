# ⌚ AI-Powered Watch Collection REST API

A modern, robust backend service built with **FastAPI** and **SQLAlchemy**, featuring AI-driven data enrichment via the **Groq LLM (Qwen)**. This API allows users to manage their watch collections, get automated specifications from AI, filter results dynamically, and extract advanced collection statistics.

![Swagger UI Screenshot](swagger-ui.png)

🔗 **Live Demo (Swagger UI):** [Coming Soon - Will be added after deployment]

## 🚀 Key Features
- **JWT Authentication:** Secure user registration and login flows.
- **AI-Powered Data Extraction:** Uses Groq API to parse natural language (e.g., *"Find me an automatic watch under $1000"*) into structured SQL queries.
- **Advanced Filtering & Pagination:** Robust query parameters for seamless frontend integration (`limit`, `page`, `brand`, `movement`).
- **Data Analytics (SQL Aggregation):** Generates portfolio statistics using `COUNT`, `AVG`, and `GROUP BY` operations.
- **Complex Relationships:** 
  - *Many-to-Many:* Users can add watches to their Favorites.
  - *One-to-Many:* Users can leave 1-5 star ratings and reviews on watches.
- **Data Export:** Export user-specific collection data directly to CSV using Pandas.
- **Containerized Architecture:** Fully containerized using **Docker** for rapid, plug-and-play deployment across any environment.

## 🛠️ Tech Stack
- **Framework:** FastAPI, Pydantic v2
- **Database:** PostgreSQL (Neon Serverless) & SQLAlchemy ORM
- **Migrations:** Alembic
- **AI Integration:** Groq API (qwen3.8-27b)
- **Security:** Passlib (Bcrypt), python-jose (JWT)
- **DevOps:** Docker

---

## 💻 Local Setup & Installation

You can run this project instantly using **Docker (Recommended)** or set it up manually.

### Prerequisites
Create a `.env` file in the root directory of the project with the following structure:
```env
DATABASE_URL=postgresql://user:password@endpoint.neon.tech/dbname?sslmode=require
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
