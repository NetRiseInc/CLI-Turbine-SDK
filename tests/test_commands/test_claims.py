import json
import pytest
from unittest.mock import patch, MagicMock
from nrcli.commands.claims import decode_jwt_payload, run


class TestDecodeJwtPayload:
    def test_decodes_valid_jwt(self):
        # eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0 is:
        # {"sub":"1234567890","name":"Test User","iat":1516239022}
        token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0."
            "signature"
        )

        result = decode_jwt_payload(token)

        assert result["sub"] == "1234567890"
        assert result["name"] == "Test User"
        assert result["iat"] == 1516239022

    def test_handles_padding(self):
        # Test with payload that needs padding
        token = (
            "eyJhbGciOiJIUzI1NiJ9."
            "eyJ0ZXN0IjoidmFsdWUifQ."
            "sig"
        )

        result = decode_jwt_payload(token)

        assert result["test"] == "value"

    def test_invalid_jwt_format_raises(self):
        with pytest.raises(ValueError, match="Invalid JWT format"):
            decode_jwt_payload("not.a.valid.jwt.token")

    def test_too_few_parts_raises(self):
        with pytest.raises(ValueError, match="Invalid JWT format"):
            decode_jwt_payload("only.two")


class TestRunCommand:
    def test_prints_claims_as_json(self, mock_client, capsys):
        run(mock_client)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["sub"] == "1234567890"
        assert output["name"] == "Test User"
