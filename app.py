import streamlit as st
import tempfile
import os

# Kapalı kutu motorlarımızı (Backend) içeri aktarıyoruz
import ocr_engine
import diff_engine

st.set_page_config(page_title="Hukuki OCR & Kıyaslama", page_icon="⚖️", layout="wide")

st.title("⚖️ Hukuki Doküman OCR ve Karşılaştırma Sistemi")
st.markdown("İki farklı PDF dosyasını yükleyin, sistem yapay zeka ve maskeleme destekli OCR kullanarak metinleri okusun ve değişen kısımları otomatik tespit etsin.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Orijinal Belge")
    orijinal_dosya = st.file_uploader("Orijinal PDF dosyasını yükleyin", type=["pdf"], key="orj")

with col2:
    st.subheader("📝 Yeni (Değiştirilmiş) Belge")
    yeni_dosya = st.file_uploader("Değiştirilmiş PDF dosyasını yükleyin", type=["pdf"], key="yni")

st.divider()

if st.button("🔍 Belgeleri Analiz Et ve Karşılaştır", type="primary", use_container_width=True):
    if orijinal_dosya is not None and yeni_dosya is not None:
        
        # Ekranda dönen bir yükleme animasyonu gösterir
        with st.spinner('Yapay Zeka ve Maskeleme (White-out) algoritmaları çalışıyor...'):
            
            # 1. ADIM: Streamlit'teki dosyaları geçici olarak diske kaydet
            # Orijinal dosya için geçici alan
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_orj:
                tmp_orj.write(orijinal_dosya.read())
                orj_path = tmp_orj.name
                
            # Yeni dosya için geçici alan
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_yni:
                tmp_yni.write(yeni_dosya.read())
                yni_path = tmp_yni.name

            try:
                # 2. ADIM: Motorları Çalıştır (Veri Boru Hattı)
                # Faz 1: Dosyaları oku ve sıralı, kusursuz metinleri (String) al
                orijinal_metin = ocr_engine.hibrit_ve_sirali_pdf_oku(orj_path)
                yeni_metin = ocr_engine.hibrit_ve_sirali_pdf_oku(yni_path)
                
                # Faz 2: Çıkan iki metni karşılaştırma motoruna sok
                fark_listesi = diff_engine.metinleri_karsilastir(orijinal_metin, yeni_metin)
                
                # 3. ADIM: Arayüz (HTML) Çıktısını Hazırla
                st.subheader("📊 Analiz Sonucu")
                
                html_cikti = "<div style='line-height: 2; font-size: 16px; font-family: Arial, sans-serif;'>"
                
                for islem, kelimeler in fark_listesi:
                    # Gelen operasyon koduna göre CSS ile renk giydirme
                    if islem == 'esit':
                        html_cikti += f"<span style='color: #333;'> {kelimeler} </span>"
                    elif islem == 'eklendi':
                        html_cikti += f"<mark style='background-color: #d4edda; color: #155724; padding: 2px 4px; border-radius: 3px;'> {kelimeler} </mark>"
                    elif islem == 'silindi' or islem == 'degisti_eski':
                        html_cikti += f"<mark style='background-color: #f8d7da; color: #721c24; text-decoration: line-through; padding: 2px 4px; border-radius: 3px;'> {kelimeler} </mark>"
                    elif islem == 'degisti_yeni':
                        html_cikti += f"<mark style='background-color: #d4edda; color: #155724; font-weight: bold; padding: 2px 4px; border-radius: 3px;'> {kelimeler} </mark>"

                html_cikti += "</div>"
                
                # Hazırlanan HTML'i ekrana güvenli bir şekilde bas
                st.markdown(html_cikti, unsafe_allow_html=True)
                
            finally:
                # İşlem bitince veya hata verirse geçici dosyaları diskten temizle (Çöp Toplama / Garbage Collection)
                os.unlink(orj_path)
                os.unlink(yni_path)
                
    else:
        st.error("Lütfen karşılaştırma yapabilmek için her iki PDF dosyasını da yükleyin!")