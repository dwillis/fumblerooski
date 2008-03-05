from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.syndication.feeds import Feed
from operator import itemgetter
from fumblerooski.recruits.models import SchoolType, City, School, Player, Outcome, Signing, Year
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State, Game

def position_index(request):
    position_list = Position.objects.all().order_by('name')
    return render_to_response('recruits/positions.html', {'position_list': position_list})

def position_detail(request, pos, year=2008):
    if year=='all':
        year=None
    else:
        year=year
    try:
        position = Position.objects.get(abbrev=pos.upper())
    except:
        raise Http404
    player_list = Player.objects.filter(position__abbrev=pos.upper())
    total = player_list.count()
    if year == None:
        current_signee_list = Signing.objects.select_related().filter(player__position__abbrev=pos.upper()).order_by('recruits_player.last_name')
    else:
        current_signee_list = Signing.objects.select_related().filter(player__position__abbrev=pos.upper(),year=year).order_by('recruits_player.last_name')
    current_signee_count = current_signee_list.count()
    signee_list = Signing.objects.select_related().filter(player__position__abbrev=pos.upper()).order_by('recruits_player.last_name')
    high_schools = {}
    for player in player_list:
        for hs in player.school.filter(school_type=1):
            high_schools[hs.id] = high_schools.get(hs.id, 0) +1
        top_high_schools = sorted(high_schools.iteritems(), key=itemgetter(1), reverse=True)
    t_h = []
    for school, number in top_high_schools[:5]:
        s = School.objects.get(id=school)
        s.number = number
        t_h.append(s)
    return render_to_response('recruits/position_detail.html', {'year': year, 'position': position, 'total': total, 'current_signee_list': current_signee_list, 'current_signee_count': current_signee_count, 'top_high_schools': t_h})

def team_detail(request, team):
    try:
        t = College.objects.get(slug=team)
        recruit_list = Signing.objects.select_related().filter(school=t)
        recruit_total = recruit_list.count()
        year_list = Year.objects.all().order_by('-id')
        position_list = Position.objects.all().order_by('name')
        recent_signing_list = Signing.objects.select_related().filter(school=t).order_by('-id')
    except:
        t = College.objects.filter(slug__startswith=team[:2])
        return render_to_response('recruits/team_detail.html', {'team': t})
    states = {}
    for player in recruit_list:
        states[player.player.home_state_id] = states.get(player.player.home_state_id, 0) +1
    top_states = sorted(states.iteritems(), key=itemgetter(1), reverse=True)
    t_s = []
    for state, number in top_states[:5]:
        s = State.objects.get(id=state)
        s.number = number
        t_s.append(s)
    return render_to_response('recruits/team_detail.html', {'team': t, 'recruit_total': recruit_total, 'year_list': year_list, 'top_states': t_s, 'position_list': position_list, 'recent_signing_list': recent_signing_list[:5]})

def team_detail_year(request, team, year):
    try:
        t = College.objects.get(slug=team)
        recruit_list = Signing.objects.select_related().filter(school=t, year=year).order_by('recruits_player.last_name')
        recruit_total = recruit_list.count()
        year_list = Year.objects.all().order_by('-id')
        outcome_list = Outcome.objects.all()
    except:
        nt = College.objects.filter(slug__startswith=team[:2])
        return render_to_response('recruits/team_detail_year.html', {'team': nt})
    return render_to_response('recruits/team_detail_year.html', {'team': t, 'recruit_list': recruit_list, 'outcome_list': outcome_list or None, 'recruit_total': recruit_total or None, 'year_list': year_list or None, 'year': year or None})

def state_index(request):
    state_list = State.objects.all().order_by('name')
    return render_to_response('recruits/state_index.html', {'state_list': state_list})

def team_detail_position(request, team, pos):
    try:
        t = College.objects.get(slug=team)
        p = Position.objects.get(abbrev=pos)
        recruit_list = Signing.objects.select_related().filter(school=t, player__position=p).order_by('-year', 'recruits_player.last_name')
        outcome_list = Outcome.objects.all()
    except:
        nt = College.objects.filter(slug__startswith=team[:2])
        return render_to_response('recruits/team_detail_position.html', {'team': nt})
    return render_to_response('recruits/team_detail_position.html', {'team': t, 'position': p, 'recruit_list': recruit_list, 'outcome_list': outcome_list})

