# In odds/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Game, BetComment, SavedBet
from .forms import BetCommentForm

def odds_list_view(request):
    """
    Fetches all games that haven't happened yet
    and displays them on the page.
    """
    # Get all games where the game_time is in the future
    upcoming_games = Game.objects.filter(
        game_time__gte=timezone.now()
    ).order_by('game_time') # Show the soonest game first
    
    # Get saved game IDs for the current user
    saved_game_ids = set()
    if request.user.is_authenticated:
        saved_game_ids = set(
            SavedBet.objects.filter(user=request.user)
            .values_list('game_id', flat=True)
        )
    
    context = {
        'games': upcoming_games,
        'saved_game_ids': saved_game_ids,
    }
    
    return render(request, 'odds/odds_list.html', context)

def game_detail_view(request, game_id):
    """
    Shows a single game with its odds and allows users to comment on it.
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Get all comments for this game
    comments = game.comments.all()
    
    # Check if game is saved by current user
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedBet.objects.filter(user=request.user, game=game).exists()
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = BetCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.game = game
            comment.author = request.user
            comment.save()
            return redirect('odds:game_detail', game_id=game_id)
    else:
        form = BetCommentForm()
    
    context = {
        'game': game,
        'comments': comments,
        'comment_form': form,
        'is_saved': is_saved,
    }
    
    return render(request, 'odds/game_detail.html', context)

@login_required
def save_bet_view(request, game_id):
    """
    Toggle save/unsave a bet for the current user.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    game = get_object_or_404(Game, id=game_id)
    saved_bet, created = SavedBet.objects.get_or_create(user=request.user, game=game)
    
    if not created:
        # If it already exists, delete it (unsave)
        saved_bet.delete()
        return JsonResponse({'saved': False, 'message': 'Bet unsaved'})
    else:
        return JsonResponse({'saved': True, 'message': 'Bet saved'})

@login_required
def saved_bets_view(request):
    """
    Display all saved bets for the current user.
    """
    saved_bets = SavedBet.objects.filter(user=request.user).select_related('game')
    games = [saved_bet.game for saved_bet in saved_bets]
    
    context = {
        'games': games,
        'saved_game_ids': set(g.id for g in games),  # For consistency with odds_list
    }
    
    return render(request, 'odds/saved_bets.html', context)