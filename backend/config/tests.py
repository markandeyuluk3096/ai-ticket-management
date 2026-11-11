from django.test import SimpleTestCase, override_settings


class CORSMiddlewareTests(SimpleTestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:5173"])
    def test_allowed_frontend_origin_receives_cors_header(self):
        response = self.client.options(
            "/",
            HTTP_ORIGIN="http://localhost:5173",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:5173")

    @override_settings(CORS_ALLOWED_ORIGINS=["http://localhost:5173"])
    def test_unlisted_origin_does_not_receive_cors_header(self):
        response = self.client.get("/", HTTP_ORIGIN="https://untrusted.example")

        self.assertNotIn("Access-Control-Allow-Origin", response)
