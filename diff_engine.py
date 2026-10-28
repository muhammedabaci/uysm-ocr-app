import difflib
import re

def metinleri_karsilastir(orijinal_metin, yeni_metin):
    # DÜZELTME 1: Sadece boşluklardan bölmek yerine, noktalama işaretlerini de kelimelerden ayırıyoruz.
    # Örnek: "Değerlendirilmesi:" -> ["Değerlendirilmesi", ":"]
    # \w+ (harf/rakam grupları) veya [^\s\w]+ (boşluk olmayan noktalama işaretleri)
    orijinal_kelimeler = re.findall(r'\w+|[^\s\w]+', orijinal_metin)
    yeni_kelimeler = re.findall(r'\w+|[^\s\w]+', yeni_metin)

    # DÜZELTME 2: autojunk=False parametresi! 
    # Sık tekrar eden kelimelerin eşleşmeyi bozmasını (hiza kaymasını) engeller.
    matcher = difflib.SequenceMatcher(None, orijinal_kelimeler, yeni_kelimeler, autojunk=False)
    
    fark_verisi = []
    
    for islem, i1, i2, j1, j2 in matcher.get_opcodes():
        if islem == 'equal':
            fark_verisi.append(('esit', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'insert':
            fark_verisi.append(('eklendi', ' '.join(yeni_kelimeler[j1:j2])))
            
        elif islem == 'delete':
            fark_verisi.append(('silindi', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'replace':
            fark_verisi.append(('degisti_eski', ' '.join(orijinal_kelimeler[i1:i2])))
            fark_verisi.append(('degisti_yeni', ' '.join(yeni_kelimeler[j1:j2])))

    # Ekran görünümünü temizlemek için Regex ile ayrılmış noktalama işaretlerinin 
    # önündeki gereksiz boşlukları toparlayan ufak bir temizlik (örn: "kelime ," -> "kelime,")
    temizlenmis_fark = []
    for islem, metin in fark_verisi:
        toparlanmis_metin = re.sub(r'\s+([.,:;!?%)\]])', r'\1', metin) # Noktalamadan önceki boşluğu sil
        toparlanmis_metin = re.sub(r'([(>\[])\s+', r'\1', toparlanmis_metin) # Parantezden sonraki boşluğu sil
        temizlenmis_fark.append((islem, toparlanmis_metin))

    return temizlenmis_fark

# --- TEST KODU ---
if __name__ == "__main__":
    eski = "Davacı taraf sözleşmeden feragat ettiğini 15 Mayıs tarihinde bildirmiştir."
    yeni = "Davacı taraf sözleşmeden kesinlikle feragat ettiğini 16 Mayıs tarihinde yazılı olarak bildirmiştir."
    
    sonuclar = metinleri_karsilastir(eski, yeni)
    
    print("\n--- KARŞILAŞTIRMA SONUCU ---")
    for islem_tipi, kelime_grubu in sonuclar:
        print(f"[{islem_tipi.upper()}] -> {kelime_grubu}")