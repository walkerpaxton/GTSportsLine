from django.contrib import admin
from .models import Game, BetComment

# Register your models here.
admin.site.register(Game)

@admin.register(BetComment)
class BetCommentAdmin(admin.ModelAdmin):
    """Admin interface for managing bet comments - allows admins to remove inappropriate comments"""
    list_display = ['content_preview', 'author', 'game', 'created_at']
    list_display_links = ['content_preview']
    list_filter = ['created_at', 'game']
    search_fields = ['content', 'author__username', 'game__home_team', 'game__away_team']
    # Note: delete_selected action is available by default in Django admin
    # Admins can delete individual comments via the delete button on the detail page
    # Admins can bulk delete comments by selecting them and using the "Delete selected" action
    
    def content_preview(self, obj):
        """Show a preview of the comment content (first 50 characters)"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance"""
        qs = super().get_queryset(request)
        return qs.select_related('author', 'game')