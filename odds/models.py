from django.db import models

class Game(models.Model):
    """
    Represents a single football game and its odds
    from one specific bookmaker.
    """
    # This ID from the API is crucial for uniqueness
    api_game_id = models.CharField(max_length=100, unique=True)
    
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    game_time = models.DateTimeField()
    
    # --- Odds Fields ---
    # We store these directly on the game
    bookmaker_name = models.CharField(max_length=100)
    last_updated = models.DateTimeField()
    
    # Moneyline
    home_team_moneyline = models.IntegerField(null=True, blank=True)
    away_team_moneyline = models.IntegerField(null=True, blank=True)
    
    # Spread (e.g., -7.5)
    home_team_spread = models.FloatField(null=True, blank=True)
    away_team_spread = models.FloatField(null=True, blank=True)
    
    # Price for the spread (e.g., -110)
    home_team_spread_price = models.IntegerField(null=True, blank=True)
    away_team_spread_price = models.IntegerField(null=True, blank=True)
    
    # Total (Over/Under)
    total_over = models.FloatField(null=True, blank=True)
    total_over_price = models.IntegerField(null=True, blank=True)
    
    total_under = models.FloatField(null=True, blank=True)
    total_under_price = models.IntegerField(null=True, blank=True)

    # --- Past Game Fields ---
    # For showing previous games REMOVED FOR NOW MIGHT COME BACK TO IT
    #home_score = models.IntegerField(null=True, blank=True)
    #away_score = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['game_time'] # Default sort: show earliest games first

    def __str__(self):
        return f"{self.away_team} @ {self.home_team}"
