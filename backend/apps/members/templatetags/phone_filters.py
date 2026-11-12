import re

from django import template

register = template.Library()


@register.filter
def phone_link(value):
    if not value:
        return ""
    if value == "1234":
        return ""
    return re.sub(r"[\s-]", "", str(value))

