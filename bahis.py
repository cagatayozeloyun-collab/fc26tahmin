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

# --- CSS (Kayan Yazı ve Stil) ---
st.markdown("""
<style>
.main { background-color: #0e1117; color: #00ff00; font-family: 'Courier New', monospace; }
.baslik { color: #00ff00; text-align: center; font-size: 45px; font-weight: 900; text-shadow: 0 0 10px #00ff00; margin-bottom: 20px; }
.mac-kutusu { border: 2px solid #00ff00; padding: 15px; border-radius: 10px; background-color: #111; margin-bottom: 10px; }
.bitmis-mac { border: 2px solid #555; padding: 10px; background-color: #222; margin-bottom: 20px; border-left: 5px solid gold; }
.takimlar { font-size: 24px; font-weight: bold; color: white; text-align: center; }
.skor-tabela { font-size: 30px; color: gold; font-weight: 900; text-align: center; letter-spacing: 5px; }
.oran-kutusu { background-color: #222; padding: 10px; border-radius: 5px; margin-top: 5px; text-align: center; color: #aaa; font-size: 14px;}
/* Kayan Yazı Stili */
.ticker-wrap {
  width: 100%; overflow: hidden; background-color: #000; padding-top: 10px; border-bottom: 1px solid #00ff00;
}
.ticker { display: inline-block; white-space: nowrap; animation: ticker 20s infinite linear; }
.ticker-item { display: inline-block; padding: 0 2rem; font-size: 18px; color: #00ff00; font-weight: bold; }
@keyframes ticker { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
.stButton>button { width: 100%; background: #008800; color: white; font-weight: bold; height: 3em; border: 1px solid #00ff00; }
.stButton>button:hover { background: #00ff00; color: black; }
</style>
""", unsafe_allow_html=True)

# --- SABİTLER ---
GOL_ARALIKLARI = ["0", "1-2", "3-4", "5-6", "7-8", "9+"]
NEWS_FEED = [
    "KASA KAZANIR...", "GÖKALP SON PARASINI BASTI!", "MR. WHITE PİYASAYI MANİPÜLE EDİYOR...",
    "YTÜ CİNGEN BET GURURLA SUNAR...", "FC26 TURNUVASINDA NEFESLER TUTULDU!", 
    "İDDAA RAKİPLERİNİ KISKANDIRAN ORANLAR BURADA!", "BANKO KUPONLAR YATMAYA MAHKUMDUR..."
]

# --- HAFIZA ---
if 'matches' not in st.session_state: st.session_state.matches = [] 
if 'bets' not in st.session_state: st.session_state.bets = []
if 'match_id_counter' not in st.session_state: st.session_state.match_id_counter = 0

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

