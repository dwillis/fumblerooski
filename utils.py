import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import State, College, Game, Coach, Position, Player, PlayerOffense, PlayerDefense, PlayerSpecial, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense

#<td width="200">East Bay High School</td><td width="200">7710 Old Big Bend Road<br>Gibsonton, Florida 33534</td>

def get_florida_hs():
    base_url = 'http://i.fhsaa.org/members/member_info.aspx?school_id='
    pattern = re.compile("""<td width..200.>(.*?)</td><td width..200.>.*?<br>(.*?), Florida""")
    for i in range(1410,2134):
        content = urllib.urlopen(base_url+str(i)).read()
        for school, city in pattern.findall(content):
            st = SchoolType.objects.get(id=1)
            c, created = City.objects.get_or_create(name=city, state='FL')
            s, created = School.objects.get_or_create(name=school, slug=school.replace(' ','-').replace('.','').replace(',','').lower(), city=c, school_type=st)

def get_players(year):
    # accepts a two-digit year, such as 06
    from BeautifulSoup import BeautifulSoup
    base_url = 'http://interact.cstv.com/recruiting/pros_card_content.cfm?sport=football&dbyear=%s&recruit_id=' % year
    f = open('players07.txt','w')
    for i in range(1,4455):
        content = urllib.urlopen(base_url+str(i)).read()
        soup = BeautifulSoup(content)
        player = soup.find('span', {"class":"recHdr"})
        details = soup.findAll('span', {"class":"recStat"})
        try:
            f.write('@'+player.contents[0].replace('&nbsp;','').replace('\n','').replace('\n','')+'|'+details[0].contents[0].replace('&nbsp;','')+'|'+details[1].contents[0].replace('&nbsp;','')[1:][:4].replace('\'','-').replace('"','')+'|'+details[1].contents[0].replace('&nbsp;','')[8:]+'|'+details[5].contents[0].replace('&nbsp;','').replace('\n','')+'|'+details[7].contents[0].replace('&nbsp;','').replace('\n','').split(',')[0].upper()+'|'+details[7].contents[0].replace('&nbsp;','').replace('\n','').split(',')[1][1:]+'|'+details[8].contents[0].replace('&nbsp;','').replace('\n',''))
        except:
            pass


def update_college_year(year):
    teams = College.objects.all()
    for team in teams:
        games = Game.objects.filter(team1=team, season=year)
        results = {'W':0, 'L':0, 'T':0}
        for game in games:
            results[game.t1_result] = results.get(game.t1_result, 0) +1            
        if team.conference:
            conf = Conference.objects.get(id = team.conference_id)
            conf_games = Game.objects.select_related().filter(team1=team, season=year, team2__conference=conf)
            conf_results = {'W':0, 'L':0, 'T':0}
            for conf_game in conf_games:
                conf_results[conf_game.t1_result] = conf_results.get(conf_game.t1_result, 0) +1
            conf_wins = conf_results['W']
            conf_losses = conf_results['L']
            conf_ties = conf_results['T']
        else:
            conf_wins = 0
            conf_losses = 0
            conf_ties = 0
        record, created = CollegeYear.objects.get_or_create(college=team, year=year, wins=results['W'], losses=results['L'], ties=results['T'], conference_wins=conf_wins, conference_losses=conf_losses, conference_ties=conf_ties)


