from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(null=False, unique=True, max_length=50)


class Tag(models.Model):
    name = models.CharField(null=False, max_length=50)


class Question(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(null=False, max_length=150)
    text = models.TextField(null=False, max_length=5000)
    tags = models.ManyToManyField(Tag)


class Answer(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(null=False, max_length=5000)
    is_correct = models.BooleanField(null=False, default=False)


class QuestionRating(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_positive = models.BooleanField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'], name='unique_question_rating'
            )
        ]


class AnswerRating(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_positive = models.BooleanField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'answer'], name='unique_answer_rating'
            )
        ]
