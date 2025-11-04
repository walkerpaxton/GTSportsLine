# In odds/urls.py (NEW FILE)

from django.urls import path
from . import views

app_name = 'odds'  # Namespacing

urlpatterns = [
    # This makes it the root of the 'odds' app
    path('', views.odds_list_view, name='odds_list'),
]