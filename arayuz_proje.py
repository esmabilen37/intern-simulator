import pandas as pd
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =====================================================
# BACKEND FONKSİYONLARI
# =====================================================

def veri_seti_olustur(ogrenci_sayisi=150, firma_sayisi=50):
    firmalar = []
    toplam_kontenjan = 0
    
    for i in range(firma_sayisi):
        kontenjan = random.randint(1, 4)
        firmalar.append({
            "Firma_ID": f"Firma_{i+1}",
            "Kontenjan": kontenjan,
            "Baslangic_Kontenjan": kontenjan
        })
        toplam_kontenjan += kontenjan

    fark = ogrenci_sayisi - toplam_kontenjan
    for _ in range(abs(fark)):
        f = random.choice(firmalar)
        if fark > 0:
            f["Kontenjan"] += 1
            f["Baslangic_Kontenjan"] += 1
        elif f["Kontenjan"] > 1:
            f["Kontenjan"] -= 1
            f["Baslangic_Kontenjan"] -= 1

    ogrenciler = []
    firma_idleri = [f["Firma_ID"] for f in firmalar]
    for i in range(ogrenci_sayisi):
        ogrenciler.append({
            "Ogrenci_ID": f"Ogr_{i+1}",
            "GNO": round(random.uniform(2.0, 4.0), 2),
            "Tercihler": random.sample(firma_idleri, 5),
            "Yerlestigi_Firma": None,
            "Tercih_Sirasi": -1
        })
    
    return pd.DataFrame(ogrenciler), firmalar

def greedy_atama(df_ogrenciler, firmalar_listesi):
    baslangic_zamani = time.time()
    islem_sayisi = 0
    kontenjan_takibi = {f["Firma_ID"]: f["Kontenjan"] for f in firmalar_listesi}
    
    df_sirali = df_ogrenciler.sort_values(by="GNO", ascending=False).copy()
    
    for idx, satir in df_sirali.iterrows():
        for i, tercih in enumerate(satir["Tercihler"]):
            islem_sayisi += 1
            if kontenjan_takibi[tercih] > 0:
                df_sirali.at[idx, "Yerlestigi_Firma"] = tercih
                df_sirali.at[idx, "Tercih_Sirasi"] = i + 1
                kontenjan_takibi[tercih] -= 1
                break
    
    bitis_zamani = time.time()
    sure = bitis_zamani - baslangic_zamani
    return df_sirali, sure, islem_sayisi

def normalize_gno(gno):
    return (gno - 2.0) / 2.0

def normalize_tercih(ts):
    return (6 - ts) / 5

def mutluluk_skoru(row):
    if row["Tercih_Sirasi"] == -1:
        return 0
    return 0.7 * normalize_gno(row["GNO"]) + 0.3 * normalize_tercih(row["Tercih_Sirasi"])

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
# TKINTER ARAYÜZÜ
# =====================================================

