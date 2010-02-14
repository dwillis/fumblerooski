from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Avg, Sum, Min, Max, Count
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.syndication.feeds import Feed
from django import forms
from django.utils import simplejson
from django.forms.models import modelformset_factory
from operator import itemgetter
from time import strptime
import datetime
from fumblerooski.college.models import *
from fumblerooski.rankings.models import *
from fumblerooski.settings import CURRENT_SEASON

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

