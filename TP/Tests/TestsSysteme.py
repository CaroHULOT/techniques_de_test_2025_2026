import pytest
from unittest.mock import Mock, patch
import threading


class TestSystemWorkflow:
    """Tests du workflow complet."""
    
    def test_complete_workflow(self, client):
        """Test: Workflow complet de bout en bout."""
        mock_pm = Mock()
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        
        # 1. Client envoie un PointSet au PointSetManager
        mock_pm.store_pointset.return_value = "workflow-id-123"
        pointset_id = mock_pm.store_pointset(test_points)
        assert pointset_id == "workflow-id-123"
        
        # 2. PointSetManager renvoie un pointSetId
        assert pointset_id is not None
        
        # 3. Client demande la triangulation au Triangulator
        mock_pm.get_pointset.return_value = test_points
        
        with patch('triangulator.pointset_manager', mock_pm):
            # 4. Triangulator contacte PointSetManager pour récupérer les points
            response = client.get(f'/triangulation/{pointset_id}')
            
            # 5. Triangulator renvoie les triangles au client
            assert response.status_code == 200
            assert response.content_type == 'application/octet-stream'
            assert len(response.data) > 0
            
            # Vérifier que le PointSetManager a été appelé
            mock_pm.get_pointset.assert_called_once()
    
    def test_workflow_with_missing_service(self, client):
        """Test: Workflow avec service manquant -> erreur approprié."""
        with patch('triangulator.pointset_manager') as mock_pm:
            mock_pm.get_pointset.side_effect = ConnectionError("Service unavailable")
            
            response = client.get('/triangulation/test-id')
            
            assert response.status_code in [502, 503]
            # Vérifie qu'il y a un message d'erreur
            assert response.data is not None
        
    def test_pointset_manager_fails_midway(self, client):
        """Test: Quand PointSetManager échoue à mi-trajet."""
        mock_pm = Mock()
        
        # Premier appel OK, deuxième échoue
        mock_pm.get_pointset.side_effect = [
            [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)],  # OK
            ConnectionError("Lost connection")     # Échoue
        ]
        
        with patch('triangulator.pointset_manager', mock_pm):
            # Première requête OK
            response1 = client.get('/triangulation/id-1')
            assert response1.status_code == 200
            
            # Deuxieme requête pas OK
            response2 = client.get('/triangulation/id-2')
            assert response2.status_code in [502, 503]
    
    def test_concurrent_triangulation_requests(self, client):
        """Test: Plusieurs requêtes simultanées."""
        mock_pm = Mock()
        test_points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        mock_pm.get_pointset.return_value = test_points
        
        results = []
        
        def make_request():
            with patch('triangulator.pointset_manager', mock_pm):
                response = client.get('/triangulation/test-id')
                results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        assert all(code in [200, 503] for code in results)
    
    def test_workflow_with_empty_pointset(self, client):
        """Test: Workflow avec PointSet vide."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = []
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/empty-id')
            
            assert response.status_code in [400, 500]
    
    def test_workflow_with_align_points(self, client):
        """Test: Workflow avec points alignés."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = [
            (0.0, 0.0),
            (1.0, 0.0),
            (2.0, 0.0)
        ]
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/collinear-id')
            
            assert response.status_code in [200, 400]
    
    def test_workflow_large_dataset(self, client, large_pointset_1000):
        """Test: Workflow avec grand dataset."""
        mock_pm = Mock()
        mock_pm.get_pointset.return_value = large_pointset_1000
        
        with patch('triangulator.pointset_manager', mock_pm):
            response = client.get('/triangulation/large-id')
            
            assert response.status_code == 200
            assert len(response.data) > 0
