from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     BooleanField, SubmitField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(message='Benutzername ist erforderlich.')])
    password = PasswordField('Passwort', validators=[DataRequired(message='Passwort ist erforderlich.')])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')


class TwoFactorForm(FlaskForm):
    token = StringField('2FA Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verifizieren')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Aktuelles Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[
        DataRequired(), Length(min=8, message='Passwort muss mindestens 8 Zeichen lang sein.')])
    confirm_password = PasswordField('Passwort bestätigen', validators=[
        DataRequired(), EqualTo('new_password', message='Passwörter stimmen nicht überein.')])
    submit = SubmitField('Passwort ändern')


class DozentForm(FlaskForm):
    titel = SelectField('Titel', choices=[('', '– Kein Titel –'), ('Prof.', 'Prof.'), ('Dr.', 'Dr.')],
                         validators=[Optional()])
    status = SelectField('Status', choices=[('intern', 'Intern'), ('extern', 'Extern')],
                          validators=[DataRequired()])
    nachname = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    vorname = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    zweiter_vorname = StringField('Zweiter Vorname', validators=[Optional(), Length(max=100)])
    email = StringField('E-Mail-Adresse', validators=[DataRequired(), Email(message='Ungültige E-Mail-Adresse.')])
    telefon = StringField('Telefonnummer', validators=[DataRequired(), Length(max=50)])
    praeferenz = SelectField('Vorlesungspräferenz', choices=[
        ('A', 'Alle Vorlesungen (A)'),
        ('M', 'Nur Master (M)'),
        ('B', 'Nur Bachelor (B)')
    ], validators=[DataRequired()])
    master_prioritaet = SelectField('Master-Priorität', choices=[
        ('', '– Keine –'), ('1', 'Priorität 1'), ('2', 'Priorität 2')
    ], validators=[Optional()], coerce=str)
    bachelor_prioritaet = SelectField('Bachelor-Priorität', choices=[
        ('', '– Keine –'), ('1', 'Priorität 1'), ('2', 'Priorität 2')
    ], validators=[Optional()], coerce=str)
    notizen = TextAreaField('Notizen', validators=[Optional()])
    submit = SubmitField('Speichern')


class VorlesungForm(FlaskForm):
    name = StringField('Name der Vorlesung', validators=[DataRequired(), Length(max=200)])
    status = SelectField('Status', choices=[('offen', 'Offen'), ('geschlossen', 'Geschlossen')],
                          validators=[DataRequired()])
    niveau = SelectField('Niveau', choices=[('Bachelor', 'Bachelor'), ('Master', 'Master')],
                          validators=[DataRequired()])
    semester = StringField('Semester', validators=[Optional(), Length(max=20)],
                           description='z.B. WS2025/26, SS2026')
    submit = SubmitField('Speichern')


class ZuweisungForm(FlaskForm):
    dozent_id = SelectField('Dozent', coerce=int, validators=[DataRequired()])
    vorlesung_id = SelectField('Vorlesung', coerce=int, validators=[DataRequired()])
    qualifikation = SelectField('Qualifikation', choices=[
        ('S', 'Sofort ohne Vorlauf (S)'),
        ('4', '4 Wochen Vorlaufzeit (4)'),
        ('M', 'Mehr als 4 Wochen Vorlaufzeit (M)')
    ], validators=[DataRequired()])
    erfahrung = SelectField('Erfahrung', choices=[
        ('P', 'An der Provadis gehalten (P)'),
        ('A', 'An anderer Hochschule gehalten (A)'),
        ('N', 'Noch nie gehalten (N)')
    ], validators=[DataRequired()])
    niveau_praeferenz = SelectField('Niveau-Präferenz (pro Vorlesung)', choices=[
        ('', '– Keine Einschränkung –'),
        ('M', 'Nur im Master'),
        ('B', 'Nur im Bachelor')
    ], validators=[Optional()])
    notizen = TextAreaField('Notizen', validators=[Optional()])
    submit = SubmitField('Speichern')


class SucheVorlesungForm(FlaskForm):
    vorlesung_id = SelectField('Vorlesung', coerce=int, validators=[DataRequired()])
    niveau = SelectField('Niveau', choices=[
        ('', '– Alle –'), ('Bachelor', 'Bachelor'), ('Master', 'Master')
    ], validators=[Optional()])
    qualifikation = SelectField('Verfügbarkeit', choices=[
        ('', '– Alle –'),
        ('S', 'Sofort verfügbar'),
        ('4', 'Innerhalb von 4 Wochen'),
        ('M', 'Mehr als 4 Wochen')
    ], validators=[Optional()])
    erfahrung = SelectField('Erfahrung', choices=[
        ('', '– Alle –'),
        ('P', 'An der Provadis gehalten'),
        ('A', 'An anderer Hochschule gehalten'),
        ('N', 'Noch nie gehalten')
    ], validators=[Optional()])
    submit = SubmitField('Suchen')


class SucheDozentForm(FlaskForm):
    dozent_id = SelectField('Dozent', coerce=int, validators=[DataRequired()])
    niveau = SelectField('Niveau', choices=[
        ('', '– Alle –'), ('Bachelor', 'Bachelor'), ('Master', 'Master')
    ], validators=[Optional()])
    qualifikation = SelectField('Verfügbarkeit', choices=[
        ('', '– Alle –'),
        ('S', 'Sofort verfügbar'),
        ('4', 'Innerhalb von 4 Wochen'),
        ('M', 'Mehr als 4 Wochen')
    ], validators=[Optional()])
    erfahrung = SelectField('Erfahrung', choices=[
        ('', '– Alle –'),
        ('P', 'An der Provadis gehalten'),
        ('A', 'An anderer Hochschule gehalten'),
        ('N', 'Noch nie gehalten')
    ], validators=[Optional()])
    submit = SubmitField('Suchen')


class UserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=80)])
    display_name = StringField('Anzeigename', validators=[Optional(), Length(max=120)])
    password = PasswordField('Passwort', validators=[Optional(), Length(min=8)])
    role = SelectField('Rolle', choices=[
        ('admin', 'Administrator'),
        ('editor', 'Bearbeiter'),
        ('viewer', 'Betrachter')
    ], validators=[DataRequired()])
    submit = SubmitField('Speichern')

