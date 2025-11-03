# PLAN DE TEST — Projet Triangulator

## 1. Objectif du plan de test

L'objctif de ce plan est de detailler l'ensemble des tests prévus pour le composant `Triangulator`.
La demarche adoptée est **Test First** 


Le but est de valider et mesurer la fiabilité, la justesse, la performance et la qualité de l’implémentation, notamment :
- les **unités** (fonctions, formats binaires, etc.) ;
- les **intégrations** avec `PointSetManager`, `Client` et `Database` simulés ;
- les **API** exposées par `Triangulator`;
- la **performance** du système ;
- la **résistance aux erreurs et aux attaques** ;
- la **qualité et la documentation** du code.


## 1.1. Attention

Le projet ne concerne que le composant `Triangulator`. Tous les autres composants, tels que `PointSetManager` ou la base de données, ne seront pas implémentés.

Tous les tests d’intégration ou de flux complets utiliseront des composants simulés. Certains comportements, comme les interactions réseau réelles, ne peuvent donc pas être testés directement. L’objectif est de vérifier le fonctionnement correct du Triangulator.

---

## 2. Périmètre du test

Le périmètre inclut :
- le service **Triangulator** (API / logique / récupération / génération des triangles) ;
- les interactions avec `PointSetManager` et `Client` via mocks.

Ne sont pas testés :
- `PointSetManager` réel et sa base de données; 
- `Client` réel;

---

## 3. Types de tests prévus

| Type de test | Objectif principal |
|---------------|--------------------|
| **Tests unitaires** | Vérifier la justesse de chaque fonction, conversion binaire et algorithme de triangulation. |
| **Tests d’intégration simulé** | Vérifier la cohérence des endpoints. |
| **Tests de performance** | Mesurer le temps d’exécution, la charge et la scalabilité. |
| **Tests de robustesse** | Garantir un comportement maîtrisé face aux entrées invalides ou extrêmes. |
| **Tests de sécurité** | Vérifier la résistance aux entrées invalides ou malveillantes. |
| **Tests système** | Vérifier le fonctionnement complet du workflow. |
| **Tests qualité** | Vérifier le code, la documentation et la couverture. |

---

## 4. Environnement et outils

- **Langage :** Python 3.10+
- **Framework web :** Flask
- **Outils de test :**
  - `pytest` pour les tests unitaires et d’intégration
  - `coverage` pour mesurer la couverture
  - `ruff` pour la qualité du code
  - `pdoc3` pour la documentation

- **Commandes Make :**
  - `make test` : lance tous les tests
  - `make unit_test` : lance les tests sans ceux de performance
  - `make perf_test` : lance uniquement les tests de performance
  - `make coverage` : génère le rapport de couverture
  - `make lint` : vérifie la qualité du code
  - `make doc` : génère la documentation HTML

---

## 5. Plan détaillé des tests

### 5.1 Tests unitaires

**Objectif :** Valider les fonctions internes de calcul et de conversion binaire.

#### 5.1.1 Algorithme de triangulation

Cas de test :
-  3 points → 1 triangle correct.
-  4 points formant un carré → 2 triangles.
-  Points alignés → aucun triangle.
-  Points dupliqués → rejet ou fusion.
-  Format d’entrée invalide → exception gérée.
-  PointSet vide → renvoyer une erreur.
-  Points avec NaN ou inf → rejeter avec 400 Bad Request

#### 5.1.2 Tests sur les conversions binaires :
- `PointSet` → flux binaire conforme.
    - Ensemble de N points → 4 premiers bytes = N (unsigned long), puis N points × 8 bytes (float X + float Y)
    - Ensemble des points identiques a l'original.
- `Triangles` → flux binaire conforme.
    - Ensemble de triangles et sommets → Partie 1 = comme PointSet, Partie 2 = nombre de triangles (4 bytes) + 3 indices par triangle (4 bytes chacun)
    - Triangles identiques à l’original
- Vérification de la taille, du nombre de bytes et si il n'y a pas plusieurs fois le même sommet pour un triangle.

**Endpoints testés :**

- **GET /triangulation/{pointSetId}**
  -  Cas valide : envoi d’un `triangle` binaire correct → réponse `200` + `Triangles`.
  -  ID inexistant → `404`.
  -  ID mal formé → `400`.
  -  Triangulation échouée → `500`
  -  Service de stockage indisponible → `503`.

---

#### 5.1.3 Gestion des erreurs HTTP

- Vérifier les codes d’erreur (`400`, `404`, `500`, `503`) selon le scénario.
---

### 5.2 Tests d’intégration simulé

**Objectif :** Vérifier le bon échange entre microservices.

1. **Flux complet PointSetManager simulé**
   - POST → récupération d’un ID.
   - GET → récupération du même PointSet.
   - Vérification : les données récupérées sont identiques à l’entrée.

2. **Triangulator ↔ PointSetManager**
   - POST `/pointset` + POST `/triangulate` avec ID.
   - Résultat triangulé non vide.
   - Gestion d’erreurs :
     - ID inexistant → `400`.
     - Service PointSetManager indisponible → `502`.
     - Format invalide → `400`.
     - Timeout → `504`.

---

### 5.3 Tests de performance

**Objectif :** Évaluer le temps et la stabilité du système.

Cas testés :
- Triangulation d'un grand nombre de points.
- Requêtes répétées.

**Méthode :**
- Temps moyen d’exécution.
- requetes répétées
- Mesure mémoire.
- Tag `@pytest.mark.performance` pour exclusion via `make unit_test`.

---

### 5.4 Tests de robustesse

**Objectif :** Vérifier la résistance aux entrées invalides et aux pannes.

Cas testés :
- PointSet tronqué → `400`.
- Coordonnées non float → `400`.
- Service ou base injoignable → `503`.
- Résultat vide → message clair.
- Exceptions internes → `500`.
- Timeout → `504`.

---

### 5.6 Tests système 

**Objectif :** Vérifier le bon déroulement du workflow complet. Attention tout les composants non implementés seront simulés.

Étapes :
1. Le client envoie un `PointSet` au `PointSetManager`.
2. Le `PointSetManager` renvoie un `pointSetId`.
3. Le client demande la triangulation au `Triangulator`.
4. Le `Triangulator` contacte le `PointSetManager` pour récupérer les points.
5. Le `Triangulator` renvoie les triangles au client.

 Attendu : cohérence du flux, formats corrects, pas d’erreur inattendue.  
 Cas d’échec : service manquant → message d’erreur approprié.

---

### 5.5 Tests de sécurité

**Objectif :** Résister aux attaques simples.

Cas testés :
- ID trafiqué.
- Requêtes surdimensionnées (DoS simulé).

---

### 5.7 Tests qualité

**Objectif :** Garantir la propreté et la maintenabilité du code.

- `ruff check` : aucun avertissement.
- `coverage` : couverture > 90 %.
- `pdoc3` : documentation générée sans erreur.
- `make` : toutes les commandes fonctionnelles (`test`, `lint`, `doc`, etc.).

---

## 6. Conclusion

Ce plan de test couvre toutes les facettes de l’implémentation du`Triangulator` : algorithme, conversion binaire, API, robustesse, performance et sécurité, avec un environnement simulé pour les interactions externes.

---

