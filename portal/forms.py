# portal/forms.py
from django import forms

class RegisterForm(forms.Form):
    institute_id = forms.CharField(max_length=64)
    institute_mail = forms.EmailField()
    name = forms.CharField()
    nature = forms.ChoiceField(choices=[('bachelors','bachelors'),('masters','masters'),('phd','phd'),('faculty','faculty')])
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    institute_mail = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class UploadBookForm(forms.Form):
    book_name = forms.CharField()
    authors = forms.CharField(required=False)
    genre = forms.CharField(required=False)
    branch = forms.CharField()
    pdf = forms.FileField()
