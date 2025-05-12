from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from sqlalchemy import func
from collections import defaultdict
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os
import time
from dotenv import load_dotenv
from flask_babel import Babel, gettext as _, get_locale

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clef_secrete'
# Configuration MySQL avec les paramètres par défaut de XAMPP
# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://root:@localhost/suis_tes_depenses')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.jinja_env.globals.update(min=min)

# Filtre personnalisé pour formater les dates
@app.template_filter('format_date')
def format_date(date):
    return date.strftime('%d/%m/%Y à %H:%M')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modèle Utilisateur
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    budget_mensuel = db.Column(db.Float, default=0)
    avatar_style = db.Column(db.Integer, default=0)
    devise = db.Column(db.String(10), default='FCFA')
    depenses = db.relationship('Depense', backref='user', lazy=True)

class Activite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('activites', lazy=True))

def enregistrer_activite(user_id, type_activite, description):
    activite = Activite(user_id=user_id, type=type_activite, description=description)
    db.session.add(activite)
    db.session.commit()

def enregistrer_activite(user_id, type_activite, description):
    activite = Activite(user_id=user_id, type=type_activite, description=description)
    db.session.add(activite)
    db.session.commit()

# Modèle Dépense
class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    categorie = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/supprimer_utilisateur/<email>')
def supprimer_utilisateur(email):
    user = User.query.filter_by(username=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return 'Utilisateur supprimé'
    return 'Utilisateur non trouvé'

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        budget_mensuel = float(request.form.get('budget_mensuel', 0))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Ce nom d\'utilisateur existe déjà.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            budget_mensuel=budget_mensuel
        )
        db.session.add(new_user)
        db.session.commit()

        enregistrer_activite(new_user.id, 'Inscription', f'Création du compte {username}')
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Identifiants invalides')
    return render_template('login.html')

@app.route('/exporter_csv')
@login_required
def exporter_csv():
    depenses = Depense.query.filter_by(user_id=current_user.id).all()
    
    # Créer un DataFrame pandas
    data = {
        'Date': [d.date.strftime('%d/%m/%Y') for d in depenses],
        'Catégorie': [d.categorie for d in depenses],
        'Description': [d.description for d in depenses],
        'Montant': [d.montant for d in depenses]
    }
    df = pd.DataFrame(data)
    
    # Créer un buffer pour le fichier CSV
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='depenses.csv'
    )

@app.route('/exporter_pdf')
@login_required
def exporter_pdf():
    depenses = Depense.query.filter_by(user_id=current_user.id).all()
    
    # Créer un buffer pour le PDF
    buffer = BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Ajouter un titre
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Rapport des dépenses - {current_user.username}", styles['Title']))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    
    # Créer le tableau des dépenses
    data = [["Date", "Catégorie", "Description", "Montant (FCFA)"]]
    for d in depenses:
        data.append([
            d.date.strftime('%d/%m/%Y'),
            d.categorie,
            d.description,
            f"{d.montant:,.2f}"
        ])
    
    # Style du tableau
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Ajouter le total
    total = sum(d.montant for d in depenses)
    elements.append(Paragraph(f"\nTotal des dépenses : {total:,.2f} FCFA", styles['Heading2']))
    
    # Générer le PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='rapport_depenses.pdf'
    )

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Identifiants invalides')
    return render_template('login.html')

def get_donnees_categories():
    # Récupérer le total par catégorie
    resultats = db.session.query(
        Depense.categorie,
        func.sum(Depense.montant).label('total')
    ).filter_by(user_id=current_user.id)\
     .group_by(Depense.categorie)\
     .all()
    
    return {cat: float(total) for cat, total in resultats}

