from django.test import TestCase
from django.test.client import Client
from fumblerooski.college.models import College, Coach, CoachForm, CoachingJob, CollegeCoach, Position, State, Game, Conference, Player, StateForm, CollegeYear, GameOffense, GameDefense, Week, City, DriveOutcome, GameDrive, PlayerRush, PlayerPass, PlayerReceiving, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerScoring, PlayerReturn, PlayerFumble, BowlGame, PlayerGame, PlayerSummary
from fumblerooski.rankings.models import Ranking, RankingType

class CollegeTestCase(TestCase):
    def setUp(self):
        self.florida = College.objects.create(name="Florida", slug='florida', drive_slug='florida',state_id='FL', updated=True)
        self.florida09 = CollegeYear.objects.create(college_id=self.florida.id, season=2009, wins=6, losses=0, ties=0, conference_wins=3, conference_losses=0, conference_ties=0)
        
    def testURL(self):
        self.assertEquals(self.florida.get_absolute_url(), '/college/teams/florida/')
        
    def test_details(self):
        response = self.client.get('/college/teams/florida/')
        self.failUnlessEqual(response.status_code, 200)

class CollegeYearTestCase(TestCase):
    def setUp(self):
        self.florida = College.objects.create(name="Florida", slug='florida', drive_slug='florida',state_id='FL', updated=True)
        self.florida09 = CollegeYear.objects.create(college_id=self.florida.id, season=2009, wins=6, losses=0, ties=0, conference_wins=3, conference_losses=0, conference_ties=0)
        
    def test_gamecount(self):
        self.assertEquals(self.florida09.game_count(), 6)
        
    def test_record(self):
        self.assertEquals(self.florida09.record(), '6-0')

class CoachTestCase(TestCase):
    def setUp(self):
        self.urban = Coach(id=2, first_name = 'Urban', last_name='Meyer', college_id = 1)
        self.urban.save()
        self.job = CoachingJob.objects.create(id= 1, name='Head Coach', slug='head-coach')
        self.florida = College.objects.create(name="Florida", slug='florida', drive_slug='florida',state_id='FL', updated=True)
        self.florida10 = CollegeYear.objects.create(college_id=self.florida.id, season=2010, wins=6, losses=0, ties=0, conference_wins=3, conference_losses=0, conference_ties=0)
        self.fl10coach = CollegeCoach.objects.create(coach = self.urban, collegeyear=self.florida10)
        self.fl10coach.jobs = [self.job]
    
    def test_save(self):
        self.assertEquals(self.urban.slug, '2-urban-meyer')
        
    def test_current_school(self):
        self.assertEquals(self.urban.current_school(), self.florida)
        
    def test_seasons_at_school(self):
        self.assertEquals(self.urban.seasons_at_school(self.florida), [[2010]])
    
    def test_seasons_at_current_school(self):
        self.assertEquals(self.urban.seasons_at_current_school(), 1)
        
    def test_current_job(self):
        self.assertEquals(self.urban.current_job(), 'Head Coach')
    
    def test_head_coach_experience(self):
        self.assertEquals(self.urban.head_coach_experience(), "Yes")
        
