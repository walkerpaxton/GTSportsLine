from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import NewsArticle

def news_list(request):
    template_data = {
        'title': 'Georgia Tech Football News'
    }
    articles = NewsArticle.objects.all()
    template_data['articles'] = articles
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
