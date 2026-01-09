import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, time, timedelta
import json
from fpdf import FPDF
import bcrypt

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Fiber System", layout="wide")

# --- SŁOWNIK TŁUMACZEŃ (PL, DE, ENG) ---
TRANSLATIONS = {
    "PL": {
        "login_title": "🔐 Logowanie - Fiber System",
        "user_label": "Login",
        "pass_label": "Hasło",
        "login_btn": "Zaloguj",
        "login_error": "Błędny login lub hasło",
        "logout_btn": "Wyloguj",
        "sidebar_login_info": "Zalogowano jako:",
        "sidebar_admin_warning": "Panel Administratora",
        
        # Formularz Montera
        "form_title": "🛠️ Formularz Pracy (DG)",
        "mode_select_label": "Wybierz tryb:",
        "mode_new": "📝 Nowy Raport",
        "mode_edit": "✏️ Popraw Raport",
        "select_report_label": "Wybierz raport do edycji (Adres)",
        "no_reports_to_edit": "Brak raportów twojego zespołu z tego dnia.",
        "edit_loaded_info": "Edytujesz raport ID: {}",
        
        "expander_data": "📍 Dane Zlecenia",
        "date_label": "Data Raportu",
        "obj_num_label": "Numer Obiektu",
        "addr_label": "Adres",
        "worker_header": "👤 Zespół i Czas Pracy",
        "worker_select_label": "Wybierz Pracownika",
        "add_worker_btn": "➕ Dodaj kolejnego pracownika",
        "remove_worker_btn": "Usuń ostatniego",
        "start_label": "Początek",
        "break_label": "Przerwa (min)",
        "end_label": "Koniec",
        
        "err_start_time": "⚠️ Start pracy nie może być wcześniejszy niż 6:00!",
        "err_end_time": "⚠️ Koniec pracy następnego dnia nie może być później niż 5:00 rano!",
        "lbl_next_day_info": "ℹ️ Praca kończy się następnego dnia: {} ({}h)",
        
        "lbl_hup_question": "Czy założyłeś Hüp?",
        "lbl_hup_type": "Wybierz rodzaj Hüp:",
        "opt_hup_yes": "Tak",
        "opt_hup_no": "Nie",
        "opt_hup_std": "Hüp",
        "opt_hup_m": "M-Hüp",
        "opt_hup_change": "Wymiana na M-Hüp",
        
        "err_break_b2b": "⚠️ B2B: Powyżej 6h pracy wymagana jest przerwa min. 30 min!",
        "err_break_std_6h": "⚠️ Umowa (ArbZG): Powyżej 6h pracy wymagana jest przerwa min. 30 min!",
        "err_break_std_9h": "⚠️ Umowa (ArbZG): Powyżej 9h pracy wymagana jest przerwa min. 45 min!",
        
        "section_1_title": "1. Wykaz Prac (Mieszkania)",
        "lbl_we_count": "Liczba WE",
        "err_we_count": "Uzupełnij liczbę WE i przejdź dalej.",
        
        "section_2_title": "2. Zużyte Materiały",
        "section_3_title": "3. Status Zakończenia",
        
        "lbl_addr_finished": "Czy adres jest skończony?",
        "lbl_mfr_ready": "Czy MFR jest gotowa?",
        "lbl_reason": "Podaj powód (Wymagane):",
        "opt_yes": "Tak",
        "opt_no": "Nie",
        
        "save_btn": "💾 Zapisz Raport",
        "update_btn": "💾 Zaktualizuj Raport",
        "save_success": "Raport zapisany! Zespół: {}. Wykonano Gf-TA: {}",
        "update_success": "Raport zaktualizowany pomyślnie!",
        "save_error": "Błąd zapisu! Sprawdź godziny pracy, przerwy lub wymagane pola.",
        
        "col_flat": "Mieszkanie (Nr)",
        "col_activation": "Aktywacja",
        "tech_label": "Rodzaj Technologii",
        
        # Admin Dashboard
        "dash_title": "📊 Dashboard Zarządzania",
        "tab_day": "📅 Raport Dzienny",
        "tab_month": "📈 Statystyki Miesięczne",
        "tab_emp": "👥 Pracownicy",
        "tab_db": "🗄️ Pełna Baza",
        "tab_users": "🔑 Konta / Users",
        "tab_pdf": "📄 Raporty PDF",
        "no_data": "Brak danych w bazie.",
        
        # Admin Employees
        "emp_header": "Zarządzanie Pracownikami",
        "add_emp_label": "Dodaj pracownika (Imię i Nazwisko)",
        "lbl_contract_type": "Typ umowy",
        "opt_contract_b2b": "B2B (Samozatrudnienie)",
        "opt_contract_std": "Umowa o pracę (ArbZG)",
        "add_emp_btn": "Dodaj do listy",
        "del_emp_btn": "Usuń z listy",
        "current_emp_list": "Aktualna lista pracowników:",
        "emp_added": "Dodano pracownika: {} ({})",
        "emp_deleted": "Usunięto pracownika: {}",
        
        # Admin Users
        "user_header": "Zarządzanie Kontami Systemowymi",
        "add_user_header": "Dodaj nowe konto",
        "lbl_u_name": "Nazwa (np. Team 1)",
        "lbl_u_login": "Login",
        "lbl_u_pass": "Hasło",
        "lbl_u_role": "Rola",
        "btn_add_user": "Utwórz konto",
        "user_added_success": "Konto '{}' zostało utworzone.",
        "user_exists_error": "Login '{}' jest już zajęty.",
        "list_users_header": "Istniejące konta:",
        "btn_del_user": "Usuń konto",
        "user_deleted": "Usunięto konto: {}",

        # Admin PDF
        "pdf_header": "Generator Raportów Okresowych",
        "pdf_date_range": "Wybierz zakres dat",
        "pdf_gen_btn": "Generuj PDF",
        "pdf_download": "Pobierz Raport PDF",
        "pdf_no_data": "Brak danych w wybranym okresie.",
        
        # Admin Metrics
        "day_summary_header": "Podsumowanie dnia - wg Teamów",
        "pick_day": "Wybierz dzień",
        "no_reports_day": "Brak raportów z tego dnia.",
        "team_header": "👷 TEAM",
        
        "lbl_tab_summary": "📌 Podsumowanie",
        "total_day_label": "∑ SUMA DNIA (Wszystkie zlecenia)",
        
        "metric_hours": "🕒 Godziny",
        "metric_we": "🏠 WE",
        "metric_gfta": "📦 Gf-TA",
        "metric_ont": "modem ONT",
        "metric_activations": "⚡ Aktywacje",
        "metric_hup": "🔧 HÜP (Ilość)",
        "metric_hup_status": "Status HÜP",
        "lbl_activated_list": "Aktywowane ONT (nr mieszkań):",
        "lbl_gfta_list": "Zamontowane Gf-TA (nr mieszkań):",
        "metric_kanal": "📏 Metalikanal 30x30",
        "metric_srv": "🖥️ Serveschrank",
        "metric_tech_used": "⚙️ Technologia",
        "details_expander": "Szczegóły raportu",
        
        "col_materials": "Zużyte Materiały",
        "col_status_addr": "Status Adres",
        "col_status_mfr": "Status MFR",
        "lbl_workers": "Pracownicy:",
        "lbl_worker_hours": "Godziny Pracy:",
        
        "month_header": "Analiza Miesięczna",
        "pick_month": "Wybierz miesiąc",
        "lbl_emp_select": "Wybierz Pracownika",
        "lbl_total_hours": "Suma Godzin",
        "lbl_addr_context": "Adres / Zlecenie",
        "chart_team": "Instalacje (Team)",
        "db_header": "Pełny zrzut bazy danych"
    },
    "DE": {
        "login_title": "🔐 Anmeldung - Fiber System",
        "user_label": "Benutzername",
        "pass_label": "Passwort",
        "login_btn": "Anmelden",
        "login_error": "Falscher Benutzername oder Passwort",
        "logout_btn": "Abmelden",
        "sidebar_login_info": "Angemeldet als:",
        "sidebar_admin_warning": "Administrator-Panel",
        
        "form_title": "🛠️ Arbeitsbericht (DG)",
        "mode_select_label": "Modus wählen:",
        "mode_new": "📝 Neuer Bericht",
        "mode_edit": "✏️ Bericht korrigieren",
        "select_report_label": "Bericht zur Bearbeitung wählen",
        "no_reports_to_edit": "Keine Berichte Ihres Teams für diesen Tag.",
        "edit_loaded_info": "Bericht bearbeiten ID: {}",
        
        "expander_data": "📍 Auftragsdaten",
        "date_label": "Berichtsdatum",
        "obj_num_label": "Objektnummer",
        "addr_label": "Adresse",
        "worker_header": "👤 Team und Arbeitszeit",
        "worker_select_label": "Mitarbeiter wählen",
        "add_worker_btn": "➕ Nächsten Mitarbeiter hinzufügen",
        "remove_worker_btn": "Letzten entfernen",
        "start_label": "Beginn",
        "break_label": "Pause (Min)",
        "end_label": "Ende",
        
        "err_start_time": "⚠️ Arbeitsbeginn nicht vor 06:00 Uhr!",
        "err_end_time": "⚠️ Arbeitsende am nächsten Tag nicht später als 05:00 Uhr!",
        "lbl_next_day_info": "ℹ️ Arbeit endet am nächsten Tag: {} ({}h)",
        
        "lbl_hup_question": "Haben Sie den HÜP installiert?",
        "lbl_hup_type": "HÜP Typ wählen:",
        "opt_hup_yes": "Ja",
        "opt_hup_no": "Nein",
        "opt_hup_std": "Hüp",
        "opt_hup_m": "M-Hüp",
        "opt_hup_change": "Austausch gegen M-Hüp",

        "err_break_b2b": "⚠️ B2B: Über 6h Arbeit sind min. 30 Min Pause erforderlich!",
        "err_break_std_6h": "⚠️ ArbZG: Über 6h Arbeit sind min. 30 Min Pause erforderlich!",
        "err_break_std_9h": "⚠️ ArbZG: Über 9h Arbeit sind min. 45 Min Pause erforderlich!",
        
        "section_1_title": "1. Wohnungsliste",
        "lbl_we_count": "Anzahl WE",
        "err_we_count": "Bitte Anzahl WE ausfüllen und fortfahren.",
        
        "section_2_title": "2. Materialverbrauch",
        "section_3_title": "3. Fertigstellungsstatus",
        
        "lbl_addr_finished": "Ist die Adresse fertig?",
        "lbl_mfr_ready": "Ist MFR fertig?",
        "lbl_reason": "Grund angeben (Erforderlich):",
        "opt_yes": "Ja",
        "opt_no": "Nein",
        
        "save_btn": "💾 Bericht Speichern",
        "update_btn": "💾 Bericht Aktualisieren",
        "save_success": "Gespeichert! Team: {}. Gf-TA installiert: {}",
        "update_success": "Bericht erfolgreich aktualisiert!",
        "save_error": "Fehler beim Speichern! Überprüfen Sie die Zeiten/Felder.",
        
        "col_flat": "Wohnung (Nr)",
        "col_activation": "Aktivierung",
        "tech_label": "Technologieart",
        
        "dash_title": "📊 Management-Dashboard",
        "tab_day": "📅 Tagesbericht",
        "tab_month": "📈 Monatsstatistik",
        "tab_emp": "👥 Mitarbeiter",
        "tab_db": "🗄️ Datenbank",
        "tab_users": "🔑 Konten / Users",
        "tab_pdf": "📄 PDF Berichte",
        "no_data": "Keine Daten in der Datenbank.",
        
        "emp_header": "Mitarbeiterverwaltung",
        "add_emp_label": "Neuen Mitarbeiter hinzufügen",
        "lbl_contract_type": "Vertragsart",
        "opt_contract_b2b": "B2B (Selbstständig)",
        "opt_contract_std": "Arbeitsvertrag (ArbZG)",
        "add_emp_btn": "Hinzufügen",
        "del_emp_btn": "Entfernen",
        "current_emp_list": "Aktuelle Mitarbeiterliste:",
        "emp_added": "Mitarbeiter hinzugefügt: {} ({})",
        "emp_deleted": "Mitarbeiter entfernt: {}",
        
        "user_header": "Systemkonten verwalten",
        "add_user_header": "Neues Konto hinzufügen",
        "lbl_u_name": "Name (z.B. Team 1)",
        "lbl_u_login": "Login",
        "lbl_u_pass": "Passwort",
        "lbl_u_role": "Rolle",
        "btn_add_user": "Konto erstellen",
        "user_added_success": "Konto '{}' erstellt.",
        "user_exists_error": "Login '{}' ist bereits vergeben.",
        "list_users_header": "Vorhandene Konten:",
        "btn_del_user": "Entfernen",
        "user_deleted": "Konto gelöscht: {}",

        "pdf_header": "Periodischer Berichtsgenerator",
        "pdf_date_range": "Datumsbereich auswählen",
        "pdf_gen_btn": "PDF generieren",
        "pdf_download": "PDF-Bericht herunterladen",
        "pdf_no_data": "Keine Daten im ausgewählten Zeitraum.",
        
        "day_summary_header": "Tageszusammenfassung - nach Teams",
        "pick_day": "Tag wählen",
        "no_reports_day": "Keine Berichte für diesen Tag.",
        "team_header": "👷 TEAM",
        
        "lbl_tab_summary": "📌 Zusammenfassung",
        "total_day_label": "∑ TAGES-SUMME:",

        "metric_hours": "🕒 Stunden",
        "metric_we": "🏠 WE",
        "metric_gfta": "📦 Gf-TA",
        "metric_ont": "modem ONT",
        "metric_activations": "⚡ Aktivierungen",
        "metric_hup": "🔧 HÜP (Menge)",
        "metric_hup_status": "HÜP Status",
        "lbl_activated_list": "Aktivierte ONT (Wohnungsnr.):", 
        "lbl_gfta_list": "Installierte Gf-TA (Liste):",
        "metric_kanal": "📏 Metalikanal 30x30",
        "metric_srv": "🖥️ Serveschrank",
        "metric_tech_used": "⚙️ Technologie",
        "details_expander": "Bericht Details",
        
        "col_materials": "Materialien",
        "col_status_addr": "Status Adresse",
        "col_status_mfr": "Status MFR",
        "lbl_workers": "Mitarbeiter:",
        "lbl_worker_hours": "Arbeitszeiten:",
        
        "month_header": "Monatsanalyse",
        "pick_month": "Monat wählen",
        "lbl_emp_select": "Mitarbeiter wählen",
        "lbl_total_hours": "Gesamtstunden",
        "lbl_addr_context": "Adresse / Auftrag",
        "chart_team": "Installationen (Team)",
        "db_header": "Vollständiger Datenbankauszug"
    },
    "ENG": {
        "login_title": "🔐 Login - Fiber System",
        "user_label": "Username",
        "pass_label": "Password",
        "login_btn": "Login",
        "login_error": "Invalid username or password",
        "logout_btn": "Logout",
        "sidebar_login_info": "Logged in as:",
        "sidebar_admin_warning": "Admin Panel",
        
        "form_title": "🛠️ Work Report (DG)",
        "mode_select_label": "Select Mode:",
        "mode_new": "📝 New Report",
        "mode_edit": "✏️ Correct Report",
        "select_report_label": "Select Report to Edit",
        "no_reports_to_edit": "No reports for your team on this day.",
        "edit_loaded_info": "Editing Report ID: {}",
        
        "expander_data": "📍 Order Data",
        "date_label": "Report Date",
        "obj_num_label": "Object Number",
        "addr_label": "Address",
        "worker_header": "👤 Team & Working Time",
        "worker_select_label": "Select Worker",
        "add_worker_btn": "➕ Add Next Worker",
        "remove_worker_btn": "Remove Last",
        "start_label": "Start Time",
        "break_label": "Break (min)",
        "end_label": "End Time",
        
        "err_start_time": "⚠️ Start time cannot be earlier than 6:00!",
        "err_end_time": "⚠️ End time next day cannot be later than 5:00 AM!",
        "lbl_next_day_info": "ℹ️ Work ends next day: {} ({}h)",
        
        "lbl_hup_question": "Did you install HÜP?",
        "lbl_hup_type": "Select HÜP Type:",
        "opt_hup_yes": "Yes",
        "opt_hup_no": "No",
        "opt_hup_std": "Hüp",
        "opt_hup_m": "M-Hüp",
        "opt_hup_change": "Exchange to M-Hüp",

        "err_break_b2b": "⚠️ B2B: Over 6h work requires min. 30 min break!",
        "err_break_std_6h": "⚠️ Contract: Over 6h work requires min. 30 min break!",
        "err_break_std_9h": "⚠️ Contract: Over 9h work requires min. 45 min break!",
        
        "section_1_title": "1. Work List (Apartments)",
        "lbl_we_count": "WE Count",
        "err_we_count": "Fill in WE count and proceed.",
        
        "section_2_title": "2. Used Materials",
        "section_3_title": "3. Completion Status",
        
        "lbl_addr_finished": "Is address finished?",
        "lbl_mfr_ready": "Is MFR ready?",
        "lbl_reason": "Provide reason (Required):",
        "opt_yes": "Yes",
        "opt_no": "No",
        
        "save_btn": "💾 Save Report",
        "update_btn": "💾 Update Report",
        "save_success": "Report saved! Team: {}. Gf-TA installed: {}",
        "update_success": "Report updated successfully!",
        "save_error": "Save failed! Check hours or required fields.",
        
        "col_flat": "Flat (No)",
        "col_activation": "Activation",
        "tech_label": "Technology Type",
        
        "dash_title": "📊 Management Dashboard",
        "tab_day": "📅 Daily Report",
        "tab_month": "📈 Monthly Stats",
        "tab_emp": "👥 Employees",
        "tab_db": "🗄️ Full Database",
        "tab_users": "🔑 Accounts / Users",
        "tab_pdf": "📄 PDF Reports",
        "no_data": "No data in database.",
        
        "emp_header": "Employee Management",
        "add_emp_label": "Add New Employee",
        "lbl_contract_type": "Contract Type",
        "opt_contract_b2b": "B2B (Self-employed)",
        "opt_contract_std": "Employment Contract",
        "add_emp_btn": "Add to List",
        "del_emp_btn": "Remove",
        "current_emp_list": "Current Employee List:",
        "emp_added": "Added employee: {} ({})",
        "emp_deleted": "Removed employee: {}",
        
        "user_header": "System Account Management",
        "add_user_header": "Add New Account",
        "lbl_u_name": "Name (e.g. Team 1)",
        "lbl_u_login": "Login",
        "lbl_u_pass": "Password",
        "lbl_u_role": "Role",
        "btn_add_user": "Create Account",
        "user_added_success": "Account '{}' created.",
        "user_exists_error": "Login '{}' is already taken.",
        "list_users_header": "Existing Accounts:",
        "btn_del_user": "Delete",
        "user_deleted": "Deleted account: {}",

        "pdf_header": "Periodic Report Generator",
        "pdf_date_range": "Select Date Range",
        "pdf_gen_btn": "Generate PDF",
        "pdf_download": "Download PDF Report",
        "pdf_no_data": "No data in selected period.",
        
        "day_summary_header": "Daily Summary - by Teams",
        "pick_day": "Select Day",
        "no_reports_day": "No reports for this day.",
        "team_header": "👷 TEAM",
        
        "lbl_tab_summary": "📌 Summary",
        "total_day_label": "∑ DAILY TOTAL:",

        "metric_hours": "🕒 Hours",
        "metric_we": "🏠 WE",
        "metric_gfta": "📦 Gf-TA",
        "metric_ont": "modem ONT",
        "metric_activations": "⚡ Activations",
        "metric_hup": "🔧 HÜP (Count)",
        "metric_hup_status": "HÜP Status",
        "lbl_activated_list": "Activated ONT (Flat No):", 
        "lbl_gfta_list": "Installed Gf-TA (List):",
        "metric_kanal": "📏 Metalikanal 30x30",
        "metric_srv": "🖥️ Serveschrank",
        "metric_tech_used": "⚙️ Technology",
        "details_expander": "Report Details",
        
        "col_materials": "Materials",
        "col_status_addr": "Status Address",
        "col_status_mfr": "Status MFR",
        "lbl_workers": "Workers:",
        "lbl_worker_hours": "Working Hours:",
        
        "month_header": "Monthly Analysis",
        "pick_month": "Select Month",
        "lbl_emp_select": "Select Worker",
        "lbl_total_hours": "Total Hours",
        "lbl_addr_context": "Address / Order",
        "chart_team": "Installations (Team)",
        "db_header": "Full Database Dump"
    }
}

