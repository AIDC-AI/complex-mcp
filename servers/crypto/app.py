from fastmcp import FastMCP
import hashlib
import hmac
import secrets
import base64
import binascii
import os
import uuid

mcp = FastMCP("CryptoServer")


@mcp.tool
async def sha256(text: str) -> str:
    """Return the SHA-256 hex digest of the given `text`."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@mcp.tool
async def sha1(text: str) -> str:
    """Return the SHA-1 hex digest of the given `text`."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


@mcp.tool
async def md5(text: str) -> str:
    """Return the MD5 hex digest of the given `text` (legacy/compatibility)."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


@mcp.tool
async def hmac_sha256(key: str, message: str) -> str:
    """Compute HMAC-SHA256 of `message` using `key`, returning a hex digest."""
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


@mcp.tool
async def pbkdf2_hex(password: str, salt: str, iterations: int = 100000, dklen: int = 32) -> str:
    """Derive a key from `password` and `salt` using PBKDF2-HMAC-SHA256.

    Returns the derived key as a hex string.
    """
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations, dklen)
    return binascii.hexlify(dk).decode()


@mcp.tool
async def random_bytes(n: int = 32) -> str:
    """Return `n` cryptographically-secure random bytes encoded as a hex string."""
    return secrets.token_hex(n)


@mcp.tool
async def random_hex(nbytes: int = 16) -> str:
    """Return `nbytes` random bytes encoded as a hex string (alias of `random_bytes`)."""
    return secrets.token_hex(nbytes)


@mcp.tool
async def base64_encode(text: str) -> str:
    """Encode `text` to Base64 and return the encoded string."""
    return base64.b64encode(text.encode()).decode()


@mcp.tool
async def base64_decode(b64: str) -> str:
    """Decode a Base64-encoded string and return the decoded text."""
    return base64.b64decode(b64.encode()).decode()


@mcp.tool
async def xor_cipher(text: str, key: str) -> str:
    """Apply a repeating-key XOR of `text` with `key` and return hex-encoded ciphertext.

    Note: this is not secure encryption; provided for toy/offline uses only.
    """
    tb = text.encode()
    kb = key.encode()
    out = bytes([tb[i] ^ kb[i % len(kb)] for i in range(len(tb))])
    return binascii.hexlify(out).decode()


@mcp.tool
async def xor_dec(hextext: str, key: str) -> str:
    """Decode a hex-encoded XOR ciphertext produced by `xor_cipher` using the same `key`."""
    tb = binascii.unhexlify(hextext)
    kb = key.encode()
    out = bytes([tb[i] ^ kb[i % len(kb)] for i in range(len(tb))])
    return out.decode()


@mcp.tool
async def simple_caesar(text: str, shift: int = 3) -> str:
    """Apply a simple Caesar cipher shifting alphabetic characters by `shift` positions."""
    res = []
    for ch in text:
        if 'a' <= ch <= 'z':
            res.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif 'A' <= ch <= 'Z':
            res.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            res.append(ch)
    return ''.join(res)


@mcp.tool
async def rot13(text: str) -> str:
    """Return ROT13 transformation of `text` (a reversible letter substitution)."""
    return text.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                       'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))


@mcp.tool
async def timing_safe_compare(a: str, b: str) -> bool:
    """Compare two strings in a timing-safe way to mitigate timing attacks."""
    return hmac.compare_digest(a, b)


@mcp.tool
async def derive_key(password: str, salt: str, iterations: int = 100000) -> str:
    """Convenience wrapper returning a PBKDF2-derived key hex string for `password` and `salt`."""
    return pbkdf2_hex.__wrapped__(password, salt, iterations)


@mcp.tool
async def entropy_estimate_hex(hexstr: str) -> float:
    """Estimate the Shannon entropy (bits per symbol) of hex-encoded `hexstr`."""
    data = binascii.unhexlify(hexstr)
    counts = {}
    for b in data:
        counts[b] = counts.get(b, 0) + 1
    import math

    ent = 0.0
    l = len(data) or 1
    for c in counts.values():
        p = c / l
        ent -= p * math.log2(p)
    return ent


@mcp.tool
async def uuid4() -> str:
    """Return a random UUID4 string."""
    return str(uuid.uuid4())


@mcp.tool
async def hex_to_bytes(hexstr: str) -> bytes:
    """Convert a hex string into raw bytes."""
    return binascii.unhexlify(hexstr)


@mcp.tool
async def bytes_to_hex(b: bytes) -> str:
    """Convert raw bytes to a lowercase hex string."""
    return binascii.hexlify(b).decode()


@mcp.tool
async def urlsafe_b64_encode(text: str) -> str:
    """Encode `text` as URL-safe Base64 string."""
    return base64.urlsafe_b64encode(text.encode()).decode()


@mcp.tool
async def urlsafe_b64_decode(text: str) -> str:
    """Decode a URL-safe Base64 string and return the decoded text."""
    return base64.urlsafe_b64decode(text.encode()).decode()


@mcp.tool
async def hmac_sign_hex(key: str, message: str) -> str:
    """Return HMAC-SHA256 signature (hex) for `message` with `key`."""
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


@mcp.tool
async def hmac_verify_hex(key: str, message: str, signature: str) -> bool:
    """Verify that `signature` matches HMAC-SHA256(message,key) in a timing-safe way."""
    expected = hmac_sign_hex.__wrapped__(key, message)
    return hmac.compare_digest(expected, signature)


@mcp.tool
async def checksum_sha256_hex(text: str) -> str:
    """Alias for SHA-256 digest of `text` (hex string)."""
    return hashlib.sha256(text.encode()).hexdigest()


@mcp.tool
async def random_choice(seq: list) -> object:
    """Return a cryptographically-secure random element from `seq`."""
    return secrets.choice(seq)


@mcp.tool
async def secure_token_urlsafe(length: int = 32) -> str:
    """Return a URL-safe secure token with the specified `length` (approx bytes)."""
    return secrets.token_urlsafe(length)


@mcp.tool
async def file_digest(path: str, algo: str = "sha256") -> str:
    """Compute the digest of a file at `path` using hash `algo` and return hex digest."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@mcp.tool
async def xor_bytes_hex(a_hex: str, b_hex: str) -> str:
    """XOR two equal-length hex-encoded byte strings and return hex-encoded result."""
    a = binascii.unhexlify(a_hex)
    b = binascii.unhexlify(b_hex)
    res = bytes(x ^ y for x, y in zip(a, b))
    return binascii.hexlify(res).decode()

