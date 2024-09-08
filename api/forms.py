from django import forms

class SignupForm(forms.Form):
    email = forms.EmailField()
    last_name = forms.CharField()
    first_name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class VerificatonForm(forms.Form):
    theFile = forms.FileField()
    bankName = forms.CharField()
    accountNum = forms.CharField()
    accountName = forms.CharField()
