import requests
from django.conf import settings
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import datetime

from .models import Game

SCHEDULE_API_URL = "https://api.collegefootballdata.com"
SCHEDULE_API_TIMEOUT_SECONDS = 10
GEORGIA_TECH_TEAM = "Georgia Tech"


def _normalize_game_date(raw_value: str | None) -> datetime | None:
    """Normalize game date from API response"""
    if not raw_value:
        return None
    
    # Try parsing as datetime
    parsed = parse_datetime(raw_value)
    if parsed:
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.utc)
        return parsed
    
    # Try ISO format
    try:
        raw_value = raw_value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(raw_value)
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return None


def _fetch_georgia_tech_schedule(year=None):
    """Fetch Georgia Tech football schedule from College Football Data API"""
    api_key = getattr(settings, "SCHEDULE_API_KEY", None)
    if not api_key:
        return [], "Schedule service is not configured yet."
    
    # Use current year if not specified
    if year is None:
        year = timezone.now().year
    
    # College Football Data API uses Bearer token authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Endpoint to get games for a specific team
    # We'll use the games endpoint with team filter
    url = f"{SCHEDULE_API_URL}/games"
    
    params = {
        "year": year,
        "team": GEORGIA_TECH_TEAM,
        "seasonType": "both",  # Get both regular and postseason
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=SCHEDULE_API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        games_data = response.json()
    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        if e.response.status_code == 401:
            return [], "Authentication failed. Please check your SCHEDULE_API_KEY."
        elif e.response.status_code == 403:
            return [], "Access forbidden. Please check your API key permissions."
        elif e.response.status_code == 404:
            return [], "Schedule endpoint not found. Please check the API documentation."
        else:
            return [], f"API error ({e.response.status_code}): {str(e)}"
    except requests.exceptions.RequestException as e:
        return [], f"Unable to reach the schedule service: {str(e)}"
    
    if not isinstance(games_data, list):
        return [], f"Unexpected response from the schedule service. Received: {type(games_data).__name__}"
    
    # Normalize and process games
    normalized_games = []
    for game in games_data:
        # Handle both snake_case and camelCase field names
        # College Football Data API typically uses camelCase
        home_team = game.get("homeTeam") or game.get("home_team") or ""
        away_team = game.get("awayTeam") or game.get("away_team") or ""
        start_date = game.get("startDate") or game.get("start_date")
        start_time = game.get("startTime") or game.get("start_time")
        start_time_tbd = game.get("startTimeTbd") or game.get("start_time_tbd", False)
        venue = game.get("venue") or ""
        home_points = game.get("homePoints") or game.get("home_points")
        away_points = game.get("awayPoints") or game.get("away_points")
        completed = game.get("completed", False)
        neutral_site = game.get("neutralSite") or game.get("neutral_site", False)
        conference_game = game.get("conferenceGame") or game.get("conference_game", False)
        
        # Determine if GT is home or away
        is_home = "Georgia Tech" in home_team or "Yellow Jackets" in home_team
        
        normalized_games.append({
            "api_game_id": game.get("id"),
            "season": game.get("season", year),
            "week": game.get("week"),
            "season_type": game.get("season_type") or game.get("seasonType", "regular"),
            "home_team": home_team,
            "away_team": away_team,
            "game_date": _normalize_game_date(start_date),
            "start_time": "TBD" if start_time_tbd else (start_time or None),
            "venue": venue,
            "home_score": home_points,
            "away_score": away_points,
            "completed": completed,
            "neutral_site": neutral_site,
            "conference_game": conference_game,
        })
    
    return normalized_games, None


def schedule_list(request):
    """Display Georgia Tech football schedule"""
    template_data = {
        'title': 'Georgia Tech Football Schedule'
    }
    
    # Get year from request, default to current year
    year = request.GET.get('year')
    if year:
        try:
            year = int(year)
        except ValueError:
            year = None
    
    # Fetch schedule from API
    games, error_message = _fetch_georgia_tech_schedule(year)
    
    template_data['games'] = games
    template_data['error_message'] = error_message
    template_data['selected_year'] = year or timezone.now().year
    
    # Get available years (current year and next year for future schedules)
    current_year = timezone.now().year
    template_data['available_years'] = list(range(current_year - 1, current_year + 2))
    
    return render(request, 'schedule/schedule.html', {'template_data': template_data})
