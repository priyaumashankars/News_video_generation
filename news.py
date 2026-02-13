import requests
from config import GNEWS_API_KEY

def fetch_news(category: str) -> str:
    url = (
        f"https://gnews.io/api/v4/top-headlines"
        f"?topic={category}&lang=en&token={GNEWS_API_KEY}"
    )

    response = requests.get(url).json()
    articles = response.get("articles", [])

    if not articles:
        return "No major updates today."

    headlines = [a["title"] for a in articles[:5]]
    return " ".join(headlines)
