# Hello World PyPI

A minimal, **modern** reference project for publishing a Python package to [PyPI](https://pypi.org).
Everything here reflects current packaging practice (PEP 517/518/621/639, Trusted Publishing) —
no `setup.py`, no `python setup.py` commands, no passwords in a config file.

```pycon
>>> from hello_world import hello
>>> hello()
'Hello, World!'
>>> hello("PyPI")
'Hello, PyPI!'
```

```console
$ hello-world PyPI
Hello, PyPI!
$ python -m hello_world
Hello, World!
```

---

## What changed since the old packaging tutorials

If you learned packaging from a pre-2020 guide, these are the things that are now different:

| Old way | Current way |
|---|---|
| `setup.py` with `setup(...)` | `pyproject.toml` with a `[project]` table (PEP 621) |
| `python setup.py sdist bdist_wheel` | `python -m build` (or `uv build`) |
| `setup.py` implies setuptools | `[build-system]` declares any backend (hatchling, setuptools, flit, pdm) |
| `username`/`password` in `~/.pypirc` | API tokens, or **Trusted Publishing** from CI with no secret at all |
| optional 2FA | **2FA is mandatory** for all PyPI accounts |
| `"License :: OSI Approved :: MIT License"` classifier | `license = "MIT"` SPDX expression + `license-files` (PEP 639) |
| flat `mypackage/` next to `setup.py` | `src/mypackage/` layout |
| `requirements.txt` for everything | `dependencies` / `[project.optional-dependencies]` in `pyproject.toml` |

> `python setup.py <anything>` is deprecated and increasingly broken. If a guide tells you to run
> it, the guide is out of date.

---

## Project layout

```
hello-world-pypi/
├── pyproject.toml              # all build config + metadata lives here
├── README.md                   # becomes the PyPI project page
├── LICENSE
├── src/
│   └── hello_world/
│       ├── __init__.py         # the public API
│       ├── __main__.py         # enables `python -m hello_world`
│       └── cli.py              # the `hello-world` console script
├── tests/
│   └── test_hello_world.py
└── .github/workflows/
    ├── ci.yml                  # test matrix + build check
    └── release.yml             # publish via Trusted Publishing
```

**Why `src/`?** Without it, `import hello_world` in your tests silently picks up the source
directory from the current working directory, so you never test what you actually ship. With
`src/`, the only way to import the package is to install it — which is what your users do.

---

## Create a project from scratch

### 0. Pick a name

PyPI normalizes names (PEP 503): `Hello_World.PyPI`, `hello-world-pypi` and `hello.world.pypi` are
the same project. Check `https://pypi.org/project/<your-name>/` first — if it 404s, the name is
probably free. The *import* name (`hello_world`) may differ from the *distribution* name
(`hello-world-pypi`); use underscores for the import name.

### 1. Set up an environment

Using the standard library:

```bash
python3 -m venv .venv            # create it in .venv/, NOT in the repo root
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

Or with [uv](https://docs.astral.sh/uv/), which is significantly faster and also builds/publishes:

```bash
uv venv
uv pip install -e ".[dev]"
```

### 2. Write `pyproject.toml`

See [`pyproject.toml`](pyproject.toml) in this repo — it is commented line by line. The two
required tables are:

```toml
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "hello-world-pypi"
version = "0.1.0"
description = "The simplest Hello World package"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
license-files = ["LICENSE"]
```

Only `name` and `version` are strictly mandatory, but `readme`, `requires-python`, `license` and
`classifiers` are what make a project page look credible.

### 3. Install in editable mode and run the tests

```bash
python -m pip install -e ".[test]"
python -m pytest
hello-world
```

Editable installs are standardized (PEP 660) and work with every modern backend.

### 4. Build the distributions

```bash
python -m pip install --upgrade build
python -m build
```

```
dist/
├── hello_world_pypi-0.1.0-py3-none-any.whl   # wheel: what pip installs
└── hello_world_pypi-0.1.0.tar.gz             # sdist: the buildable source
```

Always ship both. With uv: `uv build`.

Sanity-check the metadata and the README rendering *before* uploading — a README that fails to
render cannot be fixed without a new version number:

```bash
python -m pip install --upgrade twine
python -m twine check --strict dist/*
```

### 5. Upload to TestPyPI first

[TestPyPI](https://test.pypi.org) is a separate instance with separate accounts and tokens. Use it
as a rehearsal.

```bash
python -m twine upload --repository testpypi dist/*
```

Then verify the install in a clean environment:

```bash
python -m venv /tmp/check && /tmp/check/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  hello-world-pypi
/tmp/check/bin/hello-world
```

The `--extra-index-url` is needed because your dependencies live on real PyPI, not TestPyPI.

### 6. Upload to PyPI

```bash
python -m twine upload dist/*
```

A version can never be reused or replaced once uploaded — `0.1.0` is `0.1.0` forever, even if you
delete it. Bump the version (PEP 440: `0.1.0`, `0.2.0.dev1`, `1.0.0rc1`) and rebuild.

---

## Authentication: tokens, not passwords

Password-based uploads no longer exist. Choose one of these:

### Option A — API token (manual uploads)

1. Create a token at <https://pypi.org/manage/account/token/>, scoped to a single project where
   possible.
2. The username is always the literal string `__token__`; the password is the whole
   `pypi-...` token.
3. Store it in `~/.pypirc`, and make it user-readable only (`chmod 600 ~/.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw...
```

In CI, pass it by environment variable instead of a file:

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" python -m twine upload dist/*
```

### Option B — Trusted Publishing (recommended for CI)

PyPI can verify a short-lived OpenID Connect identity from GitHub Actions (also GitLab, Google
Cloud Build, ActiveState), so **there is no long-lived token to leak or rotate**.

1. Go to <https://pypi.org/manage/account/publishing/> and add a publisher. For a project that does
   not exist on PyPI yet, add a *pending* publisher — the project is created on first upload.
2. Fill in owner, repository, workflow filename (`release.yml`) and environment name (`pypi`).
3. Give the publishing job `permissions: id-token: write` and use
   [`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish).

See [`.github/workflows/release.yml`](.github/workflows/release.yml): it builds once, publishes to
TestPyPI, then to PyPI on a published GitHub Release. As a bonus, the action generates PEP 740
attestations, so users can verify the artifact came from this repo.

---

## Versioning

This project keeps the version static in `pyproject.toml` and reads it back at runtime from the
installed metadata, which avoids the classic "two places disagree" bug:

```python
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hello-world-pypi")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"
```

If you'd rather derive the version from git tags, use `hatch-vcs` or `setuptools-scm` and declare
`dynamic = ["version"]`.

---

## Release checklist

1. `python -m pytest` passes on every supported Python version (CI does the matrix).
2. Bump `version` in `pyproject.toml`; update the changelog.
3. `python -m build && python -m twine check --strict dist/*`.
4. `git tag v0.1.0 && git push --tags`, then publish a GitHub Release.
5. `release.yml` publishes to TestPyPI and PyPI. Verify the project page and a clean install.

---

## Repo hygiene note

A virtual environment was once created **in the repo root** (`python3.14 -m venv .`), which left
`pyvenv.cfg`, `bin/`, `lib/`, `include/` behind and a generated `.gitignore` containing a single
`*` — silently ignoring the whole project. `.gitignore` has been replaced; delete the stray venv
when convenient:

```bash
rm -rf bin include lib lib64 share pyvenv.cfg
```

Create environments in `.venv/` instead, never in the project root.

## Further reading

- [Python Packaging User Guide](https://packaging.python.org/) — the authoritative source
- [PyPA sample project](https://github.com/pypa/sampleproject)
- [`pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)

## License

MIT — see [LICENSE](LICENSE).
