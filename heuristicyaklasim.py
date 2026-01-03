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

def red_simulasyonu(df, firmalar, red_orani=0.2):
    yerliler = df[df["Yerlestigi_Firma"].notnull()]
    reddedilecek = yerliler.sample(int(len(yerliler) * red_orani))

    for idx in reddedilecek.index:
        firma_id = df.at[idx, "Yerlestigi_Firma"]
        df.at[idx, "Yerlestigi_Firma"] = None
        df.at[idx, "Tercih_Sirasi"] = -1

        for f in firmalar:
            if f["Firma_ID"] == firma_id:
                f["Kontenjan"] += 1
                break

    return df


# =====================================================
# 4. ADIM: MUTLULUK FONKSIYONU (0.7 / 0.3)
# =====================================================

def normalize_gno(gno):
    return (gno - 2.0) / 2.0

def normalize_tercih(ts):
    return (6 - ts) / 5

def mutluluk_skoru(row):
    if row["Tercih_Sirasi"] == -1:
        return 0
    return 0.7 * normalize_gno(row["GNO"]) + 0.3 * normalize_tercih(row["Tercih_Sirasi"])


# =====================================================
# 5. ADIM: KISITLI ZINCIR SWAP HEURISTIC
# =====================================================

def heuristik_zincir_swap(df, iterasyon=1000):
    baslangic = time.time()
    islem = 0

    df = df.copy()
    df["Mutluluk"] = df.apply(mutluluk_skoru, axis=1)

    for _ in range(iterasyon):
        adaylar = df[
            (df["Yerlestigi_Firma"].notnull()) &
            (df["Tercih_Sirasi"] >= 3) &
            (df["GNO"] < 3.6)
        ]

        if len(adaylar) < 3:
            break

        i1, i2, i3 = random.sample(list(adaylar.index), 3)

        f1, f2, f3 = df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"]
        t1, t2, t3 = df.at[i1,"Tercih_Sirasi"], df.at[i2,"Tercih_Sirasi"], df.at[i3,"Tercih_Sirasi"]

        eski = df.at[i1,"Mutluluk"] + df.at[i2,"Mutluluk"] + df.at[i3,"Mutluluk"]

        df.at[i1,"Yerlestigi_Firma"] = f2
        df.at[i2,"Yerlestigi_Firma"] = f3
        df.at[i3,"Yerlestigi_Firma"] = f1

        def ts(idx):
            f = df.at[idx,"Yerlestigi_Firma"]
            return df.at[idx,"Tercihler"].index(f)+1 if f in df.at[idx,"Tercihler"] else 99

        nt1, nt2, nt3 = ts(i1), ts(i2), ts(i3)

        if nt1>t1 or nt2>t2 or nt3>t3:
            df.at[i1,"Yerlestigi_Firma"] = f1
            df.at[i2,"Yerlestigi_Firma"] = f2
            df.at[i3,"Yerlestigi_Firma"] = f3
            continue

        df.at[i1,"Tercih_Sirasi"] = nt1
        df.at[i2,"Tercih_Sirasi"] = nt2
        df.at[i3,"Tercih_Sirasi"] = nt3

        yeni = (
            mutluluk_skoru(df.loc[i1]) +
            mutluluk_skoru(df.loc[i2]) +
            mutluluk_skoru(df.loc[i3])
        )

        islem += 1

        if yeni > eski:
            df.at[i1,"Mutluluk"] = mutluluk_skoru(df.loc[i1])
            df.at[i2,"Mutluluk"] = mutluluk_skoru(df.loc[i2])
            df.at[i3,"Mutluluk"] = mutluluk_skoru(df.loc[i3])
        else:
            df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"] = f1,f2,f3
            df.at[i1,"Tercih_Sirasi"], df.at[i2,"Tercih_Sirasi"], df.at[i3,"Tercih_Sirasi"] = t1,t2,t3

    sure = time.time() - baslangic
    return df, sure, islem, df["Mutluluk"].sum()


# =====================================================
# ÇALIŞTIRMA
# =====================================================

df_ogr, firmalar = veri_seti_olustur()
df_greedy, g_sure, g_islem = greedy_atama(df_ogr, firmalar)

print("\n--- GREEDY (ILK COZUM) ---")
df_greedy["Mutluluk"] = df_greedy.apply(mutluluk_skoru, axis=1)
ilk_greedy_mutluluk = df_greedy["Mutluluk"].sum()
print("Greedy Mutluluk (ilk):", round(ilk_greedy_mutluluk, 4))

# =====================================================
# RED + YENIDEN ATAMA
# =====================================================

df_sim = df_greedy.copy()
iterasyon = 1

while True:
    df_sim = red_simulasyonu(df_sim, firmalar)
    df_sim, _, _ = greedy_atama(df_sim, firmalar)

    if df_sim["Yerlestigi_Firma"].isnull().sum() == 0:
        break
    iterasyon += 1

print("\n--- RED + YENIDEN ATAMA TAMAMLANDI ---")
print("Iterasyon Sayisi:", iterasyon)

# Red sonrası greedy mutluluk (AYNI METRIK)
df_sim["Mutluluk"] = df_sim.apply(mutluluk_skoru, axis=1)
red_sonrasi_greedy_mutluluk = df_sim["Mutluluk"].sum()
print("Greedy Mutluluk (red sonrasi):", round(red_sonrasi_greedy_mutluluk, 4))

# =====================================================
# HEURISTIC
# =====================================================

heur_df, h_sure, h_islem, h_mutluluk = heuristik_zincir_swap(df_sim)

print("\n--- HEURISTIC (ZINCIR SWAP) ---")
print("Heuristic Sure:", round(h_sure, 4))
print("Heuristic Islem Sayisi:", h_islem)
print("Heuristic Mutluluk:", round(h_mutluluk, 4))

# =====================================================
# KARSILASTIRMA (DOGRU OLAN)
# =====================================================

print("\n--- DOGRU KARSILASTIRMA ---")
print("Ilk Greedy Mutluluk      :", round(ilk_greedy_mutluluk, 4))
print("Red Sonrasi Greedy      :", round(red_sonrasi_greedy_mutluluk, 4))
print("Heuristic Sonrasi       :", round(h_mutluluk, 4))

print("\nHeuristic Sonuc (ilk 5 satir):")
print(
    heur_df[
        ["Ogrenci_ID", "GNO", "Yerlestigi_Firma", "Tercih_Sirasi", "Mutluluk"]
    ].head()
)
