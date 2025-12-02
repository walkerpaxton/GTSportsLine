from django.db import models
from django.utils import timezone

class Game(models.Model):
    """Represents a Georgia Tech football game from the schedule"""
    api_game_id = models.IntegerField(unique=True, null=True, blank=True)
    
    season = models.IntegerField()
    week = models.IntegerField(null=True, blank=True)
    season_type = models.CharField(max_length=20)  # 'regular', 'postseason', etc.
    
    # Teams
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    
    # Game details
    game_date = models.DateTimeField(null=True, blank=True)
    start_time = models.CharField(max_length=50, null=True, blank=True)  # TBD, TBA, etc.
    venue = models.CharField(max_length=200, null=True, blank=True)
    
    # Scores (for completed games)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    
    # Game status
    completed = models.BooleanField(default=False)
    neutral_site = models.BooleanField(default=False)
    
    # Conference game indicator
    conference_game = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['game_date', 'start_time']
    
    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - {self.game_date}"
    
    @property
    def is_georgia_tech_home(self):
        """Check if Georgia Tech is the home team"""
        return "Georgia Tech" in self.home_team or "Yellow Jackets" in self.home_team
    
    @property
    def opponent(self):
        """Get the opponent team name"""
        if self.is_georgia_tech_home:
            return self.away_team
        return self.home_team
