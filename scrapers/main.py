from fumblerooski.college.models import College
from fumblerooski.utils import update_college_year
from fumblerooski.scrapers.games import game_updater

def full_load(year, week):
    """
    Given a year and week, performs a full load of games including all player and game stats.
    >>> full_load(2010, 13)
    """
    game_updater(year, None, week)

def full_nostats_load(year, week):
    """
    Given a year and week, performs a full load of games, but just scores, not player and game stats. Useful for 
    updates on a Saturday before game xml files are available on ncaa.org.
    >>> full_nostats_load(2010, 13)
    """
    game_updater(year, None, week, nostats=True)

def partial_loader(year, id, week):
    """
    Given a year, team id and week, performs a full load beginning with that team, in ascending order of team id.
    >>> partial_loader(2010, 235, 13)
    """
    teams = College.objects.filter(updated=True, id__gte=id).order_by('id')
    game_updater(year, teams, week)


