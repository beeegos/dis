import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, time, timedelta
import json
from fpdf import FPDF
import bcrypt
import time as time_lib

# --- KONFIGURACJA MATERIAŁÓW ---
MATERIALS = [
    "FTTP 4 faser kabel",
    "MultiHüp",
    "Hüp",
    "T-stücke",
    "Instalacionsrohr",
    "Muffe M 20",
    "Quick Schellen M 20",
    "Schutzrohr",
    "Metalikanal 30x30",
    "Plastik kanal 15x15",
    "Plombe",
    "Serveschrank"
]

MATERIALS_UNITS = {
    "FTTP 4 faser kabel": "m",
    "MultiHüp": "st.",
    "Hüp": "st.",
    "T-stücke": "st.",
    "Instalacionsrohr": "m",
    "Muffe M 20": "st.",
    "Quick Schellen M 20": "st.",
    "Schutzrohr": "m",
    "Metalikanal 30x30": "m",
    "Plastik kanal 15x15": "m",
    "Plombe": "st.",
    "Serveschrank": "st."
}

# --- LISTA TECHNOLOGII (Dla sekcji 3) ---
TECHNOLOGIES = [
    "LSK", 
    "Leerrohr", 
    "Ausenfasafde", 
    "Kamin", 
    "Serverschrank", 
    "Wohnungsteiger"
]

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
        "pick_edit_date": "Wybierz datę raportu do edycji",
        "no_reports_to_edit": "Brak raportów dla Twojego zespołu w tym dniu.",
        "edit_loaded_info": "Edytujesz raport ID: {}",
        "search_team_label": "Szukaj raportów dla zespołu (nazwa):",
        
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
        "car_label": "Auto",
        "clean_form_btn": "🧹 Wyczyść formularz",
        
        "err_start_time": "⚠️ Start pracy nie może być wcześniejszy niż 6:00!",
        "err_end_time": "⚠️ Koniec pracy następnego dnia nie może być później niż 5:00 rano!",
        "err_time_neg": "Czas pracy <= 0!",
        "err_worker_time": "Błąd godzin pracownika.",
        "err_add_one_worker": "Dodaj przynajmniej jednego pracownika!",
        "lbl_next_day_info": "ℹ️ Praca kończy się następnego dnia: {} ({}h)",
        
        # HUP - NOWE
        "lbl_hup_question": "Czy założyłeś HÜP?",
        "lbl_hup_type_select": "Wybierz rodzaj HÜP:",
        "opt_hup_yes": "Tak",
        "opt_hup_no": "Nie",
        
        "opt_hup_std": "Hüp",
        "opt_hup_multi": "MultiHüp",
        "opt_hup_change": "Wymiana na MHüp",
        "opt_hup_rebuild": "Przebudowa MHüp",
        
        "err_break_b2b": "⚠️ B2B: Powyżej 6h pracy wymagana jest przerwa min. 30 min!",
        "err_break_std_6h": "⚠️ Umowa (ArbZG): Powyżej 6h pracy wymagana jest przerwa min. 30 min!",
        "err_break_std_9h": "⚠️ Umowa (ArbZG): Powyżej 9h pracy wymagana jest przerwa min. 45 min!",
        
        "section_1_title": "1. Wykaz Prac (Mieszkania)",
        "lbl_we_count": "Liczba WE",
        "err_we_count": "⚠️ Uzupełnij liczbę WE (Mieszkania) aby zapisać raport!",
        "warn_fill_obj_we": "Uzupełnij 'Numer Obiektu' i 'Liczbę WE'.",
        "msg_flats_updated": "Zaktualizowano {} numerów mieszkań!",
        
        # Mobile View Translations & New Features
        "mobile_mode_toggle": "📱 Tryb mobilny (Duże przyciski)",
        "select_flat_label": "Wybierz mieszkanie do edycji:",
        "flat_pos_label": "Poz",
        "editing_info": "Edytujesz:",
        "flat_number_input": "Numer mieszkania (Wohnung)",
        "preview_full_list": "Podgląd całej listy",
        "btn_auto_fill": "⚡ Auto-uzupełnij numery mieszkań (z Nr Obiektu)",
        "btn_delete_report": "🗑️ Usuń ten raport (Bezpowrotnie!)",
        "btn_download_excel": "📥 Pobierz Raport Excel (Kolorowy)",
        "lbl_summary_inline": "Podsumowanie",

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
        "tab_emp": "👥 Pracownicy / Auta",
        "tab_db": "🗄️ Pełna Baza",
        "tab_users": "🔑 Konta / Users",
        "tab_pdf": "📄 Raporty PDF",
        "no_data": "Brak danych w bazie.",
        
        # Admin Employees & Cars
        "emp_header": "Zarządzanie Pracownikami",
        "car_header": "Zarządzanie Flotą (Auta)",
        "add_emp_label": "Dodaj pracownika (Imię i Nazwisko)",
        "add_car_label": "Dodaj auto (Nr Rejestracyjny)",
        "lbl_contract_type": "Typ umowy",
        "opt_contract_b2b": "B2B (Samozatrudnienie)",
        "opt_contract_std": "Umowa o pracę (ArbZG)",
        "add_emp_btn": "Dodaj do listy",
        "add_car_btn": "Dodaj auto",
        "del_btn": "Usuń",
        "current_emp_list": "Aktualna lista pracowników:",
        "current_car_list": "Aktualna lista aut:",
        "emp_added": "Dodano pracownika: {} ({})",
        "car_added": "Dodano auto: {}",
        "msg_no_employees": "Brak pracowników.",
        "msg_no_cars": "Brak aut w systemie.",
        
        # Admin Users
        "user_header": "Zarządzanie Kontami Systemowymi",
        "add_user_header": "Dodaj nowe konto",
        "lbl_u_name": "Nazwa (np. Team 1)",
        "lbl_u_login": "Login",
        "lbl_u_pass": "Hasło",
        "lbl_u_role": "Rola",
        "btn_add_user": "Konto erstellen",
        "user_added_success": "Konto '{}' zostało utworzone.",
        "user_exists_error": "Login '{}' jest już zajęty.",
        "list_users_header": "Istniejące konta:",
        "btn_del_user": "Usuń konto",
        "user_deleted": "Usunięto konto: {}",

        "pdf_header": "Generator Raportów Okresowych",
        "pdf_date_range": "Wybierz zakres dat",
        "pdf_gen_btn": "Generuj PDF",
        "pdf_download": "Pobierz Raport PDF",
        "pdf_no_data": "Brak danych w wybranym okresie.",
        
        "day_summary_header": "Podsumowanie dnia - wg Teamów",
        "pick_day": "Wybierz dzień",
        "no_reports_day": "Brak raportów z tego dnia.",
        "team_header": "👷 TEAM",
        
        "lbl_tab_summary": "📌 Podsumowanie",
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
        "chart_team": "Installations (Team)",
        "db_header": "Full Database Dump",
        "warn_no_work_month": "Brak raportów pracy dla tego pracownika w wybranym miesiącu.",
        
        "btn_init_db": "🔧 Wymuś inicjalizację bazy (init_db)",
        "msg_db_init": "Baza zainicjalizowana!"
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
        "pick_edit_date": "Berichtsdatum zur Bearbeitung wählen",
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
        "car_label": "Auto",
        "clean_form_btn": "🧹 Formular leeren",
        
        "err_start_time": "⚠️ Arbeitsbeginn nicht vor 06:00 Uhr!",
        "err_end_time": "⚠️ Arbeitsende am nächsten Tag nicht später als 05:00 Uhr!",
        "err_time_neg": "Arbeitszeit <= 0!",
        "err_worker_time": "Fehler bei den Mitarbeiterzeiten.",
        "err_add_one_worker": "Fügen Sie mindestens einen Mitarbeiter hinzu!",
        "lbl_next_day_info": "ℹ️ Arbeit endet am nächsten Tag: {} ({}h)",
        
        "lbl_hup_question": "Haben Sie den HÜP installiert?",
        "lbl_hup_type_select": "HÜP Typ wählen:",
        "opt_hup_yes": "Ja",
        "opt_hup_no": "Nein",
        
        "opt_hup_std": "Hüp",
        "opt_hup_multi": "MultiHüp",
        "opt_hup_change": "Austausch gegen MHüp",
        "opt_hup_rebuild": "Umbau MHüp",

        "err_break_b2b": "⚠️ B2B: Über 6h Arbeit sind min. 30 Min Pause erforderlich!",
        "err_break_std_6h": "⚠️ ArbZG: Über 6h Arbeit sind min. 30 Min Pause erforderlich!",
        "err_break_std_9h": "⚠️ ArbZG: Über 9h Arbeit sind min. 45 Min Pause erforderlich!",
        
        "section_1_title": "1. Wohnungsliste",
        "lbl_we_count": "Anzahl WE",
        "err_we_count": "⚠️ Bitte Anzahl WE ausfüllen, um zu speichern!",
        "warn_fill_obj_we": "Objektnummer und WE-Anzahl ausfüllen.",
        "msg_flats_updated": "{} Wohnungsnummern aktualisiert!",

        # Mobile View Translations (DE)
        "mobile_mode_toggle": "📱 Mobiler Modus (Große Tasten)",
        "select_flat_label": "Wohnung zur Bearbeitung wählen:",
        "flat_pos_label": "Pos.",
        "editing_info": "Bearbeitung:",
        "flat_number_input": "Wohnungsnummer",
        "preview_full_list": "Vorschau der gesamten Liste",
        "btn_auto_fill": "⚡ Wohnungsnummern automatisch ausfüllen",
        "btn_delete_report": "🗑️ Diesen Bericht löschen (Endgültig!)",
        "btn_download_excel": "📥 Excel-Bericht herunterladen (Farbig)",
        "lbl_summary_inline": "Zusammenfassung",
        
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
        "tab_emp": "👥 Mitarbeiter / Autos",
        "tab_db": "🗄️ Datenbank",
        "tab_users": "🔑 Konten / Users",
        "tab_pdf": "📄 PDF Berichte",
        "no_data": "Keine Daten in der Datenbank.",
        
        "emp_header": "Mitarbeiterverwaltung",
        "car_header": "Fahrzeugverwaltung",
        "add_emp_label": "Neuen Mitarbeiter hinzufügen",
        "add_car_label": "Neues Auto hinzufügen (Kennzeichen)",
        "lbl_contract_type": "Vertragsart",
        "opt_contract_b2b": "B2B (Selbstständig)",
        "opt_contract_std": "Arbeitsvertrag (ArbZG)",
        "add_emp_btn": "Hinzufügen",
        "add_car_btn": "Auto hinzufügen",
        "del_btn": "Entfernen",
        "current_emp_list": "Aktuelle Mitarbeiterliste:",
        "current_car_list": "Aktuelle Fahrzeugliste:",
        "emp_added": "Mitarbeiter hinzugefügt: {} ({})",
        "car_added": "Auto hinzugefügt: {}",
        "emp_deleted": "Mitarbeiter entfernt: {}",
        "msg_no_employees": "Keine Mitarbeiter.",
        "msg_no_cars": "Keine Autos im System.",
        
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
        "chart_team": "Installations (Team)",
        "db_header": "Full Database Dump",
        "warn_no_work_month": "Keine Arbeitsberichte für diesen Mitarbeiter im ausgewählten Monat.",

        "btn_init_db": "🔧 Datenbank initialisieren erzwingen (init_db)",
        "msg_db_init": "Datenbank initialisiert!"
    },
    "ENG": {
        "login_title": "🔐 Login - Fiber System",
        "user_label": "Login",
        "pass_label": "Password",
        "login_btn": "Sign In",
        "login_error": "Invalid credentials",
        "logout_btn": "Log out",
        "sidebar_login_info": "Logged in as:",
        "sidebar_admin_warning": "Admin Panel",
        
        "form_title": "🛠️ Work Report (DG)",
        "mode_select_label": "Select mode:",
        "mode_new": "📝 New Report",
        "mode_edit": "✏️ Edit Report",
        "select_report_label": "Select report to edit (Address)",
        "pick_edit_date": "Select report date to edit",
        "no_reports_to_edit": "No reports for your team on this date.",
        "edit_loaded_info": "Editing report ID: {}",
        "search_team_label": "Search reports for team:",
        
        "expander_data": "📍 Order Data",
        "date_label": "Report Date",
        "obj_num_label": "Object Number",
        "addr_label": "Address",
        "worker_header": "👤 Team & Work Time",
        "worker_select_label": "Select Worker",
        "add_worker_btn": "➕ Add next worker",
        "remove_worker_btn": "Remove last",
        "start_label": "Start",
        "break_label": "Break (min)",
        "end_label": "End",
        "car_label": "Car",
        "clean_form_btn": "🧹 Clear form",
        
        "err_start_time": "⚠️ Start time cannot be earlier than 06:00 AM!",
        "err_end_time": "⚠️ End time next day cannot be later than 05:00 AM!",
        "err_time_neg": "Work time <= 0!",
        "err_worker_time": "Worker hours error.",
        "err_add_one_worker": "Add at least one worker!",
        "lbl_next_day_info": "ℹ️ Work ends next day: {} ({}h)",
        
        "lbl_hup_question": "Did you install HÜP?",
        "lbl_hup_type_select": "Select HÜP type:",
        "opt_hup_yes": "Yes",
        "opt_hup_no": "No",
        
        "opt_hup_std": "Hüp",
        "opt_hup_multi": "MultiHüp",
        "opt_hup_change": "Exchange to MHüp",
        "opt_hup_rebuild": "Rebuild MHüp",
        
        "err_break_b2b": "⚠️ B2B: Over 6h work requires min. 30 min break!",
        "err_break_std_6h": "⚠️ Contract: Over 6h work requires min. 30 min break!",
        "err_break_std_9h": "⚠️ Contract: Over 9h work requires min. 45 min break!",
        
        "section_1_title": "1. Flats List",
        "lbl_we_count": "WE Count",
        "err_we_count": "⚠️ Please fill WE count to save!",
        "warn_fill_obj_we": "Fill 'Object Number' and 'WE Count'.",
        "msg_flats_updated": "Updated {} flat numbers!",
        
        "mobile_mode_toggle": "📱 Mobile Mode (Big Buttons)",
        "select_flat_label": "Select flat to edit:",
        "flat_pos_label": "Pos.",
        "editing_info": "Editing:",
        "flat_number_input": "Flat Number",
        "preview_full_list": "Full List Preview",
        "btn_auto_fill": "⚡ Auto-fill Flat Numbers",
        "btn_delete_report": "🗑️ Delete this report (Permanent!)",
        "btn_download_excel": "📥 Download Excel Report",
        "lbl_summary_inline": "Summary",

        "section_2_title": "2. Materials Used",
        "section_3_title": "3. Completion Status",
        
        "lbl_addr_finished": "Is address finished?",
        "lbl_mfr_ready": "Is MFR ready?",
        "lbl_reason": "Reason (Required):",
        "opt_yes": "Yes",
        "opt_no": "No",
        
        "save_btn": "💾 Save Report",
        "update_btn": "💾 Update Report",
        "save_success": "Saved! Team: {}. Gf-TA installed: {}",
        "update_success": "Report updated successfully!",
        "save_error": "Save error! Check times/fields.",
        
        "col_flat": "Flat (No)",
        "col_activation": "Activation",
        "tech_label": "Technology Type",
        
        "dash_title": "📊 Management Dashboard",
        "tab_day": "📅 Daily Report",
        "tab_month": "📈 Monthly Stats",
        "tab_emp": "👥 Employees / Cars",
        "tab_db": "🗄️ Full DB",
        "tab_users": "🔑 Accounts / Users",
        "tab_pdf": "📄 PDF Reports",
        "no_data": "No data in database.",
        
        "emp_header": "Employee Management",
        "car_header": "Fleet Management (Cars)",
        "add_emp_label": "Add new employee",
        "add_car_label": "Add car (License Plate)",
        "lbl_contract_type": "Contract Type",
        "opt_contract_b2b": "B2B (Self-employed)",
        "opt_contract_std": "Standard Contract",
        "add_emp_btn": "Add",
        "add_car_btn": "Add Car",
        "del_btn": "Remove",
        "current_emp_list": "Current Employee List:",
        "current_car_list": "Current Car List:",
        "emp_added": "Employee added: {} ({})",
        "car_added": "Car added: {}",
        "emp_deleted": "Employee removed: {}",
        "msg_no_employees": "No employees.",
        "msg_no_cars": "No cars.",
        
        "user_header": "System Accounts Management",
        "add_user_header": "Add new account",
        "lbl_u_name": "Name (e.g. Team 1)",
        "lbl_u_login": "Login",
        "lbl_u_pass": "Password",
        "lbl_u_role": "Role",
        "btn_add_user": "Create Account",
        "user_added_success": "Account '{}' created.",
        "user_exists_error": "Login '{}' is already taken.",
        "list_users_header": "Existing accounts:",
        "btn_del_user": "Delete",
        "user_deleted": "Account deleted: {}",

        "pdf_header": "Periodic Report Generator",
        "pdf_date_range": "Select date range",
        "pdf_gen_btn": "Generate PDF",
        "pdf_download": "Download PDF Report",
        "pdf_no_data": "No data in selected range.",
        
        "day_summary_header": "Daily Summary - by Teams",
        "pick_day": "Pick a day",
        "no_reports_day": "No reports for this day.",
        "team_header": "👷 TEAM",
        
        "lbl_tab_summary": "📌 Summary",
        "total_day_label": "∑ DAILY TOTAL:",

        "metric_hours": "🕒 Hours",
        "metric_we": "🏠 WE",
        "metric_gfta": "📦 Gf-TA",
        "metric_ont": "ONT modem",
        "metric_activations": "⚡ Activations",
        "metric_hup": "🔧 HÜP (Qty)",
        "metric_hup_status": "HÜP Status",
        "lbl_activated_list": "Activated ONT (Flat No):", 
        "lbl_gfta_list": "Installed Gf-TA (List):",
        "metric_kanal": "📏 Metalikanal 30x30",
        "metric_srv": "🖥️ Serveschrank",
        "metric_tech_used": "⚙️ Technology",
        "details_expander": "Report Details",
        
        "col_materials": "Materials",
        "col_status_addr": "Address Status",
        "col_status_mfr": "MFR Status",
        "lbl_workers": "Workers:",
        "lbl_worker_hours": "Work hours:",
        
        "month_header": "Monthly Analysis",
        "pick_month": "Select Month",
        "lbl_emp_select": "Select Employee",
        "lbl_total_hours": "Total Hours",
        "lbl_addr_context": "Address / Order",
        "chart_team": "Installations (Team)",
        "db_header": "Full Database Dump",
        "warn_no_work_month": "No reports for this employee in selected month.",
        
        "btn_init_db": "🔧 Force DB Init (init_db)",
        "msg_db_init": "Database initialized!"
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
    except (psycopg2.InterfaceError, psycopg2.OperationalError):
        # Połączenie zerwane - czyścimy cache i łączymy ponownie
        st.cache_resource.clear()
        conn = init_connection() 
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch == "all":
                return cur.fetchall()
            elif fetch == "one":
                return cur.fetchone()
            elif fetch == "none":
                conn.commit()
                return None

def init_db():
    # Tworzenie tabel w PostgreSQL
    
    # 1. Pracownicy
    run_query('''
        CREATE TABLE IF NOT EXISTS employees (
            name TEXT PRIMARY KEY,
            contract_type TEXT DEFAULT 'Contract'
        )
    ''', fetch="none")

    # 1.1 Samochody (Auta)
    run_query('''
        CREATE TABLE IF NOT EXISTS company_cars (
            plate TEXT PRIMARY KEY
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

def add_car(plate):
    try:
        run_query("INSERT INTO company_cars (plate) VALUES (%s)", (plate,), fetch="none")
        return True
    except: return False

def remove_car(plate):
    run_query("DELETE FROM company_cars WHERE plate = %s", (plate,), fetch="none")

def get_cars():
    data = run_query("SELECT plate FROM company_cars ORDER BY plate", fetch="all")
    if not data: return []
    return [d['plate'] for d in data]

def get_reports_for_editor(team_name, date_obj, role=None):
    # Pobiera raporty danego teamu z danej daty (do edycji przez montera)
    d_str = date_obj.strftime("%Y-%m-%d") if isinstance(date_obj, (datetime, pd.Timestamp)) else str(date_obj)
    
    # FIX: Używamy LIKE + % aby złapać daty zapisane jako '2024-01-01T00:00:00' (ISO) oraz '2024-01-01'
    date_pattern = d_str + "%"

    # 1. Jeśli to admin, pokazujemy WSZYSTKIE raporty z tego dnia
    if role == 'admin':
        data = run_query("SELECT * FROM reports WHERE date LIKE %s", (date_pattern,), fetch="all")
    else:
        # 2. Dla zwykłego usera: Szukamy "miękko" i po dacie LIKE
        data = run_query("SELECT * FROM reports WHERE TRIM(team_name) ILIKE TRIM(%s) AND date LIKE %s", (team_name, date_pattern), fetch="all")
        
    return pd.DataFrame(data) if data else pd.DataFrame()

def save_report_to_db(date, obj_num, address, team, we, w_json, m_json, wt_json, af, ar, mf, mr, og, ox, gs, act, tech, hs):
    # Data conversion just in case
    d_str = date.strftime("%Y-%m-%d") if isinstance(date, (datetime, pd.Timestamp)) else str(date)
    run_query('''
        INSERT INTO reports (
            date, object_num, address, team_name, we_count, workers_json, materials_json, work_table_json,
            address_finished, address_finished_reason, mfr_ready, mfr_ready_reason,
            ont_gpon_sum, ont_xgs_sum, gfta_sum, activation_sum, technology_type, hup_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        d_str, obj_num, address, team, we, w_json, m_json, wt_json, af, ar, mf, mr, og, ox, gs, act, tech, hs
    ), fetch="none")

def update_report_in_db(rep_id, date, obj_num, address, team, we, w_json, m_json, wt_json, af, ar, mf, mr, og, ox, gs, act, tech, hs):
    d_str = date.strftime("%Y-%m-%d") if isinstance(date, (datetime, pd.Timestamp)) else str(date)
    # FIX: Rzutowanie na int(rep_id) aby uniknąć problemów z numpy.int64
    run_query('''
        UPDATE reports SET
            date=%s, object_num=%s, address=%s, team_name=%s, we_count=%s, workers_json=%s, materials_json=%s, work_table_json=%s,
            address_finished=%s, address_finished_reason=%s, mfr_ready=%s, mfr_ready_reason=%s,
            ont_gpon_sum=%s, ont_xgs_sum=%s, gfta_sum=%s, activation_sum=%s, technology_type=%s, hup_status=%s
        WHERE id=%s
    ''', (
        d_str, obj_num, address, team, we, w_json, m_json, wt_json, af, ar, mf, mr, og, ox, gs, act, tech, hs, int(rep_id)
    ), fetch="none")

def delete_report(report_id):
    # FIX: Rzutowanie na int() aby uniknąć problemów z numpy.int64
    run_query("DELETE FROM reports WHERE id=%s", (int(report_id),), fetch="none")

# Dodajemy dekorator cache_data
# ttl=60 oznacza: "pamiętaj te dane przez 60 sekund, potem pobierz świeże"
@st.cache_data(ttl=60)
def load_all_data():
    data = run_query("SELECT * FROM reports", fetch="all")
    return pd.DataFrame(data) if data else pd.DataFrame()

def get_localized_hup_status(saved_status):
    """
    Tłumaczy zapisany w bazie status HÜP na aktualny język interfejsu.
    Obsługuje przypadki, gdy w bazie jest zapisane po PL, a oglądamy po DE.
    """
    if not saved_status:
        return "-"
        
    no_variants = ["Nie", "Nein", "No"]
    change_variants = ["Wymiana na MHüp", "Austausch gegen MHüp", "Exchange to MHüp", "Wymiana na M-Hüp", "Exchange to M-Hüp"]
    std_variants = ["Hüp"]
    multi_variants = ["MultiHüp"]
    rebuild_variants = ["Przebudowa MHüp", "Umbau MHüp", "Rebuild MHüp"]
    m_old_variants = ["M-Hüp"] # Stara kompatybilność

    target_key = None
    
    if saved_status in no_variants:
        target_key = "opt_hup_no"
    elif saved_status in change_variants:
        target_key = "opt_hup_change"
    elif saved_status in std_variants:
        target_key = "opt_hup_std"
    elif saved_status in multi_variants or saved_status in m_old_variants:
        target_key = "opt_hup_multi"
    elif saved_status in rebuild_variants:
        target_key = "opt_hup_rebuild"
    elif saved_status in ["Tak", "Ja", "Yes"]: 
        target_key = "opt_hup_yes"

    if target_key:
        return get_text(target_key)
    
    return saved_status

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
# init_db()

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

# --- FUNKCJA POMOCNICZA (WKLEJ TO NAD MONTER_VIEW) ---
def get_val(key, default=None):
    """Bezpieczne pobieranie wartości z st.session_state"""
    return st.session_state.get(key, default)

# --- FIX: Funkcja do czyszczenia stanu formularza ---
def reset_form_state():
    """Czyści zmienne sesyjne formularza"""
    st.session_state['workers'] = []
    if 'current_work_df' in st.session_state:
        del st.session_state['current_work_df']
    if 'last_loaded_id' in st.session_state:
        del st.session_state['last_loaded_id']
    if 'last_loaded_report_id' in st.session_state:
        del st.session_state['last_loaded_report_id']
    
    # Czyścimy materiały
    for m in MATERIALS:
        k = f"mat_{m}"
        if k in st.session_state:
            del st.session_state[k]

def monter_view():
    disp = st.session_state.get('display_name') or st.session_state['username']
    user_role = st.session_state.get('role') # Pobieramy rolę (monter/admin)
    
    st.sidebar.info(f"{get_text('sidebar_login_info')} {disp}")
    if st.sidebar.button(get_text("logout_btn")): logout()
    
    st.title(get_text("form_title"))

    # Wybór trybu
    mode = st.radio(get_text("mode_select_label"), [get_text("mode_new"), get_text("mode_edit")], horizontal=True)
    
    # --- FIX: Obsługa czyszczenia przy zmianie trybu ---
    if 'last_mode' not in st.session_state:
        st.session_state['last_mode'] = mode
    
    if st.session_state['last_mode'] != mode:
        reset_form_state()
        st.session_state['last_mode'] = mode
        st.rerun()
    # ---------------------------------------------------

    loaded_report = None
    current_edit_id = None
    
    # Automatyczne ustalanie nazwy zespołu do zapisu/wyszukiwania (dg_teamX)
    current_team_db_name = disp
    if "Team" in disp or "team" in disp:
        # Jeśli nie zaczyna się od dg_, naprawiamy
        if not disp.lower().startswith("dg_"):
            clean_name = disp.lower().replace(" ", "")
            if clean_name.startswith("team"):
                current_team_db_name = "dg_" + clean_name

    # --- ŁADOWANIE DO EDYCJI ---
    if mode == get_text("mode_edit"):
        
        # 1. Wybór daty
        edit_date = st.date_input(get_text("pick_edit_date"), datetime.now())
        
        # Automatyczne szukanie (bez inputa)
        search_team = current_team_db_name
        
        # 2. Pobieramy raporty - przekazujemy rolę
        # Jeśli jesteś adminem -> zobaczysz wszystko
        # Jeśli monterem -> zobaczysz wg search_team (z ignorowaniem wielkości liter)
        reports = get_reports_for_editor(search_team, edit_date, role=user_role)
        
        if not reports.empty:
            opts = reports.index.tolist()
            # Wyświetlamy w liście: Adres (Nr Obiektu)
            labels = [f"{row['address']} ({row['object_num']})" for i, row in reports.iterrows()]
            sel_idx = st.selectbox(get_text("select_report_label"), opts, format_func=lambda x: labels[opts.index(x)])
            loaded_report = reports.loc[sel_idx]
            current_edit_id = loaded_report['id']
            st.info(get_text("edit_loaded_info").format(current_edit_id))
        else:
            st.warning(get_text("no_reports_to_edit"))
            # --- FIX: Reset formularza gdy brak raportów (żeby nie było "duchów") ---
            reset_form_state()
            # ------------------------------------------------------------------------

    # --- DANE ZLECENIA ---
    with st.expander(get_text("expander_data"), expanded=True):
        col1, col2 = st.columns(2)
        def_date = datetime.now()
        if loaded_report is not None:
            def_date = pd.to_datetime(loaded_report['date']).to_pydatetime()
            
        report_date = col1.date_input(get_text("date_label"), def_date)
        obj_num = col2.text_input(get_text("obj_num_label"), value=loaded_report['object_num'] if loaded_report is not None else "")
        address = st.text_input(get_text("addr_label"), value=loaded_report['address'] if loaded_report is not None else "")
        
        # --- POWRÓT DO STATYCZNEGO PODPISU TEAMU ---
        # Nie pozwalamy zmieniać teamu, bo to powoduje zamieszanie. System wie kim jesteś.
        # Chyba że wczytaliśmy raport (wtedy pokazujemy właściciela raportu)
        
        team_display_val = current_team_db_name
        if loaded_report is not None:
            team_display_val = loaded_report['team_name']
            
        st.caption(f"Team (DB): {team_display_val}")
        # Przekazujemy do zapisu to, co jest w raporcie LUB to kim jesteśmy (znormalizowane)
        team_name_to_save = team_display_val
        # -------------------------------------------

    # --- PRACOWNICY ---
    st.subheader(get_text("worker_header"))
    
    # --- LOGIKA ŁADOWANIA DANYCH DO FORMULARZA (WORKERS + MATERIALS) ---
    if 'workers' not in st.session_state or (loaded_report is not None and st.session_state.get('last_loaded_id') != current_edit_id):
        # Reset domyślny
        st.session_state['workers'] = []
        
        if loaded_report is not None:
            # 1. Ładowanie pracowników
            if loaded_report['workers_json']:
                st.session_state['workers'] = json.loads(loaded_report['workers_json'])
            
            # 2. Ładowanie materiałów (FIX: WYMUSZENIE AKTUALIZACJI STANU)
            # Musimy to zrobić tutaj, zanim formularz materiałów się wyrenderuje
            loaded_mats_dict = {}
            if loaded_report['materials_json']:
                try: loaded_mats_dict = json.loads(loaded_report['materials_json'])
                except: pass
            
            # Przepisujemy wartości do session_state, żeby inputy się odświeżyły
            for m in MATERIALS:
                st.session_state[f"mat_{m}"] = loaded_mats_dict.get(m, 0)
                
            st.session_state['last_loaded_id'] = current_edit_id
        
        elif 'workers' not in st.session_state:
             st.session_state['workers'] = []
    # -------------------------------------------------------------------
            
    # Przycisk awaryjnego czyszczenia
    if st.button(get_text("clean_form_btn"), type="secondary"):
        reset_form_state()
        st.rerun()
        
    # --- Pobieranie listy aut ---
    car_list = ["-"] + get_cars()

    for i, w in enumerate(st.session_state['workers']):
        with st.expander(f"👷 {w['name']}", expanded=True):
            # Zmieniony układ na 4 kolumny (dodano auto)
            c1, c2, c3, c4 = st.columns(4)
            w['start'] = c1.text_input(get_text("start_label"), value=w.get('start', '08:00'), key=f"s_{i}")
            
            # --- ZABEZPIECZENIE PRZED BŁĘDNĄ/PUSTĄ PRZERWĄ ---
            raw_break = w.get('break')
            try:
                safe_break = int(raw_break) if raw_break is not None else 0
            except (ValueError, TypeError):
                safe_break = 0
            if safe_break < 0: safe_break = 0
            
            w['break'] = c2.number_input(get_text("break_label"), min_value=0, step=5, value=safe_break, key=f"b_{i}")
            # -------------------------------------------
            
            w['end'] = c3.text_input(get_text("end_label"), value=w.get('end', '16:00'), key=f"e_{i}")
            
            # --- NOWE POLE: AUTO ---
            current_car = w.get('car', '-')
            # Jeśli auto z raportu nie istnieje już w bazie, dodaj je do listy tymczasowo
            if current_car not in car_list: car_list.append(current_car)
            
            w['car'] = c4.selectbox(get_text("car_label"), car_list, index=car_list.index(current_car), key=f"c_{i}")

    c_add, c_rem = st.columns(2)
    emp_map = get_employees_map()
    new_worker_name = c_add.selectbox(get_text("worker_select_label"), [""] + list(emp_map.keys()))
    
    if c_add.button(get_text("add_worker_btn")) and new_worker_name:
        st.session_state['workers'].append({
            "name": new_worker_name, 
            "type": emp_map[new_worker_name],
            "start": "08:00", "end": "16:00", "break": 30, "car": "-"
        })
        st.rerun()

    if st.session_state['workers'] and c_rem.button(get_text("remove_worker_btn")):
        st.session_state['workers'].pop()
        st.rerun()

    st.write("---")

    # --- HÜP (NOWA LOGIKA 2-ETAPOWA) ---
    st.write(f"**{get_text('lbl_hup_question')}**")
    
    # 1. Sprawdzamy stan początkowy (dla edycji)
    # Domyślne wartości
    hup_yes_no_idx = 1 # Domyślnie NIE (index 1)
    specific_type_idx = 0 # Domyślnie pierwszy z listy typów
    
    # Lista typów do wyboru w kroku 2
    hup_types = [
        get_text("opt_hup_std"),      # Hüp
        get_text("opt_hup_multi"),    # MultiHüp
        get_text("opt_hup_change"),   # Wymiana na MHüp
        get_text("opt_hup_rebuild")   # Przebudowa MHüp
    ]
    
    if loaded_report is not None:
        raw_hup = loaded_report.get('hup_status', 'Nie')
        # Lista wariantów "NIE" (z bazy)
        no_variants = ["Nie", "Nein", "No"]
        
        if raw_hup in no_variants:
            hup_yes_no_idx = 1 # NIE
        else:
            hup_yes_no_idx = 0 # TAK (bo coś jest wybrane)
            # Próbujemy dopasować, co dokładnie było wybrane, żeby ustawić selectbox
            # Musimy mapować nazwy z bazy na nazwy z listy hup_types (te są z get_text)
            # Ale uwaga: lista hup_types jest tłumaczona! A w bazie może być po polsku.
            # Najlepiej sprawdzić czy raw_hup pasuje do którejś opcji.
            
            # Spróbujmy znaleźć raw_hup w liście (zakładając że język się nie zmienił)
            if raw_hup in hup_types:
                specific_type_idx = hup_types.index(raw_hup)
            else:
                # Jeśli nie znaleziono (np. zmiana języka), to fallback na helper
                translated_hup = get_localized_hup_status(raw_hup)
                if translated_hup in hup_types:
                    specific_type_idx = hup_types.index(translated_hup)

    # KROK 1: Pytanie TAK/NIE
    hup_installed = st.radio(
        get_text("lbl_hup_question"),
        [get_text("opt_hup_yes"), get_text("opt_hup_no")],
        index=hup_yes_no_idx,
        key="hup_step1",
        label_visibility="collapsed",
        horizontal=True
    )
    
    final_hup_status = "Nie" # Domyślna wartość do zapisu
    
    # KROK 2: Jeśli TAK, to jaki typ?
    if hup_installed == get_text("opt_hup_yes"):
        st.write(get_text("lbl_hup_type_select"))
        selected_type = st.selectbox(
            get_text("lbl_hup_type_select"),
            hup_types,
            index=specific_type_idx,
            label_visibility="collapsed",
            key="hup_step2"
        )
        final_hup_status = selected_type
    else:
        final_hup_status = "Nie" # Zapisujemy "Nie" do bazy

    st.write("---")

    # --- SEKCJA 1: MIESZKANIA ---
    st.subheader(get_text("section_1_title"))
    we_count = st.number_input(get_text("lbl_we_count"), min_value=0, step=1, value=get_val('we_count', loaded_report['we_count'] if loaded_report is not None else 0))
    
    if 'current_work_df' not in st.session_state or st.session_state.get('last_loaded_report_id') != current_edit_id:
        if loaded_report is not None and loaded_report['work_table_json']:
            loaded_df = pd.DataFrame(json.loads(loaded_report['work_table_json']))
            if len(loaded_df) < 20:
                missing = 20 - len(loaded_df)
                ext = pd.DataFrame({"Wohnung": ["" for _ in range(missing)], "Gfta": [False]*missing, "Ont gpon": [False]*missing, "Ont xgs": [False]*missing, "Patch Ont": [False]*missing, "Activation": [False]*missing})
                loaded_df = pd.concat([loaded_df, ext], ignore_index=True)
            st.session_state['current_work_df'] = loaded_df
        else:
            st.session_state['current_work_df'] = pd.DataFrame({
                "Wohnung": [str(i+1) for i in range(20)], 
                "Gfta": [False]*20, "Ont gpon": [False]*20, "Ont xgs": [False]*20, "Patch Ont": [False]*20, "Activation": [False]*20
            })
        st.session_state['last_loaded_report_id'] = current_edit_id

    if st.button(get_text("btn_auto_fill")):
        if obj_num and we_count > 0:
            df = st.session_state['current_work_df']
            limit = min(we_count, 20)
            for i in range(limit):
                df.at[i, 'Wohnung'] = f"{obj_num}-{i+1}"
            st.session_state['current_work_df'] = df
            st.success(get_text("msg_flats_updated").format(limit))
            st.rerun()
        else:
            st.warning(get_text("warn_fill_obj_we"))

    use_mobile_view = st.toggle(get_text("mobile_mode_toggle"), value=True)

    if use_mobile_view:
        df = st.session_state['current_work_df']
        opts = df.index.tolist()
        lbls = [f"{get_text('flat_pos_label')}: {i+1} | Nr: {row['Wohnung']}" for i, row in df.iterrows()]
        sel_idx = st.selectbox(get_text("select_flat_label"), opts, format_func=lambda x: lbls[x])
        
        st.info(f"{get_text('editing_info')} **{df.at[sel_idx, 'Wohnung']}**")
        
        c_m1, c_m2 = st.columns(2)
        new_flat = c_m1.text_input(get_text("flat_number_input"), value=df.at[sel_idx, 'Wohnung'])
        if new_flat != df.at[sel_idx, 'Wohnung']:
            df.at[sel_idx, 'Wohnung'] = new_flat
            st.rerun()

        st.write("---")
        c_t1, c_t2 = st.columns(2)
        def up_val(col): st.session_state['current_work_df'].at[sel_idx, col] = st.session_state[f"mob_{sel_idx}_{col}"]
        
        with c_t1:
            st.toggle("Gf-TA", value=df.at[sel_idx, 'Gfta'], key=f"mob_{sel_idx}_Gfta", on_change=up_val, args=("Gfta",))
            st.toggle("ONT GPON", value=df.at[sel_idx, 'Ont gpon'], key=f"mob_{sel_idx}_Ont gpon", on_change=up_val, args=("Ont gpon",))
            st.toggle("Activation", value=df.at[sel_idx, 'Activation'], key=f"mob_{sel_idx}_Activation", on_change=up_val, args=("Activation",))
        with c_t2:
            st.toggle("Patch ONT", value=df.at[sel_idx, 'Patch Ont'], key=f"mob_{sel_idx}_Patch Ont", on_change=up_val, args=("Patch Ont",))
            st.toggle("ONT XGS", value=df.at[sel_idx, 'Ont xgs'], key=f"mob_{sel_idx}_Ont xgs", on_change=up_val, args=("Ont xgs",))
        
        st.write("---")
        with st.expander(get_text("preview_full_list")):
            st.dataframe(df, hide_index=True)
        edited_df = df
    else:
        edited_df = st.data_editor(
            st.session_state['current_work_df'], num_rows="fixed", width='stretch',
            column_config={"Wohnung": st.column_config.TextColumn(get_text("col_flat"), width="small"), "Activation": st.column_config.CheckboxColumn(get_text("col_activation"), default=False)},
            key="desktop_editor"
        )
        st.session_state['current_work_df'] = edited_df

    gfta_sum = edited_df['Gfta'].sum()
    ont_gpon_sum = edited_df['Ont gpon'].sum()
    ont_xgs_sum = edited_df['Ont xgs'].sum()
    activation_sum = edited_df['Activation'].sum()
    
    st.info(f"{get_text('lbl_summary_inline')}: Gf-TA: {gfta_sum}, ONT: {ont_gpon_sum + ont_xgs_sum}, Akt: {activation_sum}")
    st.write("---")

    # --- WYBÓR TECHNOLOGII ---
    # Ustalanie domyślnej wartości
    def_tech_idx = 0
    if loaded_report is not None and loaded_report['technology_type'] in TECHNOLOGIES:
        def_tech_idx = TECHNOLOGIES.index(loaded_report['technology_type'])
    
    technology_type = st.selectbox(get_text("tech_label"), TECHNOLOGIES, index=def_tech_idx)
    st.write("---")

    # --- SEKCJA 2: MATERIAŁY ---
    st.subheader(get_text("section_2_title"))
    with st.container(border=True):
        cols = st.columns(2)
        # UWAGA: Tu pobieramy wartości już z session_state (które zaktualizowaliśmy wyżej)
        # dzięki temu inputy będą miały poprawne wartości.
        for i, mat in enumerate(MATERIALS):
            col = cols[i % 2]
            unit = MATERIALS_UNITS.get(mat, "")
            label = f"{mat} [{unit}]" if unit else mat
            
            # Pobieramy bieżącą wartość ze stanu (którą właśnie wymusiliśmy wyżej)
            current_val = st.session_state.get(f"mat_{mat}", 0)
            
            col.number_input(label, min_value=0, step=1, key=f"mat_{mat}", value=current_val)

    # --- SEKCJA 3: STATUS (Reszta) ---
    st.subheader(get_text("section_3_title"))
    
    c3a, c3b = st.columns(2)
    af_val = loaded_report['address_finished'] if loaded_report is not None else "Nie"
    mf_val = loaded_report['mfr_ready'] if loaded_report is not None else "Nie"
    
    addr_finished = c3a.selectbox(get_text("lbl_addr_finished"), [get_text("opt_yes"), get_text("opt_no")], index=0 if af_val == "Tak" else 1)
    addr_reason = ""
    if addr_finished == get_text("opt_no"):
        addr_reason = c3a.text_input(get_text("lbl_reason"), value=loaded_report['address_finished_reason'] if loaded_report is not None else "", key="ar")

    mfr_ready = c3b.selectbox(get_text("lbl_mfr_ready"), [get_text("opt_yes"), get_text("opt_no")], index=0 if mf_val == "Tak" else 1)
    mfr_reason = ""
    if mfr_ready == get_text("opt_no"):
        mfr_reason = c3b.text_input(get_text("lbl_reason"), value=loaded_report['mfr_ready_reason'] if loaded_report is not None else "", key="mr")

    st.write("---")
    
    # --- ZAPIS ---
    btn_label = get_text("update_btn") if mode == get_text("mode_edit") else get_text("save_btn")
    
    if st.button(btn_label, type="primary"):
        # --- WALIDACJA WE (BRAMKA) ---
        if we_count == 0:
            st.error(get_text("err_we_count"))
        # -----------------------------
        elif not st.session_state['workers']:
            st.error(get_text("err_add_one_worker"))
        else:
            can_save = True
            final_workers = []
            
            for w in st.session_state['workers']:
                try:
                    s = datetime.strptime(w['start'], "%H:%M")
                    e = datetime.strptime(w['end'], "%H:%M")
                    
                    # --- PRZYWRÓCONA WALIDACJA (RAMY CZASOWE) ---
                    # 1. Start nie może być wcześniej niż 06:00
                    start_limit = datetime.strptime("06:00", "%H:%M")
                    if s < start_limit:
                         st.error(f"❌ {w['name']}: {get_text('err_start_time')}")
                         can_save = False

                    # Logika zmiany dnia
                    if e < s:
                        e += timedelta(days=1)
                        # 2. Jeśli zmiana dnia, koniec nie później niż 05:00 rano
                        # Tworzymy limit 05:00 następnego dnia
                        end_limit_next_day = datetime.strptime("05:00", "%H:%M") + timedelta(days=1)
                        if e > end_limit_next_day:
                            st.error(f"❌ {w['name']}: {get_text('err_end_time')}")
                            can_save = False

                    diff = (e - s).total_seconds() / 3600.0
                    break_time = w['break']
                    calc_hours = diff - (break_time / 60.0)
                    
                    if calc_hours <= 0:
                        st.error(f"❌ {w['name']}: {get_text('err_time_neg')}")
                        can_save = False
                    
                    # --- WALIDACJA PRZERW WG UMOWY ---
                    # Pobieramy typ umowy (domyślnie 'Contract' jeśli brak w bazie)
                    c_type = emp_map.get(w['name'], 'Contract') 
                    
                    # Warunki:
                    # 1. B2B i Contract > 6h pracy -> min 30 min przerwy
                    if calc_hours > 6 and break_time < 30:
                        st.error(f"❌ {w['name']} ({c_type}): {get_text('err_break_b2b') if c_type == 'B2B' else get_text('err_break_std_6h')}")
                        can_save = False
                    
                    # 2. Tylko Contract > 9h pracy -> min 45 min przerwy
                    if c_type != 'B2B' and calc_hours > 9 and break_time < 45:
                        st.error(f"❌ {w['name']} (Umowa): {get_text('err_break_std_9h')}")
                        can_save = False
                    # ---------------------------------

                    w_data = w.copy()
                    w_data['calculated_hours'] = round(calc_hours, 2)
                    s_str = w['start']
                    e_str = w['end']
                    if e.date() > s.date(): e_str = f"{e_str} (+1)"
                    w_data['display_start'] = s_str
                    w_data['display_end'] = e_str
                    final_workers.append(w_data)
                except:
                    st.error(get_text("err_worker_time"))
                    can_save = False

            if can_save:
                w_json = json.dumps(final_workers)
                
                mats = {}
                for m in MATERIALS:
                    val = st.session_state.get(f"mat_{m}", 0)
                    if val > 0: mats[m] = val
                m_json = json.dumps(mats)
                
                wt_json = "[]"
                if 'current_work_df' in st.session_state:
                    wt_json = st.session_state['current_work_df'].to_json(orient="records")

                # Tutaj używamy wartości obliczonej w nowym bloku HÜP
                hup_s = final_hup_status

                af_db = "Tak" if addr_finished == get_text("opt_yes") else "Nie"
                mf_db = "Tak" if mfr_ready == get_text("opt_yes") else "Nie"

                if mode == get_text("mode_new"):
                    save_report_to_db(report_date, obj_num, address, team_name_to_save, we_count, w_json, m_json, wt_json, af_db, addr_reason, mf_db, mfr_reason, int(ont_gpon_sum), int(ont_xgs_sum), int(gfta_sum), int(activation_sum), technology_type, hup_s)
                    st.success(get_text("save_success").format(team_name_to_save, int(gfta_sum)))
                    
                    # --- FIX: CZYSZCZENIE PO ZAPISIE ---
                    reset_form_state()
                    # -----------------------------------
                    
                    time_lib.sleep(1)
                    st.rerun()
                else:
                    update_report_in_db(current_edit_id, report_date, obj_num, address, team_name_to_save, we_count, w_json, m_json, wt_json, af_db, addr_reason, mf_db, mfr_reason, int(ont_gpon_sum), int(ont_xgs_sum), int(gfta_sum), int(activation_sum), technology_type, hup_s)
                    st.success(get_text("update_success"))
                    
                    # --- FIX: CZYSZCZENIE PO AKTUALIZACJI ---
                    reset_form_state()
                    # ----------------------------------------
                    
                    time_lib.sleep(1)
                    st.rerun()

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
            
            # Filtrowanie danych dla wybranego dnia
            d_df = df[df['date'].dt.date == sel_day]
            
            if d_df.empty:
                st.info(get_text("no_reports_day"))
            else:
                # Iteracja po zespołach
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
                        
                        # Obliczanie sum dziennych dla zespołu
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

                        # Przygotowanie zakładek
                        report_indices = team_data.index.tolist()
                        tab_labels = [get_text("lbl_tab_summary")] 
                        for idx in report_indices:
                            row = team_data.loc[idx]
                            label = f"{row['address']} ({row['object_num']})"
                            if not label or label == " ()": label = f"Raport #{row['id']}"
                            tab_labels.append(label)
                        
                        tabs = st.tabs(tab_labels)
                        
                        for i, tab in enumerate(tabs):
                            with tab:
                                if i == 0:
                                    # PODSUMOWANIE ZESPOŁU
                                    st.caption(f"**{get_text('total_day_label')}**")
                                    cols_sum = st.columns(6)
                                    cols_sum[0].metric(get_text("metric_hours"), f"{daily_total_hours:.1f} h")
                                    cols_sum[1].metric(get_text("metric_we"), daily_total_we)
                                    cols_sum[2].metric(get_text("metric_gfta"), daily_total_gfta)
                                    cols_sum[3].metric(get_text("metric_ont"), daily_total_ont)
                                    cols_sum[4].metric(get_text("metric_activations"), daily_total_activations)
                                    cols_sum[5].metric(get_text("metric_hup"), daily_hup_count)
                                else:
                                    # SZCZEGÓŁY POJEDYNCZEGO RAPORTU
                                    row_idx = report_indices[i-1]
                                    row = team_data.loc[row_idx]
                                    report_db_id = row['id']
                                    
                                    report_hours = 0
                                    workers_details_list = []
                                    if row['workers_json']:
                                        try:
                                            w_data = json.loads(row['workers_json'])
                                            for w in w_data:
                                                report_hours += w.get('calculated_hours', 0)
                                                # Pobieramy auto
                                                car_used = w.get('car', '-')
                                                
                                                if 'display_start' in w and 'display_end' in w:
                                                    workers_details_list.append(f"{w['name']} {w['display_start']} - {w['display_end']} ({w['break']} min) [Auto: {car_used}]")
                                                else:
                                                    s_time = str(w['start'])[:5]
                                                    e_time = str(w['end'])[:5]
                                                    workers_details_list.append(f"{w['name']} {s_time}-{e_time} ({w['break']}) [Auto: {car_used}]")
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
                                    # Łączone WE / Gf-TA
                                    we_label = get_text("metric_we")
                                    c2.metric(f"{we_label} / Gf-TA", f"{r_we} / {r_gfta}")
                                    
                                    c3.metric(metric_label_mat, f"{r_mat_val} {metric_unit_mat}")
                                    # FIX: ZAMIANA METRIC NA MARKDOWN (żeby tekst się mieścił)
                                    with c4:
                                        st.caption(get_text("metric_hup_status"))
                                        st.markdown(f"**{r_hup_stat}**")

                                    st.divider()
                                    st.caption(f"{get_text('metric_tech_used')}: **{r_tech}**")

                                    if workers_details_list:
                                        st.write(f"**{get_text('lbl_worker_hours')}**")
                                        for w_det in workers_details_list:
                                            st.write(f"• {w_det}") 

                                    st.divider()

                                    # Listy mieszkań (Aktywacje i Gf-TA)
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
                                        
                                    # Tabelka ze statusami
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
                                    
                                    # PRZYCISK USUWANIA RAPORTU
                                    st.write("---")
                                    if st.button(get_text("btn_delete_report"), key=f"del_btn_{report_db_id}", type="primary"):
                                        delete_report(report_db_id)
                                        st.warning("Raport usunięty / Bericht gelöscht / Report deleted")
                                        st.rerun()

    # --- TAB 2: MIESIĘCZNY ---
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
                        target = next((w for w in w_list if w['name'] == sel_emp), None)
                        if target:
                            s_disp = target.get('display_start', str(target.get('start', ''))[:5])
                            e_disp = target.get('display_end', str(target.get('end', ''))[:5])
                            
                            log_entry = {
                                "Data": row['date'],
                                "Start": s_disp,
                                "Stop": e_disp,
                                "Przerwa": target.get('break', 0),
                                "Auto": target.get('car', '-'),
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
                log_df['Data'] = pd.to_datetime(log_df['Data'])
                log_df = log_df.sort_values('Data')
                log_df['Data'] = log_df['Data'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    log_df,
                    column_config={
                        "Data": st.column_config.DateColumn(get_text("date_label"), format="YYYY-MM-DD"),
                        "Start": st.column_config.TextColumn(get_text("start_label")),
                        "Stop": st.column_config.TextColumn(get_text("end_label")),
                        "Przerwa": st.column_config.TextColumn(get_text("break_label")),
                        "Auto": st.column_config.TextColumn(get_text("car_label")),
                        "Godziny": st.column_config.NumberColumn(get_text("metric_hours"), format="%.2f"),
                        "Adres": st.column_config.TextColumn(get_text("lbl_addr_context"), width="medium")
                    },
                    hide_index=True,
                    width='stretch'
                )
            else:
                st.warning(get_text("warn_no_work_month"))

            st.divider()
            st.subheader(get_text("chart_team"))
            if not m_df.empty:
                team_stats = m_df.groupby('team_name')[['gfta_sum', 'ont_gpon_sum', 'ont_xgs_sum']].sum().reset_index()
                st.bar_chart(team_stats.set_index('team_name'))

    # --- TAB 3: PRACOWNICY / AUTA ---
    with t3:
        st.subheader(get_text("emp_header"))
        c_f, c_l = st.columns(2)
        with c_f.form("add_e"):
            nm = st.text_input(get_text("add_emp_label"))
            ct = st.radio(get_text("lbl_contract_type"), ["B2B", "Contract"])
            if st.form_submit_button(get_text("add_emp_btn")) and nm: 
                if add_employee(nm, ct): st.success(get_text("emp_added").format(nm, ct)); st.rerun()
        
        with c_l:
            st.caption(get_text("current_emp_list"))
            emp_map = get_employees_map()
            if emp_map:
                for name, c_type in emp_map.items():
                    c1, c2 = st.columns([4,1])
                    c_label = "B2B" if c_type == "B2B" else "Umowa"
                    c1.write(f"👤 **{name}** [{c_label}]")
                    if c2.button(get_text("del_btn"), key=f"d_{name}"): 
                        remove_employee(name)
                        st.rerun()
            else:
                st.info(get_text("msg_no_employees"))

        st.divider()
        st.subheader(get_text("car_header"))
        c_c1, c_c2 = st.columns(2)
        with c_c1.form("add_c"):
            pl = st.text_input(get_text("add_car_label"))
            if st.form_submit_button(get_text("add_car_btn")) and pl:
                if add_car(pl): st.success(get_text("car_added").format(pl)); st.rerun()
        
        with c_c2:
            st.caption(get_text("current_car_list"))
            cars = get_cars()
            if cars:
                for car in cars:
                    cc1, cc2 = st.columns([4,1])
                    cc1.write(f"🚗 **{car}**")
                    if cc2.button(get_text("del_btn"), key=f"dc_{car}"):
                        remove_car(car)
                        st.rerun()
            else:
                st.info(get_text("msg_no_cars"))

    # --- TAB 4: BAZA DANYCH ---
    with t4:
        st.dataframe(df)
        st.divider()
        if st.button(get_text("btn_init_db")):
            init_db()
            st.success(get_text("msg_db_init"))

    # --- TAB 5: UŻYTKOWNICY SYSTEMU ---
    with t5:
        with st.expander(get_text("add_user_header")):
            with st.form("au"):
                u, p = st.text_input(get_text("lbl_u_login")), st.text_input(get_text("lbl_u_pass"), type="password")
                r, d = st.selectbox(get_text("lbl_u_role"), ["monter", "admin"]), st.text_input(get_text("lbl_u_name"))
                if st.form_submit_button(get_text("btn_add_user")) and u and p:
                    if add_system_user(u, p, r, d): st.success(get_text("user_added_success").format(u)); st.rerun()
                    else: st.error(get_text("user_exists_error").format(u))
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
            if f_df.empty: st.warning(get_text("pdf_no_data"))
            else:
                st.download_button(get_text("pdf_download"), create_pdf_report(f_df, sd, ed), f"rap_{sd}_{ed}.pdf", "application/pdf")

# --- APP START ---
if not st.session_state['logged_in']: login_screen()
else:
    if st.session_state['role'] == 'admin': admin_view()
    else: monter_view()