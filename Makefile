.PHONY: all install test unit_test perf_test coverage lint doc help clean run

all: install test lint coverage doc
	@echo "Vérification complète terminée."

help:
	@echo "Commandes disponibles:"
	@echo "  make install        - Installe les dépendances pip"
	@echo "  make test           - Exécute TOUS les tests"
	@echo "  make unit_test      - Tests unitaires SEULEMENT (pas performance)"
	@echo "  make perf_test      - Tests de PERFORMANCE SEULEMENT"
	@echo "  make coverage       - Génère le rapport de coverage"
	@echo "  make lint           - Vérifie la qualité du code (ruff)"
	@echo "  make doc            - Génère la documentation HTML"
	@echo "  make run            - Lance le serveur Triangulator"
	@echo "  make clean          - Nettoie les fichiers temporaires"
	@echo "  make all            - Fait tout : install + test + lint + coverage + doc"

install:
	python3 -m pip install -r requirements.txt -r dev_requirements.txt
	@echo "✓ Dépendances installées"

test:
	python3 -m pytest ./TP/tests -v --tb=short
	@echo "✓ Tous les tests exécutés"

unit_test:
	python3 -m pytest ./TP/tests -v --ignore=./TP/tests/TestsQualite.py -m "not performance" --tb=short
	@echo "✓ Tests unitaires exécutés"

perf_test:
	python3 -m pytest ./TP/tests -v --ignore=./TP/tests/TestsQualite.py -m "performance" --tb=short
	@echo "✓ Tests de performance exécutés"

coverage:
	coverage run -m pytest TP/tests/ --tb=short && coverage report -m && coverage html -d TP/htmlcov
	@echo "✓ Rapport de coverage généré dans TP/htmlcov/index.html"

lint:
	cd TP && ruff check . --fix
	@echo "✓ Vérification de qualité terminée"

doc:
	cd TP && pdoc3 --html . --force --output-dir docs
	@echo "✓ Documentation générée dans TP/docs/"

benchmark:
	cd TP && python3 benchmark_triangulation.py
	@echo "✓ Benchmark terminé"

clean:
	cd TP && rm -rf .pytest_cache __pycache__ .coverage htmlcov dist build *.egg-info docs
	find TP -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find TP -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Fichiers nettoyés"



#pris des cas ou on sait que ca va pas passer ou que ca va etre compliqué