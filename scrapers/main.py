import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import *
from fumblerooski.utils import update_college_year
from django.template.defaultfilters import slugify

from fumblerooski.scrapers.games import *
from fumblerooski.scrapers.teams import *

CURRENT_SEASON = 2009

def full_load(year, week):
    """
    Given a year and week, performs a full load of games including all player and game stats.
    >>> full_load(2009, 13)
    """
    game_updater(year, None, week)

def full_nostats_load(year, week):
    """
    Given a year and week, performs a full load of games, but just scores, not player and game stats.
    >>> full_nostats_load(2009, 13)
    """
    game_updater(year, None, week, nostats=True)

def partial_loader(year, id, week):
    """
    Given a year, team id and week, performs a full load beginning with that team, in ascending order.
    >>> partial_loader(2009, 235, 13)
    """
    teams = College.objects.filter(updated=True, id__gte=id).order_by('id')
    game_updater(year, teams, week)