# Domyślny fallback jeśli brak tłumaczeń DE/ENG w skróconym kodzie:
if "DE" not in TRANSLATIONS: TRANSLATIONS["DE"] = TRANSLATIONS["PL"]
if "ENG" not in TRANSLATIONS: TRANSLATIONS["ENG"] = TRANSLATIONS["PL"]


# --- STAŁE ---
MATERIALS_LIST = [
    {"name": "FTTP 4 faser kabel", "unit": "m"},
    {"name": "MultiHüp", "unit": "st."},
    {"name": "Hüp", "unit": "st."},
    {"name": "T-stücke", "unit": "st."},
    {"name": "Instalacionsrohr", "unit": "m"},
    {"name": "Muffe M 20", "unit": "st."},
    {"name": "Quick Schellen M 20", "unit": "st."},
    {"name": "Schutzrohr", "unit": "m"},
    {"name": "Metalikanal 30x30", "unit": "m"},
    {"name": "Plastik kanal 15x15", "unit": "m"},
    {"name": "Plombe", "unit": "st."},
    {"name": "Serveschrank", "unit": "st."},
]
TECH_OPTIONS = ["LSK", "Lr", "Ws", "Srv", "Af", "Ka"]

# --- HELPERY DO BEZPIECZEŃSTWA ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- POŁĄCZENIE Z BAZĄ DANYCH (POSTGRESQL) ---
@st.cache_resource
def init_connection():
    # Pobieramy URL z sekretów Streamlit
    return psycopg2.connect(st.secrets["DATABASE_URL"], cursor_factory=RealDictCursor)

