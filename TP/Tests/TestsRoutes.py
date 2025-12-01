import pytest
from unittest.mock import Mock, patch


class TestTriangulationEndpoint:
    """Tests de  GET /triangulation/{pointSetId}."""
    
    def test_valid_triangulation_request(self, client, mock_pointset_manager):
        """Test: Cas valide -> réponse 200 + Triangles."""
        with patch('triangulator.pointset_manager', mock_pointset_manager):
            response = client.get('/triangulation/test-id-123')
            
            assert response.status_code == 200
            assert response.content_type == 'application/octet-stream'
            assert len(response.data) > 0
    
    def test_nonexistent_id(self, client):
        """Test: ID inexistant -> 404."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = Exception("Not found")
            
            response = client.get('/triangulation/nonexistent-id')
            
            assert response.status_code == 404
    
    def test_malformed_id(self, client):
        """Test: ID mal formé -> 400."""
        response = client.get('/triangulation/')
        assert response.status_code in [400, 404]
        
        response = client.get('/triangulation/../../etc/passwd')
        assert response.status_code == 400
    
    def test_triangulation_failed(self, client, mock_pointset_manager):
        """Test: Triangulation échouée -> 500."""
        mock_pointset_manager.get_pointset.return_value = []
        
        with patch('triangulator.pointset_manager', mock_pointset_manager):
            response = client.get('/triangulation/test-id-123')
            
            assert response.status_code == 500
    
    def test_storage_service_unavailable(self, client):
        """Test: DB indisponible -> 503."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = ConnectionError("Service unavailable")
            
            response = client.get('/triangulation/test-id-123')
            
            assert response.status_code == 503


class TestErrorHandling:
    """Tests gestion erreurs HTTP."""
    
    def test_400_bad_request(self, client):
        """Test: Code 400 pour requête invalide."""
        response = client.post('/triangulation/invalid', data=b'invalid')
        assert response.status_code in [400, 405]
    
    def test_404_not_found(self, client):
        """Test: Code 404 pour ressource non trouvée."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
    
    def test_500_internal_error(self, client):
        """Test: Code 500 pour erreur interne."""
        with patch('triangulator.triangulate') as mock_tri:
            mock_tri.side_effect = Exception("Internal error")
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 500
    
    def test_503_service_unavailable(self, client):
        """Test: Code 503 pour service indisponible."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = ConnectionError()
            
            response = client.get('/triangulation/test-id')
            assert response.status_code == 503

class TestPointSetRegistration:
    """Tests de l'enregistrement de PointSet (POST /pointset)."""
    
    def test_post_pointset_success(self, client):
        """Test: POST /pointset avec données valides -> 201."""
        from binary_format import pointset_to_binary
        
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        binary_data = pointset_to_binary(test_points)
        
        response = client.post('/pointset', data=binary_data)
        
        assert response.status_code == 201
        # Réponse doit contenir un pointSetId
        assert 'pointSetId' in response.json or response.json.get('id')
    
    def test_post_pointset_invalid_format(self, client):
        """Test: POST /pointset avec format invalide -> 400."""
        response = client.post('/pointset', data=b'invalid data')
        
        assert response.status_code == 400
    
    def test_post_pointset_empty(self, client):
        """Test: POST /pointset avec données vides -> 400."""
        response = client.post('/pointset', data=b'')
        
        assert response.status_code == 400
    
    def test_get_pointset_success(self, client):
        """Test: GET /pointset/{id} avec ID valide -> 200."""
        from binary_format import pointset_to_binary
        
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        binary_data = pointset_to_binary(test_points)
        
        # Enregistrer d'abord
        post_response = client.post('/pointset', data=binary_data)
        pointset_id = post_response.json.get('pointSetId')
        
        # Récupérer
        get_response = client.get(f'/pointset/{pointset_id}')
        
        assert get_response.status_code == 200
        assert get_response.content_type == 'application/octet-stream'
    
    def test_get_pointset_not_found(self, client):
        """Test: GET /pointset/{id} avec ID inexistant -> 404."""
        response = client.get('/pointset/nonexistent-id')
        
        assert response.status_code == 404