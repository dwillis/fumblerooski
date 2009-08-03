from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Avg, Sum, Min, Max, Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.syndication.feeds import Feed
from django import forms
from operator import itemgetter
from time import strptime
import datetime
from fumblerooski.college.models import College, CollegeCoach, Position, State, Game, Conference, Player, StateForm, CollegeYear, GameOffense, GameDefense, Week, City, DriveOutcome, GameDrive, PlayerRush, PlayerPass, PlayerReceiving, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerScoring, PlayerReturn, PlayerFumble, BowlGame, Ranking, RankingType, PlayerGame, PlayerSummary
from fumblerooski.coaches.models import Coach, CoachingJob

def homepage(request):
    team_count = College.objects.all().count()
    game_count = Game.objects.all().count()
    try:
        upcoming_week = Week.objects.filter(year=2008, end_date__gte=datetime.date.today()).order_by('end_date')[0]
    except:
        upcoming_week = None
    latest_games = Game.objects.filter(team1_score__gt=0, team2_score__gt=0).order_by('-date')
    return render_to_response('college/homepage.html', {'teams': team_count, 'games': game_count, 'latest_games':latest_games[:10], 'upcoming_week':upcoming_week })

def state_index(request):
    if request.method == 'POST':
        if request.POST.has_key('name'):
            abbrev = request.POST['name']
            try:
                state = State.objects.get(id=abbrev)
                college_list = College.objects.filter(updated=True, state=state).order_by('name')
                form = StateForm(request.POST)
            except:
                college_list = None
                form = StateForm()
    else:
        form = StateForm()
        college_list = None
    return render_to_response('college/state_index.html', {'form': form, 'college_list': college_list})

def season_week(request, season, week):
    week = get_object_or_404(Week, week_num=week, year=season)
    game_list = Game.objects.select_related().filter(week=week).order_by('date', 'team1')
    return render_to_response('college/season_week.html', {'season': season, 'week': week, 'games': game_list})

def rankings_index(request):
    ranking_list = RankingType.objects.filter(typename='T').order_by('name')
    return render_to_response('college/rankings_index.html', {'ranking_list':ranking_list})

def rankings_season(request, rankingtype, season, div='B', week=None):
    rt = get_object_or_404(RankingType, slug=rankingtype)
    date = datetime.date.today()-datetime.timedelta(days=7)
    if week:
        latest_week = Week.objects.get(year=season, week_num=week)
    else:
        latest_week = Week.objects.filter(year=season, end_date__gte=date, end_date__lte=datetime.date.today()).order_by('end_date')[0]
    other_weeks = Week.objects.filter(year=season).exclude(week_num=latest_week.week_num).exclude(end_date__gte=datetime.date.today()).order_by('end_date')
    rankings_list = Ranking.objects.filter(year=season, ranking_type=rt, week=latest_week, division=div).select_related().order_by('rank')
    return render_to_response('college/rankings_season.html', {'ranking_type': rt, 'rankings_list': rankings_list, 'season':season, 'latest_week':latest_week, 'other_weeks':other_weeks})

def bowl_games(request):
    game_list = BowlGame.objects.all().order_by('name')
    bowl_seasons = Game.objects.filter(is_bowl_game=True).values_list('season', flat=True).distinct()
    return render_to_response('college/bowl_games.html', {'game_list': game_list, 'bowl_seasons': bowl_seasons})

def bowl_game_season(request, season):
    game_list = Game.objects.select_related().filter(is_bowl_game=True, season=season).order_by('date', 'bowl_game__name')
    return render_to_response('college/bowl_game_season.html', {'season': season, 'game_list': game_list})

def bowl_game_detail(request, bowl):
    bg = get_object_or_404(BowlGame, slug=bowl)
    game_list = Game.objects.filter(bowl_game=bg, t1_result='W').order_by('-date')
    return render_to_response('college/bowl_game_detail.html', {'bowl': bg, 'game_list': game_list})

def conference_index(request):
    conference_list = Conference.objects.all().order_by('name')
    return render_to_response('college/conferences.html', {'conference_list': conference_list})

def conference_detail(request, conf, season=None):
    if not season:
        season = datetime.date.today().year
    c = get_object_or_404(Conference, abbrev=conf)
    team_list = CollegeYear.objects.filter(conference=c, year=season).select_related().order_by('college_college.name')
    return render_to_response('college/conference_detail.html', {'conference': c, 'team_list': team_list, 'season':season })

