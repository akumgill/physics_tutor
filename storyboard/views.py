# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
import ast
import base64
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
# from storyboard.forms import *
from storyboard.models import *
from storyboard.prompts import *
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
import json
from django.http import HttpResponse, Http404, JsonResponse
from django.core.files import File
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile
from PIL import Image
from openai import OpenAI
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

client = OpenAI(api_key="")

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
    context["question"] = f"Question {q_id}: " + question.text
    context["question_img_url"] = question.img_name
    context["example_problem"] = question.example_problem
    context["disable_prev_question"] = q_id == 1
    context["disable_next_question"] = True
    if History.objects.filter(user=user).filter(q_id=q_id).exists():
        context["disable_next_question"] = not get_object_or_404(History, user=user, q_id=q_id).is_correct

    # QUESTION OPTIONS
    choices_question = Option.objects.filter(o_id__startswith=f"q{q_id}.o")
    context["choices_question"] = [{"idx": i, "text": o.text} for i, o in enumerate(choices_question)]
    correct_option_index = next((index for index, o in enumerate(choices_question) if o.is_correct), -1)
    print(f"Correct option id: {correct_option_index} -> {context['choices_question'][correct_option_index]}")
    
    # History
    context = findHistory(context, user, q_id)

    # HINT
    h_id = cur_progress.current_h_id
    print(f"hint: q{q_id}.h{h_id}")
    context = findHint(context, q_id, h_id)
    context["disable_prev_hint"] = h_id == str(0)

    # Load kc_progress from JSONField
    kc_progress = cur_progress.kc_progress

    if request.method == "POST" and request.POST.get('unique_identifier'):
        unique_identifier = request.POST.get('unique_identifier')
        if unique_identifier == "submit_answer":
            selected_answer_index = int(request.POST.get('answer'))
            feedback = choices_question[selected_answer_index].feedback
            is_correct = selected_answer_index == correct_option_index
            response = {
                'correct': is_correct,
                'feedback': feedback,
                'isAllCorrect': False
            }

            # Save history
            if History.objects.filter(user=user).filter(q_id=q_id).exists():
                history = get_object_or_404(History, user=user, q_id=q_id)
                history.selected_opt_idx = selected_answer_index
                history.is_correct = is_correct
                history.save()
            else:
                History(
                    user = user,
                    q_id = q_id,
                    selected_opt_idx = selected_answer_index,
                    is_correct = is_correct
                ).save()

            # Load kc_progress from JSONField
            kc_progress = cur_progress.kc_progress
            
            # Move on to the next question
            
            # Update KCs and, if correct, complete question
            if is_correct:
                print(is_correct)
                print(f"Completed question {cur_progress.current_q_id}. Moving to {cur_progress.current_q_id + 1}")
                # better handling for final question overflow
                response["isAllCorrect"] = q_id == 5
                
                # Increase KCs for correct answers
                for kc in question.kcs.all():
                    # Initialize KC to 1 if this is the first time the student is answering a question
                    if kc.kc_id not in kc_progress:
                        kc_progress[kc.kc_id] = 0
                    kc_progress[kc.kc_id] = min(kc_progress[kc.kc_id] + 1, 5)
                cur_progress.kc_progress = kc_progress
                cur_progress.save()
            else:
                # Decrease KCs for incorrect answers
                for kc in question.kcs.all():
                    # Initialize KC to 1 if this is the first time the student is answering a question
                    if kc.kc_id not in kc_progress:
                        kc_progress[kc.kc_id] = 0
                    kc_progress[kc.kc_id] = max(kc_progress[kc.kc_id] - 1, 0)
                cur_progress.kc_progress = kc_progress
                cur_progress.save()
            
            kc_response = {}
            for kc in KnowledgeComponent.objects.all():
                if kc.kc_id in kc_progress.keys():
                    kc_response[kc.text] = kc_progress[kc.kc_id]
                else:
                    kc_response[kc.text] = 0

            response['kc_progress'] = kc_response
            print(response)
            return JsonResponse(response)

        elif unique_identifier == 'submit_hint':
            hint_answer_index = int(request.POST.get('hint_answer')) - 1
            print(f"hint_answer_index: {hint_answer_index}")
            feedback = context["choices_hint"][hint_answer_index]["feedback"]

            # Update KCs based on successful or unsuccessful hint completion
            if context["hint_kc"] != "":
                # Initialize if necessary
                if context["hint_kc"] not in kc_progress:
                        kc_progress[context["hint_kc"]] = 0
                
                is_correct = context["choices_hint"][hint_answer_index]["is_correct"]
                # Increment
                if is_correct:
                    kc_progress[context["hint_kc"]] = min(kc_progress[context["hint_kc"]] + 1, 5)
                # Decrement
                else:
                    kc_progress[context["hint_kc"]] = max(kc_progress[context["hint_kc"]] - 1, 0)
                cur_progress.kc_progress = kc_progress
                cur_progress.save()
            
            kc_response = {}
            for kc in KnowledgeComponent.objects.all():
                if kc.kc_id in kc_progress.keys():
                    kc_response[kc.text] = kc_progress[kc.kc_id]
                else:
                    kc_response[kc.text] = 0
            response = {
                'correct': is_correct,
                'feedback': feedback,
                'kc_progress': kc_response,
            }
            print(response)
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
        
        context = findHistory(context, user, next_question_id)        
        context = findQuestion(context, next_question_id)
        context = findHint(context, next_question_id, str(0))
        context = updateKC(context, cur_progress)
        context["disable_prev_question"] = next_question_id == 1
        context["disable_prev_hint"] = True
        context["is_last_question"] = next_question_id == 5
        context["disable_next_question"] = True
        if History.objects.filter(user=user).filter(q_id=next_question_id).exists():
            context["disable_next_question"] = not get_object_or_404(History, user=user, q_id=next_question_id).is_correct
           
        print(context)
        return JsonResponse(context)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def findHistory(context, user, q_id):
    if History.objects.filter(user=user).filter(q_id=q_id).exists():
        history = get_object_or_404(History, user=user, q_id=q_id)
        context["selected_opt_idx"] = history.selected_opt_idx
        context["is_correct"] = history.is_correct
    else:
        context["selected_opt_idx"] = -1
        context["is_correct"] = False
    return context

