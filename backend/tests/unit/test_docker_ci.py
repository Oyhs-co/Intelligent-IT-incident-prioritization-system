"""Tests unitarios para Docker y CI/CD.

Verifica:
  - Dockerfile tiene estructura multistage
  - entrypoint.sh existe con comandos correctos
  - docker-compose.yml es válido
  - CI workflow es YAML válido
"""

from pathlib import Path

import yaml

BACKEND_DIR = Path(__file__).parent.parent.parent


class TestDockerfile:
    """Tests para el Dockerfile multistage."""

    DOCKERFILE_PATH = BACKEND_DIR / "Dockerfile"

    def test_dockerfile_exists(self):
        """El Dockerfile debe existir."""
        assert self.DOCKERFILE_PATH.exists(), "Dockerfile no encontrado"

    def test_dockerfile_multistage(self):
        """Dockerfile debe tener dos stages (builder y runtime)."""
        content = self.DOCKERFILE_PATH.read_text(encoding="utf-8")
        assert "AS builder" in content, "Debe existir el stage builder"
        assert "FROM python:3.14-slim" in content, "Debe usar python:3.14-slim"
        assert content.count("FROM ") >= 2, "Debe tener al menos 2 stages"

    def test_dockerfile_exposes_port(self):
        """Dockerfile debe exponer el puerto 8000."""
        content = self.DOCKERFILE_PATH.read_text(encoding="utf-8")
        assert "EXPOSE 8000" in content, "Debe exponer el puerto 8000"

    def test_dockerfile_entrypoint(self):
        """Dockerfile debe tener entrypoint.sh como entrypoint."""
        content = self.DOCKERFILE_PATH.read_text(encoding="utf-8")
        assert "ENTRYPOINT" in content, "Debe tener ENTRYPOINT"
        assert "entrypoint.sh" in content, "Debe usar scripts/entrypoint.sh"

    def test_dockerfile_workdir(self):
        """Dockerfile debe definir WORKDIR /app."""
        content = self.DOCKERFILE_PATH.read_text(encoding="utf-8")
        assert "WORKDIR /app" in content, "Debe tener WORKDIR /app"


class TestEntrypoint:
    """Tests para scripts/entrypoint.sh."""

    ENTRYPOINT_PATH = BACKEND_DIR / "scripts" / "entrypoint.sh"

    def test_entrypoint_exists(self):
        """entrypoint.sh debe existir."""
        assert self.ENTRYPOINT_PATH.exists(), "entrypoint.sh no encontrado"

    def test_entrypoint_is_executable(self):
        """entrypoint.sh debe ser ejecutable (tener shebang)."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert content.startswith("#!/bin/bash"), "Debe comenzar con #!/bin/bash"

    def test_entrypoint_runs_init_db(self):
        """entrypoint.sh debe ejecutar init_db.py."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert "init_db" in content, "Debe ejecutar init_db.py"

    def test_entrypoint_runs_seed_data(self):
        """entrypoint.sh debe ejecutar seed_data.py."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert "seed_data" in content, "Debe ejecutar seed_data.py"

    def test_entrypoint_starts_uvicorn(self):
        """entrypoint.sh debe iniciar uvicorn."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert "uvicorn" in content, "Debe iniciar uvicorn"
        assert "src.main:app" in content, "Debe usar src.main:app"

    def test_entrypoint_set_e(self):
        """entrypoint.sh debe tener set -e."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert "set -e" in content, "Debe tener set -e para fail fast"

    def test_entrypoint_port_configurable(self):
        """entrypoint.sh debe usar PORT variable de entorno."""
        content = self.ENTRYPOINT_PATH.read_text(encoding="utf-8")
        assert "${PORT:-8000}" in content, "Debe permitir configurar puerto via PORT"


class TestDockerCompose:
    """Tests para docker-compose.yml."""

    COMPOSE_PATH = BACKEND_DIR / "docker-compose.yml"

    def test_compose_exists(self):
        """docker-compose.yml debe existir."""
        assert self.COMPOSE_PATH.exists(), "docker-compose.yml no encontrado"

    def test_compose_is_valid_yaml(self):
        """docker-compose.yml debe ser YAML válido."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert data is not None, "El YAML debe ser válido"
        assert "services" in data, "Debe tener servicios definidos"

    def test_compose_has_postgres(self):
        """docker-compose debe incluir postgres."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "postgres" in data["services"], "Debe tener servicio postgres"

    def test_compose_has_redis(self):
        """docker-compose debe incluir redis."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "redis" in data["services"], "Debe tener servicio redis"

    def test_compose_has_app(self):
        """docker-compose debe incluir la app."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "app" in data["services"], "Debe tener servicio app"

    def test_compose_app_depends_on_postgres(self):
        """La app debe depender de postgres healthy."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        deps = data["services"]["app"].get("depends_on", {})
        assert "postgres" in deps, "App debe depender de postgres"

    def test_compose_app_depends_on_redis(self):
        """La app debe depender de redis healthy."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        deps = data["services"]["app"].get("depends_on", {})
        assert "redis" in deps, "App debe depender de redis"

    def test_compose_postgres_healthcheck(self):
        """Postgres debe tener healthcheck."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "healthcheck" in data["services"]["postgres"], \
            "Postgres debe tener healthcheck"

    def test_compose_redis_healthcheck(self):
        """Redis debe tener healthcheck."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "healthcheck" in data["services"]["redis"], \
            "Redis debe tener healthcheck"

    def test_compose_has_prometheus(self):
        """docker-compose debe incluir prometheus."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "prometheus" in data["services"], "Debe tener servicio prometheus"

    def test_compose_has_grafana(self):
        """docker-compose debe incluir grafana."""
        content = self.COMPOSE_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "grafana" in data["services"], "Debe tener servicio grafana"