def get_ncaa_games(year):
    pattern = re.compile("""<td width=411 colspan=4><a href="http://web1.ncaa.org/ssLists/orgInfo.do.orgID=(.*)" target=_parent><font size=2 face="helvetica">(.*)</font></a></td>\s*<td></td>\s*<td width=163 colspan=2><font size=2 face="helvetica">(.*?)</font></td>\s*<td></td>\s*<td width=146 colspan=2><font size=2 face="helvetica">(.*?)</font></td>\s*<td></td>\s*<td width=63><font size=2 face="helvetica">(.*?)</font></td>\s*<td></td>\s*<td width=41 colspan=4 align=right><font size=2 face="helvetica">(.*?)</font></td>\s*<td></td>\s*<td width=7><font size=2 face="helvetica">-</font></td>\s*<td></td>\s*<td width=43 colspan=2><font size=2 face="helvetica">(.*?)</font></td>\s*<td></td>""")

    base_url = 'https://goomer.ncaa.org/reports/rwservlet?hidden_run_parameters=p_mfb_schrec&p_sport_code=MFB&v_year=%s&p_orgnum=' % year

    teams = College.objects.all()

    for team in teams:
        html = urllib.urlopen(base_url+str(team.id)).read()
        html = html.replace(' rowspan=2', '') # get rid of code that appears sporadically
        for t2, teamname, type, string_date, result, t1_s, t2_s in pattern.findall(html):
            if t2 == '':
                continue
            teamname = teamname.replace('&nbsp;',' ')
            if type <> 'HOME' and type <> 'AWAY':
                type = 'Neutral'
            strdate = string_date.replace('&nbsp;',' ').replace('.','').upper()
            date = datetime.datetime(*(time.strptime(strdate, '%b %d, %Y')[0:6]))
            t1 = College.objects.get(id=team.id)
            t2, created = College.objects.get_or_create(id=t2, name=teamname)
            if t1_s == '&nbsp;':
                t1_s = int(t1_s.replace('&nbsp;', '0'))
                t2_s = int(t2_s.replace('&nbsp;', '0'))
            g = Game.objects.get_or_create(season=year, team1=t1, team2=t2, date = date, t1_game_type=type[0], t1_result=result[0], team1_score=t1_s, team2_score=t2_s)

def load_recruits():
    import csv
    reader = csv.reader(open("players2007.csv"))
    for row in reader:
        st = State.objects.get(id=row[5])
        p = Position.objects.get(abbrev=row[2])
        pl, created = Player.objects.get_or_create(first_name=row[0], last_name=row[1], pos=p, height=row[3], weight=row[4], home_state=st)
        pl.save()

def load_players(year):
    file = open('csv/DivIA.csv').readlines()
    file = file[1:]
    players = open('players.csv','w')
    for line in file:
        players.write(line)
    players.close()

    reader = csv.reader(open('players.csv'))
    for row in reader:
        y, created = Year.objects.get_or_create(id=year)
        t = College.objects.get(id=row[0])
        pos, created = Position.objects.get_or_create(abbrev=row[5])
        if row[4] == '':
            if row[3] != 'Team':
                first = raw_input("Enter a first name for %s on %s: " % (row[3], row[1]))
                p, created=Player.objects.get_or_create(ncaa_id=row[7], last_name=force_unicode(row[3].upper()), first_name='', first_name_fixed=force_unicode(first.upper()))
            else:
                pass
        else:
            # change to match on id and last_name only?
            p, created=Player.objects.get_or_create(ncaa_id=row[7], last_name=force_unicode(row[3].upper()), first_name=force_unicode(row[4].upper()), first_name_fixed=force_unicode(row[4].upper()))
        py, created = PlayerYear.objects.get_or_create(player=p, team=t, year=y, position=pos, number=row[2], ncaa_number=row[2], status=row[6])



"""
Loader for NCAA game summaries
url format:

http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/DIVISION1.HTML
http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/1200020000827.HTML
"""

def get_summary_links(year):
    """
    Given a year, retrieves urls for weekly game lists and returns all games in a list.
    """
    base_url='http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/' % year
    url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/DIVISION1.HTML" % year
    doc = urllib.urlopen(url).read()
    soup = BeautifulSoup(doc)
    links = soup.findAll("a")[13:]
    link_list = []
    for link in links:
        link_list.append(urljoin(base_url,link['href']))
    l2 = set(link_list)
    newlinks = list(l2)
    return newlinks


def get_game_xml_url(year, links):
    """
    Takes a list generated by get_summary_links() and retrieves the urls of individual game xml files.
    """
    games = []
    base_url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/" % year
    for link in links:
        doc = urllib.urlopen(link).read()
        soup = BeautifulSoup(doc)
        g_list = [a['href'].split("game=")[1] for a in soup.findAll("table")[3].findAll("a")]
        for game in g_list:
            games.append(urljoin(base_url,game))
    return games

