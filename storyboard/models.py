
# Create your models here.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
# -*- coding: utf-8 -*-



# Create your models here.
class Participant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key=True)
    updated_at = models.DateTimeField(auto_now = True, blank = True)
    def __unicode__(self):
        return 'id='+ str(self.pk)


class Section(models.Model):
    s_id = models.IntegerField(primary_key=True)
    sectionname = models.TextField(max_length = 500, blank = True)
    numberofquestions = models.PositiveIntegerField(blank = True, default = 0)
    def __unicode__(self):
        return 'id='+ str(self.pk)

class Question(models.Model):
    # section = models.ForeignKey(Section, default = None, on_delete=models.CASCADE)
    q_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    img_name = models.TextField(verbose_name="img_name", default="")

    def __unicode__(self):
        return 'id='+ str(self.pk)
    
class KnowledgeComponent(models.Model):
    kc_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)

class Hint(models.Model):
    h_id = models.TextField(primary_key=True)
    knowledgeComponent = models.ForeignKey(KnowledgeComponent, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="text", default="")
    img_url = models.TextField(verbose_name="img_url", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)
    
class Option(models.Model):
    o_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(verbose_name="feedback", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)