def run_query(query, params=None, fetch="all"):
    """Uniwersalna funkcja do zapytań SQL z obsługą reconnectu"""
    conn = init_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch == "all":
                return cur.fetchall()
            elif fetch == "one":
                return cur.fetchone()
            elif fetch == "none":
                conn.commit()
                return None
    except psycopg2.InterfaceError:
        # Jeśli połączenie zerwane, spróbuj połączyć ponownie (nie idealne, ale działa w prostych przypadkach)
        conn = init_connection() 
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()

def init_db():
    # Tworzenie tabel w PostgreSQL
    
    # 1. Pracownicy
    run_query('''
        CREATE TABLE IF NOT EXISTS employees (
            name TEXT PRIMARY KEY,
            contract_type TEXT DEFAULT 'Contract'
        )
    ''', fetch="none")
    
    # 2. Użytkownicy
    run_query('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            display_name TEXT
        )
    ''', fetch="none")
    
    # 3. Raporty (używamy SERIAL zamiast AUTOINCREMENT)
    run_query('''
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            date TEXT,
            team_name TEXT,
            address TEXT,
            object_num TEXT,
            we_count INTEGER,
            technology_type TEXT,
            workers_json TEXT,
            gfta_sum INTEGER,
            ont_gpon_sum INTEGER,
            ont_xgs_sum INTEGER,
            patch_ont_sum INTEGER,
            activation_sum INTEGER,
            address_finished TEXT,
            address_finished_reason TEXT,
            mfr_ready TEXT,
            mfr_ready_reason TEXT,
            hup_status TEXT,
            work_table_json TEXT,
            materials_json TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''', fetch="none")
    
    # Sprawdzenie admina
    res = run_query("SELECT count(*) as cnt FROM users", fetch="one")
    if res and res['cnt'] == 0:
        admin_hash = hash_password("admin123")
        run_query("INSERT INTO users (username, password, role, display_name) VALUES (%s, %s, %s, %s)",
                  ("admin", admin_hash, "admin", "Administrator"), fetch="none")
        print("Zainicjowano admina.")

# --- LOGIKA BIZNESOWA ---

def authenticate_user(username, password):
    row = run_query("SELECT password, role, display_name FROM users WHERE username=%s", (username,), fetch="one")
    if row:
        try:
            if check_password(password, row['password']):
                return {"role": row['role'], "display_name": row['display_name']}
        except ValueError:
            pass
    return None

def add_system_user(username, password, role, display_name):
    hashed = hash_password(password)
    try:
        run_query("INSERT INTO users (username, password, role, display_name) VALUES (%s, %s, %s, %s)",
                  (username, hashed, role, display_name), fetch="none")
        return True
    except:
        return False

def delete_system_user(username):
    run_query("DELETE FROM users WHERE username=%s", (username,), fetch="none")

def get_all_system_users():
    data = run_query("SELECT username, role, display_name FROM users ORDER BY username", fetch="all")
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["username", "role", "display_name"])

def add_employee(name, c_type):
    try:
        run_query("INSERT INTO employees (name, contract_type) VALUES (%s, %s)", (name, c_type), fetch="none")
        return True
    except:
        return False

def remove_employee(name):
    run_query("DELETE FROM employees WHERE name = %s", (name,), fetch="none")

def get_employees_map():
    data = run_query("SELECT name, contract_type FROM employees ORDER BY name", fetch="all")
    if not data: return {}
    df = pd.DataFrame(data)
    return pd.Series(df.contract_type.values, index=df.name).to_dict()
        
def get_employees():
    data = run_query("SELECT name FROM employees ORDER BY name", fetch="all")
    if not data: return []
    return [d['name'] for d in data]

def save_report_to_db(data):
    run_query('''
        INSERT INTO reports (
            date, team_name, address, object_num, we_count, technology_type,
            workers_json,
            gfta_sum, ont_gpon_sum, ont_xgs_sum, patch_ont_sum, activation_sum,
            address_finished, address_finished_reason, mfr_ready, mfr_ready_reason,
            hup_status,
            work_table_json, materials_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        data['date'], data['team'], data['address'], data['object_num'], data['we_count'], data['tech'],
        json.dumps(data['workers']),
        data['gfta_sum'], data['ont_gpon_sum'], data['ont_xgs_sum'], data['patch_ont_sum'], data['act_sum'],
        data['addr_fin'], data['addr_reason'], data['mfr_ready'], data['mfr_reason'],
        data['hup_status'],
        json.dumps(data['work_table']), json.dumps(data['materials'])
    ), fetch="none")

