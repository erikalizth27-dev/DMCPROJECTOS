import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError

from siniestro_facil.db import database_readiness_errors


class DatabaseReadinessTest(unittest.TestCase):
    def test_database_and_schema_are_ready(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.scalar_one_or_none.return_value = "siniestro_facil"
        engine = MagicMock()
        engine.connect.return_value.__enter__.return_value = connection

        self.assertEqual([], database_readiness_errors(engine, "siniestro_facil"))
        self.assertEqual(2, connection.execute.call_count)

    def test_reports_missing_schema(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.scalar_one_or_none.return_value = None
        engine = MagicMock()
        engine.connect.return_value.__enter__.return_value = connection

        self.assertEqual(
            ["El esquema requerido siniestro_facil no existe"],
            database_readiness_errors(engine, "siniestro_facil"),
        )

    def test_hides_database_exception_details(self) -> None:
        engine = MagicMock()
        engine.connect.side_effect = OperationalError("statement", {}, Exception("secret"))

        self.assertEqual(
            ["No fue posible conectar con PostgreSQL"],
            database_readiness_errors(engine, "siniestro_facil"),
        )


if __name__ == "__main__":
    unittest.main()
