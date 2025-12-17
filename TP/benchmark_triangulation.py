"""Benchmark script for Triangulator."""
import os
import random
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Triangulator.triangulator import triangulate
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)

def generate_random_points(n):
    """Génére n points aléatoires."""
    return [(random.uniform(0, 10000), random.uniform(0, 10000)) for _ in range(n)]

def run_benchmark():
    """Benchmark avec different nombre de points."""
    sizes = [100, 1000, 5000, 10000, 50000, 100000]
    
    print("\n Benchmark Triangulator ")
    print("=" * 45)
    print(f"{'Points':<10} | {'Time (s)':<12} | {'Triangles':<10}")
    print("-" * 45)
    
    for n in sizes:
        print(f"Generating {n} points...", end='\r')
        points = generate_random_points(n)
        
        start_time = time.time()
        try:
            triangles = triangulate(points)
            end_time = time.time()
            duration = end_time - start_time
            print(f"{n:<10} | {duration:<12.4f} | {len(triangles):<10}")
        except Exception as e:
            print(f"{n:<10} | {'FAILED':<12} | {str(e)}")

    print("=" * 45)
    print("Benchmark terminé.\n")

if __name__ == "__main__":
    run_benchmark()
