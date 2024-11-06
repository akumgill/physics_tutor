# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
# from storyboard.forms import *
from storyboard.models import *
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
import json
from django.http import HttpResponse, Http404, JsonResponse
from django.core.files import File
import sqlite3
import os
import numpy as np
import random
from django.utils import timezone

from os import listdir
from django.core.files import File
import re, math
from collections import Counter


section_names = ['Section 1 (2D Kinematics Problem)', 'Section 2 ()', 'Section 3 ()', 'Section 4 ()']
numberofquestions_list = [1, 0, 0, 0]

@ensure_csrf_cookie
@login_required
def home(request):
    context = {}
    user = request.user
    participant = get_object_or_404(Participant, user=user)
    # if not participant.signform:
    #     consentform = ConsentForm()
    #     context['consentform'] = consentform
    #     return render(request, 'storyboard/recruitment.html', context)
    # else:
    #     displaylist = []
    #     for i in range(4):
    #         section = get_object_or_404(Section, id = i+1)
    #         progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-score")
    #         progress = progress_list[0]
    #         displaylist.append(progress)

    #     context['displaylist'] = displaylist
    context['user'] = user
    print ("showshow")
    return render(request, 'storyboard/welcome.html', context)

# @login_required
# def section1(request):
#     context = {}
#     user = request.user
#     section = get_object_or_404(Section, id= 1)
#     progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
#     progress = progress_list[0]

#     if request.method == "GET":
#         if progress.trial == 0:
#             context['sectionstatus'] = "You haven't started this section yet. Please click on the button to start this section."         
#         else:
#             progress_highestscore = Progress.objects.filter(student = user).filter(section = section).order_by("-score")[0]
#             score= progress_highestscore.score
#             context["sectionstatus"] = "Your current score for this section is "+str(score)+". You can work on the section again to earn a new score."
#         return render(request, 'storyboard/section1.html', context)
        
#     else:    
#         trial = progress.trial+1
#         progress = Progress(student = user, section  = section, trial = trial, score = 0)
#         progress.save()
#         number_of_questions = section.numberofquestions
#         for i in range(number_of_questions):
#             question = Question.objects.filter(section = section).order_by("id")[i]
#             response = Response(student = user, trial = trial, question = question, section = section)
#             response.save()
#         return redirect(reverse('section1_questionpage', args = (0,)))


@login_required
def section1_questionpage(request):
    user = request.user
    context = {"user": user}
    
    section = get_object_or_404(Section, s_id=1)
    q_id = 1
    question = get_object_or_404(Question, q_id=f"q{q_id}", section=section)
    context["question"] = question.text
    context["question_img_url"] = question.img_url
    
    choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
    context["choices_question"] = [o.text for o in choices_question]
    
    h_id = 2
    hint = get_object_or_404(Hint, h_id=f"q{q_id}.h{h_id}")
    context["hint"] = hint.text
    context["hint_img_url"] = hint.img_url
    
    choices_hint = Option.objects.filter(o_id__startswith=f"q{q_id}.h{h_id}.o")
    context["choices_hint"] = [o.text for o in choices_hint]
    hint_list = Hint.objects.filter(h_id__startswith=f"q{q_id}.h")
    kc_list = list(set(h.knowledgeComponent.text for h in hint_list))
    context["knowledge_components"] = [
        {"knowledge": kc, "stars": ["star", "star", "star", "star", "star"]} 
        for kc in kc_list
        ]

    context["question"] = "Question 1: A dolphin jumps with an initial velocity of 25 m/s at an angle of 30° above the horizontal. The dolphin passes through the center of a hoop before returning to the water. If the dolphin is moving horizontally at the instant it goes through the hoop, how high, H, above the water is the center of the hoop?"
    context["choices_question"] = ["4.8m", "6.4m", "8.0m", "12.5", "16.0m"]
    context["question_img_url"] = "Q1/Q1_fig.png"
    context["knowledge_components"] = [
        {"knowledge": "Understand Problem", "stars": ["star", "star", "star", "star", "starless"]},
        {"knowledge": "Split into Components", "stars": ["star", "star", "star", "starless", "starless"]},
        {"knowledge": "Apply Relevant Equations", "stars": ["star", "starless", "starless", "starless", "starless"]},
        {"knowledge": "Perform algebra and arithmetic", "stars": ["star", "star", "starless", "starless", "starless"]},
    ]
    context["hint"] = "Hint 2 [Split into components]: The initial velocity is 25 m/s at an angle of 30° above the horizontal. What are the x and y components of the initial velocity?"
    context["choices_hint"] = [
        "\(v_{0,x} = 25 \sin(30^o) m/s\) <br> \(v_{0,y} = 25 \sin(30^o) m/s\)",
        "\(v_{0,x} = 25 \sin(30^o) m/s\) <br> \(v_{0,y} = 25 \\tan(30^o) m/s\)",
        "\(v_{0,x} = 25 \\tan(30^o) m/s\) <br> \(v_{0,y} = 25 \sin(30^o) m/s\)",
        "\(v_{0,x} = 25 m/s\) <br> \(v_{0,y} = 0 m/s\)"
    ]
    context["hint_img_url"] = "Q1/Q1_fig_hint2.png"
    context["feedback"] = "XXX"

    return render(request, 'storyboard/questionpage.html', context)



