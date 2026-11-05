import pymupdf 
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def hibrit_ve_sirali_pdf_oku(pdf_yolu):
    print(f"[{pdf_yolu}] Çöp Filtresiz Saf Analiz başlatıldı...\n")
    doc = pymupdf.open(pdf_yolu) 
    tam_metin = ""

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        bloklar = sayfa.get_text("blocks")
        
        sayfadaki_parcalar = [] 
        maskelenecek_koordinatlar = []
        
        # 1. ADIM: Dijital metinleri al
        for blok in bloklar:
            if blok[6] == 0:
                y0 = blok[1]
                metin = blok[4].strip()
                sayfadaki_parcalar.append((y0, metin))
                maskelenecek_koordinatlar.append(blok[:4])
                
        # 2. ADIM: Sayfayı resme çevir ve dijital metinleri maskele
        zoom = 300 / 72  
        mat = pymupdf.Matrix(zoom, zoom)
        pix = sayfa.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        draw = ImageDraw.Draw(img)
        for alan in maskelenecek_koordinatlar:
            x0, y0, x1, y1 = alan
            draw.rectangle([x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom], fill="white")
            
        # 3. ADIM: Kalan kısımları OCR'a sok
        ocr_veri = pytesseract.image_to_data(img, lang='tur', config='--psm 3', output_type=Output.DICT)
        
        satirlar = {}
        for i in range(len(ocr_veri['text'])):
            kelime = ocr_veri['text'][i].strip()
            if kelime and int(ocr_veri['conf'][i]) > -1: 
                y_coord = ocr_veri['top'][i] / zoom 
                satir_id = f"{ocr_veri['block_num'][i]}_{ocr_veri['par_num'][i]}_{ocr_veri['line_num'][i]}"
                
                if satir_id not in satirlar:
                    satirlar[satir_id] = {'y': y_coord, 'kelimeler': []}
                satirlar[satir_id]['kelimeler'].append(kelime)

        # ÇÖP FİLTRESİ TAMAMEN KALDIRILDI - Ne okunduysa doğrudan ekleniyor
        for satir in satirlar.values():
            satir_metni = " ".join(satir['kelimeler'])
            if satir_metni: # Sadece tamamen boş değilse ekle
                sayfadaki_parcalar.append((satir['y'], satir_metni))
                
        # 4. ADIM: Sadece Y koordinatına göre yukarıdan aşağıya sıralama
        sayfadaki_parcalar.sort(key=lambda x: x[0])
        
        birlestirilmis_sayfa = "\n".join([parca[1] for parca in sayfadaki_parcalar])
        tam_metin += birlestirilmis_sayfa + "\n\n"

    print("\n--- NİHAİ SIRALI METİN ÇIKTISI ---\n")
    print(tam_metin)
    return tam_metin