# 🔥 FirePasswords

CLI tool to **analyze password strength** and **generate secure passwords**. Shows
score, entropy, detected issues and suggestions — and checks whether a password has
appeared in real breaches via [Have I Been Pwned](https://haveibeenpwned.com/Passwords),
**without ever sending the password over the network**.

Pure **Python**, zero external dependencies (standard library only).

## Requirements

- Python 3.10+ (uses `int | None` / `list[str]` type syntax).
- Internet **only** for the optional HIBP check — analysis works fully offline.

## Usage

```bash
git clone https://github.com/xFireHide/FirePasswords.git && cd FirePasswords
python3 main.py
```

Interactive menu: **[1]** analyze a password · **[2]** generate a new one · **[3]** exit.
Passwords are shown masked as `*` while typing (raw-mode on Unix/macOS, `msvcrt` on
Windows, `getpass` fallback for pipes).

## How it works

- **Analysis** (`analise.py`) runs independent checks that adjust a 0–100 score:
  length, character variety, repeats, sequences, keyboard patterns, common/obvious
  passwords (with de-leetspeak, so `s3nh@` → `senha`), possible personal data, and a
  real-breach hit (HIBP). Final strength combines score **and** entropy (worst of the two).
- **Entropy** = `length × log2(alphabet_size)` (lower/upper 26, digits 10, symbols 32).
- **HIBP** (`api_hibp.py`) uses **k-anonymity**: SHA-1 the password, send only the
  first 5 hash chars to the Range API, match the suffix **locally**. Uses
  `Add-Padding: true`; returns `None` on network failure (analysis continues).
- **Generation** (`gerador.py`) uses the `secrets` CSPRNG, guarantees at least one
  char per selected category, and shuffles the result.

## Privacy

- Passwords are **never sent over the network** (only a 5-char SHA-1 prefix).
- Generation uses `secrets`, not `random`. Nothing is written to disk or logs.
- Beware of shell history and shoulder-surfing; the `*` mask isn't a substitute for
  a trusted environment.
