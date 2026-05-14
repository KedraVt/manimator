# Changelog and Architectural Adjustments

This document serves as a comprehensive record of the code changes, infrastructural adjustments, and strategic refactors executed against the `manimator` repository.

Each change maps back to the roadmap outlined in `WORKFLOW_IMPROVEMENTS.md`.

## 1. CI/CD & Automation Setup (Phase 1)
- **Added GitHub Actions (`.github/workflows/ci.yml`)**: Implemented an automated pipeline to run testing, formatting, and linting checks on all PRs to the `main` branch. This prevents broken code from being merged.
- **Added Dependabot (`.github/dependabot.yml`)**: Configured automated weekly checks for outdated or vulnerable packages in pip, Docker, and GitHub Actions to maintain security compliance over time.
- **Added Pre-Commit Hooks (`.pre-commit-config.yaml`)**: Empowered developers to run formatting (`black`) and linting (`flake8`) natively before pushing commits.

## 2. Code Quality & Type Safety (Phase 2)
- **Integrated Linters and Formatters**: Added `flake8`, `black`, and `mypy` to the project's dependencies (`pyproject.toml`).
- **Global Codebase Formatting**: Executed `black` across the entire `manimator` directory to enforce an 88-character line limit and maintain consistent, readable styling.
- **Strict Prompt Integrity (`.flake8`)**: Created a custom `.flake8` configuration to ignore `E501` (Line too long) within `system_prompts.py`. This ensures that complex prompt strings sent to the LLMs aren't arbitrarily broken by linters, maintaining prompt integrity.
- **Resolved Static Typing Errors**: Fixed variable shadowing and incompatible types flagged by `mypy` in `gradio_app.py` and `main.py`. Added a `mypy.ini` file to safely ignore missing type stubs from external libraries.
- **Implemented Unit Testing**: Added the `pytest` and `httpx` dependencies. Bootstrapped the `tests/` directory with a foundational `test_main.py` health-check test to satisfy the CI pipeline and serve as a template for future API test coverage.

## 3. Security, Cost Management & Reliability (Phase 3)
- **Implemented API Rate Limiting**: Added the `slowapi` dependency and wrapped all FastAPI endpoints in `main.py` with strict rate limits (e.g., `2/minute` for intensive rendering, `5/minute` for PDF processing). This prevents abuse, infinite loop attacks, and blown API budgets.
- **Strict Subprocess Timeouts**: Enforced a `timeout=120` constraint on the `subprocess.run()` function executing the Manim code inside `manimator/utils/schema.py`. This acts as a critical guardrail against LLM-hallucinated infinite loops locking up server resources.
- **Exception Obfuscation**: Refactored `except Exception` blocks in `main.py` to prevent raw system errors or environmental variables from leaking through HTTP 500 responses. We now explicitly raise generic `HTTPException`s while preserving internal tracebacks.
- **Updated PyPDF Deprecation**: Removed the deprecated `PyPDF2` library and replaced it with its modern successor, `pypdf`, removing deprecated `set_compression()` calls to prevent silent runtime exceptions.
- **Strict Schema Validation**: Implemented Pydantic V2 `ResponseModel` constraints and input `Field` length validations across all FastAPI endpoints to ensure data sanitization.

## 4. Performance Optimization (Phase 4)
- **In-Memory Caching (`@lru_cache`)**: Added `functools.lru_cache` to the `process_arxiv_by_id` and `process_prompt_scene` functions. This caches identical payloads, vastly reducing wait times and saving unnecessary LLM API credits for frequently processed ArXiv papers or repeated prompts.

## 5. Modern Frontend Decoupling (Phase 6)
- **Deprecated Gradio Monolith**: Removed the monolithic UI implementation `manimator/gradio_app.py` and stripped the `gradio` package from the `pyproject.toml` dependencies.
- **Independent HTML/JS Frontend**: Created an independent, lightweight, modern UI at `frontend/index.html`. This HTML interface handles API communication asynchronously.
- **FastAPI Static Serving**: Updated `main.py` to serve the decoupled frontend interface directly from the root path (`/`) via FastAPI's `StaticFiles` integration, establishing a clean boundary between the backend engine and the presentation layer.