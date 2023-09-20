from django import forms
from .models import Course, User
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db import models
from .models import *


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select,
        initial="student",
    )         

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES, widget=forms.Select, initial="student"
    )
    email = forms.EmailField(max_length=255, label="Email")
    username = forms.CharField(max_length=50, label="Username")

    class Meta:
        model = User
        fields = ["email", "username", "role"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        role = cleaned_data.get("role")

        if User.objects.filter(email=email, role__in=["student", "teacher"]).exists():
            existing_roles = User.objects.filter(email=email).values_list("role", flat=True)

            if "student" in existing_roles and role == "student":
                raise forms.ValidationError(
                    "This email is already registered as a student."
                )
            if "teacher" in existing_roles and role == "teacher":
                raise forms.ValidationError(
                "This email is already registered as a teacher."
                )
        return cleaned_data

class CourseForm(forms.ModelForm):
    class Meta :
        model=Course
        fields=['name','slug','description','price','discount','length','img']
        
class paymentForm(forms.ModelForm):
    class Meta :
        model=Payment
        fields='__all__'
        
class TagForm(forms.ModelForm):
    class Meta :
        model=Tag
        fields='__all__'
        
class LearningForm(forms.ModelForm):
    class Meta :
        model=Learning
        fields='__all__'
        
class PrerequisitesForm(forms.ModelForm):
    class Meta :
        model=Prerequisites
        fields='__all__'
        
class VideoForm(forms.ModelForm):
    class Meta :
        model=Video
        fields=['title','serial_number','video_id']
        

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)


