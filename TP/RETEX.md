
# Projet Triangulator

  

## 1. Détail des Tests

### 1.1 Tests Unitaires (24 tests)

Répartis entre `TestsUnitaires.py` et `TestsAutres.py`.

* Validation algorithmique (triangles nominaux, carrés, rejet doublons).

* Validation binaire (conversion bit-à-bit, en-têtes).

* Validation mathématique (NaN, Inf, grands nombres).

  

### 1.2 Tests API et Routes (11 tests)

* Codes HTTP (200, 201, 400, 404).

  

### 1.3 Robustesse et Sécurité (19 tests)

*  **Robustesse :** Résilience aux données corrompues et pannes de services tiers.

*  **Sécurité :** Protection contre les attaques.

  

### 1.4 Intégration et Système (16 tests)

Validation du workflow complet avec mocks.

  

### 1.5 Performance (4 tests + Benchmark)

* Temps de réponse triangulaire.

* Monitoring mémoire .

Tout les tests passent, toutes les commandes make aussi. On a un coverage de 93% et la documentation peut etre générée.



---

  

## 2. Retour d'Expérience 

  

### 2.1 Ce que j'ai bien fait (Réussites)

*  **Approche "Test First" Stratégique :** J'ai commencé par définir les cas limites (points alignés, NaN) avant même de coder la logique. Cela a permis d'avoir un composant robuste dès la première version.

*  **Sécurité:** Au lieu d'attendre des failles, j'ai intégré des tests de sécurité (Injection SQL dans les IDs, DoS) dès le plan de test.

*  **Automatisation (Makefile) :** La mise en place immédiate d'un `Makefile` a standardisé les commandes. Et `make test` est un gain de temps énorme.

  

### 2.2 Ce que j'ai mal fait / Difficultés rencontrées

*  **Estimation Volumétrique :** J'avais annoncé 91 tests dans le plan initial, au final j'ai fini avec un  nombre final de tests à 78. Mais cela fait partie du Test Driven Developement. 
* 
*  **Ecriture du code après les tests :**  Ca peut etre compliqué au debut d'implementer le code apres le code mais au bout d'un moment on s'y fait et ça se fait facilement.

  

### 2.3 Ce que je ferais autrement avec le recul

*  **Structure de Projet :** Je passerrai peut etre plus de temps sur la structure du projet avant de commencer a ecrire les tests. Cela pour avoir une base sure sans avoir a modifier des tests apres.


  

---

  

## 3. Critique du Plan Initial (`PLAN.md`)

  

### 3.1 En quoi le plan était BON

*  **Découpage Clair :** La séparation Unitaires / Intégration / Performance a permis de travailler sur les blocs indépendamment sans confusion.

*  **Exhaustivité Fonctionnelle :** Le plan a bien identifié les cas mathématiques critiques (colinéarité, précision flottante) qui sont le cœur du Triangulator.

  

### 3.2 En quoi le plan était MAUVAIS / Incomplet

*  **Manque de Technique :** Il était très "fonctionnel" ("Vérifier que ça marche") mais manquait de détails techniques sur *comment* tester les edge cases bizarres.

 
---

  

## 4. Conclusion

Ce projet a démontré que les tests sont très importants dans un projet. Que commencer par ceux si est possible mais demande une organisation differente. J'avais deja fait du Test-Oriented developement l'année dernière mais c'etais tres théorique et peux pratique. Ca a été interessant de faire un projet avec cette organisation complètement en pratique. 