
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
    img_url = models.TextField(verbose_name="img_url", default="")
    q_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    img_name = models.TextField(verbose_name="img_name", default="")
    total_hints = models.PositiveIntegerField(verbose_name="total_hints", default=0)
    example_problem = models.TextField(verbose_name="example_problem", default="")
    kcs = models.ManyToManyField('KnowledgeComponent')

    def __unicode__(self):
        return 'id='+ str(self.pk)
    
class KnowledgeComponent(models.Model):
    kc_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)

class Hint(models.Model):
    h_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    img_name = models.TextField(verbose_name="img_name", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)
    
class Option(models.Model):
    o_id = models.TextField(primary_key=True)
    text = models.TextField(verbose_name="text", default="")
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(verbose_name="feedback", default="")
    def __unicode__(self):
        return 'id='+ str(self.pk)

class CurrentProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, primary_key=True)
    current_q_id = models.PositiveIntegerField(verbose_name="current_q_id", default=1)
    current_h_id = models.TextField(verbose_name="current_h_id", default="0")
    kc_progress = models.JSONField(default=dict)

    def __unicode__(self):
        return 'id='+ str(self.pk)
    
class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    q_id = models.PositiveIntegerField(verbose_name="q_id", default=1)
    selected_opt_idx = models.PositiveIntegerField(verbose_name="selected_opt_idx", default=1)
    is_correct = models.BooleanField(verbose_name="is_correct", default=False)
    updated_at = models.DateTimeField(auto_now = True, blank = True)
    def __unicode__(self):
        return 'id='+ str(self.pk)
