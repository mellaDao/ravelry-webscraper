import argparse
import getpass
import os

from encrypt_password import (
    DEFAULT_CONFIG_PATH,
    ENV_KEY_NAME,
    load_plaintext_credentials,
    save_config,
)

def main():
    parser = argparse.ArgumentParser(
        description="Encrypt Ravelry login credentials into login-config.xml."
    )
    parser.add_argument(
        "--input",
        default="login-info.txt",
        help="Plaintext credentials file with username and password on separate lines.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_CONFIG_PATH,
        help="Encrypted XML config file to create.",
    )
    parser.add_argument(
        "--key",
        help=f"Encryption key. If omitted, uses {ENV_KEY_NAME} or prompts securely.",
    )
    args = parser.parse_args()

    if args.key:
        key = args.key
    elif os.environ.get(ENV_KEY_NAME):
        key = os.environ[ENV_KEY_NAME]
    else:
        key = getpass.getpass("Encryption key: ")

    username, password = load_plaintext_credentials(args.input)
    output_path = save_config(args.output, username, password, key)

    print(f"Saved encrypted credentials to {output_path}")
    print(f"Keep your encryption key safe. Set {ENV_KEY_NAME} or enter it in the GUI when loading.")


if __name__ == "__main__":
    main()
