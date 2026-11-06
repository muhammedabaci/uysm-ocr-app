import difflib

def metinleri_karsilastir(orijinal_objeler, yeni_objeler):
    # Artık düz metin (string) değil, OCR'dan gelen koordinatlı kelime objelerini alıyoruz.
    
    # difflib'in matematiksel kıyaslama yapabilmesi için bu objelerin içinden
    # sadece 'text' (metin) kısımlarını çıkararak iki basit liste oluşturuyoruz.
    orijinal_metinler = [obje['text'] for obje in orijinal_objeler]
    yeni_metinler = [obje['text'] for obje in yeni_objeler]

    # SequenceMatcher, saf metin listelerini kendi doğal ayarlarıyla kıyaslıyor
    matcher = difflib.SequenceMatcher(None, orijinal_metinler, yeni_metinler)
    fark_verisi = []
    
    for islem, i1, i2, j1, j2 in matcher.get_opcodes():
        if islem == 'equal':
            # Eşit olan kelimelerin orijinal objelerini (koordinatlarıyla) listeye ekliyoruz
            fark_verisi.append(('esit', orijinal_objeler[i1:i2]))
            
        elif islem == 'insert':
            # Yeni eklenen kelimelerin yeni objelerini alıyoruz (Orijinalde olmadıkları için)
            fark_verisi.append(('eklendi', yeni_objeler[j1:j2]))
            
        elif islem == 'delete':
            # Silinen kelimelerin orijinal objelerini alıyoruz (Sadece eski PDF'te varlar)
            fark_verisi.append(('silindi', orijinal_objeler[i1:i2]))
            
        elif islem == 'replace':
            # Değişen kelimelerin hem eski hem yeni objelerini alıyoruz.
            # Böylece arayüzde eski PDF'te kırmızı, yeni PDF'te yeşil boyayabileceğiz.
            fark_verisi.append(('degisti_eski', orijinal_objeler[i1:i2]))
            fark_verisi.append(('degisti_yeni', yeni_objeler[j1:j2]))

    return fark_verisi

# --- TEST KODU ---
if __name__ == "__main__":
    # Test için sahte (mock) koordinatlı kelime objeleri oluşturalım
    eski_liste = [
        {'text': 'Davacı', 'bbox': (10, 10, 50, 20), 'page': 0},
        {'text': 'feragat', 'bbox': (60, 10, 100, 20), 'page': 0},
        {'text': 'etti.', 'bbox': (110, 10, 130, 20), 'page': 0}
    ]
    
    yeni_liste = [
        {'text': 'Davacı', 'bbox': (10, 10, 50, 20), 'page': 0},
        {'text': 'kesinlikle', 'bbox': (55, 10, 95, 20), 'page': 0},
        {'text': 'feragat', 'bbox': (100, 10, 140, 20), 'page': 0},
        {'text': 'ettiğini', 'bbox': (150, 10, 180, 20), 'page': 0},
        {'text': 'bildirdi.', 'bbox': (190, 10, 230, 20), 'page': 0}
    ]
    
    sonuclar = metinleri_karsilastir(eski_liste, yeni_liste)
    
    print("\n--- OBJE TABANLI KARŞILAŞTIRMA SONUCU ---")
    for islem_tipi, obje_grubu in sonuclar:
        # Obje içindeki text'leri yan yana yazdırıp sonucu görelim
        kelimeler = " ".join([obj['text'] for obj in obje_grubu])
        print(f"[{islem_tipi.upper()}] -> {kelimeler} (Obje Sayısı: {len(obje_grubu)})")