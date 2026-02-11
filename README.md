# Flight Manager

Flight Manager is a Python-based project designed to manage flight-related data and operations using a clean, layered architecture. The repository is structured to separate concerns clearly (data access, business logic, and UI/CLI), making it easy to extend, test, and maintain.

---

## Project Structure

```
flight-manager/
├── data/
├── flightmanagement/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── ui/
│   ├── cli.py
│   └── error.py
│
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Directory Breakdown

### `data/`

Contains persistent application data.

* **FlightManagement.db** – SQLite database storing application data. When the application is first run, a new database file will be created with schema and populated with example data.

### `flightmanagement/`

Core application package.

* **db/**
  Database configuration, connection and transaction handling, schema creation and seed data insert.

* **models/**
  Domain models representing core entities such as flights, airports, pilots, aircraft etc.

* **repositories/**
  Data access layer. Repositories encapsulate database queries and persistence logic, keeping it separate from business rules.

* **services/**
  Business logic layer. Services coordinate repositories and enforce domain rules.

* **ui/**
  User interface layer (CLI prompts, menus, or future UI implementations).

* **cli.py**
  Entry point for running the application from the command line.

* **error.py**
  Custom error and exception definitions used across the application.

### `tests/`

Automated tests for validating application behavior (unit, integration, or end-to-end).

---

## Getting Started

### Prerequisites

* Python 3.9+
* Virtual environment tool (optional but recommended)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### Running the Application

```bash
python -m flightmanagement.cli
```

---

## Design Philosophy

* **Layered architecture** – Clear separation between UI, services, repositories, and models
* **Testability** – Business logic is isolated and easy to test
* **Extensibility** – New features (e.g., APIs, GUIs) can be added without major refactoring

---

## License

This project is licensed under the terms of the LICENSE file included in the repository.
