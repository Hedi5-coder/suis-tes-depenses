# Mémoire : Développement d'une Application Web de Gestion des Dépenses

## Introduction

Dans un contexte où la gestion financière personnelle devient de plus en plus importante, ce projet vise à développer une application web permettant aux utilisateurs de suivre et gérer leurs dépenses quotidiennes. Cette application, nommée "Suis Tes Dépenses", combine des technologies modernes du web pour offrir une solution pratique et accessible.

## 1. Analyse des Besoins et Objectifs

### 1.1 Objectifs du Projet
- Créer une interface utilisateur intuitive et responsive
- Permettre une gestion sécurisée des données personnelles
- Offrir des fonctionnalités essentielles de suivi des dépenses
- Assurer une expérience utilisateur fluide sur tous les appareils

### 1.2 Public Cible
- Particuliers souhaitant suivre leurs dépenses
- Utilisateurs de tous niveaux technologiques
- Personnes cherchant une solution simple et efficace

## 2. Architecture Technique

### 2.1 Stack Technologique
- **Backend** : Python avec Flask
  - Choix justifié par sa simplicité et sa flexibilité
  - Framework léger permettant un développement rapide
  - Grande communauté et documentation riche

- **Base de données** : SQLite avec SQLAlchemy
  - Base de données légère ne nécessitant pas de serveur
  - Parfaite pour les applications de petite à moyenne taille
  - ORM SQLAlchemy pour une abstraction efficace

- **Frontend** : HTML5, CSS3, JavaScript
  - Bootstrap 5 pour un design responsive
  - Interface moderne et professionnelle
  - Compatible avec tous les navigateurs modernes

### 2.2 Structure du Projet
```
Suis Tes Dépenses/
├── app.py              # Application principale
├── requirements.txt    # Dépendances
├── static/            
│   └── css/
│       └── style.css   # Styles personnalisés
└── templates/          # Templates HTML
    ├── base.html       # Template de base
    ├── index.html      # Page d'accueil
    └── ...
```

## 3. Implémentation

### 3.1 Base de Données
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(120))
    depenses = db.relationship('Depense', backref='user')

class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float)
    categorie = db.Column(db.String(50))
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

### 3.2 Sécurité
- **Authentification** :
  - Utilisation de Flask-Login pour la gestion des sessions
  - Hachage des mots de passe avec Werkzeug
  - Protection CSRF sur tous les formulaires

- **Protection des Données** :
  - Validation des entrées utilisateur
  - Échappement automatique des données dans les templates
  - Sessions sécurisées avec des tokens

### 3.3 Interface Utilisateur
- **Principes de Design** :
  - Hiérarchie visuelle claire
  - Palette de couleurs professionnelle
  - Typographie lisible
  - Espacement cohérent

- **Responsive Design** :
  - Adaptation automatique à la taille de l'écran
  - Navigation mobile optimisée
  - Images et tableaux responsives

## 4. Fonctionnalités Clés

### 4.1 Gestion des Utilisateurs
- Inscription sécurisée
- Connexion/Déconnexion
- Profil utilisateur

### 4.2 Gestion des Dépenses
- Ajout de nouvelles dépenses
- Catégorisation
- Historique détaillé
- Calcul des totaux

### 4.3 Visualisation des Données
- Tableau de bord intuitif
- Liste chronologique
- Filtrage par catégorie

## 5. Tests et Validation

### 5.1 Tests Unitaires
- Tests des modèles de données
- Tests des routes Flask
- Tests des formulaires

### 5.2 Tests d'Interface
- Validation sur différents navigateurs
- Tests de responsive design
- Tests d'accessibilité

## 6. Perspectives d'Évolution

### 6.1 Améliorations Possibles
- Ajout de graphiques statistiques
- Export des données
- Catégories personnalisables
- Budget prévisionnel

### 6.2 Scalabilité
- Migration vers une base de données plus robuste
- Optimisation des performances
- Architecture microservices

## Conclusion

Ce projet démontre la mise en œuvre réussie d'une application web moderne, combinant sécurité, facilité d'utilisation et professionnalisme. L'utilisation de technologies éprouvées comme Flask et SQLAlchemy, associée à une interface utilisateur soignée, permet de répondre efficacement aux besoins de gestion des dépenses personnelles.

## Bibliographie

1. Flask Documentation (https://flask.palletsprojects.com/)
2. SQLAlchemy Documentation (https://docs.sqlalchemy.org/)
3. Bootstrap Documentation (https://getbootstrap.com/docs/)
4. MDN Web Docs (https://developer.mozilla.org/)
