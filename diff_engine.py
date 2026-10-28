import difflib

def metinleri_karsilastir(orijinal_metin, yeni_metin):
    # En saf hali: Hiçbir dış müdahale, regex veya filtre yok.
    # Metni ham haliyle, sadece boşluklardan kelimelere bölüyoruz.
    orijinal_kelimeler = orijinal_metin.split()
    yeni_kelimeler = yeni_metin.split()

    # SequenceMatcher tamamen kendi doğal varsayılan ayarlarıyla çalışıyor
    matcher = difflib.SequenceMatcher(None, orijinal_kelimeler, yeni_kelimeler)
    fark_verisi = []
    
    for islem, i1, i2, j1, j2 in matcher.get_opcodes():
        if islem == 'equal':
            fark_verisi.append(('esit', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'insert':
            fark_verisi.append(('eklendi', ' '.join(yeni_kelimeler[j1:j2])))
            
        elif islem == 'delete':
            fark_verisi.append(('silindi', ' '.join(orijinal_kelimeler[i1:i2])))
            
        elif islem == 'replace':
            eski_blok = ' '.join(orijinal_kelimeler[i1:i2])
            yeni_blok = ' '.join(yeni_kelimeler[j1:j2])
            
            fark_verisi.append(('degisti_eski', eski_blok))
            fark_verisi.append(('degisti_yeni', yeni_blok))

    return fark_verisi

# --- TEST KODU ---
if __name__ == "__main__":
    eski = "Davacı taraf sözleşmeden feragat ettiğini 15 Mayıs tarihinde bildirmiştir."
    yeni = "Davacı taraf sözleşmeden kesinlikle feragat ettiğini 16 Mayıs tarihinde yazılı olarak bildirmiştir."
    
    sonuclar = metinleri_karsilastir(eski, yeni)
    
    print("\n--- KARŞILAŞTIRMA SONUCU ---")
    for islem_tipi, kelime_grubu in sonuclar:
        print(f"[{islem_tipi.upper()}] -> {kelime_grubu}")