def team_index(request):
    team_list = College.objects.filter(updated=True).order_by('name')
    return render_to_response('college/teams.html', {'team_list': team_list})

def team_detail(request, team):
    t = get_object_or_404(College, slug=team)
    college_years = CollegeYear.objects.filter(college=t).order_by('-year')
    try:
        current_head_coach = CollegeCoach.objects.get(collegeyear=college_years[0], end_date__isnull=True, jobs__name='Head Coach')
    except CollegeCoach.DoesNotExist:
        current_head_coach = None
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
    return render_to_response('college/team_detail.html', {'team': t, 'coach': current_head_coach, 'recent_games': game_list[:10], 'popular_opponents': p_o, 'college_years': college_years})

def team_detail_season(request, team, season):
    t = get_object_or_404(College, slug=team)
    season_record = get_object_or_404(CollegeYear, college=t, year=season)
    try:
        current_coach = CollegeCoach.objects.filter(collegeyear=season_record, end_date__isnull=True, jobs__name='Head Coach').order_by('-start_date')[0]
    except IndexError:
        current_coach = None
    game_list = Game.objects.filter(team1=t, season=season).order_by('-date')
    player_list = Player.objects.filter(team=t, year=season)
    return render_to_response('college/team_detail_season.html', {'team': t, 'coach': current_coach, 'season_record': season_record, 'game_list': game_list, 'player_list':player_list, 'season':season })

def team_bowl_games(request, team):
    t = get_object_or_404(College, slug=team)
    game_list = Game.objects.filter(team1=t, is_bowl_game=True).order_by('-date')
    return render_to_response('college/team_bowl_games.html', {'team': t, 'game_list': game_list })

def team_rankings_season(request, team, season, week=None):
    cy = get_object_or_404(CollegeYear, college__slug=team, year=season)
    date = datetime.date.today()-datetime.timedelta(days=7)
    if week:
        latest_week = Week.objects.get(year=season, week_num=week)
    else:
        # grab the latest week for that season
        latest_week = Week.objects.filter(year=season).order_by('-week_num')[0]
    other_weeks = Week.objects.filter(year=season).exclude(week_num__gte=latest_week.week_num).order_by('end_date')
    latest_rankings = Ranking.objects.filter(college=cy.college, year=season, week=latest_week).select_related().order_by('-college_week.week_num')
    if latest_rankings:
        best = latest_rankings.order_by('rank')[0]
        worst = latest_rankings.order_by('-rank')[0]
    else:
        best, worst = None, None
    return render_to_response('college/team_rankings_season.html', {'season_record': cy, 'latest_rankings': latest_rankings, 'latest_week': latest_week, 'other_weeks': other_weeks, 'best': best, 'worst': worst})

def team_ranking_detail(request, team, season, rankingtype):
    cy = get_object_or_404(CollegeYear, college__slug=team, year=season)
    ranking_type = get_object_or_404(RankingType,slug=rankingtype)
    rankings = Ranking.objects.filter(college=cy.college, year=season, ranking_type=ranking_type).select_related().order_by('college_week.week_num')
    best = rankings.order_by('rank')[0]
    worst = rankings.order_by('-rank')[0]
    ranks = [r.rank for r in rankings]
    weeks = [w.week.week_num for w in rankings]
    return render_to_response('college/team_ranking_detail.html', {'season_record': cy, 'ranking_type': ranking_type, 'rankings': rankings, 'best': best, 'worst': worst, 'ranks': ranks, 'weeks': weeks})

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
    if game.is_conference_game == True:
        conf = CollegeYear.objects.get(college=team_1, year=year).conference
    else:
        conf = None
    try:
        game_offense = GameOffense.objects.get(game=game, team=team_1)
        fd = []
        fd.append(game_offense.first_downs_rushing)
        fd.append(game_offense.first_downs_passing)
        fd.append(game_offense.first_downs_penalty)
    except:
        game_offense = None
        fd = None
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
    return render_to_response('college/game.html', {'team_1': team_1, 'conf': conf, 'team_2': team_2, 'game': game, 'offense': game_offense, 'defense': game_defense, 'drives': drives, 'player_rushing': player_rushing, 'player_passing': player_passing, 'player_receiving':player_receiving, 'player_tackles':player_tackles, 'player_tacklesloss':player_tacklesloss, 'player_passdefense':player_passdefense, 'first_downs': fd })

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

def team_positions(request, team):
    t = get_object_or_404(College, slug=team)
    position_list = Position.objects.all()
    return render_to_response('college/team_positions.html', {'team': t, 'position_list': position_list})

