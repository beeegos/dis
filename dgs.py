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

# --- SŁOWNIK TŁUMACZEŃ ---
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
        "dash_title": "📊 Dashboard Zarządzania",
        "tab_day": "📅 Raport Dzienny",
        "tab_month": "📈 Statystyki Miesięczne",
        "tab_emp": "👥 Pracownicy",
        "tab_db": "🗄️ Pełna Baza",
        "tab_users": "🔑 Konta / Users",
        "tab_pdf": "📄 Raporty PDF",
        "no_data": "Brak danych w bazie.",
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
       # (Tu można wkleić tłumaczenia DE z poprzedniej wersji, skróciłem dla czytelności kodu)
       # Skopiuj sekcję DE z poprzedniego kodu jeśli potrzebujesz
       "login_title": "🔐 Anmeldung - Fiber System",
       "user_label": "Benutzername", 
       "pass_label": "Passwort",
       "login_btn": "Anmelden",
       # ... RESZTA DE ...
    },
    "ENG": {
       # (Tu można wkleić tłumaczenia ENG z poprzedniej wersji)
       # Skopiuj sekcję ENG z poprzedniego kodu jeśli potrzebujesz
       "login_title": "🔐 Login - Fiber System",
       "user_label": "Username",
       "pass_label": "Password",
       "login_btn": "Login",
       # ... RESZTA ENG ...
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

def admin_view():
    disp = st.session_state.get('display_name') or st.session_state['username']
    st.sidebar.warning(f"{get_text('sidebar_admin_warning')} {disp}")
    if st.sidebar.button(get_text("logout_btn")): logout()
    st.title(get_text("dash_title"))
    df = load_all_data()
    t1, t2, t3, t4, t5, t6 = st.tabs([get_text("tab_day"), get_text("tab_month"), get_text("tab_emp"), get_text("tab_db"), get_text("tab_users"), get_text("tab_pdf")])

    # --- TAB 1: DZIENNY ---
    with t1:
        if df.empty: st.info(get_text("no_data"))
        else:
            df['date'] = pd.to_datetime(df['date'])
            sel_day = st.date_input(get_text("pick_day"), datetime.now())
            d_df = df[df['date'].dt.date == sel_day]
            if d_df.empty: st.info(get_text("no_reports_day"))
            else:
                for team in d_df['team_name'].unique():
                    t_data = d_df[d_df['team_name'] == team]
                    with st.container(border=True):
                        st.subheader(f"{get_text('team_header')} {team.upper()}")
                        st.dataframe(t_data[["address","object_num","we_count","gfta_sum","activation_sum"]], hide_index=True)

    # --- TAB 2: MIESIĘCZNY ---
    with t2:
        if df.empty: st.info(get_text("no_data"))
        else:
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
            c1, c2 = st.columns(2)
            sel_emp = c1.selectbox(get_text("lbl_emp_select"), get_employees())
            sel_mon = c2.selectbox(get_text("pick_month"), sorted(df['month'].unique(), reverse=True))
            
            m_df = df[df['month'] == sel_mon]
            w_logs, tot_h = [], 0
            for _, row in m_df.iterrows():
                if row['workers_json']:
                    for w in json.loads(row['workers_json']):
                        if w['name'] == sel_emp:
                            w_logs.append({"Data": row['date'], "H": w['calculated_hours'], "Addr": row['address']})
                            tot_h += w['calculated_hours']
            st.metric(f"{get_text('lbl_total_hours')}: {sel_emp}", f"{tot_h:.2f} h")
            if w_logs: st.dataframe(pd.DataFrame(w_logs))

    # --- TAB 3: PRACOWNICY (POPRAWIONE) ---
    with t3:
        c_f, c_l = st.columns(2)
        with c_f.form("add_e"):
            nm = st.text_input(get_text("add_emp_label"))
            ct = st.radio(get_text("lbl_contract_type"), ["B2B", "Contract"])
            if st.form_submit_button(get_text("add_emp_btn")) and nm: 
                if add_employee(nm, ct): st.success("OK"); st.rerun()
        
        with c_l:
            # Tutaj była zmiana: używamy get_employees_map() zamiast get_employees()
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