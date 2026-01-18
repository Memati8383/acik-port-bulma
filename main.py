import customtkinter as ctk
import socket
import threading
import json
import os
import subprocess
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from tkinter import filedialog, messagebox

# --- Konfigürasyon & Dosyalar ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
HISTORY_FILE = "scan_history.json"

# --- Dil Sözlüğü ---
LANGUAGES = {
    "en": {
        "title": "Aura Port Scanner Pro",
        "recent_scans": "Recent Scans",
        "clear_history": "Clear History",
        "target_host": "Target Host:",
        "start_scan": "Start Full Scan",
        "running": "Running...",
        "export_csv": "Export CSV",
        "port_range": "Port Range:",
        "threads": "Threads (Speed):",
        "timeout": "Timeout (sec):",
        "system_ready": "System Ready",
        "scan_results": "Scan Results",
        "open_stats": "Open: {} | Total: {}",
        "resolving": "Resolving {}...",
        "pinging": "Pinging {}...",
        "scanning": "Scanning {} ports...",
        "scan_complete": "Scan Complete",
        "host_error": "Could not resolve host!",
        "range_error": "Invalid port range!",
        "no_results": "No results to export!",
        "export_success": "Results exported to {}",
        "service": "Service",
        "banner": "Banner",
        "port": "Port",
        "theme": "Theme",
        "lang": "Language"
    },
    "tr": {
        "title": "Aura Port Tarayıcı Pro",
        "recent_scans": "Son Taramalar",
        "clear_history": "Geçmişi Temizle",
        "target_host": "Hedef Adres:",
        "start_scan": "Taramayı Başlat",
        "running": "Taranıyor...",
        "export_csv": "CSV Dışa Aktar",
        "port_range": "Port Aralığı:",
        "threads": "İzlek (Hız):",
        "timeout": "Zaman Aşımı (sn):",
        "system_ready": "Sistem Hazır",
        "scan_results": "Tarama Sonuçları",
        "open_stats": "Açık: {} | Toplam: {}",
        "resolving": "Çözümleniyor {}...",
        "pinging": "Ping Atılıyor {}...",
        "scanning": "{} port taranıyor...",
        "scan_complete": "Tarama Tamamlandı",
        "host_error": "Host çözümlenemedi!",
        "range_error": "Geçersiz port aralığı!",
        "no_results": "Dışa aktarılacak sonuç yok!",
        "export_success": "Sonuçlar kaydedildi: {}",
        "service": "Servis",
        "banner": "Bağlantı Bilgisi",
        "port": "Port",
        "theme": "Tema",
        "lang": "Dil"
    }
}

