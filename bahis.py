import streamlit as st
import pandas as pd
import time

# --- GÜVENLİ RERUN (Sayfa Yenileme Fonksiyonu) ---
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# --- AYARLAR ---
st.set_page_config(page_title="YTÜ CİNGEN BET", layout="wide")

# --- CSS STİLLERİ (Tek parça halinde, hatasız) ---
st.markdown("""
<style>
.main { background-color: #0e1117; color: #00ff00; font-family: 'Courier New', monospace; }
.baslik { color: #00ff00; text-align: center; font-size: 45px; font-weight: 900; text-shadow: 0 0 10px #00ff00; margin-bottom: 20px; }
.mac-kutusu { border: 2px solid #00ff00; padding: 15px; border-radius: 10px; background-color: #111; margin-bottom: 10px; }
.bitmis-mac { border: 2px solid #555; padding: 10px; background-color: #222; margin-bottom: 20px; border-left: 5px solid gold; }
.takimlar { font-size: 24px; font-weight: bold; color: white; text-align: center; }
.skor-tabela { font-size: 30px; color: gold; font-weight: 900; text-align: center; letter-spacing: 5px; }
.oran-kutusu { background-color: #222; padding: 10px; border-radius: 5px; margin-top: 5px; text-align: center; color: #aaa; font-size: 14px;}
.stButton>button { width: 100%; background: #008800; color: white; font-weight: bold; height: 3em; border: 1px solid #00ff00; }
.stButton>button:hover { background: #00ff00; color: black; }
</style>
""", unsafe_allow_html=True)

# --- SABİTLER ---
GOL_ARALIKLARI = ["0", "1-2", "3-4", "5-6", "7-8", "9+"]

# --- HAFIZA BAŞLATMA ---
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
    # 5-3-1 Puan Sistemi
    try:
        diff = abs(actual - predicted)
        if diff == 0: return 5  # Tam İsabet
        elif diff == 1: return 3 # Yakın
        elif diff == 2: return 1 # Ucundan
        else: return 0           # Karavana
    except:
        return 0

# --- YAN PANEL (ADMİN) ---
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

# --- ANA BAŞLIK ---
st.markdown('<div class="baslik">💸 KAÇAK BET: FC26 LİGİ 💸</div>', unsafe_allow_html=True)
st.info("ℹ️ PUANLAMA: Maç Sonucu (3 P) | Toplam Gol & Fark (Tam: 5P, Yakın: 3P, Uzak: 1P)")

# --- SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 KUPON YAP", "🔒 SONUÇ GİR (ADMİN)", "🏆 PUAN DURUMU", "📜 MAÇ GEÇMİŞİ"])

