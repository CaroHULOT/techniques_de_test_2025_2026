
"""Integration tests module."""

from unittest.mock import Mock, patch


class TestIntegrationWithMocks:
    """Tests d'intégration."""
    
    def test_full_workflow_with_mock_pointset_manager(self, client):
        """Test: Flux complet avec PointSetManager simulé."""
        mock_pm = Mock()
        
        #POST pour enregistrer un pointset
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        mock_pm.store_pointset.return_value = "id-123"
        
        #GET pour récupérer le pointset
        mock_pm.get_pointset.return_value = test_points
        
        with patch('triangulator.pointset_manager', mock_pm):
            #enregistrement
            pointset_id = mock_pm.store_pointset(test_points)
            assert pointset_id == "id-123"
            
            # Récupérer et vérifier
            retrieved = mock_pm.get_pointset(pointset_id)
            assert retrieved == test_points
            
            # Demander la triangulation
            response = client.get(f'/triangulation/{pointset_id}')
            assert response.status_code == 200
    
    def test_triangulator_pointset_manager_integration(self, client):
        """Test: Triangulator verq PointSetManager."""
        mock_pm = Mock()
        test_id = "test-integration-id"
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        
        mock_pm.get_pointset.return_value = test_points
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get(f'/triangulation/{test_id}')
            
            assert response.status_code == 200
            assert len(response.data) > 0
            mock_pm.get_pointset.assert_called_once_with(test_id)
    
    def test_integration_nonexistent_id_error(self, client):
        """Test: ID inexistant -> 400."""
        mock_pm = Mock()
        mock_pm.get_pointset.side_effect = KeyError("ID not found")
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/nonexistent')
            assert response.status_code in [400, 404]
    
    def test_integration_service_unavailable(self, client):
        """Test: Service PointSetManager indisponible -> 502,503."""
        mock_pm = Mock()
        mock_pm.get_pointset.side_effect = ConnectionError("Cannot connect")
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [502, 503]
    
    def test_integration_invalid_format(self, client):
        """Test: Format invalide -> 400."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = "invalid format"
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [400, 500]
    
    def test_pointset_manager_returns_invalid_format(self, client):
        """Test: PointSetManager retourne un format invalide."""
        mock_pm = Mock()
        
        # Retourne un dict au lieu de list
        mock_pm.get_pointset.return_value = {
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        }
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [400, 500]
    
    def test_pointset_manager_partial_data(self, client):
        """Test: PointSetManager retourne  des données partielles."""
        mock_pm = Mock()
        
        # Données partielles/corrompues
        mock_pm.get_pointset.return_value = [(0.0,)]  # Coordonnée incomplète
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [400, 500]
    
    def test_multiple_concurrent_triangulations(self, client):
        """Test: plusieurs triangulations en meme temps."""
        import threading
        
        mock_pm = Mock()
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        mock_pm.get_pointset.return_value = test_points
        
        results = []
        
        def triangulate():
            with patch('triangulator.pointset_manager', mock_pm):
                response = client.get('/triangulation/test-id')
                results.append(response.status_code)
        
        threads = [threading.Thread(target=triangulate) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Toutes les réponses  OK
        assert all(code == 200 for code in results)

    def test_integration_timeout_handling(self, client):
        """Test: gestion des timeouts du PointSetManager."""
        mock_pm = Mock()
        mock_pm.get_pointset.side_effect = TimeoutError("Request timed out")
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/test-id')
            assert response.status_code in [504, 503]