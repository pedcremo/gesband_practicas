from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import translation

from apps.associations.models import Association, AssociationAccess, AssociationRole
from apps.members.models import Instrument, Member, MemberInstrument, Section


class MembersPerSectionTests(TestCase):
    def setUp(self):
        self.association = Association.objects.create(name="Banda Test", slug="banda-test")
        self.other_association = Association.objects.create(name="Otra Banda", slug="otra-banda")
        self.woodwind = Section.objects.get(code="woodwind")
        self.brass = Section.objects.get(code="brass")
        self.percussion = Section.objects.get(code="percussion")
        self.flute = self.instrument("G1 flauta", self.woodwind)
        self.clarinet = self.instrument("G1 clarinete", self.woodwind)
        self.trumpet = self.instrument("G1 trompeta", self.brass)

        account = get_user_model().objects.create_user(
            username="junta@example.invalid", email="junta@example.invalid", password="secret-password"
        )
        access = AssociationAccess.objects.create(association=self.association, account=account)
        AssociationRole.objects.create(access=access, role=AssociationRole.Role.BOARD)
        self.client = Client()
        self.client.force_login(account)
        self.url = f"/panel/members/?association_id={self.association.id}"

    def instrument(self, name, section, association=None):
        return Instrument.objects.create(association=association or self.association, name=name, section=section)

    def musician(self, first_name, *instruments, association=None, **extra):
        member = Member.objects.create(
            association=association or self.association, first_name=first_name, last_name="Test", **extra
        )
        for instrument in instruments:
            MemberInstrument.objects.create(member=member, instrument=instrument)
        return member

    def counts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        return {section.code: section.active_members for section in response.context["section_counts"]}

    def test_counts_active_members_per_section(self):
        self.musician("Anna", self.flute)
        self.musician("Pau", self.clarinet)
        self.musician("Marta", self.trumpet)

        self.assertEqual(self.counts(), {"woodwind": 2, "brass": 1})

    def test_member_with_two_instruments_in_one_section_counts_once(self):
        self.musician("Anna", self.flute, self.clarinet)

        self.assertEqual(self.counts(), {"woodwind": 1})

    def test_member_in_two_sections_counts_in_both(self):
        self.musician("Anna", self.flute, self.trumpet)

        self.assertEqual(self.counts(), {"woodwind": 1, "brass": 1})

    def test_inactive_members_are_not_counted(self):
        self.musician("Anna", self.flute)
        self.musician("Pau", self.flute, status=Member.Status.INACTIVE)

        self.assertEqual(self.counts(), {"woodwind": 1})

    def test_members_of_another_association_are_not_counted(self):
        self.musician("Anna", self.flute)
        foreign_drum = self.instrument("G1 bombo", self.percussion, association=self.other_association)
        foreign_flute = self.instrument("G1 flauta", self.woodwind, association=self.other_association)
        self.musician("Intrusa", foreign_drum, association=self.other_association)
        self.musician("Intruso", foreign_flute, association=self.other_association)

        self.assertEqual(self.counts(), {"woodwind": 1})

    def test_list_shows_counters_above_the_table(self):
        self.musician("Anna", self.flute)
        self.musician("Pau", self.clarinet)
        self.musician("Marta", self.trumpet)

        response = self.client.get(self.url)
        html = response.content.decode()
        with translation.override(response.wsgi_request.LANGUAGE_CODE):
            woodwind, brass = self.woodwind.label, self.brass.label

        self.assertIn(f"{brass} 1 · {woodwind} 2", html)
        self.assertLess(html.index(f"{woodwind} 2"), html.index("<table>"))

    def test_no_counters_without_active_musicians(self):
        self.musician("Pau", self.flute, status=Member.Status.INACTIVE)

        self.assertEqual(self.counts(), {})
