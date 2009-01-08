from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from fumblerooski.college.models import College, Position, State, Game, Conference, Player, StateForm, CollegeYear, CollegeCoach, GameOffense, GameDefense, Week, City, DriveOutcome, GameDrive, PlayerRush, PlayerPass, PlayerReceiving, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerScoring, PlayerReturn, PlayerFumble, BowlGame, Ranking, RankingType
from fumblerooski.coaches.models import Coach, CoachingJob
import datetime

def coach_index(request):
    two_months_ago = datetime.date.today()-datetime.timedelta(60)
    active_hc = CollegeCoach.objects.filter(job__name='Head Coach', end_date__isnull=True).select_related().order_by('start_date')
    recent_departures = CollegeCoach.objects.filter(job__name='Head Coach', end_date__gte=two_months_ago).select_related().order_by('end_date')
    return render_to_response('coaches/coach_index.html', {'active_coaches': active_hc, 'recent_departures': recent_departures[:10]})

def coach_detail(request, coach):
    c = get_object_or_404(Coach, slug=coach)
    college_list = CollegeCoach.objects.filter(coach=c).order_by('-start_year')
    if college_list[0].end_date == None and college_list[0].end_year == None:
        current_job = college_list[0]
        college_list = college_list[1:]
    else:
        current_job = None
    return render_to_response('coaches/coach_detail.html', {'coach': c, 'college_list': college_list, 'current_job': current_job })
