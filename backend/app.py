from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import logging

from backend.models import DashboardResponse, Product, Recommendation, User
from backend.recommender import EcommerceRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IntelliCart E-Commerce Recommendation API")

# Lazy-load recommender to save startup memory
_recommender_instance = None
_recommender_error = None

def get_recommender():
    """Lazy-load recommender on first use (saves startup memory)."""
    global _recommender_instance, _recommender_error
    
    if _recommender_instance is not None:
        return _recommender_instance
    
    if _recommender_error is not None:
        raise HTTPException(status_code=503, detail=f"Recommender failed to initialize: {_recommender_error}")
    
    try:
        logger.info("Initializing EcommerceRecommender on first request...")
        _recommender_instance = EcommerceRecommender()
        logger.info("✓ EcommerceRecommender initialized successfully")
        return _recommender_instance
    except Exception as e:
        logger.error(f"Failed to initialize EcommerceRecommender: {e}", exc_info=True)
        _recommender_error = str(e)
        raise HTTPException(status_code=503, detail=f"Recommender initialization failed: {e}")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "E-Commerce Recommendation API", "mode": "lazy-loaded"}


@app.get("/products", response_model=List[Product])
def list_products(q: Optional[str] = Query(None, description="Search query for product name or category")):
    recommender = get_recommender()
    if q:
        return recommender.search_products(q, limit=50)
    return recommender.products.to_dict(orient="records")


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    recommender = get_recommender()
    product = recommender.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    recommender = get_recommender()
    user = recommender.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/recommend/popular", response_model=List[Recommendation])
def recommend_popular():
    recommender = get_recommender()
    products = recommender.popularity_recommendations(limit=10)
    return [Recommendation(**{**p, "score": float(p["sales"] * 0.1 + p["rating"])}) for p in products]


@app.get("/recommend/user/{user_id}", response_model=List[Recommendation])
def user_recommendations(user_id: int):
    recommender = get_recommender()
    if recommender.get_user(user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    products = recommender.hybrid_recommendations(user_id, limit=10)
    return [Recommendation(**{**p, "score": float(p["rating"]), "explanation": recommender.explain_recommendation(user_id, p["product_id"])}) for p in products]


@app.get("/recommend/product/{product_id}", response_model=List[Recommendation])
def similar_product_recommendations(product_id: int):
    recommender = get_recommender()
    if recommender.get_product(product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    products = recommender.get_similar_products(product_id, limit=6)
    return [Recommendation(**{**p, "score": float(score), "explanation": "Similar product based on category and description."}) for p, score in zip(products, [1.0] * len(products))]


@app.get("/dashboard/{user_id}", response_model=DashboardResponse)
def dashboard(user_id: int):
    recommender = get_recommender()
    result = recommender.get_dashboard(user_id, limit=8)
    return DashboardResponse(
        user=User(**result["user"]),
        recommendations=[Recommendation(**{**p, "score": float(p.get("rating", 0)), "explanation": recommender.explain_recommendation(user_id, p["product_id"])}) for p in result["recommendations"]],
        recent_activity=result["recent_activity"],
        trending_products=[Recommendation(**{**p, "score": float(p.get("rating", 0)), "explanation": "Trending product."}) for p in result["trending_products"]],
    )


@app.get("/trending", response_model=List[Recommendation])
def trending_products():
    recommender = get_recommender()
    products = recommender.get_trending_products(limit=10)
    return [Recommendation(**{**p, "score": float(p["rating"]), "explanation": "Trending right now."}) for p in products]
