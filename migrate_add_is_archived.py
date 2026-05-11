#!/usr/bin/env python3
"""Simple migration script for SQLite: add `is_archived` columns if missing.
Creates a backup copy of the DB before modifying it.

Usage:
    python migrate_add_is_archived.py
"""
import os
import shutil
import sqlite3

# Try to detect DB path like the app does
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'dozentenverwaltung.db')

if not os.path.exists(db_path):
    print(f"Datenbank nicht gefunden: {db_path}")
    raise SystemExit(1)

bak_path = db_path + '.bak'
shutil.copy2(db_path, bak_path)
print(f"Backup erstellt: {bak_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

def has_column(table, column):
    cur.execute("PRAGMA table_info('%s')" % table)
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def add_column_if_missing(table, column):
    if has_column(table, column):
        print(f"Tabelle '{table}': Spalte '{column}' bereits vorhanden.")
        return False
    print(f"Tabelle '{table}': Spalte '{column}' fehlt — füge hinzu...")
    sql = f"ALTER TABLE {table} ADD COLUMN {column} INTEGER DEFAULT 0"
    cur.execute(sql)
    conn.commit()
    print(f"Spalte '{column}' zu Tabelle '{table}' hinzugefügt.")
    return True

changed = False
changed |= add_column_if_missing('dozenten', 'is_archived')
changed |= add_column_if_missing('vorlesungen', 'is_archived')

if not changed:
    print('Keine Änderungen notwendig.')
else:
    print('Migration abgeschlossen. Bitte Anwendung neu starten.')

conn.close()

