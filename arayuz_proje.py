import pandas as pd
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Modern renkler
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_card': '#0f3460',
    'accent_1': '#e94560',
    'accent_2': '#533483',
    'accent_3': '#00d4ff',
    'accent_4': '#7209b7',
    'text_primary': '#ffffff',
    'text_secondary': '#b8b8d1',
    'success': '#06ffa5',
    'warning': '#ffd60a',
    'gradient_1': '#667eea',
    'gradient_2': '#764ba2',
}

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color='#e94560', hover_color='#ff5577', **kwargs):
        super().__init__(parent, height=45, bd=0, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
        self.draw_button(self.bg_color)
    
    def draw_button(self, color):
        self.delete('all')
        width = self.winfo_width() if self.winfo_width() > 1 else 300
        self.create_rectangle(2, 2, width-2, 43, fill=color, outline='', tags='bg')
        self.create_text(width//2, 22, text=self.text, fill='white', 
                        font=('Segoe UI', 11, 'bold'), tags='text')
    
    def on_enter(self, e):
        self.draw_button(self.hover_color)
        self.config(cursor='hand2')
    
    def on_leave(self, e):
        self.draw_button(self.bg_color)
    
    def on_click(self, e):
        if self.command:
            self.command()

class ModernEntry(tk.Frame):
    def __init__(self, parent, label_text, textvariable, **kwargs):
        super().__init__(parent, bg=COLORS['bg_card'])
        label = tk.Label(self, text=label_text, bg=COLORS['bg_card'], 
                        fg=COLORS['text_secondary'], font=('Segoe UI', 10))
        label.pack(anchor='w', pady=(0, 5))
        entry_frame = tk.Frame(self, bg=COLORS['accent_2'], bd=0)
        entry_frame.pack(fill='x')
        self.entry = tk.Entry(entry_frame, textvariable=textvariable, 
                             bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                             font=('Segoe UI', 11), relief='flat', bd=0,
                             insertbackground=COLORS['accent_3'])
        self.entry.pack(padx=2, pady=2, fill='x')

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
    return df_sirali, time.time() - baslangic_zamani, islem_sayisi

def normalize_gno(gno): return (gno - 2.0) / 2.0
def normalize_tercih(ts): return (6 - ts) / 5
def mutluluk_skoru(row):
    if row["Tercih_Sirasi"] == -1: return 0
    return 0.7 * normalize_gno(row["GNO"]) + 0.3 * normalize_tercih(row["Tercih_Sirasi"])

def red_simulasyonu(df, firmalar, red_orani=0.2):
    yerliler = df[df["Yerlestigi_Firma"].notnull()]
    if len(yerliler) == 0: return df
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
        adaylar = df[(df["Yerlestigi_Firma"].notnull()) & (df["Tercih_Sirasi"] >= 3) & (df["GNO"] < 3.6)]
        if len(adaylar) < 3: break
        i1, i2, i3 = random.sample(list(adaylar.index), 3)
        f1, f2, f3 = df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"]
        t1, t2, t3 = df.at[i1,"Tercih_Sirasi"], df.at[i2,"Tercih_Sirasi"], df.at[i3,"Tercih_Sirasi"]
        eski = df.at[i1,"Mutluluk"] + df.at[i2,"Mutluluk"] + df.at[i3,"Mutluluk"]
        df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"] = f2, f3, f1
        def ts(idx):
            f = df.at[idx,"Yerlestigi_Firma"]
            return df.at[idx,"Tercihler"].index(f)+1 if f in df.at[idx,"Tercihler"] else 99
        nt1, nt2, nt3 = ts(i1), ts(i2), ts(i3)
        if nt1>t1 or nt2>t2 or nt3>t3:
            df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"] = f1, f2, f3
            continue
        df.at[i1,"Tercih_Sirasi"], df.at[i2,"Tercih_Sirasi"], df.at[i3,"Tercih_Sirasi"] = nt1, nt2, nt3
        yeni = mutluluk_skoru(df.loc[i1]) + mutluluk_skoru(df.loc[i2]) + mutluluk_skoru(df.loc[i3])
        islem += 1
        if yeni > eski:
            df.at[i1,"Mutluluk"], df.at[i2,"Mutluluk"], df.at[i3,"Mutluluk"] = mutluluk_skoru(df.loc[i1]), mutluluk_skoru(df.loc[i2]), mutluluk_skoru(df.loc[i3])
        else:
            df.at[i1,"Yerlestigi_Firma"], df.at[i2,"Yerlestigi_Firma"], df.at[i3,"Yerlestigi_Firma"] = f1, f2, f3
            df.at[i1,"Tercih_Sirasi"], df.at[i2,"Tercih_Sirasi"], df.at[i3,"Tercih_Sirasi"] = t1, t2, t3
    return df, time.time() - baslangic, islem, df["Mutluluk"].sum()

# =====================================================
# TKINTER ARAYÜZÜ
# =====================================================

class EslestirmeArayuzu:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Öğrenci-Firma Eşleştirme Sistemi")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_primary'])
        self.setup_styles()
        self.df_ogr, self.firmalar, self.sonuclar = None, None, {}
        self.olustur_arayuz()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.Treeview', background=COLORS['bg_secondary'], foreground=COLORS['text_primary'], fieldbackground=COLORS['bg_secondary'], borderwidth=0, font=('Segoe UI', 10))
        style.map('Modern.Treeview', background=[('selected', COLORS['accent_2'])])
        style.configure('Modern.Treeview.Heading', background=COLORS['accent_2'], foreground=COLORS['text_primary'], borderwidth=0, font=('Segoe UI', 10, 'bold'))
        style.configure('Modern.TNotebook', background=COLORS['bg_card'], borderwidth=0)
        style.configure('Modern.TNotebook.Tab', background=COLORS['bg_secondary'], foreground=COLORS['text_secondary'], padding=[15, 5], font=('Segoe UI', 9, 'bold'))
        style.map('Modern.TNotebook.Tab', background=[('selected', COLORS['accent_2'])], foreground=[('selected', COLORS['text_primary'])])

    def olustur_arayuz(self):
        header = tk.Frame(self.root, bg=COLORS['accent_2'], height=70)
        header.pack(fill='x', side='top')
        tk.Label(header, text="🎓 ÖĞRENCİ-FİRMA EŞLEŞTİRME SİSTEMİ", bg=COLORS['accent_2'], fg=COLORS['text_primary'], font=('Segoe UI', 20, 'bold')).pack(pady=15)
        
        main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # SOL PANEL
        sol_panel = tk.Frame(main_container, bg=COLORS['bg_card'], width=400)
        sol_panel.pack(side='left', fill='both', padx=(0, 10))
        sol_panel.pack_propagate(False)
        
        # Parametreler ve Butonlar
        params_card = tk.Frame(sol_panel, bg=COLORS['bg_card'])
        params_card.pack(fill='x', padx=15, pady=10)
        
        self.ogrenci_sayisi, self.firma_sayisi = tk.IntVar(value=150), tk.IntVar(value=50)
        self.red_orani, self.heur_iter = tk.DoubleVar(value=0.2), tk.IntVar(value=1000)
        
        ModernEntry(params_card, "👨‍🎓 Öğrenci Sayısı", self.ogrenci_sayisi).pack(fill='x', pady=5)
        ModernEntry(params_card, "🏢 Firma Sayısı", self.firma_sayisi).pack(fill='x', pady=5)
        ModernEntry(params_card, "❌ Red Oranı", self.red_orani).pack(fill='x', pady=5)
        ModernEntry(params_card, "🔄 Heuristik İterasyon", self.heur_iter).pack(fill='x', pady=5)
        
        btn_frame = tk.Frame(sol_panel, bg=COLORS['bg_card'])
        btn_frame.pack(fill='x', padx=15)
        ModernButton(btn_frame, "📊 Veri Seti Oluştur", self.veri_olustur, bg_color=COLORS['gradient_1'], hover_color=COLORS['gradient_2']).pack(fill='x', pady=3)
        ModernButton(btn_frame, "⚡ Greedy Algoritması", self.greedy_calistir, bg_color='#f72585', hover_color='#ff4da6').pack(fill='x', pady=3)
        ModernButton(btn_frame, "🔄 Red Simülasyonu", self.red_sim_calistir, bg_color='#4361ee', hover_color='#5a7aff').pack(fill='x', pady=3)
        ModernButton(btn_frame, "🚀 Heuristik Optimizasyon", self.heuristik_calistir, bg_color='#7209b7', hover_color='#9d4edd').pack(fill='x', pady=3)
        
        # Notebook (Sonuçlar ve Veri Seti)
        notebook = ttk.Notebook(sol_panel, style='Modern.TNotebook')
        notebook.pack(fill='both', expand=True, padx=15, pady=10)
        
        tab_sonuc = tk.Frame(notebook, bg=COLORS['bg_card'])
        notebook.add(tab_sonuc, text='📋 Log')
        self.sonuc_text = scrolledtext.ScrolledText(tab_sonuc, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'], font=('Consolas', 9), bd=0)
        self.sonuc_text.pack(fill='both', expand=True)
        
        tab_veri = tk.Frame(notebook, bg=COLORS['bg_card'])
        notebook.add(tab_veri, text='📊 Veri')
        self.veri_text = scrolledtext.ScrolledText(tab_veri, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'], font=('Consolas', 9), bd=0)
        self.veri_text.pack(fill='both', expand=True)
        
        # SAĞ PANEL (GÜNCELLENEN KISIM)
        sag_panel = tk.Frame(main_container, bg=COLORS['bg_primary'])
        sag_panel.pack(side='right', fill='both', expand=True)
        
        # Üst Kısım: Grafik
        grafik_card = tk.Frame(sag_panel, bg=COLORS['bg_card'], height=420)
        grafik_card.pack(fill='both', expand=True, pady=(0, 10))
        grafik_card.pack_propagate(False) # Grafiğin tabloyu itmesini engeller
        
        tk.Label(grafik_card, text="📊 ANALİZ VE GÖRSELLEŞTİRME", bg=COLORS['bg_card'], fg=COLORS['accent_3'], font=('Segoe UI', 12, 'bold')).pack(pady=10)
        self.grafik_frame = tk.Frame(grafik_card, bg=COLORS['bg_card'])
        self.grafik_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Alt Kısım: Tablo
        tablo_card = tk.Frame(sag_panel, bg=COLORS['bg_card'])
        tablo_card.pack(fill='both', expand=True)
        
        tk.Label(tablo_card, text="📑 YERLEŞTİRME SONUÇLARI (İLK 50)", bg=COLORS['bg_card'], fg=COLORS['accent_3'], font=('Segoe UI', 12, 'bold')).pack(pady=10)
        self.tablo_frame = tk.Frame(tablo_card, bg=COLORS['accent_2'], bd=1)
        self.tablo_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.tablo = ttk.Treeview(self.tablo_frame, columns=('ID', 'GNO', 'Firma', 'Tercih', 'Mutluluk'), show='headings', style='Modern.Treeview')
        for col, head in zip(self.tablo['columns'], ('Öğrenci ID', 'GNO', 'Firma', 'Sıra', 'Mutluluk')):
            self.tablo.heading(col, text=head)
            self.tablo.column(col, width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(self.tablo_frame, orient="vertical", command=self.tablo.yview)
        self.tablo.configure(yscrollcommand=scrollbar.set)
        self.tablo.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def log(self, mesaj, renk=None):
        if renk: self.sonuc_text.tag_config(renk, foreground=renk)
        self.sonuc_text.insert(tk.END, mesaj + "\n", renk if renk else None)
        self.sonuc_text.see(tk.END)
        self.root.update()

    def veri_olustur(self):
        try:
            self.df_ogr, self.firmalar = veri_seti_olustur(self.ogrenci_sayisi.get(), self.firma_sayisi.get())
            self.log(f"✅ {len(self.df_ogr)} öğrenci ve {len(self.firmalar)} firma oluşturuldu.", COLORS['success'])
            self.goster_veri_seti()
            self.sonuclar = {}
        except Exception as e: self.log(f"❌ HATA: {str(e)}", COLORS['accent_1'])

    def goster_veri_seti(self):
        self.veri_text.delete(1.0, tk.END)
        self.veri_text.insert(tk.END, f"--- FİRMA KONTENJANLARI ---\n")
        for f in self.firmalar[:15]: self.veri_text.insert(tk.END, f"{f['Firma_ID']}: {f['Kontenjan']}\n")
        self.veri_text.insert(tk.END, f"\n--- ÖĞRENCİ TERCİHLERİ (İLK 15) ---\n")
        for _, r in self.df_ogr.head(15).iterrows(): self.veri_text.insert(tk.END, f"{r['Ogrenci_ID']} (GNO: {r['GNO']}): {', '.join(r['Tercihler'])}\n")

    def greedy_calistir(self):
        if self.df_ogr is None: return
        self.log("⚡ Greedy çalışıyor...", COLORS['accent_3'])
        df, sure, islem = greedy_atama(self.df_ogr, self.firmalar)
        df["Mutluluk"] = df.apply(mutluluk_skoru, axis=1)
        self.sonuclar['greedy'] = {'df': df, 'mutluluk': df["Mutluluk"].sum()}
        self.guncelle_tablo(df)
        self.guncelle_grafik()
        self.log(f"✅ Tamamlandı. Mutluluk: {self.sonuclar['greedy']['mutluluk']:.2f}", COLORS['success'])

    def red_sim_calistir(self):
        if 'greedy' not in self.sonuclar:
            messagebox.showwarning("Uyarı", "Önce Greedy algoritmasını çalıştırın!")
            return
        
        try:
            self.log("\n=== RED SİMÜLASYONU + YENİDEN ATAMA BAŞLADI ===", COLORS['accent_3'])
            df_sim = self.sonuclar['greedy']['df'].copy()
            firmalar_kopya = [f.copy() for f in self.firmalar]
            
            iterasyon = 0
            # Başlangıç durumu
            toplam_ogrenci = len(df_sim)
            
            while True:
                iterasyon += 1
                # 1. Firmalar öğrencileri reddeder
                df_sim = red_simulasyonu(df_sim, firmalar_kopya, self.red_orani.get())
                bos_kalan = df_sim["Yerlestigi_Firma"].isnull().sum()
                self.log(f"İterasyon {iterasyon}: {bos_kalan} öğrenci şu an açıkta (Red sonrası).")

                # 2. Açıkta kalanlar için Greedy tekrar çalışır
                df_sim, _, _ = greedy_atama(df_sim, firmalar_kopya)
                
                yerlesen_sayisi = df_sim["Yerlestigi_Firma"].notnull().sum()
                self.log(f"-> Atama sonrası: {yerlesen_sayisi}/{toplam_ogrenci} öğrenci yerleştirildi.")

                # Eğer herkes yerleştiyse veya döngü takıldıysa bitir
                if df_sim["Yerlestigi_Firma"].isnull().sum() == 0:
                    self.log(f"✅ Başarılı: {iterasyon} iterasyonda tüm öğrenciler yerleşti!", COLORS['success'])
                    break
                
                if iterasyon >= 10: # Sonsuz döngü koruması
                    self.log(f"⚠️ Uyarı: 10 iterasyon sonunda {df_sim['Yerlestigi_Firma'].isnull().sum()} öğrenci yerleşemedi.", COLORS['warning'])
                    break
            
            df_sim["Mutluluk"] = df_sim.apply(mutluluk_skoru, axis=1)
            toplam_mutluluk = df_sim["Mutluluk"].sum()
            
            self.sonuclar['red'] = {
                'df': df_sim,
                'iterasyon': iterasyon,
                'mutluluk': toplam_mutluluk
            }
            
            self.guncelle_tablo(df_sim)
            self.guncelle_grafik()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Red simülasyonu hatası: {str(e)}")

    def heuristik_calistir(self):
        base = self.sonuclar.get('red', self.sonuclar.get('greedy'))
        if not base: return
        self.log("🚀 Heuristik Optimizasyon...", COLORS['accent_3'])
        df_h, sure, islem, m = heuristik_zincir_swap(base['df'], self.heur_iter.get())
        self.sonuclar['heuristik'] = {'df': df_h, 'mutluluk': m}
        self.guncelle_tablo(df_h)
        self.guncelle_grafik()

    def guncelle_tablo(self, df):
        for item in self.tablo.get_children(): self.tablo.delete(item)
        for _, r in df.head(50).iterrows():
            self.tablo.insert('', tk.END, values=(r['Ogrenci_ID'], r['GNO'], r['Yerlestigi_Firma'] or 'N/A', r['Tercih_Sirasi'], f"{r['Mutluluk']:.4f}"))

    def guncelle_grafik(self):
        for w in self.grafik_frame.winfo_children(): w.destroy()
        fig = Figure(figsize=(7, 4), dpi=90, facecolor=COLORS['bg_card'])
        ax = fig.add_subplot(111, facecolor=COLORS['bg_secondary'])
        
        labels, values = list(self.sonuclar.keys()), [v['mutluluk'] for v in self.sonuclar.values()]
        if labels:
            bars = ax.bar(labels, values, color=[COLORS['accent_1'], COLORS['accent_3'], COLORS['success']][:len(labels)])
            ax.set_title("Algoritma Başarı Karşılaştırması", color='white', fontsize=10)
            ax.tick_params(colors='white', labelsize=8)
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.1f}', ha='center', va='bottom', color='white', fontsize=8)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.grafik_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = EslestirmeArayuzu(root)
    root.mainloop()