def load_ncaa_game_xml(urls):
    """
    Loader for NCAA game xml files
    url format:                year                     year000000tidyearmmdd
    http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/200000000023420000826.xml
    """
    for url in urls:
        doc = urllib.urlopen(url).read()
        soup = BeautifulSoup(doc)
        # replace all interior spaces with 0
        f = soup.findAll(text="&#160;")
        for each in f:
            each.replaceWith("0")
        try:
            t1 = College.objects.get(id = int(soup.teams.home.orgid.contents[0]))
            t2 = College.objects.get(id = int(soup.teams.visitor.orgid.contents[0]))
            d = strptime(soup.gamedate.contents[0], "%m/%d/%y")
            gd = datetime.date(d[0], d[1], d[2])
        except:
            print "Could not find one of the teams"
        try:
            game = Game.objects.get(team1=t1, team2=t2, date=gd)
            game.attendance = soup.attendance.contents[0]
            game.save
            
            home_time = strptime(soup.teams.home.top.contents[0]) or None
            visitor_time = strptime(soup.teams.visitor.top.contents[0]) or None
            
            # home team offense
            home_offense = GameOffense.objects.create(
              game=game, 
              team=t1,
              third_down_attempts=int(soup.teams.home.thirddowns.att.contents[0]),
              third_down_conversions=int(soup.teams.home.thirddowns.conv.contents[0]),
              fourth_down_attempts=int(soup.teams.home.fourthdowns.att.contents[0]),
              fourth_down_conversions=int(soup.teams.home.fourthdowns.conv.contents[0]),
              time_of_possession=home_time,
              first_downs_rushing=int(soup.teams.home.firstdowns.rush.contents[0]),
              first_downs_passing=int(soup.teams.home.firstdowns.contents[3].contents[0]), # can't use "pass"
              first_downs_penalty=int(soup.teams.home.firstdowns.penalty.contents[0]),
              first_downs_total=int(soup.teams.home.firstdowns.total.contents[0]),
              penalties=int(soup.teams.home.penalties.number.contents[0]),
              penalty_yards=int(soup.teams.home.penalties.yards.contents[0]),
              fumbles=int(soup.teams.home.fumbles.number.contents[0]),
              fumbles_lost=int(soup.teams.home.fumbles.lost.contents[0]),
              rushes=int(soup.teams.home.totals.rushing.number.contents[0]),
              rush_gain=int(soup.teams.home.totals.rushing.gain.contents[0]),
              rush_loss=int(soup.teams.home.totals.rushing.loss.contents[0]),
              rush_net=int(soup.teams.home.totals.rushing.net.contents[0]),
              rush_touchdowns=int(soup.teams.home.totals.rushing.td.contents[0]),
              total_plays=int(soup.teams.home.totals.rushing.totplays.contents[0]),
              total_yards=int(soup.teams.home.totals.rushing.totyards.contents[0]),
              pass_attempts=int(soup.teams.home.totals.passing.att.contents[0]),
              pass_completions=int(soup.teams.home.totals.passing.comp.contents[0]),
              pass_interceptions=int(soup.teams.home.totals.passing.int.contents[0]),
              pass_yards=int(soup.teams.home.totals.passing.yards.contents[0]),
              pass_touchdowns=int(soup.teams.home.totals.passing.td.contents[0]),
              receptions=int(soup.teams.home.totals.receiving.number.contents[0]),
              receiving_yards=int(soup.teams.home.totals.receiving.yards.contents[0]),
              receiving_touchdowns=int(soup.teams.home.totals.receiving.td.contents[0]),
              punts=int(soup.teams.home.totals.punt.number.contents[0]),
              punt_yards=int(soup.teams.home.totals.punt.yards.contents[0]),
              punt_returns=int(soup.teams.home.totals.returns.puntnumber.contents[0]),
              punt_return_yards=int(soup.teams.home.totals.returns.puntyards.contents[0]),
              punt_return_touchdowns=int(soup.teams.home.totals.returns.punttd.contents[0]),
              kickoff_returns=int(soup.teams.home.totals.returns.konumber.contents[0]),
              kickoff_return_yards=int(soup.teams.home.totals.returns.koyards.contents[0]),
              kickoff_return_touchdowns=int(soup.teams.home.totals.returns.kotd.contents[0]),
              touchdowns=int(soup.teams.home.totals.scoring.td.contents[0]),
              pat_attempts=int(soup.teams.home.totals.scoring.offkickatt.contents[0]),
              pat_made=int(soup.teams.home.totals.scoring.offkickmade.contents[0]),
              two_point_conversion_attempts=int(soup.teams.home.totals.scoring.offrpatt.contents[0]),
              two_point_conversions=int(soup.teams.home.totals.scoring.offrpmade.contents[0]),
              field_goal_attempts=int(soup.teams.home.totals.scoring.fgatt.contents[0]),
              field_goals_made=int(soup.teams.home.totals.scoring.fgmade.contents[0]),
              points=int(soup.teams.home.totals.scoring.pts.contents[0]),
              )
        
            # home team defense
            home_defense = GameDefense.objects.create(
                game = game,
                team = t1,
                safeties = int(soup.teams.home.totals.scoring.saf.contents[0]),
                unassisted_tackles = int(soup.teams.home.totals.tackles.uatackles.contents[0]),
                assisted_tackles = int(soup.teams.home.totals.tackles.atackles.contents[0]),
                unassisted_tackles_for_loss = int(soup.teams.home.totals.tfl.uatfl.contents[0]),
                assisted_tackles_for_loss = int(soup.teams.home.totals.tfl.atfl.contents[0]),
                tackles_for_loss_yards = int(soup.teams.home.totals.tfl.tflyards.contents[0]),
                unassisted_sacks = int(soup.teams.home.totals.tfl.uasacks.contents[0]),
                assisted_sacks = int(soup.teams.home.totals.tfl.asacks.contents[0]),
                sack_yards = int(soup.teams.home.totals.tfl.sackyards.contents[0]),
                defensive_interceptions = int(soup.teams.home.totals.passdefense.intnumber.contents[0]),
                defensive_interception_yards = int(soup.teams.home.totals.passdefense.intyards.contents[0]),
                defensive_interception_touchdowns = int(soup.teams.home.totals.passdefense.inttd.contents[0]),
                pass_breakups = int(soup.teams.home.totals.passdefense.passbreakups.contents[0]),
                fumbles_forced = int(soup.teams.home.totals.fumbles.fumblesforced.contents[0]),
                fumbles_number = int(soup.teams.home.totals.fumbles.fumblesnumber.contents[0]),
                fumbles_yards = int(soup.teams.home.totals.fumbles.fumblesyards.contents[0]),
                fumbles_touchdowns = int(soup.teams.home.totals.fumbles.fumblestd.contents[0])
            )
        
            # visiting team offense
            visiting_offense = GameOffense.objects.create(
                  game=game, 
                  team=t2,
                  third_down_attempts=int(soup.teams.visitor.thirddowns.att.contents[0]),
                  third_down_conversions=int(soup.teams.visitor.thirddowns.conv.contents[0]),
                  fourth_down_attempts=int(soup.teams.visitor.fourthdowns.att.contents[0]),
                  fourth_down_conversions=int(soup.teams.visitor.fourthdowns.conv.contents[0]),
                  time_of_possession=visitor_time,
                  first_downs_rushing=int(soup.teams.visitor.firstdowns.rush.contents[0]),
                  first_downs_passing=int(soup.teams.visitor.firstdowns.contents[3].contents[0]), # can't use "pass"
                  first_downs_penalty=int(soup.teams.visitor.firstdowns.penalty.contents[0]),
                  first_downs_total=int(soup.teams.visitor.firstdowns.total.contents[0]),
                  penalties=int(soup.teams.visitor.penalties.number.contents[0]),
                  penalty_yards=int(soup.teams.visitor.penalties.yards.contents[0]),
                  fumbles=int(soup.teams.visitor.fumbles.number.contents[0]),
                  fumbles_lost=int(soup.teams.visitor.fumbles.lost.contents[0]),
                  rushes=int(soup.teams.visitor.totals.rushing.number.contents[0]),
                  rush_gain=int(soup.teams.visitor.totals.rushing.gain.contents[0]),
                  rush_loss=int(soup.teams.visitor.totals.rushing.loss.contents[0]),
                  rush_net=int(soup.teams.visitor.totals.rushing.net.contents[0]),
                  rush_touchdowns=int(soup.teams.visitor.totals.rushing.td.contents[0]),
                  total_plays=int(soup.teams.visitor.totals.rushing.totplays.contents[0]),
                  total_yards=int(soup.teams.visitor.totals.rushing.totyards.contents[0]),
                  pass_attempts=int(soup.teams.visitor.totals.passing.att.contents[0]),
                  pass_completions=int(soup.teams.visitor.totals.passing.comp.contents[0]),
                  pass_interceptions=int(soup.teams.visitor.totals.passing.int.contents[0]),
                  pass_yards=int(soup.teams.visitor.totals.passing.yards.contents[0]),
                  pass_touchdowns=int(soup.teams.visitor.totals.passing.td.contents[0]),
                  receptions=int(soup.teams.visitor.totals.receiving.number.contents[0]),
                  receiving_yards=int(soup.teams.visitor.totals.receiving.yards.contents[0]),
                  receiving_touchdowns=int(soup.teams.visitor.totals.receiving.td.contents[0]),
                  punts=int(soup.teams.visitor.totals.punt.number.contents[0]),
                  punt_yards=int(soup.teams.visitor.totals.punt.yards.contents[0]),
                  punt_returns=int(soup.teams.visitor.totals.returns.puntnumber.contents[0]),
                  punt_return_yards=int(soup.teams.visitor.totals.returns.puntyards.contents[0]),
                  punt_return_touchdowns=int(soup.teams.visitor.totals.returns.punttd.contents[0]),
                  kickoff_returns=int(soup.teams.visitor.totals.returns.konumber.contents[0]),
                  kickoff_return_yards=int(soup.teams.visitor.totals.returns.koyards.contents[0]),
                  kickoff_return_touchdowns=int(soup.teams.visitor.totals.returns.kotd.contents[0]),
                  touchdowns=int(soup.teams.visitor.totals.scoring.td.contents[0]),
                  pat_attempts=int(soup.teams.visitor.totals.scoring.offkickatt.contents[0]),
                  pat_made=int(soup.teams.visitor.totals.scoring.offkickmade.contents[0]),
                  two_point_conversion_attempts=int(soup.teams.visitor.totals.scoring.offrpatt.contents[0]),
                  two_point_conversions=int(soup.teams.visitor.totals.scoring.offrpmade.contents[0]),
                  field_goal_attempts=int(soup.teams.visitor.totals.scoring.fgatt.contents[0]),
                  field_goals_made=int(soup.teams.visitor.totals.scoring.fgmade.contents[0]),
                  points=int(soup.teams.visitor.totals.scoring.pts.contents[0]),
                  )

            # visiting team defense
            visitor_defense = GameDefense.objects.create(
                game = game,
                team = t2,
                safeties = int(soup.teams.visitor.totals.scoring.saf.contents[0]),
                unassisted_tackles = int(soup.teams.visitor.totals.tackles.uatackles.contents[0]),
                assisted_tackles = int(soup.teams.visitor.totals.tackles.atackles.contents[0]),
                unassisted_tackles_for_loss = int(soup.teams.visitor.totals.tfl.uatfl.contents[0]),
                assisted_tackles_for_loss = int(soup.teams.visitor.totals.tfl.atfl.contents[0]),
                tackles_for_loss_yards = int(soup.teams.visitor.totals.tfl.tflyards.contents[0]),
                unassisted_sacks = int(soup.teams.visitor.totals.tfl.uasacks.contents[0]),
                assisted_sacks = int(soup.teams.visitor.totals.tfl.asacks.contents[0]),
                sack_yards = int(soup.teams.visitor.totals.tfl.sackyards.contents[0]),
                defensive_interceptions = int(soup.teams.visitor.totals.passdefense.intnumber.contents[0]),
                defensive_interception_yards = int(soup.teams.visitor.totals.passdefense.intyards.contents[0]),
                defensive_interception_touchdowns = int(soup.teams.visitor.totals.passdefense.inttd.contents[0]),
                pass_breakups = int(soup.teams.visitor.totals.passdefense.passbreakups.contents[0]),
                fumbles_forced = int(soup.teams.visitor.totals.fumbles.fumblesforced.contents[0]),
                fumbles_number = int(soup.teams.visitor.totals.fumbles.fumblesnumber.contents[0]),
                fumbles_yards = int(soup.teams.visitor.totals.fumbles.fumblesyards.contents[0]),
                fumbles_touchdowns = int(soup.teams.visitor.totals.fumbles.fumblestd.contents[0])
                )
            
        except:
            print "Could not find game between %s and %s on %s" % (t1.name, t2.name, soup.gamedate.contents[0])
    


