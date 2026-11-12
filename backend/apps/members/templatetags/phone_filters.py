import re

from django import template

register = template.Library()


@register.filter
def phone_link(value):
    if not value:
        return ""

    return re.sub(r"[\s-]", "", str(value))
