# In odds/management/commands/fetch_odds.py

import requests
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from odds.models import Game

# --- CONFIGURATION ---
# We'll target NCAAF (College Football)
SPORT_KEY = 'americanfootball_ncaaf'
# We'll only get odds from DraftKings. You can change this to another.
# Other popular keys: 'fanduel', 'betmgm', 'caesars'
BOOKMAKER_KEY = 'draftkings'
# We'll get US odds for moneyline (h2h), spreads, and totals (over/under)
REGIONS = 'us'
MARKETS = 'h2h,spreads,totals'
ODDS_FORMAT = 'american'
OUR_TEAM = 'Georgia Tech Yellow Jackets'


class Command(BaseCommand):
    help = f"Fetches NCAAF odds for {OUR_TEAM} from The Odds API"

    def handle(self, *args, **kwargs):
        self.stdout.write(f"Starting to fetch odds for {OUR_TEAM}...")

        # 1. --- Make the API Request ---
        try:
            api_response = requests.get(
                f'https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/odds',
                params={
                    'api_key': settings.ODDS_API_KEY,
                    'regions': REGIONS,
                    'markets': MARKETS,
                    'oddsFormat': ODDS_FORMAT,
                    'bookmakers': BOOKMAKER_KEY,
                }
            )
            api_response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
            data = api_response.json()
        
        except requests.exceptions.RequestException as e:
            raise CommandError(f"API request failed: {e}")

        if not data:
            self.stdout.write(self.style.WARNING(
                "No game data returned from API. Check your API key and quota."
            ))
            return

        # 2. --- Process the API Data ---
        games_processed = 0
        for game_data in data:
            # Check if our team is in this game
            if OUR_TEAM not in (game_data['home_team'], game_data['away_team']):
                continue  # Skip this game if it's not GT

            api_id = game_data['id']
            home_team = game_data['home_team']
            away_team = game_data['away_team']
            
            # Convert the ISO 8601 timestamp string into a Python datetime object
            # We replace 'Z' with '+00:00' to make it compatible with fromisoformat
            commence_time_str = game_data['commence_time'].replace('Z', '+00:00')
            commence_time_obj = datetime.datetime.fromisoformat(commence_time_str)

            # Find our chosen bookmaker's odds
            bookmaker = self.find_bookmaker(game_data.get('bookmakers', []))
            
            if not bookmaker:
                self.stdout.write(self.style.WARNING(
                    f"Could not find odds from '{BOOKMAKER_KEY}' for game: {api_id}"
                ))
                continue

            # 3. --- Extract and Organize the Odds Data ---
            odds_defaults = {
                'bookmaker_name': bookmaker.get('title', BOOKMAKER_KEY),
                'last_updated': datetime.datetime.fromisoformat(
                    bookmaker['last_update'].replace('Z', '+00:00')
                ),
                'home_team': home_team,
                'away_team': away_team,
            }
            
            # This is complex, but just extracts data from the 'markets' list
            self.parse_market(bookmaker.get('markets', []), 'h2h', odds_defaults)
            self.parse_market(bookmaker.get('markets', []), 'spreads', odds_defaults)
            self.parse_market(bookmaker.get('markets', []), 'totals', odds_defaults)
            
            # 4. --- Save to Database ---
            try:
                game, created = Game.objects.update_or_create(
                    api_game_id=api_id,  # This is the unique key we look for
                    defaults={         # These are the fields to update or create
                        'home_team': home_team,
                        'away_team': away_team,
                        'game_time': commence_time_obj,
                        **odds_defaults  # Unpacks all the odds fields we just parsed
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f"CREATED new game: {game}"
                    ))
                else:
                    self.stdout.write(self.style.NOTICE(
                        f"UPDATED existing game: {game}"
                    ))
                games_processed += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error saving game {api_id}: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Processed {games_processed} game(s) for {OUR_TEAM}."
        ))

    def find_bookmaker(self, bookmakers_list):
        """Helper function to find our bookmaker in the list."""
        for bookmaker in bookmakers_list:
            if bookmaker['key'] == BOOKMAKER_KEY:
                return bookmaker
        return None
    
    def parse_market(self, markets_list, market_key, defaults):
        """
        Helper function to find a market (h2h, spreads, totals) and
        put its data into the 'defaults' dictionary for saving.
        """
        for market in markets_list:
            if market['key'] == market_key:
                outcomes = market.get('outcomes', [])
                
                if market_key == 'h2h':
                    for outcome in outcomes:
                        if outcome['name'] == defaults.get('home_team'):
                            defaults['home_team_moneyline'] = outcome['price']
                        elif outcome['name'] == defaults.get('away_team'):
                            defaults['away_team_moneyline'] = outcome['price']
                
                elif market_key == 'spreads':
                    for outcome in outcomes:
                        if outcome['name'] == defaults.get('home_team'):
                            defaults['home_team_spread'] = outcome['point']
                            defaults['home_team_spread_price'] = outcome['price']
                        elif outcome['name'] == defaults.get('away_team'):
                            defaults['away_team_spread'] = outcome['point']
                            defaults['away_team_spread_price'] = outcome['price']
                
                elif market_key == 'totals':
                    for outcome in outcomes:
                        if outcome['name'] == 'Over':
                            defaults['total_over'] = outcome['point']
                            defaults['total_over_price'] = outcome['price']
                        elif outcome['name'] == 'Under':
                            defaults['total_under'] = outcome['point']
                            defaults['total_under_price'] = outcome['price']
                return # Stop after finding the first matching market