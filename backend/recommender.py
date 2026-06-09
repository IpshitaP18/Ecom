import math
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.database import create_connection, get_sample_data, load_table

try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import train_test_split
except ImportError:
    Dataset = None
    Reader = None
    SVD = None
    train_test_split = None


class EcommerceRecommender:
    def __init__(self):
        get_sample_data()
        self.conn = create_connection()
        self.products = load_table(self.conn, "products")
        self.users = load_table(self.conn, "users")
        self.ratings = load_table(self.conn, "ratings")
        self.views = load_table(self.conn, "views")
        self.tfidf_matrix = self._build_tfidf_matrix()
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        self.collab_model = self._build_collaborative_model()

    def _build_tfidf_matrix(self) -> np.ndarray:
        text = self.products["name"] + " " + self.products["category"] + " " + self.products["description"]
        vectorizer = TfidfVectorizer(stop_words="english")
        return vectorizer.fit_transform(text)

    def _build_collaborative_model(self):
        if Dataset is None or Reader is None or SVD is None:
            return None
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings[["user_id", "product_id", "rating"]], reader)
        trainset = data.build_full_trainset()
        model = SVD(n_factors=20, n_epochs=25, random_state=42)
        model.fit(trainset)
        return model

    def get_product(self, product_id: int) -> Optional[dict]:
        product = self.products[self.products["product_id"] == product_id]
        if product.empty:
            return None
        return product.iloc[0].to_dict()

    def get_user(self, user_id: int) -> Optional[dict]:
        user = self.users[self.users["user_id"] == user_id]
        if user.empty:
            return None
        return user.iloc[0].to_dict()

    def search_products(self, query: str, limit: int = 12) -> List[dict]:
        query = query.lower()
        matches = self.products[
            self.products.apply(
                lambda row: query in row["name"].lower()
                or query in row["category"].lower()
                or query in row["description"].lower(),
                axis=1,
            )
        ]
        return matches.head(limit).to_dict(orient="records")

    def popularity_recommendations(self, limit: int = 10) -> List[dict]:
        popular = self.products.sort_values(by=["sales", "rating"], ascending=[False, False])
        return popular.head(limit).to_dict(orient="records")

    def get_similar_products(self, product_id: int, limit: int = 6) -> List[dict]:
        product_index = self.products.index[self.products["product_id"] == product_id]
        if product_index.empty:
            return []
        idx = product_index[0]
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i for i, score in similarity_scores[1 : limit + 1]]
        return self.products.iloc[top_indices].to_dict(orient="records")

    def collaborative_recommendations(self, user_id: int, limit: int = 10) -> List[dict]:
        if self.collab_model is None:
            return self.popularity_recommendations(limit)

        rated_products = self.ratings[self.ratings["user_id"] == user_id]["product_id"].tolist()
        candidate_ids = [pid for pid in self.products["product_id"].tolist() if pid not in rated_products]
        predictions = []
        for pid in candidate_ids:
            estimate = self.collab_model.predict(uid=user_id, iid=pid).est
            predictions.append((pid, estimate))
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_pids = [pid for pid, _ in predictions[:limit]]
        return self.products[self.products["product_id"].isin(top_pids)].to_dict(orient="records")

    def hybrid_recommendations(self, user_id: int, product_id: Optional[int] = None, limit: int = 8) -> List[dict]:
        if product_id is None:
            collaborative = self.collaborative_recommendations(user_id, limit)
            popular = self.popularity_recommendations(limit)
            merged = pd.concat([pd.DataFrame(collaborative), pd.DataFrame(popular)])
            unique = merged.drop_duplicates(subset=["product_id"]).head(limit)
            return unique.to_dict(orient="records")

        content = self.get_similar_products(product_id, limit)
        collaborative = self.collaborative_recommendations(user_id, limit)
        merged = pd.concat([pd.DataFrame(content), pd.DataFrame(collaborative)])
        unique = merged.drop_duplicates(subset=["product_id"]).head(limit)
        return unique.to_dict(orient="records")

    def get_trending_products(self, limit: int = 8) -> List[dict]:
        trends = self.products.assign(trend_score=self.products["sales"] * 0.7 + self.products["rating"] * 10)
        return trends.sort_values(by="trend_score", ascending=False).head(limit).to_dict(orient="records")

    def get_recent_activity(self, user_id: int) -> List[str]:
        user_views = self.views[self.views["user_id"] == user_id]
        if user_views.empty:
            return ["New user: no activity logged yet."]
        recent_ids = user_views["product_id"].tail(5).tolist()
        products = self.products[self.products["product_id"].isin(recent_ids)]
        return [f"Viewed {row['name']}" for _, row in products.iterrows()]

    def explain_recommendation(self, user_id: int, product_id: int) -> str:
        user = self.get_user(user_id)
        product = self.get_product(product_id)
        if not user or not product:
            return "Recommendation generated using collaborative and content signals."
        return f"Recommended because you previously liked products in {user['preferences']} and this item matches your browsing history."

    def get_dashboard(self, user_id: int, limit: int = 8) -> dict:
        user = self.get_user(user_id)
        if user is None:
            return {
                "user": None,
                "recommendations": [],
                "recent_activity": ["User not found."],
                "trending_products": self.get_trending_products(limit),
            }

        recommendations = self.hybrid_recommendations(user_id, limit=limit)
        return {
            "user": user,
            "recommendations": recommendations,
            "recent_activity": self.get_recent_activity(user_id),
            "trending_products": self.get_trending_products(limit),
        }
