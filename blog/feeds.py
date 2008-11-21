from django.contrib.syndication import feeds
from django.core.exceptions import ObjectDoesNotExist
 
from fumblerooski.blog.models import Post
 
class LatestPostFeed(feeds.Feed):
    """
Feed of the latest 10 posts.
"""
    title = "Fumblerooski: Latest Entries"
    link = "/blog/"
    
    def items(self):
        return Post.objects.active()[:10]
    
    def item_pubdate(self, item):
        return item.pub_date