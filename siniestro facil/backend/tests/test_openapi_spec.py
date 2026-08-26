from pathlib import Path
import unittest

import yaml


class OpenApiSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).resolve().parents[2] / "12_api_backend_openapi.yaml"
        cls.document = yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_contract_is_valid_yaml_and_has_required_operations(self) -> None:
        self.assertEqual("3.1.0", self.document["openapi"])
        operations = {
            value["operationId"]
            for path_item in self.document["paths"].values()
            for method, value in path_item.items()
            if method in {"get", "post", "put", "patch", "delete"}
        }
        self.assertIn("crearSiniestro", operations)
        self.assertIn("cambiarEstadoSiniestro", operations)
        self.assertIn("solicitarAsistencia", operations)
        self.assertIn("prepararSolicitudPago", operations)
        self.assertIn("autorizarSolicitudPago", operations)
        self.assertNotIn("registrarPago", operations)
        self.assertEqual(11, len(operations))

    def test_payment_contract_separates_preparation_and_authorization(self) -> None:
        paths = self.document["paths"]
        prepare = paths["/siniestros/{siniestroId}/solicitudes-pago"]["post"]
        authorize = paths["/solicitudes-pago/{solicitudPagoId}/autorizacion"]["post"]

        self.assertEqual("prepararSolicitudPago", prepare["operationId"])
        self.assertEqual("autorizarSolicitudPago", authorize["operationId"])
        self.assertIn("403", authorize["responses"])
        confirmation = self.document["components"]["schemas"]["AutorizarSolicitudPago"]
        self.assertTrue(confirmation["properties"]["confirmacionHumana"]["const"])

    def test_alert_contract_exposes_summary_and_detail_variants(self) -> None:
        items = self.document["paths"]["/siniestros/{siniestroId}/alertas"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]
        references = {item["$ref"] for item in items["oneOf"]}
        self.assertEqual(
            {
                "#/components/schemas/AlertaResumen",
                "#/components/schemas/AlertaDetalle",
            },
            references,
        )

    def test_commands_and_error_responses_have_synthetic_examples(self) -> None:
        schemas = self.document["components"]["schemas"]
        command_schemas = {
            "CrearSiniestro",
            "RegistrarEvidencia",
            "CambiarEstado",
            "SolicitarAsistencia",
            "RegistrarPresupuesto",
            "RevisarAlerta",
            "PrepararSolicitudPago",
            "AutorizarSolicitudPago",
        }

        for schema_name in command_schemas:
            self.assertIn("example", schemas[schema_name], schema_name)

        responses = self.document["components"]["responses"]
        for response_name, response in responses.items():
            media_type = response["content"]["application/json"]
            self.assertIn("example", media_type, response_name)
            serialized = str(media_type["example"]).lower()
            self.assertNotIn("password", serialized)
            self.assertNotIn("secret", serialized)


if __name__ == "__main__":
    unittest.main()
