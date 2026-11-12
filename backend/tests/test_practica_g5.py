from django.test import TestCase


class Group5ContactFilterTests(TestCase):
    def test_format_tel_filter_removes_spaces_and_dashes(self):
        """Comprueba que se quiten espacios y guiones para los enlaces tel:"""
        try:
            from apps.members.templatetags.member_filters import format_tel
            self.assertEqual(format_tel("+34 600 000 001"), "+34600000001")
            self.assertEqual(format_tel("600-00-00-01"), "600000001")
            self.assertEqual(format_tel(""), "")
        except ModuleNotFoundError:
            self.fail("El filtro 'format_tel' en 'apps.members.templatetags.member_filters' aún no ha sido implementado por el Rol A.")
