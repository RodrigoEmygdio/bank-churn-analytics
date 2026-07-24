"""Static checks for Docker-based local execution."""

from __future__ import annotations

from pathlib import Path


def test_dockerfile_defines_supported_streamlit_runtime() -> None:
    dockerfile = Path("Dockerfile")
    content = dockerfile.read_text(encoding="utf-8")

    assert dockerfile.is_file()
    assert "FROM python:3.14-slim" in content
    assert "uv sync --locked --no-dev --no-install-project" in content
    assert "EXPOSE 8501" in content
    assert "--server.address=0.0.0.0" in content
    assert "--server.port=8501" in content
    assert "--server.headless=true" in content
    assert "--browser.gatherUsageStats=false" in content


def test_dockerfile_packages_required_runtime_artifacts() -> None:
    content = Path("Dockerfile").read_text(encoding="utf-8")

    assert "COPY pyproject.toml uv.lock README.md ./" in content
    assert "COPY app.py ./" in content
    assert "COPY src ./src" in content
    assert "COPY artifacts ./artifacts" in content
    assert content.index("COPY pyproject.toml uv.lock README.md ./") < content.index(
        "COPY src ./src"
    )


def test_dockerfile_runs_as_non_root_user() -> None:
    content = Path("Dockerfile").read_text(encoding="utf-8")

    assert "useradd" in content
    assert "USER appuser" in content
    assert "USER root" not in content


def test_dockerfile_has_streamlit_healthcheck() -> None:
    content = Path("Dockerfile").read_text(encoding="utf-8")

    assert "HEALTHCHECK" in content
    assert "http://localhost:8501/_stcore/health" in content


def test_dockerignore_preserves_required_runtime_inputs() -> None:
    dockerignore = Path(".dockerignore")
    ignored_entries = {
        line.strip()
        for line in dockerignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }

    assert dockerignore.is_file()
    assert ".git" in ignored_entries
    assert ".venv" in ignored_entries
    assert "__pycache__" in ignored_entries
    assert "artifacts" not in ignored_entries
    assert "artifacts/" not in ignored_entries
    assert "pyproject.toml" not in ignored_entries
    assert "uv.lock" not in ignored_entries


def test_compose_file_exposes_streamlit_port() -> None:
    compose = Path("docker-compose.yml")
    content = compose.read_text(encoding="utf-8")

    assert compose.is_file()
    assert "bank-churn-analytics" in content
    assert "8501:8501" in content
    assert "privileged" not in content


def test_readme_documents_docker_workflow() -> None:
    content = Path("README.md").read_text(encoding="utf-8")

    assert "docker build -t bank-churn-analytics ." in content
    assert "docker run --rm -p 8501:8501 bank-churn-analytics" in content
    assert "docker compose up --build" in content
    assert "http://localhost:8501" in content
