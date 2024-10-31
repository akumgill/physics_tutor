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
from storyboard.forms import *
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


section_names = ['Section 1 (Design Storyboards Based on User Needs)', 'Section 2 (Write Lead Questions)', 'Section 3 (Safe and Risky Storyboards)', 'Section 4 (Is This a Good Storyboard?)',  ]
# Section 3 (Perform Your Own Error Analysis)'
totalnum_list = [6, 5, 5 ,4]
numberofquestions_list = [6, 5, 5 ,4]

@ensure_csrf_cookie
@login_required
def home(request):
    context = {}
    user = request.user
    participant = get_object_or_404(Participant, user=  user)
    if not participant.signform:
        consentform = ConsentForm()
        context['consentform'] = consentform
        return render(request, 'storyboard/recruitment.html', context)
    else:
        displaylist = []
        for i in range(4):
            section = get_object_or_404(Section, id = i+1)
            progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-score")
            progress = progress_list[0]
            displaylist.append(progress)

        context['displaylist'] = displaylist
        context['user'] = user
        print ("showshow")
        return render(request, 'storyboard/welcome.html', context)

@login_required
def section1(request):
    context = {}
    user = request.user
    section = get_object_or_404(Section, id= 1)
    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if request.method == "GET":
        if progress.trial == 0:
            context['sectionstatus'] = "You haven't started this section yet. Please click on the button to start this section."         
        else:
            progress_highestscore = Progress.objects.filter(student = user).filter(section = section).order_by("-score")[0]
            score= progress_highestscore.score
            context["sectionstatus"] = "Your current score for this section is "+str(score)+". You can work on the section again to earn a new score."
        return render(request, 'storyboard/section1.html', context)
        
    else:    
        trial = progress.trial+1
        progress = Progress(student = user, section  = section, trial = trial, score = 0)
        progress.save()
        number_of_questions = section.numberofquestions
        for i in range(number_of_questions):
            question = Question.objects.filter(section = section).order_by("id")[i]
            response = Response(student = user, trial = trial, question = question, section = section)
            response.save()
        return redirect(reverse('section1_questionpage', args = (0,)))

@login_required
def section2(request):
    context = {}
    user = request.user
    section = get_object_or_404(Section, id= 2)
    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if request.method == "GET":
        if progress.trial == 0:
            context['sectionstatus'] = "You haven't started this section yet. Please click on the button to start this section."         
        else:
            progress_highestscore = Progress.objects.filter(student = user).filter(section = section).order_by("-score")[0]
            score= progress_highestscore.score
            context["sectionstatus"] = "Your current score for this section is "+str(score)+". You can work on the section again to earn a new score."        
        return render(request, 'storyboard/section2.html', context)
        
    else:    
        trial = progress.trial+1
        progress = Progress(student = user, section  = section, trial = trial, score = 0)
        progress.save()
        number_of_questions = section.numberofquestions
        for i in range(number_of_questions):
            question = Question.objects.filter(section = section).order_by("id")[i]
            response = Response(student = user, trial = trial, question = question, section = section)
            response.save()
        return redirect(reverse('section2_questionpage', args = (0,)))

@login_required
def section3(request):
    context = {}
    user = request.user
    section = get_object_or_404(Section, id= 3)
    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if request.method == "GET":
        if progress.trial == 0:
            context['sectionstatus'] = "You haven't started this section yet. Please click on the button to start this section."         
        else:
            progress_highestscore = Progress.objects.filter(student = user).filter(section = section).order_by("-score")[0]
            score= progress_highestscore.score
            context["sectionstatus"] = "Your current score for this section is "+str(score)+". You can work on the section again to earn a new score."
        return render(request, 'storyboard/section3.html', context)

    else:    
        trial = progress.trial+1
        progress = Progress(student = user, section  = section, trial = trial, score = 0)
        progress.save()
        number_of_questions = section.numberofquestions
        for i in range(number_of_questions):
            question = Question.objects.filter(section = section).order_by("id")[i]
            response = Response(student = user, trial = trial, question = question, section = section)
            response.save()
        return redirect(reverse('section3_questionpage', args = (0,)))

