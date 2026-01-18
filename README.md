# Aura Port Scanner Pro 🚀

Aura Port Scanner Pro, modern bir kullanıcı arayüzüne sahip, hızlı ve verimli bir ağ port tarama aracıdır. Python ve CustomTkinter kullanılarak geliştirilmiştir.

## 🌟 Özellikler

- **Hızlı Tarama:** Multi-threading (çoklu izlek) teknolojisi ile saniyeler içinde binlerce portu tarayın.
- **Akıllı Servis Tespiti:** Açık portlarda çalışan servisleri (HTTP, FTP, SSH vb.) otomatik olarak tanımlar.
- **Banner Grabbing:** Servislerin versiyon bilgilerini ve bağlantı detaylarını yakalar.
- **Geçmiş Yönetimi:** Yapılan son taramaları kaydeder ve tek tıkla tekrar erişmenizi sağlar.
- **Dışa Aktarma:** Tarama sonuçlarını CSV formatında rapor olarak kaydedin.
- **Modern Arayüz:** Koyu ve Açık tema desteği, tamamen duyarlı tasarım.
- **Çoklu Dil Desteği:** Türkçe ve İngilizce dil seçenekleri.

## 🛠️ Kurulum (Geliştiriciler İçin)

Projeyi yerel makinenizde çalıştırmak için:

1. Bu depoyu klonlayın.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install customtkinter pillow
   ```
3. Uygulamayı çalıştırın:
   ```bash
   python main.py
   ```

## 📦 EXE Haline Getirme

Uygulamayı tek bir `.exe` dosyası olarak paketlemek için şu adımları izleyin:

1. `pyinstaller` kütüphanesini yükleyin:
   ```bash
   pip install pyinstaller
   ```
2. Aşağıdaki komutu kullanarak exe dosyasını oluşturun:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --icon "app_icon.ico" --add-data "C:/Users/USER/AppData/Local/Programs/Python/Python314/Lib/site-packages/customtkinter;customtkinter/"  main.py
   ```
   _(Not: `customtkinter` yolunu kendi Python kurulumunuza göre güncellemeniz gerekebilir.)_

## 🤝 Katkıda Bulunma

Hata bildirimleri veya özellik önerileri için lütfen bir issue açın veya pull request gönderin.

---

**Geliştiren:** [Antigravity AI]
**Lisans:** MIT
