import streamlit as st
import pymupdf
import io
from PIL import Image
from ocr_engine import hibrit_ve_sirali_pdf_oku
from diff_engine import metinleri_karsilastir

# Sayfayı geniş modda başlat (Yan yana iki belge göstereceğimiz için alan lazım)
st.set_page_config(layout="wide", page_title="Hukuki Doküman OCR ve Kıyaslama")

st.title("Hukuki Doküman OCR ve Karşılaştırma Sistemi")
st.markdown("İki farklı PDF dosyasını yükleyin, sistem değişen kısımları fiziksel koordinatlarında renklendirsin.")

# Arayüz: Dosya Yükleyiciler
col1, col2 = st.columns(2)
with col1:
    orijinal_pdf_file = st.file_uploader("Orijinal Belge", type=["pdf"])
with col2:
    yeni_pdf_file = st.file_uploader("Yeni (Değiştirilmiş) Belge", type=["pdf"])

# Boyama Fonksiyonu (PyMuPDF ile fosforlu çizim)
def boyama_yap(doc, kelimeler, renk):
    # renk formatı: RGB (0-1 arası). Örn: Kırmızı (1, 0, 0)
    for kelime in kelimeler:
        page_no = kelime['page']
        bbox = kelime['bbox']
        
        sayfa = doc[page_no]
        rect = pymupdf.Rect(bbox) # Koordinatları PyMuPDF dikdörtgenine çevir
        
        annot = sayfa.add_highlight_annot(rect)
        annot.set_colors(stroke=renk)
        annot.update()

if orijinal_pdf_file and yeni_pdf_file:
    if st.button("Belgeleri Analiz Et ve Karşılaştır", use_container_width=True):
        with st.spinner("Motorlar çalışıyor, koordinatlar eşleştiriliyor..."):
            
            # Dosyaları bellekte oku ve OCR motoruna gönder
            orj_bytes = orijinal_pdf_file.read()
            yeni_bytes = yeni_pdf_file.read()
            
            orj_kelimeler, orj_ham_metin = hibrit_ve_sirali_pdf_oku(orj_bytes)
            yeni_kelimeler, yeni_ham_metin = hibrit_ve_sirali_pdf_oku(yeni_bytes)
            
            # Diff motoruna koordinatlı objeleri gönder
            fark_sonuclari = metinleri_karsilastir(orj_kelimeler, yeni_kelimeler)
            
            # PDF'leri PyMuPDF ile tekrar aç (Üzerinde boyama yapmak için)
            orj_doc = pymupdf.open(stream=orj_bytes, filetype="pdf")
            yeni_doc = pymupdf.open(stream=yeni_bytes, filetype="pdf")
            
            # Fark sonuçlarını gez ve ilgili belgelere renk atamalarını yap
            for islem, obje_grubu in fark_sonuclari:
                if islem == 'silindi':
                    # Sadece orijinal belgede vardı, kırmızıya boya
                    boyama_yap(orj_doc, obje_grubu, (1, 0, 0)) # Kırmızı
                    
                elif islem == 'eklendi':
                    # Sadece yeni belgede var, yeşile boya
                    boyama_yap(yeni_doc, obje_grubu, (0, 1, 0)) # Yeşil
                    
                elif islem == 'degisti_eski':
                    # Orijinal belgedeki değişen eski kelimeyi sarıya boya
                    boyama_yap(orj_doc, obje_grubu, (1, 0.8, 0)) # Sarı
                    
                elif islem == 'degisti_yeni':
                    # Yeni belgedeki değişmiş yeni kelimeyi sarıya boya
                    boyama_yap(yeni_doc, obje_grubu, (1, 0.8, 0)) # Sarı

            st.success("Analiz tamamlandı! Değişiklikler aşağıda işaretlenmiştir.")
            
            # Renklendirilmiş sayfaları yan yana gösterme alanı
            gorsel_col1, gorsel_col2 = st.columns(2)
            
            # Sayfaları yüksek çözünürlüklü (zoom 2.0) resimlere çevirip ekrana bas
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