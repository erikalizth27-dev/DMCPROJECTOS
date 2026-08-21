import unittest

from siniestro_facil.domain.idempotency import fingerprint_request, validate_idempotency_key


class IdempotencyTest(unittest.TestCase):
    def test_fingerprint_is_independent_of_key_order(self) -> None:
        self.assertEqual(fingerprint_request({"a": 1, "b": 2}), fingerprint_request({"b": 2, "a": 1}))

    def test_rejects_short_key(self) -> None:
        with self.assertRaises(ValueError):
            validate_idempotency_key("short")

    def test_accepts_valid_key(self) -> None:
        key = "siniestro-2026-0001"
        self.assertEqual(key, validate_idempotency_key(key))


if __name__ == "__main__":
    unittest.main()

