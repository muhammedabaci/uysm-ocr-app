import pymupdf 
import pytesseract
from pytesseract import Output  # Koordinat verilerini almak için eklendi
from PIL import Image, ImageDraw
import io
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def cop_metin_mi(metin):
    harf_sayisi = len(re.findall(r'[a-zA-ZğüşöçıİĞÜŞÖÇ]', metin))
    ozel_karakter_sayisi = len(re.findall(r'[^a-zA-ZğüşöçıİĞÜŞÖÇ0-9\s]', metin))
    
    if harf_sayisi == 0 and ozel_karakter_sayisi > 0:
        return True
    if ozel_karakter_sayisi > (harf_sayisi * 2): 
        return True
    return False

def hibrit_ve_sirali_pdf_oku(pdf_yolu):
    print(f"[{pdf_yolu}] Mekansal Sıralamalı (Spatial) Hibrit Analiz başlatıldı...\n")
    doc = pymupdf.open(pdf_yolu) 
    tam_metin = ""

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        bloklar = sayfa.get_text("blocks")
        
        # Bu sayfadaki TÜM metinleri (Dijital + Flat) koordinatlarıyla tutacağımız liste
        # Format: [ (y_koordinati, "metin"), (y_koordinati, "metin") ]
        sayfadaki_parcalar = [] 
        maskelenecek_koordinatlar = []
        
        # 1. ADIM: Dijital metinleri bul, Y-koordinatıyla (yukarıdan aşağı) birlikte listeye ekle
        for blok in bloklar:
            if blok[6] == 0:
                y0 = blok[1] # Bloğun Y (dikey) koordinatı
                metin = blok[4].strip()
                sayfadaki_parcalar.append((y0, metin))
                maskelenecek_koordinatlar.append(blok[:4])
                
        # 2. ADIM: Sayfayı resme çevir ve dijital metinleri beyazla maskele
        zoom = 300 / 72  
        mat = pymupdf.Matrix(zoom, zoom)
        pix = sayfa.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        draw = ImageDraw.Draw(img)
        for alan in maskelenecek_koordinatlar:
            x0, y0, x1, y1 = alan
            draw.rectangle([x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom], fill="white")
            
        # 3. ADIM: Geriye kalan (Flat) kısımları OCR'a sok (Koordinatlarıyla Birlikte!)
        # Output.DICT bize sadece metni değil, kelimelerin sayfadaki konumlarını (top, left) da verir.
        ocr_veri = pytesseract.image_to_data(img, lang='tur', output_type=Output.DICT)
        
        # Tesseract kelimeleri dağınık verebilir, onları satır satır toparlayalım:
        satirlar = {}
        for i in range(len(ocr_veri['text'])):
            kelime = ocr_veri['text'][i].strip()
            # Sadece geçerli (boş olmayan ve güvenilirlik skoru yüksek) kelimeleri al
            if kelime and int(ocr_veri['conf'][i]) > -1: 
                y_coord = ocr_veri['top'][i] / zoom # Zoom oranını geri bölüyoruz ki PDF ile eşleşsin
                satir_id = f"{ocr_veri['block_num'][i]}_{ocr_veri['par_num'][i]}_{ocr_veri['line_num'][i]}"
                
                if satir_id not in satirlar:
                    satirlar[satir_id] = {'y': y_coord, 'kelimeler': []}
                satirlar[satir_id]['kelimeler'].append(kelime)

        # Toparlanan OCR satırlarını listeye ekle
        for satir in satirlar.values():
            satir_metni = " ".join(satir['kelimeler'])
            if not cop_metin_mi(satir_metni):
                sayfadaki_parcalar.append((satir['y'], satir_metni))
                
        # 4. ADIM: MÜKEMMEL SIRALAMA (Mekansal Sorting)
        # Listedeki tüm elemanları (Dijital + Flat fark etmeksizin) Y koordinatına göre yukarıdan aşağıya sıralıyoruz
        sayfadaki_parcalar.sort(key=lambda x: x[0])
        
        # Sıralanmış listeyi tek bir metin (String) halinde birleştir
        birlestirilmis_sayfa = "\n".join([parca[1] for parca in sayfadaki_parcalar])
        tam_metin += birlestirilmis_sayfa + "\n\n"

    print("\n--- NİHAİ SIRALI METİN ÇIKTISI ---\n")
    print(tam_metin)
    return tam_metin

# Testi çalıştır:
#hibrit_ve_sirali_pdf_oku("deneme_hibrit.pdf")