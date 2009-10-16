from django.test import TestCase
from django.test.client import Client
from fumblerooski.college.models import College, CollegeYear

class CollegeTestCase(TestCase):
    def setUp(self):
        self.florida = College.objects.create(name="Florida", slug='florida', drive_slug='florida',state_id='FL', updated=True)
        self.florida09 = CollegeYear.objects.create(college_id=self.florida.id, year=2009, wins=6, losses=0, ties=0, conference_wins=3, conference_losses=0, conference_ties=0)
        
    def testURL(self):
        self.assertEquals(self.florida.get_absolute_url(), '/college/teams/florida/')
        
    def test_details(self):
        response = self.client.get('/college/teams/florida/')
        self.failUnlessEqual(response.status_code, 200)

class CollegeYearTestCase(TestCase):
    def setUp(self):
        self.florida = College.objects.create(name="Florida", slug='florida', drive_slug='florida',state_id='FL', updated=True)
        self.florida09 = CollegeYear.objects.create(college_id=self.florida.id, year=2009, wins=6, losses=0, ties=0, conference_wins=3, conference_losses=0, conference_ties=0)
        
    def test_gamecount(self):
        self.assertEquals(self.florida09.game_count(), 6)
        
    def test_record(self):
        self.assertEquals(self.florida09.record(), '6-0')
    