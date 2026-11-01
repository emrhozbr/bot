# Alfa Trade Club (Mahşerin 4 Atlısı) — Android APK Projesi

Bu klasör, `botv4.0.2.py` dosyanızdaki tüm strateji motorunun (`Kırılım Yoksa Swing Yoktur`, `8 HTF Safe Bölge: 1.QML > 2.OB > 3.Fresh > 4.OTE`, `Mahşerin 4 Atlısı Puanlama`, `Pine Script v6` ve `Canlı TradingView HTML Grafik`) masaüstü bağımlılıklarından (`customtkinter`, `matplotlib`) arındırılarak **Flet** mobil arayüzüne dönüştürülmüş tam sürümüdür.

## Yöntem A: Bilgisayarınıza Hiçbir SDK Kurmadan Ücretsiz Bulutta APK Üretmek (Önerilen)
1. Ücretsiz bir GitHub hesabı açın ve yeni (Private/Gizli) bir repo oluşturun.
2. Bu ZIP içindeki tüm dosyaları (`main.py`, `pyproject.toml`, `requirements.txt`, `.github/workflows/build_apk.yml`) reponuza yükleyin.
3. GitHub reponuzda üst menüdeki **Actions** sekmesine tıklayın.
4. Soldaki **Android APK Olustur (Flet)** iş akışını seçip **Run workflow** butonuna basın.
5. Yaklaşık 6-8 dakika içinde derleme tamamlanır ve sayfanın altındaki **Artifacts** kısmından **`Alfa-Trade-Bot-Android-APK`** dosyasını indirip doğrudan Android telefonunuza kurabilirsiniz.

## Yöntem B: Kendi Bilgisayarınızda Komut Satırından APK Üretmek
```bash
pip install "flet[all]>=0.24.0" ccxt pandas numpy requests
# Önce masaüstünde mobil görünümü test etmek için:
flet run main.py --android

# Doğrudan APK dosyası üretmek için (Flutter SDK kurulu olmalıdır):
flet build apk
```