def game_fetcher(year):
    l = get_summary_links(year)
    g = get_game_xml_url(year,l)
    for game in g:
        urllib.urlretrieve(game, game.split("worksheets/")[1])

def game_loader(year):
    l = get_summary_links(year)
    g = get_game_xml_url(year,l)
    load_ncaa_game_xml(g)

def load_rosters(year):
    """
    Loader for NCAA roster information. Loops through all teams in the database and finds rosters for the given year, then populates Player table with
    information for each player for that year. Also adds aggregate class totals for team in CollegeYear model.
    """
    teams = College.objects.all()
    for team in teams:
        load_team(team.id, year)

def load_team(team_id, year):
    f = open('errors.txt','w')
    team = College.objects.get(id=team_id)
    url = "http://web1.ncaa.org/football/exec/roster?year=%s&org=%s" % (year, team.id)
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    try:
        classes = soup.find("th").contents[0].split(":")[1].split(',') # retrieve class numbers for team
        fr, so, jr, sr = [int(c.strip()[0:2]) for c in classes] # assign class numbers
        t = CollegeYear.objects.get(college=team, year=year)
        t.freshmen = fr
        t.sophomores = so
        t.juniors = jr
        t.seniors = sr
        t.save()
        rows = soup.findAll("tr")[5:]
        for row in rows:
            cells = row.findAll("td")
            if cells[2].contents[0].strip() == '-':
                f.write("Incomplete record for %s in %s: %s\n" % (team.name, year, cells[1].a))
            else:
                unif = cells[0].contents[0].strip()
                name = cells[1].a.contents[0].strip()
                pos = Position.objects.get(abbrev=cells[2].contents[0].strip())
                cl = cells[3].contents[0].strip()
                gp = int(cells[4].contents[0].strip())
                py, created = Player.objects.get_or_create(name=name, slug=name.lower().replace(' ','-').replace('.','').replace("'","-"), team=team, year=year, position=pos, number=unif, games_played=gp, status=cl)
    except:
        pass
    f.close()

