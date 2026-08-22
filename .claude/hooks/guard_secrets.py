#!/usr/bin/env python3
"""
PreToolUse guard: refuse any shell command that reads a credential file.

Why this exists alongside the `permissions.deny` rules in settings.json:
deny rules cover the Read tool, but they do not inspect shell commands, so
`cat .env` would sail straight past them. This hook closes that path.

Contract: reads the hook payload as JSON on stdin, prints a decision as JSON on
stdout, exits 0. Printing nothing means "no opinion, carry on".

Deliberately fails closed on unparseable input for Bash, and deliberately allows
the *.example / *.template / *.sample variants, which are committed placeholders
with no real values in them.
"""

import json
import re
import sys

# Placeholder files that are meant to be readable. Stripped from the command
# string before the secret patterns are applied, so `cp .env.example .env` is
# still caught on the `.env` half while `cat .env.example` is not.
ALLOWED = re.compile(
    r"""[\w./-]*\.(?:env|npmrc|pypirc)?[\w./-]*\.(?:example|template|sample|dist)\b"""
    r"""|\.env\.(?:example|template|sample|dist)\b""",
    re.IGNORECASE,
)

SECRET_PATTERNS = [
    (r"(?<![\w.-])\.env(?![\w-])",       "a .env file"),
    (r"\.env\.(?:local|production|prod|development|dev|staging)\b", "an environment file"),
    (r"\bid_(?:rsa|dsa|ecdsa|ed25519)\b", "an SSH private key"),
    (r"(?<![\w-])\.ssh/",                "the .ssh directory"),
    (r"(?<![\w-])\.aws/",                "AWS credentials"),
    (r"(?<![\w-])\.gnupg/",              "GnuPG keyring"),
    (r"(?<![\w-])\.kube/config\b",       "a kubeconfig"),
    (r"\.(?:pem|p12|pfx|jks|keystore)\b", "a certificate or key file"),
    (r"(?<![\w-])\.netrc\b",             "a .netrc file"),
    (r"(?<![\w-])\.git-credentials\b",   "stored git credentials"),
    (r"(?<![\w-])\.(?:npmrc|pypirc)\b",  "a package-registry token file"),
    (r"\bcredentials\.json\b",           "a credentials file"),
    (r"\bservice-account[\w-]*\.json\b", "a service-account key"),
    (r"(?<![\w-])secrets?/",             "a secrets directory"),
    (r"\bid_rsa\b|\bprivate[_-]?key\b",  "a private key"),
]

# Commands that only *write* or *list* are not exfiltration. Reading is the risk.
# We do not try to distinguish: any reference to a secret path in a shell command
# is refused, because `echo x > .env` is not something an agent should do either.


def decide(payload: dict):
    tool = payload.get("tool_name", "")
    if tool != "Bash":
        return None

    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return None

    haystack = ALLOWED.sub(" ", command)

    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE):
            return (
                f"Blocked: this command references {label}. "
                "Credentials must never be read, printed, or copied by an agent. "
                "If you need a value from the environment, use it as a shell variable "
                "(for example: [ -n \"$MY_TOKEN\" ] && echo set) without opening the file. "
                "The committed *.example files are readable and show the expected shape."
            )
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # Unparseable payload: say nothing rather than blocking every command on a
        # malformed frame. The Read-tool deny rules still apply independently.
        return 0

    reason = decide(payload)
    if reason:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
