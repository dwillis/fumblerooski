Fumblerooski
=============

Fumblerooski is a college football statistics application written in Python using the Django framework, based on data provided by the NCAA and editor input. Most statistics are from 2000 onward, although some teams have game scores dating back to 1988.

Requirements
------------

  * Python 2.5+ (lower versions may work but are untested.)
  * Django 1.1+ (aggregates support required)
  * BeautifulSoup (HTML and XML parsing)
  * django-googlecharts (http://github.com/jacobian/django-googlecharts)

Overview
------------

Fumblerooski uses the NCAA's statistics site (http://web1.ncaa.org/mfb/mainpage.jsp?year=2009) as a base - nearly everything game and player-related derives from information parsed or scraped from this site. The NCAA provides game information in XML, but most other elements - rosters, drives and rankings included - are scraped using BeautifulSoup. Coaching information is based on an Excel file provided by the NCAA but supplemented by data entry for assistant coaches and coaching history back to 2000.

Structure
------------

Fumblerooski is divided into several app or app-like structures. The main one is the college app, which contains most of the models and views, including those related to teams, games, coaches and players. The rankings and scrapers are split into their own directories as well, along with small API and blog apps.

Loaders
------------

Information from the NCAA is scraped using the ncaa_loader.py file, and is presently very tied into the rest of the app, so running the loaders independent of the college app will not produce the desired effect (and will produce lots of errors). The NCAA produces an XML file for each completed game, but the remainder of the information used by Fumblerooski, including schedules, rosters and rankings are parsed using BeautifulSoup. 

The main scraper library has three functions: full_load, full_nostats_load and partial_loader. Because of the need to scrape the HTML tables for an entire season, each of the loaders loops through each team marked to be updated (updated=True) and parses the schedule/results information. The full_load also creates drive and player stats, but those are not available until up to 12-15 hours after the end of the game, so a nostats load only records the score. Normally the full_load can be run on a Sunday afternoon to capture all of Saturday's games. It's also recommended that the load_roster scraper be run after a full_load, as it updates the number of games a player has played in. Rankings also tend to be updated on Sundays, so the team and player rankings can be run then, too.