# --- SAYFA ÜSTÜ: KAYAN YAZI (TICKER) ---
news_html = f"""
<div class="ticker-wrap">
<div class="ticker">
  <div class="ticker-item">{'  |  '.join(NEWS_FEED)}</div>
</div>
</div>
"""
st.markdown(news_html, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🕵️ ADMİN PANELİ")
    ev_takim = st.text_input("EV SAHİBİ:")
    dep_takim = st.text_input("DEPLASMAN:")
    
    if st.button("BÜLTENE EKLE"):
        if ev_takim and dep_takim:
            m_id = st.session_state.match_id_counter
            st.session_state.matches.append({
                "id": m_id, "ev": ev_takim, "dep": dep_takim,
                "status": "open", "score_ev": None, "score_dep": None
            })
            st.session_state.match_id_counter += 1
            st.success("MAÇ AÇILDI!")
            time.sleep(0.5)
            safe_rerun()
            
    st.divider()
    if st.button("SİSTEMİ SIFIRLA"):
        st.session_state.matches = []
        st.session_state.bets = []
        st.session_state.match_id_counter = 0
        safe_rerun()

# --- BAŞLIK ---
st.markdown('<div class="baslik">💸 KAÇAK BET: CASINO ROYALE 💸</div>', unsafe_allow_html=True)
st.info("ℹ️ YENİ KURAL: Her kuponda 1 adet 'BANKO' (x2 Puan) seçme hakkın var! İyi düşün.")

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 KUPON YAP", "🔒 SONUÇ GİR (ADMİN)", "🏆 LİDERLİK & RÜTBE", "📜 GEÇMİŞ"])

# --- TAB 1: KUPON YAP ---
with tab1:
    acik_maclar = [m for m in st.session_state.matches if m['status'] == 'open']
    
    if not acik_maclar:
        st.info("⚠️ BAHİSE AÇIK MAÇ YOK.")
    else:
        kullanici = st.text_input("KUMARBAZ İSMİ:", key="bet_user")
        st.write("---")
        
        kupon_data = {} 
        
        for m in acik_maclar:
            st.markdown(f"""
            <div class="mac-kutusu">
                <div class="takimlar">{m['ev']} vs {m['dep']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            
            # 1. MAÇ SONUCU
            with c1:
                st.markdown("<div class='oran-kutusu'>MAÇ SONUCU</div>", unsafe_allow_html=True)
                ms = st.radio("Taraf:", ["EV (1)", "BERABER (X)", "DEP (2)"], key=f"ms_{m['id']}", index=None)
                ms_code = None
                if ms == "EV (1)": ms_code = 1
                elif ms == "BERABER (X)": ms_code = 0
                elif ms == "DEP (2)": ms_code = 2
            
            # 2. TOPLAM GOL
            with c2:
                st.markdown("<div class='oran-kutusu'>TOPLAM GOL</div>", unsafe_allow_html=True)
                tg_secim = st.radio("Gol Aralığı:", GOL_ARALIKLARI, key=f"tg_{m['id']}", index=None, horizontal=True)
                tg_index = GOL_ARALIKLARI.index(tg_secim) if tg_secim else None
            
            # 3. GOL FARKI
            with c3:
                st.markdown("<div class='oran-kutusu'>GOL FARKI</div>", unsafe_allow_html=True)
                gf = st.slider("Fark:", -10, 10, 0, key=f"gf_{m['id']}", help="+: Ev, -: Dep, 0: Beraber")

            # 4. BANKO (JOKER)
            with c4:
                st.markdown("<div class='oran-kutusu'>🃏 BANKO?</div>", unsafe_allow_html=True)
                is_banko = st.checkbox("x2 Puan", key=f"banko_{m['id']}", help="Sadece 1 maç için seçebilirsin!")
            
            kupon_data[m['id']] = {"ms": ms_code, "tg_idx": tg_index, "gf": gf, "banko": is_banko}
            st.divider()
            
        if st.button("KUPONU YATIR 💵"):
            hata_mesajlari = []
            banko_sayisi = sum([1 for x in kupon_data.values() if x['banko']])
            
            if not kullanici: 
                hata_mesajlari.append("İSİMSİZ KUPON OLMAZ!")
            
            if banko_sayisi > 1:
                hata_mesajlari.append(f"❌ SADECE 1 TANE BANKO SEÇEBİLİRSİN! (Sen {banko_sayisi} tane seçtin)")
            
            for mid, data in kupon_data.items():
                m_obj = next((x for x in acik_maclar if x['id'] == mid), None)
                mac_adi = f"{m_obj['ev']} vs {m_obj['dep']}"
                
                ms, tg, gf = data["ms"], data["tg_idx"], data["gf"]
                
                if ms is None or tg is None:
                    hata_mesajlari.append(f"❌ {mac_adi}: Eksik Seçim!")
                    continue
                    
                # MANTIK KONTROLLERİ
                if ms == 1:
                    if gf <= 0: hata_mesajlari.append(f"❌ {mac_adi}: 'Ev' dedin, Fark pozitif olmalı!")
                    if tg == 0: hata_mesajlari.append(f"❌ {mac_adi}: 'Ev' dedin, 0 gol olmaz!")
                elif ms == 2:
                    if gf >= 0: hata_mesajlari.append(f"❌ {mac_adi}: 'Dep' dedin, Fark negatif olmalı!")
                    if tg == 0: hata_mesajlari.append(f"❌ {mac_adi}: 'Dep' dedin, 0 gol olmaz!")
                elif ms == 0:
                    if gf != 0: hata_mesajlari.append(f"❌ {mac_adi}: 'Beraber' dedin, Fark 0 olmalı!")

            if hata_mesajlari:
                for err in hata_mesajlari: st.error(err)
            else:
                st.session_state.bets = [b for b in st.session_state.bets if b['user'] != kullanici]
                for mid, data in kupon_data.items():
                    st.session_state.bets.append({
                        "user": kullanici, "match_id": mid,
                        "ms": data["ms"], "tg_idx": data["tg_idx"], "gf": data["gf"], "banko": data["banko"]
                    })
                st.success(f"✅ {kullanici} KUPONU ALINDI! JOKER MAÇIN HAYIRLI OLSUN.")
                time.sleep(2)
                safe_rerun()

# --- TAB 2: ADMİN ---
with tab2:
    st.write("### 🔒 ADMİN SKOR GİRİŞİ")
    for m in st.session_state.matches:
        if m['status'] == 'open':
            st.warning(f"🟢 {m['ev']} vs {m['dep']} (OYNANIYOR)")
            c1, c2, c3 = st.columns([1,1,2])
            with c1: s_ev = st.number_input("EV", 0, key=f"s_ev_{m['id']}")
            with c2: s_dep = st.number_input("DEP", 0, key=f"s_dep_{m['id']}")
            with c3:
                st.write("")
                st.write("")
                if st.button(f"MAÇI BİTİR (ID: {m['id']})", key=f"btn_end_{m['id']}"):
                    m['score_ev'] = s_ev
                    m['score_dep'] = s_dep
                    m['status'] = 'closed'
                    st.success("SKOR GİRİLDİ!")
                    safe_rerun()
        else:
            st.success(f"🔴 {m['ev']} {m['score_ev']} - {m['score_dep']} {m['dep']} (BİTTİ)")

# --- TAB 3: LİDERLİK & RÜTBE ---
with tab3:
    st.write("### 🏆 LİDERLİK & RÜTBELER")
    leaderboard = {}
    stats = {} # {user: {'tam_isabet': 0, 'banko_tuttu': 0}}
    
    closed_matches = {m['id']: m for m in st.session_state.matches if m['status'] == 'closed'}
    
    for bet in st.session_state.bets:
        mid = bet['match_id']
        if mid in closed_matches:
            match = closed_matches[mid]
            u = bet['user']
            if u not in stats: stats[u] = {'tam_isabet': 0, 'banko_fail': 0}
            
            gev, gdep = match['score_ev'], match['score_dep']
            gms = 1 if gev > gdep else (0 if gev == gdep else 2)
            gtg_idx = get_gol_aralik_index(gev + gdep)
            gfark = gev - gdep
            
            p = 0
            # Puanlama
            p1 = 3 if bet['ms'] == gms else 0
            p2 = calculate_proximity_points(gtg_idx, bet['tg_idx'])
            p3 = calculate_proximity_points(gfark, bet['gf'])
            
            round_points = p1 + p2 + p3
            
            # Banko Çarpanı
            if bet.get('banko', False):
                round_points *= 2
                if round_points == 0: stats[u]['banko_fail'] += 1 # Bankosu yattı
            
            # İstatistik
            if p2 == 5: stats[u]['tam_isabet'] += 1 # Golü tam bildi
            
            if u not in leaderboard: leaderboard[u] = 0
            leaderboard[u] += round_points
            
    if leaderboard:
        sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        for i, (usr, score) in enumerate(sorted_lb):
            rank = i + 1
            color = "gold" if rank == 1 else ("silver" if rank == 2 else ("#cd7f32" if rank == 3 else "white"))
            
            # RÜTBE HESAPLAMA
            rutbe = ""
            user_stat = stats.get(usr, {})
            if rank == 1: rutbe += " 👑 KRAL"
            if rank == len(sorted_lb): rutbe += " 🤡 KOVA"
            if user_stat.get('tam_isabet', 0) > 1: rutbe += " 🎯 SNIPER"
            if user_stat.get('banko_fail', 0) > 0: rutbe += " 💔 HAYAL KIRIKLIĞI"
            
            card_html = f"""
            <div style='background:#222; padding:10px; margin:5px; border-left:5px solid {color}; color:{color}; font-size:20px; font-weight:bold;'>
                {rank}. {usr} <span style='font-size:14px; color:#aaa;'>{rutbe}</span>
                <span style='float:right; color:#00ff00;'>{score} P</span>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("Puan durumu bekleniyor...")

# --- TAB 4: GEÇMİŞ ---
with tab4:
    st.write("### 📜 MAÇ GEÇMİŞİ")
    closed_matches_list = [m for m in st.session_state.matches if m['status'] == 'closed']
    
    if not closed_matches_list:
        st.info("Biten maç yok.")
    else:
        for m in reversed(closed_matches_list):
            ev, dep = m['ev'], m['dep']
            sev, sdep = m['score_ev'], m['score_dep']
            
            st.markdown(f"""
            <div class="bitmis-mac">
                <div class="takimlar">{ev} vs {dep}</div>
                <div class="skor-tabela">{sev} - {sdep}</div>
            </div>
            """, unsafe_allow_html=True)
            
            mac_bahisleri = [b for b in st.session_state.bets if b['match_id'] == m['id']]
            if mac_bahisleri:
                gms = 1 if sev > sdep else (0 if sev == sdep else 2)
                gtg_idx = get_gol_aralik_index(sev + sdep)
                gfark = sev - sdep
                
                table_data = []
                for b in mac_bahisleri:
                    ums_txt = "EV" if b['ms'] == 1 else ("BER" if b['ms'] == 0 else "DEP")
                    utg_txt = GOL_ARALIKLARI[b['tg_idx']]
                    
                    p1 = 3 if b['ms'] == gms else 0
                    p2 = calculate_proximity_points(gtg_idx, b['tg_idx'])
                    p3 = calculate_proximity_points(gfark, b['gf'])
                    toplam = p1 + p2 + p3
                    
                    # Banko Gösterimi
                    banko_icon = "🃏 (x2)" if b.get('banko', False) else ""
                    if b.get('banko', False): toplam *= 2
                    
                    table_data.append({
                        "Oyuncu": b['user'] + " " + banko_icon,
                        "Tahminler": f"MS:{ums_txt} | G:{utg_txt} | F:{b['gf']}",
                        "TOPLAM PUAN": toplam
                    })
                st.table(pd.DataFrame(table_data))
