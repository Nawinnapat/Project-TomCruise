from __future__ import annotations

import base64
import gzip
import json
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from scraper.dbd_crypto import decode_jwt_payload, decrypt_envelope, is_encrypted_envelope


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _jwt(payload: dict[str, Any]) -> str:
    return ".".join([_b64url(b'{"alg":"none"}'), _b64url(json.dumps(payload).encode()), ""])


def test_decode_jwt_payload_reads_enc_key_and_exp():
    token = _jwt({"encKey": _b64url(b"secret"), "exp": 123})

    assert decode_jwt_payload(token) == {"encKey": _b64url(b"secret"), "exp": 123}


def test_decrypt_envelope_decodes_gzipped_json_payload():
    api_path = "/api/v1/company-profiles/infos"
    ikm = b"test encryption seed"
    salt = b"test salt"
    iv = b"123456789012"
    token = _jwt({"encKey": _b64url(ikm), "exp": 123})
    key = HKDF(
        algorithm=SHA256(),
        length=32,
        salt=salt,
        info=b"bdw|v1|" + api_path.encode("utf-8"),
    ).derive(ikm)
    plaintext = gzip.compress(json.dumps({"contents": [{"jpNo": "0107544000108"}]}).encode())
    ciphertext = AESGCM(key).encrypt(iv, plaintext, b"bdw|v1|" + api_path.encode("utf-8"))
    envelope = {"kid": 1, "salt": _b64url(salt), "iv": _b64url(iv), "ct": _b64url(ciphertext)}

    assert is_encrypted_envelope(envelope)
    assert decrypt_envelope(envelope, api_path, token) == {"contents": [{"jpNo": "0107544000108"}]}

