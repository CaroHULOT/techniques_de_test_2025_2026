"""Module for performance tests."""
import time
from unittest.mock import Mock, patch

import pytest


@pytest.mark.performance
class TestPerformance:
    """Tests de performance."""
    
    def test_large_pointset_triangulation(self, large_pointset):
        """Test: Triangulation d'un grand nombre de points."""
        from Triangulator.triangulator import triangulate
        
        start_time = time.time()
        triangles = triangulate(large_pointset)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Triangulation took {execution_time}s, expected < 5s"
        assert len(triangles) > 0
    
    def test_repeated_requests_performance(self, client):
        """Test: Requêtes répétées."""
        mock_pm = Mock()
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        mock_pm.get_pointset.return_value = test_points
        
        num_requests = 100
        times = []
        
        with patch('triangulator.pointset_manager', mock_pm):
            for _ in range(num_requests):
                start = time.time()
                response = client.get('/triangulation/test-id')
                times.append(time.time() - start)
                assert response.status_code == 200
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Average time {avg_time}s, expected < 0.1s"
    
    @pytest.mark.performance
    def test_memory_usage(self, large_pointset):
        """Test: Mesure de l'utilisation de lamémoire."""
        import tracemalloc

        from Triangulator.triangulator import triangulate
        
        tracemalloc.start()
        
        _ = triangulate(large_pointset)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Vérifier que la mémoire utilisée est raisonnable (< 50 MB)
        assert peak < 50 * 1024 * 1024, f"memory {peak / (1024*1024):.2f} MB"
    
    @pytest.mark.performance
    def test_binary_conversion_performance(self, large_pointset):
        """Test: Performance des conversions binaires."""
        from Triangulator.binary_format import binary_to_pointset, pointset_to_binary
        
        # Conversion vers binaire
        start = time.time()
        binary_data = pointset_to_binary(large_pointset)
        to_binary_time = time.time() - start
        
        # Conversion depuis binaire
        start = time.time()
        _ = binary_to_pointset(binary_data)
        from_binary_time = time.time() - start
        
        assert to_binary_time < 0.5
        assert from_binary_time < 0.5