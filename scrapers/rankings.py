import urllib
import datetime
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import College, CollegeYear, Week, Position, Player
from fumblerooski.rankings.models import Ranking, RankingType, RushingSummary, PassEfficiency

def ranking_loader(year, week):
    
    teams = College.objects.filter(updated=True).order_by('id')
    for team in teams:
        cy = CollegeYear.objects.get(college=team, year=year)
        w = Week.objects.get(year=year, week_num=week)
        html = urllib.urlopen(cy.get_ncaa_week_url()+str(week)).read()
        soup = BeautifulSoup(html)
        try:
            rankings = soup.findAll('table')[4]
        except:
            rankings = None
        if rankings:
            rows = rankings.findAll('tr')[5:22]
            for row in rows:
                cells = row.findAll('td')
                rt = RankingType.objects.get(name=str(cells[0].find("a").contents[0]))
                try:
                    rk =int(cells[1].contents[0])
                    i_t = False
                except ValueError:
                    rk = int(cells[1].contents[0].split('T-')[1])
                    i_t = True
        
                try:
                    cr = int(cells[5].contents[0])
                    ic_t = False
                except ValueError:
                    cr = int(cells[5].contents[0].split('T-')[1])
                    ic_t = True
        
                r, created = Ranking.objects.get_or_create(ranking_type=rt, college=team, year=year, week=w, rank=rk, is_tied = i_t, actual=float(cells[2].contents[0]), conference_rank=cr, is_conf_tied=ic_t, division = cy.division)

def player_rushing(year):
    url = "http://web1.ncaa.org/mfb/natlRank.jsp?year=%s&div=B&rpt=IA_playerrush&site=org" % year
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    rankings = soup.find('table', {'class': 'statstable'})
    rows = rankings.findAll('tr')[1:]
    d = datetime.date.today()
    if year == d.year:
        w = Week.objects.filter(end_date__lte=d, year=year).order_by('-week_num')[0]
    else:
        w = Week.objects.filter(year=year).order_by('-week_num')[0]
    for row in rows:
        rank = int(row.findAll('td')[0].contents[0])
        year = int(row.findAll('td')[1].find('a')['href'].split('=')[1][:4])
        team_id = int(row.findAll('td')[1].find('a')['href'].split('=')[2].split('&')[0])
        p_num = str(row.findAll('td')[1].find('a')['href'].split('=')[3])
        pos = Position.objects.get(abbrev=str(row.findAll('td')[2].contents[0]))
        carries = int(row.findAll('td')[5].contents[0])
        net = int(row.findAll('td')[6].contents[0])
        td = int(row.findAll('td')[7].contents[0])
        avg = float(row.findAll('td')[8].contents[0])
        ypg = float(row.findAll('td')[9].contents[0])
        team = College.objects.get(id=team_id)
        player = Player.objects.get(team=team, number=p_num, year=year, position=pos)
        prs, created = RushingSummary.objects.get_or_create(player=player, year=year, week=w, rank=rank, carries=carries, net=net, td=td, average=avg, yards_per_game=ypg)

def pass_efficiency(year):
    url = "http://web1.ncaa.org/mfb/natlRank.jsp?year=%s&div=B&rpt=IA_playerpasseff&site=org" % year
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    rankings = soup.find('table', {'class': 'statstable'})
    rows = rankings.findAll('tr')[1:]
    d = datetime.date.today()
    if year == d.year:
        w = Week.objects.filter(end_date__lte=d, year=year).order_by('-week_num')[0]
    else:
        w = Week.objects.filter(year=year).order_by('-week_num')[0]
    for row in rows:
        rank = int(row.findAll('td')[0].contents[0])
        team_id = int(row.findAll('td')[1].find('a')['href'].split('=')[2].split('&')[0])
        p_num = str(row.findAll('td')[1].find('a')['href'].split('=')[3])
        pos = Position.objects.get(abbrev=str(row.findAll('td')[2].contents[0]))
        team = College.objects.get(id=team_id)
        att = int(row.findAll('td')[5].contents[0])
        comp = int(row.findAll('td')[6].contents[0])
        comp_pct = float(row.findAll('td')[7].contents[0])
        intercept = int(row.findAll('td')[8].contents[0])
        int_pct = float(row.findAll('td')[9].contents[0])
        yards = int(row.findAll('td')[10].contents[0])
        yds_per_att = float(row.findAll('td')[11].contents[0])
        tds = int(row.findAll('td')[12].contents[0])
        td_pct = float(row.findAll('td')[13].contents[0])
        rating = float(row.findAll('td')[14].contents[0])
        player = Player.objects.get(team=team, number=p_num, year=year, position=pos)
        pass_eff, created = PassEfficiency.objects.get_or_create(player=player, year=year, week=w, rank=rank, attempts=att,completions=comp, completion_pct=comp_pct, interceptions=intercept, attempts_per_interception=int_pct, yards=yards, yards_per_attempt=yds_per_att, touchdowns=tds, attempts_per_touchdown=td_pct, rating=rating)
