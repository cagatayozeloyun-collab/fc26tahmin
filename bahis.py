import streamlit as st
import pandas as pd
import time
import random

# --- GÜVENLİ RERUN ---
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# --- AYARLAR ---
st.set_page_config(page_title="YTÜ CİNGEN BET", layout="wide")

# CSS
st.markdown("""
<style>
.main { background-color: #0e1117; color: #00ff00; font-family: 'Courier New', monospace; }
.baslik { color: #00ff00; text-align: center; font-size: 45px; font-weight: 900; text-shadow: 0 0 10px #00ff00; margin-bottom: 20px; }
.mac-kutusu { border: 2px solid #00ff00; padding: 15px; border-radius: 10px; background-color: #111; margin-bottom: 10px; }
.bitmis-mac { border: 2px solid #555; padding: 10px; background-color: #222; margin-bottom: 20px; border-left: 5px solid gold; }
.canli-mac-header { background-color: #003300; padding: 10px; border-radius: 5px; margin-bottom: 5px; border: 1px solid #00ff00; color: white; font-weight: bold; }
.takimlar { font-size: 24px; font-weight: bold; color: white; text-align: center; }
.skor-tabela { font-size: 30px; color: gold; font-weight: 900; text-align: center; letter-spacing: 5px; }
.oran-kutusu { background-color: #222; padding: 10px; border-radius: 5px; margin-top: 5px; text-align: center; color: #aaa; font-size: 14px;}
.ticker-wrap { width: 100%; overflow: hidden; background-color: #000; padding-top: 10px; border-bottom: 1px solid #00ff00; }
.ticker { display: inline-block; white-space: nowrap; animation: ticker 20s infinite linear; }
.ticker-item { display: inline-block; padding: 0 2rem; font-size: 18px; color: #00ff00; font-weight: bold; }
@keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
.stButton>button { width: 100%; background: #008800; color: white; font-weight: bold; height: 3em; border: 1px solid #00ff00; }
.stButton>button:hover { background: #00ff00; color: black; }
</style>
""", unsafe_allow_html=True)

# --- SABİTLER ---
GOL_ARALIKLARI = ["0", "1-2", "3-4", "5-6", "7-8", "9+"]
IY_MS_SECENEKLER = ["1/1", "1/X", "1/2", "X/1", "X/X", "X/2", "2/1", "2/X", "2/2"]
NEWS = ["ŞİKE YOK, AFFETMEK YOK...", "KENDİ MAÇINA OYNAYAN DİSKALİFİYE OLUR...", "LİG KIZIŞIYOR...", "GURME BAHİSÇİLER BURAYA..."]

# --- HAFIZA ---
if 'matches' not in st.session_state: st.session_state.matches = [] 
if 'bets' not in st.session_state: st.session_state.bets = []
if 'teams' not in st.session_state: st.session_state.teams = [] 
if 'match_id_counter' not in st.session_state: st.session_state.match_id_counter = 0
if 'admin_ev' not in st.session_state: st.session_state.admin_ev = ""
if 'admin_dep' not in st.session_state: st.session_state.admin_dep = ""
if 'msg' not in st.session_state: st.session_state.msg = "" 

# --- YARDIMCI FONKSİYONLAR ---
def get_gol_aralik_index(toplam_gol):
    if toplam_gol == 0: return 0
    elif 1 <= toplam_gol <= 2: return 1
    elif 3 <= toplam_gol <= 4: return 2
    elif 5 <= toplam_gol <= 6: return 3
    elif 7 <= toplam_gol <= 8: return 4
    else: return 5

def calculate_proximity_points(actual, predicted):
    try:
        diff = abs(actual - predicted)
        if diff == 0: return 5  
        elif diff == 1: return 3 
        elif diff == 2: return 1 
        else: return 0           
    except: return 0

# --- CALLBACKS ---
def add_team_callback():
    yeni_takim = st.session_state.new_team_input
    if yeni_takim and yeni_takim not in st.session_state.teams:
        st.session_state.teams.append(yeni_takim)
        st.session_state.msg = f"✅ {yeni_takim} EKLENDİ!"
        st.session_state.new_team_input = "" 
    elif yeni_takim in st.session_state.teams:
        st.session_state.msg = "⚠️ BU TAKIM ZATEN VAR!"
    else:
        st.session_state.msg = "❌ BOŞ İSİM GİRİLMEZ!"

