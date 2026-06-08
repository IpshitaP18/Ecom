from backend.database import _load_official_dataset

products, users, ratings, views = _load_official_dataset()
print('products', len(products))
print('users', len(users))
print('ratings', len(ratings))
print('views', len(views))
print(products[:2])
print(users[:2])
