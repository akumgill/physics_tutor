from django import forms
from django.contrib.auth.models import User
from storyboard.models import *
from django.shortcuts import render, redirect, get_object_or_404

from random import shuffle


class ConsentForm(forms.Form):
    olderthan18 = forms.BooleanField(initial = False, required = False)
    readinfo = forms.BooleanField(initial = False, required = False)
    access = forms.BooleanField(initial= False, required = False)
    noaccess= forms.BooleanField(initial = False, required = False)
    def clean(self):
        cleaned_data = super(ConsentForm, self).clean()
        olderthan18 = cleaned_data.get('olderthan18')
        readinfo = cleaned_data.get('readinfo')
        access = cleaned_data.get('access')
        noaccess = cleaned_data.get('noaccess')
        # if access == True and noaccess ==True:
           
        #     raise forms.ValidationError("You cannot check both statements at the same time.")

        return cleaned_data

class QuestionForm(forms.ModelForm):
    # response = forms.ChoiceField(choices = [(1,"1"),(2,"2"),(3,"3")], widget = forms.RadioSelect(), required = True)
    justification = forms.CharField(max_length = 500, widget = forms.Textarea(attrs ={
        'class':'textinput', 'placeholder':'Optional: leave additional comments'
        }), required = False)

    class Meta:
        model = Response
        fields = ('response', 'justification')    
    def __init__(self, *args, **kwargs):
        optionlist = kwargs.pop('optionlist')
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['response'] =forms.ChoiceField(choices = getchoices(optionlist), widget  = forms.RadioSelect(), required = True)
    def clean_response(self):
        response = self.cleaned_data["response"]
        return response

    def clean_justification(self):
        justification = self.cleaned_data["justification"]
        return justification



class ScreenshotForm(forms.ModelForm):
    screenshot = forms.FileField(widget = forms.FileInput)
    class Meta:
        model = ScreenshotUpload
        fields = ('screenshot',)
    def clean_screenshot(self):
        screenshot = self.cleaned_data["screenshot"]   
        return screenshot


class SeverityQuestionForm(forms.ModelForm):
    # response = forms.ChoiceField(choices = [(1,"1"),(2,"2"),(3,"3")], widget = forms.RadioSelect(), required = True)
    justification = forms.CharField(max_length = 500, widget = forms.Textarea(attrs ={
        'class':'textinput', 'placeholder':'Optional: leave additional comments'
        }), required = False)

    class Meta:
        model = SeverityResponse
        fields = ('response', 'justification')    
    def __init__(self, *args, **kwargs):
        optionlist = kwargs.pop('optionlist')
        super(SeverityQuestionForm, self).__init__(*args, **kwargs)
        self.fields['response'] =forms.ChoiceField(choices = getchoices(optionlist), widget  = forms.RadioSelect(), required = True)
    def clean_response(self):
        response = self.cleaned_data["response"]
        return response
    def clean_justification(self):
        justification = self.cleaned_data["justification"]
        return justification



def getchoices(optionlist):
    choicelist = []
    for i in range(len(optionlist)):
        choicelist.append((i+1, optionlist[i]))
    return choicelist