def get_donnees_temporelles():
    # Date de début pour les statistiques (30 derniers jours)
    date_debut = datetime.now() - timedelta(days=30)
    
    # Récupérer toutes les dépenses des 30 derniers jours
    depenses = Depense.query\
        .filter(Depense.user_id == current_user.id)\
        .filter(Depense.date >= date_debut)\
        .order_by(Depense.date)\
        .all()
    
    # Préparer les données par semaine et par mois
    donnees_semaine = defaultdict(float)
    donnees_mois = defaultdict(float)
    
    for depense in depenses:
        # Format semaine : '2025-W20'
        semaine = depense.date.strftime('%Y-W%W')
        donnees_semaine[semaine] += depense.montant
        
        # Format mois : 'Mai 2025'
        mois = depense.date.strftime('%B %Y')
        donnees_mois[mois] += depense.montant
    
    # Trier et formater les données
    return {
        'semaine': {
            'labels': list(donnees_semaine.keys()),
            'montants': list(donnees_semaine.values())
        },
        'mois': {
            'labels': list(donnees_mois.keys()),
            'montants': list(donnees_mois.values())
        }
    }

def analyser_depenses(depenses, user):
    if not depenses:
        return []
    
    suggestions = []
    mois_actuel = datetime.now().strftime('%Y-%m')
    
    # 1. Analyse des tendances mensuelles par catégorie
    categories = {}
    for depense in depenses:
        mois = depense.date.strftime('%Y-%m')
        if mois not in categories:
            categories[mois] = {}
        if depense.categorie not in categories[mois]:
            categories[mois][depense.categorie] = 0
        categories[mois][depense.categorie] += depense.montant

    # Calculer les moyennes et tendances
    moyennes = {}
    tendances = {}
    for categorie in set(sum([list(m.keys()) for m in categories.values()], [])):
        montants = [month.get(categorie, 0) for month in categories.values()]
        moyennes[categorie] = sum(montants) / len(categories)
        
        # Détecter les tendances sur les 3 derniers mois
        if len(montants) >= 3:
            tendance = sum(montants[-3:]) / 3 - moyennes[categorie]
            tendances[categorie] = tendance

    # 2. Générer des conseils personnalisés
    if mois_actuel in categories:
        # Alertes de dépassement
        for categorie, montant in categories[mois_actuel].items():
            if categorie in moyennes:
                if montant > moyennes[categorie] * 1.5:
                    suggestions.append({
                        'type': 'alerte',
                        'message': f"Vos dépenses en {categorie} ({montant:.2f}€) dépassent largement votre moyenne habituelle ({moyennes[categorie]:.2f}€).",
                        'conseil': get_conseil_reduction(categorie)
                    })

        # Analyse des tendances
        for categorie, tendance in tendances.items():
            if tendance > moyennes[categorie] * 0.2:  # Augmentation de 20%
                suggestions.append({
                    'type': 'tendance',
                    'message': f"Vos dépenses en {categorie} augmentent progressivement ces derniers mois.",
                    'conseil': get_conseil_reduction(categorie)
                })

    # 3. Conseils budgétaires généraux
    if user.budget_mensuel:
        total_mois = sum(categories.get(mois_actuel, {}).values())
        if total_mois > user.budget_mensuel * 0.8:
            jours_restants = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - datetime.now()
            suggestions.append({
                'type': 'budget',
                'message': f"Il vous reste {jours_restants.days} jours ce mois-ci et vous avez déjà utilisé {(total_mois/user.budget_mensuel*100):.1f}% de votre budget.",
                'conseil': "Essayez de limiter les dépenses non essentielles pour le reste du mois."
            })

    # 4. Recommandations d'économies
    cat_principales = sorted(moyennes.items(), key=lambda x: x[1], reverse=True)[:3]
    if cat_principales:
        suggestions.append({
            'type': 'economie',
            'message': f"Vos principales dépenses sont en {', '.join(cat[0] for cat in cat_principales)}.",
            'conseil': "Concentrez vos efforts d'économie sur ces catégories pour un impact maximal."
        })

    return suggestions

