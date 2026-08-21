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


if __name__ == "__main__":
    unittest.main()

