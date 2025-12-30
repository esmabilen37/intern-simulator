import pandas as pd
import random
import time

# 1. ADIM: VERİ SETİ OLUŞTURMA (Parametrik ve Dengeli)
def veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50):
    firmalar = []
    toplam_kontenjan = 0
    
    # Firmaları ve ilk kontenjanları oluştur (30-50 firma arası) 
    for i in range(firma_sayisi):
        kontenjan = random.randint(1, 4)
        firmalar.append({
            "Firma_ID": f"Firma_{i+1}",
            "Kontenjan": kontenjan,
            "Baslangic_Kontenjan": kontenjan # Raporlama için saklıyoruz
        })
        toplam_kontenjan += kontenjan

    # Önemli: Toplam kontenjan öğrenci sayısına eşit olmalı 
    fark = ogrenci_sayisi - toplam_kontenjan
    for _ in range(abs(fark)):
        f = random.choice(firmalar)
        if fark > 0:
            f["Kontenjan"] += 1
            f["Baslangic_Kontenjan"] += 1
        elif f["Kontenjan"] > 1:
            f["Kontenjan"] -= 1
            f["Baslangic_Kontenjan"] -= 1

    # Öğrencileri oluştur (100-150 öğrenci arası) 
    ogrenciler = []
    firma_idleri = [f["Firma_ID"] for f in firmalar]
    for i in range(ogrenci_sayisi):
        ogrenciler.append({
            "Ogrenci_ID": f"Ogr_{i+1}",
            "GNO": round(random.uniform(2.0, 4.0), 2),
            "Tercihler": random.sample(firma_idleri, 5),
            "Yerlestigi_Firma": None,
            "Tercih_Sirasi": -1 # Kaçıncı tercihine yerleştiğini takip için
        })
    
    return pd.DataFrame(ogrenciler), firmalar

# 2. ADIM: GREEDY ATAMA VE ANALİZ
def greedy_atama(df_ogrenciler, firmalar_listesi):
    baslangic_zamani = time.time()
    islem_sayisi = 0
    kontenjan_takibi = {f["Firma_ID"]: f["Kontenjan"] for f in firmalar_listesi}
    
    # GNO'ya göre büyükten küçüğe sırala 
    df_sirali = df_ogrenciler.sort_values(by="GNO", ascending=False).copy()
    
    for idx, satir in df_sirali.iterrows():
        for i, tercih in enumerate(satir["Tercihler"]):
            islem_sayisi += 1
            if kontenjan_takibi[tercih] > 0:
                df_sirali.at[idx, "Yerlestigi_Firma"] = tercih
                df_sirali.at[idx, "Tercih_Sirasi"] = i + 1 # 1'den başlar
                kontenjan_takibi[tercih] -= 1
                break
    
    bitis_zamani = time.time()
    sure = bitis_zamani - baslangic_zamani
    return df_sirali, sure, islem_sayisi

# 3. ANALİZ: MEMNUNİYET SKORU HESAPLAMA
def memnuniyet_skoru_hesapla(df):
    # 1. tercih: 50, 2. tercih: 40... yerleşemeyen: 0 puan 
    skor = 0
    for _, row in df.iterrows():
        if row["Tercih_Sirasi"] > 0:
            skor += (60 - (row["Tercih_Sirasi"] * 10))
    return skor

# --- ÇALIŞTIRMA ---
df_ogr, firmalar = veri_seti_olustur()
# Veriyi CSV olarak kaydet (Gereksinim 6) 
df_ogr.to_csv("ogrenci_verileri.csv", index=False)

sonuc_df, sure, islemler = greedy_atama(df_ogr, firmalar)
toplam_memnuniyet = memnuniyet_skoru_hesapla(sonuc_df)

print(f"Greedy İşlem Süresi: {sure:.6f} saniye")
print(f"Toplam İşlem Sayısı: {islemler}")
print(f"Toplam Memnuniyet Skoru: {toplam_memnuniyet}")
print(sonuc_df[['Ogrenci_ID', 'GNO', 'Yerlestigi_Firma', 'Tercih_Sirasi']].head())
