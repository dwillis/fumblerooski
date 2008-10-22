from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.syndication.feeds import Feed
from django import forms
from operator import itemgetter
from time import strptime
import datetime
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State, Game, Conference, Player, StateForm, CollegeYear, GameOffense, GameDefense, Week, City, DriveOutcome, GameDrive, PlayerRush, PlayerPass, PlayerReceiving, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense

def homepage(request):
    team_count = College.objects.all().count()
    game_count = Game.objects.all().count()
    upcoming_week = Week.objects.filter(year=2008, end_date__gte=datetime.date.today()).order_by('end_date')[0]
    latest_games = Game.objects.filter(team1_score__gt=0, team2_score__gt=0).order_by('-date')
    return render_to_response('college/homepage.html', {'teams': team_count, 'games': game_count, 'latest_games':latest_games[:10], 'upcoming_week':upcoming_week })

def state_index(request):
    form = StateForm()
    return render_to_response('college/state_index.html', {'form': form})

def season_week(request, season, week):
    week = get_object_or_404(Week, week_num=week, year=season)
    game_list = Game.objects.select_related().filter(week=week, team1__division='B').order_by('date', 'team1')
    return render_to_response('college/season_week.html', {'season': season, 'week': week, 'games': game_list})

def conference_index(request):
    conference_list = Conference.objects.all().order_by('name')
    return render_to_response('college/conferences.html', {'conference_list': conference_list})

def conference_detail(request, conf, season):
    c = get_object_or_404(Conference, abbrev=conf)
    team_list = CollegeYear.objects.filter(conference=c, year=season).select_related().order_by('college_college.name')
    return render_to_response('college/conference_detail.html', {'conference': c, 'team_list': team_list })

def team_index(request):
    team_list = College.objects.filter(updated=True).order_by('name')
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
    player_list = Player.objects.filter(team=t, year=season)
    return render_to_response('college/team_detail_season.html', {'team': t, 'coach': current_coach, 'season_record': season_record, 'game_list': game_list, 'player_list':player_list, 'season':season })

def team_opponents(request, team):
    t = get_object_or_404(College, slug=team)
    game_list = Game.objects.filter(team1=t).select_related().order_by('college_college.name')
    opponents = {}
    for game in game_list:
        print game.team2.id
        opponents[game.team2.id] = opponents.get(game.team2.id, 0) +1
    opponent_dict = sorted(opponents.iteritems(), key=itemgetter(1), reverse=True)
    opp_list = []
    for team, number in opponent_dict:
        c = College.objects.get(id=team)
        c.number = number
        opp_list.append(c)
    return render_to_response('college/team_opponents.html', {'team': t, 'opponent_list': opp_list})

def team_first_downs(request, team):
    t = get_object_or_404(College, slug=team)
    offense_list = GameOffense.objects.select_related(depth=1).filter(team=t).order_by('-college_game.date')
    most = offense_list.order_by('-first_downs_total')[0]
    least = offense_list.order_by('first_downs_total')[0]
    return render_to_response('college/first_downs.html', {'team': t, 'offense_list': offense_list, 'most': most, 'least': least })

def team_penalties(request, team):
    t = get_object_or_404(College, slug=team)
    least = GameOffense.objects.select_related(depth=1).filter(team=t).order_by('penalties')[0]
    most = least.reverse()[0]
    return render_to_response('college/first_downs.html', {'team': t, 'most': most, 'least': least })

def team_offense(request, team):
    t = get_object_or_404(College, slug=team)
    return render_to_response('college/offense.html', {'team': t })

def team_offense_rushing(request, team):
    t = get_object_or_404(College, slug=team)
    offense = GameOffense.objects.select_related(depth=1).filter(team=t).order_by('-rush_net')
    return render_to_response('college/offense_rushing.html', {'team': t, 'offense_list':offense[:10] })

def team_defense(request, team):
    t = get_object_or_404(College, slug=team)
    return render_to_response('college/defense.html', {'team': t })

def team_passing(request, team):
    t = get_object_or_404(College, slug=team)
    
    return render_to_response('college/team_passing.html', {'team': t, })

def team_first_downs_category(request, team, category):
    t = get_object_or_404(College, slug=team)
    cat = category.title()
    cat_key = 'first_downs_'+category
    offense_list = GameOffense.objects.select_related(depth=1).filter(team=t).order_by('-college_game.date')
    least = offense_list.order_by(cat_key)
    most = least.reverse()
    return render_to_response('college/first_downs_category.html', {'team': t, 'offense_list': offense_list, 'most': most.values(cat_key)[0][cat_key], 'm_game': most[0], 'least': least.values(cat_key)[0][cat_key], 'l_game': least[0], 'category': cat })

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