# --- TAB 1: KUPON YAPMA ---
with tab1:
    acik_maclar = [m for m in st.session_state.matches if m['status'] == 'open']
    
    if not acik_maclar:
        st.info("⚠️ BAHİSE AÇIK MAÇ YOK.")
    else:
        kullanici = st.text_input("KUMARBAZ İSMİ:", key="bet_user")
        st.write("---")
        
        kupon_data = {} 
        
        for m in acik_maclar:
            # Hata riskini yok etmek için değişkenleri ayırıyoruz
            ev_adi = m['ev']
            dep_adi = m['dep']
            
            # HTML'i güvenli oluştur
            st.markdown(f"""
            <div class="mac-kutusu">
                <div class="takimlar">{ev_adi} vs {dep_adi}</div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            
            # 1. MAÇ SONUCU
            with c1:
                st.markdown("<div class='oran-kutusu'>MAÇ SONUCU (ZORUNLU)</div>", unsafe_allow_html=True)
                ms = st.radio("Taraf:", ["EV (1)", "BERABER (X)", "DEP (2)"], key=f"ms_{m['id']}", index=None)
                
                # Seçimi koda çevir
                ms_code = None
                if ms == "EV (1)": ms_code = 1
                elif ms == "BERABER (X)": ms_code = 0
                elif ms == "DEP (2)": ms_code = 2
            
            # 2. TOPLAM GOL
            with c2:
                st.markdown("<div class='oran-kutusu'>TOPLAM GOL (ZORUNLU)</div>", unsafe_allow_html=True)
                tg_secim = st.radio("Gol Aralığı:", GOL_ARALIKLARI, key=f"tg_{m['id']}", index=None, horizontal=True)
                tg_index = GOL_ARALIKLARI.index(tg_secim) if tg_secim else None
            
            # 3. GOL FARKI
            with c3:
                st.markdown("<div class='oran-kutusu'>GOL FARKI (-10 / +10)</div>", unsafe_allow_html=True)
                gf = st.slider("Fark:", -10, 10, 0, key=f"gf_{m['id']}", help="+: Ev Farkı, -: Dep Farkı")
            
            kupon_data[m['id']] = {"ms": ms_code, "tg_idx": tg_index, "gf": gf}
            st.divider()
            
        if st.button("KUPONU YATIR 💵"):
            if not kullanici: 
                st.error("❌ İSİMSİZ KUPON OLMAZ!")
            else:
                eksik_maclar = []
                # Eksik kontrolü
                for mid, data in kupon_data.items():
                    if data["ms"] is None or data["tg_idx"] is None:
                        # Maç adını bul
                        m_obj = next((x for x in acik_maclar if x['id'] == mid), None)
                        if m_obj:
                            eksik_maclar.append(f"{m_obj['ev']} vs {m_obj['dep']}")
                
                if eksik_maclar:
                    st.error("❌ EKSİK SEÇİMLER VAR! LÜTFEN ŞU MAÇLARI DOLDURUN:")
                    for eksik in eksik_maclar:
                        st.write(f"- {eksik}")
                else:
                    # Eski kuponu sil ve yenisini ekle
                    st.session_state.bets = [b for b in st.session_state.bets if b['user'] != kullanici]
                    for mid, data in kupon_data.items():
                        st.session_state.bets.append({
                            "user": kullanici, "match_id": mid,
                            "ms": data["ms"], "tg_idx": data["tg_idx"], "gf": data["gf"]
                        })
                    st.success(f"✅ {kullanici} KUPONU ONAYLANDI! BOL ŞANS.")
                    time.sleep(1.5)
                    safe_rerun()

# --- TAB 2: SONUÇ GİRİŞİ ---
with tab2:
    st.write("### 🔒 ADMİN SKOR GİRİŞİ")
    for m in st.session_state.matches:
        if m['status'] == 'open':
            st.warning(f"🟢 {m['ev']} vs {m['dep']} (OYNANIYOR)")
            col_a, col_b, col_c = st.columns([1,1,2])
            with col_a: s_ev = st.number_input("EV", 0, key=f"s_ev_{m['id']}")
            with col_b: s_dep = st.number_input("DEP", 0, key=f"s_dep_{m['id']}")
            with col_c:
                st.write("") # Boşluk
                st.write("")
                if st.button(f"MAÇI BİTİR (ID: {m['id']})", key=f"btn_end_{m['id']}"):
                    m['score_ev'] = s_ev
                    m['score_dep'] = s_dep
                    m['status'] = 'closed'
                    st.success("SKOR GİRİLDİ!")
                    safe_rerun()
        else:
            st.success(f"🔴 {m['ev']} {m['score_ev']} - {m['score_dep']} {m['dep']} (BİTTİ)")

# --- TAB 3: PUAN DURUMU ---
with tab3:
    st.write("### 🏆 CANLI LİDERLİK TABLOSU")
    leaderboard = {}
    
    # Biten maçları bul
    closed_matches = {m['id']: m for m in st.session_state.matches if m['status'] == 'closed'}
    
    if not st.session_state.bets:
        st.info("Henüz hiç bahis yapılmamış.")
    
    for bet in st.session_state.bets:
        mid = bet['match_id']
        if mid in closed_matches:
            match = closed_matches[mid]
            u = bet['user']
            
            # Gerçek Sonuçlar
            gev = match['score_ev']
            gdep = match['score_dep']
            
            # Maç Sonucu (1-0-2)
            if gev > gdep: gms = 1
            elif gev == gdep: gms = 0
            else: gms = 2
            
            gtg_idx = get_gol_aralik_index(gev + gdep)
            gfark = gev - gdep
            
            # Puan Hesapla
            p = 0
            # 1. Maç Sonucu (3 Puan)
            if bet['ms'] == gms: p += 3
            # 2. Toplam Gol (5-3-1 Puan)
            p += calculate_proximity_points(gtg_idx, bet['tg_idx'])
            # 3. Gol Farkı (5-3-1 Puan)
            p += calculate_proximity_points(gfark, bet['gf'])
            
            if u not in leaderboard: leaderboard[u] = 0
            leaderboard[u] += p
            
    if leaderboard:
        # Sıralama Yap
        sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        
        for i, (usr, score) in enumerate(sorted_lb):
            rank = i + 1
            color = "gold" if rank == 1 else ("silver" if rank == 2 else ("#cd7f32" if rank == 3 else "white"))
            
            # HTML'i dışarıda hazırla
            card_html = f"""
            <div style='background:#222; padding:10px; margin:5px; border-left:5px solid {color}; color:{color}; font-size:20px; font-weight:bold;'>
                {rank}. {usr} <span style='float:right; color:#00ff00;'>{score} P</span>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    elif closed_matches:
        st.warning("Maçlar bitti ama kimse puan alamamış?!")
    else:
        st.info("Henüz sonuçlanmış maç yok.")

# --- TAB 4: GEÇMİŞ ---
with tab4:
    st.write("### 📜 MAÇ GEÇMİŞİ & DETAYLAR")
    closed_matches_list = [m for m in st.session_state.matches if m['status'] == 'closed']
    
    if not closed_matches_list:
        st.info("Biten maç yok.")
    else:
        # En son biten maç en üstte
        for m in reversed(closed_matches_list):
            ev = m['ev']
            dep = m['dep']
            sev = m['score_ev']
            sdep = m['score_dep']
            
            # Güvenli HTML
            st.markdown(f"""
            <div class="bitmis-mac">
                <div class="takimlar">{ev} vs {dep}</div>
                <div class="skor-tabela">{sev} - {sdep}</div>
            </div>
            """, unsafe_allow_html=True)
            
            mac_bahisleri = [b for b in st.session_state.bets if b['match_id'] == m['id']]
            
            if not mac_bahisleri:
                st.warning("Bu maça kimse oynamamış.")
            else:
                # Gerçek veriler
                gms = 1 if sev > sdep else (0 if sev == sdep else 2)
                gtg_idx = get_gol_aralik_index(sev + sdep)
                gfark = sev - sdep
                
                table_data = []
                for b in mac_bahisleri:
                    # Kullanıcı Tahmin Metinleri
                    ums_txt = "EV (1)" if b['ms'] == 1 else ("BER (X)" if b['ms'] == 0 else "DEP (2)")
                    utg_txt = GOL_ARALIKLARI[b['tg_idx']]
                    ugf_txt = str(b['gf'])
                    
                    # Puanlar
                    p1 = 3 if b['ms'] == gms else 0
                    p2 = calculate_proximity_points(gtg_idx, b['tg_idx'])
                    p3 = calculate_proximity_points(gfark, b['gf'])
                    toplam = p1 + p2 + p3
                    
                    table_data.append({
                        "Oyuncu": b['user'],
                        "MS (+3)": f"{ums_txt} ({p1}p)",
                        "Gol (+5)": f"{utg_txt} ({p2}p)",
                        "Fark (+5)": f"{ugf_txt} ({p3}p)",
                        "TOPLAM": toplam
                    })
                
                st.table(pd.DataFrame(table_data))
