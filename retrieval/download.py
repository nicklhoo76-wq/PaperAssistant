import requests
import os

def download_pdf(url, filename):
    os.makedirs("pdfs", exist_ok=True)

    filepath = os.path.join("pdfs", filename)

    if not os.path.exists(filepath):
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            with open(filepath, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print("PDF下载失败:", e)
            return None

    return filepath