@login_required
def section4(request):
    context = {}
    user = request.user
    section = get_object_or_404(Section, id= 4)
    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if request.method == "GET":
        if progress.trial == 0:
            context['sectionstatus'] = "You haven't started this section yet. Please click on the button to start this section."         
        else:
            progress_highestscore = Progress.objects.filter(student = user).filter(section = section).order_by("-score")[0]
            score= progress_highestscore.score
            context["sectionstatus"] = "Your current score for this section is "+str(score)+". You can work on the section again to earn a new score."
        return render(request, 'storyboard/section4.html', context)

    else:    
        trial = progress.trial+1
        progress = Progress(student = user, section  = section, trial = trial, score = 0)
        progress.save()
        number_of_questions = section.numberofquestions
        for i in range(number_of_questions):
            question = Question.objects.filter(section = section).order_by("id")[i]
            response = Response(student = user, trial = trial, question = question, section = section)
            response.save()
        return redirect(reverse('section4_questionpage', args = (0,)))


@login_required
def section1_questionpage(request, id):

    user = request.user
    section = get_object_or_404(Section, id= 1)
    context = {}


    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]
    trial = progress.trial

    question = Question.objects.filter(section = section).order_by("id")[int(id)]
    print(question.id)
    response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]

    optionlist = []
    optionlist.append(question.option1)
    optionlist.append(question.option2)
    optionlist.append(question.option3)
    optionlist.append(question.option4)

    print("mewmewresponse")
    print(response.response)

    if response.response!=0:
        form = QuestionForm(instance = response, optionlist = optionlist)
        attempted = True
        context["feedbackmessage"] = response.feedbackmessage
    else:
        form = QuestionForm(optionlist = optionlist)
        attempted = False


    context['user'] = user
    context['question'] = question
    context['form'] = form
    context['pageid'] = id
    context['section'] = section
    context['attempted'] = attempted
    # context["feedbackmessage"] = response.feedbackmessage

    image_v= question.img
    imagelist =[]

    if ";" in image_v:
        images = image_v.split(";")
        for image in images:
            imagelist.append(image.strip())
        context["imagelist"] = imagelist

    elif image_v!="None":
        imagelist.append(image_v.strip())
        context["imagelist"] = imagelist
        
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

    return render(request, 'storyboard/questionpage_test.html', context)


@login_required
def section2_questionpage(request, id):

    user = request.user
    section = get_object_or_404(Section, id= 2)
    context = {}


    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]
    trial = progress.trial

    question = Question.objects.filter(section = section).order_by("id")[int(id)]
    response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]

    optionlist = []
    optionlist.append(question.option1)
    optionlist.append(question.option2)
    optionlist.append(question.option3)
    optionlist.append(question.option4)

  

    if response.response!=0:
        form = QuestionForm(instance = response, optionlist = optionlist)
        attempted = True
        context["feedbackmessage"] = response.feedbackmessage
    else:
        form = QuestionForm(optionlist = optionlist)
        attempted = False


    context['user'] = user
    context['question'] = question
    context['form'] = form
    context['pageid'] = id
    context['section'] = section
    context['attempted'] = attempted
    context["feedbackmessage"] = response.feedbackmessage

    image_v= question.img
    imagelist =[]

    if ";" in image_v:
        images = image_v.split(";")
        for image in images:
            imagelist.append(image.strip())
        context["imagelist"] = imagelist

    elif image_v!="None":
        imagelist.append(image_v.strip())
        context["imagelist"] = imagelist

    return render(request, 'storyboard/questionpage2.html', context)
    

@login_required
def section3_questionpage(request, id):

    user = request.user
    section = get_object_or_404(Section, id= 3)
    context = {}


    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]
    trial = progress.trial

    question = Question.objects.filter(section = section).order_by("id")[int(id)]
    response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]

    optionlist = []
    optionlist.append(question.option1)
    optionlist.append(question.option2)

    if response.response!=0:
        form = QuestionForm(instance = response, optionlist = optionlist)
        attempted = True
        context["feedbackmessage"] = response.feedbackmessage
    else:
        form = QuestionForm(optionlist = optionlist)
        attempted = False


    context['user'] = user
    context['question'] = question
    context['form'] = form
    context['pageid'] = id
    context['section'] = section
    context['attempted'] = attempted
    context["feedbackmessage"] = response.feedbackmessage

    image_v= question.img
    imagelist =[]

    if ";" in image_v:
        images = image_v.split(";")
        for image in images:
            imagelist.append(image.strip())
        context["imagelist"] = imagelist

    elif image_v!="None":
        imagelist.append(image_v.strip())
        context["imagelist"] = imagelist
    context["image0"] = imagelist[0]
    context["image1"] = imagelist[1]
    context["image2"] = imagelist[2]

    return render(request, 'storyboard/questionpage3.html', context)


