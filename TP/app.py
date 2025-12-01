"""Application Flask pour le service Triangulator.

Ce module implémente un service REST qui expose trois endpoints principaux:

1. **POST /pointset**: Enregistre un nouveau PointSet et retourne un ID unique
2. **GET /pointset/{id}**: Récupère un PointSet enregistré
3. **GET /triangulation/{id}**: Calcule et retourne la triangulation d'un PointSet

Architecture:
    - L'application utilise un stockage en mémoire (stub) pour les PointSets.
    - La triangulation est calculée via le module 'triangulator'.
    - Les données sont échangées en format binaire optimisé via 'binary_format'.

Codes de réponse HTTP:
    - 200 OK: Requête réussie
    - 201 Created: PointSet enregistré avec succès
    - 400 Bad Request: Format invalide ou données manquantes
    - 404 Not Found: PointSet non trouvé
    - 500 Internal Server Error: Erreur serveur

Exemple d'utilisation::

    from app import app, pointset_store
    from binary_format import pointset_to_binary
    
    client = app.test_client()
    
    # Enregistrer un PointSet
    points = [(0, 0), (1, 0), (0.5, 1)]
    binary = pointset_to_binary(points)
    resp = client.post('/pointset', data=binary)
    pointset_id = resp.get_json()['pointSetId']
    
    # Calculer la triangulation
    resp = client.get(f'/triangulation/{pointset_id}')
    # resp.data contient la triangulation en binaire

Sécurité:
    - Validation des IDs pour éviter l'accès à des fichiers (path traversal).
    - Gestion explicite des erreurs pour éviter les fuites d'information.
"""

from flask import Flask, request, jsonify
import uuid

try:
    from binary_format import pointset_to_binary, binary_to_pointset, triangles_to_binary, binary_to_triangles
    from triangulator import triangulate
except ImportError:
    from .binary_format import pointset_to_binary, binary_to_pointset, triangles_to_binary, binary_to_triangles
    from .triangulator import triangulate

app = Flask(__name__)
"""Flask: Application Flask pour le service Triangulator."""

pointset_store = {}
"""dict: Stockage en mémoire des PointSets (clé: ID, valeur: données binaires)."""


@app.route('/triangulation/<pointset_id>', methods=['GET'])
def get_triangulation(pointset_id):
    """Calcule et retourne la triangulation d'un PointSet.
    
    Récupère un PointSet par son ID, calcule sa triangulation de Delaunay,
    et retourne le résultat encodé en format binaire.
    
    Args:
        pointset_id (str): Identifiant unique du PointSet (UUID).
    
    Returns:
        bytes: Données binaires contenant le PointSet original et ses triangles.
    
    Response Codes:
        - 200 OK: Triangulation calculée avec succès
        - 400 Bad Request: ID invalide ou format PointSet invalide
        - 404 Not Found: PointSet avec cet ID n'existe pas
        - 500 Internal Server Error: Erreur lors du calcul
    """
    try:
        if not pointset_id or pointset_id.startswith("../"):
            return jsonify({"error": "Invalid ID"}), 400
        
        if pointset_id not in pointset_store:
            return jsonify({"error": "Not found"}), 404
        
        binary_pointset = pointset_store[pointset_id]
        points = binary_to_pointset(binary_pointset)
        triangles = triangulate(points)
        result_binary = triangles_to_binary(points, triangles)
        
        return app.response_class(response=result_binary, status=200, mimetype='application/octet-stream')
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@app.route('/pointset', methods=['POST'])
def store_pointset():
    """Enregistre un nouveau PointSet et retourne son ID unique.
    
    Reçoit les données binaires d'un PointSet, les valide et les stocke
    en associant un identifiant unique UUID.
    
    Request:
        - Content-Type: application/octet-stream
        - Body: données binaires au format PointSet
    
    Returns:
        dict: JSON avec le champ 'pointSetId' (UUID généré)
    
    Response Codes:
        - 201 Created: PointSet enregistré avec succès
        - 400 Bad Request: Données vides ou format invalide
        - 500 Internal Server Error: Erreur serveur
    """
    try:
        binary_data = request.get_data()
        
        if not binary_data or len(binary_data) == 0:
            return jsonify({"error": "Empty body"}), 400
        
        points = binary_to_pointset(binary_data)
        pointset_id = str(uuid.uuid4())
        pointset_store[pointset_id] = binary_data
        
        return jsonify({"pointSetId": pointset_id}), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@app.route('/pointset/<pointset_id>', methods=['GET'])
def get_pointset(pointset_id):
    """Récupère un PointSet enregistré par son ID.
    
    Retourne les données binaires du PointSet stocké.
    
    Args:
        pointset_id (str): Identifiant unique du PointSet (UUID).
    
    Returns:
        bytes: Données binaires au format PointSet
    
    Response Codes:
        - 200 OK: PointSet récupéré avec succès
        - 400 Bad Request: ID invalide
        - 404 Not Found: PointSet avec cet ID n'existe pas
        - 500 Internal Server Error: Erreur serveur
    """
    try:
        if not pointset_id or pointset_id.startswith("../"):
            return jsonify({"error": "Invalid ID"}), 400
        
        if pointset_id not in pointset_store:
            return jsonify({"error": "Not found"}), 404
        
        binary_data = pointset_store[pointset_id]
        return app.response_class(response=binary_data, status=200, mimetype='application/octet-stream')
    
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
