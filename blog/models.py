from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
 
class PostManager(models.Manager):
    def active(self):
        return self.filter(active=True)
 
class Post(models.Model):
    title = models.CharField(_("title"), max_length=100)
    slug = models.SlugField(_("slug"), unique=True)
    body = models.TextField(_("body"))
    active = models.BooleanField(default=False)
    create_date = models.DateTimeField(_("created"), default=datetime.now)
    pub_date = models.DateTimeField(_("published"), default=datetime.now)
    
    objects = PostManager()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ("-pub_date",)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog_post_detail", kwargs={
            "year": self.pub_date.strftime("%Y"),
            "month": self.pub_date.strftime("%b").lower(),
            "day": self.pub_date.strftime("%d"),
            "slug": self.slug,
        })