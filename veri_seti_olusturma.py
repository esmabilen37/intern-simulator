import pandas as pd
import random
import time

# 1. ADIM: VERİ SETİ OLUŞTURMA (Parametrik ve Dengeli)
def veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50):
    firmalar = []
    toplam_kontenjan = 0
    
    # Firmaları ve ilk kontenjanları oluştur (Ödev: 30-50 firma arası) 
    for i in range(firma_sayisi):
        kontenjan = random.randint(1, 4)
        firmalar.append({
            "Firma_ID": f"Firma_{i+1}",
            "Kontenjan": kontenjan,
            "Baslangic_Kontenjan": kontenjan 
        })
        toplam_kontenjan += kontenjan

    # Önemli: Toplam kontenjan öğrenci sayısına eşit olmalı (Ödev Kuralı) 
    fark = ogrenci_sayisi - toplam_kontenjan
    for _ in range(abs(fark)):
        f = random.choice(firmalar)
        if fark > 0:
            f["Kontenjan"] += 1
            f["Baslangic_Kontenjan"] += 1
        elif f["Kontenjan"] > 1:
            f["Kontenjan"] -= 1
            f["Baslangic_Kontenjan"] -= 1

    # Öğrencileri oluştur (Ödev: 100-150 öğrenci arası) 
    ogrenciler = []
    firma_idleri = [f["Firma_ID"] for f in firmalar]
    for i in range(ogrenci_sayisi):
        ogrenciler.append({
            "Ogrenci_ID": f"Ogr_{i+1}",
            "GNO": round(random.uniform(2.0, 4.0), 2), # GNO 2.0-4.0 arası 
            "Tercihler": random.sample(firma_idleri, 5), # 5 firma tercihi 
            "Yerlestigi_Firma": None,
            "Tercih_Sirasi": -1 # Başlangıç değeri
        })
    
    return pd.DataFrame(ogrenciler), firmalar

# 2. ADIM: GREEDY ATAMA VE ANALİZ
def greedy_atama(df_ogrenciler, firmalar_listesi):
    baslangic_zamani = time.time()
    islem_sayisi = 0
    # Kontenjanları takip etmek için sözlük yapısı
    kontenjan_takibi = {f["Firma_ID"]: f["Kontenjan"] for f in firmalar_listesi}
    
    # GNO'ya göre büyükten küçüğe sırala (Greedy Mantığı) 
    df_sirali = df_ogrenciler.sort_values(by="GNO", ascending=False).copy()
    
    for idx, satir in df_sirali.iterrows():
        for i, tercih in enumerate(satir["Tercihler"]):
            islem_sayisi += 1
            if kontenjan_takibi[tercih] > 0:
                # Atama işlemini gerçekleştir 
                df_sirali.at[idx, "Yerlestigi_Firma"] = tercih
                df_sirali.at[idx, "Tercih_Sirasi"] = i + 1 # 1. tercih, 2. tercih vb.
                kontenjan_takibi[tercih] -= 1
                break
    
    bitis_zamani = time.time()
    sure = bitis_zamani - baslangic_zamani
    return df_sirali, sure, islem_sayisi

# 3. ANALİZ: MEMNUNİYET SKORU HESAPLAMA
def memnuniyet_skoru_hesapla(df):
    # Puanlama: 1. tercih 50, 2. tercih 40... 
    skor = 0
    for _, row in df.iterrows():
        if row["Tercih_Sirasi"] > 0:
            skor += (60 - (row["Tercih_Sirasi"] * 10))
    return skor

# --- ANA ÇALIŞTIRICI ---
if __name__ == "__main__":
    # 1. Veri setini oluştur (Parametrik: Sayıları buradan değiştirebilirsin) 
    df_ogr, firmalar = veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50)

    # 2. Greedy atamasını yap
    sonuc_df, sure, islemler = greedy_atama(df_ogr, firmalar)

    # 3. Memnuniyet skorunu hesapla
    toplam_memnuniyet = memnuniyet_skoru_hesapla(sonuc_df)

    # 4. GÜNCEL VERİYİ KAYDET (Kritik: sonuc_df kaydedilmeli)
    sonuc_df.to_csv("staj_yerlestirme_sonuclari.csv", index=False)
    print("Sonuçlar 'staj_yerlestirme_sonuclari.csv' dosyasına kaydedildi.\n")

    # 5. Sonuçları Ekrana Yazdır
    print(f"Greedy İşlem Süresi: {sure:.6f} saniye")
    print(f"Toplam İşlem Sayısı: {islemler}")
    print(f"Toplam Memnuniyet Skoru: {toplam_memnuniyet}")
    
    # Tüm listeyi görmek istersen (Pandas ayarı ile)
    pd.set_option('display.max_rows', None)
    print("\n--- TAM YERLEŞTİRME LİSTESİ ---")
    print(sonuc_df[['Ogrenci_ID', 'GNO', 'Yerlestigi_Firma', 'Tercih_Sirasi']])
