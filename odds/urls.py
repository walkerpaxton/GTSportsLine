# In odds/urls.py (NEW FILE)

from django.urls import path
from . import views

app_name = 'odds'  # Namespacing

urlpatterns = [
    # This makes it the root of the 'odds' app
    path('', views.odds_list_view, name='odds_list'),
    path('saved/', views.saved_bets_view, name='saved_bets'),
    path('<int:game_id>/', views.game_detail_view, name='game_detail'),
    path('<int:game_id>/save/', views.save_bet_view, name='save_bet'),
]