import streamlit as st
import pandas as pd
import json
import os
import time
import base64
from datetime import datetime
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FKK GÜNEY OTO MES", layout="wide", initial_sidebar_state="expanded")

# --- VERİ YÖNETİMİ ---
def load_data(file_name, default_data):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default_data
    return default_data

def save_data(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- HAFIZA BAŞLATMA ---
if 'db' not in st.session_state: st.session_state.db = load_data("kayitlar.json", [])
if 'arsiv_db' not in st.session_state: st.session_state.arsiv_db = load_data("arsiv.json", [])

# Varsayılan personel listesi
varsayilan_personel = [
    {"ad": "Önder Şensoy", "rol": "Sorumlu Personel", "durum": "Aktif"},
    {"ad": "Yunus Emre Arslan", "rol": "Sorumlu Personel", "durum": "Aktif"},
    {"ad": "Rasim Bayrı", "rol": "Sorumlu Personel", "durum": "Aktif"},
    {"ad": "Semih Çokşen", "rol": "Sorumlu Personel", "durum": "Aktif"},
    {"ad": "Engin Çakırkaya", "rol": "Sorumlu Personel", "durum": "Aktif"},
    {"ad": "Adem Sekmen", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Cengiz Yılmaz", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Coşkun Bulut", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Cumhur Kara", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Ersin Kıllı", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Furkan Kol", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Furkan Şeker", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Hüseyin Erdoğan", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Kazım Çavuşoğlu", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Ramazan Demirbilek", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Ramazan Genç", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Selvet Gayretli", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Seyit Ahmet Çakır", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Süleyman Karaman", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Şafak Şahin", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Taha Baytekin", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Taha Kara", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Ufuk Uçak", "rol": "Operatör", "durum": "Aktif"},
    {"ad": "Yunus Emre Arı", "rol": "Operatör", "durum": "Aktif"},
]

# Personel verisini yükle ve normalize et
def load_personel():
    raw = load_data("personel.json", varsayilan_personel)
    temiz = []
    for i, p in enumerate(raw):
        ad = p.get('ad') or p.get('isim') or p.get('name') or p.get('Ad') or ""
        if not ad or 'Personel' in ad:
            # Varsayılan listeden eşleştir
            ad = varsayilan_personel[i]['ad'] if i < len(varsayilan_personel) else ""
        if ad:
            temiz.append({
                "ad": ad,
                "rol": p.get('rol', 'Operatör'),
                "durum": p.get('durum', 'Aktif')
            })
    # Hiç geçerli kayıt yoksa veya sayı az ise varsayılanı yaz
    if len(temiz) < len(varsayilan_personel):
        # Mevcut isimleri koru, eksikleri ekle
        mevcut_adlar = [p['ad'] for p in temiz]
        for vp in varsayilan_personel:
            if vp['ad'] not in mevcut_adlar:
                temiz.append(vp)
    save_data("personel.json", temiz)
    return temiz

if 'personel_db' not in st.session_state:
    st.session_state.personel_db = load_personel()

if 'sorumlu_listesi' not in st.session_state:
    aktif = [p['ad'] for p in st.session_state.personel_db if p.get('durum') == 'Aktif' and p.get('rol') in ['Operatör', 'Sorumlu Personel']]
    st.session_state.sorumlu_listesi = aktif if aktif else load_data("sorumlular.json", ["Adem Sekmen", "Cengiz Yılmaz", "Habibe Nur Kayhan", "Süleyman Karaman"])

# --- ÜRÜN VERİ TABANI ---
tam_urun_listesi_varsayilan = {
    "338": "DİTAŞ", "339": "DİTAŞ", "552": "PİYASA", "555": "PİYASA", "1196": "PİYASA", 
    "1372": "PİYASA", "1373": "PİYASA", "1525": "PİYASA", "1610": "PİYASA", "1611": "PİYASA", 
    "1649": "PİYASA", "1750": "PİYASA", "1751": "PİYASA", "1764": "PİYASA", "1766": "PİYASA", 
    "1769": "PİYASA", "1770": "PİYASA", "1771": "İHRACAT", "1806": "PİYASA", "1807": "PİYASA", 
    "1809": "PİYASA", "1811": "PİYASA", "1813": "PİYASA", "1814": "PİYASA", "1815": "PİYASA", 
    "1852": "PİYASA", "1863": "PİYASA", "1864": "PİYASA", "1872": "PİYASA", "1873": "PİYASA", 
    "1889": "PİYASA", "1890": "PİYASA", "1891": "PİYASA", "1892": "PİYASA", "1893": "PİYASA", 
    "1894": "PİYASA", "1895": "PİYASA", "1897": "PİYASA", "1998-1": "PİYASA", "2012": "PİYASA", 
    "5500": "İHRACAT", "5501": "İHRACAT", "5502": "HEKSAGON", "5503": "PİYASA", "5504": "PİYASA", 
    "5505": "PİYASA", "5506": "HEKSAGON", "5507": "İHRACAT", "5508": "KARSAN", "5509": "VİBRACUSTİC", 
    "5510": "VİBRACUSTİC", "5511": "PİYASA", "5512": "VİBRACUSTİC", "5513": "VİBRACUSTİC", 
    "5515": "PİYASA", "5516": "PİYASA", "5517": "PİYASA", "5528": "GÜRMAK", "5529": "GÜRMAK", 
    "5531": "REİN", "5534": "İHRACAT", "5535": "KARSAN", "5536": "KARSAN", "5537": "KARSAN", 
    "5538": "İHRACAT", "5539": "İHRACAT", "5540": "İHRACAT", "5541": "GÜRMAK", "5545": "KARSAN", 
    "5546": "GÜRMAK", "5548": "İHRACAT", "5551": "PİYASA", "5553": "İHRACAT", "5555": "PİYASA", 
    "5556": "İHRACAT", "5557": "İHRACAT", "5558": "İHRACAT", "5559": "PİYASA", "5560": "İHRACAT", 
    "5564": "İHRACAT", "6101": "PİYASA", "6108": "PİYASA", "6109": "PİYASA", "7001": "PİYASA", 
    "7002": "PİYASA", "7004": "PİYASA", "9067": "PİYASA", "9112": "PİYASA", "9117": "PİYASA", 
    "9136": "PİYASA", "9137": "PİYASA", "9211": "PİYASA", "9213-1": "PİYASA", "9513": "PİYASA", 
    "9514": "PİYASA", "9515": "ZF SACHS", "9516": "ZF SACHS", "9517": "ZF SACHS", "9518": "ZF SACHS", 
    "9520": "PİYASA", "9521": "PİYASA", "9525": "ZF SACHS", "9526": "ZF SACHS", "9528": "ZF SACHS", 
    "9529": "ZF SACHS", "9530": "ZF SACHS", "9543": "PİYASA", "9545": "MAYSAN", "9547": "ZF SACHS", 
    "9548": "PİYASA", "9549": "ZF SACHS", "9550": "ZF SACHS", "9553": "ZF SACHS", "9554": "ZF SACHS", 
    "9555": "ZF SACHS", "9558": "ZF SACHS", "9559": "ZF SACHS", "9560": "ZF SACHS", "9561": "ZF SACHS", 
    "9563": "ZF SACHS", "16579": "PİYASA", "16586": "PİYASA", "17002": "PİYASA", "17009": "PİYASA", 
    "17011": "PİYASA", "17018": "PİYASA", "17021": "PİYASA", "20005": "PİYASA", "20006": "PİYASA", 
    "20007": "PİYASA", "20008": "PİYASA", "20011": "PİYASA", "20074": "PİYASA", "20083": "PİYASA", 
    "20084": "PİYASA", "20085": "PİYASA", "20086": "PİYASA", "20117": "PİYASA", "20118": "PİYASA", 
    "20120": "PİYASA", "20123": "PİYASA", "57230": "EGE PAZ", "60288": "İHRACAT", "60289": "İHRACAT", 
    "60355": "İHRACAT", "60369": "İHRACAT", "60370": "İHRACAT", "60387-1": "İHRACAT", "60445": "PİYASA", 
    "60450": "İHRACAT", "60451": "İHRACAT", "60479": "İHRACAT", "60481": "İHRACAT", "60482": "İHRACAT", 
    "60517": "PİYASA", "60572": "İHRACAT", "60573": "PİYASA", "60642": "İHRACAT", "60663": "İHRACAT", 
    "60664": "İHRACAT", "60767": "İHRACAT", "60850": "İHRACAT", "60854": "İHRACAT", "60890": "İHRACAT", 
    "60891": "İHRACAT", "65001": "PİYASA", "65002": "PİYASA", "65003": "MAYSAN", "65004": "MAYSAN", 
    "65005": "MAYSAN", "65006": "MAYSAN", "65007": "MAYSAN", "65008": "MAYSAN", "65009": "MAYSAN", 
    "65010": "MAYSAN", "65011": "MAYSAN", "65012": "MAYSAN", "65025": "MAYSAN", "65026": "MAYSAN", 
    "65029": "GÜRMAK", "65032": "MAYSAN", "65035": "MAYSAN", "65503": "İHRACAT", "65504": "İHRACAT", 
    "80003": "PİYASA", "80004": "PİYASA", "80005": "PİYASA", "80008": "PİYASA", "700007": "TOFAŞ", 
    "700013": "FORD", "700014": "FORD", "700015": "FORD", "1197-1": "PİYASA", "1226-1": "PİYASA", 
    "1228-1": "ZF SACHS", "1229-1": "PİYASA", "1266-1": "PİYASA", "1368-1": "PİYASA", "1369-1": "PİYASA", 
    "1370-1": "PİYASA", "1371-1": "PİYASA", "17004": "PİYASA", "17005-1": "PİYASA", "17006-1": "PİYASA", 
    "17019-1": "PİYASA", "1765-1": "PİYASA", "1812-1": "PİYASA", "1996-1": "KARSAN", "20075-1": "PİYASA", 
    "20076-1": "PİYASA", "20077-1": "PİYASA", "20078-1": "PİYASA", "20080": "PİYASA", "20081-1": "PİYASA", 
    "20082-1": "PİYASA", "20090-1": "PİYASA", "20091-1": "PİYASA", "20119-1": "PİYASA", "20121-1": "PİYASA", 
    "20122-1": "PİYASA", "20124-1": "PİYASA", "2060-1": "FORD", "2061-1": "PİYASA", "2069-1": "FORD", 
    "551-1": "PİYASA", "5519-1": "PİYASA", "5527-1": "KARSAN", "5532-1": "KARSAN", "5533-1": "İHRACAT", 
    "5544-1": "İHRACAT", "5554-1": "İHRACAT", "5563-1": "OLGUN ÇELİK", "60566-1": "KARSAN", "6100": "PİYASA", 
    "65014-1": "MAYSAN", "65015-1": "MAYSAN", "65016-1": "MAYSAN", "65017-1": "MAYSAN", "65018-1": "MAYSAN", 
    "65019-1": "MAYSAN", "65020-1": "MAYSAN", "65021-1": "MAYSAN", "65501-1": "İHRACAT", "65502-1": "İHRACAT", 
    "80006-1": "PİYASA", "80007-1": "PİYASA", "9082-1": "PİYASA", "9083": "PİYASA", "9085-1": "PİYASA", 
    "9087-1": "PİYASA", "9088-1": "PİYASA", "9089-1": "PİYASA", "9092-1": "PİYASA", "9093-1": "PİYASA", 
    "9094-1": "PİYASA", "9096-1": "PİYASA", "9097-1": "PİYASA", "9100-1": "PİYASA", "9109-1": "PİYASA", 
    "9110-1": "PİYASA", "9111-1": "PİYASA", "9120-1": "PİYASA", "9120-3": "PİYASA", "9121-1": "PİYASA", 
    "9122-1": "PİYASA", "9155-1": "PİYASA", "9177-1": "PİYASA", "9178-1": "PİYASA", "9179-1": "PİYASA", 
    "9180-1": "PİYASA", "9181-1": "PİYASA", "9206-1": "PİYASA", "9207-1": "PİYASA", "9214-1": "PİYASA", 
    "9227-1": "PİYASA", "9228-1": "PİYASA", "9230-1": "TOFAŞ", "9544/1": "PİYASA", "9544/2": "PİYASA"
}

if 'kod_musteri_dict' not in st.session_state: 
    st.session_state.kod_musteri_dict = load_data("urunler.json", tam_urun_listesi_varsayilan)

# --- KESİM ADETLERİ ---
kesim_adetleri = {
    "338": 20, "339": 40, "551-1": 1, "552": 1, "555": 1, "1197-1": 1, "1226-1": 1,
    "1228-1": 1, "1229-1": 1, "1266-1": 1, "1368-1": 1, "1369-1": 1, "1370-1": 1,
    "1371-1": 1, "1372": 1, "1373-1": 1, "1525": 1, "1610": 1, "1611": 1, "1649": 1,
    "1750": 5, "1751": 1, "1764": 2, "1766": 1, "1769": 14, "1770": 14, "1771": 1,
    "1806": 1, "1807": 1, "1809": 1, "1811": 1, "1812-1": 1, "1813": 1, "1814": 1,
    "1815": 1, "1863": 1, "1872": 1, "1873": 1, "1889": 1, "1890": 1, "1891": 1,
    "1892": 1, "1893": 1, "1894": 1, "1895": 1, "1897": 1, "1998-1": 1, "2012": 1,
    "2060-1": 1, "2061-1": 1, "2069-1": 1, "2074-1": 1, "5500": 1, "5501": 1,
    "5502": 1, "5503": 45, "5504": 45, "5505": 1, "5507": 1, "5511": 1, "5519-1": 1,
    "5527-1": 1, "5528": 1, "5529": 1, "5531": 1, "5532-1": 1, "5533-1": 1,
    "5534": 1, "5535": 1, "5536": 1, "5537": 1, "5538": 1, "5539": 1, "5540": 1,
    "5541": 1, "5544-1": 1, "5546": 1, "5548": 2, "5551": 1, "5553": 1, "5554-1": 1,
    "5555": 18, "5556": 1, "5557": 1, "5558": 1, "5559": 9, "5560": 1, "5563-1": 1,
    "5564": 1, "6100": 1, "6101": 1, "6108": 1, "6109": 1, "7001": 1, "7002": 1,
    "7004": 1, "9067": 1, "9082-1": 1, "9083": 1, "9085-1": 1, "9087-1": 1,
    "9088-1": 1, "9089-1": 1, "9092-1": 1, "9096-1": 1, "9097-1": 1, "9100-1": 1,
    "9109-1": 1, "9110-1": 1, "9111-1": 1, "9112": 1, "9117": 1, "9120-1": 1,
    "9120-3": 2, "9121-1": 1, "9122-1": 1, "9136": 1, "9137": 1, "9155-1": 1,
    "9177-1": 1, "9178-1": 1, "9179-1": 1, "9180-1": 1, "9181-1": 1, "9206": 1,
    "9207-1": 1, "9211": 1, "9213-1": 1, "9214-1": 1, "9227-1": 1, "9228-1": 1,
    "9230-1": 1, "9514": 1, "9515": 1, "9516": 1, "9517": 1, "9518": 1, "9525": 1,
    "9526": 1, "9543": 1, "9547": 3, "9549": 1, "9550": 1, "9553": 1, "9554": 1,
    "9555": 2, "9561": 1, "9563": 1, "9564-1": 1, "16579": 1, "16586": 1,
    "17002": 2, "17004": 1, "17005-1": 1, "17006-1": 1, "17009": 5, "17011": 1,
    "17018": 22, "17019-1": 1, "17021": 1, "20005": 1, "20006": 1, "20007": 1,
    "20008": 1, "20011": 1, "20074": 1, "20075-1": 1, "20078-1": 1, "20080": 1,
    "20081": 1, "20082-1": 1, "20083": 1, "20084": 1, "20085": 1, "20090-1": 1,
    "20117": 1, "20118": 1, "20119-1": 1, "20120": 1, "20121-1": 1, "20122-1": 1,
    "20123": 1, "20124-1": 1, "60355": 1, "60369": 1, "60387-1": 1, "60479": 1,
    "60481": 1, "60517": 1, "60573-1": 1, "60642": 1, "60663": 5, "60664": 5,
    "60767": 1, "60854": 6, "60890": 40, "60891": 40, "65003": 1, "65004": 1,
    "65005": 1, "65008": 1, "65009": 1, "65010": 1, "65012": 1, "65018-1": 1,
    "65020-1": 1, "65021-1": 1, "65025": 3, "65026": 4, "65029": 3, "65032": 1,
    "65035": 1, "65504": 1, "80003": 1, "80004": 1, "80005": 1, "80006-1": 1,
    "80007-1": 1, "80008": 1, "660.001": 10, "700.005": 1, "700.007": 1,
    "700.008": 1, "700.009": 1, "700.013": 5, "700.014": 4, "700.015": 5,
    "741.703": 1, "1806-P": 1, "1863-P": 1, "1873-P": 1, "1890-P": 1, "1892-P": 1,
    "1893-P": 1, "1895-P": 1, "1897-P": 1, "6101-P": 1, "9089-1P": 1,
    "9100-1P": 1, "9109-1P": 1, "9214-1P": 1, "16586-P": 1
}

# --- MAKİNE DURUMLARI ---
raw_m = load_data("makine_statu.json", {})
corrected_m = {}
for i in range(1, 6):
    m_name = f"Tambur {i}"
    m_old = raw_m.get(m_name, {})
    corrected_m[m_name] = {
        "durum": m_old.get("durum", "Çalışıyor") if m_old.get("durum", "Çalışıyor") in ["Çalışıyor", "Duruş"] else "Çalışıyor",
        "personel": m_old.get("personel", "Seçilmedi"),
        "hedef": m_old.get("hedef", 1000),
        "durus": m_old.get("durus", 0),
        "neden": m_old.get("neden", ""),
        "vardiya": m_old.get("vardiya", "-"),
        "tarih": m_old.get("tarih", "-")
    }
st.session_state.makine_verileri = corrected_m

# --- CSS VE ANİMASYON ---
st.markdown("""
<style>
    @keyframes spinX { 0% { transform: perspective(600px) rotateY(0deg); } 100% { transform: perspective(600px) rotateY(360deg); } }
    .rotating-logo-x { display: block; margin: 0 auto; width: 150px; animation: spinX 4s ease-in-out infinite; transform-style: preserve-3d; }
    [data-testid="stMetric"] { background-color: #1a3a5a; padding: 15px !important; border-radius: 10px !important; border-left: 5px solid #00BFFF !important; }
    .machine-card { padding: 20px; border-radius: 15px; margin-bottom: 5px; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    html, body, [class*="css"] { font-size: 16px !important; }
    .stRadio label { font-size: 15px !important; }
    .stSelectbox label, .stNumberInput label, .stTextInput label { font-size: 15px !important; }
    .stDataFrame { font-size: 15px !important; }
    p, div, span { font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# --- TÜM AKTİF PERSONEL LİSTESİ ---
def get_personel_listesi(rol_filtre=None):
    """Session state'teki personel listesinden aktif personeli getirir."""
    personel_db = st.session_state.get('personel_db', load_personel())
    if rol_filtre:
        liste = [p['ad'] for p in personel_db if p.get('durum') == 'Aktif' and p.get('rol') == rol_filtre]
    else:
        liste = [p['ad'] for p in personel_db if p.get('durum') == 'Aktif' and p.get('rol') in ['Operatör', 'Sorumlu Personel']]
    return [x for x in liste if x] or st.session_state.sorumlu_listesi

# --- GİRİŞ SİSTEMİ ---
if 'auth_status' not in st.session_state:
    st.session_state.auth_status, st.session_state.user_role, st.session_state.user_name = False, None, None

def login_ekrani():
    if not st.session_state.auth_status:
        if os.path.exists("fkk_logo.png"):
            with open("fkk_logo.png", "rb") as f:
                encoded_logo = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(f'<img src="data:image/png;base64,{encoded_logo}" class="rotating-logo-x">', unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #00BFFF;'>FKK GÜNEY OTO MES</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            bolum = st.selectbox("Bölüm", ["Yönetim", "Sorumlu Personel", "Operatör"])
            # Şifreleri dosyadan oku
            sifre_db_login = load_data("sifreler.json", {
                "Yönetim": "fkk.yonetim.1957",
                "Sorumlu Personel": "fkk.sorumlu1957",
                "Operatör": "fkk.operator1957"
            })
            if bolum == "Yönetim": 
                liste, pwd_check, role = ["Ufuk Altuncu", "Emre Altuncu", "Ömer Faruk Akdoğan", "Zeki Meral"], sifre_db_login.get("Yönetim", "fkk.yonetim.1957"), "Yönetim"
            elif bolum == "Sorumlu Personel": 
                liste, pwd_check, role = ["Önder Şensoy", "Yunus Emre Arslan", "Rasim Bayrı", "Semih Çokşen", "Engin Çakırkaya"], sifre_db_login.get("Sorumlu Personel", "fkk.sorumlu1957"), "Sorumlu Personel"
            else: 
                # Sadece Operatör rolündeki aktif personel
                personel_listesi_login = load_data("personel.json", varsayilan_personel)
                operatorler = [p.get('ad','') for p in personel_listesi_login if p.get('rol') == 'Operatör' and p.get('durum') == 'Aktif']
                if not operatorler:
                    operatorler = ["Adem Sekmen", "Cengiz Yılmaz", "Coşkun Bulut", "Cumhur Kara", "Ersin Kıllı",
                                   "Furkan Kol", "Furkan Şeker", "Hüseyin Erdoğan", "Kazım Çavuşoğlu",
                                   "Ramazan Demirbilek", "Ramazan Genç", "Selvet Gayretli", "Seyit Ahmet Çakır",
                                   "Süleyman Karaman", "Şafak Şahin", "Taha Baytekin", "Taha Kara",
                                   "Ufuk Uçak", "Yunus Emre Arı"]
                liste, pwd_check, role = operatorler, sifre_db_login.get("Operatör", "fkk.operator1957"), "Operatör"
            
            user = st.selectbox("İsim Seçiniz", liste)
            pwd = st.text_input("Şifre", type="password")
            if st.button("Sisteme Giriş Yap", use_container_width=True):
                # Önce kişiye özel şifre var mı kontrol et, yoksa rol şifresi geçerli
                kisi_sifre = sifre_db_login.get(user, None)
                gecerli_sifre = kisi_sifre if kisi_sifre else pwd_check
                if pwd == gecerli_sifre:
                    st.session_state.auth_status, st.session_state.user_role, st.session_state.user_name = True, role, user
                    st.rerun()
                else: st.error("Hatalı Şifre!")
        st.stop()

login_ekrani()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("fkk_logo.png"): st.image("fkk_logo.png", use_container_width=True)
    st.write(f"👤 **{st.session_state.user_name}**")
    st.write(f"🏷️ **{st.session_state.user_role}**")
    st.markdown("---")
    if st.session_state.user_role == "Yönetim": 
        items = ["🏠 Dashboard", "📡 Vardiya Yönetimi", "📥 Veri Giriş", "📊 Analiz", "📄 Raporlar", "⚙️ Yönetim"]
    elif st.session_state.user_role == "Sorumlu Personel":
        items = ["🏠 Dashboard", "📡 Vardiya Yönetimi", "📥 Veri Giriş", "📊 Analiz", "📄 Raporlar"]
    else: items = ["📥 Veri Giriş"]
    menu = st.radio("ANA MENÜ", items)
    if st.button("🔴 Güvenli Çıkış"): st.session_state.auth_status = False; st.rerun()

# --- 1. DASHBOARD ---
if menu == "🏠 Dashboard":
    # Saat + Tarih birlikte
    st.components.v1.html("""
        <div style="background-color: #0e1117; padding: 10px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #1a3a5a;">
            <span id="live-date" style="color: #aaaaaa; font-size: 16px; font-family: monospace;"></span>
            <span id="live-clock" style="color: #00BFFF; font-size: 26px; font-weight: bold; font-family: monospace;">00:00:00</span>
        </div>
        <script>
            function updateClock() {
                var now = new Date();
                var time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0') + ':' + now.getSeconds().toString().padStart(2, '0');
                var days = ['Pazar','Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi'];
                var date = days[now.getDay()] + ' ' + now.getDate().toString().padStart(2,'0') + '.' + (now.getMonth()+1).toString().padStart(2,'0') + '.' + now.getFullYear();
                document.getElementById('live-clock').innerHTML = time;
                document.getElementById('live-date').innerHTML = '📅 ' + date;
            }
            setInterval(updateClock, 1000); updateClock();
        </script>
    """, height=65)

    now = datetime.now()
    v_auto = "1. VARDİYA" if 8 <= now.hour < 16 else ("2. VARDİYA" if 16 <= now.hour < 24 else "3. VARDİYA")
    st.markdown(f"## 🏭 {v_auto} AKTİF")

    df_live = pd.DataFrame(st.session_state.db)
    v_uretim = int(df_live['Fiili'].sum()) if not df_live.empty else 0
    v_hedef = sum(m['hedef'] for m in st.session_state.makine_verileri.values())
    fire_cols = ['Yırtık', 'Çatlak', 'Hava Boşluğu', 'Kalıp Kaçırma']
    v_fire = int(df_live[df_live.columns.intersection(fire_cols)].sum().sum()) if not df_live.empty else 0
    t_durus = sum(m['durus'] for m in st.session_state.makine_verileri.values())

    # Düzeltilmiş hesaplamalar
    verim = round((v_uretim / v_hedef) * 100, 1) if v_hedef > 0 else 0
    kalite = round(((v_uretim - v_fire) / v_uretim) * 100, 1) if v_uretim > 0 else "-"

    # Metrikler — 6'ya çıkarıldı
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Toplam Üretim", v_uretim)
    m2.metric("Toplam Hedef", v_hedef)
    m3.metric("Verimlilik %", f"%{verim}" if verim else "%0")
    m4.metric("Kalite Oranı %", f"%{kalite}" if kalite != "-" else "Veri Yok")
    m5.metric("Toplam Fire", v_fire)
    m6.metric("Toplam Duruş", f"{int(t_durus)} dk")

    st.markdown("---")

    for m, v in st.session_state.makine_verileri.items():
        bg = "#2d5a27" if v['durum'] == "Çalışıyor" else ("#8b1a1a" if v['durum'] == "Duruş" else "#8b5a1a")
        m_fiili = int(df_live[df_live['Tambur'] == m]['Fiili'].sum()) if not df_live.empty else 0
        m_fire = int(df_live[df_live['Tambur'] == m][df_live.columns.intersection(fire_cols)].sum().sum()) if not df_live.empty else 0
        m_progress = min(float(m_fiili / v['hedef']), 1.0) if v['hedef'] > 0 else 0.0

        # O tambura ait son ürün kodu
        m_df = df_live[df_live['Tambur'] == m] if not df_live.empty else pd.DataFrame()
        son_kod = m_df.iloc[-1]['Kod'] if not m_df.empty else "-"
        son_musteri = m_df.iloc[-1]['Müşteri'] if not m_df.empty else "-"

        tamamlanma_yuzde = round(m_progress * 100, 1)
        st.markdown(f'''<div class="machine-card" style="background-color: {bg};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 18px; font-weight: bold;">{m} - {v["durum"]}</span><br>
                    <span style="font-size: 13px; opacity: 0.9;">👤 {v.get("operatör1", v.get("personel", "-"))} | {v.get("operatör2", "-")} | {v.get("operatör3", "-")}</span><br>
                    <span style="font-size: 13px; opacity: 0.9;">📦 Ürün: {son_kod} | Müşteri: {son_musteri}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 15px;">🎯 Hedef: {v["hedef"]} | 📈 Fiili: {m_fiili} | ❌ Fire: {m_fire}</span><br>
                    <span style="font-size: 13px; color: #ffeb3b;">⏱️ Duruş: {int(df_live[df_live["Tambur"] == m]["Duruş Süresi"].sum()) if not df_live.empty and "Duruş Süresi" in df_live.columns else 0} dk</span><br>
                    <span style="font-size: 15px; color: #00BFFF; font-weight: bold;">📊 Tamamlanma: %{tamamlanma_yuzde}</span>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)
        st.progress(m_progress)

# --- 2. VARDİYA YÖNETİMİ ---
elif menu == "📡 Vardiya Yönetimi":
    st.subheader("📡 Vardiya Yönetimi")
    now = datetime.now()
    su_an_ki_vardiya = "1. Vardiya" if 8 <= now.hour < 16 else ("2. Vardiya" if 16 <= now.hour < 24 else "3. Vardiya")
    bugun = now.strftime("%d.%m.%Y")

    # Planlayan alanı
    if st.session_state.user_role == "Sorumlu Personel":
        planlayan = st.session_state.user_name
        st.markdown(f"""
            <div style="background-color: #1a3a5a; padding: 12px; border-radius: 8px; border-left: 6px solid #00BFFF; margin-bottom: 20px; color: #00BFFF; font-weight: bold;">
                📅 Tarih: {bugun} | 🕒 Aktif Vardiya: {su_an_ki_vardiya} | 📋 Planlayan: {planlayan}
            </div>
        """, unsafe_allow_html=True)
    else:
        col_plan1, col_plan2 = st.columns([3, 1])
        col_plan1.markdown(f"""
            <div style="background-color: #1a3a5a; padding: 12px; border-radius: 8px; border-left: 6px solid #00BFFF; margin-bottom: 20px; color: #00BFFF; font-weight: bold;">
                📅 Tarih: {bugun} | 🕒 Aktif Vardiya: {su_an_ki_vardiya}
            </div>
        """, unsafe_allow_html=True)
        planlayan = col_plan2.selectbox("📋 Planlayan", ["Seçiniz"] + ["Önder Şensoy", "Yunus Emre Arslan", "Rasim Bayrı", "Semih Çokşen", "Engin Çakırkaya"])

    temp = st.session_state.makine_verileri.copy()
    for m in st.session_state.makine_verileri:
        with st.container(border=True):
            st.write(f"#### {m}")
            c1, c2, c3, c4, c5 = st.columns(5)
            d = c1.selectbox("Makine Durumu", ["Çalışıyor", "Duruş"],
                key=f"d_{m}",
                index=["Çalışıyor", "Duruş"].index(temp[m]["durum"]) if temp[m]["durum"] in ["Çalışıyor", "Duruş"] else 0)
            tam_personel = get_personel_listesi("Operatör")
            op1_val = temp[m].get("operatör1", "Seçilmedi")
            op2_val = temp[m].get("operatör2", "Seçilmedi")
            op3_val = temp[m].get("operatör3", "Seçilmedi")
            op1_idx = (["Seçilmedi"] + tam_personel).index(op1_val) if op1_val in ["Seçilmedi"] + tam_personel else 0
            op2_idx = (["Seçilmedi"] + tam_personel).index(op2_val) if op2_val in ["Seçilmedi"] + tam_personel else 0
            op3_idx = (["Seçilmedi"] + tam_personel).index(op3_val) if op3_val in ["Seçilmedi"] + tam_personel else 0
            p1 = c2.selectbox("Operatör 1", ["Seçilmedi"] + tam_personel, key=f"p1_{m}", index=op1_idx)
            p2 = c3.selectbox("Operatör 2", ["Seçilmedi"] + tam_personel, key=f"p2_{m}", index=op2_idx)
            p3 = c4.selectbox("Operatör 3", ["Seçilmedi"] + tam_personel, key=f"p3_{m}", index=op3_idx)
            h = c5.number_input("Hedef Adet", value=0 if d == "Duruş" else temp[m]["hedef"], key=f"h_{m}", disabled=d == "Duruş")
            temp[m] = {
                "durum": d, "personel": p1,
                "operatör1": p1, "operatör2": p2, "operatör3": p3,
                "hedef": h, "vardiya": su_an_ki_vardiya,
                "tarih": bugun, "planlayan": planlayan
            }
    if st.button("VARDİYA YÖNETİM PLANINI YAYINLA", use_container_width=True):
        if planlayan == "Seçiniz":
            st.warning("Planlayan kişiyi seçiniz!")
        else:
            st.session_state.makine_verileri = temp
            save_data("makine_statu.json", temp)
            st.success(f"Plan {planlayan} tarafından mühürlendi!")
            st.rerun()

# --- 3. VERİ GİRİŞ ---
elif menu == "📥 Veri Giriş":
    st.subheader("📥 Üretim Kayıt Formu")
    if 'form_id' not in st.session_state: st.session_state.form_id = 0
    if 'son_kayit' not in st.session_state: st.session_state.son_kayit = None

    # Kayıt özeti göster
    if st.session_state.son_kayit:
        k = st.session_state.son_kayit
        st.success("✅ Kayıt Başarıyla Tamamlandı!")
        with st.container(border=True):
            st.markdown(f"""
            | Alan | Bilgi |
            |------|-------|
            | 📅 Tarih | {k['Tarih']} |
            | 🕒 Vardiya | {k['Vardiya']} |
            | 🏭 Tambur | {k['Tambur']} |
            | 📦 Ürün Kodu | {k['Kod']} |
            | 👥 Müşteri | {k['Müşteri']} |
            | 👤 Operatör 1 | {k.get('Operatör 1', '-')} |
            | 👤 Operatör 2 | {k.get('Operatör 2', '-')} |
            | 👤 Operatör 3 | {k.get('Operatör 3', '-')} |
            | 📋 Kaydeden | {k.get('Kaydeden', '-')} |
            | 📈 Fiili Üretim | {k['Fiili']} adet |
            | ❌ Toplam Fire | {k['Yırtık'] + k['Çatlak'] + k['Hava Boşluğu'] + k['Kalıp Kaçırma']} adet |
            | ✅ Sağlam Üretim | {k['Fiili'] - k['Yırtık'] - k['Çatlak'] - k['Hava Boşluğu'] - k['Kalıp Kaçırma']} adet |
            | ⏱️ Duruş Süresi | {k.get('Duruş Süresi', 0)} dk |
            | 🔧 Duruş Nedeni | {k.get('Duruş Nedeni', '-') or '-'} |
            | ⚙️ Net Üretim Süresi | {k.get('Net Üretim Süresi', 0)} dk |
            """)
        if st.button("➕ Yeni Kayıt Gir", use_container_width=True):
            st.session_state.son_kayit = None
            st.session_state.form_id += 1
            st.rerun()
    else:
        with st.container(border=True):
            now = datetime.now()
            col1, col2, col3 = st.columns(3)
            # Vardiya otomatik seçili, değiştirilebilir
            v_default = 0 if 8 <= now.hour < 16 else (1 if 16 <= now.hour < 24 else 2)
            v_secim = col1.selectbox("Vardiya Seçimi", ["1. Vardiya (08:00 - 16:00)", "2. Vardiya (16:00 - 24:00)", "3. Vardiya (00:00 - 08:00)"], index=v_default, key=f"v_{st.session_state.form_id}")
            tarih_giris = col2.date_input("Üretim Tarihi", value=now, key=f"t_{st.session_state.form_id}")
            # Kaydeden — Sorumlu Personel ise otomatik, Yönetim ise listeden seçsin
            if st.session_state.user_role == "Sorumlu Personel":
                kaydeden = st.session_state.user_name
                col3.info(f"📋 Kaydeden: **{kaydeden}**")
            else:
                kaydeden = col3.selectbox("Kaydeden (Sorumlu Personel)", 
                    ["Seçiniz"] + ["Önder Şensoy", "Yunus Emre Arslan", "Rasim Bayrı", "Semih Çokşen", "Engin Çakırkaya"],
                    key=f"kdy_{st.session_state.form_id}")
            st.markdown("---")
            st.markdown("#### 👥 Operatör Bilgileri")
            operatör_listesi = get_personel_listesi("Operatör")
            op1, op2, op3 = st.columns(3)
            op_1 = op1.selectbox("Operatör 1", ["Seçiniz"] + operatör_listesi, key=f"op1_{st.session_state.form_id}")
            op_2 = op2.selectbox("Operatör 2", ["Seçiniz"] + operatör_listesi, key=f"op2_{st.session_state.form_id}")
            op_3 = op3.selectbox("Operatör 3", ["Seçiniz"] + operatör_listesi, key=f"op3_{st.session_state.form_id}")
            st.markdown("---")

            c1, c2, c3, c4 = st.columns(4)
            m_secim = c1.selectbox("Makine / Tambur", list(st.session_state.makine_verileri.keys()), key=f"m_{st.session_state.form_id}")
            k_secim = c2.selectbox("Ürün Kodu", sorted(list(st.session_state.kod_musteri_dict.keys())), key=f"k_{st.session_state.form_id}")
            musteri_adi = st.session_state.kod_musteri_dict.get(k_secim, "Bilinmiyor")
            kesim = kesim_adetleri.get(k_secim, 1)

            baslangic = c3.text_input("Üretim Başlangıç", value="08:00", placeholder="08:00", key=f"b_{st.session_state.form_id}")
            bitis = c4.text_input("Üretim Bitiş", value=now.strftime("%H:%M"), placeholder="16:00", key=f"bit_{st.session_state.form_id}")

            st.info(f"📦 Müşteri: **{musteri_adi}** | ✂️ Kesim Adeti: **{kesim}**")

            fiili = st.number_input("Fiili Üretim (Adet)", min_value=0, step=1, key=f"f_{st.session_state.form_id}")

            st.markdown("#### ⏱️ Duruş Bilgisi")
            d1, d2 = st.columns(2)
            durus_sure = d1.number_input("Duruş Süresi (dk)", min_value=0, step=1, key=f"ds_{st.session_state.form_id}")
            durus_neden = d2.text_input("Duruş Nedeni", value="", placeholder="Örn: Kalıp değişimi, arıza...", key=f"dn_{st.session_state.form_id}")

            st.markdown("#### ❌ Kalite Kayıpları")
            st.caption("⚠️ Fire adetleri kesim adeti ile çarpılarak rapora yansıtılır.")
            h1, h2, h3, h4 = st.columns(4)
            y  = h1.number_input("Yırtık", 0, key=f"y_{st.session_state.form_id}")
            c  = h2.number_input("Çatlak", 0, key=f"c_{st.session_state.form_id}")
            hb = h3.number_input("Hava Boşluğu", 0, key=f"hb_{st.session_state.form_id}")
            kk = h4.number_input("Kalıp Kaçırma", 0, key=f"kk_{st.session_state.form_id}")

            # Kesim adeti ile çarp
            y_gercek  = y  * kesim
            c_gercek  = c  * kesim
            hb_gercek = hb * kesim
            kk_gercek = kk * kesim
            toplam_fire = y_gercek + c_gercek + hb_gercek + kk_gercek

            if (y + c + hb + kk) > 0 and kesim > 1:
                st.info(f"✂️ Kesim x Fire: {y+c+hb+kk} adet girişi → **{toplam_fire} adet** olarak kaydedilecek (kesim adeti: {kesim})")

            b1, b2 = st.columns(2)
            if b1.button("✅ KAYDI TAMAMLA VE GÖNDER", use_container_width=True):
                if op_1 == "Seçiniz" or fiili == 0:
                    st.warning("En az 1 operatör seçiniz ve fiili üretim giriniz!")
                elif kaydeden == "Seçiniz":
                    st.warning("Kaydeden personeli seçiniz!")
                elif toplam_fire > fiili:
                    st.error(f"❌ Toplam fire ({toplam_fire}) fiili üretimden ({fiili}) fazla olamaz!")
                else:
                    s_saat = datetime.now().strftime("%H:%M:%S")
                    # Net üretim süresi hesapla
                    try:
                        from datetime import datetime as dt2
                        bas = dt2.strptime(baslangic, "%H:%M")
                        bit = dt2.strptime(bitis, "%H:%M")
                        toplam_sure = int((bit - bas).total_seconds() / 60)
                        if toplam_sure < 0: toplam_sure += 1440  # gece yarısı geçişi
                        net_sure = max(toplam_sure - durus_sure, 0)
                    except:
                        toplam_sure = 0
                        net_sure = 0
                    op_2_kayit = op_2 if op_2 != "Seçiniz" else "-"
                    op_3_kayit = op_3 if op_3 != "Seçiniz" else "-"
                    yeni = {
                        "Tarih": tarih_giris.strftime("%d.%m.%Y"), "Saat": s_saat,
                        "Vardiya": v_secim.split(" (")[0],
                        "Operatör 1": op_1, "Operatör 2": op_2_kayit, "Operatör 3": op_3_kayit,
                        "Kaydeden": kaydeden,
                        "Tambur": m_secim, "Kod": k_secim, "Müşteri": musteri_adi,
                        "Fiili": fiili, "Başlangıç": baslangic, "Bitiş": bitis,
                        "Duruş Süresi": durus_sure, "Duruş Nedeni": durus_neden,
                        "Toplam Süre": toplam_sure, "Net Üretim Süresi": net_sure,
                        "Yırtık": y_gercek, "Çatlak": c_gercek,
                        "Hava Boşluğu": hb_gercek, "Kalıp Kaçırma": kk_gercek
                    }
                    st.session_state.db.append(yeni)
                    save_data("kayitlar.json", st.session_state.db)
                    st.session_state.son_kayit = yeni
                    st.rerun()
            if b2.button("🧹 EKRANI TEMİZLE", use_container_width=True):
                st.session_state.son_kayit = None
                st.session_state.form_id += 1
                st.rerun()

# --- 4. ANALİZ ---
elif menu == "📊 Analiz":
    st.markdown("### 📈 Stratejik Üretim Analiz Paneli")
    df_all = pd.concat([pd.DataFrame(st.session_state.arsiv_db), pd.DataFrame(st.session_state.db)], ignore_index=True)
    if not df_all.empty:
        def vardiya_std(v):
            v = str(v).strip()
            if "1." in v or "08:00" in v: return "1. Vardiya"
            if "2." in v or "16:00" in v: return "2. Vardiya"
            if "3." in v or "00:00" in v or v == "nan" or v == "": return "3. Vardiya"
            return v
        df_all['Vardiya'] = df_all['Vardiya'].apply(vardiya_std)
        h_cols = ['Yırtık', 'Çatlak', 'Hava Boşluğu', 'Kalıp Kaçırma']
        df_all['Hata_Top'] = df_all[df_all.columns.intersection(h_cols)].sum(axis=1)
        df_all['Saglam'] = df_all['Fiili'] - df_all['Hata_Top']
        # Sıfıra bölme koruması
        df_all['Kalite_%'] = df_all.apply(lambda r: round(r['Saglam'] / r['Fiili'] * 100, 2) if r['Fiili'] > 0 else 0, axis=1)
        # Süre hesaplamaları
        if 'Toplam Süre' in df_all.columns and 'Duruş Süresi' in df_all.columns:
            df_all['Toplam Süre'] = pd.to_numeric(df_all['Toplam Süre'], errors='coerce').fillna(0)
            df_all['Duruş Süresi'] = pd.to_numeric(df_all['Duruş Süresi'], errors='coerce').fillna(0)
            df_all['Net Üretim Süresi'] = pd.to_numeric(df_all.get('Net Üretim Süresi', 0), errors='coerce').fillna(0)
            df_all['Kullanılabilirlik_%'] = df_all.apply(lambda r: round(r['Net Üretim Süresi'] / 390 * 100, 1) if r['Net Üretim Süresi'] > 0 else 0, axis=1)
        else:
            df_all['Toplam Süre'] = 0
            df_all['Duruş Süresi'] = 0
            df_all['Net Üretim Süresi'] = 0
            df_all['Kullanılabilirlik_%'] = 0

        # --- GENEL TARİH FİLTRESİ ---
        df_all['Tarih_DT'] = pd.to_datetime(df_all['Tarih'], format='%d.%m.%Y', errors='coerce')
        min_t = df_all['Tarih_DT'].min()
        max_t = df_all['Tarih_DT'].max()
        with st.expander("📅 Tarih Filtresi", expanded=False):
            f1, f2 = st.columns(2)
            bas_t = f1.date_input("Başlangıç", value=min_t, key="analiz_bas")
            bit_t = f2.date_input("Bitiş", value=max_t, key="analiz_bit")
        df_all = df_all[(df_all['Tarih_DT'].dt.date >= bas_t) & (df_all['Tarih_DT'].dt.date <= bit_t)]

        analiz_modu = st.radio("Görünüm Seçin", ["📉 Üretim & Vardiya", "🏆 Tambur Analizi", "📂 Ürün Arama & Detay", "📦 Sipariş Takibi", "🎴 KPI Özet"], horizontal=True)
        st.markdown("---")

        if analiz_modu == "📉 Üretim & Vardiya":
            # Sadece üretim ve fire — duruş/kullanılabilirlik Tambur Analizi'nde
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Vardiya Bazlı Sağlam Üretim**")
                st.bar_chart(df_all.groupby("Vardiya")["Saglam"].sum().sort_index())
            with c2:
                st.write("**Vardiya Bazlı Fire Adedi**")
                st.bar_chart(df_all.groupby("Vardiya")["Hata_Top"].sum().sort_index(), color="#FF4B4B")
            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                st.write("**Makine Bazlı Sağlam Üretim**")
                st.bar_chart(df_all.groupby("Tambur")["Saglam"].sum(), color="#00BFFF")
            with c4:
                st.write("**Makine Bazlı Fire Adedi**")
                st.bar_chart(df_all.groupby("Tambur")["Hata_Top"].sum(), color="#FF4B4B")

        elif analiz_modu == "🏆 Tambur Analizi":
            # Kalite, kullanılabilirlik, duruş — tambur bazlı detaylı analiz
            t_data = df_all.groupby("Tambur").agg({'Fiili':'sum', 'Saglam':'sum', 'Hata_Top':'sum', 'Duruş Süresi':'sum', 'Toplam Süre':'sum', 'Net Üretim Süresi':'sum'})
            t_data['Kalite_%'] = t_data.apply(lambda r: round(r['Saglam'] / r['Fiili'] * 100, 1) if r['Fiili'] > 0 else 0, axis=1)
            t_data['Kullanılabilirlik_%'] = t_data.apply(lambda r: round(r['Net Üretim Süresi'] / 390 * 100, 1) if r['Net Üretim Süresi'] > 0 else 0, axis=1)
            fire_cols_mevcut = [c for c in h_cols if c in df_all.columns]
            for col in fire_cols_mevcut:
                t_data[col] = df_all.groupby("Tambur")[col].sum()
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Tambur Bazlı Kalite Oranı (%)**")
                st.bar_chart(t_data['Kalite_%'])
            with c2:
                st.write("**Tambur Bazlı Kullanılabilirlik (%)**")
                st.bar_chart(t_data['Kullanılabilirlik_%'], color="#00BFFF")
            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                st.write("**Tambur Bazlı Duruş Süresi (dk)**")
                st.bar_chart(t_data['Duruş Süresi'], color="#d4a017")
            with c4:
                st.write("**Tambur Bazlı Fire Kırılımı**")
                if fire_cols_mevcut:
                    st.bar_chart(t_data[fire_cols_mevcut])
            st.markdown("---")
            st.write("**Detay Tablo**")
            goster_cols = ['Fiili', 'Saglam', 'Hata_Top', 'Kalite_%', 'Kullanılabilirlik_%', 'Duruş Süresi']
            st.dataframe(t_data[[c for c in goster_cols if c in t_data.columns]].sort_values(by="Kalite_%", ascending=False), use_container_width=True)

        elif analiz_modu == "📂 Ürün Arama & Detay":
            secilen_kod = st.selectbox("Analiz Edilecek Ürün Kodu:", options=sorted(df_all['Kod'].unique()))
            if secilen_kod:
                u_df = df_all[df_all['Kod'] == secilen_kod].copy()
                toplam_fiili = int(u_df['Fiili'].sum())
                toplam_saglam = int(u_df['Saglam'].sum())
                toplam_fire = int(u_df['Hata_Top'].sum())
                toplam_durus = int(u_df['Duruş Süresi'].sum()) if 'Duruş Süresi' in u_df.columns else 0
                hata_oran = round(toplam_fire / toplam_fiili * 100, 1) if toplam_fiili > 0 else 0
                k1, k2, k3, k4, k5 = st.columns(5)
                k1.metric("Toplam Fiili", f"{toplam_fiili}")
                k2.metric("Sağlam", f"{toplam_saglam}")
                k3.metric("Hata Oranı", f"%{hata_oran}")
                k4.metric("Müşteri", f"{u_df['Müşteri'].iloc[0]}")
                k5.metric("Toplam Duruş", f"{toplam_durus} dk")
                st.line_chart(u_df.groupby('Tarih').agg({'Fiili':'sum', 'Saglam':'sum', 'Hata_Top':'sum'}))
                st.write("**Fire Kırılımı**")
                st.bar_chart(u_df[u_df.columns.intersection(h_cols)].sum(), color="#FF4B4B")
                detay_cols = ["Tarih", "Vardiya", "Tambur", "Operatör 1", "Operatör 2", "Operatör 3",
                              "Fiili", "Saglam", "Hata_Top", "Duruş Süresi", "Duruş Nedeni"]
                st.dataframe(u_df[[c for c in detay_cols if c in u_df.columns]], use_container_width=True)

        elif analiz_modu == "📦 Sipariş Takibi":
            siparis_db = load_data("siparisler.json", [])
            st.markdown("#### ➕ Yeni Sipariş Ekle")
            with st.container(border=True):
                sp1, sp2, sp3, sp4 = st.columns(4)
                # Tüm müşteri ve ürün kodları ürün veritabanından gelsin
                tum_musteriler = sorted(set(st.session_state.kod_musteri_dict.values()))
                tum_kodlar = sorted(st.session_state.kod_musteri_dict.keys())
                sp_musteri = sp1.selectbox("Müşteri", tum_musteriler, key="sp_mus")
                # Müşteri seçilince o müşteriye ait kodlar filtrele
                musteri_kodlari = sorted([k for k, v in st.session_state.kod_musteri_dict.items() if v == sp_musteri])
                sp_kod = sp2.selectbox("Ürün Kodu", musteri_kodlari if musteri_kodlari else tum_kodlar, key="sp_kod")
                sp_adet = sp3.number_input("Sipariş Adeti", min_value=1, step=1, key="sp_adet")
                sp_termin = sp4.date_input("Termin Tarihi", key="sp_termin")
                if st.button("✅ Sipariş Ekle", use_container_width=True):
                    siparis_db.append({
                        "musteri": sp_musteri, "kod": sp_kod,
                        "siparis": int(sp_adet),
                        "termin": sp_termin.strftime("%d.%m.%Y"),
                        "eklenme": datetime.now().strftime("%d.%m.%Y")
                    })
                    save_data("siparisler.json", siparis_db)
                    st.success("Sipariş eklendi!"); st.rerun()

            st.markdown("---")
            st.markdown("#### 📊 Sipariş Takip Tablosu")
            if siparis_db:
                for idx, sp in enumerate(siparis_db):
                    # O ürün koduna ait toplam üretimi hesapla
                    if not df_all.empty and sp['kod'] in df_all['Kod'].values:
                        uretilen = int(df_all[df_all['Kod'] == sp['kod']]['Saglam'].sum())
                    else:
                        uretilen = 0
                    kalan = max(sp['siparis'] - uretilen, 0)
                    tamamlanma = round(uretilen / sp['siparis'] * 100, 1) if sp['siparis'] > 0 else 0
                    # Terminle kalan gün
                    try:
                        termin_dt = datetime.strptime(sp['termin'], "%d.%m.%Y")
                        kalan_gun = (termin_dt - datetime.now()).days
                        gun_str = f"🔴 {kalan_gun} gün kaldı" if kalan_gun < 3 else f"🟢 {kalan_gun} gün kaldı"
                    except:
                        gun_str = "-"

                    renk = "#2d5a27" if tamamlanma >= 100 else ("#d4a017" if tamamlanma >= 50 else "#8b1a1a")
                    with st.container(border=True):
                        c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 2, 1])
                        c1.markdown(f"**{sp['musteri']}** | Kod: {sp['kod']}")
                        c2.markdown(f"📦 {sp['siparis']} adet")
                        c3.markdown(f"✅ Üretilen: **{uretilen}** | Kalan: **{kalan}**")
                        c4.markdown(f"**%{tamamlanma}** tamamlandı | {gun_str}")
                        if c5.button("🗑️", key=f"sp_sil_{idx}"):
                            siparis_db.pop(idx)
                            save_data("siparisler.json", siparis_db)
                            st.rerun()
                        st.progress(min(tamamlanma / 100, 1.0))
            else:
                st.info("Henüz sipariş eklenmemiş.")

        elif analiz_modu == "🎴 KPI Özet":
            toplam_saglam = int(df_all['Saglam'].sum())
            toplam_fire = int(df_all['Hata_Top'].sum())
            toplam_fiili = int(df_all['Fiili'].sum())
            toplam_durus = int(df_all['Duruş Süresi'].sum())
            toplam_net_sure = int(df_all['Net Üretim Süresi'].sum())
            toplam_sure = int(df_all['Toplam Süre'].sum())
            genel_kalite = round(toplam_saglam / toplam_fiili * 100, 1) if toplam_fiili > 0 else 0
            genel_fire_oran = round(toplam_fire / toplam_fiili * 100, 1) if toplam_fiili > 0 else 0
            genel_kull = round(toplam_net_sure / (390 * len(df_all)) * 100, 1) if len(df_all) > 0 and toplam_net_sure > 0 else 0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Toplam Sağlam", f"{toplam_saglam}")
            k2.metric("Toplam Fire", f"{toplam_fire}")
            k3.metric("Kalite Oranı", f"%{genel_kalite}")
            k4.metric("Toplam Duruş", f"{toplam_durus} dk")
            k5.metric("Kullanılabilirlik", f"%{genel_kull}")
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Günlük Sağlam Üretim Trendi**")
                st.line_chart(df_all.groupby("Tarih")["Saglam"].sum())
            with c2:
                st.write("**Günlük Fire Trendi**")
                st.line_chart(df_all.groupby("Tarih")["Hata_Top"].sum())
            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                st.write("**Günlük Duruş Trendi (dk)**")
                st.line_chart(df_all.groupby("Tarih")["Duruş Süresi"].sum())
            with c4:
                st.write("**Fire Tipi Kırılımı**")
                fire_ozet = df_all[df_all.columns.intersection(h_cols)].sum()
                st.bar_chart(fire_ozet, color="#FF4B4B")
    else: st.info("Analiz için veri bulunamadı.")

# --- 5. RAPORLAR ---
elif menu == "📄 Raporlar":
    st.subheader("📄 Gelişmiş Üretim Raporu")
    df_full = pd.concat([pd.DataFrame(st.session_state.db), pd.DataFrame(st.session_state.arsiv_db)], ignore_index=True)
    
    if not df_full.empty:
        def calc_perc(part, total): return f"%{round((part / total * 100), 1)}" if total > 0 else "%0"

        # Hesaplamalar
        fire_cols_r = ['Yırtık', 'Çatlak', 'Hava Boşluğu', 'Kalıp Kaçırma']
        df_full['Hata_Top'] = df_full[df_full.columns.intersection(fire_cols_r)].sum(axis=1)
        df_full['Sağlam'] = df_full['Fiili'] - df_full['Hata_Top']
        df_full['Kalite %'] = df_full.apply(lambda x: calc_perc(x['Sağlam'], x['Fiili']), axis=1)
        df_full['Yırtık %'] = df_full.apply(lambda x: calc_perc(x['Yırtık'], x['Fiili']), axis=1)
        df_full['Çatlak %'] = df_full.apply(lambda x: calc_perc(x['Çatlak'], x['Fiili']), axis=1)
        df_full['Hava %'] = df_full.apply(lambda x: calc_perc(x['Hava Boşluğu'], x['Fiili']), axis=1)
        df_full['Kalıp %'] = df_full.apply(lambda x: calc_perc(x['Kalıp Kaçırma'], x['Fiili']), axis=1)
        df_full['Tarih_DT'] = pd.to_datetime(df_full['Tarih'], format='%d.%m.%Y', errors='coerce')

        # Filtreler
        with st.expander("🔍 Rapor Filtreleme Seçenekleri", expanded=True):
            f1, f2, f3 = st.columns(3)
            f_kod = f1.multiselect("Ürün Kodu", options=sorted(df_full['Kod'].unique().tolist()))
            f_makine = f2.multiselect("Makine (Tambur)", options=sorted(df_full['Tambur'].unique().tolist()))
            f_musteri = f3.multiselect("Müşteri", options=sorted(df_full['Müşteri'].unique().tolist()))
            f4, f5 = st.columns(2)
            f_vardiya = f4.multiselect("Vardiya", options=["1. Vardiya", "2. Vardiya", "3. Vardiya"])
            min_d = df_full['Tarih_DT'].min() if not df_full['Tarih_DT'].isnull().all() else datetime.now()
            max_d = df_full['Tarih_DT'].max() if not df_full['Tarih_DT'].isnull().all() else datetime.now()
            start_date, end_date = f5.date_input("Tarih Aralığı", [min_d, max_d])

        # Filtre uygula
        filtered_df = df_full[
            (df_full['Tarih_DT'].dt.date >= start_date) &
            (df_full['Tarih_DT'].dt.date <= end_date)
        ]
        if f_kod: filtered_df = filtered_df[filtered_df['Kod'].isin(f_kod)]
        if f_makine: filtered_df = filtered_df[filtered_df['Tambur'].isin(f_makine)]
        if f_musteri: filtered_df = filtered_df[filtered_df['Müşteri'].isin(f_musteri)]
        if f_vardiya: filtered_df = filtered_df[filtered_df['Vardiya'].isin(f_vardiya)]

        # Sütun sırası — mantıklı ve koordineli
        all_cols = [
            "Tarih", "Saat", "Vardiya", "Tambur",
            "Kod", "Müşteri",
            "Operatör 1", "Operatör 2", "Operatör 3", "Kaydeden",
            "Başlangıç", "Bitiş", "Duruş Süresi", "Duruş Nedeni", "Toplam Süre", "Net Üretim Süresi",
            "Fiili", "Sağlam", "Yırtık", "Çatlak", "Hava Boşluğu", "Kalıp Kaçırma",
            "Kalite %", "Yırtık %", "Çatlak %", "Hava %", "Kalıp %"
        ]
        final_cols = [c for c in all_cols if c in filtered_df.columns]
        display_df = filtered_df[final_cols].fillna("-")

        # Özet satırı
        toplam_fiili = int(filtered_df['Fiili'].sum())
        toplam_saglam = int(filtered_df['Sağlam'].sum())
        toplam_fire = int(filtered_df['Hata_Top'].sum())
        genel_kalite = calc_perc(toplam_saglam, toplam_fiili)
        toplam_durus = int(filtered_df['Duruş Süresi'].sum()) if 'Duruş Süresi' in filtered_df.columns else 0

        st.markdown(f"""
        <div style="background-color:#1a3a5a; padding:12px; border-radius:8px; border-left:6px solid #00BFFF; margin-bottom:15px;">
            <span style="color:#00BFFF; font-weight:bold;">📊 Filtrelenmiş Özet → </span>
            <span style="color:white;">
            Toplam Kayıt: <b>{len(display_df)}</b> &nbsp;|&nbsp;
            Fiili: <b>{toplam_fiili}</b> &nbsp;|&nbsp;
            Sağlam: <b>{toplam_saglam}</b> &nbsp;|&nbsp;
            Fire: <b>{toplam_fire}</b> &nbsp;|&nbsp;
            Kalite: <b>{genel_kalite}</b> &nbsp;|&nbsp;
            Toplam Duruş: <b>{toplam_durus} dk</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        excel_out = io.BytesIO()
        with pd.ExcelWriter(excel_out, engine='xlsxwriter') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Uretim_Raporu')
        try:
            bas_str = start_date.strftime("%d.%m.%Y")
            bit_str = end_date.strftime("%d.%m.%Y")
            excel_dosya_adi = f"FKK_Rapor_{bas_str}_{bit_str}.xlsx"
        except:
            excel_dosya_adi = "FKK_Rapor.xlsx"
        st.download_button("📥 Excel Raporu İndir", excel_out.getvalue(), excel_dosya_adi, use_container_width=True)

    else: st.info("Raporlanacak veri bulunamadı.")

# --- 6. YÖNETİM ---
elif menu == "⚙️ Yönetim":
    st.subheader("⚙️ Sistem Yönetimi")

    yon_sekme = st.radio("", ["👥 Personel Yönetimi", "📦 Ürün Yönetimi", "🔐 Şifre Yönetimi", "🛠️ Sistem İşlemleri"], horizontal=True)
    st.markdown("---")

    # --- PERSONEL YÖNETİMİ ---
    if yon_sekme == "👥 Personel Yönetimi":
        personel_db = st.session_state.personel_db

        st.markdown("#### ➕ Yeni Personel Ekle")
        with st.container(border=True):
            p1, p2, p3 = st.columns(3)
            yeni_ad = p1.text_input("Personel Adı Soyadı")
            yeni_rol = p2.selectbox("Rol", ["Operatör", "Sorumlu Personel", "Yönetim"])
            yeni_durum = p3.selectbox("Durum", ["Aktif", "Pasif"])
            if st.button("✅ Personel Ekle", use_container_width=True):
                if yeni_ad.strip() == "":
                    st.warning("Personel adı boş olamaz!")
                elif any(p['ad'] == yeni_ad.strip() for p in personel_db):
                    st.warning("Bu isimde personel zaten mevcut!")
                else:
                    personel_db.append({"ad": yeni_ad.strip(), "rol": yeni_rol, "durum": yeni_durum})
                    save_data("personel.json", personel_db)
                    st.session_state.personel_db = personel_db
                    aktif_ops = [p['ad'] for p in personel_db if p.get('durum') == 'Aktif' and p.get('rol') in ['Operatör', 'Sorumlu Personel']]
                    st.session_state.sorumlu_listesi = aktif_ops
                    save_data("sorumlular.json", aktif_ops)
                    st.success(f"{yeni_ad} eklendi!"); st.rerun()

        st.markdown("#### 📋 Personel Listesi")
        if personel_db:
            for i, p in enumerate(personel_db):
                ad = p['ad']
                rol = p['rol']
                durum = p['durum']
                renk = "🟢" if durum == "Aktif" else "🔴"
                with st.container(border=True):
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
                    c1.write(f"👤 **{ad}**")
                    c2.write(f"🏷️ {rol}")
                    c3.write(f"{renk} {durum}")
                    yeni_d = c4.selectbox("", ["Aktif", "Pasif"], index=0 if durum == "Aktif" else 1, key=f"pd_{i}", label_visibility="collapsed")
                    if c5.button("💾", key=f"pg_{i}", help="Güncelle"):
                        personel_db[i]['durum'] = yeni_d
                        save_data("personel.json", personel_db)
                        aktif_ops = [p['ad'] for p in personel_db if p.get('rol') in ["Operatör", "Sorumlu Personel"] and p.get('durum') == "Aktif"]
                        st.session_state.sorumlu_listesi = aktif_ops
                        save_data("sorumlular.json", aktif_ops)
                        st.success(f"{ad} güncellendi!"); st.rerun()
                    if c6.button("🗑️", key=f"sil_{i}", help="Sil"):
                        personel_db.pop(i)
                        save_data("personel.json", personel_db)
                        aktif_ops = [p['ad'] for p in personel_db if p.get('rol') in ["Operatör", "Sorumlu Personel"] and p.get('durum') == "Aktif"]
                        st.session_state.sorumlu_listesi = aktif_ops
                        save_data("sorumlular.json", aktif_ops)
                        st.success(f"{ad} silindi!"); st.rerun()
        else:
            st.info("Henüz personel eklenmemiş.")

    # --- ÜRÜN YÖNETİMİ ---
    elif yon_sekme == "📦 Ürün Yönetimi":
        st.markdown("#### ➕ Yeni Ürün Ekle")
        with st.container(border=True):
            u1, u2, u3 = st.columns(3)
            yeni_kod = u1.text_input("Ürün Kodu")
            yeni_musteri = u2.text_input("Müşteri Adı")
            yeni_kesim = u3.number_input("Kesim Adeti", min_value=1, step=1, value=1)
            if st.button("✅ Ürün Ekle", use_container_width=True):
                if yeni_kod.strip() == "" or yeni_musteri.strip() == "":
                    st.warning("Ürün kodu ve müşteri adı boş olamaz!")
                elif yeni_kod.strip() in st.session_state.kod_musteri_dict:
                    st.warning("Bu ürün kodu zaten mevcut!")
                else:
                    st.session_state.kod_musteri_dict[yeni_kod.strip()] = yeni_musteri.strip()
                    save_data("urunler.json", st.session_state.kod_musteri_dict)
                    # Kesim adetini de kaydet
                    kesim_db = load_data("kesim_adetleri.json", {})
                    kesim_db[yeni_kod.strip()] = int(yeni_kesim)
                    save_data("kesim_adetleri.json", kesim_db)
                    st.success(f"Ürün {yeni_kod} eklendi!"); st.rerun()

        st.markdown("#### 📋 Mevcut Ürünler")
        arama = st.text_input("🔍 Ürün Kodu veya Müşteri Ara")
        kesim_db_goster = load_data("kesim_adetleri.json", kesim_adetleri)
        urun_listesi = [
            {"Kod": k, "Müşteri": v, "Kesim Adeti": kesim_db_goster.get(k, 1)}
            for k, v in st.session_state.kod_musteri_dict.items()
            if arama.lower() in k.lower() or arama.lower() in v.lower()
        ]
        if urun_listesi:
            kesim_db_sil = load_data("kesim_adetleri.json", kesim_adetleri)
            for j, u in enumerate(urun_listesi):
                with st.container(border=True):
                    cu1, cu2, cu3, cu4 = st.columns([2, 2, 1, 1])
                    cu1.write(f"📦 **{u['Kod']}**")
                    cu2.write(f"👥 {u['Müşteri']}")
                    cu3.write(f"✂️ {u['Kesim Adeti']}")
                    if cu4.button("🗑️", key=f"usil_{j}", help="Ürünü Sil"):
                        del st.session_state.kod_musteri_dict[u['Kod']]
                        save_data("urunler.json", st.session_state.kod_musteri_dict)
                        if u['Kod'] in kesim_db_sil:
                            del kesim_db_sil[u['Kod']]
                            save_data("kesim_adetleri.json", kesim_db_sil)
                        st.success(f"{u['Kod']} silindi!"); st.rerun()
        else:
            st.info("Ürün bulunamadı.")

    # --- ŞİFRE YÖNETİMİ ---
    elif yon_sekme == "🔐 Şifre Yönetimi":
        # Kişi bazlı şifreler: {"Ufuk Altuncu": "sifre123", ...}
        # Rol bazlı varsayılan şifreler de tutulur
        sifre_db = load_data("sifreler.json", {
            "Yönetim": "fkk.yonetim.1957",
            "Sorumlu Personel": "fkk.sorumlu1957",
            "Operatör": "fkk.operator1957"
        })
        personel_db_s = st.session_state.get('personel_db', load_personel())

        st.markdown("#### 🔑 Kişi Bazlı Şifre Güncelle")
        with st.container(border=True):
            # Tüm personel + yönetim listesi
            yonetim_listesi = ["Ufuk Altuncu", "Emre Altuncu", "Ömer Faruk Akdoğan", "Zeki Meral"]
            tum_kisiler = yonetim_listesi + [p.get('ad','') for p in personel_db_s if p.get('ad')]
            
            kisi_sec = st.selectbox("Şifresi Değiştirilecek Kişi", tum_kisiler)
            s1, s2 = st.columns(2)
            yeni_sifre = s1.text_input("Yeni Şifre", type="password", key="yeni")
            yeni_sifre2 = s2.text_input("Yeni Şifre (Tekrar)", type="password", key="yeni2")
            
            # Mevcut şifreyi göster (yönetici onayı)
            yonetici_onay = st.text_input("Yönetim Şifresi (Onay)", type="password", key="yon_onay")
            
            if st.button("🔐 Şifreyi Güncelle", use_container_width=True):
                yon_sifre = sifre_db.get("Yönetim", "fkk.yonetim.1957")
                if yonetici_onay != yon_sifre:
                    st.error("Yönetim şifresi hatalı!")
                elif yeni_sifre != yeni_sifre2:
                    st.error("Yeni şifreler eşleşmiyor!")
                elif len(yeni_sifre) < 6:
                    st.error("Şifre en az 6 karakter olmalı!")
                else:
                    sifre_db[kisi_sec] = yeni_sifre
                    save_data("sifreler.json", sifre_db)
                    st.success(f"{kisi_sec} şifresi güncellendi!")

        st.caption("⚠️ Kişiye özel şifre tanımlanmamışsa sistem varsayılan rol şifresi geçerlidir.")

    # --- SİSTEM İŞLEMLERİ ---
    elif yon_sekme == "🛠️ Sistem İşlemleri":

        sifre_db_sis = load_data("sifreler.json", {"Yönetim": "fkk.yonetim.1957"})

        # 1. GÜNÜ KAPAT VE ARŞİVLE
        st.markdown("#### 📁 Günü Kapat ve Arşivle")
        with st.container(border=True):
            st.write("Günün aktif kayıtları arşive taşınır, aktif kayıtlar temizlenir. Arşiv korunur.")
            st.info(f"Aktif kayıt: **{len(st.session_state.db)}** | Arşivdeki kayıt: **{len(st.session_state.arsiv_db)}**")
            if st.button("🔴 Günü Kapat ve Arşivle", use_container_width=True):
                st.session_state.arsiv_db.extend(st.session_state.db)
                save_data("arsiv.json", st.session_state.arsiv_db)
                st.session_state.db = []
                save_data("kayitlar.json", [])
                st.success("Gün kapatıldı, kayıtlar arşive alındı."); st.rerun()

        st.markdown("---")

        # 2. ARŞİVİ DIŞA AKTAR VE TEMİZLE
        st.markdown("#### 📤 Arşivi Dışa Aktar ve Temizle")
        with st.container(border=True):
            st.write("Tüm arşiv Excel'e aktarılır, ardından arşiv temizlenir. Aktif kayıtlar etkilenmez.")
            st.info(f"Arşivdeki kayıt: **{len(st.session_state.arsiv_db)}**")
            arsiv_onay_sifre = st.text_input("Yönetim Şifresi", type="password", key="arsiv_pwd")
            arsiv_onay = st.checkbox("Arşivin temizleneceğini anlıyorum, Excel dosyasını indireceğim.")
            if st.button("📤 Arşivi Dışa Aktar ve Temizle", use_container_width=True):
                if arsiv_onay_sifre != sifre_db_sis.get("Yönetim", "fkk.yonetim.1957"):
                    st.error("Hatalı şifre!")
                elif not arsiv_onay:
                    st.warning("Lütfen onay kutusunu işaretleyin.")
                elif not st.session_state.arsiv_db:
                    st.warning("Arşivde kayıt bulunmuyor.")
                else:
                    # Excel oluştur
                    df_arsiv = pd.DataFrame(st.session_state.arsiv_db)
                    excel_arsiv = io.BytesIO()
                    with pd.ExcelWriter(excel_arsiv, engine='xlsxwriter') as writer:
                        df_arsiv.to_excel(writer, index=False, sheet_name='Arsiv')
                    # İndir butonu göster
                    st.download_button(
                        "📥 Arşivi İndir (Excel)",
                        excel_arsiv.getvalue(),
                        f"FKK_Arsiv_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                        use_container_width=True
                    )
                    # Arşivi temizle
                    st.session_state.arsiv_db = []
                    save_data("arsiv.json", [])
                    st.success("Arşiv dışa aktarıldı ve temizlendi.")
                    st.rerun()

        st.markdown("---")

        # 3. SİSTEMİ SIFIRLA
        st.markdown("#### 🗑️ Sistemi Sıfırla")
        with st.container(border=True):
            st.error("⚠️ Bu işlem TÜM kayıtları ve arşivi kalıcı olarak siler. Geri alınamaz!")
            sifirla_sifre = st.text_input("Yönetim Şifresi", type="password", key="sifirla_pwd")
            onay = st.checkbox("Tüm verilerin silineceğini ve bu işlemin geri alınamayacağını anlıyorum.")
            if st.button("🗑️ Sistemi Sıfırla", use_container_width=True):
                if sifirla_sifre != sifre_db_sis.get("Yönetim", "fkk.yonetim.1957"):
                    st.error("Hatalı şifre!")
                elif not onay:
                    st.warning("Lütfen onay kutusunu işaretleyin.")
                else:
                    st.session_state.db = []
                    st.session_state.arsiv_db = []
                    save_data("kayitlar.json", [])
                    save_data("arsiv.json", [])
                    # Makine verilerini tamamen sıfırla
                    bos_makine = {}
                    for i in range(1, 6):
                        m_name = f"Tambur {i}"
                        bos_makine[m_name] = {
                            "durum": "Duruş",
                            "personel": "Seçilmedi",
                            "operatör1": "Seçilmedi",
                            "operatör2": "Seçilmedi",
                            "operatör3": "Seçilmedi",
                            "hedef": 0,
                            "vardiya": "-",
                            "tarih": "-",
                            "planlayan": "-"
                        }
                    st.session_state.makine_verileri = bos_makine
                    save_data("makine_statu.json", bos_makine)
                    st.success("Sistem sıfırlandı."); st.rerun()
