"""Dependency-boundary tests for the scaffolded domain package."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_DOMAIN_IMPORTS = {"streamlit", "pandas", "sklearn", "joblib"}
INFRASTRUCTURE_IMPORTS = {"joblib"}


def test_domain_modules_do_not_import_infrastructure_libraries() -> None:
    domain_dir = Path("src/churn_app/domain")

    for path in domain_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", maxsplit=1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", maxsplit=1)[0])

        assert imported_roots.isdisjoint(FORBIDDEN_DOMAIN_IMPORTS), path


def test_decision_policy_imports_no_infrastructure_libraries() -> None:
    path = Path("src/churn_app/services/decision_policy.py")

    assert _imported_roots(path).isdisjoint(
        {"streamlit", "pandas", "sklearn", "joblib", "hashlib", "json"}
    )


def test_artifact_loader_is_only_source_module_importing_joblib() -> None:
    source_paths = Path("src").glob("**/*.py")
    joblib_importers = [
        path for path in source_paths if "joblib" in _imported_roots(path)
    ]

    assert joblib_importers == [Path("src/churn_app/services/artifact_loader.py")]


def test_only_input_and_prediction_boundaries_import_pandas() -> None:
    source_paths = Path("src").glob("**/*.py")
    pandas_importers = [
        path for path in source_paths if "pandas" in _imported_roots(path)
    ]

    assert sorted(pandas_importers) == [
        Path("src/churn_app/services/input_builder.py"),
        Path("src/churn_app/services/prediction_service.py"),
    ]


def test_input_builder_imports_no_forbidden_runtime_boundaries() -> None:
    imported_roots = _imported_roots(Path("src/churn_app/services/input_builder.py"))

    assert "joblib" not in imported_roots
    assert "streamlit" not in imported_roots
    assert "prediction_service" not in imported_roots
    assert "decision_policy" not in imported_roots


def test_prediction_service_imports_no_forbidden_runtime_boundaries() -> None:
    imported_modules = _imported_modules(
        Path("src/churn_app/services/prediction_service.py")
    )

    assert "streamlit" not in _root_modules(imported_modules)
    assert "churn_app.services.input_builder" not in imported_modules
    assert "churn_app.services.decision_policy" not in imported_modules
    assert "churn_app.services.interpreter" not in imported_modules


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(
                alias.name.split(".", maxsplit=1)[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", maxsplit=1)[0])

    return imported_roots


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    return imported_modules


def _root_modules(imported_modules: set[str]) -> set[str]:
    return {module.split(".", maxsplit=1)[0] for module in imported_modules}
