import requests
import os

def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, "wb") as f:
        f.write(response.content)