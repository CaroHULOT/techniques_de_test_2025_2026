#!/usr/bin/env python3
"""Script interactif pour tester le Triangulator avec vos propres valeurs."""

import sys

from Triangulator.binary_format import (
    binary_to_triangles,
    pointset_to_binary,
    triangles_to_binary,
)
from Triangulator.triangulator import triangulate


def print_menu():
    """Affiche le menu principal."""
    print("\n" + "=" * 70)
    print("🔷 TRIANGULATOR - Test Interactif".center(70))
    print("=" * 70)
    print("1. Entrer des points manuellement")
    print("2. Utiliser des exemples prédéfinis")
    print("3. Lancer le serveur Flask")
    print("4. Quitter")
    print("=" * 70)


def input_points_manually():
    """Demande à l'utilisateur d'entrer des points."""
    print("\n Entrez vos points (format: x y)")
    print("   Entrez au moins 3 points. Tapez 'done' quand terminé.\n")

    points = []
    counter = 1

    while True:
        user_input = input(f"Point {counter}: ").strip()

        if user_input.lower() == "done":
            if len(points) < 3:
                print(" Vous devez entrer au moins 3 points!")
                continue
            break

        try:
            x, y = map(float, user_input.split())
            points.append((x, y))
            counter += 1
            print(f"   ✓ Point ajouté: ({x}, {y})")
        except ValueError:
            print(" Format invalide. Tapez: x y (nombres séparés par un espace)")

    return points


def test_triangulation(points):
    """Teste la triangulation avec les points donnés."""
    print("\n" + "-" * 70)
    print(" RÉSULTATS DE LA TRIANGULATION")
    print("-" * 70)

    print(f"\n Points d'entrée ({len(points)}):")
    for i, (x, y) in enumerate(points):
        print(f"   {i}: ({x}, {y})")

    try:
        # Triangulation
        triangles = triangulate(points)

        print(f"\n🔺 Triangles ({len(triangles)}):")
        if triangles:
            for i, (a, b, c) in enumerate(triangles):
                p1 = points[a]
                p2 = points[b]
                p3 = points[c]
                print(f"   Triangle {i}: indices({a}, {b}, {c})")
                print(f"     → {p1} — {p2} — {p3}")
        else:
            print("   ℹ️  Aucun triangle (points colinéaires)")

    except Exception as e:
        print(f"\n Erreur: {e}")
        return

    # Format binaire
    print("\n Format binaire:")
    try:
        binary = pointset_to_binary(points)
        print(f"   PointSet size: {len(binary)} bytes")
        print(f"   Hex: {binary.hex()}")

        full_binary = triangles_to_binary(points, triangles)
        print(f"   Full (PointSet + Triangles): {len(full_binary)} bytes")

        # Vérifier le round-trip
        points_decoded, triangles_decoded = binary_to_triangles(full_binary)
        if points_decoded == points and triangles_decoded == triangles:
            print("   ✓ Round-trip (encode/decode) OK")
        else:
            print("     Round-trip mismatch")

    except Exception as e:
        print(f"    Erreur binaire: {e}")


def show_examples():
    """Affiche les exemples prédéfinis."""
    examples = {
        "1": {
            "name": "Triangle simple (3 points)",
            "points": [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)],
        },
        "2": {
            "name": "Carré (4 points)",
            "points": [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
        },
        "3": {
            "name": "Pentagone (5 points)",
            "points": [
                (0.0, 0.0),
                (2.0, 0.0),
                (2.5, 1.5),
                (1.0, 2.5),
                (-0.5, 1.5),
            ],
        },
        "4": {
            "name": "Points alignés (3 points colinéaires)",
            "points": [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
        },
        "5": {
            "name": "Cercle (8 points)",
            "points": [
                (1.0, 0.0),
                (0.707, 0.707),
                (0.0, 1.0),
                (-0.707, 0.707),
                (-1.0, 0.0),
                (-0.707, -0.707),
                (0.0, -1.0),
                (0.707, -0.707),
            ],
        },
    }

    print("\n" + "=" * 70)
    print("📋 EXEMPLES PRÉDÉFINIS")
    print("=" * 70)

    for key, example in examples.items():
        print(f"{key}. {example['name']}")

    choice = input("\nChoisissez un exemple (1-5): ").strip()

    if choice in examples:
        points = examples[choice]["points"]
        print(f"\n✓ Exemple sélectionné: {examples[choice]['name']}")
        test_triangulation(points)
    else:
        print(" Choix invalide")


def launch_flask_server():
    """Lance le serveur Flask."""
    print("\n" + "=" * 70)
    print(" LANCER LE SERVEUR FLASK")
    print("=" * 70)

    import subprocess

    print("\nLancement du serveur sur http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter.\n")

    try:
        subprocess.run(
            ["python3", "Triangulator/app.py"],
            cwd="/home/dockeruser/TechTest/techniques_de_test_2025_2026/TP",
        )
    except KeyboardInterrupt:
        print("\n\n✓ Serveur arrêté")


def main():
    """Boucle principale."""
    print("\n Bienvenue dans le Triangulator interactif!")

    while True:
        print_menu()
        choice = input("Votre choix: ").strip()

        if choice == "1":
            points = input_points_manually()
            test_triangulation(points)

        elif choice == "2":
            show_examples()

        elif choice == "3":
            launch_flask_server()

        elif choice == "4":
            print("\n Au revoir!\n")
            sys.exit(0)

        else:
            print(" Choix invalide")


if __name__ == "__main__":
    main()
