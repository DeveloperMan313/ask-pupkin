from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q, F, Sum, Value
from django.db.models.functions import Cast


class ProfileManager(models.query.QuerySet):
    def best(self, count: int = 10):
        return self.annotate(answer_count=Count('user__answer', distinct=True)).order_by('-answer_count')[:count]


class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    nickname = models.CharField(null=False, unique=True, max_length=50)
    picture = models.ImageField(null=True)

    objects = ProfileManager.as_manager()

    def __str__(self):
        return self.nickname


class TagManager(models.query.QuerySet):
    def popular(self, count: int = 10):
        return self.annotate(times_used=Count('question', distinct=True)).order_by('-times_used')[:count]


class Tag(models.Model):
    name = models.CharField(null=False, unique=True, max_length=50)

    objects = TagManager.as_manager()

    def __str__(self):
        return self.name


class QuestionManager(models.query.QuerySet):
    def with_rating(self):
        return self \
            .annotate(likes=Count('question_rating', distinct=True, filter=Q(question_rating__is_positive=True))) \
            .annotate(dislikes=Count('question_rating', distinct=True, filter=Q(question_rating__is_positive=False))) \
            .annotate(rating=F('likes') - F('dislikes'))

    def with_answer_count(self):
        return self.annotate(answer_count=Count('answer', distinct=True))
    
    def with_user_rating(self, user: User):
        if user.is_authenticated:
            return self.annotate(user_rating=Sum(-1 + 2 * Cast('question_rating__is_positive', models.IntegerField()), default=0, filter=Q(question_rating__user=user), distinct=True))
        else:
            return self.annotate(user_rating=Value(0))

    def new(self):
        return self.with_rating().with_answer_count().order_by('-pk')

    def hot(self):
        return self.with_rating().with_answer_count().order_by('-rating')

    def by_tag_name(self, tag_name: str):
        return self.new().filter(tags__in=Tag.objects.filter(name=tag_name))

    def by_id(self, question_id: int):
        return self.with_rating().get(pk=question_id)


class Question(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(null=False, max_length=150)
    text = models.TextField(null=False, max_length=5000)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = QuestionManager.as_manager()

    def init_tag_list(self):
        self.tag_list = tuple(map(str, self.tags.all()))


class AnswerManager(models.query.QuerySet):
    def with_rating(self):
        return self \
            .annotate(likes=Count('answer_rating', distinct=True, filter=Q(answer_rating__is_positive=True))) \
            .annotate(dislikes=Count('answer_rating', distinct=True, filter=Q(answer_rating__is_positive=False))) \
            .annotate(rating=F('likes') - F('dislikes'))

    def with_user_rating(self, user: User):
        if user.is_authenticated:
            return self.annotate(user_rating=Sum(-1 + 2 * Cast('answer_rating__is_positive', models.IntegerField()), default=0, filter=Q(answer_rating__user=user), distinct=True))
        else:
            return self.annotate(user_rating=Value(0))

    def by_question_id(self, question_id: int):
        return self.with_rating().filter(question__id=question_id).order_by('-is_correct', '-rating')


class Answer(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(null=False, max_length=5000)
    is_correct = models.BooleanField(null=False, default=False)

    objects = AnswerManager.as_manager()


class QuestionRating(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='question_rating')
    is_positive = models.BooleanField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'], name='unique_question_rating'
            )
        ]


class AnswerRating(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='answer_rating')
    is_positive = models.BooleanField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'answer'], name='unique_answer_rating'
            )
        ]
