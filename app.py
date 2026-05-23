import streamlit as st
import gspread
from datetime import datetime
import pandas as pd
from streamlit_calendar import calendar
import time

# --- TEMA VE SAYFA AYARLARI ---
st.set_page_config(page_title="Asmira Komuta Merkezi", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
     /* YAN MENÜYÜ SABİTLE VE KAPATMA OKUNU GİZLE */
     [data-testid="collapsedControl"] { display: none !important; }
     [data-testid="stSidebarCollapseButton"] { display: none !important; }
     
     /* YAN MENÜ GENİŞLİĞİNİ DARALT VE KİLİTLE (Çizgiyi sola yaklaştırdık) */
     [data-testid="stSidebar"] { min-width: 210px !important; max-width: 210px !important; width: 210px !important; background-color: #f4f5f7; border-right: 1px solid #e1e4e8; }
     [data-testid="stSidebarResizer"] { display: none !important; }

     /* GENEL ARKA PLAN VE YAZI TİPİ */
     .stApp { background-color: #fcfcfc; }
          
     /* SOL MENÜ ŞEFFAF VE ZARİF TASARIM */
     [data-testid="stSidebar"] label[data-baseweb="radio"] {
          display: block !important;
          width: 100% !important;
          margin-bottom: 5px !important;
          padding: 12px 5px !important; 
          background-color: transparent !important;
          border: none !important;
          border-radius: 6px !important;
          transition: background-color 0.3s ease, color 0.3s ease !important;
          cursor: pointer !important;
     }
          
     /* YUVARLAK RADYO BUTONLARINI VE KIRMIZI NOKTAYI KÖKÜNDEN YOK ET */
     [data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
          display: none !important;
      }
          
     /* MENÜ YAZILARINI GÖRÜNÜR YAP, SOLA YASLA VE TEK SATIRDA TUT */
     [data-testid="stSidebar"] label[data-baseweb="radio"] p {
           margin: 0 !important; 
           padding-left: 10px !important; 
           color: #495057 !important; 
           font-size: 16px !important; 
           font-weight: 600 !important; 
           white-space: nowrap !important;
           display: block !important;
      }
      
     [data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
           background-color: rgba(0, 123, 255, 0.08) !important;
     }
     [data-testid="stSidebar"] label[data-baseweb="radio"]:hover p {
           color: #007BFF !important;
     }
     
     /* SEÇİLİ MENÜ EFEKTİ */
     [data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] {
          background-color: rgba(0, 86, 179, 0.1) !important;
     }
     [data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] p {
          color: #0056b3 !important; font-weight: 700 !important;
     }
          
     /* ANA EKRAN İÇİN 3'LÜ BÜYÜK METRİK HATTI */
     .minimal-stats {
          display: flex; justify-content: space-around; padding: 30px 0;
          border-bottom: 1px solid #e1e4e8; margin-bottom: 25px; background-color: transparent;
     }
     .stat-item { text-align: center; flex: 1; padding: 0 10px; }
     .stat-value { font-size: 38px; font-weight: 700; color: #0056b3; display: block; line-height: 1; }
     .stat-label { font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-top: 10px; }
     .stat-divider { border-left: 1px solid #e1e4e8; height: 50px; align-self: center; }
     
     .section-header { font-size: 20px !important; font-weight: 600 !important; color: #2c3e50; }
     hr { margin: 10px 0 20px 0 !important; border-top: 1px solid #e1e4e8 !important; }
          
     /* BUTON TASARIMLARI (KURUMSAL MAVİ) */
     button[kind="primary"], .stFormSubmitButton > button {
           background-color: #0056b3 !important; color: white !important; border-radius: 4px !important;
           height: 42px !important; width: 100% !important; border: none !important; transition: background-color 0.3s ease !important;
     }
     button[kind="primary"]:hover, .stFormSubmitButton > button:hover { background-color: #004494 !important; }
          
     /* SEKMELERİN (TABS) TASARIMI */
     button[data-baseweb="tab"] p { color: #495057 !important; font-weight: 500 !important; }
     button[data-baseweb="tab"]:hover p { color: #0056b3 !important; }
     button[data-baseweb="tab"][aria-selected="true"] p { color: #0056b3 !important; font-weight: 600 !important; }
     div[data-baseweb="tab-highlight"] { background-color: #0056b3 !important; }
          
     /* --------------------------------------------------- */
     /* YENİ LİSTE TASARIMI: SIFIR GİZLİ BOŞLUK, TAM HİZALAMA */
     /* --------------------------------------------------- */
     .liste-kutusu { 
          max-height: 800px; 
          overflow-y: auto; 
          padding-right: 8px; 
          margin-top: 0px !important; 
     }
     .satir-tasarimi {
          display: flex; 
          justify-content: space-between; 
          align-items: center; 
          padding-bottom: 12px; 
          margin-bottom: 12px; 
          border-bottom: 1px solid #f0f2f6; 
     }
          
     /* INPUT ODAKLANMA EFEKTİ */
     div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
          border-color: #0056b3 !important; box-shadow: 0 0 0 1px #0056b3 !important;
     }

     /* TAKVİM YAZILARI KÜÇÜLTME VE KIRMIZI YAPMA */
     .fc-event {
          background-color: transparent !important; 
          border: 1px solid #ff4b4b !important;
          margin-bottom: 2px !important;
     }
     .fc-event-title {
          color: #ff0000 !important;
          font-size: 10px !important;
          font-weight: bold !important;
          white-space: normal !important;
          line-height: 1.1 !important;
          padding: 1px 2px !important;
     }
</style> 
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS BAĞLANTI ---
@st.cache_resource
def baglanti_kur():
     try:
          client = gspread.oauth(credentials_filename='client_secret.json', authorized_user_filename='token.json')
          return client.open("Asmira_Veritabani")
     except Exception as e:
          st.error(f"Bağlantı Hatası: {e}")
          return None

# --- VERİ İŞLEME FONKSİYONLARI ---
@st.cache_data(ttl=2)
def veri_cek_taze(sayfa_adi):
     sp = baglanti_kur()
     if sp:
          try: return sp.worksheet(sayfa_adi).get_all_records()
          except: return []
     return []

def veri_yaz(sayfa_adi, satir):
     sp = baglanti_kur()
     if sp:
          sp.worksheet(sayfa_adi).append_row(satir)
          st.cache_data.clear()

def veri_guncelle(sayfa_adi, eski_unvan, yeni_satir):
     sp = baglanti_kur()
     if sp:
          try:
               ws = sp.worksheet(sayfa_adi)
               cell = ws.find(eski_unvan)
               if cell:
                    en_harf = chr(64 + len(yeni_satir))
                    range_label = f"A{cell.row}:{en_harf}{cell.row}"
                    ws.update(range_label, [yeni_satir])
                    st.cache_data.clear()
                    return True
          except: return False
     return False

def veri_sil(sayfa_adi, unvan_sil):
     sp = baglanti_kur()
     if sp:
          try:
               ws = sp.worksheet(sayfa_adi)
               cell = ws.find(unvan_sil)
               if cell:
                    ws.delete_rows(cell.row)
                    st.cache_data.clear()
                    return True
          except: return False
     return False

# --- VERİLERİ ÇEK ---
ana_data = veri_cek_taze("ANA_EKRAN")
k_data = veri_cek_taze("KURULUS_YONETIMI")
t_data = veri_cek_taze("SATIS_VE_TEKLIF")
op_data = veri_cek_taze("OPERASYON_MERKEZI")

# --- SOL MENÜ ---
with st.sidebar:
     try: st.image("logo.png", width=160)
     except: st.title("ASMİRA")
     st.markdown("<br>", unsafe_allow_html=True)
     menu = st.radio("", ["Ana Ekran", "Kuruluş Yönetimi", "Satış ve Teklif", "Operasyon Merkezi", "Sistem Ayarları"])

# ==========================================
# 1. ANA EKRAN
# ==========================================
if menu == "Ana Ekran":
     df_op = pd.DataFrame(op_data) if op_data else pd.DataFrame(columns=["Kuruluş Unvanı"])
     df_k = pd.DataFrame(k_data) if k_data else pd.DataFrame(columns=["Kuruluş Unvanı"])
     df_t = pd.DataFrame(t_data) if t_data else pd.DataFrame(columns=["Kuruluş Unvanı"])
     
     toplam_k = len(df_k)
     bekleyen_t = len(df_t)
     toplam_is = len(df_op)
          
     st.markdown(f"""
     <div class="minimal-stats">
          <div class="stat-item"><span class="stat-value">{toplam_k}</span><span class="stat-label">TOPLAM KURULUŞ</span></div>
          <div class="stat-divider"></div>
          <div class="stat-item"><span class="stat-value">{bekleyen_t}</span><span class="stat-label">BEKLEYEN TEKLİFLER</span></div>
          <div class="stat-divider"></div>
          <div class="stat-item"><span class="stat-value">{toplam_is}</span><span class="stat-label">DEVAM EDEN İŞLER</span></div>
     </div>""", unsafe_allow_html=True)

     col_left, col_right = st.columns([2.1, 1])
     
     with col_left:
          st.markdown('<span class="section-header">Operasyon Takvimi</span><hr>', unsafe_allow_html=True)
          cal_events = []
          for r in ana_data:
               try:
                    if 'Geçerlilik Tarihi' in r and r['Geçerlilik Tarihi']:
                         d = datetime.strptime(str(r['Geçerlilik Tarihi']), "%d.%m.%Y").strftime("%Y-%m-%d")
                         tam_ad = str(r.get('Kuruluş Unvanı','Bilinmiyor'))
                         kisa_ad = " ".join(tam_ad.split()[:2]) if len(tam_ad.split()) >= 2 else tam_ad
                         cal_events.append({"title": kisa_ad, "start": d, "backgroundColor": "transparent", "textColor": "red", "borderColor": "red"})
               except: continue
          
          takvim_css = """
          .fc-event-title { font-size: 10px !important; font-weight: bold !important; color: red !important; white-space: normal !important; word-wrap: break-word !important; line-height: 1.2 !important; padding: 2px !important; }
          .fc-event { white-space: normal !important; word-wrap: break-word !important; }
          .fc-daygrid-event { white-space: normal !important; align-items: flex-start !important; }
          .fc .fc-button { background: #f8f9fa !important; color: #495057 !important; border: 1px solid #ced4da !important; box-shadow: none !important; } 
          .fc .fc-button:hover { background: #e2e6ea !important; } 
          .fc .fc-button-primary { background: #0056b3 !important; color: white !important; border-color: #004494 !important; } 
          .fc .fc-button-primary:hover { background: #004494 !important; }
          """
          calendar(events=cal_events, options={"locale": "tr", "height": 800, "firstDay": 1, "buttonText": {"today": "Bugün", "month": "Ay", "week": "Hafta", "day": "Gün"}, "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,dayGridWeek,dayGridDay"}, "initialView": "dayGridMonth"}, custom_css=takvim_css)
          
     with col_right:
          st.markdown('<span class="section-header">Süresi Yaklaşanlar (Son 3 Ay)</span><hr>', unsafe_allow_html=True)
          
          if ana_data:
               df_ana = pd.DataFrame(ana_data)
               if 'Kalan Gün' in df_ana.columns:
                    df_ana['Kalan_Gun'] = pd.to_numeric(df_ana['Kalan Gün'], errors='coerce').fillna(0).astype(int)
                    df_yaklasan = df_ana[df_ana['Kalan_Gun'] <= 90]
                    
                    liste_html = '<div class="liste-kutusu">'
                    for _, r in df_yaklasan.sort_values('Kalan_Gun').iterrows():
                         tam_unvan = str(r.get("Kuruluş Unvanı", "-"))
                         kelimeler = tam_unvan.split()
                         kisa_unvan = " ".join(kelimeler[:2]) if len(kelimeler) >= 2 else tam_unvan
                         
                         # Streamlit'in kod bloğu sanmaması için HTML'i tamamen tek bir satırda birleştiriyoruz
                         liste_html += f'<div class="satir-tasarimi"><div style="font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 75%;"><span style="font-weight: 800; color: #2c3e50;">{kisa_unvan}</span><span style="color: #7f8c8d; font-weight: 500; margin-left: 5px;">| {r.get("Hizmet Türü", "-")}</span></div><div style="color: red; font-weight: 900; font-size: 13px; white-space: nowrap;">{r["Kalan_Gun"]} GÜN</div></div>'
                    
                    liste_html += '</div>'
                    st.markdown(liste_html, unsafe_allow_html=True)
          else:
               st.info("Henüz arşivlenmiş belge uyarısı yok.")

# ==========================================
# 2. KURULUŞ YÖNETİMİ
# ==========================================
elif menu == "Kuruluş Yönetimi":
     st.markdown('<span class="section-header">Kuruluş Portföyü ve Kayıt Merkezi</span>', unsafe_allow_html=True)
     st.markdown("<hr>", unsafe_allow_html=True)
          
     m_tab1, m_tab2 = st.tabs(["Kuruluş Listesi", "Yeni Kuruluş Ekle"])
          
     with m_tab1:
          if k_data:
               df_k = pd.DataFrame(k_data)
               if 'aktif_firma' not in st.session_state: st.session_state.aktif_firma = "Seçiniz..."
               if 'duzenleme_modu' not in st.session_state: st.session_state.duzenleme_modu = False
               if 'silme_onayi' not in st.session_state: st.session_state.silme_onayi = False
                         
               if st.session_state.aktif_firma == "Seçiniz...":
                    arama = st.text_input("Kuruluş Ara...", key="arama_kutusu")
                    term = arama.replace('i', 'İ').replace('ı', 'I').upper()
                    
                    u_col = df_k.columns[0]
                    df_goster = df_k[df_k[u_col].astype(str).str.contains(term, na=False)] if arama else df_k
                    st.markdown('<div class="liste-kutusu">', unsafe_allow_html=True)
                    for i, row in df_goster.iterrows():
                         unvan = str(row.iloc[0])
                         if st.button(unvan, use_container_width=True, key=f"btn_{unvan}_{i}"):
                              st.session_state.aktif_firma = unvan; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
               else:
                    if st.button("⬅️ LİSTEYE GERİ DÖN", type="primary"):
                         st.session_state.aktif_firma = "Seçiniz..."; st.session_state.duzenleme_modu = False; st.session_state.silme_onayi = False; st.rerun()
                                   
                    detay = df_k[df_k.iloc[:, 0] == st.session_state.aktif_firma].iloc[0]
                    st.subheader(f"{st.session_state.aktif_firma}")
                    st.markdown("<hr>", unsafe_allow_html=True)
                    c_tab1, c_tab2, c_tab3 = st.tabs(["Kurumsal Bilgiler", "Arşiv ve Belgeler", "Süreç Notları"])
                                   
                    with c_tab1:
                         with st.form("yerinde_edit_form", border=False):
                              c1, c2 = st.columns(2)
                              up_u = c1.text_input("Kuruluş Unvanı", value=str(detay.get('Kuruluş Unvanı','')), disabled=not st.session_state.duzenleme_modu)
                              up_v = c1.text_input("Vergi No", value=str(detay.get('Vergi No','')), disabled=not st.session_state.duzenleme_modu)
                              up_vd = c1.text_input("Vergi Dairesi", value=str(detay.get('Vergi Dairesi','')), disabled=not st.session_state.duzenleme_modu)
                              up_k = c1.text_input("Kuruluş Sahibi", value=str(detay.get('Kuruluş Sahibi','')), disabled=not st.session_state.duzenleme_modu)
                              up_kt = c1.text_input("Kuruluş Sahibi Telefon", value=str(detay.get('Kuruluş Sahibi Telefon','')), disabled=not st.session_state.duzenleme_modu)
                                             
                              up_w = c2.text_input("Web Sitesi", value=str(detay.get('Web Sitesi','')), disabled=not st.session_state.duzenleme_modu)
                              up_a = c2.text_area("Adres", value=str(detay.get('Adres','')), disabled=not st.session_state.duzenleme_modu)
                              up_m = c2.text_input("E-Mail", value=str(detay.get('E-Mail','')), disabled=not st.session_state.duzenleme_modu)
                              up_i = c2.text_input("İlgili Kişi", value=str(detay.get('İlgili Kişi','')), disabled=not st.session_state.duzenleme_modu)
                              up_t = c2.text_input("İlgili Kişi Telefon", value=str(detay.get('İlgili Kişi Telefon','')), disabled=not st.session_state.duzenleme_modu)
                                             
                              st.markdown("<hr>", unsafe_allow_html=True)
                              col_b_sol, col_b_orta, col_b_bos, col_b_sag = st.columns([1.2, 1.5, 1, 1.2])
                              if not st.session_state.duzenleme_modu:
                                   if col_b_sol.form_submit_button("BİLGİLERİ DÜZENLE"): st.session_state.duzenleme_modu = True; st.rerun()
                              else:
                                   if col_b_orta.form_submit_button("DEĞİŞİKLİKLERİ KAYDET"):
                                        y_satir = [up_u.replace('i', 'İ').upper(), up_v, up_vd.replace('i', 'İ').upper(), up_k.replace('i', 'İ').upper(), up_kt, up_w.lower(), up_a.replace('i', 'İ').upper(), up_m.lower(), up_i.replace('i', 'İ').upper(), up_t, detay.get('Kayıt Tarihi')]
                                        if veri_guncelle("KURULUS_YONETIMI", st.session_state.aktif_firma, y_satir):
                                             st.session_state.aktif_firma = up_u.replace('i', 'İ').upper(); st.session_state.duzenleme_modu = False; st.rerun()
                              if col_b_sag.form_submit_button("KAYDI SİL"): st.session_state.silme_onayi = True; st.rerun()
                         
                         if st.session_state.silme_onayi:
                              st.error("DİKKAT: Bu kuruluş kaydı tamamen silinecektir. Onaylıyor musunuz?")
                              c_onay1, c_onay2 = st.columns([1, 4])
                              if c_onay1.button("EVET, SİL"):
                                   if veri_sil("KURULUS_YONETIMI", st.session_state.aktif_firma): st.session_state.aktif_firma = "Seçiniz..."; st.session_state.silme_onayi = False; st.rerun()
                              if c_onay2.button("HAYIR, VAZGEÇ"): st.session_state.silme_onayi = False; st.rerun()
                                   
                    with c_tab2:
                         f_arsiv = [a for a in ana_data if a.get('Kuruluş Unvanı') == st.session_state.aktif_firma]
                         if f_arsiv: st.table(pd.DataFrame(f_arsiv)[["Hizmet Türü", "Geçerlilik Tarihi", "Kalan Gün"]])
                         else: st.info("Bu kuruluşa ait aktif belge kaydı bulunamadı.")
                                   
                    with c_tab3:
                         st.write("Operasyon Merkezi'nden girilen iş bilgileri ve süreç notları:")
                         f_notlar = [n for n in op_data if n.get('Kuruluş Unvanı') == st.session_state.aktif_firma]
                         for n in f_notlar:
                              st.caption(f"Tarih: {n.get('İş Başlangıç Tarihi','-')} | Sorumlu: {n.get('Sorumlu Personel','-')} | Hizmet: {n.get('Hizmet Türü','-')}")
                              st.info(n.get('Süreç Notları','-'))
          else:
               st.info("Henüz kuruluş kaydı bulunmuyor.")
          
     with m_tab2:
          st.subheader("Yeni Kuruluş Kayıt Formu")
          with st.form("yeni_kurulus_form", border=True):
               c1, c2 = st.columns(2)
               unvan = c1.text_input("Kuruluş Unvanı")
               v_no = c1.text_input("Vergi No")
               v_daire = c1.text_input("Vergi Dairesi")
               ks = c1.text_input("Kuruluş Sahibi")
               ks_tel = c1.text_input("Kuruluş Sahibi Telefon")
               web = c2.text_input("Web Sitesi")
               adr = c2.text_area("Adres")
               mail = c2.text_input("E-Mail")
               ilg = c2.text_input("İlgili Kişi")
               tel = c2.text_input("İlgili Kişi Telefon")
                         
               if st.form_submit_button("SİSTEME KAYDET"):
                    if unvan:
                         u_f = unvan.replace('i', 'İ').replace('ı', 'I').upper()
                         vd_f = v_daire.replace('i', 'İ').replace('ı', 'I').upper()
                         ks_f = ks.replace('i', 'İ').replace('ı', 'I').upper()
                         adr_f = adr.replace('i', 'İ').replace('ı', 'I').upper()
                         ilg_f = ilg.replace('i', 'İ').replace('ı', 'I').upper()
                         veri_yaz("KURULUS_YONETIMI", [u_f, v_no, vd_f, ks_f, ks_tel, web.lower(), adr_f, mail.lower(), ilg_f, tel, datetime.now().strftime("%d.%m.%Y")])
                         st.success(f"{u_f} portföye başarıyla eklendi!"); st.balloons(); time.sleep(1.5); st.rerun()
                    else:
                         st.error("Lütfen Unvan alanını doldurun.")

# ==========================================
# 3. SATIŞ VE TEKLİF
# ==========================================
elif menu == "Satış ve Teklif":
     st.markdown('<span class="section-header">Satış Süreçleri ve Teklif Yönetimi</span>', unsafe_allow_html=True)
     st.markdown("<hr>", unsafe_allow_html=True)
          
     t_tab1, t_tab2 = st.tabs(["Yeni Teklif Hazırla", "Teklif Listesi"])
          
     with t_tab1:
          st.write("Teklif taslak formu hazırlama alanı (Gelecek güncelleme).")
               
     with t_tab2:
          st.subheader("Aktif Teklifler ve İşe Devir")
          cols_t = ["Kuruluş Unvanı", "Vergi No", "Kuruluş Sahibi", "Web Sitesi", "E-Mail", "İlgili Kişi", "Telefon", "Adres", "Hizmet Bedeli"]
          df_t = pd.DataFrame(t_data) if t_data else pd.DataFrame(columns=cols_t)
          ed_t = st.data_editor(df_t, num_rows="dynamic", use_container_width=True, key="ed_t")
                    
          if st.button("TEKLİFLERİ KAYDET", type="primary"):
               sp = baglanti_kur()
               if sp:
                    ws = sp.worksheet("SATIS_VE_TEKLIF"); ws.clear(); ws.append_row(cols_t)
                    if not ed_t.empty: ws.append_rows(ed_t.values.tolist())
                    st.cache_data.clear(); st.success("Teklifler güncellendi."); st.balloons(); time.sleep(1.5); st.rerun()
                    
          st.info("Onaylanan teklifleri 'Koordinasyon Panosu' sekmesinden doğrudan göreve dönüştürebilirsiniz.")

# ==========================================
# 4. OPERASYON MERKEZİ
# ==========================================
elif menu == "Operasyon Merkezi":
     st.markdown('<span class="section-header">Operasyon Merkezi ve İş Ajandası</span>', unsafe_allow_html=True)
     st.markdown("<hr>", unsafe_allow_html=True)
          
     m_tab1, m_tab2 = st.tabs(["Koordinasyon Panosu", "Operasyon Ajandası"])
          
     with m_tab1:
          st.subheader("Doğrudan Görev Aç (Manuel İş Atama)")
          with st.form("manuel_goreg_form", border=True):
               cc1, cc2 = st.columns(2)
               f_sec = cc1.selectbox("Kuruluş Seçin", ["Seçiniz..."] + [str(k.get('Kuruluş Unvanı','')) for k in k_data])
               h_sec = cc1.selectbox("Hizmet Departmanı", ["Sistem Belgelendirme", "Ürün Belgelendirme", "Sınai Mülkiyet", "Devlet Destekleri", "Diğer Hizmetler", "Eğitim ve Sertifikasyon"])
               p_sec = cc2.selectbox("Sorumlu Personel", ["Atanmadı", "Kürşad Bey", "Ahmet Bey", "Mehmet Bey", "Nazan Hanım"])
               not_sec = cc2.text_area("İş Notu / Detaylar")
                         
               if st.form_submit_button("GÖREVİ OLUŞTUR VE BİRİME ATA"):
                    veri_yaz("OPERASYON_MERKEZI", [f_sec, h_sec, p_sec, not_sec, datetime.now().strftime("%d.%m.%Y")])
                    st.success("Görev başarıyla oluşturuldu!"); st.balloons(); time.sleep(1.5); st.rerun()
                         
          st.markdown("<br>", unsafe_allow_html=True)
          st.subheader("Genel İş Dağılımı")
          cols_op = ["Kuruluş Unvanı", "Hizmet Türü", "Sorumlu Personel", "Süreç Notları", "İş Başlangıç Tarihi"]
          df_op = pd.DataFrame(op_data) if op_data else pd.DataFrame(columns=cols_op)
          ed_is = st.data_editor(df_op, num_rows="dynamic", use_container_width=True, key="ed_is_manager")
          
          if st.button("TÜM İŞ LİSTESİNİ KAYDET", type="primary"):
               sp = baglanti_kur()
               if sp:
                    ws = sp.worksheet("OPERASYON_MERKEZI"); ws.clear(); ws.append_row(cols_op)
                    if not ed_is.empty: ws.append_rows(ed_is.values.tolist())
                    st.cache_data.clear(); st.success("İş Dağılım Listesi güncellendi."); st.balloons(); time.sleep(1.5); st.rerun()
          
     with m_tab2:
          sub_t1, sub_t2, sub_t3, sub_t4, sub_t5, sub_t6 = st.tabs(["Sistem Belgelendirme", "Ürün Belgelendirme", "Sınai Mülkiyet", "Devlet Destekleri", "Diğer Hizmetler", "Eğitim ve Sertifikasyon"])
          df_op2 = pd.DataFrame(op_data) if op_data else pd.DataFrame(columns=["Kuruluş Unvanı", "Hizmet Türü", "Sorumlu Personel", "Süreç Notları", "İş Başlangıç Tarihi"])
          
          with sub_t1: st.subheader("Sistem Belgelendirme Ajandası"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Sistem", case=False, na=False)], use_container_width=True)
          with sub_t2: st.subheader("Ürün Belgelendirme Ajandası"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Ürün", case=False, na=False)], use_container_width=True)
          with sub_t3: st.subheader("Sınai Mülkiyet Ajandası"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Sınai", case=False, na=False)], use_container_width=True)
          with sub_t4: st.subheader("Devlet Destekleri Ajandası"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Devlet", case=False, na=False)], use_container_width=True)
          with sub_t5: st.subheader("Diğer Hizmetler Ajandası"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Diğer", case=False, na=False)], use_container_width=True)
          with sub_t6: st.subheader("Eğitim ve Sertifikasyon Süreçleri"); st.dataframe(df_op2[df_op2["Hizmet Türü"].str.contains("Eğitim", case=False, na=False)], use_container_width=True)

# ==========================================
# 5. SİSTEM AYARLARI
# ==========================================
elif menu == "Sistem Ayarları":
     st.markdown('<span class="section-header">Sistem Ayarları ve Yetkilendirme</span>', unsafe_allow_html=True)
     st.markdown("<hr>", unsafe_allow_html=True)
     st.info("Bu bölüm yönetici yetkileri içindir.")