def generate_fixture_callback():
    takimlar = st.session_state.teams
    if len(takimlar) < 2:
        st.session_state.msg = "⚠️ EN AZ 2 TAKIM LAZIM!"
        return
    
    count = 0
    for ev in takimlar:
        for dep in takimlar:
            if ev != dep:
                exists = any(m['ev'] == ev and m['dep'] == dep for m in st.session_state.matches)
                if not exists:
                    m_id = st.session_state.match_id_counter
                    st.session_state.matches.append({
                        "id": m_id, "ev": ev, "dep": dep,
                        "status": "open", 
                        "score_ev": None, "score_dep": None,
                        "iy_ev": None, "iy_dep": None
                    })
                    st.session_state.match_id_counter += 1
                    count += 1
    if count > 0: st.session_state.msg = f"🚀 {count} MAÇTAN OLUŞAN FİKSTÜR HAZIR!"
    else: st.session_state.msg = "⚠️ FİKSTÜR ZATEN VAR."

def swap_callback():
    temp = st.session_state.admin_ev
    st.session_state.admin_ev = st.session_state.admin_dep
    st.session_state.admin_dep = temp
    st.session_state.msg = "↔️ Takımlar yer değiştirdi."

def add_match_callback():
    ev = st.session_state.admin_ev
    dep = st.session_state.admin_dep
    if ev and dep:
        m_id = st.session_state.match_id_counter
        st.session_state.matches.append({
            "id": m_id, "ev": ev, "dep": dep,
            "status": "open", "score_ev": None, "score_dep": None, "iy_ev": None, "iy_dep": None
        })
        st.session_state.match_id_counter += 1
        st.session_state.admin_ev = ""
        st.session_state.admin_dep = ""
        st.session_state.msg = f"✅ {ev} vs {dep} EKLENDİ!"
    else: st.session_state.msg = "❌ Takım isimlerini gir!"

def reset_system_callback():
    st.session_state.matches = []
    st.session_state.bets = []
    st.session_state.teams = []
    st.session_state.match_id_counter = 0
    st.session_state.msg = "♻️ HER ŞEY SIFIRLANDI"

