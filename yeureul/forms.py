from django import forms


class LoginForm(forms.Form):
    email_username = forms.CharField(label="Nom d'utilisateur ou email",
                                     error_messages={'required': "Entrer un nom d'utilisateur ou email"})
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe',
                               error_messages={'required': "Entrer un mot de passe"})
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