def team_by_cls(request, team, year, cl):
    t = get_object_or_404(College, slug=team)
    cy = get_object_or_404(CollegeYear, team=t, year=season)
    player_list = Player.objects.filter(team=t, year=season, status=cl)
    return render_to_response('college/team_class.html', {'team':t, 'year': year, 'cls': cl, 'player_list':player_list })

def team_position_detail(request, team, season, pos):
    t = get_object_or_404(College, slug=team)
    p = Position.objects.get(abbrev=pos.upper())
    player_list = Player.objects.filter(team=t, position=p, year=season).order_by('-games_played')
    return render_to_response('college/team_position_detail.html', {'team': t, 'position': p, 'season': season, 'player_list': player_list})

def team_class_detail(request, team, season, cls):
    t = get_object_or_404(College, slug=team)
    player_list = Player.objects.filter(team=t, status=cls.upper(), year=season).order_by('-games_played')
    return render_to_response('college/team_class_detail.html', {'team': t, 'class': cls, 'season': season, 'player_list': player_list})

def player_detail(request, team, season, player):
    t = get_object_or_404(College, slug=team)
    cy = get_object_or_404(CollegeYear, college=t, year=season)
    p = Player.objects.get(team=t, year=cy.year, slug=player)
    pg = PlayerGame.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    ps = PlayerScoring.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    pret = PlayerReturn.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    pf = PlayerFumble.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    pr = PlayerRush.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    if pr:
        rush_totals = pr.aggregate(Sum('net'),Sum('gain'),Sum('loss'),Sum('rushes'),Sum('td'))
        rush_tot_avg = float(rush_totals['net__sum'])/float(rush_totals['rushes__sum'])
    else:
        rush_totals = {'rushes__sum': None, 'gain__sum': None, 'loss__sum': None, 'td__sum': None, 'net__sum': None}
        rush_tot_avg = None
    pp = PlayerPass.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    if pp:
        pass_totals = pp.aggregate(Sum('td'), Sum('yards'), Sum('attempts'), Sum('completions'), Sum('interceptions'), Avg('pass_efficiency'))
        comp_pct = float(pass_totals['completions__sum'])/float(pass_totals['attempts__sum'])*100
    else:
        pass_totals = {'interceptions__sum': None, 'td__sum':None, 'attempts__sum': None, 'completions__sum': None, 'yards__sum': None, 'pass_efficiency__avg': None}
        comp_pct = None
    prec = PlayerReceiving.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    if prec:
        rec_totals = prec.aggregate(Sum('receptions'), Sum('yards'), Sum('td'))
        rec_tot_avg = float(rec_totals['yards__sum'])/float(rec_totals['receptions__sum'])
    else:
        rec_totals = {'receptions__sum': None, 'yards__sum': None, 'td__sum': None}
        rec_tot_avg = None
    pt = PlayerTackle.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    ptfl = PlayerTacklesLoss.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    ppd = PlayerPassDefense.objects.filter(player=p, game__season=season).select_related().order_by('-college_game.date')
    other_seasons = Player.objects.filter(team=t, slug=p.slug).exclude(year=season).order_by('-year')
    return render_to_response('college/player_detail.html', {'team': t, 'year': season, 'cy': cy, 'player': p, 'other_seasons': other_seasons, 'scoring': ps, 'returns': pret, 'fumbles': pf, 
        'rushing': pr, 'passing':pp, 'receiving': prec, 'tackles':pt, 'tacklesloss': ptfl, 'passdefense':ppd, 
        'pass_tot_int':pass_totals['interceptions__sum'], 'pass_tot_td':pass_totals['td__sum'], 'pass_tot_attempts': pass_totals['attempts__sum'], 'pass_tot_comps': pass_totals['completions__sum'], 
        'pass_tot_yards': pass_totals['yards__sum'], 'pass_tot_eff': pass_totals['pass_efficiency__avg'], 'rush_tot_rushes': rush_totals['rushes__sum'], 'rush_tot_gains': rush_totals['gain__sum'],
        'rush_tot_loss': rush_totals['loss__sum'], 'rush_tot_td': rush_totals['td__sum'], 'rush_tot_net': rush_totals['net__sum'], 'rush_tot_avg': rush_tot_avg, 'comp_pct':comp_pct, 
        'rec_tot_receptions': rec_totals['receptions__sum'], 'rec_tot_yards': rec_totals['yards__sum'], 'rec_tot_td': rec_totals['td__sum'], 'rec_tot_avg': rec_tot_avg})
