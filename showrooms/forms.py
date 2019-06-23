from django import forms
from django.forms import ModelForm
from .models import Showroom


class ShowroomRegistrationForm(forms.Form):
    email = forms.EmailField(label="Adresse email",
                             error_messages={'required': "Entrer un email", 'invalid': "Le mail n'est pas valide"})
    showroom_name = forms.CharField(min_length=2, label="Nom de votre boutique",
                                    error_messages={'required': "Entrer le nom de la boutique",
                                                    'min_length': "Le nom de la boutique doit avoir " +
                                                                  "au moins 2 caractères"})
    password = forms.CharField(min_length=5, widget=forms.PasswordInput, label='Mot de passe',
                               error_messages={'required': "Entrer un mot de passe",
                                               'min_length': "Le mot de passe doit avoir au moins 5 caractères"})
    terms = forms.BooleanField(widget=forms.CheckboxInput(), required=True,
                               error_messages={'required': 'Vous devez accepté les termes'})


class ShowroomEditInformationForm(ModelForm):
    old_password = forms.CharField(min_length=5, widget=forms.PasswordInput, required=False, label="Ancien mot de passe")
    new_password = forms.CharField(min_length=5, widget=forms.PasswordInput, required=False, label="Nouveau mot de passe")

    class Meta:
        model = Showroom
        fields = ['name', 'website', 'slogan', 'description', 'phone_number_1', 'phone_number_2', 'avatar', 'address']
