import streamlit as st
import pymupdf
import io
from PIL import Image
from ocr_engine import hibrit_ve_sirali_pdf_oku
from diff_engine import metinleri_karsilastir

# Sayfayı geniş modda başlat
st.set_page_config(layout="wide", page_title="Hukuki Doküman OCR ve Kıyaslama")

st.title("Hukuki Doküman OCR ve Karşılaştırma Sistemi")
st.markdown("İki farklı PDF dosyasını yükleyin, sistem değişen kısımları fiziksel koordinatlarında renklendirsin.")

# Arayüz: Dosya Yükleyiciler
col1, col2 = st.columns(2)
with col1:
    orijinal_pdf_file = st.file_uploader("Orijinal Belge", type=["pdf"])
with col2:
    yeni_pdf_file = st.file_uploader("Yeni (Değiştirilmiş) Belge", type=["pdf"])

# Boyama Fonksiyonu (Şeffaflık Eklendi)
def boyama_yap(doc, kelimeler, renk):
    for kelime in kelimeler:
        page_no = kelime['page']
        bbox = kelime['bbox']
        
        sayfa = doc[page_no]
        rect = pymupdf.Rect(bbox) 
        
        annot = sayfa.add_highlight_annot(rect)
        annot.set_colors(stroke=renk)
        annot.set_opacity(0.4) # Yarı şeffaflık: Altındaki siyah metnin cam gibi okunmasını sağlar
        annot.update()

if orijinal_pdf_file and yeni_pdf_file:
    if st.button("Belgeleri Analiz Et ve Karşılaştır", use_container_width=True):
        with st.spinner("Motorlar çalışıyor, koordinatlar eşleştiriliyor..."):
            
            orj_bytes = orijinal_pdf_file.read()
            yeni_bytes = yeni_pdf_file.read()
            
            orj_kelimeler, orj_ham_metin = hibrit_ve_sirali_pdf_oku(orj_bytes)
            yeni_kelimeler, yeni_ham_metin = hibrit_ve_sirali_pdf_oku(yeni_bytes)
            
            fark_sonuclari = metinleri_karsilastir(orj_kelimeler, yeni_kelimeler)
            
            orj_doc = pymupdf.open(stream=orj_bytes, filetype="pdf")
            yeni_doc = pymupdf.open(stream=yeni_bytes, filetype="pdf")
            
            # GÜNCEL UX MANTIĞI: Turuncu iptal edildi, sadece Pastel Kırmızı ve Pastel Yeşil var.
            for islem, obje_grubu in fark_sonuclari:
                
                # Orijinal (Eski) belgede silinen veya değişen eski her şeyi Kırmızı yap
                if islem in ['silindi', 'degisti_eski']:
                    boyama_yap(orj_doc, obje_grubu, (1, 0.4, 0.4)) # Pastel Kırmızı
                    
                # Yeni belgede eklenen veya değişerek gelen yeni her şeyi Yeşil yap
                elif islem in ['eklendi', 'degisti_yeni']:
                    boyama_yap(yeni_doc, obje_grubu, (0.4, 1, 0.4)) # Pastel Yeşil

            st.success("Analiz tamamlandı! Değişiklikler aşağıda işaretlenmiştir.")
            
            gorsel_col1, gorsel_col2 = st.columns(2)
            zoom = pymupdf.Matrix(2.0, 2.0)
            
            with gorsel_col1:
                st.subheader("Orijinal Belge")
                for sayfa_no in range(len(orj_doc)):
                    sayfa = orj_doc[sayfa_no]
                    pix = sayfa.get_pixmap(matrix=zoom)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    st.image(img, use_container_width=True)
                    
            with gorsel_col2:
                st.subheader("Yeni Belge")
                for sayfa_no in range(len(yeni_doc)):
                    sayfa = yeni_doc[sayfa_no]
                    pix = sayfa.get_pixmap(matrix=zoom)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    st.image(img, use_container_width=True)