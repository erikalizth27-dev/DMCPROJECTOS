import os
import unittest
from unittest.mock import patch

from siniestro_facil.config import Settings


class SettingsTest(unittest.TestCase):
    def test_reports_missing_database_url(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_environment()
        self.assertIn("DATABASE_URL no configurada", settings.readiness_errors())

    def test_accepts_expected_schema(self) -> None:
        settings = Settings(database_url="postgresql+psycopg://example", database_schema="siniestro_facil")
        self.assertEqual([], settings.readiness_errors())

    def test_reports_missing_identity_configuration(self) -> None:
        settings = Settings()
        self.assertEqual(
            ["IDENTITY_ISSUER no configurado", "IDENTITY_AUDIENCE no configurada"],
            settings.identity_configuration_errors(),
        )

    def test_reads_identity_configuration_from_environment(self) -> None:
        with patch.dict(
            os.environ,
            {
                "IDENTITY_ISSUER": "https://identity.example.invalid",
                "IDENTITY_AUDIENCE": "siniestro-facil-backend",
            },
            clear=True,
        ):
            settings = Settings.from_environment()
        self.assertEqual([], settings.identity_configuration_errors())


if __name__ == "__main__":
    unittest.main()
