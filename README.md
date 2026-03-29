# Dozentenverwaltung – Provadis Hochschule Frankfurt

> **WebApp zur optimalen Zuweisung von Dozenten zu Vorlesungen**  
> Entwickelt für die Provadis Hochschule Frankfurt am Main

---

## Inhaltsverzeichnis

1. [Projektbeschreibung](#projektbeschreibung)
2. [Funktionsumfang](#funktionsumfang)
3. [Installation & Start](#installation--start)
4. [Anmeldedaten (Testumgebung)](#anmeldedaten-testumgebung)
5. [Bedienungsanleitung](#bedienungsanleitung)
6. [Technische Dokumentation](#technische-dokumentation)
7. [Datenmodell](#datenmodell)
8. [Projektstruktur](#projektstruktur)
9. [Testdaten](#testdaten)
10. [Projektbericht des Scrum Masters](#projektbericht-des-scrum-masters)

---

## Projektbeschreibung

Die **Dozentenverwaltung** ist eine browserbasierte Webanwendung, die es der Provadis Hochschule ermöglicht, die Zuweisung von Dozenten zu Vorlesungen systematisch zu verwalten und zu optimieren. 

### Problemstellung

An der Provadis Hochschule müssen regelmäßig Dozenten für Vorlesungen gefunden werden – oft kurzfristig. Dabei spielen verschiedene Faktoren eine Rolle:

- **Qualifikation**: Kann der Dozent sofort einspringen oder benötigt er Vorbereitungszeit?
- **Erfahrung**: Hat der Dozent die Vorlesung bereits an der Provadis, an einer anderen Hochschule oder noch nie gehalten?
- **Präferenzen**: Bevorzugt der Dozent Master- oder Bachelor-Vorlesungen?
- **Verfügbarkeit**: Ist der Dozent intern oder extern?

### Lösung

Die Anwendung bietet eine zentrale Plattform, um:

1. Alle Dozenten mit ihren Qualifikationen und Präferenzen zu verwalten
2. Alle Vorlesungen (Bachelor & Master) mit Semesterzuordnung zu pflegen
3. Über eine **intelligente Suche** den bestgeeigneten Dozenten für eine bestimmte Vorlesung zu finden
4. Über **Reports** systematische Auswertungen zu erstellen und zu exportieren

### Anwendungsbeispiele

- *„Ich suche dringend einen Dozenten, der das Fach Mathematik ohne Vorbereitung im Bachelorstudium unterrichten kann."*  
  → Suche: Vorlesung „Mathematik I" → Qualifikation „Sofort" → Erfahrung „Provadis"

- *„Ich suche einen Dozenten, der im nächsten Semester Agile Projektarbeit im Master unterrichten kann und das in der Vergangenheit an der Provadis schon getan hat."*  
  → Suche: Vorlesung „Agile Projektarbeit (Master)" → Erfahrung „Provadis"

---

## Funktionsumfang

### Kernfunktionen

| Funktion | Beschreibung |
|---|---|
| **Dozentenverwaltung** | Anlegen, bearbeiten und löschen von Dozenten mit Titel, Status (intern/extern), Kontaktdaten, Vorlieben und Prioritäten |
| **Vorlesungsverwaltung** | Verwaltung aller Vorlesungen mit Niveau (Bachelor/Master), Status (offen/geschlossen) und Semester |
| **Zuweisungen** | Verknüpfung von Dozenten mit Vorlesungen inkl. Qualifikation (S/4/M), Erfahrung (P/A/N) und Niveau-Präferenz pro Kurs |
| **Suche: Dozent für Vorlesung** | Vorlesung auswählen → nach Verfügbarkeit, Erfahrung und Niveau filtern → sortierte Ergebnisliste |
| **Suche: Vorlesungen für Dozent** | Dozent auswählen → alle zugewiesenen Vorlesungen mit Filter anzeigen |
| **Reports** | 4 vordefinierte Reports mit tabellarischer Anzeige und Export als CSV, JSON und PDF |
| **Login & Sicherheit** | Benutzername/Passwort mit optionaler Zwei-Faktor-Authentifizierung (TOTP) |

### Dozenten-Datenfelder

| Feld | Beschreibung | Pflicht |
|---|---|---|
| Titel | Prof., Dr. oder leer | Nein |
| Status | Intern oder Extern | Ja |
| Nachname | Familienname | Ja |
| Vorname | Rufname | Ja |
| Zweiter Vorname | Weiterer Vorname | Nein |
| E-Mail-Adresse | Kontakt-E-Mail | Ja |
| Telefonnummer | Kontakttelefon | Ja |
| Vorlesungspräferenz | M (nur Master), B (nur Bachelor), A (alle) | Ja |
| Master-Priorität | Priorität 1 oder 2 | Nein |
| Bachelor-Priorität | Priorität 1 oder 2 | Nein |
| Notizen | Freitextfeld | Nein |

### Vorlesungs-Datenfelder

| Feld | Beschreibung | Pflicht |
|---|---|---|
| Name | Name der Vorlesung | Ja |
| Status | Offen oder Geschlossen | Ja |
| Niveau | Bachelor oder Master | Ja |
| Semester | z.B. WS2026/27, SS2026 | Nein |

### Qualifikationsstufen (Dozent → Vorlesung)

| Kürzel | Bedeutung |
|---|---|
| **S** | Dozent kann die Vorlesung **sofort** ohne Vorlauf halten |
| **4** | Dozent benötigt **vier Wochen** Vorlaufzeit |
| **M** | Dozent benötigt **mehr als vier Wochen** Vorlaufzeit |

### Erfahrungsstufen

| Kürzel | Bedeutung |
|---|---|
| **P** | Dozent hat die Vorlesung an der **Provadis** schon gehalten |
| **A** | Dozent hat die Vorlesung an einer **anderen Hochschule** gehalten |
| **N** | Dozent hat die Vorlesung **noch nie** gehalten |

### Vorlieben-System

- **M** = Der Dozent hält ausschließlich Master-Vorlesungen
- **B** = Der Dozent hält ausschließlich Bachelor-Vorlesungen
- **A** = Der Dozent hält alle Vorlesungen. In diesem Fall können **pro Vorlesung** individuelle Niveau-Präferenzen gesetzt werden (z.B. Vorlesung X nur im Master)

Zusätzlich können Prioritäten vergeben werden:
- Master-Priorität 1 + Bachelor-Priorität 2 → Dozent macht beides, bevorzugt aber Master
- Bachelor-Priorität 1 + Master leer → Dozent hält ausschließlich Bachelor

### Reports

| # | Report | Beschreibung |
|---|---|---|
| 1 | **Dozenten mit Provadis-Erfahrung** | Alle Dozenten und Vorlesungen, die bereits an der Provadis gehalten wurden |
| 2 | **Dozenten ohne Provadis-Erfahrung** | Alle Dozenten und Vorlesungen, die noch nie an der Provadis gehalten wurden |
| 3 | **Vorlesungen ohne Dozent** | Alle Vorlesungen, denen kein Dozent zugewiesen ist |
| 4 | **Vorlesungen nur mit externer Erfahrung** | Vorlesungen, bei denen alle zugewiesenen Dozenten nur an anderen Hochschulen Erfahrung haben |

Jeder Report kann als **CSV**, **JSON** oder **PDF** exportiert werden.

---

## Installation & Start

### Voraussetzungen

- **Python 3.10** oder neuer
- **pip** (Python-Paketmanager)
- **Webbrowser**: Google Chrome oder Mozilla Firefox

### Schritt-für-Schritt-Anleitung

```bash
# 1. Repository klonen oder Projektordner öffnen
cd Dozentenverwaltung

# 2. Virtuelle Python-Umgebung erstellen
python3 -m venv venv

# 3. Virtuelle Umgebung aktivieren
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# 5. Datenbank initialisieren (erstellt SQLite-DB mit Beispieldaten)
python init_db.py

# 6. Anwendung starten
python app.py
```

Die Anwendung ist dann unter **http://localhost:5050** erreichbar.

> **Hinweis:** Port 5000 ist auf macOS durch AirPlay belegt, daher wird Port 5050 verwendet.

### Datenbank zurücksetzen

Um die Datenbank zurückzusetzen und alle Beispieldaten neu zu laden:

```bash
python init_db.py
```

Dies löscht alle vorhandenen Daten und erstellt die Datenbank mit den vordefinierten Testdaten neu.

---

## Anmeldedaten (Testumgebung)

| Benutzername | Passwort | Rolle |
|---|---|---|
| `admin` | `Provadis2026!` | Administrator (Vollzugriff) |
| `viewer` | `Viewer2026!` | Betrachter (für zukünftige Rollentrennung vorbereitet) |

---

## Bedienungsanleitung

### Typischer Ablauf 1: Dozent für eine Vorlesung suchen

1. Im Seitenmenü auf **„Dozent für Vorlesung"** klicken
2. Gewünschte **Vorlesung** aus der Dropdown-Liste auswählen
3. Optional filtern nach:
   - **Niveau**: Bachelor oder Master (Standard: alle)
   - **Verfügbarkeit**: Sofort, innerhalb 4 Wochen oder länger (Standard: alle)
   - **Erfahrung**: Provadis, andere Hochschule oder noch nie (Standard: alle)
4. Auf **„Suchen"** klicken
5. Die Ergebnisliste zeigt die geeigneten Dozenten **sortiert nach Eignung** (Provadis-Erfahrung + sofortige Verfügbarkeit zuerst)

### Typischer Ablauf 2: Vorlesungen eines Dozenten anzeigen

1. Im Seitenmenü auf **„Vorlesungen für Dozent"** klicken
2. Gewünschten **Dozenten** auswählen
3. Optional nach Niveau, Verfügbarkeit oder Erfahrung filtern
4. Alle zugewiesenen Vorlesungen werden mit sämtlichen Informationen angezeigt

### Reports erstellen

1. Im Seitenmenü auf **„Reports"** klicken
2. Gewünschten Report auswählen
3. Der Report wird als Tabelle im Browser angezeigt
4. Über die **Export-Buttons** (CSV, JSON, PDF) oben rechts können die Daten heruntergeladen werden

### Dozent anlegen

1. **„Dozenten"** → **„Neuer Dozent"**
2. Alle Pflichtfelder ausfüllen (Vorname, Nachname, E-Mail, Telefon, Status)
3. Vorlesungspräferenz festlegen (Master/Bachelor/Alle) und ggf. Prioritäten
4. **„Anlegen"** klicken

### Zuweisung erstellen

1. **„Zuweisung erstellen"** im Seitenmenü oder über den Button in der Dozenten-/Vorlesungsdetailansicht
2. Dozent und Vorlesung auswählen
3. Qualifikation (S/4/M) und Erfahrung (P/A/N) festlegen
4. Optional: Niveau-Präferenz pro Vorlesung (nur wenn Dozent-Präferenz „Alle" ist)
5. **„Erstellen"** klicken

### 2FA einrichten (optional)

1. **„Profil"** im Seitenmenü
2. Unter **„Zwei-Faktor-Authentifizierung"** auf **„2FA einrichten"** klicken
3. QR-Code mit einer Authenticator-App scannen (z.B. Google Authenticator, Authy)
4. Bestätigungscode eingeben und aktivieren

---

## Technische Dokumentation

### Technologie-Stack

| Komponente | Technologie | Version |
|---|---|---|
| **Backend** | Python, Flask | 3.x |
| **Datenbank** | SQLite (via SQLAlchemy ORM) | – |
| **Frontend** | HTML5, CSS3, JavaScript | – |
| **CSS-Framework** | Bootstrap 5 | 5.3.3 |
| **Icons** | Font Awesome | 6.5.1 |
| **Authentifizierung** | Flask-Login, Werkzeug | – |
| **2FA** | pyotp, qrcode | – |
| **PDF-Export** | ReportLab | 4.x |
| **Formulare** | Flask-WTF, WTForms | – |
| **CSRF-Schutz** | Flask-WTF CSRFProtect | – |

### Browserkompatibilität

- ✅ Google Chrome (aktuelle Version)
- ✅ Mozilla Firefox (aktuelle Version)
- ✅ Microsoft Edge (Chromium-basiert)
- ✅ Safari (macOS)

### Sicherheit

- Passwörter werden mit **Werkzeug** gehasht (PBKDF2 + SHA256 + Salt)
- **CSRF-Schutz** auf allen Formularen aktiv
- **2FA (TOTP)** vorbereitet und aktivierbar
- **Rollen-System** vorbereitet (admin, editor, viewer) für zukünftige Berechtigungstrennung
- Session-basierte Authentifizierung mit Flask-Login

---

## Datenmodell

```
┌─────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │ DozentVorlesung  │       │  Vorlesung   │
├─────────────┤       ├──────────────────┤       ├──────────────┤
│ id           │       │ id               │       │ id           │
│ username     │       │ dozent_id (FK)   │───┐   │ name         │
│ password_hash│       │ vorlesung_id(FK) │──┐│   │ status       │
│ display_name │       │ qualifikation    │  ││   │ niveau       │
│ role         │       │ erfahrung        │  ││   │ semester     │
│ totp_secret  │       │ niveau_praeferenz│  ││   └──────────────┘
│ is_2fa_enabled       │ notizen          │  ││           ▲
│ created_at   │       └──────────────────┘  ││           │
└─────────────┘               ▲              │└───────────┘
                              │              │
                    ┌─────────┘              │
                    │                        │
              ┌─────────────┐                │
              │   Dozent    │────────────────┘
              ├─────────────┤
              │ id           │
              │ titel        │
              │ status       │
              │ nachname     │
              │ vorname      │
              │ zweiter_vorn.│
              │ email        │
              │ telefon      │
              │ praeferenz   │
              │ master_prio  │
              │ bachelor_prio│
              │ notizen      │
              └─────────────┘
```

---

## Projektstruktur

```
Dozentenverwaltung/
├── app.py                          # Flask-Anwendung mit allen Routes
├── config.py                       # Konfiguration (DB-Pfad, Secret Key)
├── models.py                       # SQLAlchemy-Datenbankmodelle
├── forms.py                        # WTForms-Formulardefinitionen
├── init_db.py                      # Datenbank-Initialisierung mit Testdaten
├── requirements.txt                # Python-Abhängigkeiten
├── README.md                       # Diese Datei
├── dozentenverwaltung.db           # SQLite-Datenbank (nach init_db.py)
│
├── static/
│   ├── css/
│   │   └── style.css               # Provadis-Design (Farben, Layout, Komponenten)
│   ├── js/
│   │   └── app.js                  # Frontend-JavaScript (Sidebar, Filter, Sorting)
│   └── img/
│       ├── provadis-hochschule.svg       # Offizielles Provadis-Logo
│       └── provadis-hochschule-white.svg # Logo (weiß, für dunkle Sidebar)
│
└── templates/
    ├── base.html                   # Basis-Layout mit Sidebar-Navigation
    ├── login.html                  # Login-Seite
    ├── verify_2fa.html             # 2FA-Verifikation
    ├── setup_2fa.html              # 2FA-Einrichtung
    ├── profil.html                 # Benutzerprofil & Passwortänderung
    ├── dashboard.html              # Dashboard mit Statistiken
    ├── dozenten/
    │   ├── liste.html              # Dozenten-Übersicht mit Filter
    │   ├── detail.html             # Dozenten-Detailansicht
    │   └── form.html               # Dozent anlegen / bearbeiten
    ├── vorlesungen/
    │   ├── liste.html              # Vorlesungen-Übersicht mit Filter
    │   ├── detail.html             # Vorlesungen-Detailansicht
    │   └── form.html               # Vorlesung anlegen / bearbeiten
    ├── zuweisungen/
    │   └── form.html               # Zuweisung anlegen / bearbeiten
    ├── suche/
    │   ├── index.html              # Suche-Startseite
    │   ├── dozent_fuer_vorlesung.html  # Dozent für Vorlesung finden
    │   └── vorlesungen_fuer_dozent.html # Vorlesungen für Dozent anzeigen
    ├── reports/
    │   ├── index.html              # Reports-Übersicht
    │   └── ergebnis.html           # Report-Ergebnisanzeige mit Export
    └── errors/
        ├── 404.html                # Seite nicht gefunden
        └── 500.html                # Serverfehler
```

---

## Testdaten

Die Anwendung wird mit umfangreichen Testdaten ausgeliefert:

- **20 Dozenten** (10 intern, 10 extern) mit realistischen Profilen
- **35 Vorlesungen** (19 Bachelor, 16 Master) aus verschiedenen Fachbereichen
- **91 Zuweisungen** mit verschiedenen Qualifikations- und Erfahrungskombinationen
- **2 Benutzer** (Administrator und Betrachter)

Die Testdaten decken folgende Szenarien ab:
- Vorlesungen **mit** und **ohne** zugewiesene Dozenten
- Dozenten mit Erfahrung **nur an der Provadis**, **nur an anderen Hochschulen** und **ohne Erfahrung**
- Dozenten mit verschiedenen **Präferenzen** (nur Master, nur Bachelor, alle)
- Verschiedene **Qualifikationsstufen** (sofort, 4 Wochen, >4 Wochen)
- **Geschlossene** Vorlesungen (IT-Sicherheit, Quantencomputing)

---