class EslestirmeArayuzu:
    def __init__(self, root):
        self.root = root
        self.root.title("Öğrenci-Firma Eşleştirme Sistemi")
        self.root.geometry("1200x800")
        
        # Değişkenler
        self.df_ogr = None
        self.firmalar = None
        self.sonuclar = {}
        
        self.olustur_arayuz()
    
    def olustur_arayuz(self):
        # Ana frame'ler
        sol_frame = ttk.Frame(self.root, padding="10")
        sol_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        sag_frame = ttk.Frame(self.root, padding="10")
        sag_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        
        # SOL PANEL - Parametreler ve Kontroller
        ttk.Label(sol_frame, text="Parametreler", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Öğrenci sayısı
        ttk.Label(sol_frame, text="Öğrenci Sayısı:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ogrenci_sayisi = tk.IntVar(value=150)
        ttk.Entry(sol_frame, textvariable=self.ogrenci_sayisi, width=15).grid(row=1, column=1, pady=5)
        
        # Firma sayısı
        ttk.Label(sol_frame, text="Firma Sayısı:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.firma_sayisi = tk.IntVar(value=50)
        ttk.Entry(sol_frame, textvariable=self.firma_sayisi, width=15).grid(row=2, column=1, pady=5)
        
        # Red oranı
        ttk.Label(sol_frame, text="Red Oranı:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.red_orani = tk.DoubleVar(value=0.2)
        ttk.Entry(sol_frame, textvariable=self.red_orani, width=15).grid(row=3, column=1, pady=5)
        
        # Heuristik iterasyon
        ttk.Label(sol_frame, text="Heuristik İterasyon:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.heur_iter = tk.IntVar(value=1000)
        ttk.Entry(sol_frame, textvariable=self.heur_iter, width=15).grid(row=4, column=1, pady=5)
        
        # Butonlar
        ttk.Button(sol_frame, text="Veri Seti Oluştur", command=self.veri_olustur).grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        ttk.Button(sol_frame, text="Greedy Algoritması Çalıştır", command=self.greedy_calistir).grid(row=6, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(sol_frame, text="Red Simülasyonu + Yeniden Atama", command=self.red_sim_calistir).grid(row=7, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(sol_frame, text="Heuristik Optimizasyon", command=self.heuristik_calistir).grid(row=8, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(sol_frame, text="Tüm İşlemleri Çalıştır", command=self.tum_islemleri_calistir, style='Accent.TButton').grid(row=9, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Sonuçlar alanı
        ttk.Label(sol_frame, text="Sonuçlar", font=('Arial', 12, 'bold')).grid(row=10, column=0, columnspan=2, pady=(20,10))
        self.sonuc_text = scrolledtext.ScrolledText(sol_frame, width=50, height=20, wrap=tk.WORD)
        self.sonuc_text.grid(row=11, column=0, columnspan=2, pady=5)
        
        # SAĞ PANEL - Görselleştirme
        ttk.Label(sag_frame, text="Görselleştirme", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Grafik için frame
        self.grafik_frame = ttk.Frame(sag_frame)
        self.grafik_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tablo için frame
        ttk.Label(sag_frame, text="Örnek Öğrenci Verileri", font=('Arial', 12, 'bold')).pack(pady=(10,5))
        
        self.tablo_frame = ttk.Frame(sag_frame)
        self.tablo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview oluştur
        self.tablo = ttk.Treeview(self.tablo_frame, columns=('ID', 'GNO', 'Firma', 'Tercih', 'Mutluluk'), show='headings', height=10)
        self.tablo.heading('ID', text='Öğrenci ID')
        self.tablo.heading('GNO', text='GNO')
        self.tablo.heading('Firma', text='Yerleştiği Firma')
        self.tablo.heading('Tercih', text='Tercih Sırası')
        self.tablo.heading('Mutluluk', text='Mutluluk Skoru')
        
        self.tablo.column('ID', width=100)
        self.tablo.column('GNO', width=80)
        self.tablo.column('Firma', width=120)
        self.tablo.column('Tercih', width=100)
        self.tablo.column('Mutluluk', width=120)
        
        scrollbar = ttk.Scrollbar(self.tablo_frame, orient=tk.VERTICAL, command=self.tablo.yview)
        self.tablo.configure(yscroll=scrollbar.set)
        
        self.tablo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log(self, mesaj):
        self.sonuc_text.insert(tk.END, mesaj + "\n")
        self.sonuc_text.see(tk.END)
        self.root.update()
    
    def veri_olustur(self):
        try:
            self.log("\n=== VERİ SETİ OLUŞTURULUYOR ===")
            self.df_ogr, self.firmalar = veri_seti_olustur(
                self.ogrenci_sayisi.get(), 
                self.firma_sayisi.get()
            )
            self.log(f"✓ {len(self.df_ogr)} öğrenci oluşturuldu")
            self.log(f"✓ {len(self.firmalar)} firma oluşturuldu")
            self.sonuclar = {}
            messagebox.showinfo("Başarılı", "Veri seti başarıyla oluşturuldu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Veri oluşturulurken hata: {str(e)}")
    
    def greedy_calistir(self):
        if self.df_ogr is None:
            messagebox.showwarning("Uyarı", "Önce veri seti oluşturun!")
            return
        
        try:
            self.log("\n=== GREEDY ALGORİTMASI ===")
            df_greedy, sure, islem = greedy_atama(self.df_ogr, self.firmalar)
            df_greedy["Mutluluk"] = df_greedy.apply(mutluluk_skoru, axis=1)
            
            toplam_mutluluk = df_greedy["Mutluluk"].sum()
            
            self.sonuclar['greedy'] = {
                'df': df_greedy,
                'sure': sure,
                'islem': islem,
                'mutluluk': toplam_mutluluk
            }
            
            self.log(f"✓ Süre: {sure:.6f} saniye")
            self.log(f"✓ İşlem Sayısı: {islem}")
            self.log(f"✓ Toplam Mutluluk: {toplam_mutluluk:.4f}")
            
            self.guncelle_tablo(df_greedy)
            self.guncelle_grafik()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Greedy algoritması hatası: {str(e)}")
    
    def red_sim_calistir(self):
        if 'greedy' not in self.sonuclar:
            messagebox.showwarning("Uyarı", "Önce Greedy algoritmasını çalıştırın!")
            return
        
        try:
            self.log("\n=== RED SİMÜLASYONU + YENİDEN ATAMA ===")
            df_sim = self.sonuclar['greedy']['df'].copy()
            firmalar_kopya = [f.copy() for f in self.firmalar]
            
            iterasyon = 0
            while True:
                df_sim = red_simulasyonu(df_sim, firmalar_kopya, self.red_orani.get())
                df_sim, _, _ = greedy_atama(df_sim, firmalar_kopya)
                iterasyon += 1
                
                if df_sim["Yerlestigi_Firma"].isnull().sum() == 0:
                    break
            
            df_sim["Mutluluk"] = df_sim.apply(mutluluk_skoru, axis=1)
            toplam_mutluluk = df_sim["Mutluluk"].sum()
            
            self.sonuclar['red'] = {
                'df': df_sim,
                'iterasyon': iterasyon,
                'mutluluk': toplam_mutluluk
            }
            
            self.log(f"✓ İterasyon Sayısı: {iterasyon}")
            self.log(f"✓ Toplam Mutluluk: {toplam_mutluluk:.4f}")
            
            self.guncelle_tablo(df_sim)
            self.guncelle_grafik()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Red simülasyonu hatası: {str(e)}")
    
    def heuristik_calistir(self):
        if 'red' not in self.sonuclar:
            messagebox.showwarning("Uyarı", "Önce Red Simülasyonunu çalıştırın!")
            return
        
        try:
            self.log("\n=== HEURİSTİK OPTİMİZASYON ===")
            df_heur, sure, islem, mutluluk = heuristik_zincir_swap(
                self.sonuclar['red']['df'], 
                self.heur_iter.get()
            )
            
            self.sonuclar['heuristik'] = {
                'df': df_heur,
                'sure': sure,
                'islem': islem,
                'mutluluk': mutluluk
            }
            
            self.log(f"✓ Süre: {sure:.6f} saniye")
            self.log(f"✓ İşlem Sayısı: {islem}")
            self.log(f"✓ Toplam Mutluluk: {mutluluk:.4f}")
            
            self.guncelle_tablo(df_heur)
            self.guncelle_grafik()
            
            messagebox.showinfo("Başarılı", "Heuristik optimizasyon tamamlandı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Heuristik algoritması hatası: {str(e)}")
    
    def tum_islemleri_calistir(self):
        self.veri_olustur()
        self.root.after(500, self.greedy_calistir)
        self.root.after(1000, self.red_sim_calistir)
        self.root.after(1500, self.heuristik_calistir)
    
    def guncelle_tablo(self, df):
        # Tabloyu temizle
        for item in self.tablo.get_children():
            self.tablo.delete(item)
        
        # İlk 20 satırı ekle
        for _, row in df.head(20).iterrows():
            mutluluk = row.get('Mutluluk', 0)
            self.tablo.insert('', tk.END, values=(
                row['Ogrenci_ID'],
                row['GNO'],
                row['Yerlestigi_Firma'] if row['Yerlestigi_Firma'] else 'Yerleşemedi',
                row['Tercih_Sirasi'] if row['Tercih_Sirasi'] > 0 else '-',
                f"{mutluluk:.4f}"
            ))
    
    def guncelle_grafik(self):
        # Grafik frame'ini temizle
        for widget in self.grafik_frame.winfo_children():
            widget.destroy()
        
        if not self.sonuclar:
            return
        
        # Yeni figure oluştur
        fig = Figure(figsize=(8, 6), dpi=80)
        
        # Alt grafik 1: Mutluluk Karşılaştırması
        ax1 = fig.add_subplot(2, 1, 1)
        metotlar = []
        mutluluklar = []
        
        if 'greedy' in self.sonuclar:
            metotlar.append('Greedy')
            mutluluklar.append(self.sonuclar['greedy']['mutluluk'])
        
        if 'red' in self.sonuclar:
            metotlar.append('Red+Yeniden')
            mutluluklar.append(self.sonuclar['red']['mutluluk'])
        
        if 'heuristik' in self.sonuclar:
            metotlar.append('Heuristik')
            mutluluklar.append(self.sonuclar['heuristik']['mutluluk'])
        
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        ax1.bar(metotlar, mutluluklar, color=colors[:len(metotlar)])
        ax1.set_ylabel('Toplam Mutluluk Skoru')
        ax1.set_title('Algoritma Karşılaştırması - Mutluluk')
        ax1.grid(axis='y', alpha=0.3)
        
        # Alt grafik 2: Tercih Dağılımı
        ax2 = fig.add_subplot(2, 1, 2)
        
        if 'heuristik' in self.sonuclar:
            df = self.sonuclar['heuristik']['df']
        elif 'red' in self.sonuclar:
            df = self.sonuclar['red']['df']
        elif 'greedy' in self.sonuclar:
            df = self.sonuclar['greedy']['df']
        else:
            return
        
        tercih_dagilim = df[df['Tercih_Sirasi'] > 0]['Tercih_Sirasi'].value_counts().sort_index()
        ax2.bar(tercih_dagilim.index, tercih_dagilim.values, color='#9b59b6')
        ax2.set_xlabel('Tercih Sırası')
        ax2.set_ylabel('Öğrenci Sayısı')
        ax2.set_title('Tercih Dağılımı')
        ax2.grid(axis='y', alpha=0.3)
        
        fig.tight_layout()
        
        # Canvas oluştur
        canvas = FigureCanvasTkAgg(fig, master=self.grafik_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# =====================================================
# UYGULAMAYI BAŞLAT
# =====================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = EslestirmeArayuzu(root)
    root.mainloop()