from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q, F, Sum, Value, Case, When
from django.db.models.functions import Cast
from datetime import datetime, timedelta


class ProfileManager(models.query.QuerySet):
    def best(self, count: int = 10, stats_days: int = 7):
        stats_days_ago = datetime.now() - timedelta(days=stats_days)

        question_ratings = Question.objects.with_rating().filter(
            timestamp__gte=stats_days_ago
        ).values('user', 'rating')

        answer_ratings = Answer.objects.with_rating().filter(
            timestamp__gte=stats_days_ago
        ).values('user', 'rating')

        user_rating_sum = (
            (
                sum(
                    q_u_r['rating']
                    for q_u_r in question_ratings
                    if q_u_r['user'] == user['pk']
                )
                + sum(
                    a_u_r['rating']
                    for a_u_r in answer_ratings
                    if a_u_r['user'] == user['pk']
                ),
                user['pk'],
            )
            for user in User.objects.all().values('pk')
        )

        pk_list = tuple(user[1] for user in sorted(user_rating_sum, reverse=True)[:count])
        preserved = Case(*[When(user__pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return self.filter(user__pk__in=pk_list).order_by(preserved)


class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    nickname = models.CharField(null=False, unique=True, max_length=50)
    picture = models.ImageField(null=True)

    objects = ProfileManager.as_manager()

    def __str__(self):
        return self.nickname


class TagManager(models.query.QuerySet):
    def popular(self, count: int = 10, stats_days: int = 90):
        stats_days_ago = datetime.now() - timedelta(days=stats_days)
        return self.annotate(times_used=Count('question', filter=Q(question__timestamp__gte=stats_days_ago), distinct=True)).order_by('-times_used')[:count]


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
    timestamp = models.DateTimeField(auto_now_add=True)

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
    timestamp = models.DateTimeField(auto_now_add=True)

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
