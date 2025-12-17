"""Robustness tests module."""
import random
import struct
from unittest.mock import Mock, patch

import pytest


class TestRobustness:
    """Tests de robustesse face aux entrées invalides."""
    
    def test_truncated_pointset(self, client):
        """Test: PointSet tronqué -> 400."""
        truncated_data = b'\x03\x00\x00\x00\x00\x00'  # Incomplete
        
        response = client.post('/pointset', data=truncated_data)
        assert response.status_code in [400, 405]
    
    def test_non_float_coordinates(self):
        """Test: Coordonnées non float (NaN) -> 400."""
        from Triangulator.binary_format import binary_to_pointset
        
        # Binary data with NaN in one coordinate
        # Count = 1 (4 bytes), then NaN and 0.0 (8 bytes)
        invalid_data = struct.pack('<L', 1) + struct.pack('<ff', float('nan'), 0.0)
        
        with pytest.raises((ValueError, struct.error)):
            binary_to_pointset(invalid_data)
    
    def test_unreachable_service(self, client):
        """Test: Service injoignable -> 503."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = ConnectionError()
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 503
    
    def test_empty_result(self, client):
        """Test: Résultat vide -> message clair."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]  # Collinear
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            
            # Peut être 200 avec résultat vide ou 400 avec message
            assert response.status_code in [200, 400]
    
    def test_internal_exception_handling(self, client):
        """Test: Exceptions -> 500."""
        # Mock pointset_manager to ensure points are found (avoids 404)
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

        with patch('triangulator.triangulate') as mock_tri, \
             patch('triangulator.pointset_manager', mock_pm):
            mock_tri.side_effect = RuntimeError("Unexpected error")
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 500
    
    def test_timeout_handling(self, client):
        """Test: Timeout -> 504."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = TimeoutError()
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 504
    
    
    def test_negative_coordinates_robustness(self):
        """Test: Points avec coordonnées négatives."""
        from Triangulator.triangulator import triangulate
        
        points = [
            (-100.0, -200.0),
            (-50.0, -100.0),
            (-75.0, -50.0)
        ]
        
        # pas d' erreur
        triangles = triangulate(points)
        assert isinstance(triangles, list)
    
    def test_beyond_float_limits(self):
        """Test: Valeurs au-delà des limites float."""
        from Triangulator.triangulator import triangulate
        
        # Très grandes valeurs mais encore dans les limites
        points = [
            (1e30, 1e30),
            (1e30 + 1, 1e30),
            (1e30 + 0.5, 1e30 + 1)
        ]
        
        try:
            triangles = triangulate(points)
            assert isinstance(triangles, list)
        except (ValueError, OverflowError):
            pass  # rejet si trop grand
    
    def test_random_corrupted_data(self):
        """Test: Données aléatoires/corrompues."""
        from Triangulator.binary_format import binary_to_pointset
        
        # Générer données aléatoires
        corrupted = bytes(random.getrandbits(8) for _ in range(20))
        
        # Devrait lever une exception mais ne pas crasher
        with pytest.raises((ValueError, struct.error, AssertionError)):
            binary_to_pointset(corrupted)
    
    def test_pointset_with_single_point(self):
        """Test: PointSet avec un seul point."""
        from Triangulator.triangulator import triangulate
        
        points = [(0.0, 0.0)]
        
        with pytest.raises(ValueError) as exc_info:
            triangulate(points)
        
        assert "insufficient" in str(exc_info.value).lower() or \
               "moins" in str(exc_info.value).lower()
    
    def test_pointset_with_two_points(self):
        """Test: PointSet avec deux points."""
        from Triangulator.triangulator import triangulate
        
        points = [(0.0, 0.0), (1.0, 1.0)]
        
        with pytest.raises(ValueError) as exc_info:
            triangulate(points)
        
        assert "insufficient" in str(exc_info.value).lower() or \
               "moins" in str(exc_info.value).lower()
    
    def test_database_connection_failure(self, client):
        """Test: Défaillance  base de données."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = ConnectionError("DB connection lost")
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 503
    
    def test_pointset_format_mismatch(self, client):
        """Test: Format PointSet inattendu."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = {"invalid": "format"}  # Dict au lieu de list
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [400, 500]
    
    def test_triangle_with_out_of_range_indices(self):
        """Test: Triangle avec indices hors limites."""
        from Triangulator.binary_format import triangles_to_binary
        
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        
        # indice invalide
        invalid_triangles = [(0, 1, 999)]
        
        with pytest.raises((ValueError, IndexError)):
            triangles_to_binary(points, invalid_triangles)