import io
import json
import csv
from datetime import datetime

from flask import (Flask, render_template, redirect, url_for, flash, request,
                   jsonify, send_file, session, abort)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import pyotp
import qrcode
import base64

from config import Config
from models import db, User, Dozent, Vorlesung, DozentVorlesung
from forms import (LoginForm, TwoFactorForm, ChangePasswordForm, DozentForm,
                   VorlesungForm, ZuweisungForm, SucheVorlesungForm, SucheDozentForm)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    csrf = CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Bitte melden Sie sich an.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ──────────────────────── Context Processors ────────────────────────

    @app.context_processor
    def inject_globals():
        return dict(
            app_name=app.config['APP_NAME'],
            hochschule=app.config['HOCHSCHULE_NAME'],
            now=datetime.utcnow()
        )

    # ──────────────────────── Auth Routes ────────────────────────

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                if user.is_2fa_enabled:
                    session['2fa_user_id'] = user.id
                    session['2fa_remember'] = form.remember_me.data
                    return redirect(url_for('verify_2fa'))
                login_user(user, remember=form.remember_me.data)
                flash('Erfolgreich angemeldet.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            flash('Ungültige Anmeldedaten.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/verify-2fa', methods=['GET', 'POST'])
    def verify_2fa():
        if '2fa_user_id' not in session:
            return redirect(url_for('login'))
        form = TwoFactorForm()
        if form.validate_on_submit():
            user = db.session.get(User, session['2fa_user_id'])
            if user and pyotp.TOTP(user.totp_secret).verify(form.token.data):
                login_user(user, remember=session.get('2fa_remember', False))
                session.pop('2fa_user_id', None)
                session.pop('2fa_remember', None)
                flash('Erfolgreich angemeldet.', 'success')
                return redirect(url_for('dashboard'))
            flash('Ungültiger 2FA-Code.', 'danger')
        return render_template('verify_2fa.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Sie wurden abgemeldet.', 'info')
        return redirect(url_for('login'))

    @app.route('/profil', methods=['GET', 'POST'])
    @login_required
    def profil():
        pw_form = ChangePasswordForm()
        if pw_form.validate_on_submit():
            if current_user.check_password(pw_form.current_password.data):
                current_user.set_password(pw_form.new_password.data)
                db.session.commit()
                flash('Passwort erfolgreich geändert.', 'success')
                return redirect(url_for('profil'))
            else:
                flash('Aktuelles Passwort ist falsch.', 'danger')
        return render_template('profil.html', pw_form=pw_form)

    @app.route('/setup-2fa', methods=['GET', 'POST'])
    @login_required
    def setup_2fa():
        if not current_user.totp_secret:
            current_user.totp_secret = pyotp.random_base32()
            db.session.commit()
        totp = pyotp.TOTP(current_user.totp_secret)
        uri = totp.provisioning_uri(name=current_user.username, issuer_name='Provadis Dozentenverwaltung')
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        form = TwoFactorForm()
        if form.validate_on_submit():
            if totp.verify(form.token.data):
                current_user.is_2fa_enabled = True
                db.session.commit()
                flash('2FA erfolgreich aktiviert!', 'success')
                return redirect(url_for('profil'))
            else:
                flash('Ungültiger Code. Bitte versuchen Sie es erneut.', 'danger')

        return render_template('setup_2fa.html', form=form, qr_b64=qr_b64, secret=current_user.totp_secret)

    @app.route('/disable-2fa', methods=['POST'])
    @login_required
    def disable_2fa():
        current_user.is_2fa_enabled = False
        current_user.totp_secret = None
        db.session.commit()
        flash('2FA wurde deaktiviert.', 'info')
        return redirect(url_for('profil'))

    # ──────────────────────── Dashboard ────────────────────────

    @app.route('/')
    @login_required
    def dashboard():
        dozenten_count = Dozent.query.count()
        vorlesungen_count = Vorlesung.query.count()
        offene_vorlesungen = Vorlesung.query.filter_by(status='offen').count()
        zuweisungen_count = DozentVorlesung.query.count()
        interne = Dozent.query.filter_by(status='intern').count()
        externe = Dozent.query.filter_by(status='extern').count()
        bachelor_count = Vorlesung.query.filter_by(niveau='Bachelor').count()
        master_count = Vorlesung.query.filter_by(niveau='Master').count()

        # Vorlesungen ohne Dozent
        vorlesungen_ohne_dozent = Vorlesung.query.filter(~Vorlesung.dozenten.any()).count()

        # Letzte 5 Dozenten
        letzte_dozenten = Dozent.query.order_by(Dozent.erstellt_am.desc()).limit(5).all()
        letzte_vorlesungen = Vorlesung.query.order_by(Vorlesung.erstellt_am.desc()).limit(5).all()

        return render_template('dashboard.html',
                               dozenten_count=dozenten_count,
                               vorlesungen_count=vorlesungen_count,
                               offene_vorlesungen=offene_vorlesungen,
                               zuweisungen_count=zuweisungen_count,
                               interne=interne, externe=externe,
                               bachelor_count=bachelor_count,
                               master_count=master_count,
                               vorlesungen_ohne_dozent=vorlesungen_ohne_dozent,
                               letzte_dozenten=letzte_dozenten,
                               letzte_vorlesungen=letzte_vorlesungen)

    # ──────────────────────── Dozenten ────────────────────────

    @app.route('/dozenten')
    @login_required
    def dozenten_liste():
        status_filter = request.args.get('status', '')
        praeferenz_filter = request.args.get('praeferenz', '')
        suche = request.args.get('q', '')

        query = Dozent.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if praeferenz_filter:
            query = query.filter_by(praeferenz=praeferenz_filter)
        if suche:
            query = query.filter(
                db.or_(
                    Dozent.nachname.ilike(f'%{suche}%'),
                    Dozent.vorname.ilike(f'%{suche}%'),
                    Dozent.email.ilike(f'%{suche}%')
                )
            )
        dozenten = query.order_by(Dozent.nachname, Dozent.vorname).all()
        return render_template('dozenten/liste.html', dozenten=dozenten,
                               status_filter=status_filter,
                               praeferenz_filter=praeferenz_filter,
                               suche=suche)

    @app.route('/dozenten/neu', methods=['GET', 'POST'])
    @login_required
    def dozent_neu():
        form = DozentForm()
        if form.validate_on_submit():
            dozent = Dozent(
                titel=form.titel.data or '',
                status=form.status.data,
                nachname=form.nachname.data,
                vorname=form.vorname.data,
                zweiter_vorname=form.zweiter_vorname.data or '',
                email=form.email.data,
                telefon=form.telefon.data,
                praeferenz=form.praeferenz.data,
                master_prioritaet=int(form.master_prioritaet.data) if form.master_prioritaet.data else None,
                bachelor_prioritaet=int(form.bachelor_prioritaet.data) if form.bachelor_prioritaet.data else None,
                notizen=form.notizen.data or ''
            )
            db.session.add(dozent)
            try:
                db.session.commit()
                flash(f'Dozent {dozent.full_name} wurde erfolgreich angelegt.', 'success')
                return redirect(url_for('dozent_detail', id=dozent.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Fehler beim Anlegen: {str(e)}', 'danger')
        return render_template('dozenten/form.html', form=form, titel='Neuen Dozenten anlegen', edit=False)

    @app.route('/dozenten/<int:id>')
    @login_required
    def dozent_detail(id):
        dozent = db.session.get(Dozent, id) or abort(404)
        zuweisungen = DozentVorlesung.query.filter_by(dozent_id=id).all()
        return render_template('dozenten/detail.html', dozent=dozent, zuweisungen=zuweisungen)

    @app.route('/dozenten/<int:id>/bearbeiten', methods=['GET', 'POST'])
    @login_required
    def dozent_bearbeiten(id):
        dozent = db.session.get(Dozent, id) or abort(404)
        form = DozentForm(obj=dozent)
        if request.method == 'GET':
            form.master_prioritaet.data = str(dozent.master_prioritaet) if dozent.master_prioritaet else ''
            form.bachelor_prioritaet.data = str(dozent.bachelor_prioritaet) if dozent.bachelor_prioritaet else ''
        if form.validate_on_submit():
            dozent.titel = form.titel.data or ''
            dozent.status = form.status.data
            dozent.nachname = form.nachname.data
            dozent.vorname = form.vorname.data
            dozent.zweiter_vorname = form.zweiter_vorname.data or ''
            dozent.email = form.email.data
            dozent.telefon = form.telefon.data
            dozent.praeferenz = form.praeferenz.data
            dozent.master_prioritaet = int(form.master_prioritaet.data) if form.master_prioritaet.data else None
            dozent.bachelor_prioritaet = int(form.bachelor_prioritaet.data) if form.bachelor_prioritaet.data else None
            dozent.notizen = form.notizen.data or ''
            try:
                db.session.commit()
                flash(f'Dozent {dozent.full_name} wurde aktualisiert.', 'success')
                return redirect(url_for('dozent_detail', id=dozent.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Fehler: {str(e)}', 'danger')
        return render_template('dozenten/form.html', form=form, titel='Dozent bearbeiten', edit=True, dozent=dozent)

    @app.route('/dozenten/<int:id>/loeschen', methods=['POST'])
    @login_required
    def dozent_loeschen(id):
        dozent = db.session.get(Dozent, id) or abort(404)
        name = dozent.full_name
        db.session.delete(dozent)
        db.session.commit()
        flash(f'Dozent {name} wurde gelöscht.', 'success')
        return redirect(url_for('dozenten_liste'))

    # ──────────────────────── Vorlesungen ────────────────────────

    @app.route('/vorlesungen')
    @login_required
    def vorlesungen_liste():
        status_filter = request.args.get('status', '')
        niveau_filter = request.args.get('niveau', '')
        suche = request.args.get('q', '')

        query = Vorlesung.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if niveau_filter:
            query = query.filter_by(niveau=niveau_filter)
        if suche:
            query = query.filter(Vorlesung.name.ilike(f'%{suche}%'))
        vorlesungen = query.order_by(Vorlesung.name).all()
        return render_template('vorlesungen/liste.html', vorlesungen=vorlesungen,
                               status_filter=status_filter, niveau_filter=niveau_filter, suche=suche)

    @app.route('/vorlesungen/neu', methods=['GET', 'POST'])
    @login_required
    def vorlesung_neu():
        form = VorlesungForm()
        if form.validate_on_submit():
            vorlesung = Vorlesung(
                name=form.name.data,
                status=form.status.data,
                niveau=form.niveau.data,
                semester=form.semester.data or ''
            )
            db.session.add(vorlesung)
            try:
                db.session.commit()
                flash(f'Vorlesung "{vorlesung.name}" wurde angelegt.', 'success')
                return redirect(url_for('vorlesung_detail', id=vorlesung.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Fehler: {str(e)}', 'danger')
        return render_template('vorlesungen/form.html', form=form, titel='Neue Vorlesung anlegen', edit=False)

    @app.route('/vorlesungen/<int:id>')
    @login_required
    def vorlesung_detail(id):
        vorlesung = db.session.get(Vorlesung, id) or abort(404)
        zuweisungen = DozentVorlesung.query.filter_by(vorlesung_id=id).all()
        return render_template('vorlesungen/detail.html', vorlesung=vorlesung, zuweisungen=zuweisungen)

    @app.route('/vorlesungen/<int:id>/bearbeiten', methods=['GET', 'POST'])
    @login_required
    def vorlesung_bearbeiten(id):
        vorlesung = db.session.get(Vorlesung, id) or abort(404)
        form = VorlesungForm(obj=vorlesung)
        if form.validate_on_submit():
            vorlesung.name = form.name.data
            vorlesung.status = form.status.data
            vorlesung.niveau = form.niveau.data
            vorlesung.semester = form.semester.data or ''
            try:
                db.session.commit()
                flash(f'Vorlesung "{vorlesung.name}" wurde aktualisiert.', 'success')
                return redirect(url_for('vorlesung_detail', id=vorlesung.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Fehler: {str(e)}', 'danger')
        return render_template('vorlesungen/form.html', form=form, titel='Vorlesung bearbeiten',
                               edit=True, vorlesung=vorlesung)

    @app.route('/vorlesungen/<int:id>/loeschen', methods=['POST'])
    @login_required
    def vorlesung_loeschen(id):
        vorlesung = db.session.get(Vorlesung, id) or abort(404)
        name = vorlesung.name
        db.session.delete(vorlesung)
        db.session.commit()
        flash(f'Vorlesung "{name}" wurde gelöscht.', 'success')
        return redirect(url_for('vorlesungen_liste'))

    # ──────────────────────── Zuweisungen ────────────────────────

    @app.route('/zuweisungen/neu', methods=['GET', 'POST'])
    @login_required
    def zuweisung_neu():
        form = ZuweisungForm()
        dozenten = Dozent.query.order_by(Dozent.nachname, Dozent.vorname).all()
        vorlesungen = Vorlesung.query.order_by(Vorlesung.name).all()
        form.dozent_id.choices = [(d.id, d.full_name) for d in dozenten]
        form.vorlesung_id.choices = [(v.id, f'{v.name} ({v.niveau})') for v in vorlesungen]

        # Pre-fill from query params
        if request.method == 'GET':
            if request.args.get('dozent_id'):
                form.dozent_id.data = int(request.args.get('dozent_id'))
            if request.args.get('vorlesung_id'):
                form.vorlesung_id.data = int(request.args.get('vorlesung_id'))

        if form.validate_on_submit():
            existing = DozentVorlesung.query.filter_by(
                dozent_id=form.dozent_id.data,
                vorlesung_id=form.vorlesung_id.data
            ).first()
            if existing:
                flash('Diese Zuweisung existiert bereits.', 'warning')
            else:
                zuweisung = DozentVorlesung(
                    dozent_id=form.dozent_id.data,
                    vorlesung_id=form.vorlesung_id.data,
                    qualifikation=form.qualifikation.data,
                    erfahrung=form.erfahrung.data,
                    niveau_praeferenz=form.niveau_praeferenz.data or None,
                    notizen=form.notizen.data or ''
                )
                db.session.add(zuweisung)
                db.session.commit()
                flash('Zuweisung wurde erfolgreich erstellt.', 'success')
                next_url = request.args.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('dozent_detail', id=zuweisung.dozent_id))
        return render_template('zuweisungen/form.html', form=form, titel='Neue Zuweisung', edit=False)

    @app.route('/zuweisungen/<int:id>/bearbeiten', methods=['GET', 'POST'])
    @login_required
    def zuweisung_bearbeiten(id):
        zuweisung = db.session.get(DozentVorlesung, id) or abort(404)
        form = ZuweisungForm(obj=zuweisung)
        dozenten = Dozent.query.order_by(Dozent.nachname, Dozent.vorname).all()
        vorlesungen = Vorlesung.query.order_by(Vorlesung.name).all()
        form.dozent_id.choices = [(d.id, d.full_name) for d in dozenten]
        form.vorlesung_id.choices = [(v.id, f'{v.name} ({v.niveau})') for v in vorlesungen]
        if form.validate_on_submit():
            zuweisung.dozent_id = form.dozent_id.data
            zuweisung.vorlesung_id = form.vorlesung_id.data
            zuweisung.qualifikation = form.qualifikation.data
            zuweisung.erfahrung = form.erfahrung.data
            zuweisung.niveau_praeferenz = form.niveau_praeferenz.data or None
            zuweisung.notizen = form.notizen.data or ''
            db.session.commit()
            flash('Zuweisung wurde aktualisiert.', 'success')
            return redirect(url_for('dozent_detail', id=zuweisung.dozent_id))
        return render_template('zuweisungen/form.html', form=form, titel='Zuweisung bearbeiten',
                               edit=True, zuweisung=zuweisung)

    @app.route('/zuweisungen/<int:id>/loeschen', methods=['POST'])
    @login_required
    def zuweisung_loeschen(id):
        zuweisung = db.session.get(DozentVorlesung, id) or abort(404)
        dozent_id = zuweisung.dozent_id
        db.session.delete(zuweisung)
        db.session.commit()
        flash('Zuweisung wurde gelöscht.', 'success')
        next_url = request.form.get('next') or url_for('dozent_detail', id=dozent_id)
        return redirect(next_url)

    # ──────────────────────── Suche ────────────────────────

    @app.route('/suche')
    @login_required
    def suche():
        return render_template('suche/index.html')

    @app.route('/suche/dozent-fuer-vorlesung', methods=['GET', 'POST'])
    @login_required
    def suche_dozent_fuer_vorlesung():
        form = SucheVorlesungForm()
        vorlesungen = Vorlesung.query.order_by(Vorlesung.name).all()
        form.vorlesung_id.choices = [(0, '– Vorlesung wählen –')] + [
            (v.id, f'{v.name} ({v.niveau})') for v in vorlesungen
        ]

        ergebnisse = None
        vorlesung = None

        if request.args.get('vorlesung_id'):
            form.vorlesung_id.data = int(request.args.get('vorlesung_id', 0))
            form.niveau.data = request.args.get('niveau', '')
            form.qualifikation.data = request.args.get('qualifikation', '')
            form.erfahrung.data = request.args.get('erfahrung', '')

            if form.vorlesung_id.data:
                vorlesung = db.session.get(Vorlesung, form.vorlesung_id.data)
                query = DozentVorlesung.query.filter_by(vorlesung_id=form.vorlesung_id.data)

                if form.qualifikation.data:
                    if form.qualifikation.data == 'S':
                        query = query.filter(DozentVorlesung.qualifikation == 'S')
                    elif form.qualifikation.data == '4':
                        query = query.filter(DozentVorlesung.qualifikation.in_(['S', '4']))
                    # 'M' shows all

                if form.erfahrung.data:
                    query = query.filter(DozentVorlesung.erfahrung == form.erfahrung.data)

                ergebnisse = query.all()

                # Filter by dozent preference and niveau
                if form.niveau.data:
                    filtered = []
                    for z in ergebnisse:
                        dozent = z.dozent
                        if dozent.praeferenz == 'A':
                            if z.niveau_praeferenz and z.niveau_praeferenz != form.niveau.data[0]:
                                continue
                            filtered.append(z)
                        elif dozent.praeferenz == form.niveau.data[0]:
                            filtered.append(z)
                        # Skip if dozent preference doesn't match
                    ergebnisse = filtered

                # Sort: Provadis first, then Sofort, then name
                def sort_key(z):
                    erfahrung_order = {'P': 0, 'A': 1, 'N': 2}
                    quali_order = {'S': 0, '4': 1, 'M': 2}
                    prio = 99
                    if vorlesung and vorlesung.niveau == 'Master' and z.dozent.master_prioritaet:
                        prio = z.dozent.master_prioritaet
                    elif vorlesung and vorlesung.niveau == 'Bachelor' and z.dozent.bachelor_prioritaet:
                        prio = z.dozent.bachelor_prioritaet
                    return (
                        erfahrung_order.get(z.erfahrung, 9),
                        quali_order.get(z.qualifikation, 9),
                        prio,
                        z.dozent.nachname
                    )

                ergebnisse = sorted(ergebnisse, key=sort_key)

        return render_template('suche/dozent_fuer_vorlesung.html',
                               form=form, ergebnisse=ergebnisse, vorlesung=vorlesung)

    @app.route('/suche/vorlesungen-fuer-dozent', methods=['GET', 'POST'])
    @login_required
    def suche_vorlesungen_fuer_dozent():
        form = SucheDozentForm()
        dozenten = Dozent.query.order_by(Dozent.nachname, Dozent.vorname).all()
        form.dozent_id.choices = [(0, '– Dozent wählen –')] + [
            (d.id, d.full_name) for d in dozenten
        ]

        ergebnisse = None
        dozent = None

        if request.args.get('dozent_id'):
            form.dozent_id.data = int(request.args.get('dozent_id', 0))
            form.niveau.data = request.args.get('niveau', '')
            form.qualifikation.data = request.args.get('qualifikation', '')
            form.erfahrung.data = request.args.get('erfahrung', '')

            if form.dozent_id.data:
                dozent = db.session.get(Dozent, form.dozent_id.data)
                query = DozentVorlesung.query.filter_by(dozent_id=form.dozent_id.data)

                if form.niveau.data:
                    query = query.join(Vorlesung).filter(Vorlesung.niveau == form.niveau.data)

                if form.qualifikation.data:
                    if form.qualifikation.data == 'S':
                        query = query.filter(DozentVorlesung.qualifikation == 'S')
                    elif form.qualifikation.data == '4':
                        query = query.filter(DozentVorlesung.qualifikation.in_(['S', '4']))

                if form.erfahrung.data:
                    query = query.filter(DozentVorlesung.erfahrung == form.erfahrung.data)

                ergebnisse = query.all()

        return render_template('suche/vorlesungen_fuer_dozent.html',
                               form=form, ergebnisse=ergebnisse, dozent=dozent)

    # ──────────────────────── Reports ────────────────────────

    REPORT_TITLES = {
        1: 'Dozenten mit Vorlesungen an der Provadis',
        2: 'Dozenten mit Vorlesungen (nie an der Provadis gehalten)',
        3: 'Vorlesungen ohne bekannten Dozenten',
        4: 'Vorlesungen nur mit Dozenten von anderen Hochschulen'
    }

    def get_report_data(report_id):
        if report_id == 1:
            # Alle Dozenten und Vorlesungen, die an der Provadis gehalten wurden
            zuweisungen = DozentVorlesung.query.filter_by(erfahrung='P').all()
            rows = []
            for z in zuweisungen:
                rows.append({
                    'dozent': z.dozent.full_name,
                    'status': z.dozent.status_display,
                    'vorlesung': z.vorlesung.name,
                    'niveau': z.vorlesung.niveau,
                    'qualifikation': z.qualifikation_display,
                    'semester': z.vorlesung.semester or '–'
                })
            headers = ['Dozent', 'Status', 'Vorlesung', 'Niveau', 'Qualifikation', 'Semester']
            keys = ['dozent', 'status', 'vorlesung', 'niveau', 'qualifikation', 'semester']
            return headers, keys, sorted(rows, key=lambda r: (r['dozent'], r['vorlesung']))

        elif report_id == 2:
            # Dozenten und Vorlesungen, die noch nie an der Provadis gehalten wurden
            zuweisungen = DozentVorlesung.query.filter(DozentVorlesung.erfahrung != 'P').all()
            rows = []
            for z in zuweisungen:
                rows.append({
                    'dozent': z.dozent.full_name,
                    'status': z.dozent.status_display,
                    'vorlesung': z.vorlesung.name,
                    'niveau': z.vorlesung.niveau,
                    'qualifikation': z.qualifikation_display,
                    'erfahrung': z.erfahrung_display,
                    'semester': z.vorlesung.semester or '–'
                })
            headers = ['Dozent', 'Status', 'Vorlesung', 'Niveau', 'Qualifikation', 'Erfahrung', 'Semester']
            keys = ['dozent', 'status', 'vorlesung', 'niveau', 'qualifikation', 'erfahrung', 'semester']
            return headers, keys, sorted(rows, key=lambda r: (r['dozent'], r['vorlesung']))

        elif report_id == 3:
            # Vorlesungen ohne Dozent
            vorlesungen = Vorlesung.query.filter(~Vorlesung.dozenten.any()).all()
            rows = []
            for v in vorlesungen:
                rows.append({
                    'vorlesung': v.name,
                    'niveau': v.niveau,
                    'status': 'Offen' if v.status == 'offen' else 'Geschlossen',
                    'semester': v.semester or '–'
                })
            headers = ['Vorlesung', 'Niveau', 'Status', 'Semester']
            keys = ['vorlesung', 'niveau', 'status', 'semester']
            return headers, keys, sorted(rows, key=lambda r: r['vorlesung'])

        elif report_id == 4:
            # Vorlesungen, für die es nur Dozenten gibt, die an anderen (nicht Provadis) Hochschulen gehalten haben
            vorlesungen = Vorlesung.query.filter(Vorlesung.dozenten.any()).all()
            rows = []
            for v in vorlesungen:
                has_provadis = any(z.erfahrung == 'P' for z in v.dozenten)
                has_andere = any(z.erfahrung == 'A' for z in v.dozenten)
                if not has_provadis and has_andere:
                    dozent_names = ', '.join(z.dozent.full_name for z in v.dozenten if z.erfahrung == 'A')
                    rows.append({
                        'vorlesung': v.name,
                        'niveau': v.niveau,
                        'status': 'Offen' if v.status == 'offen' else 'Geschlossen',
                        'dozenten': dozent_names,
                        'semester': v.semester or '–'
                    })
            headers = ['Vorlesung', 'Niveau', 'Status', 'Dozenten (andere HS)', 'Semester']
            keys = ['vorlesung', 'niveau', 'status', 'dozenten', 'semester']
            return headers, keys, sorted(rows, key=lambda r: r['vorlesung'])

        return [], [], []

    @app.route('/reports')
    @login_required
    def reports():
        return render_template('reports/index.html', report_titles=REPORT_TITLES)

    @app.route('/reports/<int:report_id>')
    @login_required
    def report_anzeigen(report_id):
        if report_id not in REPORT_TITLES:
            abort(404)
        headers, keys, rows = get_report_data(report_id)
        return render_template('reports/ergebnis.html',
                               report_id=report_id,
                               report_title=REPORT_TITLES[report_id],
                               headers=headers, keys=keys, rows=rows)

    @app.route('/api/export/<int:report_id>/<fmt>')
    @login_required
    def export_report(report_id, fmt):
        if report_id not in REPORT_TITLES:
            abort(404)
        headers, keys, rows = get_report_data(report_id)
        title = REPORT_TITLES[report_id]

        if fmt == 'json':
            return jsonify({
                'report': title,
                'erstellt_am': datetime.utcnow().isoformat(),
                'anzahl': len(rows),
                'daten': rows
            })

        elif fmt == 'csv':
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=keys, extrasaction='ignore')
            writer.writerow(dict(zip(keys, headers)))
            for row in rows:
                writer.writerow(row)
            mem = io.BytesIO()
            mem.write(output.getvalue().encode('utf-8-sig'))
            mem.seek(0)
            return send_file(mem, mimetype='text/csv',
                             as_attachment=True,
                             download_name=f'report_{report_id}_{datetime.now().strftime("%Y%m%d")}.csv')

        elif fmt == 'pdf':
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                                    topMargin=20 * mm, bottomMargin=15 * mm,
                                    leftMargin=15 * mm, rightMargin=15 * mm)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'],
                                          fontSize=16, textColor=colors.HexColor('#0c2f6f'),
                                          alignment=TA_CENTER, spaceAfter=12)
            elements.append(Paragraph(f'Provadis Hochschule – {title}', title_style))
            elements.append(Paragraph(
                f'Erstellt am: {datetime.now().strftime("%d.%m.%Y %H:%M")}',
                ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER, spaceAfter=20)
            ))

            # Table
            cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)
            header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9,
                                           leading=11, textColor=colors.white)

            table_data = [[Paragraph(h, header_style) for h in headers]]
            for row in rows:
                table_data.append([Paragraph(str(row.get(k, '')), cell_style) for k in keys])

            col_count = len(headers)
            available = landscape(A4)[0] - 30 * mm
            col_width = available / col_count

            t = Table(table_data, colWidths=[col_width] * col_count, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c2f6f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10 * mm))
            elements.append(Paragraph(f'Anzahl Einträge: {len(rows)}',
                                       ParagraphStyle('Footer', parent=styles['Normal'],
                                                      fontSize=8, textColor=colors.grey)))

            doc.build(elements)
            buf.seek(0)
            return send_file(buf, mimetype='application/pdf',
                             as_attachment=True,
                             download_name=f'report_{report_id}_{datetime.now().strftime("%Y%m%d")}.pdf')

        abort(400, 'Ungültiges Format. Erlaubt: json, csv, pdf')

    # ──────────────────────── Error Handlers ────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5050)




