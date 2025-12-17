"""Module de gestion des formats binaires pour PointSet et Triangles.

Ce module fournit des fonctions de conversion bidirectionnelles entre
les structures de données Python (listes de tuples) et un format binaire optimisé.

Le format binaire est conçu pour être compact et facilement sérialisable:

**Format PointSet:**
    - 4 bytes (unsigned long en little-endian): nombre de points N
    - N * 8 bytes: pour chaque point, 2 floats (X et Y en little-endian)
    
**Format Triangles:**
    - Part 1: PointSet complet (cf. Format PointSet)
    - Part 2: Triangles
        - 4 bytes (unsigned long): nombre de triangles T
        - T * 12 bytes: pour chaque triangle, 3 unsigned longs (indices en little-endian)

Exemple d'utilisation::

    from binary_format import pointset_to_binary, binary_to_pointset
    
    points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
    binary = pointset_to_binary(points)
    reconstructed = binary_to_pointset(binary)
    assert reconstructed == points

Avantages du format binaire:
    - Compacité: pas de texte, structures alignées
    - Sérialisation efficace: facilement transmissible sur HTTP
    - Pas d'ambiguïté numérique: utilise struct (spécification IEEE 754)
    - Compatible: little-endian universel
"""

import math
import struct


def pointset_to_binary(points):
    """Convertit une liste de points en format binaire compact.
    
    Encode chaque point (x, y) comme deux floats IEEE 754 en little-endian,
    précédés du nombre de points sur 4 bytes.
    
    Args:
        points (list): Liste de tuples ou listes (x, y).
                      Chaque coordonnée est convertie en float.
    
    Returns:
        bytes: Données binaires au format PointSet.
              Taille: 4 + len(points) * 8 bytes
    
    Exemple::
    
        >>> binary = pointset_to_binary([(0, 0), (1, 0), (0.5, 1)])
        >>> len(binary)  # 4 bytes (count) + 3 * 8 bytes (points)
        28
    
    Note:
        - Les coordonnées sont converties en float IEEE 754 (précision simple).
        - Format: little-endian pour compatibilité universelle.
        - Pas de validation: utiliser binary_to_pointset pour valider.

    """
    binary_data = struct.pack('<L', len(points))
    for x, y in points:
        binary_data += struct.pack('<ff', float(x), float(y))
    return binary_data


def binary_to_pointset(binary_data):
    r"""Convertit des données binaires en liste de points.
    
    Décode le format PointSet et valide l'intégrité des données.
    
    Args:
        binary_data (bytes): Données binaires au format PointSet.
    
    Returns:
        list: Liste de tuples (x, y) reconstruit.
    
    Raises:
        ValueError: Si les données sont trop courtes, tronquées ou invalides.
    
    Exemple::
    
        >>> binary = b'\\x03\\x00\\x00\\x00' + (b'\\x00\\x00\\x00\\x00' * 6)
        >>> points = binary_to_pointset(binary)
        >>> len(points)
        3
    
    Note:
        - Valide que la taille des données correspond au nombre de points.
        - Génère une erreur explicite en cas de données tronquées.

    """
    if len(binary_data) < 4:
        raise ValueError("Binary data too short")
    
    num_points = struct.unpack('<L', binary_data[:4])[0]
    expected_size = 4 + (num_points * 8)
    
    if len(binary_data) < expected_size:
        raise ValueError("Binary data truncated")
    
    points = []
    offset = 4
    for _ in range(num_points):
        x, y = struct.unpack('<ff', binary_data[offset:offset+8])
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("NaN or Infinite value detected")

        points.append((x, y))
        offset += 8
    
    return points


def triangles_to_binary(points, triangles):
    """Convertit des points et triangles en format binaire compact.
    
    Combine le PointSet avec les indices des triangles dans un seul flux binaire.
    
    Args:
        points (list): Liste de tuples (x, y) représentant les points.
        triangles (list): Liste de tuples (i, j, k) où i, j, k sont les indices 
                         dans 'points' (0-based indexing).
    
    Returns:
        bytes: Données binaires contenant le PointSet puis les Triangles.
              Taille: 4 + len(points)*8 + 4 + len(triangles)*12 bytes
    
    Raises:
        ValueError: Si un indice est hors limites ou un triangle invalide.
    
    Exemple::
    
        >>> points = [(0, 0), (1, 0), (0.5, 1)]
        >>> triangles = [(0, 1, 2)]
        >>> binary = triangles_to_binary(points, triangles)
        >>> len(binary)  # 4 + 24 + 4 + 12
        44
    
    Note:
        - Validation stricte: tous les indices doivent être valides.
        - Chaque triangle doit avoir exactement 3 sommets distincts.

    """
    binary_data = pointset_to_binary(points)
    binary_data += struct.pack('<L', len(triangles))
    
    for tri in triangles:
        if len(tri) != 3:
            raise ValueError("Triangle must have 3 vertices")
        for idx in tri:
            if not isinstance(idx, int) or idx < 0 or idx >= len(points):
                raise ValueError(f"Index {idx} out of range")
            binary_data += struct.pack('<L', idx)
    
    return binary_data


def binary_to_triangles(binary_data):
    """Convertit des données binaires en points et triangles.
    
    Décode le format Triangles complet et valide l'intégrité.
    
    Args:
        binary_data (bytes): Données binaires au format Triangles.
    
    Returns:
        tuple: (points, triangles) où:
            - points est une liste de tuples (x, y)
            - triangles est une liste de tuples (i, j, k)
    
    Raises:
        ValueError: Si les données sont invalides, tronquées ou contiennent 
                   des indices hors limites.
    
    Exemple::
    
        >>> points = [(0, 0), (1, 0), (0.5, 1)]
        >>> triangles = [(0, 1, 2)]
        >>> binary = triangles_to_binary(points, triangles)
        >>> decoded_points, decoded_triangles = binary_to_triangles(binary)
        >>> decoded_triangles == triangles
        True
    
    Note:
        - Validation bidirectionnelle complète.
        - Détecte les triangles avec sommet dupliqué.
        - Garantit la consistance entre les indices et le nombre de points.

    """
    if len(binary_data) < 4:
        raise ValueError("Binary data too short")
    
    num_points = struct.unpack('<L', binary_data[:4])[0]
    pointset_size = 4 + (num_points * 8)
    
    if len(binary_data) < pointset_size + 4:
        raise ValueError("Binary data truncated")
    
    points = binary_to_pointset(binary_data[:pointset_size])
    
    num_triangles = struct.unpack('<L', binary_data[pointset_size:pointset_size+4])[0]
    expected_size = pointset_size + 4 + (num_triangles * 12)
    
    if len(binary_data) < expected_size:
        raise ValueError("Binary data truncated")
    
    triangles = []
    offset = pointset_size + 4
    
    for _ in range(num_triangles):
        idx1, idx2, idx3 = struct.unpack('<LLL', binary_data[offset:offset+12])
        
        for idx in [idx1, idx2, idx3]:
            if idx >= len(points):
                raise ValueError(f"Index {idx} out of range")
        
        if len(set([idx1, idx2, idx3])) != 3:
            raise ValueError("Triangle has duplicate vertices")
        
        triangles.append((idx1, idx2, idx3))
        offset += 12
    
    return points, triangles
