"""Duración legible de una actividad para las plantillas del panel."""

from datetime import timezone as datetime_timezone

from django import template
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def duration(starts_at, ends_at):
    """Devuelve horas y minutos entre dos fechas, o vacío si no son válidas."""
    if starts_at is None or ends_at is None:
        return ""

    try:
        if starts_at.utcoffset() is not None and ends_at.utcoffset() is not None:
            starts_at = starts_at.astimezone(datetime_timezone.utc)
            ends_at = ends_at.astimezone(datetime_timezone.utc)
        seconds = (ends_at - starts_at).total_seconds()
    except (AttributeError, TypeError, ValueError):
        return ""

    if seconds < 0:
        return ""

    minutes = int(seconds // 60)
    hours, remaining_minutes = divmod(minutes, 60)
    if hours and remaining_minutes:
        return _("%(hours)s h %(minutes)s min") % {
            "hours": hours,
            "minutes": remaining_minutes,
        }
    if hours:
        return _("%(hours)s h") % {"hours": hours}
    return _("%(minutes)s min") % {"minutes": remaining_minutes}
