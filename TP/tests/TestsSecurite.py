"""Security tests module."""
import struct

import pytest


class TestSecurity:
    """Tests de sécurité."""
    
    def test_tampered_id(self, client):
        """Test: ID trafiqué."""
        #exemple d'id trafiqués
        malicious_ids = [
            "../../../etc/passwd",
            "'; DROP TABLE pointsets; --",
            "<script>alert('xss')</script>",
            "id%00.txt"
        ]
        
        for malicious_id in malicious_ids:
            response = client.get(f'/triangulation/{malicious_id}')
            assert response.status_code in [400, 404]
    
    def test_oversized_request_dos(self, client):
        """Test: Requêtes surdimensionnées (DoS simulé)."""
        huge_data = b'\xFF' * (10 * 1024 * 1024)  # 10 MB
        
        response = client.post('/pointset', data=huge_data)
        # Devrait rejeter ou gérer gracieusement
        assert response.status_code in [400, 413, 405]
    
    def test_sql_injection_in_id(self, client):
        """Test: Injection SQL dans l'ID."""
        sql_injection = "1' OR '1'='1"
        
        response = client.get(f'/triangulation/{sql_injection}')
        assert response.status_code in [400, 404]
        
    def test_oversized_binary_pointset(self, client):
        """Test: PointSet trop volumineux."""
        # Prétendre avoir 1 million de points
        huge_header = b'\x00\x0c\x42\x6f' + b'\x00' * (1000 * 1000)
        
        response = client.post('/pointset', data=huge_header)
        assert response.status_code in [400, 413]
    
    def test_command_injection_in_pointset_data(self):
        """Test: Injection de commande dans données PointSet."""
        from Triangulator.binary_format import binary_to_pointset
        
        # Injecter des commandes shell
        shell_commands = b'; rm -rf / #'
        
        with pytest.raises((ValueError, struct.error)):
            binary_to_pointset(shell_commands)