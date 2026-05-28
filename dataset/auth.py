"""OAuth flow for Google Drive access — manual code-paste, not local-server.

Phase A (no --code): prints auth URL, saves PKCE code_verifier to disk.
Phase B (with --code <auth_code>): reads verifier, exchanges code for token.
Non-interactive callers use get_credentials() which only reads/refreshes
the cached token; it raises if no token is present.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DEFAULT_TOKEN_PATH = Path.home() / ".config" / "citizen_voice_irr" / "token.json"
DEFAULT_VERIFIER_PATH = Path.home() / ".config" / "citizen_voice_irr" / "code_verifier.tmp"
REDIRECT_URI = "http://localhost"


def get_credentials(
    credentials_path: Path,
    token_path: Path = DEFAULT_TOKEN_PATH,
) -> Credentials:
    """Load cached token, refresh if needed. Does NOT trigger interactive auth.

    Raises FileNotFoundError if token.json doesn't exist.
    """
    if not token_path.exists():
        raise FileNotFoundError(
            f"No token at {token_path}. "
            f"Run `python -m dataset.auth --credentials {credentials_path}` first."
        )
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        else:
            raise RuntimeError(
                f"Cached token at {token_path} is invalid and has no refresh token. "
                f"Re-run `python -m dataset.auth --credentials {credentials_path}`."
            )
    return creds


def _phase_a_print_url(credentials_path: Path, verifier_path: Path) -> None:
    flow = Flow.from_client_secrets_file(
        str(credentials_path), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    verifier_path.parent.mkdir(parents=True, exist_ok=True)
    verifier_path.write_text(flow.code_verifier)
    print("Open this URL in your browser, complete consent, then copy the")
    print("`code=` value from the localhost redirect URL:")
    print()
    print(url)
    print()
    print(f"Then re-run with --code <CODE>")


def _phase_b_exchange(
    credentials_path: Path,
    auth_code: str,
    verifier_path: Path,
    token_path: Path,
) -> None:
    if not verifier_path.exists():
        raise RuntimeError(
            f"PKCE verifier not found at {verifier_path}. "
            f"Re-run without --code to generate a new auth URL."
        )
    verifier = verifier_path.read_text().strip()
    flow = Flow.from_client_secrets_file(
        str(credentials_path), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )
    flow.code_verifier = verifier
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    verifier_path.unlink(missing_ok=True)
    print(f"Token cached at {token_path}")
    print(f"refresh_token present: {bool(creds.refresh_token)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--code", help="auth code from the OAuth redirect URL")
    parser.add_argument("--token", type=Path, default=DEFAULT_TOKEN_PATH)
    parser.add_argument("--verifier", type=Path, default=DEFAULT_VERIFIER_PATH)
    args = parser.parse_args()
    if args.code:
        _phase_b_exchange(args.credentials, args.code, args.verifier, args.token)
    else:
        _phase_a_print_url(args.credentials, args.verifier)


if __name__ == "__main__":
    main()
