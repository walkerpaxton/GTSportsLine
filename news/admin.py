from django.contrib import admin
from .models import NewsArticle, Comment

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for managing comments - allows admins to remove inappropriate comments"""
    list_display = ['content_preview', 'author', 'article', 'created_at']
    list_filter = ['created_at', 'article']
    search_fields = ['content', 'author__username', 'article__title']
    actions = ['delete_selected']
    
    def content_preview(self, obj):
        """Show a preview of the comment content (first 50 characters)"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance"""
        qs = super().get_queryset(request)
        return qs.select_related('author', 'article')