@login_required
def section4_questionpage(request, id):

    user = request.user
    section = get_object_or_404(Section, id= 4)
    context = {}

    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]
    trial = progress.trial

    question = Question.objects.filter(section = section).order_by("id")[int(id)]
    response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]

    optionlist = []
    optionlist.append(question.option1)
    optionlist.append(question.option2)
    optionlist.append(question.option3)
    optionlist.append(question.option4)

    if response.response!=0:
        form = QuestionForm(instance = response, optionlist = optionlist)
        attempted = True
        context["feedbackmessage"] = response.feedbackmessage
    else:
        form = QuestionForm(optionlist = optionlist)
        attempted = False

    context['user'] = user
    context['question'] = question
    context['form'] = form
    context['pageid'] = id
    context['section'] = section
    context['attempted'] = attempted
    context["feedbackmessage"] = response.feedbackmessage

    image_v= question.img
    imagelist =[]

    if ";" in image_v:
        images = image_v.split(";")
        for image in images:
            imagelist.append(image.strip())
        context["imagelist"] = imagelist

    elif image_v!="None":
        imagelist.append(image_v.strip())
        context["imagelist"] = imagelist

    return render(request, 'storyboard/questionpage4.html', context)


@login_required
def nextpage(request):
    print ("nextpage")
    print (request.POST)
    user = request.user
    questionid = int(request.POST['questionid'])
    pageid = int(request.POST['pageid'])
    question = get_object_or_404(Question, id = questionid)
    section = question.section

    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if pageid>=section.numberofquestions-1:
        progress.complete = True
        progress.save()
        return redirect(reverse('section'+str(section.id)))
    else:

        responses = Response.objects.filter(student =user).filter(question = question).order_by("-updated_at")
        response = responses[0]
        response.justification = request.POST['justification']
        response.nextquestion_at= timezone.now()
        response.save()
        reversepage = "section1_questionpage"
        return redirect(reverse(reversepage, args = (str(pageid+1),)))


@login_required
def nextpage2(request):
    print ("nextpage")
    print (request.POST)
    user = request.user
    questionid = int(request.POST['questionid'])
    sectionid = int(request.POST['sectionid'])
    print("section:")
    print(sectionid)

    pageid = int(request.POST['pageid'])
    question = get_object_or_404(Question, id = questionid)
    section = get_object_or_404(Section, id = sectionid)

    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if pageid>=section.numberofquestions-1:
        progress.complete = True
        progress.save()
        return redirect(reverse('section'+str(section.id)))
    else:

        responses = Response.objects.filter(student =user).filter(question = question).order_by("-updated_at")
        response = responses[0]
        response.justification = request.POST['justification']
        response.nextquestion_at= timezone.now()
        response.save()
        reversepage = "section2_questionpage"
        return redirect(reverse(reversepage, args = (str(pageid+1),)))


@login_required
def nextpage3(request):
    print ("nextpage")
    print (request.POST)
    user = request.user
    questionid = int(request.POST['questionid'])
    sectionid = int(request.POST['sectionid'])
    print("section:")
    print(sectionid)

    pageid = int(request.POST['pageid'])
    question = get_object_or_404(Question, id = questionid)
    section = get_object_or_404(Section, id = sectionid)

    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if pageid>=section.numberofquestions-1:
        progress.complete = True
        progress.save()
        return redirect(reverse('section'+str(section.id)))
    else:

        responses = Response.objects.filter(student =user).filter(question = question).order_by("-updated_at")
        response = responses[0]
        response.justification = request.POST['justification']
        response.nextquestion_at= timezone.now()
        response.save()
        reversepage = "section3_questionpage"
        return redirect(reverse(reversepage, args = (str(pageid+1),)))


