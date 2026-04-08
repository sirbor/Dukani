# Security Policy

## Reporting a vulnerability

### Upstream django-oscar

If the problem exists in **django-oscar behaviour** and is **not** introduced by this fork’s own changes, please report it privately to upstream:

[django-oscar security advisories](https://github.com/django-oscar/django-oscar/security/advisories)

### This repository (Dukani fork)

If the vulnerability is in **this fork’s** code or configuration (customisations, sandbox, docs, CI, or anything not attributable to stock Oscar), report it through **this repository’s** security reporting channel. On GitHub, use **Security** → **Report a vulnerability** so maintainers can coordinate a fix before public disclosure.

### Django settings and hosting

Issues that are solved only by changing Django settings, the web server, TLS, or headers (for example `DEBUG`, `ALLOWED_HOSTS`, or HSTS) are usually **deployment concerns**, not bugs in the framework package itself. Verify your production configuration against [Django’s deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/).

Thank you for caring!
