import xlrd
import urllib.request
from fumblerooski.college.models import Coach

# deprecated
def load_coaches():
    url1 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd654a53ad23b/d1a_birthdates.xls?MOD=AJPERES'
    file = urllib.request.urlretrieve(url1, 'csv/coaches.xls')
    book = xlrd.open_workbook('csv/coaches.xls')
    sh = book.sheet_by_index(0)
    for rx in range(1,sh.nrows):
        n = sh.cell_value(rowx=rx, colx=0).split(' (')
        date = datetime.date(xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[0], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[1], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[2])
        c, created = Coach.objects.get_or_create(ncaa_name = sh.cell_value(rowx=rx, colx=0), name = n[0], alma_mater = n[1].split(')')[0], birth_date = date)
        c.slug = c.name.lower().replace(' ','-').replace(',','-').replace('.','-').replace('--','-')
        c.save()
    url2 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd1b4a538e0d9/d1a.xls?MOD=AJPERES'
    file2 = urllib.request.urlretrieve(url2, 'csv/coaches2.xls')
    book2 = xlrd.open_workbook('csv/coaches2.xls')
    sh2 = book2.sheet_by_index(0)
    for rx in range(1, sh2.nrows):
        c = Coach.objects.get(ncaa_name = sh2.cell_value(rowx=rx, colx=0))
        c.years = sh2.cell_value(rowx=rx, colx=2)
        c.wins = sh2.cell_value(rowx=rx, colx=3)
        c.losses = sh2.cell_value(rowx=rx, colx=4)
        c.ties = sh2.cell_value(rowx=rx, colx=5)
        c.save()