class TestCIWorkflow:
    """Tests para el workflow de CI en GitHub Actions."""

    CI_PATH = BACKEND_DIR.parent / ".github" / "workflows" / "backend-ci.yml"

    def test_ci_workflow_exists(self):
        """El workflow de CI debe existir."""
        assert self.CI_PATH.exists(), "backend-ci.yml no encontrado"

    def test_ci_workflow_is_valid_yaml(self):
        """El workflow debe ser YAML válido."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert data is not None, "El YAML debe ser válido"
        assert "name" in data, "Debe tener nombre"
        assert "jobs" in data, "Debe tener jobs definidos"

    def test_ci_has_test_job(self):
        """El workflow debe tener un job de tests."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "backend-tests" in data["jobs"], "Debe tener job backend-tests"

    def test_ci_uses_python_314(self):
        """El workflow debe usar Python 3.14."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        steps = data["jobs"]["backend-tests"]["steps"]
        python_versions = [
            s["with"]["python-version"]
            for s in steps
            if s.get("name") == "Setup Python"
        ]
        assert "3.14" in python_versions, "Debe usar Python 3.14"

    def test_ci_runs_lint(self):
        """El workflow debe ejecutar ruff check."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        assert "ruff check" in content, "Debe ejecutar ruff check"

    def test_ci_runs_tests_with_coverage(self):
        """El workflow debe ejecutar tests con cobertura."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        assert "pytest" in content, "Debe ejecutar pytest"
        assert "--cov" in content, "Debe incluir flag --cov"

    def test_ci_has_coverage_xml(self):
        """El workflow debe generar reporte XML de cobertura."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        assert "--cov-report=xml" in content, "Debe generar coverage.xml"

    def test_ci_working_directory(self):
        """El workflow debe usar backend como working-directory."""
        content = self.CI_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        defaults = data["jobs"]["backend-tests"].get("defaults", {})
        wd = defaults.get("run", {}).get("working-directory", "")
        assert wd == "backend", "Debe usar backend como working-directory"


class TestDotDockerignore:
    """Tests para .dockerignore."""

    DOCKERIGNORE_PATH = BACKEND_DIR / ".dockerignore"

    def test_dockerignore_exists(self):
        """.dockerignore debe existir."""
        assert self.DOCKERIGNORE_PATH.exists(), ".dockerignore no encontrado"

    def test_dockerignore_ignores_pycache(self):
        """.dockerignore debe ignorar __pycache__."""
        content = self.DOCKERIGNORE_PATH.read_text(encoding="utf-8")
        assert "__pycache__" in content, "Debe ignorar __pycache__"

    def test_dockerignore_ignores_git(self):
        """.dockerignore debe ignorar .git."""
        content = self.DOCKERIGNORE_PATH.read_text(encoding="utf-8")
        assert ".git" in content, "Debe ignorar .git"

    def test_dockerignore_ignores_env(self):
        """.dockerignore debe ignorar .env."""
        content = self.DOCKERIGNORE_PATH.read_text(encoding="utf-8")
        assert ".env" in content, "Debe ignorar .env"

    def test_dockerignore_ignores_tests(self):
        """.dockerignore debe ignorar tests/."""
        content = self.DOCKERIGNORE_PATH.read_text(encoding="utf-8")
        assert "tests/" in content, "Debe ignorar tests/"
