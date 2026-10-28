import difflib

def metinleri_karsilastir(orijinal_metin, yeni_metin):
    # Metinleri boşluklardan bölerek kelime listelerine (array) dönüştürüyoruz
    orijinal_kelimeler = orijinal_metin.split()
    yeni_kelimeler = yeni_metin.split()

    # SequenceMatcher, iki listeyi yan yana koyup LCS algoritmasını çalıştırır
    matcher = difflib.SequenceMatcher(None, orijinal_kelimeler, yeni_kelimeler)
    
    # Arayüze (UI) göndereceğimiz yapılandırılmış fark listesi
    fark_verisi = []
    
    # get_opcodes() fonksiyonu bize iki metin arasındaki operasyon (değişim) türlerini döndürür
    for islem, i1, i2, j1, j2 in matcher.get_opcodes():
        if islem == 'equal':
            # Her iki belgede de aynı olan kısımlar
            fark_verisi.append(('esit', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'insert':
            # Orijinalde olmayıp, yeni belgeye eklenen kelimeler
            fark_verisi.append(('eklendi', ' '.join(yeni_kelimeler[j1:j2])))
            
        elif islem == 'delete':
            # Orijinalde olup, yeni belgeden silinen kelimeler
            fark_verisi.append(('silindi', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'replace':
            # Mevcut bir kelimenin/cümlenin silinip yerine başkasının yazıldığı kısımlar
            fark_verisi.append(('degisti_eski', ' '.join(orijinal_kelimeler[i1:i2])))
            fark_verisi.append(('degisti_yeni', ' '.join(yeni_kelimeler[j1:j2])))

    return fark_verisi

# --- TEST KODU ---
if __name__ == "__main__":
    eski = "Davacı taraf sözleşmeden feragat ettiğini 15 Mayıs tarihinde bildirmiştir."
    yeni = "Davacı taraf sözleşmeden kesinlikle feragat ettiğini 16 Mayıs tarihinde yazılı olarak bildirmiştir."
    
    sonuclar = metinleri_karsilastir(eski, yeni)
    
    print("\n--- KARŞILAŞTIRMA SONUCU ---")
    for islem_tipi, kelime_grubu in sonuclar:
        print(f"[{islem_tipi.upper()}] -> {kelime_grubu}")