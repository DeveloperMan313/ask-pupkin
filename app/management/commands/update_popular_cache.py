from django.core.management.base import BaseCommand
from django.core.cache import cache
from ...models import Profile, Tag


class Command(BaseCommand):
    help = 'Update popular users and popular tags lists in cache'

    def add_arguments(self, parser):
        parser.add_argument('--ttl', type=int)

    def handle(self, *args, **kwargs):
        if kwargs['ttl'] is None:
            print('Please, supply --ttl [cache TTL]')
            return
        cache_ttl = kwargs['ttl']

        popular_users = Profile.objects.best()
        popular_tags = Tag.objects.popular()
        cache.set('popular_users', popular_users, timeout=cache_ttl)
        cache.set('popular_tags', popular_tags, timeout=cache_ttl)
        print('Cache updated')
