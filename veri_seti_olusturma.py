def veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50):
    firmalar = []
    toplam_kontenjan = 0
    
    for i in range(firma_sayisi):
        kontenjan = random.randint(1, 4)
        firmalar.append({
            "Firma_ID": f"Firma_{i+1}",
            "Kontenjan": kontenjan,
            "Mevcut_Bos": kontenjan
        })
        toplam_kontenjan += kontenjan

    # Kontenjan dengeleme
    fark = ogrenci_sayisi - toplam_kontenjan
    for _ in range(abs(fark)):
        f = random.choice(firmalar)
        if fark > 0:
            f["Mevcut_Bos"] += 1
            f["Kontenjan"] += 1
        elif f["Mevcut_Bos"] > 1:
            f["Mevcut_Bos"] -= 1
            f["Kontenjan"] -= 1

    ogrenciler = []
    firma_idleri = [f["Firma_ID"] for f in firmalar]
    for i in range(ogrenci_sayisi):
        ogrenciler.append({
            "Ogrenci_ID": f"Ogr_{i+1}",
            "GNO": round(random.uniform(2.0, 4.0), 2),
            "Tercihler": random.sample(firma_idleri, 5),
            "Yerlestigi_Firma": None
        })
    
    return pd.DataFrame(ogrenciler), firmalar
