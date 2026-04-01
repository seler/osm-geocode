# OSM Geocode - Development tasks

# Default recipe: list available recipes
default:
    @just --list

# Python binary in the pyenv virtualenv
python := env("HOME") / ".pyenv/versions/osm-geocode/bin/python"
pytest := env("HOME") / ".pyenv/versions/osm-geocode/bin/pytest"
pip := env("HOME") / ".pyenv/versions/osm-geocode/bin/pip"

# Install test dependencies (no editable install - conflicts with HA loader)
install:
    {{pip}} install "pytest>=8.0" "pytest-asyncio>=0.23" "pytest-homeassistant-custom-component>=0.13" "requests-mock>=1.11"

# Run unit tests
test *args='':
    {{pytest}} tests/ -v {{args}}

# Run unit tests with coverage
test-cov:
    {{pytest}} tests/ -v --cov=custom_components/osm_geocode --cov-report=term-missing

# Run Docker integration tests (HA + HACS)
integration:
    bash tests/integration/test_integration.sh

# Run HACS validation (requires GitHub Actions via act)
hacs-validate:
    act -j hacs-validation --container-architecture linux/amd64

# Run all tests
test-all: test integration

# Run GitHub Actions locally with act
ci-local:
    act --container-architecture linux/amd64

# Run a specific GH Actions job locally
ci-job job:
    act -j {{job}} --container-architecture linux/amd64

# Clean up Docker resources
clean:
    docker compose -f tests/integration/docker-compose.yml down --remove-orphans --rmi local 2>/dev/null || true
