# Agent Guidelines for Edubot Repository

This document outlines the conventions, commands, and style guidelines for AI agents operating within the Edubot codebase. Adhering to these guidelines ensures consistency, maintainability, and efficient collaboration.

## 1. Build, Lint, and Test Commands

### 1.1 Application Execution

The primary application is a FastAPI service.
*   **Run Command (Development):**
    ```bash
    uvicorn src.api.main:app --reload
    ```
    This command starts the FastAPI application with auto-reloading for development purposes.

### 1.2 Linting

No explicit linting configuration was found (e.g., `.flake8`, `pyproject.toml` for `ruff`).
*   **Recommended Linter:** For Python, `flake8` or `ruff` is recommended to ensure code quality and adherence to PEP 8.
*   **Example Lint Command:**
    ```bash
    # Assuming flake8 is installed
    flake8 src/
    # Or with ruff
    # ruff check src/
    ```

### 1.3 Testing

No automated test suite was explicitly identified (e.g., `pytest` configuration, `unittest` modules, or `test_` prefixed files within the `test/` directory).
*   **Recommendation:** If new tests are to be introduced, `pytest` is the recommended framework.
*   **Example Test Command (if pytest were configured):**
    ```bash
    # Run all tests
    pytest
    # Run a single test file
    pytest path/to/your_test_file.py
    # Run a specific test within a file
    pytest path/to/your_test_file.py::test_function_name
    ```
    *Note: As of the current analysis, no executable tests were found. Agents should be cautious when making changes and manually verify functionality if no test coverage exists.*

## 2. Code Style Guidelines (Python)

The codebase predominantly uses Python. Adhere to the following conventions:

### 2.1 Imports

*   **Order:** Imports should generally be grouped as follows:
    1.  Standard library imports
    2.  Third-party library imports
    3.  Local application/project-specific imports
*   **Absolute vs. Relative:** Both absolute (`from src.apps.Dulcinea.main import ...`) and relative (`from .v1.routers import ...`) imports are present. Prefer absolute imports for clarity unless within a package where relative imports simplify things.
*   **Placement:** All imports should be at the top of the file, after any module-level docstrings and `__future__` imports.

### 2.2 Formatting

No explicit formatting tool (like Black) configuration was found.
*   **Recommendation:** Use `black` for consistent code formatting.
*   **Key Formatting Principles (observed and recommended):**
    *   **Indentation:** 4 spaces for indentation.
    *   **Line Length:** Strive for lines not exceeding 79 characters, though 99 characters (Black's default) is acceptable for readability.
    *   **Whitespace:** Use consistent whitespace around operators, function arguments, and in empty lines to separate logical blocks.

### 2.3 Types

*   **Type Hints:** Type hints (`def func(arg: str) -> bool:`) are extensively used and are mandatory for all function arguments, return values, and class attributes where applicable.
*   **Pydantic:** `pydantic.BaseModel` is used for data validation and serialization, particularly in FastAPI schemas.
*   **Typing Module:** `from typing import Literal, TypedDict` and other components from the `typing` module are utilized for more complex type definitions.

### 2.4 Naming Conventions

*   **Modules:** `snake_case` (e.g., `main.py`, `db_utils.py`).
*   **Packages:** `snake_case` (e.g., `api`, `dulcinea`).
*   **Classes:** `PascalCase` (e.g., `FastAPI`, `BaseModel`, `ChatGoogleGenerativeAI`, `State`).
*   **Functions/Methods:** `snake_case` (e.g., `get_dulci_report`, `create_dulcinea`, `retrive_sqlite_messages`).
*   **Variables:** `snake_case` (e.g., `guild_id`, `channel_name`, `initial_state`).
*   **Constants:** `UPPER_SNAKE_CASE` (e.g., `SQLITE_QUERY_1`, `PROMPT_1`).

### 2.5 Error Handling

*   **Explicit Handling:** Implement explicit error handling using `try...except` blocks where errors are anticipated.
*   **Meaningful Exceptions:** Raise appropriate and descriptive exceptions (`ValueError`, `TypeError`, custom exceptions) when an unrecoverable error or invalid state is encountered.
*   **API Error Responses:** For FastAPI endpoints, return standardized error responses (e.g., using `HTTPException` from `fastapi`).
*   No explicit `raise` statements were found in the examined code, suggesting error handling might be managed at a higher level or by the framework. Agents should ensure robust error handling is considered in any new or modified code.

### 2.6 Logging

*   **Centralized Configuration:** The `src/logging_config.py` module provides a centralized logging setup. Agents should utilize the functions provided in this module (`get_logger`) for all logging needs.
*   **Log Levels:** Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) for different severities of messages.
*   **Contextual Logging:** Include relevant contextual information in log messages to aid in debugging and monitoring.

## 3. Cursor/Copilot Rules

No `.cursor/rules/` directory or `.github/copilot-instructions.md` file was found in this repository. Agents should adhere to general best practices for AI-assisted coding and prioritize the guidelines outlined above.