@login_required
def nextpage4(request):
    print ("nextpage")
    print (request.POST)
    user = request.user
    questionid = int(request.POST['questionid'])
    sectionid = int(request.POST['sectionid'])
    print("section:")
    print(sectionid)

    pageid = int(request.POST['pageid'])
    question = get_object_or_404(Question, id = questionid)
    section = get_object_or_404(Section, id = sectionid)

    progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
    progress = progress_list[0]

    if pageid>=section.numberofquestions-1:
        progress.complete = True
        progress.save()
        return redirect(reverse('section'+str(section.id)))
    else:

        responses = Response.objects.filter(student =user).filter(question = question).order_by("-updated_at")
        response = responses[0]
        response.justification = request.POST['justification']
        response.nextquestion_at= timezone.now()
        response.save()
        reversepage = "section4_questionpage"
        return redirect(reverse(reversepage, args = (str(pageid+1),)))


@ensure_csrf_cookie
@login_required
def imagefeedback(request):
    user = request.user
    if request.method =="POST":
        print (request.POST)
        sectionid = int(request.POST['sectionid'])
        print (sectionid)
        section = get_object_or_404(Section, id= sectionid)
        
        progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
        progress = progress_list[0]
        trial = progress.trial

        questionid =int(request.POST["questionid"])
        question = get_object_or_404(Question, pk = questionid)
        
        response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]
        if response.response!=0:
            alertmessage = "True"
            response_text = '{ "alertmessage": "'+alertmessage+'"}'
            print ("yesyes")
            return HttpResponse(response_text, 'application/json')


        response_choice = int(request.POST['response'])
        if response_choice == int(question.correctanswer):
            feedbackmessage =  "<p style = 'color:green;'>Great! You picked the user need the student created this Storyboard for.</p>"
            correct = 1
        else:
            correctanswer = int(question.correctanswer)
            optionlist = []
            optionlist.append(question.option1)
            optionlist.append(question.option2)
            optionlist.append(question.option3)
            optionlist.append(question.option4)
            feedbackmessage = "<p style = 'color:red;'>Sorry, this Storyboard was created for the user need: <strong> #"+str(correctanswer)+"</strong></p>"
            correct = 0
        

        response.response = response_choice
        response.updated_at = timezone.now()
        response.correct = correct
        response.feedbackmessage = feedbackmessage
        response.save()

        pageid = int(request.POST['pageid'])

        if pageid>=section.numberofquestions-1:
            progress.complete = True
            progress.save()
        print (feedbackmessage)

        question_response_list = Response.objects.filter(student =user).filter(section = section).filter(trial = trial)
        score = 0
        for item in question_response_list:
            score = score+item.correct
        progress.score = score
        progress.save()

        response_text = '{ "feedbackmessage": "'+feedbackmessage+'"}'
        return HttpResponse(response_text, 'application/json')



@ensure_csrf_cookie
@login_required
def imagefeedback2(request):
    user = request.user
    if request.method =="POST":
        print (request.POST)
        sectionid = int(request.POST['sectionid'])
        print (sectionid)
        section = get_object_or_404(Section, id= sectionid)
        
        progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
        progress = progress_list[0]
        trial = progress.trial

        questionid =int(request.POST["questionid"])
        question = get_object_or_404(Question, pk = questionid)

        response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]
        if response.response!=0:
            alertmessage = "True"
            response_text = '{ "alertmessage": "'+alertmessage+'"}'
            print ("yesyes")
            return HttpResponse(response_text, 'application/json')

        response_choice = int(request.POST['response'])

        if response_choice == int(question.correctanswer):
            feedbackmessage = "<p style = 'color:green;'>Great! You picked the lead question written by the student who created this Storyboard. It's a good lead question to ask for this Storyboard."+ question.feedback+ "</p>"
            correct = 1
        else:
            correctanswer = int(question.correctanswer)
            optionlist = []
            optionlist.append(question.option1)
            optionlist.append(question.option2)
            optionlist.append(question.option3)
            optionlist.append(question.option4)

            feedbackmessage = "<p style = 'color:red;'>Sorry, the student who created this Storyboard used the lead question <strong> #"+str(correctanswer)+"</strong>" + question.feedback+ "</p>" 
            correct = 0


        response.response = response_choice
        response.updated_at = timezone.now()
        response.correct = correct
        response.feedbackmessage = feedbackmessage
        response.save()


        pageid = int(request.POST['pageid'])

        if pageid>=section.numberofquestions:
            progress.complete = True
            progress.save()
        print (feedbackmessage)

        question_response_list = Response.objects.filter(student =user).filter(section = section).filter(trial = trial)
        score = 0
        for item in question_response_list:
            score = score+item.correct
        progress.score = score
        progress.save()

        response_text = '{ "feedbackmessage": "'+feedbackmessage+'"}'
        return HttpResponse(response_text, 'application/json')


