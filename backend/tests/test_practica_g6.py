"""Pràctica 1 · Grup 6 · Duració de l'activitat.

Contracte acordat amb la persona A (codi):
- Fitxer: backend/apps/activities/templatetags/activity_duration.py
- Filtre: ``duration``, rep una activitat i torna el text («45 min», «2 h»,
  «2 h 30 min») o una cadena buida si no hi ha duració.
- Ús en la plantilla: {% load activity_duration %} ... {{ activity|duration }}
"""

from datetime import timedelta
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.utils import timezone

from apps.activities.models import Activity
from apps.associations.models import Association, AssociationAccess, AssociationRole


def fake_activity(minutes=None, starts_at=None):
    """Activitat «de mentida» sense base de dades: només starts_at i ends_at."""
    starts_at = starts_at or timezone.now()
    ends_at = None if minutes is None else starts_at + timedelta(minutes=minutes)
    return SimpleNamespace(starts_at=starts_at, ends_at=ends_at)


class DurationFilterTests(SimpleTestCase):
    def duration(self, activity):
        # L'import va ací dins perquè, mentre no existisca el filtre,
        # fallen aquestes proves però no tot el fitxer.
        from apps.activities.templatetags.activity_duration import duration

        return duration(activity)

    def test_only_minutes(self):
        self.assertEqual(self.duration(fake_activity(minutes=45)), "45 min")

    def test_only_hours(self):
        self.assertEqual(self.duration(fake_activity(minutes=120)), "2 h")

    def test_hours_and_minutes(self):
        self.assertEqual(self.duration(fake_activity(minutes=150)), "2 h 30 min")

    def test_without_end_shows_nothing(self):
        self.assertEqual(self.duration(fake_activity(minutes=None)), "")

    def test_end_before_start_shows_nothing(self):
        self.assertEqual(self.duration(fake_activity(minutes=-30)), "")


class ActivityDetailDurationTests(TestCase):
    def setUp(self):
        self.association = Association.objects.create(name="Banda Test", slug="banda-test")
        email = "junta-g6@example.invalid"
        self.board = get_user_model().objects.create_user(username=email, email=email, password="secret-password")
        access = AssociationAccess.objects.create(association=self.association, account=self.board)
        AssociationRole.objects.create(access=access, role=AssociationRole.Role.BOARD)
        self.web = Client()
        self.web.force_login(self.board)
        self.starts_at = timezone.now() + timedelta(days=7)

    def activity(self, ends_at=None):
        return Activity.objects.create(
            association=self.association,
            created_by=self.board,
            kind=Activity.Kind.REHEARSAL,
            title="Assaig general",
            starts_at=self.starts_at,
            ends_at=ends_at,
        )

    def detail(self, activity):
        return self.web.get(f"/panel/activities/{activity.id}/?association_id={self.association.id}")

    def test_detail_shows_the_duration(self):
        activity = self.activity(ends_at=self.starts_at + timedelta(hours=2, minutes=30))

        page = self.detail(activity)

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "2 h 30 min")

    def test_detail_without_end_shows_no_duration(self):
        activity = self.activity(ends_at=None)

        page = self.detail(activity)

        self.assertEqual(page.status_code, 200)
        # Ni l'etiqueta «Duració» (ca) ni «Duración» (es) han d'aparéixer.
        self.assertNotContains(page, "Duraci")
