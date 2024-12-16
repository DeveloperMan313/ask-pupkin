from django import forms
from django.contrib.auth import authenticate
from .models import *


class SignupForm(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=50)
    email = forms.EmailField(label='Email', max_length=100)
    nickname = forms.CharField(label='Nickname', min_length=4, max_length=50)
    password = forms.CharField(
        label='Password',
        min_length=8,
        max_length=50,
        widget=forms.PasswordInput(),
    )
    password_repeat = forms.CharField(
        label='Repeat password',
        min_length=8,
        max_length=50,
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        nickname = cleaned_data.get('nickname')
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if not all(c.isalnum() or c in '_@+.-' for c in username):
            self.add_error(
                'username',
                'Username must only contain letters, numbers and "_@+.-" symbols',
            )
        elif User.objects.filter(username=username).first():
            self.add_error('username', 'Username already taken')

        if not all(c.isalnum() or c in '_@+.- ' for c in nickname):
            self.add_error(
                'nickname',
                'Nickname must only contain letters, numbers, "_@+.-" symbols and spaces',
            )
        elif Profile.objects.filter(nickname=nickname).first():
            self.add_error('nickname', 'Nickname already taken')

        if not (
            any(c.isupper() for c in password) and any(c.isnumeric() for c in password)
        ):
            self.add_error(
                'password',
                'Password must contain at least one uppercase letter and one digit',
            )
        elif password != password_repeat:
            self.add_error('password_repeat', 'Passwords do not match')
            self.fields['password'].widget = forms.PasswordInput(render_value=True)

        if len(self.errors) == 0:
            self.user = User(username=username, email=email)
            self.password = password
            self.profile = Profile(user=self.user, nickname=nickname)

    def save(self):
        self.user.set_password(self.password)
        self.user.save()
        self.profile.save()

    def get_user(self):
        return self.user


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=50)
    password = forms.CharField(
        label='Password', min_length=8, max_length=50, widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()

        self.user = authenticate(
            username=cleaned_data.get('username'),
            password=cleaned_data.get('password'),
        )

        if self.user is None:
            self.add_error('', 'Incorrect username or password')

    def get_user(self):
        return self.user
