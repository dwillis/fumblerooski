from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.syndication.feeds import Feed
from django import newforms as forms
from operator import itemgetter
from fumblerooski.recruits.models import SchoolType, City, School, Recruit, Outcome, Signing, Year
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State, Game, Conference, Player, PlayerYear, StateForm, CollegeYear

def homepage(request):
    team_count = College.objects.all().count()
    game_count = Game.objects.all().count()
    return render_to_response('college/homepage.html', {'teams': team_count, 'games': game_count })

def state_index(request):
    form = StateForm()
    return render_to_response('college/state_index.html', {'form': form})

def conference_index(request):
    conference_list = Conference.objects.all().order_by('name')
    return render_to_response('college/conferences.html', {'conference_list': conference_list})

def conference_detail(request, conf):
    c = get_object_or_404(Conference, abbrev=conf)
    team_list = College.objects.filter(conference=c).order_by('name')
    recent_games = Game.objects.filter(team1__conference=c, team2__conference=c).order_by('-date')[:10]
    return render_to_response('college/conference_detail.html', {'conference': c, 'team_list': team_list, 'recent_games':recent_games })

def team_index(request):
    team_list = College.objects.all().order_by('name')
    return render_to_response('college/teams.html', {'team_list': team_list})

def team_detail(request, team):
    t = get_object_or_404(College, slug=team)
    try:
        current_coach = CollegeCoach.objects.get(college=t, end_date__isnull=True)
    except CollegeCoach.DoesNotExist:
        current_coach = None
    college_years = CollegeYear.objects.filter(college=t).order_by('-year')
    game_list = Game.objects.filter(team1=t).order_by('-date')
    opponents = {}
    for game in game_list:
        opponents[game.team2.id] = opponents.get(game.team2.id, 0) +1
    popular_opponents = sorted(opponents.iteritems(), key=itemgetter(1), reverse=True)
    p_o = []
    for team, number in popular_opponents[:10]:
        c = College.objects.get(id=team)
        c.number = number
        p_o.append(c)
    return render_to_response('college/team_detail.html', {'team': t, 'coach': current_coach, 'recent_games': game_list[:10], 'popular_opponents': p_o, 'college_years': college_years})

def team_detail_season(request, team, season):
    t = get_object_or_404(College, slug=team)
    try:
        current_coach = CollegeCoach.objects.get(college=t, end_date__isnull=True)
    except CollegeCoach.DoesNotExist:
        current_coach = None
    season_record = get_object_or_404(CollegeYear, college=t, year=season)
    game_list = Game.objects.filter(team1=t, season=season).order_by('-date')
    return render_to_response('college/team_detail_season.html', {'team': t, 'coach': current_coach, 'season_record': season_record, 'game_list': game_list })

def team_opponents(request, team):
    t = get_object_or_404(College, slug=team)
    game_list = Game.objects.select_related().filter(team1=t).order_by('college_college.name')
    opponents = {}
    for game in game_list:
        opponents[game.team2.id] = opponents.get(game.team2.id, 0) +1
    opponent_dict = sorted(opponents.iteritems(), key=itemgetter(1), reverse=True)
    opp_list = []
    for team, number in opponent_dict:
        c = College.objects.get(id=team)
        c.number = number
        opp_list.append(c)
    return render_to_response('college/team_opponents.html', {'team': t, 'opponent_list': opp_list})

def team_vs(request, team1, team2, outcome=None):
    team_1 = get_object_or_404(College, slug=team1)
    try:
        team_2 = College.objects.get(slug=team2)
        if team_1 == team_2:
            team_2 = None
    except:
        team_2 = None
    if outcome:
        games = Game.objects.filter(team1=team_1, team2=team_2, t1_result=outcome[0].upper()).order_by('-date')
    else:
        games = Game.objects.filter(team1=team_1, team2=team_2).order_by('-date')
    wins = games.filter(t1_result='W').count()
    losses = games.filter(t1_result='L').count()
    ties = games.filter(t1_result='T').count()        
    try:
        last_home_loss = games.filter(t1_game_type='H', t1_result='L')[0]
    except:
        last_home_loss = None
    try:
        last_road_win = games.filter(t1_game_type='A', t1_result='W')[0]
    except:
        last_road_win = None
    return render_to_response('college/team_vs.html', {'team_1': team_1, 'team_2': team_2, 'games': games, 'last_home_loss': last_home_loss, 'last_road_win': last_road_win, 'wins': wins, 'losses': losses, 'ties': ties, 'outcome': outcome })

def coach_detail(request, coach):
    c = get_object_or_404(Coach, slug=coach)
    current_job = CollegeCoach.objects.get(coach=c, end_date__isnull=True)
    college_list = CollegeCoach.objects.filter(coach=c).order_by('-start_date')[1:5]
    return render_to_response('college/coach_detail.html', {'coach': c, 'college_list': college_list, 'current_job': current_job })

def game(request, team1, team2, year):
    team_1 = get_object_or_404(College, slug=team1)
    try:
        team_2 = College.objects.get(slug=team2)
        if team_1 == team_2:
            team_2 = None
    except:
        team_2 = None
    games = Game.objects.filter(team1=team_1, team2=team_2, season=year)
    for game in games:
        if game.season > 2002:
            game.drivechart = True
    return render_to_response('college/game.html', {'team_1': team_1, 'team_2': team_2, 'games': games, 'season': year })

def game_index(request):
    pass # do calendar-based view here

def state_detail(request, state):
    s = get_object_or_404(State, id=state)
    team_list = College.objects.filter(state=s).order_by('name')
    return render_to_response('college/state.html', {'team_list': team_list, 'state': s})

def team_players(request, team, year=2007):
    t = get_object_or_404(College, slug=team)
    player_list = PlayerYear.objects.select_related().filter(team=t, year=year).order_by('college_player.last_name')
    return render_to_response('college/team_players.html', {'team': t, 'year': year, 'player_list': player_list })