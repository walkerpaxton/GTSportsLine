from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .models import NewsArticle


NEWS_API_URL = "https://newsapi.org/v2/everything"
NEWS_API_TIMEOUT_SECONDS = 8


def _normalize_published_at(raw_value: str | None) -> datetime | None:
    if not raw_value:
        return None

    parsed = parse_datetime(raw_value)
    if parsed:
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.utc)
        return parsed

    try:
        # Handle potential non-ISO formats by letting datetime parse after replacing Z
        raw_value = raw_value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(raw_value)
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return None


def _fetch_georgia_tech_football_news():
    api_key = getattr(settings, "NEWS_API_KEY", None)
    if not api_key:
        return [], "News service is not configured yet."

    params = {
        "q": '"Georgia Tech" AND ("Yellow Jackets" OR football)',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 12,
        "apiKey": api_key,
    }

    try:
        response = requests.get(
            NEWS_API_URL,
            params=params,
            timeout=NEWS_API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException:
        return [], "Unable to reach the news service right now."

    if payload.get("status") != "ok":
        return [], "Unexpected response from the news service."

    normalized_articles = []
    for article in payload.get("articles", []):
        normalized_articles.append(
            {
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "image_url": article.get("urlToImage"),
                "source": (article.get("source") or {}).get("name"),
                "author": article.get("author"),
                "published_at": _normalize_published_at(article.get("publishedAt")),
            }
        )

    return normalized_articles, None

def news_list(request):
    template_data = {
        'title': 'Georgia Tech Football News'
    }
    
    # Get user-created articles from database
    db_articles = NewsArticle.objects.all()
    
    # Convert database articles to same format as API articles
    db_articles_list = []
    for article in db_articles:
        db_articles_list.append({
            "title": article.title,
            "description": article.content[:200] + "..." if len(article.content) > 200 else article.content,
            "url": f"/news/{article.id}/",  # Link to detail page
            "image_url": None,
            "source": "GTSportsLine",
            "author": article.author.username,
            "published_at": article.created_at,
            "is_db_article": True,  # Flag to identify database articles
            "article_id": article.id,
        })
    
    # Get external news from API
    api_articles, error_message = _fetch_georgia_tech_football_news()
    
    # Add flag to API articles
    for article in api_articles:
        article["is_db_article"] = False
    
    # Combine both, with database articles first
    all_articles = db_articles_list + api_articles
    
    template_data['articles'] = all_articles
    template_data['error_message'] = error_message
    return render(request, 'news/news.html', {'template_data': template_data})

@login_required
def create_news(request):
    template_data = {
        'title': 'Create News Article'
    }
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            article = NewsArticle.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            return redirect('news.list')
    
    return render(request, 'news/create.html', {'template_data': template_data})

def news_detail(request, article_id):
    template_data = {
        'title': 'News Article'
    }
    article = get_object_or_404(NewsArticle, id=article_id)
    template_data['article'] = article
    return render(request, 'news/detail.html', {'template_data': template_data})

@login_required
def delete_news(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    
    # Only allow the author to delete their article
    if request.user != article.author:
        return redirect('news.detail', article_id=article_id)
    
    if request.method == 'POST':
        article.delete()
        return redirect('news.list')
    
    # If GET request, show confirmation page or redirect
    return redirect('news.detail', article_id=article_id)
