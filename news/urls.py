from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='news.list'),
    path('create/', views.create_news, name='news.create'),
    path('<int:article_id>/', views.news_detail, name='news.detail'),
    path('<int:article_id>/delete/', views.delete_news, name='news.delete'),
]