def get_conseil_reduction(categorie):
    conseils = {
        'Alimentation': "Essayez de planifier vos repas à l'avance et de faire une liste de courses pour éviter les achats impulsifs.",
        'Transport': "Pensez aux options de transport en commun ou au covoiturage pour réduire vos frais.",
        'Logement': "Vérifiez vos factures d'énergie et identifiez les possibilités d'économies.",
        'Loisirs': "Recherchez des activités gratuites ou à prix réduit dans votre région.",
        'Santé': "Vérifiez si tous vos soins sont bien pris en charge par votre mutuelle.",
        'Shopping': "Attendez les périodes de soldes et comparez les prix avant d'acheter.",
        'Factures': "Analysez vos abonnements et résiliez ceux que vous utilisez peu.",
        'Autre': "Essayez de catégoriser plus précisément vos dépenses pour mieux les suivre."
    }
    return conseils.get(categorie, "Examinez en détail cette catégorie pour identifier des pistes d'économies.")

@app.route('/dashboard')
@login_required
def dashboard():
    sort_by = request.args.get('sort', 'date')
    periode = request.args.get('periode', '')
    date_debut = request.args.get('date_debut', '')
    date_fin = request.args.get('date_fin', '')
    
    # Créer la requête de base
    query = Depense.query.filter_by(user_id=current_user.id)
    
    # Appliquer les filtres de date
    if periode:
        today = datetime.now().date()
        if periode == 'semaine':
            date_debut = today - timedelta(days=today.weekday())
            date_fin = date_debut + timedelta(days=6)
        elif periode == 'mois':
            date_debut = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            date_fin = next_month - timedelta(days=next_month.day)
        elif periode == 'annee':
            date_debut = today.replace(month=1, day=1)
            date_fin = today.replace(month=12, day=31)
    else:
        # Utiliser les dates personnalisées si fournies
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Appliquer les filtres de date à la requête
    if date_debut:
        query = query.filter(Depense.date >= date_debut)
    if date_fin:
        query = query.filter(Depense.date <= date_fin)
    
    # Appliquer le tri
    if sort_by == 'date':
        depenses = query.order_by(Depense.date.desc()).all()
    else:
        depenses = query.order_by(Depense.categorie).all()
    
    total = sum(d.montant for d in depenses)
    
    # Récupérer les données pour les graphiques
    donnees_categories = get_donnees_categories()
    donnees_temporelles = get_donnees_temporelles()
    
    # Formater les dates pour l'affichage
    date_debut_str = date_debut.strftime('%Y-%m-%d') if isinstance(date_debut, date) else ''
    date_fin_str = date_fin.strftime('%Y-%m-%d') if isinstance(date_fin, date) else ''
    
    # Calculer le total des dépenses du mois en cours
    debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mois = (debut_mois + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    depenses_mois = Depense.query.filter(
        Depense.user_id == current_user.id,
        Depense.date >= debut_mois,
        Depense.date <= fin_mois
    ).all()
    total_mois = sum(d.montant for d in depenses_mois)
    
    # Calculer le pourcentage du budget utilisé
    pourcentage_budget = 0
    if current_user.budget_mensuel > 0:
        pourcentage_budget = (total_mois / current_user.budget_mensuel) * 100
    
    # Analyser les dépenses pour générer des suggestions
    suggestions = analyser_depenses(depenses, current_user)

    return render_template('dashboard.html', 
        depenses=depenses,
        total=total,
        total_mois=total_mois,
        username=current_user.username,
        sort_by=sort_by,
        periode=periode,
        date_debut=date_debut_str,
        date_fin=date_fin_str,
        donnees_categories=donnees_categories,
        donnees_temporelles=donnees_temporelles,
        budget_mensuel=current_user.budget_mensuel,
        pourcentage_budget=pourcentage_budget,
        suggestions=suggestions
    )

@app.route('/ajouter_depense', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        montant = float(request.form.get('montant'))
        devise_entree = request.form.get('devise')
        categorie = request.form.get('categorie')
        description = request.form.get('description')
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d')

        # Définir les taux de conversion vers FCFA
        taux = {
            'FCFA': 1,
            'EUR': 655.957,  # 1 EUR = 655.957 FCFA
            'USD': 600,      # 1 USD = 600 FCFA
            'GBP': 750       # 1 GBP = 750 FCFA
        }

        # Convertir le montant en FCFA
        if devise_entree == 'FCFA':
            montant_fcfa = montant
        else:
            # Si la devise n'est pas FCFA, convertir en FCFA
            montant_fcfa = round(montant * taux[devise_entree], 2)

        depense = Depense(
            montant=montant_fcfa,  # Stocker en FCFA
            categorie=categorie,
            description=description,
            date=date,
            user_id=current_user.id
        )

        db.session.add(depense)
        db.session.commit()

        enregistrer_activite(current_user.id, 'Dépense', f'Ajout d\'une dépense de {montant} {devise_entree} pour {categorie}')
        flash('Dépense ajoutée avec succès !', 'success')
        return redirect(url_for('dashboard'))

    date_aujourdhui = datetime.now().strftime('%Y-%m-%d')
    return render_template('ajouter_depense.html', date_default=date_aujourdhui)

@app.route('/modifier_depense/<int:depense_id>', methods=['GET', 'POST'])
@login_required
def modifier_depense(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    if depense.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        depense.montant = float(request.form.get('montant'))
        depense.categorie = request.form.get('categorie')
        depense.description = request.form.get('description')
        db.session.commit()
        enregistrer_activite(current_user.id, 'Dépense', f'Modification de la dépense {depense.montant} FCFA pour {depense.categorie}')
        flash('Dépense modifiée avec succès')
        return redirect(url_for('dashboard'))
    
    return render_template('modifier_depense.html', depense=depense)

@app.route('/supprimer_depense/<int:depense_id>')
@login_required
def supprimer_depense(depense_id):
    depense = Depense.query.get_or_404(depense_id)
    if depense.user_id == current_user.id:
        montant = depense.montant
        categorie = depense.categorie
        db.session.delete(depense)
        db.session.commit()
        enregistrer_activite(current_user.id, 'Dépense', f'Suppression de la dépense {montant} FCFA pour {categorie}')
        flash('Dépense supprimée avec succès')
    return redirect(url_for('dashboard'))

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        if 'devise' in request.form:
            current_user.devise = request.form['devise']
            db.session.commit()
            flash('Devise mise à jour avec succès')

        if 'budget_mensuel' in request.form:
            try:
                budget = float(request.form['budget_mensuel'])
                current_user.budget_mensuel = budget
                db.session.commit()
                flash('Budget mensuel mis à jour avec succès')
            except ValueError:
                flash('Veuillez entrer un montant valide pour le budget', 'error')

        return redirect(url_for('profil'))

    # Récupérer les 10 dernières activités
    activites = Activite.query.filter_by(user_id=current_user.id)\
        .order_by(Activite.date.desc())\
        .limit(10)\
        .all()

    devises = {
        'FCFA': 'Franc CFA',
        'EUR': 'Euro',
        'USD': 'Dollar US',
        'GBP': 'Livre Sterling'
    }

    return render_template('profil.html', activites=activites, devises=devises)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    avatar_choice = request.form.get('avatar_choice')

    if username != current_user.username:
        # Vérifier si le nom d'utilisateur est déjà pris
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return redirect(url_for('profil'))
        
        current_user.username = username
        enregistrer_activite(current_user.id, 'Profil', 'Modification du nom d\'utilisateur')

    if avatar_choice is not None:
        # Mettre à jour le style de l'avatar
        avatar_style = int(avatar_choice)
        if current_user.avatar_style != avatar_style:
            current_user.avatar_style = avatar_style
            enregistrer_activite(current_user.id, 'Profil', 'Modification du style de l\'avatar')

    db.session.commit()
    flash('Profil mis à jour avec succès !', 'success')
    return redirect(url_for('profil'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
