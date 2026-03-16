# AGENT GUIDELINES FOR THE `edubot` REPOSITORY

This document outlines the conventions, commands, and best practices for agentic coding agents operating within this repository. Adhering to these guidelines ensures consistency, maintainability, and efficient collaboration.

## 1. Project Overview

This is primarily a Python project, utilizing FastAPI for its API, SQLAlchemy for database interactions (PostgreSQL), and `discord.py` for Discord bot functionalities. Docker Compose is used to manage the PostgreSQL database service.

## 2. Build, Lint, and Test Commands

### 2.1 Dependency Management

*   **Installation:** It is assumed that dependencies are managed in a virtual environment. While a `requirements.txt` file is currently not present, it is highly recommended to create one if new dependencies are added or if explicit dependency management is required.
    ```bash
    # Example: Create a requirements.txt file
    # pip freeze > requirements.txt
    # pip install -r requirements.txt
    ```

### 2.2 Running Applications

*   **FastAPI Application:** The main API entry point is `src/api/main.py`.
    *   **Development:** `uvicorn src.api.main:app --reload`
    *   **Production:** `uvicorn src.api.main:app --host 0.0.0.0 --port 80` (adjust port as necessary)

*   **Discord Bot (`DiscordEchoSaver`):**
    *   `python3 -m src.apps.DiscordEchoSaver.botv1`

*   **Database Initialization (`src/database.py`):**
    *   `python3 -m src.database` (This script creates database tables)

*   **Docker Compose:** To start the PostgreSQL database:
    *   `docker-compose up -d postgres-db`

### 2.3 Linting and Formatting

*   **Recommendation:** No explicit linting or formatting tools are currently configured. For consistency and code quality, it is recommended to integrate `black` for code formatting and `ruff` for linting.
    *   **Black (Formatting):**
        *   `pip install black`
        *   `black .` (to format all Python files)
        *   `black <file_path>` (to format a single file)
    *   **Ruff (Linting):**
        *   `pip install ruff`
        *   `ruff check .` (to lint all Python files)
        *   `ruff check <file_path>` (to lint a single file)

### 2.4 Testing

*   **Current State:** There is no dedicated unit testing framework configured. The `test/streamlit/app.py` file appears to be an example or a standalone application, not unit tests.
*   **Recommendation:** Implement `pytest` for robust unit and integration testing.
    *   **Pytest:**
        *   `pip install pytest`
        *   `pytest` (to run all tests)
        *   `pytest <file_path>::<test_function_name>` (to run a single test function in a specific file)

## 3. Code Style Guidelines

### 3.1 Imports

*   **Ordering:** Generally, standard library imports, third-party library imports, and local application imports are grouped.
*   **Absolute vs. Relative:** Prefer absolute imports (e.g., `from src import models`, `from src.apps.module.submodule import Class`) over relative imports for clarity and to avoid potential issues.

### 3.2 Naming Conventions

*   **Modules, Functions, Variables:** Use `snake_case` (e.g., `my_module.py`, `my_function()`, `my_variable`).
*   **Classes:** Use `PascalCase` (e.g., `MyClass`, `DatabaseError`).
*   **Constants:** Use `SCREAMING_SNAKE_CASE` (e.g., `MY_CONSTANT = 123`).

### 3.3 Type Hinting

*   Utilize type hints for function arguments, return values, and variable annotations to improve code readability and maintainability.

### 3.4 Error Handling

*   **`try...except`:** Use `try...except` blocks to gracefully handle expected errors, especially for I/O and database operations.
*   **Custom Exceptions:** Define custom exception classes for application-specific error scenarios (e.g., `DatabaseError`).
*   **Exception Chaining:** When re-raising exceptions, use `raise ... from original_exception` for better debuggability.

### 3.5 Docstrings and Comments

*   **Docstrings:** Provide concise docstrings for modules, classes, methods, and functions, explaining their purpose, arguments, and return values. Spanish is acceptable for docstrings where appropriate, following existing patterns.
*   **Comments:** Use inline comments sparingly to explain complex logic or non-obvious code sections. Avoid redundant comments that merely restate the code.

### 3.6 General Formatting

*   **Indentation:** Use 4 spaces per indentation level.
*   **Line Length:** Strive for a maximum line length of 80 characters (as per PEP 8), though some existing code may exceed this. Agents should aim to adhere to 80 characters.
*   **Blank Lines:** Use blank lines to separate logical blocks of code, methods within a class, and class definitions.

## 4. Cursor/Copilot Rules

No specific Cursor or Copilot instruction files (`.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`) were found in this repository. Agents should follow the general code style guidelines outlined above.
