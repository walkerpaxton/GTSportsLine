from django.db import models
from django.contrib.auth.models import User

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

class BetComment(models.Model):
    """Comments on sports bets/games that can be removed by admins if inappropriate"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.game}"

class SavedBet(models.Model):
    """Saved bets/games by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_bets')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'game']  # Prevent duplicate saves
        ordering = ['-saved_at']  # Most recently saved first
    
    def __str__(self):
        return f"{self.user.username} saved {self.game}"
