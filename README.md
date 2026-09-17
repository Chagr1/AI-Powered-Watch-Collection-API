## 🚀 API Endpoints (Swagger UI)

![Swagger UI Screenshot](swagger-ui.png)
# 🤖 AI-Powered Watch Collection REST API

A modern, robust backend service built with **FastAPI**, **SQLAlchemy**, and **Groq LLM (Qwen)**. This project automates watch data collection by leveraging artificial intelligence to enrich technical specifications from simple brand and model inputs, complete with strict Pydantic validation, error handling, and a full CRUD lifecycle.

---

## 🚀 Key Features

* **AI-Driven Data Enrichment:** Automatically fetches and structures technical details (movement type, case size, crystal type, water resistance, strap, power reserve) using an LLM.
* **Confidence Scoring & Validation:** Evaluates AI outputs with an `ai_confidence` score and a Python-controlled `needs_verification` safety flag.
* **Full CRUD Operations:** Create, Read, Update, and Delete watch records seamlessly.
* **Advanced Search & Filtering:** Dynamic query parameters for filtering by brand, movement, crystal type, and case size range, supported by pagination.
* **Data Integrity & Safety:** Duplicate prevention (`409 Conflict`), strict Pydantic v2 data bounds, and environment-based secret management (`.env`).

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **Database & ORM:** SQLite & SQLAlchemy
* **Validation:** Pydantic v2
* **AI Integration:** Groq API (OpenAI client SDK)
* **Environment Management:** python-dotenv

---

## 📂 Project Architecture

```text
PythonAPI/
│
├── .env                # Environment variables (API keys)
├── main.py             # Core FastAPI application & endpoints
├── watch_collection.db # SQLite database (auto-generated)
└── README.md           # Project documentation
