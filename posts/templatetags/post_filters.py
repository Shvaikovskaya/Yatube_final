import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="post_saved")
def post_saved(user, id):
    return user.saved_posts.filter(id=id).count() > 0


@register.filter(name="search_result", is_safe=True)
def search_result(text, query):
    words = query.split()
    for word in words:
        text = text.replace(word,
                            ("<span style='background: #D9FFAD'>"
                             f"{word}"
                             "</span>"))
    return mark_safe(text)


@register.filter(name="hashtag", is_safe=True)
def search_result(text):
    tags = re.findall(r"(#\w+)", text)
    for tag in tags:
        text = text.replace(tag,
                            ("<a href='/hashtag/"
                             f"{tag[1:]}"
                             "'>"
                             f"{tag}"
                             "</a>"))
    return mark_safe(text)
