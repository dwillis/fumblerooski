from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from fumblerooski.college.models import CollegeCoach

class CoachesFeed(Feed):
    link = "/coaches/"
    
    def get_object(self, bits):
        if bits[0] in ['hires','departures']:
            return bits[0]
        else:
            raise FeedDoesNotExist
    
    def title(self, obj):
        return "Fumblerooski.org Coaching %s" % obj.title()
            
    def description(self, obj):
        return "Updates on coaching %s." % obj
    
    def items(self, obj):
        if obj == 'hires':
            return CollegeCoach.objects.filter(start_date__isnull=False).order_by('-start_date')[:15]
        elif obj == 'departures':
            return CollegeCoach.objects.filter(end_date__isnull=False).order_by('-end_date')[:15]
            
    def item_link(self, item):
        return item.coach.get_absolute_url()
    