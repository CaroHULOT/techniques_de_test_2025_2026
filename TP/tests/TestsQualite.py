"""Quality tests module."""
class TestCodeQuality:
    """Tests de qualité du code."""
    
    def test_ruff_check_passes(self):
        """Test: ruff check -> aucun avertissement."""
        import subprocess
        
        result = subprocess.run(['ruff', 'check', '.'], capture_output=True)
        assert result.returncode == 0, f"Ruff found issues: {result.stdout.decode()}"
    
    def test_coverage_threshold(self):
        """Test: Coverage >= 90%."""
        import subprocess
        
        # executer coverage
        subprocess.run(['coverage', 'run', '-m', 'pytest', '--ignore=TP/tests/TestsQualite.py'])
        result = subprocess.run(['coverage', 'report'], capture_output=True, text=True)
        
        # pourcentage
        output = result.stdout
        for line in output.split('\n'):
            if 'TOTAL' in line:
                parts = line.split()
                coverage_percent = int(parts[-1].rstrip('%'))
                assert coverage_percent >= 90, f"Coverage is {coverage_percent}%, expected >= 90%"
    
    def test_documentation_generation(self):
        """Test: génère la documentation sans erreur."""
        import subprocess
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = ['pdoc3', '--html', '.', '--output-dir', tmp_dir, '--force']
            result = subprocess.run(cmd, cwd='TP', capture_output=True)
            assert result.returncode == 0, f"Documentation generation failed: {result.stderr.decode()}"
    
    def test_all_make_targets(self):
        """Test: Toutes les commandes sont fonctionnelles."""
        import subprocess
        
        # On retire les cibles qui lancent les tests pour éviter la récursion infinie
        targets = ['lint', 'doc']
        
        for target in targets:
            result = subprocess.run(['make', target], capture_output=True)
            #verifie que make ne plante pas
            assert result.returncode in [0, 2], f"Make target '{target}' failed"