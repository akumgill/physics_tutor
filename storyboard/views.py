# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
import ast
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
from django.forms.models import model_to_dict
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
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt


section_names = ['Section 1 (2D Kinematics Problem)', 'Section 2 ()', 'Section 3 ()', 'Section 4 ()']
numberofquestions_list = [5, 0, 0, 0]

@ensure_csrf_cookie
@login_required
def home(request):
    context = {}
    user = request.user
    participant = get_object_or_404(Participant, user=user)
    if not CurrentProgress.objects.filter(user=user).exists():
        CurrentProgress(user=user).save()
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
    cur_progress = get_object_or_404(CurrentProgress, user=user)

    # KC
    context = updateKC(context, cur_progress)

    # QUESTION
    q_id = cur_progress.current_q_id
    question = get_object_or_404(Question, q_id=f"q{q_id}")
    context["question"] = question.text
    context["question_img_url"] = question.img_name
    context["example_problem"] = question.example_problem
    context["disable_prev_question"] = q_id == 1

    # QUESTION OPTIONS
    choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
    context["choices_question"] = [{"idx": i, "text": o.text} for i, o in enumerate(choices_question)]
    correct_option_index = next((index for index, o in enumerate(choices_question) if o.is_correct), -1)
    print(f"Correct option id: {correct_option_index} -> {context['choices_question'][correct_option_index]}")

    # HINT
    h_id = cur_progress.current_h_id
    print(f"q{q_id}.h{h_id}")
    context = findHint(context, q_id, h_id)
    context["disable_prev_hint"] = h_id == str(0)

    if request.method == "POST" and request.POST.get('unique_identifier'):
        unique_identifier = request.POST.get('unique_identifier')
        if unique_identifier == "submit_answer":
            selected_answer_index = int(request.POST.get('answer'))
            feedback = choices_question[selected_answer_index].feedback
            is_correct = selected_answer_index == correct_option_index
            response = {
                'correct': is_correct,
                'feedback': feedback
            }
            print(response)

            # Load kc_progress from JSONField
            kc_progress = cur_progress.kc_progress
            
            # Move on to the next question
            if is_correct:
                print(is_correct)
                print(f"Completed question {cur_progress.current_q_id}. Moving to {cur_progress.current_q_id + 1}")
                # TODO better way to move to next question than refreshing
                # TODO better handling for final question overflow
                # cur_progress.current_q_id += 1
                # cur_progress.current_h_id = 0
                
                # Increase KCs for correct answers
                for kc in question.kcs.all():
                    # Initialize KC to 1 if this is the first time the student is answering a question
                    if kc.kc_id not in kc_progress:
                        kc_progress[kc.kc_id] = 0
                    kc_progress[kc.kc_id] = min(kc_progress[kc.kc_id] + 1, 5)
                cur_progress.kc_progress = kc_progress
                cur_progress.save()
            return JsonResponse(response)
        elif unique_identifier == 'submit_hint':
            hint_answer_index = int(request.POST.get('hint_answer')) - 1
            print(f"hint_answer_index: {hint_answer_index}")
            feedback = context["choices_hint"][hint_answer_index]["feedback"]
            response = {
                'correct': context["choices_hint"][hint_answer_index]["is_correct"], 
                'feedback': feedback
            }
            return JsonResponse(response)

    return render(request, 'storyboard/questionpage.html', context)

@csrf_exempt
def changequestion(request):
    print("Change Question")
    user = request.user
    cur_progress = get_object_or_404(CurrentProgress, user=user)
    print(cur_progress)
    if request.method == "POST" and request.POST.get('unique_identifier') == "change_question":
        context = {}
        q_id = cur_progress.current_q_id
        
        isNextQuestion = request.POST.get("isNextQuestion") == 'true'
        if isNextQuestion:
            next_question_id = min(q_id + 1, 5)
        else:
            next_question_id = max(q_id - 1, 1)
        
        cur_progress.current_q_id = next_question_id
        cur_progress.current_h_id = str(0)
        cur_progress.save()
        
        context = findQuestion(context, next_question_id)
        context = findHint(context, next_question_id, str(0))
        context = updateKC(context, cur_progress)
        context["disable_prev_question"] = next_question_id == 1
        context["disable_prev_hint"] = True
        
        # print(context)
        return JsonResponse(context)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def findQuestion(context, q_id):
    try:
        question = get_object_or_404(Question, q_id=f"q{q_id}")
        context["question"] = question.text
        context["question_img_url"] = question.img_name
        context["example_problem"] = question.example_problem

        # QUESTION OPTIONS
        choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
        context["choices_question"] = [{"idx": i, "text": o.text} for i, o in enumerate(choices_question)]
        correct_option_index = next((index for index, o in enumerate(choices_question) if o.is_correct), -1)
        print(f"Correct option id: {correct_option_index} -> {context['choices_question'][correct_option_index]}")
    except Question.DoesNotExist:
        context["question"] = "No more question available."
        context["question_img_url"] = ""
        context["example_problem"] = ""
        context["choices_question"] = [{"idx": i + 1, "text": ""} for i, o in enumerate(5)]
    return context


