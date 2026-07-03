import base64
import hashlib
import os
import secrets
import xml.etree.ElementTree as ET
from pathlib import Path

from Crypto.Cipher import AES

CONFIG_COMMENT = "<!-- This config file was saved with the config.load -->\n"
DEFAULT_CONFIG_PATH = "login-config.xml"
ENV_KEY_NAME = "RAVELRY_KEY"


def derive_key(key: str, salt: str) -> bytes:
    digest = hashlib.sha512((key + salt).encode()).digest()
    encoded = base64.b64encode(digest).decode("ascii")
    return encoded[:32].encode("ascii")


def _zero_pad(data: bytes, block_size: int = 16) -> bytes:
    remainder = len(data) % block_size
    if remainder == 0:
        return data
    return data + b"\x00" * (block_size - remainder)


def _strip_zero_padding(data: bytes) -> bytes:
    for index in range(len(data), 0, -1):
        if data[index - 1] != 0:
            return data[:index]
    return b""


def encrypt_value(value: str, key: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)

    total_key = derive_key(key, salt)
    cipher = AES.new(total_key, AES.MODE_ECB)
    encrypted = cipher.encrypt(_zero_pad(value.encode("utf-8")))
    return base64.b64encode(encrypted).decode("ascii"), salt


def decrypt_value(encrypted_value: str, key: str, salt: str) -> str:
    total_key = derive_key(key, salt)
    cipher = AES.new(total_key, AES.MODE_ECB)
    encrypted = base64.b64decode(encrypted_value)
    decrypted = cipher.decrypt(encrypted)
    return _strip_zero_padding(decrypted).decode("utf-8")


def resolve_key(key: str | None = None) -> str:
    if key:
        return key

    env_key = os.environ.get(ENV_KEY_NAME)
    if env_key:
        return env_key

    raise ValueError(
        f"Encryption key required. Pass key=... or set the {ENV_KEY_NAME} environment variable."
    )


def save_config(
    config_path: str | Path,
    username: str,
    password: str,
    key: str,
) -> Path:
    config_file = Path(config_path)
    encrypted_password, salt = encrypt_value(password, key)

    root = ET.Element("config")
    root.set("username", username)
    root.set("password", encrypted_password)
    root.set("salt", salt)

    content = CONFIG_COMMENT + ET.tostring(root, encoding="unicode")
    config_file.write_text(content, encoding="utf-8")
    return config_file


def load_config(config_path: str | Path, key: str | None = None) -> tuple[str, str]:
    config_file = Path(config_path)
    if not config_file.is_file():
        raise FileNotFoundError(f"No password file saved: {config_file}")

    root = ET.fromstring(config_file.read_text(encoding="utf-8"))
    username = root.get("username") or ""
    encrypted_password = root.get("password") or ""
    salt = root.get("salt") or ""

    if not encrypted_password or not salt:
        raise ValueError("Password config file is missing password or salt values.")

    resolved_key = resolve_key(key)
    password = decrypt_value(encrypted_password, resolved_key, salt)

    if not username:
        raise ValueError("Password config file is missing username.")

    return username, password


def load_plaintext_credentials(path: str | Path) -> tuple[str, str]:
    credentials_path = Path(path)
    if not credentials_path.is_file():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    with credentials_path.open(encoding="utf-8") as file:
        username = file.readline().strip()
        password = file.readline().strip()

    if not username or not password:
        raise ValueError("Credentials file must contain username and password on separate lines.")

    return username, password


def resolve_credentials_path(path: str | Path | None = None) -> Path:
    if path:
        return Path(path)

    encrypted_path = Path(DEFAULT_CONFIG_PATH)
    plaintext_path = Path("login-info.txt")

    if encrypted_path.is_file():
        return encrypted_path
    return plaintext_path


def load_credentials(
    path: str | Path | None = None,
    key: str | None = None,
) -> tuple[str, str]:
    credentials_path = resolve_credentials_path(path)

    if credentials_path.suffix.lower() == ".xml" or credentials_path.name == DEFAULT_CONFIG_PATH:
        return load_config(credentials_path, key=key)

    return load_plaintext_credentials(credentials_path)