# --- SAYFA ÜSTÜ ---
st.markdown(f'<div class="ticker-wrap"><div class="ticker"><div class="ticker-item">{" | ".join(NEWS)}</div></div></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ LİG YÖNETİMİ")
    st.text_input("TAKIM / OYUNCU EKLE:", key="new_team_input", on_change=add_team_callback)
    if st.session_state.teams:
        st.write("📋 **LİGDEKİ TAKIMLAR:**")
        for t in st.session_state.teams: st.write(f"- {t}")
    st.write("---")
    st.button("📅 LİGİ KUR (FİKSTÜR)", on_click=generate_fixture_callback)
    if st.session_state.msg: st.info(st.session_state.msg)
    st.divider()
    st.header("TEK MAÇ EKLE")
    st.text_input("EV SAHİBİ:", key="admin_ev")
    st.text_input("DEPLASMAN:", key="admin_dep")
    st.button("↔️ SWAP", on_click=swap_callback)
    st.button("BÜLTENE EKLE", on_click=add_match_callback)
    st.divider()
    st.button("🔥 HER ŞEYİ SIFIRLA", on_click=reset_system_callback)

# --- BAŞLIK ---
st.markdown('<div class="baslik">💸 KAÇAK BET: ETİK MOD 💸</div>', unsafe_allow_html=True)
st.info("ℹ️ KURAL: Ligdeki oyuncular kendi maçlarına bahis yapamaz! Dışarıdan izleyenler serbest.")

# --- SEKMELER ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📝 KUPON YAP", "🔒 SKOR GİR", "💸 BAHİS LİGİ", "⚽ FC26 LİGİ", "👀 CANLI", "📜 GEÇMİŞ"])

# --- TAB 1: KUPON YAP ---
with tab1:
    acik_maclar = [m for m in st.session_state.matches if m['status'] == 'open']
    if not acik_maclar: st.info("⚠️ BÜLTEN BOŞ.")
    else:
        kullanici = st.text_input("KUMARBAZ İSMİ:", key="bet_user")
        st.write("---")
        kupon_data = {} 
        for m in acik_maclar:
            st.markdown(f"<div class='mac-kutusu'><div class='takimlar'>{m['ev']} vs {m['dep']}</div></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            with c1:
                st.markdown("<div class='oran-kutusu'>🌗 İY / MS</div>", unsafe_allow_html=True)
                iy_ms = st.selectbox("Seçim:", IY_MS_SECENEKLER, key=f"iyms_{m['id']}", index=None, placeholder="Seçiniz...")
            with c2:
                st.markdown("<div class='oran-kutusu'>TOPLAM GOL</div>", unsafe_allow_html=True)
                tg_secim = st.radio("Aralık:", GOL_ARALIKLARI, key=f"tg_{m['id']}", index=None, horizontal=True)
                tg_index = GOL_ARALIKLARI.index(tg_secim) if tg_secim else None
            with c3:
                st.markdown("<div class='oran-kutusu'>GOL FARKI</div>", unsafe_allow_html=True)
                gf = st.slider("Fark:", -10, 10, 0, key=f"gf_{m['id']}", help="+: Ev, -: Dep")
            with c4:
                st.markdown("<div class='oran-kutusu'>🃏 BANKO</div>", unsafe_allow_html=True)
                is_banko = st.checkbox("x2", key=f"bnk_{m['id']}")
            kupon_data[m['id']] = {"iy_ms": iy_ms, "tg_idx": tg_index, "gf": gf, "banko": is_banko}
            st.divider()
            
        if st.button("KUPONU YATIR 💵"):
            hata_mesajlari = []
            banko_count = sum([1 for x in kupon_data.values() if x['banko']])
            
            # İsim Normalizasyonu (Büyük/Küçük harf duyarlılığını kaldırmak için)
            kullanici_clean = kullanici.strip() if kullanici else ""
            
            if not kullanici_clean: hata_mesajlari.append("İSİMSİZ KUPON OLMAZ!")
            if banko_count > 1: hata_mesajlari.append(f"❌ SADECE 1 BANKO! ({banko_count} seçtin)")
            
            for mid, data in kupon_data.items():
                m_obj = next((x for x in acik_maclar if x['id'] == mid), None)
                mac_adi = f"{m_obj['ev']} vs {m_obj['dep']}"
                
                # --- ŞİKE KONTROLÜ (YENİ!) ---
                # Eğer kullanıcının ismi Ev Sahibi veya Deplasman ile aynıysa engelle
                if kullanici_clean.lower() == m_obj['ev'].lower() or kullanici_clean.lower() == m_obj['dep'].lower():
                     hata_mesajlari.append(f"⛔ {mac_adi}: ETİK KURALI! Kendi maçına bahis yapamazsın ({kullanici_clean})!")
                     continue

                iyms, tg, gf = data["iy_ms"], data["tg_idx"], data["gf"]
                if iyms is None or tg is None:
                    hata_mesajlari.append(f"❌ {mac_adi}: Eksik Seçim!")
                    continue
                
                tahmin_ms = iyms.split("/")[1]
                if tahmin_ms == "1": 
                    if gf <= 0: hata_mesajlari.append(f"❌ {mac_adi}: MS '1' için Fark Pozitif olmalı!")
                    if tg == 0: hata_mesajlari.append(f"❌ {mac_adi}: MS '1' için Gol 0 olamaz!")
                elif tahmin_ms == "2": 
                    if gf >= 0: hata_mesajlari.append(f"❌ {mac_adi}: MS '2' için Fark Negatif olmalı!")
                    if tg == 0: hata_mesajlari.append(f"❌ {mac_adi}: MS '2' için Gol 0 olamaz!")
                elif tahmin_ms == "X": 
                    if gf != 0: hata_mesajlari.append(f"❌ {mac_adi}: MS 'X' için Fark 0 olmalı!")
                
                max_goals_map = {0:0, 1:2, 2:4, 3:6, 4:8, 5:99}
                if abs(gf) > max_goals_map[tg]:
                    hata_mesajlari.append(f"❌ {mac_adi}: İmkansız Skor! (Fark > Gol)")

            if hata_mesajlari:
                for err in hata_mesajlari: st.error(err)
            else:
                st.session_state.bets = [b for b in st.session_state.bets if b['user'] != kullanici_clean]
                for mid, data in kupon_data.items():
                    st.session_state.bets.append({
                        "user": kullanici_clean, "match_id": mid,
                        "iy_ms": data["iy_ms"], "tg_idx": data["tg_idx"], "gf": data["gf"], "banko": data["banko"]
                    })
                st.success(f"✅ {kullanici_clean} KUPONU ONAYLANDI!")
                time.sleep(2)
                safe_rerun()

# --- TAB 2: ADMİN ---
with tab2:
    st.write("### 🔒 ADMİN SKOR GİRİŞİ")
    aciklar = [m for m in st.session_state.matches if m['status'] == 'open']
    if not st.session_state.matches: st.info("Maç yok.")
    for m in aciklar:
        st.warning(f"🟢 {m['ev']} vs {m['dep']}")
        c1, c2 = st.columns(2)
        with c1: iy_ev = st.number_input("İY Ev", 0, key=f"iy_ev_{m['id']}")
        with c2: iy_dep = st.number_input("İY Dep", 0, key=f"iy_dep_{m['id']}")
        c3, c4 = st.columns(2)
        with c3: ms_ev = st.number_input("MS Ev", 0, key=f"ms_ev_{m['id']}")
        with c4: ms_dep = st.number_input("MS Dep", 0, key=f"ms_dep_{m['id']}")
        if st.button(f"MAÇI BİTİR (ID: {m['id']})", key=f"btn_end_{m['id']}"):
            if ms_ev < iy_ev or ms_dep < iy_dep: st.error("HATA: MS < İY olamaz!")
            else:
                m['score_ev'], m['score_dep'] = ms_ev, ms_dep
                m['iy_ev'], m['iy_dep'] = iy_ev, iy_dep
                m['status'] = 'closed'
                st.success("SKOR KAYDEDİLDİ!")
                safe_rerun()
        st.write("---")

# --- TAB 3: BAHİS LİGİ ---
with tab3:
    st.write("### 💸 BAHİS LİGİ (Tahminciler)")
    leaderboard = {}
    stats = {}
    closed_matches = {m['id']: m for m in st.session_state.matches if m['status'] == 'closed'}
    for bet in st.session_state.bets:
        mid = bet['match_id']
        if mid in closed_matches:
            match = closed_matches[mid]
            u = bet['user']
            if u not in stats: stats[u] = {'sniper': 0, 'banko_fail': 0}
            
            ms_ev, ms_dep = match['score_ev'], match['score_dep']
            iy_ev, iy_dep = match['iy_ev'], match['iy_dep']
            gercek_ms = "1" if ms_ev > ms_dep else ("X" if ms_ev == ms_dep else "2")
            gercek_iy = "1" if iy_ev > iy_dep else ("X" if iy_ev == iy_dep else "2")
            gercek_iyms = f"{gercek_iy}/{gercek_ms}"
            tahmin_iy, tahmin_ms = bet['iy_ms'].split("/")
            
            p_mac = 0
            if bet['iy_ms'] == gercek_iyms: p_mac = 5
            elif tahmin_ms == gercek_ms: p_mac = 3
            elif tahmin_iy == gercek_iy: p_mac = 1
            
            gtg_idx = get_gol_aralik_index(ms_ev + ms_dep)
            gfark = ms_ev - ms_dep
            p2 = calculate_proximity_points(gtg_idx, bet['tg_idx'])
            p3 = calculate_proximity_points(gfark, bet['gf'])
            
            toplam = p_mac + p2 + p3
            if bet.get('banko', False):
                toplam *= 2
                if toplam == 0: stats[u]['banko_fail'] += 1
            if p2 == 5: stats[u]['sniper'] += 1
            if u not in leaderboard: leaderboard[u] = 0
            leaderboard[u] += toplam
            
    if leaderboard:
        sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        for i, (usr, score) in enumerate(sorted_lb):
            rank = i + 1
            color = "gold" if rank == 1 else ("silver" if rank == 2 else ("#cd7f32" if rank == 3 else "white"))
            rutbe = ""
            if rank == 1: rutbe += " 👑 KRAL"
            if rank == len(sorted_lb): rutbe += " 🤡 KOVA"
            if stats[usr]['sniper'] > 0: rutbe += " 🎯 SNIPER"
            if stats[usr]['banko_fail'] > 0: rutbe += " 💔 REZİL"
            st.markdown(f"<div style='background:#222; padding:10px; margin:5px; border-left:5px solid {color}; color:{color}; font-size:20px; font-weight:bold;'>{rank}. {usr} <span style='font-size:14px; color:#aaa;'>{rutbe}</span> <span style='float:right; color:#00ff00;'>{score} P</span></div>", unsafe_allow_html=True)
    else: st.info("Puan yok.")

# --- TAB 4: FC26 PUAN DURUMU ---
with tab4:
    st.write("### ⚽ FC26 LİG TABLOSU")
    league_table = {t: {'O':0, 'G':0, 'B':0, 'M':0, 'AG':0, 'YG':0, 'AV':0, 'P':0} for t in st.session_state.teams}
    closed_list = [m for m in st.session_state.matches if m['status'] == 'closed']
    for m in closed_list:
        t1, t2 = m['ev'], m['dep']
        s1, s2 = m['score_ev'], m['score_dep']
        if t1 not in league_table: league_table[t1] = {'O':0, 'G':0, 'B':0, 'M':0, 'AG':0, 'YG':0, 'AV':0, 'P':0}
        if t2 not in league_table: league_table[t2] = {'O':0, 'G':0, 'B':0, 'M':0, 'AG':0, 'YG':0, 'AV':0, 'P':0}
        league_table[t1]['O'] += 1; league_table[t2]['O'] += 1
        league_table[t1]['AG'] += s1; league_table[t1]['YG'] += s2
        league_table[t2]['AG'] += s2; league_table[t2]['YG'] += s1
        league_table[t1]['AV'] = league_table[t1]['AG'] - league_table[t1]['YG']
        league_table[t2]['AV'] = league_table[t2]['AG'] - league_table[t2]['YG']
        if s1 > s2:
            league_table[t1]['G'] += 1; league_table[t1]['P'] += 3
            league_table[t2]['M'] += 1
        elif s1 == s2:
            league_table[t1]['B'] += 1; league_table[t1]['P'] += 1
            league_table[t2]['B'] += 1; league_table[t2]['P'] += 1
        else:
            league_table[t2]['G'] += 1; league_table[t2]['P'] += 3
            league_table[t1]['M'] += 1
    if league_table:
        df_league = pd.DataFrame.from_dict(league_table, orient='index')
        df_league = df_league.sort_values(by=['P', 'AV', 'AG'], ascending=False)
        st.table(df_league)
    else: st.info("Takım ekleyin veya maç oynayın.")

# --- TAB 5: CANLI KUPONLAR ---
with tab5:
    st.write("### 👀 KİM NE OYNADI?")
    acik_maclar_listesi = [m for m in st.session_state.matches if m['status'] == 'open']
    if not acik_maclar_listesi: st.info("Oynanan maç yok.")
    else:
        for m in acik_maclar_listesi:
            st.markdown(f"<div class='canli-mac-header'>⚽ {m['ev']} vs {m['dep']}</div>", unsafe_allow_html=True)
            bu_maca_bahisler = [b for b in st.session_state.bets if b['match_id'] == m['id']]
            if not bu_maca_bahisler: st.warning("Bahis yok.")
            else:
                canli_data = []
                for b in bu_maca_bahisler:
                    tg_text = GOL_ARALIKLARI[b['tg_idx']]
                    banko_text = "🔥 EVET" if b.get('banko', False) else "-"
                    canli_data.append({"KUMARBAZ": b['user'], "İY / MS": b['iy_ms'], "GOL": tg_text, "FARK": b['gf'], "BANKO?": banko_text})
                st.table(pd.DataFrame(canli_data))
            st.write("---")

# --- TAB 6: GEÇMİŞ ---
with tab6:
    st.write("### 📜 GEÇMİŞ")
    if not closed_list: st.info("Yok.")
    else:
        for m in reversed(closed_list):
            iy_txt = f"(İY: {m['iy_ev']}-{m['iy_dep']})"
            st.markdown(f"<div class='bitmis-mac'><div class='takimlar'>{m['ev']} vs {m['dep']}</div><div class='skor-tabela'>{m['score_ev']} - {m['score_dep']} <span style='font-size:16px; color:#aaa'>{iy_txt}</span></div></div>", unsafe_allow_html=True)
            mac_bahisleri = [b for b in st.session_state.bets if b['match_id'] == m['id']]
            if mac_bahisleri:
                ms_ev, ms_dep = m['score_ev'], m['score_dep']
                iy_ev, iy_dep = m['iy_ev'], m['iy_dep']
                gms = "1" if ms_ev > ms_dep else ("X" if ms_ev == ms_dep else "2")
                giy = "1" if iy_ev > iy_dep else ("X" if iy_ev == iy_dep else "2")
                real_iyms = f"{giy}/{gms}"
                gtg_idx = get_gol_aralik_index(ms_ev + ms_dep)
                gfark = ms_ev - ms_dep
                
                table_data = []
                for b in mac_bahisleri:
                    t_full = b['iy_ms']
                    t_iy, t_ms = t_full.split("/")
                    utg_txt = GOL_ARALIKLARI[b['tg_idx']]
                    pm = 0
                    if t_full == real_iyms: pm = 5
                    elif t_ms == gms: pm = 3
                    elif t_iy == giy: pm = 1
                    p2 = calculate_proximity_points(gtg_idx, b['tg_idx'])
                    p3 = calculate_proximity_points(gfark, b['gf'])
                    tot = pm + p2 + p3
                    if b.get('banko', False): tot *= 2
                    b_icon = "🃏" if b.get('banko', False) else ""
                    table_data.append({"Oyuncu": f"{b['user']} {b_icon}", "Tahmin": t_full, "Gol": utg_txt, "Fark": b['gf'], "Skor P": pm, "TOPLAM": tot})
                st.table(pd.DataFrame(table_data))