# @login_required
# def nextpage(request):
#     print ("nextpage")
#     print (request.POST)
#     user = request.user
#     questionid = int(request.POST['questionid'])
#     pageid = int(request.POST['pageid'])
#     question = get_object_or_404(Question, id = questionid)
#     section = question.section

#     progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
#     progress = progress_list[0]

#     if pageid>=section.numberofquestions-1:
#         progress.complete = True
#         progress.save()
#         return redirect(reverse('section'+str(section.id)))
#     else:

#         responses = Response.objects.filter(student =user).filter(question = question).order_by("-updated_at")
#         response = responses[0]
#         response.justification = request.POST['justification']
#         response.nextquestion_at= timezone.now()
#         response.save()
#         reversepage = "section1_questionpage"
#         return redirect(reverse(reversepage, args = (str(pageid+1),)))



# @ensure_csrf_cookie
# @login_required
# def imagefeedback(request):
#     user = request.user
#     if request.method =="POST":
#         print (request.POST)
#         sectionid = int(request.POST['sectionid'])
#         print (sectionid)
#         section = get_object_or_404(Section, id= sectionid)
        
#         progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
#         progress = progress_list[0]
#         trial = progress.trial

#         questionid =int(request.POST["questionid"])
#         question = get_object_or_404(Question, pk = questionid)
        
#         response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]
#         if response.response!=0:
#             alertmessage = "True"
#             response_text = '{ "alertmessage": "'+alertmessage+'"}'
#             print ("yesyes")
#             return HttpResponse(response_text, 'application/json')


#         response_choice = int(request.POST['response'])
#         if response_choice == int(question.correctanswer):
#             feedbackmessage =  "<p style = 'color:green;'>Great! You picked the user need the student created this Storyboard for.</p>"
#             correct = 1
#         else:
#             correctanswer = int(question.correctanswer)
#             optionlist = []
#             optionlist.append(question.option1)
#             optionlist.append(question.option2)
#             optionlist.append(question.option3)
#             optionlist.append(question.option4)
#             feedbackmessage = "<p style = 'color:red;'>Sorry, this Storyboard was created for the user need: <strong> #"+str(correctanswer)+"</strong></p>"
#             correct = 0
        

#         response.response = response_choice
#         response.updated_at = timezone.now()
#         response.correct = correct
#         response.feedbackmessage = feedbackmessage
#         response.save()

#         pageid = int(request.POST['pageid'])

#         if pageid>=section.numberofquestions-1:
#             progress.complete = True
#             progress.save()
#         print (feedbackmessage)

#         question_response_list = Response.objects.filter(student =user).filter(section = section).filter(trial = trial)
#         score = 0
#         for item in question_response_list:
#             score = score+item.correct
#         progress.score = score
#         progress.save()

#         response_text = '{ "feedbackmessage": "'+feedbackmessage+'"}'
#         return HttpResponse(response_text, 'application/json')


# def signform(request):
#     user = request.user

#     participant = get_object_or_404(Participant, user=  user)

#     if "noaccess" in request.POST:
#         participant.exclude = True
#         participant.save()
#     if "access" in request.POST:
#         participant.share = True
#         participant.save()


#     # for item in Section.objects.all():
#     #     progress = Progress(student = user, section = item, complete= False, score = 0, trial = 0)
#     #     progress.save()
#     # participant.signform = True
#     participant.save()
#     return redirect(reverse('home'))

###


####register all students with their andrewids and passwords
def batchregister():
    data =  pd.read_csv("userlist.csv")
    for i in range(len(data)):
        entry = data.iloc[i]
        andrewid = entry["andrewid"].strip()
        user = User.objects.create_user(username = andrewid, password =andrewid)
        user.save()
        participant = Participant(user = user)
        participant.save()
        print(andrewid)
    successmessage = "users registered"
    return successmessage        


def importsections():
    for name, num in zip(section_names, numberofquestions_list):
        section = Section(sectionname = name, numberofquestions = num)
        section.save()
    successmessage = "sections imported"
    return successmessage        

    
def startup():
    print (batchregister())
    print (importsections())