def findQuestion(context, q_id):
    try:
        question = get_object_or_404(Question, q_id=f"q{q_id}")
        context["question"] = f"Question {q_id}: " + question.text
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
        cur_opt = request.POST.get("hint_option_idx", "0")
        print(f"Hint Option Index selected before changing hint: {cur_opt}")
        all_hints_of_question = Hint.objects.filter(h_id__startswith=f"q{q_id}.h")
        all_hints_of_question = [h.h_id for h in all_hints_of_question]

        # Determine whether to get the next or previous hint
        isNextHint = request.POST.get("isNextHint") == 'true'
        
        # Determine whether next hint is manually assigned
        next_hint_id = request.POST.get("next_hint_idx", "0")
        
        if int(next_hint_id) > 0:
            next_hint_id = str(next_hint_id)
        elif isNextHint:
            next_hint_id = str(min(int(h_id[0]) + 1, question.total_hints))
        else:
            next_hint_id = str(max(int(h_id[0]) - 1, 1))  

        # Update current hint ID in user's progress
        
        context["disable_prev_hint"] = str(next_hint_id) == str(0)

        if f"q{q_id}.h{next_hint_id}" in all_hints_of_question:
            print(f"q{q_id}.h{next_hint_id}")
            context = findHint(context, q_id, next_hint_id)
            cur_progress.current_h_id = str(next_hint_id)
            cur_progress.save()
        elif f"q{q_id}.h{next_hint_id}_{cur_opt}" in all_hints_of_question:
            print(f"q{q_id}.h{next_hint_id}_{cur_opt}")
            context = findHint(context, q_id, f"{next_hint_id}_{cur_opt}")
            cur_progress.current_h_id = f"{next_hint_id}_{cur_opt}"
            cur_progress.save()
        else:
            context["hint"] = ""
            context["hint_img_url"] = ""
            context["choices_hint"] = [
                {"idx": i + 1, "text": "", "feedback": "", "is_correct": False} for i in range(5)
            ]
        return JsonResponse(context)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def findHint(context, q_id, h_id):
    try:
        hint = get_object_or_404(Hint, h_id=f"q{q_id}.h{h_id}")
        context["hint"] = f"Hint {h_id[0]}: " + hint.text
        if h_id[0] == "0":
            context["hint"] = hint.text
        context["hint_img_url"] = hint.img_name if hint.img_name != "no_img" else ""
        context["hint_kc"] = hint.kc_id if hint.kc_id != "none" else ""

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
            kc_id = entry["kc_id"],
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

