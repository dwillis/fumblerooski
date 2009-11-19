from piston.handler import BaseHandler
from piston.utils import rc
from fumblerooski.college.models import College

class CollegeHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = College
    fields = ('id', 'updated', 'name', 'slug', ('state', ('id', 'name')), ('collegeyear_set', ('year','record','conference_record', 'division', ('conference', ('abbrev','name')))))
    exclude = ('official_url','official_rss', 'drive_slug')
    
    def read(self, request, slug):
        try:
            return College.objects.get(slug=slug)
        except College.DoesNotExist:
            return rc.NOT_FOUND
        except College.MultipleObjectsReturned:
            return rc.BAD_REQUEST
        
    
    @classmethod
    def resource_uri(cls, college):
        return ('colleges', ['json',])