from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='admin')  # Vorbereitet für Rollen: admin, editor, viewer
    totp_secret = db.Column(db.String(32), nullable=True)
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Dozent(db.Model):
    __tablename__ = 'dozenten'

    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(10), nullable=True, default='')  # Prof., Dr., oder leer
    status = db.Column(db.String(10), nullable=False, default='extern')  # intern oder extern
    nachname = db.Column(db.String(100), nullable=False)
    vorname = db.Column(db.String(100), nullable=False)
    zweiter_vorname = db.Column(db.String(100), nullable=True, default='')
    email = db.Column(db.String(200), nullable=False, unique=True)
    telefon = db.Column(db.String(50), nullable=False)
    # Vorlieben: M = nur Master, B = nur Bachelor, A = Alle
    praeferenz = db.Column(db.String(1), nullable=False, default='A')
    # Prioritäten (1 = höchste Prio)
    master_prioritaet = db.Column(db.Integer, nullable=True)
    bachelor_prioritaet = db.Column(db.Integer, nullable=True)
    notizen = db.Column(db.Text, nullable=True, default='')
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    aktualisiert_am = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vorlesungen = db.relationship('DozentVorlesung', back_populates='dozent', cascade='all, delete-orphan')

    @property
    def full_name(self):
        parts = []
        if self.titel:
            parts.append(self.titel)
        parts.append(self.vorname)
        if self.zweiter_vorname:
            parts.append(self.zweiter_vorname)
        parts.append(self.nachname)
        return ' '.join(parts)

    @property
    def praeferenz_display(self):
        mapping = {'M': 'Nur Master', 'B': 'Nur Bachelor', 'A': 'Alle'}
        return mapping.get(self.praeferenz, 'Alle')

    @property
    def status_display(self):
        return 'Intern' if self.status == 'intern' else 'Extern'


class Vorlesung(db.Model):
    __tablename__ = 'vorlesungen'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(15), nullable=False, default='offen')  # offen oder geschlossen
    niveau = db.Column(db.String(10), nullable=False, default='Bachelor')  # Bachelor oder Master
    semester = db.Column(db.String(20), nullable=True, default='')
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    aktualisiert_am = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dozenten = db.relationship('DozentVorlesung', back_populates='vorlesung', cascade='all, delete-orphan')

    @property
    def niveau_badge(self):
        if self.niveau == 'Master':
            return 'bg-purple'
        return 'bg-primary'

    @property
    def status_badge(self):
        if self.status == 'offen':
            return 'bg-success'
        return 'bg-secondary'


class DozentVorlesung(db.Model):
    __tablename__ = 'dozent_vorlesung'

    id = db.Column(db.Integer, primary_key=True)
    dozent_id = db.Column(db.Integer, db.ForeignKey('dozenten.id'), nullable=False)
    vorlesung_id = db.Column(db.Integer, db.ForeignKey('vorlesungen.id'), nullable=False)
    # Qualifikation: S = Sofort, 4 = 4 Wochen Vorlauf, M = Mehr als 4 Wochen
    qualifikation = db.Column(db.String(1), nullable=False, default='S')
    # Erfahrung: P = Provadis, A = Andere Hochschule, N = Nein
    erfahrung = db.Column(db.String(1), nullable=False, default='N')
    # Niveau-Präferenz pro Vorlesung (nur relevant wenn Dozent.praeferenz == 'A')
    # M = Master, B = Bachelor, None = keine Einschränkung
    niveau_praeferenz = db.Column(db.String(1), nullable=True)
    notizen = db.Column(db.Text, nullable=True, default='')

    dozent = db.relationship('Dozent', back_populates='vorlesungen')
    vorlesung = db.relationship('Vorlesung', back_populates='dozenten')

    __table_args__ = (
        db.UniqueConstraint('dozent_id', 'vorlesung_id', name='uq_dozent_vorlesung'),
    )

    @property
    def qualifikation_display(self):
        mapping = {'S': 'Sofort', '4': '4 Wochen Vorlauf', 'M': 'Mehr als 4 Wochen'}
        return mapping.get(self.qualifikation, 'Unbekannt')

    @property
    def qualifikation_badge(self):
        mapping = {'S': 'bg-success', '4': 'bg-warning text-dark', 'M': 'bg-danger'}
        return mapping.get(self.qualifikation, 'bg-secondary')

    @property
    def erfahrung_display(self):
        mapping = {'P': 'Provadis', 'A': 'Andere Hochschule', 'N': 'Keine'}
        return mapping.get(self.erfahrung, 'Unbekannt')

    @property
    def erfahrung_badge(self):
        mapping = {'P': 'bg-success', 'A': 'bg-info', 'N': 'bg-secondary'}
        return mapping.get(self.erfahrung, 'bg-secondary')