@csrf_exempt  # Allow CSRF exemption for this view
def changehint(request):
    print("Change Hint")
    user = request.user
    cur_progress = get_object_or_404(CurrentProgress, user=user)
    print(cur_progress)
    if request.method == "POST" and request.POST.get('unique_identifier') == "change_hint":
        context = {}
        q_id = cur_progress.current_q_id
        h_id = cur_progress.current_h_id
        question = get_object_or_404(Question, q_id=f"q{q_id}")
        cur_opt = request.POST["hint_option_idx"]
        all_hints_of_question = Hint.objects.filter(h_id__startswith=f"q{q_id}.h")
        all_hints_of_question = [h.h_id for h in all_hints_of_question]

        # Determine whether to get the next or previous hint
        isNextHint = request.POST.get("isNextHint") == 'true'

        if isNextHint:
            next_hint_id = str(min(int(h_id[0]) + 1, question.total_hints))
        else:
            next_hint_id = str(max(int(h_id[0]) - 1, 1))  

        # Update current hint ID in user's progress
        cur_progress.current_h_id = str(next_hint_id)
        cur_progress.save()
        context["disable_prev_hint"] = str(next_hint_id) == str(0)

        if f"q{q_id}.h{next_hint_id}" in all_hints_of_question:
            print(f"q{q_id}.h{next_hint_id}")
            context = findHint(context, q_id, next_hint_id)
        elif f"q{q_id}.h{next_hint_id}_{cur_opt}" in all_hints_of_question:
            print(f"q{q_id}.h{next_hint_id}_{cur_opt}")
            context = findHint(context, q_id, f"{next_hint_id}_{cur_opt}")
        else:
            context["hint"] = ""
            context["hint_img_url"] = ""
            context["choices_hint"] = ["", "", "", "", ""]
        return JsonResponse(context)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def findHint(context, q_id, h_id):
    try:
        hint = get_object_or_404(Hint, h_id=f"q{q_id}.h{h_id}")
        context["hint"] = hint.text
        context["hint_img_url"] = hint.img_name if hint.img_name != "no_img" else ""

        # HINT OPTIONS
        choices_hint = Option.objects.filter(o_id__startswith=f"q{q_id}.h{h_id}.o")
        context["choices_hint"] = [model_to_dict(o) for o in choices_hint]
        for i, o in enumerate(context["choices_hint"]):
            o["idx"] = i + 1
            o.pop("o_id", None)
    except Hint.DoesNotExist:
        context["hint"] = "No more hints available."
        context["hint_img_url"] = ""
        context["choices_hint"] = [
            {"idx": i + 1, "text": "", "feedback": "", "is_correct": False} for i in range(5)
        ]

    return context

def updateKC(context, cur_progress):
    kcs = KnowledgeComponent.objects.all()
    context["knowledge_components"] = []
    for kc in kcs:
        kc_id = kc.kc_id
        progress_value = cur_progress.kc_progress.get(kc_id, 0)  # Default to 0.0 if not found
        star_list = ["star" if i < progress_value else "starless" for i in range(5)]
        context["knowledge_components"].append({
            "knowledge": kc.text,
            "stars": star_list
        })
    return context    


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
            example_problem = entry["example_problem"],
        )
        question.save()

        # Link questions to KCs
        kc_ids = ast.literal_eval(entry["kcs"])
        kcs_to_add = [KnowledgeComponent.objects.get(pk=kc_id) for kc_id in kc_ids]
        question.kcs.set(kcs_to_add)
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
    q_h_count = {}
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
        
        temp = entry["h_id"].split(".")
        q_id = temp[0]
        h_id = int(temp[1].split("_")[0][1:])
        if q_id not in q_h_count:
            q_h_count[q_id] = [h_id]
        else:
            if h_id not in q_h_count[q_id]:
                q_h_count[q_id].append(h_id)
    
    for k in q_h_count.keys():
        question = get_object_or_404(Question, q_id=k)
        question.total_hints = len(q_h_count[k])
        question.save()
                    
    successmessage = "hints imported"
    return successmessage


def import_kcs():
    data = pd.read_csv("kcs.csv", header=0, delimiter=',')
    for i in range(len(data)):
        entry = data.iloc[i]
        kc = KnowledgeComponent(
            kc_id = entry["kc_id"],
            text = entry["kc_text"],
        )
        kc.save()
    successmessage = "KCs imported"
    return successmessage

def startup():
    print (batchregister())
    print (import_sections())
    print (import_kcs())
    print (import_questions())
    print (import_options())
    print (import_hints())
