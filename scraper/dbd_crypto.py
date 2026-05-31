from __future__ import annotations

import base64
import gzip
import json
import zlib
from typing import Any

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.hashes import SHA256
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except ImportError as exc:  # pragma: no cover - exercised only in incomplete environments
    raise RuntimeError("DBD envelope decryption requires the 'cryptography' package") from exc


def decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("Invalid JWT: missing payload")
    return json.loads(_b64url_decode(parts[1]).decode("utf-8"))


def decrypt_envelope(envelope: dict[str, Any], api_path: str, access_token: str) -> Any:
    token_payload = decode_jwt_payload(access_token)
    enc_key = token_payload.get("encKey")
    if not enc_key:
        raise ValueError("JWT is missing encKey")

    kid = envelope["kid"]
    info = f"bdw|v{kid}|{api_path}".encode("utf-8")
    aes_key = HKDF(
        algorithm=SHA256(),
        length=32,
        salt=_b64url_decode(envelope["salt"]),
        info=info,
    ).derive(_b64url_decode(enc_key))

    plaintext = AESGCM(aes_key).decrypt(
        nonce=_b64url_decode(envelope["iv"]),
        data=_b64url_decode(envelope["ct"]),
        associated_data=info,
    )
    return json.loads(_decompress(plaintext).decode("utf-8"))


def is_encrypted_envelope(value: Any) -> bool:
    return isinstance(value, dict) and {"kid", "salt", "iv", "ct"}.issubset(value)


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _decompress(value: bytes) -> bytes:
    for decompressor in (gzip.decompress, zlib.decompress):
        try:
            return decompressor(value)
        except zlib.error:
            continue
        except OSError:
            continue
    try:
        return zlib.decompress(value, -zlib.MAX_WBITS)
    except zlib.error:
        return value