@ensure_csrf_cookie
@login_required
def imagefeedback3(request):
    user = request.user
    if request.method =="POST":
        print (request.POST)
        sectionid = int(request.POST['sectionid'])
        print (sectionid)
        section = get_object_or_404(Section, id= sectionid)
        
        progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
        progress = progress_list[0]
        trial = progress.trial

        questionid =int(request.POST["questionid"])
        question = get_object_or_404(Question, pk = questionid)

        response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]
        if response.response!=0:
            alertmessage = "True"
            response_text = '{ "alertmessage": "'+alertmessage+'"}'
            print ("yesyes")
            return HttpResponse(response_text, 'application/json')

        response_choice = int(request.POST['response'])
        print(question.feedback)
        if response_choice == int(question.correctanswer):
            feedbackmessage = "<p style = 'color:green;'>Great! You are right."+question.feedback+"</p>"
            correct = 1
        else:
            correctanswer = int(question.correctanswer)
            optionlist = []
            optionlist.append(question.option1)
            optionlist.append(question.option2)
            optionlist.append(question.option3)
            optionlist.append(question.option4)
            if correctanswer == 1:
                feedbackmessage = "<p style = 'color:red;'>Sorry, the three storyboards do follow a progression of riskiness. "+question.feedback+"</p>"
            else:
                feedbackmessage = "<p style = 'color:red;'>Sorry, the three storyboards do not show a progression of riskiness in the design. "+question.feedback+"</p>"
            correct = 0

        response.response = response_choice
        response.updated_at = timezone.now()
        response.correct = correct
        response.feedbackmessage = feedbackmessage
        response.save()

        pageid = int(request.POST['pageid'])

        if pageid>=section.numberofquestions:
            progress.complete = True
            progress.save()
        print (feedbackmessage)

        question_response_list = Response.objects.filter(student =user).filter(section = section).filter(trial = trial)
        score = 0
        for item in question_response_list:
            score = score+item.correct
        progress.score = score
        progress.save()

        response_text = '{ "feedbackmessage": "'+feedbackmessage+'"}'
        return HttpResponse(response_text, 'application/json')


@ensure_csrf_cookie
@login_required
def imagefeedback4(request):
    user = request.user
    if request.method =="POST":
        print (request.POST)
        sectionid = int(request.POST['sectionid'])
        print (sectionid)
        section = get_object_or_404(Section, id= sectionid)
        
        progress_list = Progress.objects.filter(student = user).filter(section = section).order_by("-trial")
        progress = progress_list[0]
        trial = progress.trial

        questionid =int(request.POST["questionid"])
        question = get_object_or_404(Question, pk = questionid)
        
        response = Response.objects.filter(student= user).filter(trial = trial).filter(section = section).filter(question = question)[0]
        if response.response!=0:
            alertmessage = "True"
            response_text = '{ "alertmessage": "'+alertmessage+'"}'
            print ("yesyes")
            return HttpResponse(response_text, 'application/json')

        response_choice = int(request.POST['response'])
        if response_choice == int(question.correctanswer):
            feedbackmessage = "<p style = 'color:green;'>Great! You gave the same feedback to this Storyboard as an instructor. "+ question.feedback+"</p>"
            correct = 1
        else:
            correctanswer= int(question.correctanswer)
            feedbackmessage = "<p style = 'color:red;'>Sorry, the instrucotr found the issue with this Storyboard to be  <strong> #"+str(correctanswer)+"</strong> " + question.feedback+ "</p>"
            correct = 0
  
        response.response = response_choice
        response.updated_at = timezone.now()
        response.correct = correct
        response.feedbackmessage = feedbackmessage
        response.save()


        pageid = int(request.POST['pageid'])

        if pageid>=section.numberofquestions:
            progress.complete = True
            progress.save()
        print (feedbackmessage)

        question_response_list = Response.objects.filter(student =user).filter(section = section).filter(trial = trial)
        score = 0
        for item in question_response_list:
            score = score+item.correct
        progress.score = score
        progress.save()

        response_text = '{ "feedbackmessage": "'+feedbackmessage+'"}'
        return HttpResponse(response_text, 'application/json')