def load_coaches():
    import xlrd
    url1 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd654a53ad23b/d1a_birthdates.xls?MOD=AJPERES'
    file = urllib.urlretrieve(url1, 'csv/coaches.xls')
    book = xlrd.open_workbook('csv/coaches.xls')
    sh = book.sheet_by_index(0)
    for rx in range(1,sh.nrows):
        n = sh.cell_value(rowx=rx, colx=0).split(' (')
        date = datetime.date(xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[0], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[1], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[2])
        c, created = Coach.objects.get_or_create(ncaa_name = sh.cell_value(rowx=rx, colx=0), name = n[0], alma_mater = n[1].split(')')[0], birth_date = date)
        c.slug = c.name.lower().replace(' ','-').replace(',','-').replace('.','-').replace('--','-')
        c.save()
    url2 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd1b4a538e0d9/d1a.xls?MOD=AJPERES'
    file2 = urllib.urlretrieve(url2, 'csv/coaches2.xls')
    book2 = xlrd.open_workbook('csv/coaches2.xls')
    sh2 = book2.sheet_by_index(0)
    for rx in range(1, sh2.nrows):
        c = Coach.objects.get(ncaa_name = sh2.cell_value(rowx=rx, colx=0))
        c.years = sh2.cell_value(rowx=rx, colx=2)
        c.wins = sh2.cell_value(rowx=rx, colx=3)
        c.losses = sh2.cell_value(rowx=rx, colx=4)
        c.ties = sh2.cell_value(rowx=rx, colx=5)
        c.save()

