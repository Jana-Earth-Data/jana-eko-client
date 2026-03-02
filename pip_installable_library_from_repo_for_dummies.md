# Make a GitHub Repo `pip install`-able (For Dummies)

This guide shows the **modern, simplest, and most correct** way to turn a GitHub repo into a Python library you can install with:

- `pip install -e .` (local dev install)
- `pip install git+https://github.com/you/repo.git` (install from GitHub)
- `pip install your-package` (install from PyPI, optional)

It assumes you’re using **Python 3.9+** and a normal repo on GitHub.

---

## 0) Mental model (what you’re building)

When you “make a repo pip-installable”, you are adding:

1. **A package** (a folder with Python code + `__init__.py`)
2. **Packaging metadata** (name, version, dependencies, etc.)
3. **A build system** (so pip knows how to build/install it)

The modern standard is: **`pyproject.toml`** (PEP 517/518 + PEP 621).

---

## 1) The minimal correct folder structure

Recommended (the **src layout**):

```
your-repo/
├── pyproject.toml
├── README.md
├── LICENSE              (optional but recommended)
├── src/
│   └── your_package/
│       ├── __init__.py
│       └── core.py
└── tests/               (optional but recommended)
    └── test_smoke.py
```

### Important rules
- `src/your_package/` is the **importable** package.
- `__init__.py` is required (it can be empty).
- The PyPI **distribution name** can be different from the **import name**:
  - Distribution (pip install): `your-package`
  - Import (Python): `import your_package`

---

## 2) Create the package code

Example files:

### `src/your_package/__init__.py`
```py
__all__ = ["hello"]
from .core import hello
```

### `src/your_package/core.py`
```py
def hello() -> str:
    return "Hello from your_package!"
```

---

## 3) Add `pyproject.toml` (the key step)

Create `pyproject.toml` in the repo root:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package"              # pip install name
version = "0.1.0"                  # see versioning notes below
description = "A short description of your library"
readme = "README.md"
requires-python = ">=3.9"
authors = [{ name = "Your Name", email = "you@example.com" }]
license = { text = "MIT" }         # or: { file = "LICENSE" }

dependencies = [
  # Put runtime deps here, e.g.:
  # "requests>=2.31.0"
]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

### What this does
- Tells `pip` how to build/install your library.
- Declares name, version, Python requirement, dependencies.
- Configures setuptools to find packages under `src/`.

---

## 4) Install locally (developer workflow)

From the repo root:

```bash
python -m pip install -U pip
pip install -e .
```

The `-e` means **editable install**: changes to your code apply immediately.

Test it:

```bash
python -c "import your_package; print(your_package.hello())"
```

If that works, your repo is successfully pip-installable locally.

---

## 5) Install directly from GitHub (no PyPI required)

Anyone can install your library straight from GitHub:

```bash
pip install git+https://github.com/USERNAME/REPO.git
```

Install from a branch/tag/commit:

```bash
pip install git+https://github.com/USERNAME/REPO.git@main
pip install git+https://github.com/USERNAME/REPO.git@v0.1.0
pip install git+https://github.com/USERNAME/REPO.git@<commit_sha>
```

> Note: GitHub installs still build a wheel under the hood using your `pyproject.toml`.

---

## 6) Add optional dependencies (dev/test extras)

In `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = ["pytest", "ruff", "black"]
```

Install with:

```bash
pip install -e .[dev]
```

---

## 7) Add tests (recommended)

Example `tests/test_smoke.py`:

```py
from your_package import hello

def test_hello():
    assert "Hello" in hello()
```

Run tests:

```bash
pytest -q
```

---

## 8) Build a distributable package (wheel + sdist)

Install build tooling:

```bash
pip install -U build
```

Build:

```bash
python -m build
```

You’ll get:

```
dist/
├── your_package-0.1.0-py3-none-any.whl
└── your_package-0.1.0.tar.gz
```

You can even install the wheel locally:

```bash
pip install dist/*.whl
```

---

## 9) Publish to PyPI (optional)

Publishing is optional. If you publish, users can do:

```bash
pip install your-package
```

### Steps
1. Create accounts on PyPI (and optional TestPyPI).
2. Create a PyPI API token.
3. Upload with `twine`.

Commands:

```bash
pip install -U twine build
python -m build
twine upload dist/*
```

---

## 10) Versioning: the simplest workable approach

Start with manual versions in `pyproject.toml`:

- Bugfix: `0.1.0` → `0.1.1`
- New features: `0.1.0` → `0.2.0`
- Breaking changes: `0.1.0` → `1.0.0`

If you want **automatic versioning from git tags**, use `setuptools_scm` later.

---

## 11) Common mistakes (and quick fixes)

### “It installs but `import your_package` fails”
- You likely **didn’t include `__init__.py`** or your package isn’t under `src/`.
- Confirm: `src/your_package/__init__.py` exists.

### “pip says it can’t find a build backend”
- Your `pyproject.toml` is missing `[build-system]`.

### “It installed the repo but not my subpackages”
- You didn’t configure package discovery under `src/`.
- Ensure:

```toml
[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

### “My repo name has dashes but import needs underscores”
That’s normal:
- `name = "my-library"` (pip)
- `src/my_library/` (import)

---

## 12) One-minute checklist

✅ `src/<import_name>/__init__.py` exists  
✅ `pyproject.toml` exists with `[build-system]` + `[project]`  
✅ `pip install -e .` works  
✅ `python -c "import <import_name>"` works  
✅ (Optional) `python -m build` produces `dist/`  

---

## 13) Copy/paste templates (ready to use)

### Minimal `README.md` template
```md
# your-package

## Install
```bash
pip install git+https://github.com/USERNAME/REPO.git
```

## Usage
```py
from your_package import hello
print(hello())
```
```

---

## Want me to tailor this to your repo?
If you paste:
- your repo tree (`tree -L 3`) OR a screenshot
- your desired package name (pip name + import name)

…I can generate the exact `pyproject.toml` and folder moves for your project.
