# IntelliCart: E-Commerce Product Recommendation System

This repository is an IntelliCart product recommendation system built with Python.
It includes dataset-driven recommendation logic, a FastAPI backend, and a Streamlit frontend dashboard.

## Architecture

- Dataset
- Data Preprocessing
- Feature Engineering
- Recommendation Engine
- Backend API
- Frontend Dashboard

## Dataset

IntelliCart uses an official recognized dataset when available.

- UCI Online Retail dataset (`data/Online Retail.xlsx`)

The system learns from real retail transactions, including:

- purchases
- customer history
- product descriptions
- quantity and sales patterns

The dataset focuses on learning:

- user preferences
- product similarities
- hidden behavioral patterns

The output is a ranked list of the top products the user is most likely to interact with.

If the official dataset is missing, IntelliCart will fall back safely to a small local sample dataset.

## Tech Stack

- Python
- Pandas, NumPy
- Scikit-Learn, Surprise
- FastAPI
- Streamlit
- SQLite
- Plotly, Matplotlib

## Features

- Popularity-based recommendations
- Content-based similarity
- Collaborative filtering with SVD
- Hybrid recommendation strategy
- Product catalog and search
- Trending products dashboard
- Personalized user recommendations
- Recommendation explanations

## Getting Started

1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the backend API first

```powershell
uvicorn backend.app:app --reload
```

3. In a separate terminal, run the Streamlit dashboard

```powershell
streamlit run frontend/streamlit_app.py
```

```powershell
streamlit run frontend/streamlit_app.py
```

## Project Structure

- `backend/` - FastAPI backend, database seeding, recommendation logic
- `frontend/` - Streamlit dashboard
- `data/` - Sample dataset generation and reference

## Notes

- The backend loads a sample dataset into SQLite automatically on first run.
- For cold-start users, the system returns trending and popular products.
- Hybrid recommendations combine content and collaborative signals.
