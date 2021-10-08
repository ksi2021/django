from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core import validators

from .models import UserData


class RegForm(UserCreationForm):
    first_name = forms.RegexField(label="Имя", regex=r'^[а-яА-ЯёЁ\s]+$', max_length=30,
                                  error_messages={'invalid': 'Только символы русского алфавита.'},
                                  help_text='Обязательное поле. Не более 30 символов. Только буквы русского алфавита.')

    class Meta:
        model = UserData
        fields = ('username', 'first_name', 'phone')


class UpdateUserData(forms.ModelForm):
    first_name = forms.RegexField(label="Имя", regex=r'^[а-яА-ЯёЁ\s]+$', max_length=30,
                                  error_messages={'invalid': 'Только символы русского алфавита.'},
                                  help_text='Обязательное поле. Не более 30 символов. Только буквы русского алфавита.')

    class Meta:
        model = UserData
        fields = ('username', 'first_name', 'phone')