def game(request, team1, team2, year, month, day):
    team_1 = get_object_or_404(College, slug=team1)
    try:
        team_2 = College.objects.get(slug=team2)
        if team_1 == team_2:
            team_2 = None
    except:
        team_2 = None
    
    date = datetime.date(int(year), int(month), int(day))
    game = get_object_or_404(Game, team1=team_1, team2=team_2, date=date)
    try:
        game_offense = GameOffense.objects.get(game=game, team=team_1)
    except:
        game_offense = None
    try:
        game_defense = GameDefense.objects.get(game=game, team=team_1)
    except:
        game_defense = None
    try:
        drives = GameDrive.objects.get(game=game, team=team_1)
    except:
        drives = None
    try:
        player_rushing = PlayerRush.objects.filter(game=game, player__team=team_1).order_by('-net')
    except:
        player_rushing = None
    try:
        player_passing = PlayerPass.objects.filter(game=game, player__team=team_1).order_by('-yards')
    except:
        player_passing = None
    try:
        player_receiving = PlayerReceiving.objects.filter(game=game, player__team=team_1).order_by('-yards')
    except:
        player_receiving = None
    try:
        player_tackles = PlayerTackle.objects.filter(game=game, player__team=team_1).order_by('-unassisted_tackles')[:5]
    except:
        player_tackles = None
    try:
        player_tacklesloss = PlayerTacklesLoss.objects.filter(game=game, player__team=team_1).order_by('-unassisted_tackles_for_loss')
    except:
        player_tacklesloss = None
    try:
        player_passdefense = PlayerPassDefense.objects.filter(game=game, player__team=team_1).order_by('-interceptions')
    except:
        player_passdefense = None
    return render_to_response('college/game.html', {'team_1': team_1, 'team_2': team_2, 'game': game, 'offense': game_offense, 'defense': game_defense, 'drives': drives, 'player_rushing': player_rushing, 'player_passing': player_passing, 'player_receiving':player_receiving, 'player_tackles':player_tackles, 'player_tacklesloss':player_tacklesloss, 'player_passdefense':player_passdefense })

def game_drive(request, team1, team2, year, month, day):
    team_1 = get_object_or_404(College, slug=team1)
    try:
        team_2 = College.objects.get(slug=team2)
        if team_1 == team_2:
            team_2 = None
    except:
        team_2 = None
    
    date = datetime.date(int(year), int(month), int(day))
    game = get_object_or_404(Game, team1=team_1, team2=team_2, date=date)
    try:
        drives = GameDrive.objects.filter(game=game, team=team_1).order_by('drive')
    except:
        drives = None
    return render_to_response('college/game_drives.html', {'team_1': team_1, 'team_2': team_2, 'game': game, 'drives': drives })


def game_index(request):
    pass # do calendar-based view here

def undefeated_teams(request, season):
    unbeaten = CollegeYear.objects.select_related().filter(college__updated=True, year=int(season), losses=0, wins__gt=0).order_by('college_college.name', '-wins')
    return render_to_response('college/undefeated.html', {'teams': unbeaten, 'season':season})

def state_detail(request, state):
    s = get_object_or_404(State, id=state)
    team_list = College.objects.filter(state=s).order_by('name')
    return render_to_response('college/state.html', {'team_list': team_list, 'state': s})

def team_players(request, team, season):
    t = get_object_or_404(College, slug=team)
    player_list = Player.objects.filter(team=t, year=season)
    return render_to_response('college/team_players.html', {'team': t, 'year': season, 'player_list': player_list })

def team_by_cls(request, team, year, cl):
    t = get_object_or_404(College, slug=team)
    cy = get_object_or_404(CollegeYear, team=t, year=season)
    player_list = Player.objects.filter(team=t, year=season, status=cl)
    return render_to_response('college/team_class.html', {'team':t, 'year': year, 'cls': cl, 'player_list':player_list })

def player_detail(request, team, season, player):
    t = get_object_or_404(College, slug=team)
    cy = get_object_or_404(CollegeYear, college=t, year=season)
    p = Player.objects.get(team=t, year=season, slug=player)
    ps = PlayerScoring.objects.filter(player=p).select_related().order_by('-college_game.date')
    pret = PlayerReturn.objects.filter(player=p).select_related().order_by('-college_game.date')
    pf = PlayerFumble.objects.filter(player=p).select_related().order_by('-college_game.date')
    if p.position.position_type == 'O':
        pr = PlayerRush.objects.filter(player=p).select_related().order_by('-college_game.date')
        pp = PlayerPass.objects.filter(player=p).select_related().order_by('-college_game.date')
        prec = PlayerReceiving.objects.filter(player=p).select_related().order_by('-college_game.date')
    elif p.position.position_type == 'D':
        pt = PlayerTackle.objects.filter(player=p).select_related().order_by('-college_game.date')
        ptfl = PlayerTacklesLoss.objects.filter(player=p).select_related().order_by('-college_game.date')
        ppd = PlayerPassDefense.objects.filter(player=p).select_related().order_by('-college_game.date')
    other_seasons = Player.objects.filter(team=t, slug=p.slug).exclude(year=season).order_by('year')
    return render_to_response('college/player_detail.html', {'team': t, 'year': season, 'player': p, 'other_seasons': other_seasons, 'scoring': ps, 'returns': pret, 'fumbles': pf, 'rushing': pr or None, 'passing':pp or None, 'receiving': prec or None, 'tackles':pt or None, 'tacklesloss': ptfl or None, 'passdefense':ppd or None })
