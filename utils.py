import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime
import time
from fumblerooski.recruits.models import SchoolType, School, City, Position, Year
from fumblerooski.college.models import State, College, Game, Coach, Player, PlayerYear, PlayerScore, PlayerOffense, PlayerDefense, PlayerSpecial, PlayerSummary

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


def load_older_games():
    reader = csv.reader(open('csv/older_games.csv'))
    for row in reader:
        
    

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
            if row[5] == 'ANDRÉ':
                row[5] = 'ANDRE'
            else:
                pass
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