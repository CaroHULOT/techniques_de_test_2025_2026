import pytest
from unittest.mock import Mock


@pytest.fixture
def sample_points():
    """Mock fournissant un ensemble de points."""
    return [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.5, 1.0)
    ]

@pytest.fixture
def square_points():
    """Mock fournissant 4 points formant un carré."""
    return [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0)
    ]

@pytest.fixture
def collinear_points():
    """Mock fournissant des points alignés."""
    return [
        (0.0, 0.0),
        (1.0, 0.0),
        (2.0, 0.0)
    ]

@pytest.fixture
def large_pointset():
    """Mock fournissant un grand ensemble de points pour tests de performance."""
    points = []
    for i in range(1000):
        x = float(i % 100)
        y = float(i // 100)
        points.append((x, y))
    return points


@pytest.fixture
def large_pointset_1000():
    """Mock: 1000 points."""
    import random
    random.seed(42)
    points = []
    for i in range(1000):
        x = random.uniform(-1000.0, 1000.0)
        y = random.uniform(-1000.0, 1000.0)
        points.append((x, y))
    return points

@pytest.fixture
def extreme_pointset():
    """Mock: Points avec coordonnées extrêmes."""
    return [
        (float('-1e6'), float('-1e6')),
        (float('1e6'), float('1e6')),
        (0.0, 0.0)
    ]

@pytest.fixture
def very_close_points():
    """Mock: Points très proches."""
    return [
        (0.0, 0.0),
        (1e-8, 1e-8),
        (2e-8, 0.0)
    ]

@pytest.fixture
def negative_coordinates_points():
    """Mock: Points avec coordonnées négatives."""
    return [
        (-100.0, -100.0),
        (-50.0, -50.0),
        (-75.0, 25.0)
    ]

@pytest.fixture
def mixed_scale_points():
    """Mock: Points à différentes échelles."""
    return [
        (0.0001, 0.0001),
        (1000.0, 1000.0),
        (500.0, 500.0)
    ]

@pytest.fixture
def flask_app():
    """Mock pour l'application Flask."""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Ajoute les routes du Triangulator
    @app.route('/triangulation/<pointset_id>', methods=['GET'])
    def triangulation(pointset_id):
        # Placeholder - sera implémenté par le Triangulator
        return {'error': 'Not implemented'}, 501
    
    @app.route('/pointset', methods=['POST'])
    def store_pointset():
        # Placeholder - sera implémenté par le Triangulator
        return {'error': 'Not implemented'}, 501
    
    @app.route('/pointset/<pointset_id>', methods=['GET'])
    def get_pointset(pointset_id):
        # Placeholder - sera implémenté par le Triangulator
        return {'error': 'Not implemented'}, 501
    
    return app

@pytest.fixture
def client(flask_app):
    """Client de test Flask."""
    return flask_app.test_client()

@pytest.fixture
def mock_pointset_manager():
    """Mock du PointSetManager."""
    mock = Mock()
    mock.get_pointset.return_value = [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.5, 1.0)
    ]
    return mock

@pytest.fixture
def mock_database():
    """Mock de la base de données."""
    mock = Mock()
    mock.store.return_value = "test-id-123"
    mock.retrieve.return_value = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?\x00\x00\x00\x00\x00\x00\x00?\x00\x00\x80?'
    return mock

@pytest.fixture
def mock_pointset_manager_with_timeout():
    """Mock du PointSetManager avec timeout."""
    mock = Mock()
    mock.get_pointset.side_effect = TimeoutError("Request timeout")
    return mock

@pytest.fixture
def mock_pointset_manager_unavailable():
    """Mock du PointSetManager indisponible."""
    mock = Mock()
    mock.get_pointset.side_effect = ConnectionError("Service unavailable")
    return mock

@pytest.fixture
def corrupted_binary_data():
    """Mock: Données binaires corrompues."""
    return b'\xFF\xFF\xFF\xFF' + b'\x00' * 100

@pytest.fixture
def empty_binary_data():
    """Mock: Données binaires vides."""
    return b''

@pytest.fixture
def oversized_binary_data():
    """Mock: Données binaires volumineuses."""
    return b'\x00\x0c\x42\x6f' + b'\x00' * (50 * 1024 * 1024)