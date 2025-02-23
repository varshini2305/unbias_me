import requests
from bs4 import BeautifulSoup


def extract_full_article(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print("Error fetching URL:", e)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-article elements (ads, navigation, scripts, etc.)
    for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form", "noscript"]):
        tag.decompose()

    # Remove ads and sponsored content
    ad_classes = ["ad", "sponsored", "video", "promo", "advertisement", "related-articles"]
    for div in soup.find_all("div", class_=lambda x: x and any(cls in x.lower() for cls in ad_classes)):
        div.decompose()

    # Remove video elements
    for video_tag in soup.find_all(["video", "iframe", "embed"]):
        video_tag.decompose()

    # Unwrap links but keep their text
    for a in soup.find_all("a"):
        a.unwrap()

    # Extract the title
    title = soup.title.string if soup.title else "No title found"

    # Extract article content
    article_tag = soup.find("article")
    if article_tag:
        content = article_tag.get_text(separator="\n", strip=True)
    else:
        main_div = soup.find(
            "div",
            class_=lambda x: x and any(k in x.lower() for k in ["content", "article", "main"]),
        )
        if main_div:
            content = main_div.get_text(separator="\n", strip=True)
        else:
            content = soup.get_text(separator="\n", strip=True)

    return {"title": title, "content": content}


def extract_content_from_url(url):
    

    article_data = extract_full_article(url)
    if article_data:
        return {"title":article_data["title"], "content": article_data["content"]}

test_url = "https://www.cnn.com/2025/02/21/europe/pope-francis-rome-hospital-pneumonia-one-week-intl/index.html"
extract_content_from_url(test_url)