def update_report_in_db(report_id, data):
    run_query('''
        UPDATE reports SET
            date=%s, team_name=%s, address=%s, object_num=%s, we_count=%s, technology_type=%s,
            workers_json=%s,
            gfta_sum=%s, ont_gpon_sum=%s, ont_xgs_sum=%s, patch_ont_sum=%s, activation_sum=%s,
            address_finished=%s, address_finished_reason=%s, mfr_ready=%s, mfr_ready_reason=%s,
            hup_status=%s,
            work_table_json=%s, materials_json=%s
        WHERE id=%s
    ''', (
        data['date'], data['team'], data['address'], data['object_num'], data['we_count'], data['tech'],
        json.dumps(data['workers']),
        data['gfta_sum'], data['ont_gpon_sum'], data['ont_xgs_sum'], data['patch_ont_sum'], data['act_sum'],
        data['addr_fin'], data['addr_reason'], data['mfr_ready'], data['mfr_reason'],
        data['hup_status'],
        json.dumps(data['work_table']), json.dumps(data['materials']),
        report_id
    ), fetch="none")

def get_reports_by_team_and_date(team, date_str):
    data = run_query("SELECT id, address, object_num FROM reports WHERE team_name=%s AND date=%s", (team, date_str), fetch="all")
    # Zwracamy listę tupli żeby pasowało do starej logiki (id, address, object_num)
    return [(d['id'], d['address'], d['object_num']) for d in data] if data else []

def get_report_by_id(report_id):
    return run_query("SELECT * FROM reports WHERE id=%s", (report_id,), fetch="one")

def load_all_data():
    data = run_query("SELECT * FROM reports", fetch="all")
    return pd.DataFrame(data) if data else pd.DataFrame()

