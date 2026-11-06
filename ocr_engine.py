import pymupdf 
import pytesseract
from pytesseract import Output
from PIL import Image, ImageDraw
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def hibrit_ve_sirali_pdf_oku(pdf_yolu):
    print(f"[{pdf_yolu}] Koordinat Hafızalı (Spatial) Analiz başlatıldı...\n")
    doc = pymupdf.open(stream=pdf_yolu, filetype="pdf")
    
    tum_kelimeler = [] # Artık kelimeleri koordinat objeleri olarak tutacağız
    tam_metin_ciktisi = "" # Kontrol/Debug amaçlı düz metin

    for sayfa_no in range(len(doc)):
        sayfa = doc[sayfa_no]
        
        bloklar = sayfa.get_text("blocks")
        dijital_kelimeler = sayfa.get_text("words") # Kelime bazlı koordinatlar için
        
        sayfadaki_parcalar = [] # Format: (Y_koordinati, kelime_objeleri_listesi)
        maskelenecek_koordinatlar = []
        
        # 1. ADIM: Dijital kelimeleri koordinatlarıyla kaydet
        dijital_gruplar = {}
        for w in dijital_kelimeler:
            x0, y0, x1, y1, kelime, block_no, line_no, word_no = w
            
            if block_no not in dijital_gruplar:
                dijital_gruplar[block_no] = {'y0': y0, 'kelimeler': []}
            
            # Kelimeyi, sayfayı ve milimetrik koordinatını obje olarak kaydediyoruz
            dijital_gruplar[block_no]['kelimeler'].append({
                'text': kelime,
                'bbox': (x0, y0, x1, y1),
                'page': sayfa_no
            })
            
        for b_no, grup in dijital_gruplar.items():
            sayfadaki_parcalar.append((grup['y0'], grup['kelimeler']))

        # OCR'ın tekrar okumaması için dijital metin bloklarını maskelemeye ayır
        for blok in bloklar:
            if blok[6] == 0:
                maskelenecek_koordinatlar.append(blok[:4])
                
        # 2. ADIM: Sayfayı resme çevir ve maskele
        zoom = 300 / 72  
        mat = pymupdf.Matrix(zoom, zoom)
        pix = sayfa.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        draw = ImageDraw.Draw(img)
        for alan in maskelenecek_koordinatlar:
            x0, y0, x1, y1 = alan
            draw.rectangle([x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom], fill="white")
            
        # 3. ADIM: Geri kalan (Flat) kısımları OCR ile oku (PSM 3)
        ocr_veri = pytesseract.image_to_data(img, lang='tur', config='--psm 3', output_type=Output.DICT)
        
        ocr_satirlar = {}
        for i in range(len(ocr_veri['text'])):
            kelime = ocr_veri['text'][i].strip()
            if kelime and int(ocr_veri['conf'][i]) > -1: 
                # Zoom oranını geri bölerek PDF'in orijinal koordinatlarına (bbox) iniyoruz
                x0 = ocr_veri['left'][i] / zoom 
                y0 = ocr_veri['top'][i] / zoom
                x1 = (ocr_veri['left'][i] + ocr_veri['width'][i]) / zoom
                y1 = (ocr_veri['top'][i] + ocr_veri['height'][i]) / zoom
                
                satir_id = f"{ocr_veri['block_num'][i]}_{ocr_veri['par_num'][i]}_{ocr_veri['line_num'][i]}"
                
                if satir_id not in ocr_satirlar:
                    ocr_satirlar[satir_id] = {'y0': y0, 'kelimeler': []}
                    
                # Tesseract kelimelerini de obje olarak kaydediyoruz
                ocr_satirlar[satir_id]['kelimeler'].append({
                    'text': kelime,
                    'bbox': (x0, y0, x1, y1),
                    'page': sayfa_no
                })

        for satir in ocr_satirlar.values():
            if satir['kelimeler']:
                sayfadaki_parcalar.append((satir['y0'], satir['kelimeler']))
                
        # 4. ADIM: Blokları Y koordinatına göre yukarıdan aşağıya sırala
        sayfadaki_parcalar.sort(key=lambda x: x[0])
        
        # İç içe listeyi tek bir düz kelimeler zincirine dönüştür
        for parca in sayfadaki_parcalar:
            tum_kelimeler.extend(parca[1])
            
            # Terminalde okuyabilmemiz için düz metni de ayrıca oluşturuyoruz
            satir_metni = " ".join([k['text'] for k in parca[1]])
            tam_metin_ciktisi += satir_metni + "\n"
        
        tam_metin_ciktisi += "\n" 

    print("\n--- OBJE TABANLI (SPATIAL) METİN ÇIKTISI ---\n")
    print(tam_metin_ciktisi)
    
    # DİKKAT: Artık fonksiyon iki değer döndürüyor (Kelime Listesi ve Ham Metin)
    return tum_kelimeler, tam_metin_ciktisi