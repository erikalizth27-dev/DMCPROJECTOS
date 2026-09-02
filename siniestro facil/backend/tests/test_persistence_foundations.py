import unittest

from sqlalchemy import create_engine, text

from siniestro_facil.persistence.models import Base, SCHEMA
from siniestro_facil.persistence.session import (
    create_session_factory,
    transactional_session,
)


class PersistenceModelsTest(unittest.TestCase):
    def test_sprint_one_tables_are_mapped_to_expected_schema(self) -> None:
        expected = {
            "asegurado",
            "reportante",
            "poliza",
            "vehiculo",
            "cobertura",
            "siniestro",
            "evento_linea_tiempo",
            "solicitud_idempotente",
            "usuario_interno",
            "proveedor",
            "asignacion_siniestro",
            "identidad_actor",
            "evidencia",
            "solicitud_evidencia_idempotente",
            "asistencia",
            "solicitud_asistencia_idempotente",
        }
        mapped = {
            table.name
            for table in Base.metadata.tables.values()
            if table.schema == SCHEMA
        }
        self.assertEqual(expected, mapped)

    def test_siniestro_exposes_optimistic_version(self) -> None:
        table = Base.metadata.tables[f"{SCHEMA}.siniestro"]
        self.assertIn("version", table.columns)
        self.assertFalse(table.columns.version.nullable)


class TransactionalSessionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        with self.engine.begin() as connection:
            connection.execute(text("CREATE TABLE sample (value INTEGER NOT NULL)"))
        self.factory = create_session_factory(self.engine)

    def count_rows(self) -> int:
        with self.engine.connect() as connection:
            return connection.execute(text("SELECT count(*) FROM sample")).scalar_one()

    def test_commits_successful_unit_of_work(self) -> None:
        with transactional_session(self.factory) as session:
            session.execute(text("INSERT INTO sample (value) VALUES (1)"))
        self.assertEqual(1, self.count_rows())

    def test_rolls_back_failed_unit_of_work(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "fallo controlado"):
            with transactional_session(self.factory) as session:
                session.execute(text("INSERT INTO sample (value) VALUES (1)"))
                raise RuntimeError("fallo controlado")
        self.assertEqual(0, self.count_rows())


if __name__ == "__main__":
    unittest.main()
