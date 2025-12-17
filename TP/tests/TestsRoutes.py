"""Routes tests module."""
from Triangulator.binary_format import pointset_to_binary


class TestTriangulationEndpoint:
    """Tests de  GET /triangulation/{pointSetId}."""
    
    def test_valid_triangulation_request(self, client):
        """Test: Cas valide -> réponse 200 + Triangles."""
        # D'abord créer un pointset
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        binary = pointset_to_binary(points)
        resp = client.post('/pointset', data=binary)
        assert resp.status_code == 201
        pointset_id = resp.get_json()['pointSetId']
        
        # Puis demander la triangulation
        response = client.get(f'/triangulation/{pointset_id}')
        
        assert response.status_code == 200
        assert response.content_type == 'application/octet-stream'
        assert len(response.data) > 0
    
    def test_nonexistent_id(self, client):
        """Test: ID inexistant -> 404."""
        response = client.get('/triangulation/nonexistent-id-12345')
        assert response.status_code == 404
    
    def test_malformed_id(self, client):
        """Test: ID mal formé -> 400 ou 404."""
        response = client.get('/triangulation/../../etc/passwd')
        assert response.status_code in [400, 404]
    
    def test_triangulation_collinear(self, client):
        """Test: Points colinéaires -> liste vide."""
        # Points colinéaires
        points = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        binary = pointset_to_binary(points)
        resp = client.post('/pointset', data=binary)
        pointset_id = resp.get_json()['pointSetId']
        
        response = client.get(f'/triangulation/{pointset_id}')
        assert response.status_code == 200



class TestErrorHandling:
    """Tests gestion erreurs HTTP."""
    
    def test_400_bad_request(self, client):
        """Test: Code 400 pour requête invalide."""
        response = client.post('/pointset', data=b'invalid binary data')
        assert response.status_code == 400
    
    def test_404_not_found(self, client):
        """Test: Code 404 pour ressource non trouvée."""
        response = client.get('/pointset/nonexistent-id')
        assert response.status_code == 404


class TestPointSetRegistration:
    """Tests de l'enregistrement de PointSet (POST /pointset)."""
    
    def test_post_pointset_success(self, client):
        """Test: POST /pointset avec données valides -> 201."""
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        binary_data = pointset_to_binary(test_points)
        
        response = client.post('/pointset', data=binary_data)
        
        assert response.status_code == 201
        assert 'pointSetId' in response.json
    
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