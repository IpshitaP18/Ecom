import os
import socket
from urllib.request import urlopen

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
TARGET = os.path.join(DATA_DIR, "Online Retail.xlsx")

os.makedirs(DATA_DIR, exist_ok=True)

socket.setdefaulttimeout(120)

print(f"Downloading Online Retail dataset to {TARGET}")
with urlopen(URL) as response:
    with open(TARGET, "wb") as f:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            f.write(chunk)
print("Download complete")
