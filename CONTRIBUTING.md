# Contributing to Dumpcat

Thanks for your interest in contributing! Whether it's a bug fix, new feature, or documentation improvement, all contributions are welcome.

## Getting started

1. **Fork and clone** the repo:

   ```bash
   git clone https://github.com/<your-username>/dumpcat.git
   cd dumpcat
   ```

2. **Install in development mode** with dev dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

3. **Create a branch** for your change:

   ```bash
   git checkout -b my-change
   ```

## Making changes

- Keep changes focused — one fix or feature per pull request.
- Follow the existing code style. The project uses [Ruff](https://docs.astral.sh/ruff/) for linting:

  ```bash
  ruff check src/ tests/
  ```

- Add or update tests for any new behavior. Tests live in `tests/` and use pytest:

  ```bash
  pytest
  ```

- Run tests with coverage to make sure nothing slipped through:

  ```bash
  pytest --cov=dumpcat --cov-report=term-missing
  ```

## Commit messages

Write clear, concise commit messages. A good format:

```
Add support for xyz

Brief description of what changed and why.
```

## Submitting a pull request

1. Push your branch to your fork.
2. Open a pull request against `main`.
3. Describe what you changed and why. If it fixes an issue, reference it (e.g. "Fixes #12").
4. Make sure CI passes — the same checks run automatically on every PR.

## Reporting bugs

Found a bug? [Open an issue](https://github.com/Allenfp/dumpcat/issues) with:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Your Python version and OS

## Suggesting features

Have an idea? Open an issue and describe the use case. Even rough ideas are helpful — we can figure out the details together.

## Code of conduct

Be kind, be respectful. This is a small project and everyone's here to make it better.
