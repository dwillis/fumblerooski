import urllib
import datetime
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import Ranking, College, CollegeYear, Week, Position, RushingSummary


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

def load_player_rushing(year):
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
