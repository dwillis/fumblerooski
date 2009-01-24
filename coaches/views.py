from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from fumblerooski.college.models import College, Position, State, Game, Conference, Player, StateForm, CollegeYear, CollegeCoach, GameOffense, GameDefense, Week, City, DriveOutcome, GameDrive, PlayerRush, PlayerPass, PlayerReceiving, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerScoring, PlayerReturn, PlayerFumble, BowlGame, Ranking, RankingType
from fumblerooski.coaches.models import Coach, CoachingJob
import datetime

CURRENT_SEASON = 2009

def coach_index(request):
    two_months_ago = datetime.date.today()-datetime.timedelta(60)
    active_hc = CollegeCoach.objects.select_related().filter(jobs__name='Head Coach', end_date__isnull=True, collegeyear__year__exact=CURRENT_SEASON).order_by('-start_date')
    recent_departures = CollegeCoach.objects.select_related().filter(jobs__name='Head Coach', end_date__gte=two_months_ago).order_by('end_date')[:10]
    return render_to_response('coaches/coach_index.html', {'active_coaches': active_hc, 'recent_departures': recent_departures })

def coach_detail(request, coach):
    c = get_object_or_404(Coach, slug=coach)
    college_list = CollegeCoach.objects.filter(coach=c).select_related().order_by('-college_collegeyear.year', '-start_date')
    return render_to_response('coaches/coach_detail.html', {'coach': c, 'college_list': college_list })

def assistant_index(request):
    two_months_ago = datetime.date.today()-datetime.timedelta(60)
    recent_hires = CollegeCoach.objects.select_related().filter(start_date__gte=two_months_ago, end_date__isnull=True, collegeyear__year__exact=CURRENT_SEASON).exclude(jobs__name='Head Coach').order_by('-start_date')[:10]
    recent_departures = CollegeCoach.objects.select_related().filter(end_date__gte=two_months_ago).exclude(jobs__name='Head Coach').order_by('end_date')[:10]
    return render_to_response('coaches/assistant_index.html', {'recent_hires': recent_hires, 'recent_departures': recent_departures })    