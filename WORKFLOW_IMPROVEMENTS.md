# Manimator: Current Workflow & Improvement Plan

This document outlines the current workflow, resources, tools, and APIs utilized in the `manimator` repository, followed by a comprehensive plan to improve the project's overall efficiency.

## 1. Current Workflow & Architecture

### Development & Deployment Workflow
- **Dependency Management:** Managed via `Poetry` (`pyproject.toml`, `poetry.lock`) with fallback `requirements.txt` and system packages (`packages.txt`).
- **Containerization:** `Docker` is used to build and run the application in isolated environments (both FastAPI and Gradio).
- **Environment Management:** Managed through `.env` files (template `.env.example`).
- **Running Locally:** Uses `poetry run app` for FastAPI and `poetry run gradio-app` for the Gradio interface.

### Resources & Tools Used
- **Python Frameworks:** `FastAPI` (for REST APIs), `Gradio` (for Web UI interactable demo).
- **Animation Engine:** `Manim` (used to generate MP4 animations from Python code).
- **PDF Processing:** `PyPDF2` (for parsing and compressing PDFs).
- **Server:** `Uvicorn` (ASGI web server implementation for Python).
- **System Dependencies:** `ffmpeg`, `texlive`, `libcairo2`, `libpango1.0`, `dvisvgm` (required by Manim).

### APIs & External Services
- **LiteLLM:** Used as an abstraction layer to interact with various LLM providers (e.g., DeepSeek, Llama 3.3 via Groq, Gemini 1.5/2.0).
- **arXiv API:** Fetching and downloading research papers as PDFs directly from `arxiv.org`.

### Internal Modules & Functions
- **`manimator/main.py`:** Main entry point for FastAPI. Exposes endpoints (`/generate-pdf-scene`, `/generate-prompt-scene`, `/pdf/{arxiv_id}`, `/generate-animation`).
- **`manimator/gradio_app.py`:** Main entry point for the Gradio frontend application.
- **`manimator/api/scene_description.py`:**
  - `process_prompt_scene`: Generates a scene description from a user prompt using LiteLLM.
  - `process_pdf_prompt`: Processes a PDF file (extracts/compresses) and generates a scene description using LiteLLM.
- **`manimator/api/animation_generation.py`:**
  - `generate_animation_response`: Uses LLM to generate Manim Python code based on a scene description prompt.
- **`manimator/utils/helpers.py`:** Utilities for downloading arXiv PDFs, compressing PDFs, and reading few-shot base64 examples.
- **`manimator/utils/schema.py`:**
  - `ManimProcessor`: Class that handles the extraction of python code from LLM responses, saving it to temp files, and rendering the Manim scenes into MP4 videos using subprocess.
- **`manimator/utils/system_prompts.py`:** Contains LLM system prompts (`MANIM_SYSTEM_PROMPT`, `SCENE_SYSTEM_PROMPT`).
- **`manimator/few_shot/`:** Contains few-shot examples for PDF handling and prompt processing.

---

## 2. Comprehensive Improvement Plan (360-Degree Efficiency)

To improve the efficiency of the project—spanning code quality, security, performance, and product quality—the following actions are proposed:

### Phase 1: CI/CD & Automation (Development Efficiency)
- **Implement GitHub Actions:**
  - **Linting & Formatting Check:** Run `black`, `flake8` or `ruff` to enforce consistent code styling.
  - **Type Checking:** Integrate `mypy` to catch type errors before runtime.
  - **Automated Testing:** Set up `pytest` to run automated unit tests for API endpoints and internal utilities on every PR.
- **Pre-commit Hooks:** Add `.pre-commit-config.yaml` to run formatting (e.g., `black`, `isort`) and linting locally before commits are pushed.

### Phase 2: Code Quality & Architecture
- **Testing Suite:** Currently, there are no tests. Write unit tests for PDF extraction, code generation logic, and API endpoints using `pytest` and `httpx`.
- **Error Handling & Retries:** Enhance LLM retry mechanisms (currently relying partly on litellm's `num_retries`) and add fallback models natively in the code for better fault tolerance.
- **Type Hinting:** Enforce strict type hinting across all functions and classes to reduce bugs and make the codebase easier to understand.
- **Refactoring:**
  - Abstract the LLM calls into a dedicated service/class to decouple business logic from the specific LLM library, making it easier to mock in tests.

### Phase 3: Security Improvements
- **Dependency Vulnerability Scanning:** Use tools like `Dependabot` or `Snyk` to continuously monitor `poetry.lock` and `requirements.txt` for known vulnerabilities.
- **Secret Management:** Ensure API keys and environment variables are never logged or leaked in error responses. Use proper exception handling that obscures sensitive configuration details.
- **Sandbox Execution for Manim Code:** Currently, the LLM-generated code is executed directly via `subprocess.run(["manim", ...])`. This is a massive **Remote Code Execution (RCE)** security risk.
  - *Fix:* Isolate the Manim rendering process using a restricted Docker container (e.g., Docker-in-Docker or a secure sandbox like `gVisor`) with dropped privileges and disabled network access to execute untrusted code safely.

### Phase 4: Product & Performance Efficiency
- **Caching Mechanisms:** Implement caching (e.g., Redis or simple in-memory caching) for previously processed arXiv IDs and exact prompts to save expensive LLM API calls and rendering time.
- **Asynchronous Processing:** Long-running tasks like Manim rendering and PDF processing should be handled asynchronously using a task queue like `Celery` or `RQ`. This will prevent FastAPI/Gradio timeouts and provide users with a task status polling mechanism.
- **PDF Extraction Optimization:** Improve PDF extraction logic using more advanced parsers (e.g., `PyMuPDF` or `pdfplumber`) to handle mathematical equations and figures better before feeding them to the LLM.
