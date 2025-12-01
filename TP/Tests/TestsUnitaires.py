import pytest
import struct
from unittest.mock import Mock, patch


class TestTriangulationAlgorithm:
    """Tests unitaires de l'algorithme de triangulation."""
    
    def test_three_points_one_triangle(self, sample_points):
        """Test: 3 points -> 1 triangle correct."""
        from triangulator import triangulate
        
        triangles = triangulate(sample_points)
        
        assert len(triangles) == 1
        assert len(triangles[0]) == 3
        assert set(triangles[0]) == {0, 1, 2}
    
    def test_four_points_square_two_triangles(self, square_points):
        """Test: 4 points formant un carré -> 2 triangles."""
        from triangulator import triangulate
        
        triangles = triangulate(square_points)
        
        assert len(triangles) == 2
        for triangle in triangles:
            assert len(triangle) == 3
    
    def test_collinear_points_no_triangle(self, collinear_points):
        """Test: Points alignés -> aucun triangle."""
        from triangulator import triangulate
        
        triangles = triangulate(collinear_points)
        
        assert len(triangles) == 0
    
    def test_duplicate_points_rejection(self):
        """Test: Points dupliqués -> rejet ou fusion."""
        from triangulator import triangulate
        
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (0.5, 1.0),
            (0.0, 0.0)  # Dupliqué
        ]
        
        # Soit rejeter , soit fusionner
        try:
            triangles = triangulate(points)
            # Si fusion, vérifier qu'on a 3 points uniques
            unique_indices = set()
            for triangle in triangles:
                unique_indices.update(triangle)
            assert len(unique_indices) <= 3
        except ValueError as e:
            assert "duplicate" in str(e).lower() or "duplicat" in str(e).lower()
    
    def test_invalid_input_format(self):
        """Test: Format d'entrée invalide -> exceptions gérées."""
        from triangulator import triangulate
        
        with pytest.raises((TypeError, ValueError)):
            triangulate("invalid")
        
        with pytest.raises((TypeError, ValueError)):
            triangulate([1, 2, 3])
        
        with pytest.raises((TypeError, ValueError)):
            triangulate([(1.0,)])
    
    def test_empty_pointset(self):
        """Test: PointSet vide -> renvoyer une erreur."""
        from triangulator import triangulate
        
        with pytest.raises(ValueError) as exc_info:
            triangulate([])
        
        assert "empty" in str(exc_info.value).lower() or "vide" in str(exc_info.value).lower()
    
    def test_points_with_nan(self):
        """Test: Points avec NaN -> rejeter."""
        from triangulator import triangulate
        
        points = [
            (0.0, 0.0),
            (float('nan'), 0.0),
            (0.5, 1.0)
        ]
        
        with pytest.raises(ValueError) as exc_info:
            triangulate(points)
        
        assert "nan" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_points_with_inf(self):
        """Test: Points avec inf -> rejeter."""
        from triangulator import triangulate
        
        points = [
            (0.0, 0.0),
            (float('inf'), 0.0),
            (0.5, 1.0)
        ]
        
        with pytest.raises(ValueError) as exc_info:
            triangulate(points)
        
        assert "inf" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    
    def test_very_large_coordinates(self):
        """Test: Points avec très grandes coordonnées ->overflow potentiel."""
        from triangulator import triangulate
        
        points = [
            (1e6, 1e6),
            (1e6 + 1, 1e6),
            (1e6 + 0.5, 1e6 + 1)
        ]
        
        # Devrait fonctionner sans overflow
        triangles = triangulate(points)
        assert len(triangles) >= 0  # Au minimum, pas de crash
    
    def test_very_close_points_precision(self, very_close_points):
        """Test: Points très proches."""
        from triangulator import triangulate
        
        # Points séparés de 1e-8 peuvent causer des problèmes de précision
        try:
            triangles = triangulate(very_close_points)
            # Soit aucun triangle (si trop proches pour être distingués)
            # Soit un triangle valide
            assert len(triangles) >= 0
        except ValueError:
            # rejet si trop proches
            pass
    
    def test_large_number_of_points_1000(self, large_pointset_1000):
        """Test: Triangulation avec 1000 points."""
        from triangulator import triangulate
        
        triangles = triangulate(large_pointset_1000)
        
        # Vérifie qu'on a des triangles
        assert len(triangles) > 0
        
        # Vérifie que les indices sont valides
        for triangle in triangles:
            assert all(0 <= idx < len(large_pointset_1000) for idx in triangle)
    
    def test_negative_coordinates(self):
        """Test: Points avec coordonnées négatives."""
        from triangulator import triangulate
        
        points = [
            (-1.0, -1.0),
            (1.0, -1.0),
            (0.0, 1.0)
        ]
        
        triangles = triangulate(points)
        assert len(triangles) == 1