@login_required
def chatbot(request):
    # user = request.user
    # context = {"user": user}
    # cur_progress = get_object_or_404(CurrentProgress, user=user)
    # q_id = cur_progress.current_q_id
    # question = get_object_or_404(Question, q_id=f"q{q_id}")
    # context["question"] = question.text
    chatbot_html = render_to_string('storyboard/chatbot.html')  # Path to your chatbot template
    return JsonResponse({'html': chatbot_html})
    # return render(request, 'storyboard/chatbot.html', context)

def sendmessage(request):
    print("sendMessage")
    user = request.user
    if request.method == "POST":
        context = {}
        cur_progress = get_object_or_404(CurrentProgress, user=user)
        q_id = cur_progress.current_q_id
        question = get_object_or_404(Question, q_id=f"q{q_id}")
        message = request.POST["message"]
        img_data = request.POST["imageBase64"]
        prompt = PROMPT_QA.format(
            std_msg=message,
            hints=find_hint_with_answer(q_id)
        )
        print(prompt)
        msg_to_gpt = [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }]
        if img_data:
            # Extract image file from Base64 data
            img_format, imgstr = img_data.split(';base64,')  # Separate format and Base64 string
            ext = img_format.split('/')[-1]  # Extract the file extension

            # Save the image to the model
            image = ContentFile(base64.b64decode(imgstr), name=f"uploaded_image.{ext}")
            uploaded_image = UploadedImage.objects.create(image=image, text=message)
            print(uploaded_image.image.url)
            base64_image = encode_image(uploaded_image.image.path)
            img_to_gpt = {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{base64_image}",
                }
            }
            msg_to_gpt[0]['content'].append(img_to_gpt)
        # print(message)
        
        gpt_response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=msg_to_gpt, 
            response_format={"type": "json_object"}
        )
        print(gpt_response.choices[0].message.content)
        gpt_response_json = json.loads(gpt_response.choices[0].message.content)
        hint_idx = gpt_response_json['hint_idx']
        hint_click = f'<span class="clickable-text" onclick="clickHintInChat({hint_idx})">Hint {hint_idx}</span>'
        context['bot_message'] = gpt_response_json['response'] + f" You may refer to {hint_click} for help."
        
        # context['bot_message'] = "Your answer seems to have swapped the sine and cosine for the components of the initial velocity. You may refer to Hint 2 for some help."
        response = json.dumps(context)
        return HttpResponse(response, 'application/javascript')

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8') 

def find_hint_with_answer(q_id):
    response = []
    all_hints_of_question = Hint.objects.filter(h_id__startswith=f"q{q_id}.h")
    all_hints_of_question = [h for h in all_hints_of_question if "_" not in h.h_id and h.h_id[-1] != "0"]
    all_hints_of_question = [(h.h_id, h.text) for h in all_hints_of_question]
    for h_id, h_text in all_hints_of_question:
        options = Option.objects.filter(o_id__startswith=f"{h_id}.o", is_correct=True)
        if options:
            response.append(f"""\"{h_id[-1]}. {h_text} The answer should be: {options[0].text}\"""")
    return "\n".join(response)

def parse_json(response: str):
	try:
		out = json.loads(response)
		return out
	except:
		if "{" in response and "}" in response:
			cleaned_json = re.findall(r"\{.*\}", response, re.DOTALL)[0]
			cleaned_json.replace("\n", "")
			return parse_json(cleaned_json)
		else:
			raise Exception("Invalid JSON format.")
