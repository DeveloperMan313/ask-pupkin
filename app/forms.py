from django import forms
from django.contrib.auth import authenticate
from django.db import transaction
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
    profile_picture = forms.ImageField(label='Profile picture', required=False)

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

    @transaction.atomic
    def save(self) -> User:
        cleaned_data = super().clean()
        self.user.set_password(self.password)
        self.user.save()
        profile_picture = cleaned_data.get('profile_picture')
        if profile_picture:
            profile_picture.name = self.user.password[-64:]
            self.profile.picture = profile_picture
        self.profile.save()
        return self.user


class SettingsForm(forms.Form):
    username = forms.CharField(label='Username', min_length=4, max_length=50)
    email = forms.EmailField(label='Email', max_length=100)
    nickname = forms.CharField(label='Nickname', min_length=4, max_length=50)
    profile_picture = forms.ImageField(label='Profile picture', required=False)

    def __init__(self, user: User, **args):
        super().__init__(**args)
        self.user = user
        self.profile = Profile.objects.get(user=user)

        self.fields['username'].initial = self.user.username
        self.fields['email'].initial = self.user.email
        self.fields['nickname'].initial = self.profile.nickname

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        nickname = cleaned_data.get('nickname')

        if not all(c.isalnum() or c in '_@+.-' for c in username):
            self.add_error(
                'username',
                'Username must only contain letters, numbers and "_@+.-" symbols',
            )
        elif User.objects.filter(username=username).exclude(pk=self.user.pk).first():
            self.add_error('username', 'Username already taken')

        if not all(c.isalnum() or c in '_@+.- ' for c in nickname):
            self.add_error(
                'nickname',
                'Nickname must only contain letters, numbers, "_@+.-" symbols and spaces',
            )
        elif (
            Profile.objects.filter(nickname=nickname)
            .exclude(pk=self.profile.pk)
            .first()
        ):
            self.add_error('nickname', 'Nickname already taken')

    @transaction.atomic
    def save(self):
        cleaned_data = super().clean()

        profile_picture = cleaned_data.get('profile_picture')
        if profile_picture:
            profile_picture.name = self.user.password[-64:]
            self.profile.picture = profile_picture

        self.user.username = cleaned_data.get('username')
        self.user.email = cleaned_data.get('email')
        self.profile.nickname = cleaned_data.get('nickname')

        self.user.save()
        self.profile.save()


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


class QuestionForm(forms.Form):
    title = forms.CharField(label='Title', min_length=10, max_length=150)
    text = forms.CharField(
        label='Text',
        max_length=5000,
        widget=forms.Textarea(attrs={'rows': '5'}),
    )
    tags = forms.CharField(label='Tags')

    def __init__(
        self, user: User = None, min_tag_len: int = 4, max_tags: int = 3, **args
    ):
        super().__init__(**args)
        self.user = user
        self.min_tag_len = min_tag_len
        self.max_tags = max_tags

    def clean(self):
        cleaned_data = super().clean()
        tag_strs = cleaned_data.get('tags').split()

        if len(tag_strs) > self.max_tags:
            self.add_error('tags', 'Maximum {} tags allowed'.format(self.max_tags))
        elif not all(len(tag) >= self.min_tag_len for tag in tag_strs):
            self.add_error(
                'tags',
                'Tags must be at least {} characters long'.format(self.min_tag_len),
            )
        elif not all(s.isalnum() or s in '_ ' for s in cleaned_data.get('tags')):
            self.add_error(
                'tags', 'Tags must only contain letters, numbers and underscores'
            )

        if len(self.errors) == 0:
            self.tags = (Tag.objects.get_or_create(name=name)[0] for name in tag_strs)

    @transaction.atomic
    def save(self) -> int:
        cleaned_data = super().clean()
        question = Question(
            user=self.user,
            title=cleaned_data.get('title'),
            text=cleaned_data.get('text'),
        )
        question.save()
        question.tags.set(self.tags)
        return question.pk


class AnswerForm(forms.Form):
    text = forms.CharField(
        label='Answer',
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                'cols': '30',
                'rows': '5',
                'placeholder': 'Enter your answer...',
            }
        ),
    )

    def __init__(self, user: User = None, question: Question = None, **args):
        super().__init__(**args)
        self.user = user
        self.question = question

    def save(self) -> int:
        cleaned_data = super().clean()
        answer = Answer(
            user=self.user, question=self.question, text=cleaned_data.get('text')
        )
        answer.save()
        return answer.pk
