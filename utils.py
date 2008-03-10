import re
import urllib
import datetime
from time import strptime
import time
from fumblerooski.recruits.models import SchoolType, School, City, Position
from fumblerooski.college.models import State, College, Game, Coach

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


def get_games(year):
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

def load_players():
    import csv
    reader = csv.reader(open("players2007.csv"))
    for row in reader:
        st = State.objects.get(id=row[5])
        p = Position.objects.get(abbrev=row[2])
        pl, created = Player.objects.get_or_create(first_name=row[0], last_name=row[1], pos=p, height=row[3], weight=row[4], home_state=st)
        pl.save()

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