def signform(request):
    user = request.user

    participant = get_object_or_404(Participant, user=  user)

    if "noaccess" in request.POST:
        participant.exclude = True
        participant.save()
    if "access" in request.POST:
        participant.share = True
        participant.save()


    for item in Section.objects.all():
        progress = Progress(student = user, section = item, complete= False, score = 0, trial = 0)
        progress.save()
    participant.signform = True
    participant.save()
    return redirect(reverse('home'))

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
    successmessage = "group2 registered"
    return successmessage        

def batchregister_group1():
    data =  pd.read_csv("userlist.csv")
    for i in range(len(data)):
        entry = data.iloc[i]
        andrewid = entry["andrewid"].strip()
        user = User.objects.create_user(username = andrewid, password =andrewid)
        user.save()
        participant = Participant(user = user)
        participant.save()
        print(andrewid)
    successmessage = "group1 registered"
    return successmessage   

def importsections():
    for i in range(len(section_names)):
        section = Section(sectionname = section_names[i], numberofquestions = numberofquestions_list[i], totalnum = totalnum_list[i])
        section.save()
    successmessage = "sections imported"
    return successmessage        

def import_questions_section1():
    data = pd.read_csv("match_board_need.csv", header =0, encoding = "ISO-8859-1")
    section = get_object_or_404(Section, pk = 1)

    for i in range(len(data)):
        entry = data.iloc[i]
        question = Question(img = entry["img"],correctanswer = entry["correct"], option1 = entry["option1"], option2 = entry["option2"], option3=  entry["option3"], option4 = entry["option4"], section = section)
        question.save()

    successmessage = "section 1 questions imported"
    return successmessage


def import_questions_section2():
    data = pd.read_csv("match_board_question.csv", header =0, encoding = "ISO-8859-1")
    section = get_object_or_404(Section, pk = 2)

    for i in range(len(data)):
        entry = data.iloc[i]
        question = Question(question_stem = entry["question_stem"], img = entry["img"], correctanswer = entry["correct"], option1 = entry["option1"], option2 = entry["option2"], option3=  entry["option3"], option4 = entry["option4"], section = section)
        question.save()

    successmessage = "section 2 questions imported"
    return successmessage


def import_questions_section3():
    data = pd.read_csv("match_progression.csv", header =0, encoding = "ISO-8859-1")
    section = get_object_or_404(Section, pk = 3)

    for i in range(len(data)):
        entry = data.iloc[i]
        question = Question(question_stem = entry["question_stem"], question_stem_ctn = entry["question_stem_ctn"], img = entry["img"], correctanswer = entry["correct"], option1 = entry["option1"], option2 = entry["option2"],feedback = entry["feedback"], section = section)
        question.save()

    successmessage = "section 3 questions imported"
    return successmessage

def import_questions_section4():
    data = pd.read_csv("match_board_feedback.csv", header =0, encoding = "ISO-8859-1")
    section = get_object_or_404(Section, pk = 4 )

    for i in range(len(data)):
        entry = data.iloc[i]
        feedback = entry["feedback"]
        if pd.isnull(feedback):
            feedback = ""

        question = Question(question_stem = entry["question_stem"], question_stem_ctn = entry["question_stem_ctn"], img = entry["img"], correctanswer = entry["correct"],option1 = entry["option1"], option2 = entry["option2"],option3 = entry["option3"], option4 = entry["option4"], feedback = feedback, section = section)
        question.save()

    successmessage = "section 4 questions imported"
    return successmessage



def register_new_user():
    name = "jesses1"
    user = User.objects.create_user(username = name, password =name)
    user.save()
    participant = Participant(user = user)
    participant.save()
    print ("new user registered")
    
def startup():
    print (batchregister())
    print (importsections())

def import_questions():
    print (import_questions_section1())
    print (import_questions_section2())
    print (import_questions_section3())
    print (import_questions_section4())

def group1():
    print (batchregister_group1())

