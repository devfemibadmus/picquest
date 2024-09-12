from django import forms

class SignupForm(forms.Form):
    email = forms.EmailField()
    fullName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class SigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class VerificatonForm(forms.Form):
    theFile = forms.FileField()
    bankName = forms.CharField()
    accountNum = forms.CharField()
    accountName = forms.CharField()
