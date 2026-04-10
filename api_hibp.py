import hashlib
import urllib.error
import urllib.request

HIBP_RANGE_BASE = "https://api.pwnedpasswords.com/range/"
USER_AGENT = "analisador-senhas/1.0 (Python; Pwned Passwords k-anonymity)"


def contagem_vazamentos_hibp(senha: str, timeout: float = 12.0) -> int | None:
    digest = hashlib.sha1(senha.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]

    url = f"{HIBP_RANGE_BASE}{prefix}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Add-Padding": "true",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None

    suffix_upper = suffix.upper()
    for raw in body.splitlines():
        line = raw.strip()
        if ":" not in line:
            continue
        suf, _, count_part = line.partition(":")
        try:
            count = int(count_part.strip())
        except ValueError:
            continue
        if suf.upper() == suffix_upper:
            return count

    return 0