def load_player_stats(yr=2007):
    y = Year.objects.get(id=int(yr))
    file = open('csv/DIVISION1_1125.csv').readlines()
    file = file[2:]
    playergame = open('csv/playergames.csv','w')
    for line in file:
        playergame.write(line.replace('""', '"0"'))    
    playergame.close()
        
    reader = csv.reader(open('csv/playergames.csv'))
    for row in reader:
        date = datetime.datetime(*(strptime(row[2], "%m/%d/%y")[0:5]))
        if date >= datetime.datetime(2007, 1, 10):
            t = College.objects.get(id=row[0])
            g = Game.objects.get(team1=t, date=date)
            if row[5] == '0':
                p, created = PlayerYear.objects.get_or_create(team=t, year=y, player__last_name=row[4], number=row[3])
                print "created new playeryear"
            else:
                p, created = PlayerYear.objects.get_or_create(team=t, year=y, player__last_name=row[4], player__first_name_fixed=row[5], ncaa_number=row[3])
                print "created new playeryear"                
            if p:
                pt, created = PlayerScore.objects.get_or_create(game=g, playeryear=p, total_td=row[36], total_points=row[48])
                po, created = PlayerOffense.objects.get_or_create(game=g, playeryear=p, rushes=row[6], rush_gain=row[7], rush_loss=row[8], rush_net=row[9], rush_td=row[10], pass_attempts=row[11], pass_complete=row[12], pass_intercept=row[13], pass_yards=row[14], pass_td=row[15], conversions=row[16], offense_plays=row[17], offense_yards=row[18], receptions=row[19], reception_yards=row[20], reception_td=row[21])
                pd, created = PlayerDefense.objects.get_or_create(game=g, playeryear=p, interceptions=row[22], interception_yards=row[23], interception_td=row[24], fumble_returns=row[25], fumble_return_yards=row[26], fumble_return_td=row[27], safeties=row[47])
                ps, created = PlayerSpecial.objects.get_or_create(game=g, playeryear=p, punts=row[28], punt_yards=row[29], punt_returns=row[30], punt_return_yards=row[31], punt_return_td=row[32], kickoff_returns=row[33], kickoff_return_yards=row[34], kickoff_return_td=row[35], pat_attempts=row[37], pat_made=row[38], two_point_attempts=row[39], two_point_made=row[40], defense_pat_attempts=row[41], defense_pat_made=row[42], defense_return_attempts=row[43], defense_return_made=row[44], field_goal_attempts=row[45], field_goal_made=row[46])
                print "Created player stats for %s on %s" % (row[4], t.name)
            else:
                print "Could not create stats for %s on %s" %s (row[4], t.name)
