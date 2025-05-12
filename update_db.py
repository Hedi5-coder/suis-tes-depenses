from app import app, db, User, Depense
from datetime import datetime
from sqlalchemy import text

# Créer le contexte d'application
with app.app_context():
    # Supprimer la base de données existante
    db.drop_all()
    
    # Créer la nouvelle base de données avec tous les champs
    db.create_all()

    # Mettre à jour les utilisateurs existants avec des valeurs par défaut
    users = User.query.all()
    for user in users:
        if not hasattr(user, 'email'):
            user.email = f"{user.username}@example.com"  # Email temporaire
        if not hasattr(user, 'seuil_alerte'):
            user.seuil_alerte = 10000
        if not hasattr(user, 'jours_inactivite'):
            user.jours_inactivite = 7
        if not hasattr(user, 'derniere_depense'):
            derniere_depense = user.depenses.order_by(Depense.date.desc()).first()
            user.derniere_depense = derniere_depense.date if derniere_depense else datetime.utcnow()

    db.session.commit()

    print("Base de données mise à jour avec succès !")

    # Ajout de la colonne budget_mensuel
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE user ADD COLUMN budget_mensuel FLOAT DEFAULT 0'))
            print('Colonne budget_mensuel ajoutée avec succès')
        except Exception as e:
            if 'duplicate column name' in str(e).lower():
                print('La colonne budget_mensuel existe déjà')
            else:
                print(f'Erreur : {e}')