class TestBinaryConversions:
    """Tests unitaires des conversions binaires."""
    
    def test_pointset_to_binary(self, sample_points):
        """Test: PointSet -> flux binaire conforme."""
        from binary_format import pointset_to_binary
        
        binary_data = pointset_to_binary(sample_points)
        
        # Vérifie les 4 premiers bytes (nombre de points)
        num_points = struct.unpack('<L', binary_data[:4])[0]
        assert num_points == 3
        
        # Vérifie la taille totale
        expected_size = 4 + (3 * 8)  # 4 bytes header + 3 points * 8 bytes
        assert len(binary_data) == expected_size
        
        # Vérifier chaque point
        offset = 4
        for i, (x, y) in enumerate(sample_points):
            x_bytes = binary_data[offset:offset+4]
            y_bytes = binary_data[offset+4:offset+8]
            
            x_decoded = struct.unpack('<f', x_bytes)[0]
            y_decoded = struct.unpack('<f', y_bytes)[0]
            
            assert abs(x_decoded - x) < 1e-6
            assert abs(y_decoded - y) < 1e-6
            
            offset += 8
    
    def test_binary_to_pointset(self, sample_points):
        """Test: flux binaire -> PointSet, points identiques à l'original."""
        from binary_format import pointset_to_binary, binary_to_pointset
        
        binary_data = pointset_to_binary(sample_points)
        decoded_points = binary_to_pointset(binary_data)
        
        assert len(decoded_points) == len(sample_points)
        
        for original, decoded in zip(sample_points, decoded_points):
            assert abs(original[0] - decoded[0]) < 1e-6
            assert abs(original[1] - decoded[1]) < 1e-6
    
    def test_triangles_to_binary(self, sample_points):
        """Test: Triangles -> flux binaire conforme."""
        from binary_format import triangles_to_binary
        
        triangles = [(0, 1, 2)]
        binary_data = triangles_to_binary(sample_points, triangles)
        
        # Partie 1: PointSet
        num_points = struct.unpack('<L', binary_data[:4])[0]
        assert num_points == 3
        
        pointset_size = 4 + (3 * 8)
        
        # Partie 2: Triangles
        num_triangles = struct.unpack('<L', binary_data[pointset_size:pointset_size+4])[0]
        assert num_triangles == 1
        
        # Vérifier les indices du triangle
        offset = pointset_size + 4
        for i in range(3):
            idx = struct.unpack('<L', binary_data[offset:offset+4])[0]
            assert idx == i
            offset += 4
    
    def test_binary_to_triangles(self, sample_points):
        """Test: flux binaire -> Triangles, triangles identiques à l'original."""
        from binary_format import triangles_to_binary, binary_to_triangles
        
        original_triangles = [(0, 1, 2)]
        binary_data = triangles_to_binary(sample_points, original_triangles)
        
        decoded_points, decoded_triangles = binary_to_triangles(binary_data)
        
        assert len(decoded_triangles) == len(original_triangles)
        assert decoded_triangles[0] == original_triangles[0]
    
    def test_no_duplicate_vertex_in_triangle(self, sample_points):
        """Test: Vérifier qu'il n'y a pas plusieurs fois le même sommet pour un triangle."""
        from binary_format import triangles_to_binary, binary_to_triangles
        
        triangles = [(0, 1, 2)]
        binary_data = triangles_to_binary(sample_points, triangles)
        _, decoded_triangles = binary_to_triangles(binary_data)
        
        for triangle in decoded_triangles:
            assert len(set(triangle)) == 3, "Triangle has duplicate vertices"
    
    def test_binary_size_verification(self, sample_points):
        """Test: Vérification de la taille et du nombre de bytes."""
        from binary_format import pointset_to_binary, triangles_to_binary
        
        # PointSet
        ps_binary = pointset_to_binary(sample_points)
        expected_ps_size = 4 + len(sample_points) * 8
        assert len(ps_binary) == expected_ps_size
        
        # Triangles
        triangles = [(0, 1, 2)]
        tr_binary = triangles_to_binary(sample_points, triangles)
        expected_tr_size = expected_ps_size + 4 + len(triangles) * 12
        assert len(tr_binary) == expected_tr_size
    
    
    def test_binary_with_negative_coordinates(self):
        """Test: Conversion binaire avec coordonnées négatives."""
        from binary_format import pointset_to_binary, binary_to_pointset
        
        points = [
            (-1.5, -2.5),
            (3.0, -1.0),
            (-0.5, 4.5)
        ]
        
        binary_data = pointset_to_binary(points)
        decoded = binary_to_pointset(binary_data)
        
        for original, decoded_pt in zip(points, decoded):
            assert abs(original[0] - decoded_pt[0]) < 1e-6
            assert abs(original[1] - decoded_pt[1]) < 1e-6
    
    def test_binary_with_large_pointset(self, large_pointset_1000):
        """Test: Conversion binaire avec 1000 points."""
        from binary_format import pointset_to_binary, binary_to_pointset
        
        binary_data = pointset_to_binary(large_pointset_1000)
        decoded = binary_to_pointset(binary_data)
        
        assert len(decoded) == len(large_pointset_1000)
        
        # Vérification avec quelques points aléatoires
        for i in [0, 100, 500, 999]:
            assert abs(large_pointset_1000[i][0] - decoded[i][0]) < 1e-6
            assert abs(large_pointset_1000[i][1] - decoded[i][1]) < 1e-6
    
    def test_binary_corrupted_data(self):
        """Test: Données binaires corrompues -> exceptions."""
        from binary_format import binary_to_pointset
        
        # Données trop courtes
        corrupted = b'\x05\x00\x00\x00'
        
        with pytest.raises((ValueError, struct.error)):
            binary_to_pointset(corrupted)
    
    def test_binary_zero_points(self):
        """Test: Conversion binaire avec 0 points."""
        from binary_format import pointset_to_binary, binary_to_pointset
        
        points = []
        binary_data = pointset_to_binary(points)
        
        assert len(binary_data) >= 4
        
        decoded = binary_to_pointset(binary_data)
        assert len(decoded) == 0