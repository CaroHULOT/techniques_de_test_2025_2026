.PHONY: all install test unit_test perf_test coverage lint doc help clean

all: install test lint coverage doc
	@echo " Vérification complète terminé ."

help:
	@echo "Commandes disponibles:"
	@echo "  make all            - Installe tout et lance TOUS les tests + qualité"
	@echo "  make install        - Installe les dépendances pip"
	@echo "  make test           - Exécute TOUS les tests (unit + perf)"
	@echo "  make unit_test      - Tests unitaires SEULEMENT"
	@echo "  make perf_test      - Tests de PERFORMANCE SEULEMENT"
	@echo "  make coverage       - Génère le rapport de coverage"
	@echo "  make lint           - Vérifie la qualité du code (ruff)"
	@echo "  make doc            - Génère la documentation HTML"
	@echo "  make clean          - Nettoie les fichiers temporaires"

install:
	pip install -r requirements.txt

test:
	pytest -v

unit_test:
	pytest -v -m "not performance"

perf_test:
	pytest -v -m "performance"

coverage:
	pytest --cov=. --cov-report=term --cov-report=html --ignore=TestsPerformance.py
	@echo "Rapport HTML généré dans htmlcov/index.html"

lint:
	ruff check . --fix

doc:
	pdoc3 --html . --force --output-dir docs

clean:
	rm -rf .pytest_cache __pycache__ .coverage htmlcov dist build *.egg-info docs
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete