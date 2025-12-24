import pandas as pd
import random

# 1. ADIM: VERİ SETİ OLUŞTURMA
def veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50):
    firmalar = []
    toplam_kontenjan = 0
    
    for i in range(firma_sayisi):
        kontenjan = random.randint(1, 4)
        firmalar.append({
            "Firma_ID": f"Firma_{i+1}",
            "Kontenjan": kontenjan
        })
        toplam_kontenjan += kontenjan

    # Kontenjan dengeleme (Öğrenci sayısı kadar kontenjan olsun)
    fark = ogrenci_sayisi - toplam_kontenjan
    for _ in range(abs(fark)):
        f = random.choice(firmalar)
        if fark > 0: f["Kontenjan"] += 1
        elif f["Kontenjan"] > 1: f["Kontenjan"] -= 1

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

# 2. ADIM: GREEDY ATAMA
def greedy_atama(df_ogrenciler, firmalar_listesi):
   
    kontenjan_takibi = {f["Firma_ID"]: f["Kontenjan"] for f in firmalar_listesi}
    
    # GNO'ya göre büyükten küçüğe sıral
    df_sirali = df_ogrenciler.sort_values(by="GNO", ascending=False).copy()
    
    for idx, satir in df_sirali.iterrows():
        for tercih in satir["Tercihler"]:
            if kontenjan_takibi[tercih] > 0:
                df_sirali.at[idx, "Yerlestigi_Firma"] = tercih
                kontenjan_takibi[tercih] -= 1
                break # Öğrenci yerleşti, diğer tercihlerine bakmaya gerek yok
    return df_sirali


df_ogr, firmalar = veri_seti_olustur()
sonuc_df = greedy_atama(df_ogr, firmalar)

print(sonuc_df.head())
print(f"Yerleşemeyen Öğrenci Sayısı: {sonuc_df['Yerlestigi_Firma'].isna().sum()}")
