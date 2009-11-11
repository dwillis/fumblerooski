Fumblerooski
=============

Fumblerooski is a college football statistics application written in Python using the Django framework, based on data provided by the NCAA and editor input. Most statistics are from 2000 onward, although some teams have game scores dating back to 1988.

Requirements
------------

  * Python 2.5+ (lower versions may work but are untested.)
  * Django 1.1+ (aggregates)
  * BeautifulSoup (HTML and XML parsing)
  * django-googlecharts (http://github.com/jacobian/django-googlecharts)

Overview
------------

Fumblerooski uses the NCAA's statistics site (http://web1.ncaa.org/mfb/mainpage.jsp?year=2009) as a base - nearly everything game and player-related derives from information parsed or scraped from this site. The NCAA provides game information in XML, but most other elements - rosters, drives and rankings included - are scraped using BeautifulSoup. Coaching information is based on an Excel file provided by the NCAA but supplemented by data entry for assistance coaches and coaching history.