def state_detail(request, state):
    try:
        st = State.objects.get(id=state.upper())
    except:
        nst = State.objects.filter(id__startswith=state[0].upper())
        return render_to_response('recruits/state_detail.html', {'nst': nst})
    player_list = Player.objects.select_related().filter(home_state=st)
    player_total = player_list.count()
    state_colleges = College.objects.filter(state=st).order_by('name')
    recent_signing_list = Signing.objects.select_related().filter(player__home_state=st).order_by('-id')
    colleges, high_schools = {}, {}
    for player in player_list:
        for signing in player.signing_set.all():
            colleges[signing.school.id] = colleges.get(signing.school.id, 0) + 1
        top_colleges = sorted(colleges.iteritems(), key=itemgetter(1), reverse=True)
        for hs in player.school.filter(school_type=1):
            high_schools[hs.id] = high_schools.get(hs.id, 0) +1
        top_high_schools = sorted(high_schools.iteritems(), key=itemgetter(1), reverse=True)
    t_c = []
    for college, number in top_colleges[:5]:
        c = College.objects.get(id=college)
        c.number = number
        t_c.append(c)
    t_h = []
    for school, number in top_high_schools[:5]:
        s = School.objects.get(id=school)
        s.number = number
        t_h.append(s)
    return render_to_response('recruits/state_detail.html', {'state': st, 'player_total': player_total, 'top_high_schools': t_h, 'top_colleges': t_c, 'state_colleges': state_colleges, 'recent_signing_list': recent_signing_list[:5]})

def school_detail(request, state, city, school, pos=None):
    try:
        st = State.objects.get(id=state.upper())
    except:
        nst = State.objects.filter(id__startswith=state[0].upper())
        return render_to_response('recruits/school_detail.html', {'nst': nst})
    try:
        c = City.objects.get(slug=city, state=state.upper())
    except:
        nc = City.objects.filter(slug__startswith=city[:3], state=state.upper())
        return render_to_response('recruits/school_detail.html', {'nc': nc, 'state': st})
    try:
        s = School.objects.get(city=c, slug=school)
        oc = Outcome.objects.get(id=3)
        if pos:
            p = Position.objects.get(abbrev=pos)
            player_list = Player.objects.select_related().filter(school=s, position=p).order_by('last_name')
        else:
            player_list = Player.objects.select_related().filter(school=s).order_by('last_name')
            p = None
        player_total = player_list.count()
        if player_total > 1:
            use_plural = True
        else:
            use_plural = False
        positions, colleges = {}, {}
        for player in player_list:
            positions[player.position.id] = positions.get(player.position.id, 0) +1
            for signing in player.signing_set.filter(outcome__isnull=True):
                colleges[signing.school.id] = colleges.get(signing.school.id, 0) + 1
        top_positions = sorted(positions.iteritems(), key=itemgetter(1), reverse=True)
        t_p = []
        for position, number in top_positions[:5]:
            p = Position.objects.get(id=position)
            p.number = number
            t_p.append(p)
        top_colleges = sorted(colleges.iteritems(), key=itemgetter(1), reverse=True)
        t_c = []
        for college, number in top_colleges[:5]:
            c = College.objects.get(id=college)
            c.number = number
            t_c.append(c)
    except:
        ns = School.objects.filter(city=c)
        return render_to_response('recruits/school_detail.html', {'ns': ns, 'city': c})
    return render_to_response('recruits/school_detail.html', {'city': c, 'school': s, 'player_list': player_list, 'player_total': player_total, 'state': st, 'top_positions': t_p, 'top_colleges': t_c, 'position': p, 'use_plural': use_plural})

def city_index(request, state, city):
    try:
        st = State.objects.get(id=state.upper())
    except:
        nst = State.objects.filter(id__startswith=state[0].upper())
        return render_to_response('recruits/city_index.html', {'nst': nst})
    try:
        c = City.objects.get(slug=city, state=state.upper())
    except:
        nc = City.objects.filter(slug__startswith=city[:3], state=state.upper())
        return render_to_response('recruits/city_index.html', {'nc': nc, 'state': st})
    s_t = SchoolType.objects.get(id=1)
    school_list = School.objects.select_related().filter(city=c).order_by('name')
    for school in school_list:
        school.players = Player.objects.filter(school=school).count()
        if school.players == 0:
            school.delete()
        else:
            pass
    return render_to_response('recruits/city_index.html', {'state': st, 'city': c, 'school_list': school_list})

def player_detail(request, slug):
    try:
        player = Player.objects.select_related().get(slug=slug)
    except:
        raise Http404
    return render_to_response('recruits/player_detail.html', {'player': player})

def state_position_index(request, state, pos):
    st = State.objects.get(id=state.upper())
    p = Position.objects.get(abbrev=pos.upper())
    player_list = Player.objects.select_related().filter(home_state=st, position=p).order_by('last_name', 'first_name')
    return render_to_response('recruits/state_position_index.html', {'state': st, 'position': p, 'player_list': player_list})

