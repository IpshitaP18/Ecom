from typing import List, Optional
from pydantic import BaseModel


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    description: str
    price: float
    rating: float
    sales: int


class User(BaseModel):
    user_id: int
    name: str
    preferences: Optional[str] = None


class Recommendation(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    rating: float
    score: float
    explanation: Optional[str] = None


class DashboardResponse(BaseModel):
    user: User
    recommendations: List[Recommendation]
    recent_activity: List[str]
    trending_products: List[Recommendation]
