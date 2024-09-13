from django import forms

class SignupForm(forms.Form):
    email = forms.EmailField()
    fullName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class SigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
