# Suis Tes Dépenses

Une application web de gestion des dépenses personnelles développée avec Flask.

## Fonctionnalités

- Inscription et connexion des utilisateurs
- Ajout de dépenses avec catégories
- Visualisation du total des dépenses
- Historique détaillé des dépenses
- Interface responsive et moderne

## Technologies utilisées

- Backend : Python avec Flask
- Frontend : HTML, CSS, JavaScript
- Base de données : SQLite avec SQLAlchemy
- Framework CSS : Bootstrap 5
- Authentification : Flask-Login

## Installation

1. Cloner le projet
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l'application :
   ```bash
   python app.py
   ```
4. Ouvrir un navigateur et accéder à : `http://localhost:5000`

## Structure du projet

```
Suis Tes Dépenses/
├── app.py              # Application principale Flask
├── requirements.txt    # Dépendances Python
├── static/            
│   └── css/
│       └── style.css   # Styles personnalisés
└── templates/          # Templates HTML
    ├── base.html       # Template de base
    ├── index.html      # Page d'accueil
    ├── login.html      # Page de connexion
    ├── register.html   # Page d'inscription
    ├── dashboard.html  # Tableau de bord
    └── ajouter_depense.html  # Formulaire d'ajout de dépense
```

## Sécurité

- Mots de passe hashés avec Werkzeug
- Protection CSRF sur les formulaires
- Sessions sécurisées avec Flask-Login

## Contribution

Ce projet a été développé dans le cadre d'un mémoire de 3e année. Pour toute suggestion d'amélioration, n'hésitez pas à créer une issue ou une pull request.
