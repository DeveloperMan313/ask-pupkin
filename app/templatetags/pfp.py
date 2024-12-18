from django import template
from ask_pupkin.settings import MEDIA_URL, STATIC_URL

register = template.Library()


@register.filter
def get_pfp_url(profile_picture):
    if profile_picture:
        return MEDIA_URL + profile_picture.name
    else:
        return STATIC_URL + 'images/placeholder.png'
