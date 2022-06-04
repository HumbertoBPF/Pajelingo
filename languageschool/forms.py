from django import forms

class FormPicture(forms.Form):
    '''Form to update profile picture'''
    picture = forms.ImageField(label='Change profile picture', required=False)