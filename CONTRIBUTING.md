# Contributing to pynextsms

Thank you for your interest in contributing! Here's everything you need.

---

## Development Setup

```bash
git clone https://github.com/ronaldgosso/pynextsms.git
cd pynextsms

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Running Tests

```bash
pytest                                        # all tests
pytest --cov=pynextsms --cov-report=term-missing  # with coverage
pytest tests/ -v -k "TestSend"               # specific class
```

## Linting & Formatting

```bash
ruff check pynextsms/     # lint
black pynextsms/ tests/   # format
mypy pynextsms/           # type-check
```

All four commands must pass before submitting a PR.

---

## Pull Request Checklist

- [ ] All tests pass (`pytest`)
- [ ] No lint errors (`ruff check pynextsms/`)
- [ ] Code is formatted (`black --check pynextsms/ tests/`)
- [ ] No type errors (`mypy pynextsms/`)
- [ ] New features have tests
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

---

## Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/<short-desc>` | `feat/otp-helper` |
| Bug fix | `fix/<short-desc>` | `fix/retry-on-timeout` |
| Docs | `docs/<short-desc>` | `docs/schedule-example` |

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) spec:

```
feat: add OTP helper method
fix: handle empty Retry-After header gracefully
docs: add scheduling example to README
test: add coverage for 429 rate-limit path
```

---

## Reporting Issues

Open an issue and include:
1. Python version (`python --version`)
2. pynextsms version (`pip show pynextsms`)
3. Minimal reproduction code
4. Full traceback
