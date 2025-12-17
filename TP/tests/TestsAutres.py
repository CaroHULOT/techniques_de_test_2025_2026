"""Tests de cas limites."""
import pytest


class TestEdgeCases:
    """Tests de cas limites."""
    
    def test_single_point(self):
        """Test: Un seul point."""
        from triangulator import triangulate
        
        points = [(0.0, 0.0)]
        
        with pytest.raises(ValueError):
            triangulate(points)
    
    def test_two_points(self):
        """Test: Deux points."""
        from triangulator import triangulate
        
        points = [(0.0, 0.0), (1.0, 1.0)]
        
        with pytest.raises(ValueError):
            triangulate(points)