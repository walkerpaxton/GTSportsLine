# In odds/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Game, BetComment
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
    
    context = {
        'games': upcoming_games,
    }
    
    return render(request, 'odds/odds_list.html', context)

def game_detail_view(request, game_id):
    """
    Shows a single game with its odds and allows users to comment on it.
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Get all comments for this game
    comments = game.comments.all()
    
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
    }
    
    return render(request, 'odds/game_detail.html', context)