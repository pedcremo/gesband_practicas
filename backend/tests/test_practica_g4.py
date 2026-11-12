
from django.test import SimpleTestCase, override_settings


class VersionEndpointTests(SimpleTestCase):

    def test_get_returns_name_and_version_without_login(self):
        response = self.client.get("/version/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"name": "Gesband", "version": "0.1.0"}
        )

    def test_post_returns_method_not_allowed(self):
        response = self.client.post("/version/")

        self.assertEqual(response.status_code, 405)

    @override_settings(GESBAND_VERSION="9.9.9")
    def test_version_can_be_overridden(self):
        response = self.client.get("/version/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"name": "Gesband", "version": "9.9.9"}
        )
