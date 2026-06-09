from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional

from backend.models import DashboardResponse, Product, Recommendation, User
from backend.recommender import EcommerceRecommender

app = FastAPI(title="IntelliCart E-Commerce Recommendation API")
recommender = EcommerceRecommender()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "E-Commerce Recommendation API"}


@app.get("/products", response_model=List[Product])
def list_products(q: Optional[str] = Query(None, description="Search query for product name or category")):
    if q:
        return recommender.search_products(q, limit=50)
    return recommender.products.to_dict(orient="records")


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = recommender.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = recommender.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/recommend/popular", response_model=List[Recommendation])
def recommend_popular():
    products = recommender.popularity_recommendations(limit=10)
    return [Recommendation(**{**p, "score": float(p["sales"] * 0.1 + p["rating"])}) for p in products]


@app.get("/recommend/user/{user_id}", response_model=List[Recommendation])
def user_recommendations(user_id: int):
    if recommender.get_user(user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    products = recommender.hybrid_recommendations(user_id, limit=10)
    return [Recommendation(**{**p, "score": float(p["rating"]), "explanation": recommender.explain_recommendation(user_id, p["product_id"])}) for p in products]


@app.get("/recommend/product/{product_id}", response_model=List[Recommendation])
def similar_product_recommendations(product_id: int):
    if recommender.get_product(product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    products = recommender.get_similar_products(product_id, limit=6)
    return [Recommendation(**{**p, "score": float(score), "explanation": "Similar product based on category and description."}) for p, score in zip(products, [1.0] * len(products))]


@app.get("/dashboard/{user_id}", response_model=DashboardResponse)
def dashboard(user_id: int):
    result = recommender.get_dashboard(user_id, limit=8)
    return DashboardResponse(
        user=User(**result["user"]),
        recommendations=[Recommendation(**{**p, "score": float(p.get("rating", 0)), "explanation": recommender.explain_recommendation(user_id, p["product_id"])}) for p in result["recommendations"]],
        recent_activity=result["recent_activity"],
        trending_products=[Recommendation(**{**p, "score": float(p.get("rating", 0)), "explanation": "Trending product."}) for p in result["trending_products"]],
    )


@app.get("/trending", response_model=List[Recommendation])
def trending_products():
    products = recommender.get_trending_products(limit=10)
    return [Recommendation(**{**p, "score": float(p["rating"]), "explanation": "Trending right now."}) for p in products]