# --- KALKULACJE CZASU ---
def calculate_work_details(report_date, start_time, end_time, break_minutes):
    if not start_time or not end_time: return 0.0, "", "", False, "Brak czasu", 0
    if start_time < time(6, 0): return 0.0, "", "", False, "start_too_early", 0
    start_dt = datetime.combine(report_date, start_time)
    end_dt = datetime.combine(report_date, end_time)
    is_next_day = False
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
        is_next_day = True
    if is_next_day and end_time > time(5, 0): return 0.0, "", "", False, "end_too_late", 0
    duration = end_dt - start_dt
    total_minutes = duration.total_seconds() / 60
    try: brk = int(break_minutes)
    except: brk = 0
    actual_minutes = total_minutes - brk
    calculated_hours = round(actual_minutes / 60, 2)
    return calculated_hours, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"), True, None, brk

# --- PDF GENERATOR ---
def remove_polish_chars(text):
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
        'ü': 'ue', 'ä': 'ae', 'ö': 'oe', 'ß': 'ss', 'Ü': 'Ue', 'Ä': 'Ae', 'Ö': 'Oe'
    }
    for k, v in replacements.items(): text = text.replace(k, v)
    return text

def create_pdf_report(df, start_date, end_date):
    total_we = df['we_count'].sum()
    total_gfta = df['gfta_sum'].sum()
    total_srv, total_kanal, total_multihup, total_hup = 0, 0, 0, 0
    for idx, row in df.iterrows():
        if row['materials_json']:
            mats = json.loads(row['materials_json'])
            total_srv += mats.get("Serveschrank", 0)
            total_kanal += mats.get("Metalikanal 30x30", 0)
            total_multihup += mats.get("MultiHüp", 0)
            total_hup += mats.get("Hüp", 0)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = f"Raport Fiber System: {start_date} - {end_date}"
    pdf.cell(200, 10, txt=remove_polish_chars(title), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    def add_line(label, value, unit=""):
        txt = f"{label}: {value} {unit}"
        pdf.cell(200, 10, txt=remove_polish_chars(txt), ln=True, align='L')
    add_line("Suma WE (Liczba mieszkan)", total_we)
    add_line("Suma GF-TA", total_gfta)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Materialy:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    add_line("Serverschrank", total_srv, "st.")
    add_line("Metalikanal 30x30", total_kanal, "m")
    add_line("MultiHup", total_multihup, "st.")
    add_line("Hup", total_hup, "st.")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- UI START ---
init_db()

if 'lang' not in st.session_state: st.session_state['lang'] = 'PL'
def get_text(key): return TRANSLATIONS[st.session_state['lang']][key]

with st.sidebar:
    st.write("🌐 Language / Język / Sprache")
    selected_lang = st.selectbox("Wybierz", ["PL", "DE", "ENG"], index=["PL", "DE", "ENG"].index(st.session_state['lang']))
    if selected_lang != st.session_state['lang']:
        st.session_state['lang'] = selected_lang
        st.rerun()
    st.divider()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.session_state['display_name'] = None

def login_screen():
    st.title(get_text("login_title"))
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input(get_text("user_label"))
        password = st.text_input(get_text("pass_label"), type="password")
        if st.button(get_text("login_btn")):
            user_data = authenticate_user(username, password)
            if user_data:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['role'] = user_data['role']
                st.session_state['display_name'] = user_data['display_name']
                st.rerun()
            else:
                st.error(get_text("login_error"))

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.session_state['display_name'] = None
    st.rerun()

def monter_view():
    disp = st.session_state.get('display_name') or st.session_state['username']
    st.sidebar.info(f"{get_text('sidebar_login_info')} {disp}")
    if st.sidebar.button(get_text("logout_btn")): logout()
    st.title(get_text("form_title"))
    
    emp_map = get_employees_map()
    employee_list = list(emp_map.keys())

    if 'report_mode' not in st.session_state: st.session_state['report_mode'] = 'new'
    st.session_state['report_mode'] = st.radio(get_text("mode_select_label"), ('new', 'edit'), format_func=lambda x: get_text("mode_new") if x == 'new' else get_text("mode_edit"), horizontal=True)

    loaded_report, current_edit_id = None, None
    if st.session_state['report_mode'] == 'edit':
        st.info("Tryb edycji: Wybierz datę i adres.")
        c_date, c_rep = st.columns(2)
        edit_date = c_date.date_input("Data", datetime.now())
        available_reports = get_reports_by_team_and_date(st.session_state['username'], edit_date.strftime("%Y-%m-%d"))
        if not available_reports:
            st.warning(get_text("no_reports_to_edit"))
            return
        report_options = {f"{r[1]} ({r[2]})": r[0] for r in available_reports}
        selected_label = c_rep.selectbox(get_text("select_report_label"), list(report_options.keys()))
        if selected_label:
            current_edit_id = report_options[selected_label]
            loaded_report = get_report_by_id(current_edit_id)
            if loaded_report: st.success(get_text("edit_loaded_info").format(current_edit_id))
    
    def get_val(key, default): return loaded_report.get(key, default) if loaded_report else default

    with st.expander(get_text("expander_data"), expanded=True):
        col1, col2 = st.columns(2)
        default_date = datetime.strptime(loaded_report['date'], "%Y-%m-%d") if loaded_report else datetime.now()
        date_rep = col1.date_input(get_text("date_label"), default_date)
        obj_num = col2.text_input(get_text("obj_num_label"), value=get_val('object_num', ""))
        address = st.text_input(get_text("addr_label"), value=get_val('address', ""))
        st.divider()
        st.write(f"**{get_text('worker_header')}**")
        
        loaded_workers_list = json.loads(loaded_report['workers_json']) if (loaded_report and loaded_report['workers_json']) else []
        if st.session_state['report_mode'] == 'edit' and loaded_workers_list:
             if 'last_edit_id' not in st.session_state or st.session_state['last_edit_id'] != current_edit_id:
                 st.session_state.worker_count = len(loaded_workers_list)
                 st.session_state['last_edit_id'] = current_edit_id
        if 'worker_count' not in st.session_state: st.session_state.worker_count = 1

        workers_data, all_workers_valid = [], True
        for i in range(st.session_state.worker_count):
            st.markdown(f"**Pracownik #{i+1}**")
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            def_w_name, def_w_start, def_w_break, def_w_end = "", time(8,0), "0", time(16,0)
            if loaded_workers_list and i < len(loaded_workers_list):
                w = loaded_workers_list[i]
                def_w_name = w['name']
                try:
                    def_w_start = datetime.strptime(w['start'][:5], "%H:%M").time()
                    def_w_end = datetime.strptime(w['end'][:5], "%H:%M").time()
                    def_w_break = w['break']
                except: pass
            
            k_base = f"{i}_{st.session_state['report_mode']}_{current_edit_id}"
            k_name, k_start, k_break, k_end = f"w_name_{k_base}", f"w_start_{k_base}", f"w_break_{k_base}", f"w_end_{k_base}"
            
            if k_name not in st.session_state: st.session_state[k_name] = def_w_name if def_w_name in employee_list else (employee_list[0] if employee_list else "")
            if k_start not in st.session_state: st.session_state[k_start] = def_w_start
            if k_break not in st.session_state: st.session_state[k_break] = def_w_break
            if k_end not in st.session_state: st.session_state[k_end] = def_w_end

            w_name = c1.selectbox(get_text("worker_select_label"), employee_list, key=k_name) if employee_list else c1.text_input(get_text("worker_select_label"), key=k_name)
            w_start = c2.time_input(get_text("start_label"), key=k_start)
            w_break = c3.text_input(get_text("break_label"), key=k_break)
            w_end = c4.time_input(get_text("end_label"), key=k_end)
            
            hrs, s_str, e_str, valid, err_code, break_int = calculate_work_details(date_rep, w_start, w_end, w_break)
            contract = emp_map.get(w_name, "Contract")
            if not valid:
                all_workers_valid = False
                st.error(get_text("err_start_time") if err_code == "start_too_early" else get_text("err_end_time"))
            else:
                work_min_net = hrs * 60
                if contract == "B2B" and work_min_net > 360 and break_int < 30:
                    st.error(get_text("err_break_b2b"))
                    all_workers_valid = False
                elif contract != "B2B":
                     if (work_min_net > 360 and work_min_net <= 540 and break_int < 30):
                        st.error(get_text("err_break_std_6h"))
                        all_workers_valid = False
                     elif (work_min_net > 540 and break_int < 45):
                        st.error(get_text("err_break_std_9h"))
                        all_workers_valid = False
            workers_data.append({"name": w_name, "start": str(w_start), "break": w_break, "end": str(w_end), "calculated_hours": hrs, "display_start": s_str, "display_end": e_str})
        
        bc1, bc2 = st.columns(2)
        if bc1.button(get_text("add_worker_btn")): st.session_state.worker_count += 1; st.rerun()
        if st.session_state.worker_count > 1 and bc2.button(get_text("remove_worker_btn")): st.session_state.worker_count -= 1; st.rerun()

    st.subheader(get_text("section_1_title"))
    we_count = st.number_input(get_text("lbl_we_count"), min_value=0, step=1, value=get_val('we_count', 0))
    
    loaded_df = pd.DataFrame(json.loads(loaded_report['work_table_json'])) if (loaded_report and loaded_report['work_table_json']) else pd.DataFrame({
        "Wohnung": [""] * 12, "Gfta": [False] * 12, "Ont gpon": [False] * 12, "Ont xgs": [False] * 12, "Patch Ont": [False] * 12, "Activation": [False] * 12, 
    })
    edited_df = st.data_editor(loaded_df, num_rows="dynamic", width='stretch', column_config={"Wohnung": st.column_config.TextColumn(get_text("col_flat"), width="small"), "Activation": st.column_config.CheckboxColumn(get_text("col_activation"), default=False)})
    
    st.info(get_text("tech_label"))
    tech_idx = TECH_OPTIONS.index(loaded_report['technology_type']) if (loaded_report and loaded_report['technology_type'] in TECH_OPTIONS) else 0
    selected_tech = st.selectbox(get_text("tech_label"), TECH_OPTIONS, index=tech_idx, label_visibility="collapsed")

    st.subheader(get_text("section_2_title"))
    hup_status_val = loaded_report.get('hup_status', get_text("opt_hup_no")) if loaded_report else get_text("opt_hup_no")
    st.markdown(f"**{get_text('lbl_hup_question')}**")
    hup_yn = st.radio("hup_yn", [get_text("opt_hup_no"), get_text("opt_hup_yes")], index=1 if (hup_status_val != get_text("opt_hup_no") and hup_status_val != "Nie") else 0, horizontal=True, label_visibility="collapsed")
    final_hup_status = get_text("opt_hup_no")
    if hup_yn == get_text("opt_hup_yes"):
        st.caption(get_text("lbl_hup_type"))
        opts = [get_text("opt_hup_std"), get_text("opt_hup_m"), get_text("opt_hup_change")]
        final_hup_status = st.radio("hup_type", opts, index=opts.index(hup_status_val) if hup_status_val in opts else 0, label_visibility="collapsed")
    
    st.divider()
    loaded_mats = json.loads(loaded_report['materials_json']) if (loaded_report and loaded_report['materials_json']) else {}
    materials_collected = {}
    m_cols = st.columns(3)
    for i, item in enumerate(MATERIALS_LIST):
        with m_cols[i % 3]:
            qty = st.number_input(f"{i+1}. {item['name']} ({item['unit']})", min_value=0, step=1, value=loaded_mats.get(item['name'], 0), key=f"mat_{i}_{current_edit_id}")
            if qty > 0: materials_collected[item['name']] = qty
    st.divider()

    st.subheader(get_text("section_3_title"))
    c_s1, c_s2 = st.columns(2)
    def_addr_fin = 1 if (loaded_report and loaded_report['address_finished'] == get_text("opt_no")) else 0
    def_mfr_fin = 1 if (loaded_report and loaded_report['mfr_ready'] == get_text("opt_no")) else 0
    
    with c_s1:
        st.write(f"**{get_text('lbl_addr_finished')}**")
        addr_fin = st.radio("addr_fin", [get_text("opt_yes"), get_text("opt_no")], index=def_addr_fin, horizontal=True, label_visibility="collapsed")
        addr_reason = st.text_input(get_text("lbl_reason"), value=get_val('address_finished_reason', ""), key="ar") if addr_fin == get_text("opt_no") else ""
    with c_s2:
        st.write(f"**{get_text('lbl_mfr_ready')}**")
        mfr_fin = st.radio("mfr_fin", [get_text("opt_yes"), get_text("opt_no")], index=def_mfr_fin, horizontal=True, label_visibility="collapsed")
        mfr_reason = st.text_input(get_text("lbl_reason"), value=get_val('mfr_ready_reason', ""), key="mr") if mfr_fin == get_text("opt_no") else ""

    st.divider()
    btn_txt = get_text("save_btn") if st.session_state['report_mode'] == 'new' else get_text("update_btn")
    if st.button(btn_txt, type="primary"):
        if we_count <= 0: st.error(get_text("err_we_count")); return
        if not all_workers_valid: st.error(get_text("save_error")); return
        if (addr_fin == get_text("opt_no") and not addr_reason.strip()) or (mfr_fin == get_text("opt_no") and not mfr_reason.strip()): st.error(get_text("save_error")); return

        if address and len(workers_data) > 0:
            payload = {
                "date": date_rep.strftime("%Y-%m-%d"), "team": st.session_state['username'], "address": address, "object_num": obj_num,
                "we_count": we_count, "tech": selected_tech, "workers": workers_data,
                "gfta_sum": int(edited_df["Gfta"].sum()), "ont_gpon_sum": int(edited_df["Ont gpon"].sum()), 
                "ont_xgs_sum": int(edited_df["Ont xgs"].sum()), "patch_ont_sum": int(edited_df["Patch Ont"].sum()), 
                "act_sum": int(edited_df["Activation"].sum()), "addr_fin": addr_fin, "addr_reason": addr_reason,
                "mfr_ready": mfr_fin, "mfr_reason": mfr_reason, "hup_status": final_hup_status,
                "work_table": edited_df.to_dict(orient='records'), "materials": materials_collected
            }
            if st.session_state['report_mode'] == 'new':
                save_report_to_db(payload)
                st.session_state.worker_count = 1
                st.success(get_text("save_success").format(st.session_state['username'], payload['gfta_sum']))
            else:
                update_report_in_db(current_edit_id, payload)
                st.success(get_text("update_success"))
        else: st.error(get_text("save_error"))

def get_localized_hup_status(saved_status):
    """
    Tłumaczy zapisany w bazie status HÜP na aktualny język interfejsu.
    Obsługuje przypadki, gdy w bazie jest zapisane po PL, a oglądamy po DE.
    """
    if not saved_status:
        return "-"
        
    # Lista wszystkich możliwych wariantów "NIE" (zapisanych w bazie)
    no_variants = ["Nie", "Nein", "No"]
    # Lista wariantów "WYMIANA"
    change_variants = ["Wymiana na M-Hüp", "Austausch gegen M-Hüp", "Exchange to M-Hüp"]
    # Warianty standardowe (są takie same w każdym języku, ale dla porządku)
    std_variants = ["Hüp"]
    m_variants = ["M-Hüp"]

    # Logika mapowania na klucz słownika TRANSLATIONS
    target_key = None
    
    if saved_status in no_variants:
        target_key = "opt_hup_no"
    elif saved_status in change_variants:
        target_key = "opt_hup_change"
    elif saved_status in std_variants:
        target_key = "opt_hup_std"
    elif saved_status in m_variants:
        target_key = "opt_hup_m"
    elif saved_status in ["Tak", "Ja", "Yes"]: 
        target_key = "opt_hup_yes"

    # Jeśli znaleźliśmy klucz, zwracamy tłumaczenie w obecnym języku
    if target_key:
        return get_text(target_key)
    
    # Jeśli to coś innego (np. pusty string), zwracamy oryginał
    return saved_status

def admin_view():
    disp = st.session_state.get('display_name') or st.session_state['username']
    st.sidebar.warning(f"{get_text('sidebar_admin_warning')} {disp}")
    if st.sidebar.button(get_text("logout_btn")): logout()
    st.title(get_text("dash_title"))
    df = load_all_data()
    t1, t2, t3, t4, t5, t6 = st.tabs([
        get_text("tab_day"), get_text("tab_month"), get_text("tab_emp"), 
        get_text("tab_db"), get_text("tab_users"), get_text("tab_pdf")
    ])

    # --- TAB 1: DZIENNY ---
    with t1:
        if df.empty:
            st.info(get_text("no_data"))
        else:
            df['date'] = pd.to_datetime(df['date'])
            st.header(get_text("day_summary_header"))
            sel_day = st.date_input(get_text("pick_day"), datetime.now())
            d_df = df[df['date'].dt.date == sel_day]
            
            if d_df.empty:
                st.info(get_text("no_reports_day"))
            else:
                for team in d_df['team_name'].unique():
                    team_data = d_df[d_df['team_name'] == team]
                    with st.container(border=True):
                        st.subheader(f"{get_text('team_header')} {team.upper()}")
                        
                        daily_total_hours = 0
                        daily_total_we = 0
                        daily_total_gfta = 0
                        daily_total_ont = 0
                        daily_total_activations = 0
                        daily_hup_count = 0
                        
                        for idx, row in team_data.iterrows():
                            if row['workers_json']:
                                try:
                                    workers = json.loads(row['workers_json'])
                                    for w in workers:
                                        daily_total_hours += w.get('calculated_hours', 0)
                                except: pass
                            
                            daily_total_we += row['we_count']
                            daily_total_gfta += row['gfta_sum']
                            daily_total_ont += (row['ont_gpon_sum'] + row['ont_xgs_sum'])
                            daily_total_activations += row['activation_sum']
                            
                            raw_hup = row.get('hup_status')
                            localized_hup = get_localized_hup_status(raw_hup)
                            
                            if localized_hup and localized_hup != get_text("opt_hup_no") and localized_hup != "-":
                                daily_hup_count += 1

                        report_indices = team_data.index.tolist()
                        tab_labels = [get_text("lbl_tab_summary")] 
                        for idx in report_indices:
                            row = team_data.loc[idx]
                            label = f"{row['address']} ({row['object_num']})"
                            if not label or label == " ()": label = f"Raport #{idx}"
                            tab_labels.append(label)
                        
                        tabs = st.tabs(tab_labels)
                        
                        for i, tab in enumerate(tabs):
                            with tab:
                                if i == 0:
                                    st.caption(f"**{get_text('total_day_label')}**")
                                    cols_sum = st.columns(6)
                                    cols_sum[0].metric(get_text("metric_hours"), f"{daily_total_hours:.1f} h")
                                    cols_sum[1].metric(get_text("metric_we"), daily_total_we)
                                    cols_sum[2].metric(get_text("metric_gfta"), daily_total_gfta)
                                    cols_sum[3].metric(get_text("metric_ont"), daily_total_ont)
                                    cols_sum[4].metric(get_text("metric_activations"), daily_total_activations)
                                    cols_sum[5].metric(get_text("metric_hup"), daily_hup_count)
                                else:
                                    row_idx = report_indices[i-1]
                                    row = team_data.loc[row_idx]
                                    
                                    report_hours = 0
                                    workers_details_list = []
                                    if row['workers_json']:
                                        try:
                                            w_data = json.loads(row['workers_json'])
                                            for w in w_data:
                                                report_hours += w.get('calculated_hours', 0)
                                                if 'display_start' in w and 'display_end' in w:
                                                    workers_details_list.append(f"{w['name']} {w['display_start']} - {w['display_end']} ({w['break']} min)")
                                                else:
                                                    s_time = str(w['start'])[:5]
                                                    e_time = str(w['end'])[:5]
                                                    workers_details_list.append(f"{w['name']} {s_time}-{e_time} ({w['break']})")
                                        except: pass
                                    
                                    r_gfta = row['gfta_sum']
                                    r_we = row['we_count']
                                    r_tech = row['technology_type']
                                    r_hup_stat = get_localized_hup_status(row.get('hup_status', '-'))
                                    
                                    metric_label_mat = get_text("metric_kanal")
                                    metric_unit_mat = "m"
                                    target_key = "Metalikanal 30x30"
                                    if r_tech == "Srv":
                                        metric_label_mat = get_text("metric_srv")
                                        metric_unit_mat = "st."
                                        target_key = "Serveschrank"
                                    
                                    r_mat_val = 0
                                    mats = {}
                                    if row['materials_json']:
                                        try:
                                            mats = json.loads(row['materials_json'])
                                            r_mat_val = mats.get(target_key, 0)
                                        except: pass
                                        
                                    c1, c2, c3, c4 = st.columns(4)
                                    c1.metric(get_text("metric_hours"), f"{report_hours:.1f} h")
                                    c2.metric(get_text("metric_we"), r_we)
                                    c3.metric(metric_label_mat, f"{r_mat_val} {metric_unit_mat}")
                                    c4.metric(get_text("metric_hup_status"), r_hup_stat)

                                    st.divider()
                                    st.caption(f"{get_text('metric_tech_used')}: **{r_tech}**")

                                    if workers_details_list:
                                        st.write(f"**{get_text('lbl_worker_hours')}**")
                                        for w_det in workers_details_list:
                                            st.write(f"• {w_det}") 

                                    st.divider()

                                    active_flats = []
                                    gfta_flats = []
                                    if row['work_table_json']:
                                        try:
                                            wtable = json.loads(row['work_table_json'])
                                            for entry in wtable:
                                                flat_num = str(entry.get('Wohnung', ''))
                                                if entry.get('Activation'):
                                                    active_flats.append(flat_num)
                                                if entry.get('Gfta'):
                                                    gfta_flats.append(flat_num)
                                        except: pass

                                    if gfta_flats:
                                        st.write(f"**{get_text('lbl_gfta_list')}** {', '.join(gfta_flats)}")
                                    
                                    if active_flats:
                                        st.write(f"**{get_text('lbl_activated_list')}** {', '.join(active_flats)}")
                                        
                                    def format_status(status, reason, yes_val, no_val):
                                        if status == yes_val: return "✅"
                                        elif status == no_val: return f"❌ {reason}"
                                        return str(status)
                                    
                                    mat_str = "-"
                                    if mats:
                                        items = [f"{k}: {v}" for k,v in mats.items() if v>0]
                                        if items: mat_str = ", ".join(items)

                                    st_addr = format_status(row['address_finished'], row['address_finished_reason'], "Tak", "Nie")
                                    st_mfr = format_status(row['mfr_ready'], row['mfr_ready_reason'], "Tak", "Nie")

                                    single_view = pd.DataFrame([{
                                        "mat": mat_str,
                                        "st_addr": st_addr,
                                        "st_mfr": st_mfr
                                    }])
                                    
                                    st.dataframe(
                                        single_view,
                                        column_config={
                                            "mat": get_text("col_materials"),
                                            "st_addr": get_text("col_status_addr"),
                                            "st_mfr": get_text("col_status_mfr")
                                        },
                                        hide_index=True,
                                        width='stretch'
                                    )

    # --- TAB 2: MIESIĘCZNY (NAPRAWIONY) ---
    with t2:
        if df.empty:
            st.info(get_text("no_data"))
        else:
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
            all_months = sorted(df['month'].unique(), reverse=True)
            
            c1, c2 = st.columns(2)
            sel_emp = c1.selectbox(get_text("lbl_emp_select"), get_employees())
            sel_mon = c2.selectbox(get_text("pick_month"), all_months)

            m_df = df[df['month'] == sel_mon]
            
            worker_logs = []
            total_month_hours = 0
            
            for idx, row in m_df.iterrows():
                if row['workers_json']:
                    try:
                        w_list = json.loads(row['workers_json'])
                        # Szukamy konkretnego pracownika w liście
                        target = next((w for w in w_list if w['name'] == sel_emp), None)
                        if target:
                            # Próba wyciągnięcia sformatowanych czasów (jeśli są) lub ucięcie sekund
                            s_disp = target.get('display_start', str(target.get('start', ''))[:5])
                            e_disp = target.get('display_end', str(target.get('end', ''))[:5])
                            
                            log_entry = {
                                "Data": row['date'],
                                "Start": s_disp,
                                "Stop": e_disp,
                                "Przerwa": target.get('break', 0),
                                "Godziny": target.get('calculated_hours', 0),
                                "Adres": f"{row['address']} ({row['object_num']})"
                            }
                            worker_logs.append(log_entry)
                            total_month_hours += log_entry['Godziny']
                    except:
                        pass
            
            st.metric(f"{get_text('lbl_total_hours')}: {sel_emp} ({sel_mon})", f"{total_month_hours:.2f} h")
            
            if worker_logs:
                log_df = pd.DataFrame(worker_logs)
                # Sortowanie po dacie
                log_df['Data'] = pd.to_datetime(log_df['Data'])
                log_df = log_df.sort_values('Data')
                log_df['Data'] = log_df['Data'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    log_df,
                    column_config={
                        "Godziny": st.column_config.NumberColumn(get_text("metric_hours"), format="%.2f"),
                        "Adres": st.column_config.TextColumn(get_text("lbl_addr_context"), width="medium")
                    },
                    hide_index=True,
                    width='stretch'
                )
            else:
                st.warning("Brak raportów pracy dla tego pracownika w wybranym miesiącu.")

            st.divider()
            st.subheader(get_text("chart_team"))
            if not m_df.empty:
                team_stats = m_df.groupby('team_name')[['gfta_sum', 'ont_gpon_sum', 'ont_xgs_sum']].sum().reset_index()
                st.bar_chart(team_stats.set_index('team_name'))

    # --- TAB 3: PRACOWNICY ---
    with t3:
        c_f, c_l = st.columns(2)
        with c_f.form("add_e"):
            nm = st.text_input(get_text("add_emp_label"))
            ct = st.radio(get_text("lbl_contract_type"), ["B2B", "Contract"])
            if st.form_submit_button(get_text("add_emp_btn")) and nm: 
                if add_employee(nm, ct): st.success("OK"); st.rerun()
        
        with c_l:
            emp_map = get_employees_map()
            if emp_map:
                for name, c_type in emp_map.items():
                    c1, c2 = st.columns([4,1])
                    c_label = "B2B" if c_type == "B2B" else "Umowa"
                    c1.write(f"👤 **{name}** [{c_label}]")
                    if c2.button("X", key=f"d_{name}"): 
                        remove_employee(name)
                        st.rerun()
            else:
                st.info("Brak pracowników.")

    # --- TAB 4: BAZA DANYCH ---
    with t4: st.dataframe(df)

    # --- TAB 5: UŻYTKOWNICY SYSTEMU ---
    with t5:
        with st.expander(get_text("add_user_header")):
            with st.form("au"):
                u, p = st.text_input("Login"), st.text_input("Hasło", type="password")
                r, d = st.selectbox("Rola", ["monter", "admin"]), st.text_input("Nazwa")
                if st.form_submit_button("Dodaj") and u and p:
                    if add_system_user(u, p, r, d): st.success("OK"); st.rerun()
                    else: st.error("Error")
        for i, row in get_all_system_users().iterrows():
            c1, c2, c3 = st.columns([3,2,1])
            c1.write(f"{row['display_name']} ({row['role']})")
            if row['username'] != st.session_state['username'] and c3.button("X", key=f"du_{row['username']}"):
                delete_system_user(row['username']); st.rerun()

    # --- TAB 6: RAPORTY PDF ---
    with t6:
        d1, d2 = st.columns(2)
        sd = d1.date_input("Start", datetime.now().replace(day=1))
        ed = d2.date_input("End", datetime.now())
        if st.button(get_text("pdf_gen_btn")):
            df['date'] = pd.to_datetime(df['date'])
            f_df = df[(df['date'].dt.date >= sd) & (df['date'].dt.date <= ed)]
            if f_df.empty: st.warning("Brak danych")
            else:
                st.download_button(get_text("pdf_download"), create_pdf_report(f_df, sd, ed), f"rap_{sd}_{ed}.pdf", "application/pdf")

# --- APP START ---
if not st.session_state['logged_in']: login_screen()
else:
    if st.session_state['role'] == 'admin': admin_view()
    else: monter_view()