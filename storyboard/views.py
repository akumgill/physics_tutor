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
import logging


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


@login_required
def section1_questionpage(request):
    user = request.user
    context = {"user": user}
    
    # section = get_object_or_404(Section, s_id=1)
    # q_id = 1
    # question = get_object_or_404(Question, q_id=f"q{q_id}")
    # context["question"] = question.text
    # context["question_img_url"] = question.img_url
    
    # choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
    # context["choices_question"] = [o.text for o in choices_question]
    
    # h_id = 2
    # hint = get_object_or_404(Hint, h_id=f"q{q_id}.h{h_id}")
    # context["hint"] = hint.text
    # context["hint_img_url"] = hint.img_url
    
    # choices_hint = Option.objects.filter(o_id__startswith=f"q{q_id}.h{h_id}.o")
    # context["choices_hint"] = [o.text for o in choices_hint]
    # hint_list = Hint.objects.filter(h_id__startswith=f"q{q_id}.h")
    # kc_list = list(set(h.knowledgeComponent.text for h in hint_list))
    # context["knowledge_components"] = [
    #     {"knowledge": kc, "stars": ["star", "star", "star", "star", "star"]} 
    #     for kc in kc_list
    #     ]

    # context["question"] = "Question 1: A dolphin jumps with an initial velocity of 25 m/s at an angle of 30° above the horizontal. The dolphin passes through the center of a hoop before returning to the water. If the dolphin is moving horizontally at the instant it goes through the hoop, how high, H, above the water is the center of the hoop?"
    # context["choices_question"] = ["4.8m", "6.4m", "8.0m", "12.5", "16.0m"]
    
    

    correct_answer = "8.0m"  # Example correct answer

    if request.method == "POST":
        unique_identifier = request.POST.get('unique_identifier')
        if unique_identifier == "submit_answer":
            selected_answer = request.POST.get('answer')
            feedback = "Correct! Well done." if selected_answer == correct_answer else "Incorrect. Try again."
            print(f"Selected answer: {selected_answer}, Feedback: {feedback}")  # logging
            return JsonResponse({'correct': selected_answer == correct_answer, 'feedback': feedback})

    q1 = get_object_or_404(Question, q_id="q1")
    context["question"] = q1.text
    context["question_img_url"] = q1.img_name
    # TODO[Akum]: import options and KCs
    
    context["choices_question"] = ["4.8m", "6.4m", "8.0m", "12.5m", "16.0m"]
    context["knowledge_components"] = [
        {"knowledge": "Understand Problem", "stars": ["star", "star", "star", "star", "starless"]},
        {"knowledge": "Split into Components", "stars": ["star", "star", "star", "starless", "starless"]},
        {"knowledge": "Apply Relevant Equations", "stars": ["star", "starless", "starless", "starless", "starless"]},
        {"knowledge": "Perform algebra and arithmetic", "stars": ["star", "star", "starless", "starless", "starless"]},
    ]
    context["hint"] = "Hint 2 [Split into components]: The initial velocity is 25 m/s at an angle of 30° above the horizontal. What are the x and y components of the initial velocity?"
    context["choices_hint"] = [
        "\\(v_{0,x} = 25 \\sin(30^o) m/s\\) <br> \\(v_{0,y} = 25 \\cos(30^o) m/s\\)",
        "\\(v_{0,x} = 25 \\sin(30^o) m/s\\) <br> \\(v_{0,y} = 25 \\tan(30^o) m/s\\)",
        "\\(v_{0,x} = 25 \\tan(30^o) m/s\\) <br> \\(v_{0,y} = 25 \\sin(30^o) m/s\\)",
        "\\(v_{0,x} = 25 m/s\\) <br> \\(v_{0,y} = 0 m/s\\)"
    ]
    context["hint_img_url"] = "Q1_fig_hint2.png"

    return render(request, 'storyboard/questionpage.html', context)


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


def import_sections():
    for name, num in zip(section_names, numberofquestions_list):
        section = Section(sectionname = name, numberofquestions = num)
        section.save()
    successmessage = "sections imported"
    return successmessage        


def import_questions():
    data = pd.read_csv("questions.csv", header=0, delimiter=',')
    for i in range(len(data)):
        entry = data.iloc[i]
        question = Question(
            q_id = entry["q_id"],
            text = entry["text"],
            img_name = entry["img_name"],
        )
        question.save()
    successmessage = "questions imported"
    return successmessage


def startup():
    print (batchregister())
    print (import_sections())
    print (import_questions())
    
