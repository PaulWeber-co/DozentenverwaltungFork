"""Datenbank initialisieren und mit umfangreichen Beispieldaten befüllen."""
from app import create_app
from models import db, User, Dozent, Vorlesung, DozentVorlesung


def init_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('✓ Datenbank-Tabellen erstellt.')

        # ─── Benutzer ───
        admin = User(username='admin', display_name='Administrator', role='admin')
        admin.set_password('Provadis2026!')
        db.session.add(admin)

        viewer = User(username='viewer', display_name='Betrachter (Test)', role='viewer')
        viewer.set_password('Viewer2026!')
        db.session.add(viewer)
        print('✓ 2 Benutzer erstellt (admin / Provadis2026!  |  viewer / Viewer2026!)')

        # ─── Dozenten (20 Stück) ───
        dozenten_data = [
            # --- Interne Dozenten ---
            dict(titel='Prof.', status='intern', nachname='Müller', vorname='Thomas', zweiter_vorname='',
                 email='t.mueller@provadis.de', telefon='+49 69 305-1001', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=2,
                 notizen='Fachbereich Mathematik, seit 2015 an der Provadis.'),
            dict(titel='Dr.', status='intern', nachname='Schmidt', vorname='Anna', zweiter_vorname='Maria',
                 email='a.schmidt@provadis.de', telefon='+49 69 305-1002', praeferenz='M',
                 master_prioritaet=1, bachelor_prioritaet=None,
                 notizen='Spezialisierung Data Science & KI.'),
            dict(titel='Prof.', status='intern', nachname='Weber', vorname='Klaus', zweiter_vorname='',
                 email='k.weber@provadis.de', telefon='+49 69 305-1003', praeferenz='A',
                 master_prioritaet=2, bachelor_prioritaet=1,
                 notizen='Leiter des Fachbereichs Informatik.'),
            dict(titel='Prof.', status='intern', nachname='Wagner', vorname='Christine', zweiter_vorname='',
                 email='c.wagner@provadis.de', telefon='+49 69 305-1004', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=2,
                 notizen='Schwerpunkt Management und Organisation.'),
            dict(titel='Dr.', status='intern', nachname='Hoffmann', vorname='Laura', zweiter_vorname='',
                 email='l.hoffmann@provadis.de', telefon='+49 69 305-1005', praeferenz='M',
                 master_prioritaet=1, bachelor_prioritaet=None,
                 notizen='Forschungsschwerpunkt Machine Learning.'),
            dict(titel='Dr.', status='intern', nachname='Klein', vorname='Andreas', zweiter_vorname='',
                 email='a.klein@provadis.de', telefon='+49 69 305-1006', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=1,
                 notizen='Datenbanken und IT-Sicherheit.'),
            dict(titel='Prof.', status='intern', nachname='Wolf', vorname='Petra', zweiter_vorname='Elisabeth',
                 email='p.wolf@provadis.de', telefon='+49 69 305-1007', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=1,
                 notizen='Physik und angewandte Mathematik.'),
            dict(titel='Prof.', status='intern', nachname='Braun', vorname='Markus', zweiter_vorname='',
                 email='m.braun@provadis.de', telefon='+49 69 305-1008', praeferenz='B',
                 master_prioritaet=None, bachelor_prioritaet=1,
                 notizen='Grundlagenvorlesungen im Bachelor.'),
            dict(titel='Dr.', status='intern', nachname='Schwarz', vorname='Katharina', zweiter_vorname='',
                 email='k.schwarz@provadis.de', telefon='+49 69 305-1009', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=2,
                 notizen='Wirtschaftswissenschaften und Controlling.'),
            dict(titel='', status='intern', nachname='Lang', vorname='Tobias', zweiter_vorname='',
                 email='t.lang@provadis.de', telefon='+49 69 305-1010', praeferenz='A',
                 master_prioritaet=2, bachelor_prioritaet=1,
                 notizen='Lehrkraft für besondere Aufgaben, Schwerpunkt Webentwicklung.'),

            # --- Externe Dozenten ---
            dict(titel='', status='extern', nachname='Fischer', vorname='Sandra', zweiter_vorname='',
                 email='s.fischer@extern-uni.de', telefon='+49 170 1234567', praeferenz='B',
                 master_prioritaet=None, bachelor_prioritaet=1,
                 notizen='Lehrbeauftragte an der Goethe-Universität.'),
            dict(titel='Dr.', status='extern', nachname='Schneider', vorname='Michael', zweiter_vorname='Johannes',
                 email='m.schneider@extern-uni.de', telefon='+49 171 9876543', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=1,
                 notizen='Freiberuflicher Projektmanagement-Trainer.'),
            dict(titel='', status='extern', nachname='Becker', vorname='Stefan', zweiter_vorname='',
                 email='s.becker@industry.com', telefon='+49 172 5551234', praeferenz='B',
                 master_prioritaet=None, bachelor_prioritaet=1,
                 notizen='IT-Consultant bei Accenture, Gastdozent.'),
            dict(titel='Prof.', status='extern', nachname='Koch', vorname='Martin', zweiter_vorname='Friedrich',
                 email='m.koch@other-uni.de', telefon='+49 173 3334444', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=2,
                 notizen='Professor an der TU Darmstadt, Kooperation.'),
            dict(titel='', status='extern', nachname='Richter', vorname='Julia', zweiter_vorname='',
                 email='j.richter@consulting.de', telefon='+49 174 7778888', praeferenz='A',
                 master_prioritaet=2, bachelor_prioritaet=1,
                 notizen='Selbstständige Unternehmensberaterin.'),
            dict(titel='Dr.', status='extern', nachname='Neumann', vorname='Robert', zweiter_vorname='',
                 email='r.neumann@fraunhofer.de', telefon='+49 175 2223333', praeferenz='M',
                 master_prioritaet=1, bachelor_prioritaet=None,
                 notizen='Fraunhofer-Institut, Experte für KI und Robotik.'),
            dict(titel='', status='extern', nachname='Zimmermann', vorname='Lisa', zweiter_vorname='Marie',
                 email='l.zimmermann@sap.com', telefon='+49 176 4445555', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=1,
                 notizen='SAP-Beraterin, Schwerpunkt ERP-Systeme.'),
            dict(titel='Prof.', status='extern', nachname='Hartmann', vorname='Dieter', zweiter_vorname='',
                 email='d.hartmann@hs-rheinmain.de', telefon='+49 611 9495-100', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=1,
                 notizen='Professor an der HS RheinMain, Fachbereich Chemie.'),
            dict(titel='', status='extern', nachname='Krüger', vorname='Simone', zweiter_vorname='',
                 email='s.krueger@deloitte.de', telefon='+49 177 6667777', praeferenz='B',
                 master_prioritaet=None, bachelor_prioritaet=1,
                 notizen='Wirtschaftsprüferin bei Deloitte, Gastdozentin.'),
            dict(titel='Dr.', status='extern', nachname='Meier', vorname='Florian', zweiter_vorname='',
                 email='f.meier@tu-darmstadt.de', telefon='+49 178 8889999', praeferenz='A',
                 master_prioritaet=1, bachelor_prioritaet=2,
                 notizen='Postdoc an der TU Darmstadt, Forschung Quantencomputing.'),
        ]

        dozenten = []
        for d in dozenten_data:
            dozent = Dozent(**d)
            db.session.add(dozent)
            dozenten.append(dozent)
        print(f'✓ {len(dozenten)} Dozenten erstellt.')

        # ─── Vorlesungen (35 Stück) ───
        vorlesungen_data = [
            # Bachelor
            dict(name='Mathematik I', status='offen', niveau='Bachelor', semester='WS2026/27'),            # 0
            dict(name='Mathematik II', status='offen', niveau='Bachelor', semester='SS2026'),               # 1
            dict(name='Statistik', status='offen', niveau='Bachelor', semester='WS2026/27'),                # 2
            dict(name='Informatik Grundlagen', status='offen', niveau='Bachelor', semester='WS2026/27'),    # 3
            dict(name='Programmierung I', status='offen', niveau='Bachelor', semester='WS2026/27'),         # 4
            dict(name='Programmierung II', status='offen', niveau='Bachelor', semester='SS2026'),            # 5
            dict(name='Datenbanken', status='offen', niveau='Bachelor', semester='SS2026'),                  # 6
            dict(name='Betriebswirtschaftslehre', status='offen', niveau='Bachelor', semester='WS2026/27'), # 7
            dict(name='Agile Projektarbeit', status='offen', niveau='Bachelor', semester='SS2026'),          # 8
            dict(name='Wirtschaftsinformatik', status='offen', niveau='Bachelor', semester='WS2026/27'),    # 9
            dict(name='Physik', status='offen', niveau='Bachelor', semester='WS2026/27'),                    # 10
            dict(name='Chemie Grundlagen', status='offen', niveau='Bachelor', semester='WS2026/27'),        # 11
            dict(name='Webentwicklung', status='offen', niveau='Bachelor', semester='SS2026'),               # 12
            dict(name='Technische Mechanik', status='offen', niveau='Bachelor', semester='WS2026/27'),      # 13
            dict(name='Rechnungswesen', status='offen', niveau='Bachelor', semester='SS2026'),               # 14
            dict(name='Marketing Grundlagen', status='offen', niveau='Bachelor', semester='WS2026/27'),     # 15
            dict(name='Wirtschaftsrecht', status='offen', niveau='Bachelor', semester='SS2026'),             # 16
            dict(name='Operations Research', status='offen', niveau='Bachelor', semester='WS2026/27'),      # 17
            dict(name='Lineare Algebra', status='offen', niveau='Bachelor', semester='SS2026'),              # 18

            # Master
            dict(name='Agile Projektarbeit', status='offen', niveau='Master', semester='SS2026'),            # 19
            dict(name='Data Science', status='offen', niveau='Master', semester='WS2026/27'),                # 20
            dict(name='Machine Learning', status='offen', niveau='Master', semester='SS2026'),               # 21
            dict(name='Projektmanagement', status='offen', niveau='Master', semester='WS2026/27'),          # 22
            dict(name='Führung und Organisation', status='offen', niveau='Master', semester='SS2026'),      # 23
            dict(name='Software Engineering', status='offen', niveau='Master', semester='SS2026'),           # 24
            dict(name='IT-Sicherheit', status='geschlossen', niveau='Master', semester=''),                  # 25
            dict(name='Supply Chain Management', status='offen', niveau='Master', semester='SS2026'),        # 26
            dict(name='Business Intelligence', status='offen', niveau='Master', semester='WS2026/27'),      # 27
            dict(name='Cloud Computing', status='offen', niveau='Master', semester='SS2026'),                # 28
            dict(name='Quantitative Methoden', status='offen', niveau='Master', semester='WS2026/27'),      # 29
            dict(name='Digitale Transformation', status='offen', niveau='Master', semester='SS2026'),       # 30
            dict(name='Forschungsmethoden', status='offen', niveau='Master', semester='WS2026/27'),         # 31
            dict(name='ERP-Systeme', status='offen', niveau='Master', semester='SS2026'),                    # 32
            dict(name='Künstliche Intelligenz', status='offen', niveau='Master', semester='WS2026/27'),     # 33
            dict(name='Quantencomputing', status='geschlossen', niveau='Master', semester=''),               # 34
        ]

        vorlesungen = []
        for v in vorlesungen_data:
            vorlesung = Vorlesung(**v)
            db.session.add(vorlesung)
            vorlesungen.append(vorlesung)
        print(f'✓ {len(vorlesungen)} Vorlesungen erstellt.')

        db.session.flush()

        # ─── Zuweisungen (Dozent-Index -> Vorlesung-Index) ───
        # Dozenten 0-9 = intern, 10-19 = extern
        # 0  Prof. Müller       | 1  Dr. Schmidt       | 2  Prof. Weber
        # 3  Prof. Wagner       | 4  Dr. Hoffmann      | 5  Dr. Klein
        # 6  Prof. Wolf         | 7  Prof. Braun       | 8  Dr. Schwarz
        # 9  Lang               | 10 Fischer            | 11 Dr. Schneider
        # 12 Becker             | 13 Prof. Koch         | 14 Richter
        # 15 Dr. Neumann        | 16 Zimmermann         | 17 Prof. Hartmann
        # 18 Krüger             | 19 Dr. Meier

        zuweisungen_data = [
            # --- Prof. Müller (0) – Mathematik ---
            (0, 0, 'S', 'P', None),    # Mathematik I – sofort, Provadis
            (0, 1, 'S', 'P', None),    # Mathematik II – sofort, Provadis
            (0, 2, '4', 'A', None),    # Statistik – 4W, andere HS
            (0, 18, 'S', 'P', None),   # Lineare Algebra – sofort, Provadis
            (0, 17, '4', 'N', None),   # Operations Research – 4W, nie

            # --- Dr. Schmidt (1) – Data Science & KI ---
            (1, 20, 'S', 'P', None),   # Data Science – sofort, Provadis
            (1, 21, 'S', 'P', None),   # Machine Learning – sofort, Provadis
            (1, 33, 'S', 'P', None),   # KI – sofort, Provadis
            (1, 2, 'M', 'N', None),    # Statistik – >4W, nie
            (1, 29, '4', 'A', None),   # Quantitative Methoden – 4W, andere HS

            # --- Prof. Weber (2) – Informatik ---
            (2, 3, 'S', 'P', None),    # Informatik Grundlagen – sofort, Provadis
            (2, 4, 'S', 'P', None),    # Programmierung I – sofort, Provadis
            (2, 5, '4', 'P', None),    # Programmierung II – 4W, Provadis
            (2, 6, 'S', 'A', None),    # Datenbanken – sofort, andere HS
            (2, 12, '4', 'P', None),   # Webentwicklung – 4W, Provadis
            (2, 24, 'M', 'N', None),   # Software Engineering – >4W, nie

            # --- Prof. Wagner (3) – Management ---
            (3, 23, 'S', 'P', None),   # Führung und Organisation – sofort, Provadis
            (3, 22, 'S', 'P', None),   # Projektmanagement – sofort, Provadis
            (3, 7, '4', 'P', 'B'),     # BWL – 4W, Provadis, nur Bachelor
            (3, 30, '4', 'A', None),   # Digitale Transformation – 4W, andere HS
            (3, 15, 'S', 'P', None),   # Marketing Grundlagen – sofort, Provadis

            # --- Dr. Hoffmann (4) – Machine Learning ---
            (4, 21, '4', 'A', None),   # Machine Learning – 4W, andere HS
            (4, 20, 'S', 'A', None),   # Data Science – sofort, andere HS
            (4, 24, 'S', 'P', None),   # Software Engineering – sofort, Provadis
            (4, 33, '4', 'P', None),   # KI – 4W, Provadis
            (4, 28, 'M', 'N', None),   # Cloud Computing – >4W, nie

            # --- Dr. Klein (5) – Datenbanken & IT-Sec ---
            (5, 6, 'S', 'P', None),    # Datenbanken – sofort, Provadis
            (5, 4, '4', 'P', None),    # Programmierung I – 4W, Provadis
            (5, 25, 'S', 'P', None),   # IT-Sicherheit – sofort, Provadis
            (5, 27, '4', 'A', None),   # Business Intelligence – 4W, andere HS
            (5, 28, '4', 'N', None),   # Cloud Computing – 4W, nie

            # --- Prof. Wolf (6) – Mathe & Physik ---
            (6, 0, 'S', 'P', None),    # Mathematik I – sofort, Provadis
            (6, 10, 'S', 'P', None),   # Physik – sofort, Provadis
            (6, 2, 'S', 'P', None),    # Statistik – sofort, Provadis
            (6, 18, '4', 'P', None),   # Lineare Algebra – 4W, Provadis
            (6, 29, 'S', 'P', None),   # Quantitative Methoden – sofort, Provadis

            # --- Prof. Braun (7) – Bachelor Grundlagen ---
            (7, 3, 'S', 'P', None),    # Informatik Grundlagen – sofort, Provadis
            (7, 0, '4', 'P', None),    # Mathematik I – 4W, Provadis
            (7, 4, '4', 'A', None),    # Programmierung I – 4W, andere HS
            (7, 12, 'S', 'P', None),   # Webentwicklung – sofort, Provadis
            (7, 13, 'M', 'N', None),   # Technische Mechanik – >4W, nie

            # --- Dr. Schwarz (8) – Wirtschaft ---
            (8, 7, 'S', 'P', None),    # BWL – sofort, Provadis
            (8, 14, 'S', 'P', None),   # Rechnungswesen – sofort, Provadis
            (8, 15, '4', 'P', None),   # Marketing Grundlagen – 4W, Provadis
            (8, 26, '4', 'A', None),   # Supply Chain Management – 4W, andere HS
            (8, 16, 'S', 'P', None),   # Wirtschaftsrecht – sofort, Provadis
            (8, 30, 'M', 'N', None),   # Digitale Transformation – >4W, nie

            # --- Lang (9) – Webentwicklung ---
            (9, 12, 'S', 'P', None),   # Webentwicklung – sofort, Provadis
            (9, 3, '4', 'P', None),    # Informatik Grundlagen – 4W, Provadis
            (9, 5, 'S', 'P', None),    # Programmierung II – sofort, Provadis
            (9, 4, 'S', 'P', None),    # Programmierung I – sofort, Provadis
            (9, 9, '4', 'A', None),    # Wirtschaftsinformatik – 4W, andere HS

            # --- Fischer (10) – extern, Bachelor ---
            (10, 7, 'S', 'P', None),   # BWL – sofort, Provadis
            (10, 8, '4', 'A', None),   # Agile Projektarbeit Bachelor – 4W, andere HS
            (10, 14, '4', 'P', None),  # Rechnungswesen – 4W, Provadis
            (10, 15, 'M', 'N', None),  # Marketing Grundlagen – >4W, nie

            # --- Dr. Schneider (11) – extern, Projektmanagement ---
            (11, 19, 'S', 'P', None),  # Agile Projektarbeit Master – sofort, Provadis
            (11, 22, '4', 'A', None),  # Projektmanagement – 4W, andere HS
            (11, 24, 'M', 'N', None),  # Software Engineering – >4W, nie
            (11, 8, '4', 'P', None),   # Agile Projektarbeit Bachelor – 4W, Provadis
            (11, 30, '4', 'A', None),  # Digitale Transformation – 4W, andere HS

            # --- Becker (12) – extern, IT ---
            (12, 9, 'S', 'P', None),   # Wirtschaftsinformatik – sofort, Provadis
            (12, 3, '4', 'N', None),   # Informatik Grundlagen – 4W, nie
            (12, 12, '4', 'A', None),  # Webentwicklung – 4W, andere HS
            (12, 28, 'M', 'N', None),  # Cloud Computing – >4W, nie

            # --- Prof. Koch (13) – extern, Supply Chain ---
            (13, 19, '4', 'A', None),  # Agile Projektarbeit Master – 4W, andere HS
            (13, 26, 'S', 'P', None),  # Supply Chain Management – sofort, Provadis
            (13, 22, '4', 'P', None),  # Projektmanagement – 4W, Provadis
            (13, 17, 'S', 'A', None),  # Operations Research – sofort, andere HS

            # --- Richter (14) – extern, BWL/WI ---
            (14, 7, 'M', 'N', None),   # BWL – >4W, nie
            (14, 9, '4', 'A', None),   # Wirtschaftsinformatik – 4W, andere HS
            (14, 8, 'S', 'P', None),   # Agile Projektarbeit Bachelor – sofort, Provadis
            (14, 16, '4', 'A', None),  # Wirtschaftsrecht – 4W, andere HS

            # --- Dr. Neumann (15) – extern, KI & Robotik ---
            (15, 33, 'S', 'A', None),  # KI – sofort, andere HS
            (15, 21, '4', 'A', None),  # Machine Learning – 4W, andere HS
            (15, 20, '4', 'A', None),  # Data Science – 4W, andere HS
            (15, 34, 'S', 'A', None),  # Quantencomputing – sofort, andere HS

            # --- Zimmermann (16) – extern, ERP ---
            (16, 32, 'S', 'P', None),  # ERP-Systeme – sofort, Provadis
            (16, 9, '4', 'P', None),   # Wirtschaftsinformatik – 4W, Provadis
            (16, 27, '4', 'A', None),  # Business Intelligence – 4W, andere HS
            (16, 30, '4', 'N', None),  # Digitale Transformation – 4W, nie

            # --- Prof. Hartmann (17) – extern, Chemie ---
            (17, 11, 'S', 'P', None),  # Chemie Grundlagen – sofort, Provadis
            (17, 10, '4', 'A', None),  # Physik – 4W, andere HS
            (17, 13, 'S', 'A', None),  # Technische Mechanik – sofort, andere HS

            # --- Krüger (18) – extern, Wirtschaft ---
            (18, 14, 'S', 'A', None),  # Rechnungswesen – sofort, andere HS
            (18, 7, '4', 'A', None),   # BWL – 4W, andere HS
            (18, 16, 'S', 'P', None),  # Wirtschaftsrecht – sofort, Provadis

            # --- Dr. Meier (19) – extern, Quanten & Physik ---
            (19, 34, 'S', 'A', None),  # Quantencomputing – sofort, andere HS
            (19, 10, '4', 'A', None),  # Physik – 4W, andere HS
            (19, 29, '4', 'A', None),  # Quantitative Methoden – 4W, andere HS
            (19, 0, 'M', 'N', None),   # Mathematik I – >4W, nie
        ]

        for di, vi, qual, erf, npref in zuweisungen_data:
            zuweisung = DozentVorlesung(
                dozent_id=dozenten[di].id,
                vorlesung_id=vorlesungen[vi].id,
                qualifikation=qual,
                erfahrung=erf,
                niveau_praeferenz=npref
            )
            db.session.add(zuweisung)
        print(f'✓ {len(zuweisungen_data)} Zuweisungen erstellt.')

        db.session.commit()
        print('\n✅ Datenbank erfolgreich initialisiert!')
        print(f'   {len(dozenten)} Dozenten, {len(vorlesungen)} Vorlesungen, {len(zuweisungen_data)} Zuweisungen')
        print('   Anmeldedaten: admin / Provadis2026!')


if __name__ == '__main__':
    init_database()

