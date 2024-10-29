
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
    signform = models.BooleanField(default = False) 
    exclude = models.BooleanField(default = False) 
    share = models.BooleanField(default = False)
    updated_at = models.DateTimeField(auto_now = True, blank = True)
    group = models.CharField(max_length= 50, blank = True)
    def __unicode__(self):
        return 'id='+ str(self.pk)


class Section(models.Model):
    sectionname = models.CharField(max_length = 500, blank = True)
    totalnum = models.PositiveIntegerField(blank = True, default = 0)
    numberofquestions = models.PositiveIntegerField(blank = True, default = 0)
    def __unicode__(self):
        return 'id='+ str(self.pk)


class Progress(models.Model):
    student = models.ForeignKey(User, default = None, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, default = None, on_delete=models.CASCADE)
    question_order = models.CharField(max_length= 3000, blank = True)
    question_complete_list = models.CharField(max_length= 3000, blank = True)
    complete = models.BooleanField(default = False)
    score = models.PositiveIntegerField(default = 0, blank = True)
    numdone = models.PositiveIntegerField(default = 0, blank = True)
    trial = models.PositiveIntegerField(blank = True, default = 0)
    created_at = models.DateTimeField(auto_now_add= True, blank = True)
    updated_at = models.DateTimeField(auto_now = True, blank = True)

class Question(models.Model):
    section = models.ForeignKey(Section, default = None ,on_delete=models.CASCADE)
    background = models.CharField(max_length = 3000, blank = True)
    q = models.CharField(max_length = 3000, blank = True)

    question_stem  = models.CharField(max_length = 300000, blank = True)
    question_stem_ctn  = models.CharField(max_length = 300000, blank = True)
    question_stem_ctn2 = models.CharField(max_length = 300000, blank = True)

    category= models.CharField(max_length = 500, blank = True, null = True)

    img= models.CharField(max_length = 500, blank = True, null = True)
    q_id = models.CharField(max_length = 500, blank = True)
    correctanswer = models.PositiveIntegerField(default = 0, blank = True)
    feedback = models.CharField(max_length = 3000, blank = True)
    option1 = models.CharField(max_length = 500, blank = True)
    option2 = models.CharField(max_length = 500, blank  = True)
    option3 = models.CharField(max_length = 500, blank = True)
    option4 = models.CharField(max_length = 500, blank = True)
    def __unicode__(self):
        return 'id='+ str(self.pk)

class ScreenshotUpload(models.Model):
    user = models.ForeignKey(User, default = None,on_delete=models.CASCADE)
    screenshot = models.FileField(upload_to="screenshots/", blank=True)
    complete= models.BooleanField(blank = True, default = False)



class Response(models.Model):
    student = models.ForeignKey(User, default = None, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, default = None, on_delete=models.CASCADE)
    response = models.PositiveIntegerField(blank = True, default= 0)
    justification = models.CharField(max_length = 3000, blank = True)
    correct = models.BooleanField(blank= True, default=False)
    trial = models.PositiveIntegerField(blank = True, default = 0)
    section = models.ForeignKey(Section, default = None, on_delete=models.CASCADE)
    feedbackmessage = models.CharField(max_length = 1000, blank = True)
    checkanswer_at = models.DateTimeField(auto_now = False, blank = True, default = timezone.now)
    nextquestion_at = models.DateTimeField(auto_now = False, blank = True, default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True, blank = True)
    def __unicode__(self):
        return 'id='+ str(self.pk)

class SeverityQuestion(models.Model):
    section = models.ForeignKey(Section, default = None, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, default = None, on_delete=models.CASCADE)
    
    response_text = models.CharField(max_length = 3000, blank = True)

    option1 = models.CharField(max_length = 3000, default = None)
    option2 = models.CharField(max_length = 3000, default = None)
    option3 = models.CharField(max_length = 3000, default = None)
    correctanswer = models.PositiveIntegerField(blank = True, default = 0)

class SeverityResponse(models.Model):
    student = models.ForeignKey(User, default = None, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, default = None, on_delete=models.CASCADE)
    trial = models.PositiveIntegerField(blank = True, default = 0)
    question = models.ForeignKey(SeverityQuestion, default  = None, on_delete=models.CASCADE)
    response = models.PositiveIntegerField(blank = True, default = 0)
    justification = models.CharField(max_length = 3000, blank = True)
    correct = models.BooleanField(blank= True, default=False)
    feedbackmessage = models.CharField(max_length = 1000, blank = True)
    checkanswer_at = models.DateTimeField(auto_now = False, blank = True, default = timezone.now)
    nextquestion_at = models.DateTimeField(auto_now = False, blank = True, default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True, blank = True)

