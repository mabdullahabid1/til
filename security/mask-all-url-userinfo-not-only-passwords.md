# Mask All URL Userinfo, Not Only Passwords

Credential scrubbing must handle both `user:password@host` and single-token `token@host` URL userinfo. Parse the URL, replace the entire userinfo section, and never log the original value when parsing fails.

```python
from urllib.parse import urlsplit, urlunsplit

parts = urlsplit(url)
host = parts.hostname or ""
safe_netloc = f"MASKED@{host}" if parts.username else parts.netloc
safe_url = urlunsplit(
    (parts.scheme, safe_netloc, parts.path, parts.query, parts.fragment)
)
```

If the input appears credential-bearing but cannot be parsed safely, replace the whole value with a placeholder.