class PortResultCard(ctk.CTkFrame):
    """Açık port sonucunu temsil eden modern bir kart yapısı."""
    def __init__(self, master, port: int, service: str, banner: str = "", lang: str = "en", **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Gösterge: Başarı durumu için dinamik tema rengi
        self.indicator = ctk.CTkLabel(
            self, text="●", text_color=("#27ae60", "#2ecc71"), font=ctk.CTkFont(size=20)
        )
        self.indicator.grid(row=0, column=0, padx=(15, 10), pady=10)
        
        # Port Bilgisi
        self.info_label = ctk.CTkLabel(
            self, 
            text=f"{LANGUAGES[lang]['port']} {port}", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.info_label.grid(row=0, column=1, sticky="w", pady=(10, 0))
        
        # Servis Bilgisi
        self.service_label = ctk.CTkLabel(
            self, 
            text=f"{LANGUAGES[lang]['service']}: {service}", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=("gray30", "gray70")
        )
        self.service_label.grid(row=1, column=1, sticky="w", pady=(0, 10))

        # Banner (Yazılım Sürümü) Bilgisi
        if banner:
            self.banner_label = ctk.CTkLabel(
                self, 
                text=f"{banner[:40]}...", 
                font=ctk.CTkFont(family="Consolas", size=11),
                fg_color=("#e0e0e0", "#333333"),
                corner_radius=5
            )
            self.banner_label.grid(row=0, column=2, rowspan=2, padx=15, pady=10, sticky="e")

class AuraPortScannerPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "tr"  # Varsayılan dil Türkçe
        self.title(LANGUAGES[self.current_lang]["title"])
        self.geometry("1100x720")
        
        # Pencere ikonu ayarı
        if os.path.exists("app_icon.ico"):
            self.after(200, lambda: self.iconbitmap("app_icon.ico"))
        
        # Ana Grid Düzeni
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        
        # Uygulama Durumu
        self.is_scanning = False
        self.scan_results = []
        self.load_history()
        self.update_ui_text()

    def setup_sidebar(self):
        """Yan menü bileşenlerini oluşturur."""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="AuraPro", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.history_label = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(weight="bold"))
        self.history_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        self.history_list = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.history_list.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.clear_history_btn = ctk.CTkButton(
            self.sidebar, text="", fg_color="transparent", border_width=1,
            command=self.clear_history, text_color=("gray20", "gray95"),
            border_color=("gray60", "gray40"), hover_color=("gray85", "gray30")
        )
        self.clear_history_btn.grid(row=3, column=0, padx=20, pady=5)

        # Ayarlar Bölümü
        self.settings_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.settings_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        
        self.lang_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=["Türkçe", "English"], 
            command=self.change_language, width=100
        )
        self.lang_menu.pack(side="top", pady=5, fill="x")
        self.lang_menu.set("Türkçe")

        self.theme_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=["System", "Dark", "Light"], 
            command=ctk.set_appearance_mode, width=100
        )
        self.theme_menu.pack(side="top", pady=5, fill="x")

    def setup_main_area(self):
        """Ana içerik alanını oluşturur."""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)

        # 1. Konfigürasyon Paneli (Kart Düzeni)
        self.config_card = ctk.CTkFrame(self.main_content)
        self.config_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.config_card.grid_columnconfigure((0,1,2,3), weight=1)

        self.target_label = ctk.CTkLabel(self.config_card, text="", font=ctk.CTkFont(weight="bold"))
        self.target_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.target_entry = ctk.CTkEntry(self.config_card, placeholder_text="localhost", height=38)
        self.target_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.target_entry.insert(0, "localhost")

        self.scan_btn = ctk.CTkButton(self.config_card, text="", height=38, font=ctk.CTkFont(weight="bold"), 
                                      command=self.start_scan, text_color="white")
        self.scan_btn.grid(row=1, column=2, padx=10, pady=(0, 20), sticky="ew")

        self.export_btn = ctk.CTkButton(self.config_card, text="", height=38, 
                                        fg_color=("#34495e", "#2c3e50"), hover_color=("#2c3e50", "#1a252f"),
                                        text_color="white", command=self.export_results)
        self.export_btn.grid(row=1, column=3, padx=20, pady=(0, 20), sticky="ew")

        # Port, İzlek ve Zaman Aşımı Seçicileri
        self.range_label = ctk.CTkLabel(self.config_card, text="", font=ctk.CTkFont(size=12))
        self.range_label.grid(row=2, column=0, padx=20, sticky="w")
        
        self.range_input_frame = ctk.CTkFrame(self.config_card, fg_color="transparent")
        self.range_input_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")
        
        self.port_start = ctk.CTkEntry(self.range_input_frame, width=60)
        self.port_start.pack(side="left", padx=(0, 5))
        self.port_start.insert(0, "1")

        self.port_end = ctk.CTkEntry(self.range_input_frame, width=60)
        self.port_end.pack(side="left")
        self.port_end.insert(0, "1024")

        self.thread_label = ctk.CTkLabel(self.config_card, text="", font=ctk.CTkFont(size=12))
        self.thread_label.grid(row=2, column=1, sticky="w")
        self.thread_slider = ctk.CTkSlider(self.config_card, from_=10, to=400, number_of_steps=39)
        self.thread_slider.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")
        self.thread_slider.set(100)

        self.timeout_label = ctk.CTkLabel(self.config_card, text="", font=ctk.CTkFont(size=12))
        self.timeout_label.grid(row=2, column=2, sticky="w")
        self.timeout_slider = ctk.CTkSlider(self.config_card, from_=0.1, to=3.0, number_of_steps=29)
        self.timeout_slider.grid(row=3, column=2, padx=20, pady=(0, 20), sticky="ew")
        self.timeout_slider.set(0.6)

        # 2. Durum ve İlerleme Çubuğu
        self.status_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(fill="x", side="top", pady=(0, 5))
        self.progress_bar.set(0)
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="", font=ctk.CTkFont(size=12, slant="italic"), text_color=("gray30", "gray70"))
        self.status_text.pack(side="left")

        self.stats_label = ctk.CTkLabel(self.status_frame, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color=("#2980b9", "#3498db"))
        self.stats_label.pack(side="right")

        # 3. Sonuç Listesi (Kaydırılabilir)
        self.results_frame = ctk.CTkScrollableFrame(self.main_content)
        self.results_frame.grid(row=2, column=0, sticky="nsew")

    def update_ui_text(self):
        """Seçili dile göre tüm arayüz metinlerini günceller."""
        L = LANGUAGES[self.current_lang]
        self.title(L["title"])
        self.history_label.configure(text=L["recent_scans"])
        self.clear_history_btn.configure(text=L["clear_history"])
        self.target_label.configure(text=L["target_host"])
        self.scan_btn.configure(text=L["start_scan"] if not self.is_scanning else L["running"])
        self.export_btn.configure(text=L["export_csv"])
        self.range_label.configure(text=L["port_range"])
        self.thread_label.configure(text=L["threads"])
        self.timeout_label.configure(text=L["timeout"])
        self.status_text.configure(text=L["system_ready"] if not self.is_scanning else self.status_text.cget("text"))
        self.results_frame.configure(label_text=L["scan_results"], label_font=ctk.CTkFont(weight="bold"))
        self.update_stats()

    def change_language(self, choice: str):
        """Kullanıcının dil seçimini işler."""
        self.current_lang = "tr" if choice == "Türkçe" else "en"
        self.update_ui_text()
        # Mevcut sonuç kartlarını güncelle
        for widget in self.results_frame.winfo_children():
            if isinstance(widget, PortResultCard):
                widget.info_label.configure(text=f"{LANGUAGES[self.current_lang]['port']} {widget.info_label.cget('text').split(' ')[-1]}")
                old_service = widget.service_label.cget("text").split(": ")[-1]
                widget.service_label.configure(text=f"{LANGUAGES[self.current_lang]['service']}: {old_service}")

    def ping_host(self, host: str) -> bool:
        """Hedefin aktif olup olmadığını kontrol eder (Ping)."""
        param = "-n" if os.name == "nt" else "-c"
        return subprocess.call(["ping", param, "1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def get_service_name(self, port: int) -> str:
        """Port numarasına göre bilinen servis adını getirir."""
        try: return socket.getservbyport(port, "tcp")
        except: return "unknown"

    def banner_grab(self, sopt: socket.socket) -> str:
        """Banner Grabbing: Servis versiyon bilgisini çekmeye çalışır."""
        try:
            sopt.send(b"Hello\r\n")
            return sopt.recv(1024).decode(errors="ignore").strip()
        except: return ""

    def scan_single_port(self, host_ip: str, port: int, timeout: float):
        """Tek bir portu tarar."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((host_ip, port)) == 0:
                    service = self.get_service_name(port)
                    banner = self.banner_grab(s)
                    self.after(0, lambda: self.add_result_card(port, service, banner))
                    return True
            return False
        except: return False

    def add_result_card(self, port: int, service: str, banner: str):
        """Bulunan açık portu listeye kart olarak ekler."""
        self.scan_results.append({"port": port, "service": service, "banner": banner})
        card = PortResultCard(self.results_frame, port, service, banner, lang=self.current_lang)
        card.pack(fill="x", padx=10, pady=5)
        self.update_stats()

    def update_stats(self):
        """Bulunan açık port sayısını günceller."""
        L = LANGUAGES[self.current_lang]
        open_count = len(self.scan_results)
        total = self.port_end.get()
        self.stats_label.configure(text=L["open_stats"].format(open_count, total))

    def start_scan(self):
        """Tarama işlemini başlatır."""
        if self.is_scanning: return
        L = LANGUAGES[self.current_lang]
        
        target = self.target_entry.get().strip()
        try:
            start_p = int(self.port_start.get())
            end_p = int(self.port_end.get())
        except ValueError:
            messagebox.showerror("Hata", L["range_error"])
            return

        if not target: return

        # UI Hazırlığı
        self.is_scanning = True
        self.update_ui_text()
        self.scan_results = []
        for widget in self.results_frame.winfo_children():
            if not isinstance(widget, ctk.CTkLabel) or widget.cget("text") not in ["Scan Results", "Tarama Sonuçları"]:
                widget.destroy()
        
        self.progress_bar.set(0)
        self.status_text.configure(text=L["resolving"].format(target))
        # Taramayı arka planda (Thread) çalıştır
        threading.Thread(target=self.run_scan_logic, args=(target, start_p, end_p), daemon=True).start()

    def run_scan_logic(self, target: str, start_p: int, end_p: int):
        """Asıl tarama mantığı (Multi-threading)."""
        L = LANGUAGES[self.current_lang]
        try:
            target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            self.after(0, lambda: messagebox.showerror("Hata", L["host_error"]))
            self.after(0, self.finish_scan)
            return

        self.after(0, lambda: self.status_text.configure(text=L["pinging"].format(target_ip)))
        self.ping_host(target_ip) 

        ports = range(start_p, end_p + 1)
        total_ports = len(ports)
        self.after(0, lambda: self.status_text.configure(text=L["scanning"].format(total_ports)))

        # İzlek Havuzu kullanarak eş zamanlı tarama
        with ThreadPoolExecutor(max_workers=int(self.thread_slider.get())) as executor:
            scanned = 0
            futures = [executor.submit(self.scan_single_port, target_ip, p, self.timeout_slider.get()) for p in ports]
            for _ in futures:
                scanned += 1
                self.after(0, lambda p=scanned/total_ports: self.progress_bar.set(p))

        self.after(0, lambda: self.finish_scan(target))

    def finish_scan(self, target: str = ""):
        """Tarama bitiş işlemlerini yapar."""
        self.is_scanning = False
        self.update_ui_text()
        self.status_text.configure(text=LANGUAGES[self.current_lang]["scan_complete"])
        if target: self.save_to_history(target)

    def load_history(self):
        """Geçmiş taramaları dosyadan yükler."""
        if not os.path.exists(HISTORY_FILE): return
        try:
            with open(HISTORY_FILE, "r") as f:
                for item in json.load(f):
                    self.add_history_item(item["target"], item["date"])
        except: pass

    def save_to_history(self, target: str):
        """Yeni başarılı taramayı geçmişe kaydeder."""
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f: history = json.load(f)
        if not any(h["target"] == target for h in history[-5:]):
            history.append({"target": target, "date": date_str})
            with open(HISTORY_FILE, "w") as f: json.dump(history, f)
            self.add_history_item(target, date_str)

    def add_history_item(self, target: str, date: str):
        """Yan menüye tarihçe butonu ekler."""
        btn = ctk.CTkButton(
            self.history_list, text=f"{target}\n{date}", font=ctk.CTkFont(size=11),
            fg_color="transparent", anchor="w", text_color=("gray20", "gray95"),
            command=lambda t=target: self.target_entry.delete(0, "end") or self.target_entry.insert(0, t)
        )
        btn.pack(fill="x", pady=2)

    def clear_history(self):
        """Tüm geçmişi temizler."""
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        for widget in self.history_list.winfo_children(): widget.destroy()

    def export_results(self):
        """Sonuçları CSV olarak dışa aktarır."""
        L = LANGUAGES[self.current_lang]
        if not self.scan_results:
            messagebox.showwarning("Uyarı", L["no_results"])
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=["port", "service", "banner"])
                w.writeheader()
                w.writerows(self.scan_results)
            messagebox.showinfo("Başarılı", L["export_success"].format(path))

if __name__ == "__main__":
    app = AuraPortScannerPro()
    app.mainloop()
