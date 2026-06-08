from surprise import Dataset

print('loaded surprise')
data = Dataset.load_builtin('ml-100k')
print('type:', type(data))
print('dataset dir:', data.dataset_dir)
train = data.build_full_trainset()
print('n_users', train.n_users, 'n_items', train.n_items)
print('first raw rating', next(iter(data.raw_ratings)))
