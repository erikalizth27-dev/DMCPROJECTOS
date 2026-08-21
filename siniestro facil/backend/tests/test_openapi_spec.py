from pathlib import Path
import unittest

import yaml


class OpenApiSpecTest(unittest.TestCase):
    def test_contract_is_valid_yaml_and_has_required_operations(self) -> None:
        path = Path(__file__).resolve().parents[2] / "12_api_backend_openapi.yaml"
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual("3.1.0", document["openapi"])
        operations = {
            value["operationId"]
            for path_item in document["paths"].values()
            for method, value in path_item.items()
            if method in {"get", "post", "put", "patch", "delete"}
        }
        self.assertIn("crearSiniestro", operations)
        self.assertIn("cambiarEstadoSiniestro", operations)
        self.assertIn("registrarPago", operations)
        self.assertEqual(len(operations), len(set(operations)))


if __name__ == "__main__":
    unittest.main()