#    cleanup()

def update_offense(yr='2007'):
    y = Year.objects.get(year=int(yr))
    py = PlayerYear.objects.select_related().filter(year=yr)
    cursor = connection.cursor()
    for player in py:
        ps = PlayerSummary.objects.get_or_create(playeryear=player)
        cursor.execute("""
            update football_playersummary 
            set rushes = (
                select sum(football_playeroffense.rushes)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            rush_gain = (
                select sum(football_playeroffense.rush_gain)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            rush_net = (
                select sum(football_playeroffense.rush_net)
                from football_playeroffense
                where football_playeroffense.playeryear_id = %s),
            rush_td = (
                select sum(football_playeroffense.rush_td)
                from football_playeroffense
                where football_playeroffense.playeryear_id = %s),
            pass_attempts = (
                select sum(football_playeroffense.pass_attempts)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_complete = (
                select sum(football_playeroffense.pass_complete)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_yards = (
                select sum(football_playeroffense.pass_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_td = (
                select sum(football_playeroffense.pass_td)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            receptions = (
                select sum(football_playeroffense.receptions)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            reception_yards = (
                select sum(football_playeroffense.reception_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            reception_td = (
                select sum(football_playeroffense.reception_td)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            offense_plays = (
                select sum(football_playeroffense.offense_plays)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            offense_yards = (
                select sum(football_playeroffense.offense_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s)
            where football_playersummary.playeryear_id = %s""", (player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id)
            )