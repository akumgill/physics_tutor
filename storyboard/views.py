# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
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
    
    section = get_object_or_404(Section, s_id=1)
    
    # QUESTION
    q_id = 1
    question = get_object_or_404(Question, q_id=f"q{q_id}")
    context["question"] = question.text
    context["question_img_url"] = question.img_name
    
    # QUESTION OPTIONS
    choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
    context["choices_question"] = [o.text for o in choices_question]
    correct_option_index = next((index for index, o in enumerate(choices_question) if o.is_correct), -1)

    # Initial hint setup
    h_id = 1
    hint = get_object_or_404(Hint, h_id=f"q{q_id}.h{h_id}")
    context["hint"] = hint.text
    if hint.img_name != "no_img":
        context["hint_img_url"] = hint.img_name

    # HINT OPTIONS
    choices_hint = Option.objects.filter(o_id__startswith=f"q{q_id}.h{h_id}.o")
    context["choices_hint"] = [o.text for o in choices_hint]
    correct_hint_index = next((index for index, o in enumerate(choices_hint) if o.is_correct), -1)

    if request.method == "POST" and request.POST.get('direction'):
        current_hint_id = request.POST.get('current_hint_id')
        direction = request.POST.get('direction')
        hint = navigate_hint(q_id, current_hint_id, direction)
        return JsonResponse({'hint_text': hint.text, 'hint_img_url': hint.img_name, 'hint_id': hint.h_id})

    # Handle POST requests for hint navigation
    if request.method == "POST" and request.POST.get('unique_identifier'):
        unique_identifier = request.POST.get('unique_identifier')
        if unique_identifier == "submit_answer":
            selected_answer_index = request.POST.get('answer')
            feedback = choices_question[int(selected_answer_index)].feedback
            return JsonResponse({'correct': int(selected_answer_index) == correct_option_index, 'feedback': feedback})
        elif unique_identifier == 'submit_hint':
            hint_answer_index = request.POST.get('hint_answer')
            feedback = choices_hint[int(hint_answer_index)].feedback
            return JsonResponse({'correct': int(hint_answer_index) == correct_hint_index, 'feedback': feedback})


    # Knowledge Components
    context["knowledge_components"] = [
        {"knowledge": "Understand Problem", "stars": ["star", "star", "star", "star", "starless"]},
        {"knowledge": "Split into Components", "stars": ["star", "star", "star", "starless", "starless"]},
        {"knowledge": "Apply Relevant Equations", "stars": ["star", "starless", "starless", "starless", "starless"]},
        {"knowledge": "Perform algebra and arithmetic", "stars": ["star", "star", "starless", "starless", "starless"]},
    ]

    return render(request, 'storyboard/questionpage.html', context)

def navigate_hint(q_id, current_hint_id, direction):
    # Extract the current hint number
    current_hint_number = int(current_hint_id.split('h')[-1])
    if direction == "next":
        new_hint_number = current_hint_number + 1
    else:
        new_hint_number = current_hint_number - 1

    # Construct the new hint ID
    new_hint_id = f"q{q_id}.h{new_hint_number}"
    # Fetch the new hint
    return get_object_or_404(Hint, h_id=new_hint_id)


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

def import_options():
    data = pd.read_csv("options.csv", header=0, delimiter=',')
    for i in range(len(data)):
        entry = data.iloc[i]
        option = Option(
            o_id = entry["o_id"],
            text = entry["text"],
            is_correct = entry["is_correct"],
            feedback = entry["feedback"],
        )
        option.save()
    successmessage = "options imported"
    return successmessage

def import_hints():
    data = pd.read_csv("hints.csv", header=0, delimiter=',')
    for i in range(len(data)):
        entry = data.iloc[i]
        hint = Hint(
            h_id = entry["h_id"],
            # TODO[Akum]: add kc_id as foreign key after I import them
            # kc_id = entry["kc_id"],
            text = entry["text"],
            img_name = entry["img_name"],
        )
        print(hint)
        hint.save()
    successmessage = "hints imported"
    return successmessage

def startup():
    print (batchregister())
    print (import_sections())
    print (import_questions())
    print (import_options())
    print (import_hints())
