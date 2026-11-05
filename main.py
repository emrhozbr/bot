# ==============================================================================
# BULUT SENKRONİZASYON (PC <-> ANDROID EŞLEŞTİRME) VE TEK TUŞLA OTA GÜNCELLEME
# ==============================================================================
import base64 as _b64
import re as _re
import re

BOT_VERSIYONU = "v4.0.9"
BOT_DOSYA_ADI = "botv4.0.9.py"
if "BIRINCIL_BOLGE_OLCEK_CARPANI" not in globals(): BIRINCIL_BOLGE_OLCEK_CARPANI = 5.0
if "BIRINCIL_VIP_EK_SLOT" not in globals(): BIRINCIL_VIP_EK_SLOT = 3
if "IKINCIL_REZERV_SLOT" not in globals(): IKINCIL_REZERV_SLOT = 2
if "KYSY_HTF_ATR_CARPANI" not in globals(): KYSY_HTF_ATR_CARPANI = 1.85
if "KYSY_LTF_ATR_CARPANI" not in globals(): KYSY_LTF_ATR_CARPANI = 1.30
if "EQH_EQL_TOL_ATR" not in globals(): EQH_EQL_TOL_ATR = 0.30
if "SFP_MIN_IGNE_ATR" not in globals(): SFP_MIN_IGNE_ATR = 0.12
if "IKINCIL_BOLGE_GIRIS_AKTIF" not in globals(): IKINCIL_BOLGE_GIRIS_AKTIF = True
if "GEMINI_API_KEY" not in globals(): GEMINI_API_KEY = ""
if "GEMINI_MODEL" not in globals(): GEMINI_MODEL = "gemini-2.5-flash"
if "GEMINI_OTOMATIK_ISLEM_YORUMU" not in globals(): GEMINI_OTOMATIK_ISLEM_YORUMU = True
if "htf_1_oncelik_radar_cache" not in globals(): htf_1_oncelik_radar_cache = {}

if "GITHUB_REPO_ADRESI" not in globals() or not GITHUB_REPO_ADRESI:
    GITHUB_REPO_ADRESI = "emrhozbr/bot"
if "GITHUB_TOKEN" not in globals():
    GITHUB_TOKEN = ""

BULUT_SENK_AKTIF = True
AKTIF_OTA_SURUM_BILGISI = "v4.0.9 (Canlı Motor)"
_SON_BULUT_OKUMA_TS = 0.0
_SON_BULUT_YAZMA_HASH = ""
_SON_PC_AYAR_TS = 0.0
_BULUT_DOSYA_ADI = "senkron_durum.json"
_OTA_YEREL_CEKIRDEK = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_cekirdek_motor.py')
_OTA_YEREL_UI = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_flet_ui.py')
_OTA_META_DOSYA = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_meta_bilgi.json')

def masaustu_ayar_sozlugu_uret():
    """Aktif tüm strateji, MTF ve risk ayarlarını tek pakette toplar (Arka planda sıfırlanmayı önler)."""
    return {
        "guncelleme_ts": time.time(),
        "bot_versiyonu": globals().get("BOT_VERSIYONU", "v4.0.9"),
        "piyasa_modu": PIYASA_MODU,
        "testnet": bool(TESTNET_AKTIF),
        "kaldirac": int(KALDIRAC),
        "marjin_tipi": MARJIN_TIPI,
        "maks_marjin": F(MAKS_MARJIN_USDT),
        "islem_risk": F(ISLEM_BASI_RISK_USDT),
        "rr_orani": F(RISK_ODUL_ORANI),
        "nihai_tp_rr": F(NIHAI_TP_RR),
        "min_skor": int(MIN_CONFLUENCE_SKORU),
        "mtf_sablon": AKTIF_MTF_SABLONU,
        "htf_periyot": HTF_PERIYOT,
        "mtf_periyot": MTF_PERIYOT,
        "ltf_periyot": LTF_PERIYOT,
        "islem_tarzi": ISLEM_TARZI_MODU,
        "risk_seviyesi": AKTIF_RISK_SEVIYESI,
        "stop_modu": STOP_BELIRLEME_MODU,
        "parite_limiti": int(ae),
        "kysy_htf_atr": F(globals().get("KYSY_HTF_ATR_CARPANI", 1.85)),
        "kysy_ltf_atr": F(globals().get("KYSY_LTF_ATR_CARPANI", 1.30)),
        "eqh_tol_atr": F(globals().get("EQH_EQL_TOL_ATR", 0.30)),
        "sfp_min_atr": F(globals().get("SFP_MIN_IGNE_ATR", 0.12)),
        "ikincil_bolge_aktif": bool(globals().get("IKINCIL_BOLGE_GIRIS_AKTIF", True)),
        "birincil_olcek_carpani": F(globals().get("BIRINCIL_BOLGE_OLCEK_CARPANI", 5.0))
    }

def _sozlukten_ayarlari_uygula(d: dict):
    """Hem yerel diskten hem de Masaüstü (PC) senkronizasyonundan gelen ayarları eksiksiz uygular."""
    global API_KEY, API_SECRET, TESTNET_AKTIF, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GITHUB_REPO_ADRESI, GITHUB_TOKEN
    global STOP_BELIRLEME_MODU, PIYASA_MODU, MARJIN_TIPI, KALDIRAC, MAKS_MARJIN_USDT, ISLEM_BASI_RISK_USDT
    global RISK_ODUL_ORANI, NIHAI_TP_RR, MIN_CONFLUENCE_SKORU, AKTIF_MTF_SABLONU, AKTIF_RISK_SEVIYESI, ae
    global KYSY_HTF_ATR_CARPANI, KYSY_LTF_ATR_CARPANI, EQH_EQL_TOL_ATR, SFP_MIN_IGNE_ATR, IKINCIL_BOLGE_GIRIS_AKTIF, BIRINCIL_BOLGE_OLCEK_CARPANI
    if not I(d, dict):
        return
    if d.get("api_key"): API_KEY = str(d["api_key"]).strip()
    if d.get("api_secret"): API_SECRET = str(d["api_secret"]).strip()
    if "testnet" in d: TESTNET_AKTIF = bool(d["testnet"])
    if d.get("telegram_token"): TELEGRAM_TOKEN = str(d["telegram_token"]).strip()
    if d.get("telegram_chat_id"): TELEGRAM_CHAT_ID = str(d["telegram_chat_id"]).strip()
    if d.get("github_repo"): GITHUB_REPO_ADRESI = str(d["github_repo"]).strip()
    if d.get("github_token"): GITHUB_TOKEN = str(d["github_token"]).strip()
    if d.get("stop_modu"): STOP_BELIRLEME_MODU = str(d["stop_modu"]).strip()
    if d.get("piyasa_modu"): PIYASA_MODU = str(d["piyasa_modu"]).strip()
    if d.get("marjin_tipi"): MARJIN_TIPI = str(d["marjin_tipi"]).strip()
    # Önce MTF şablonunu uygula, ardından kullanıcının özel RR ve sayısal ayarlarını koru!
    if d.get("mtf_sablon"): mtf_sablonu_uygula(str(d["mtf_sablon"]))
    if d.get("risk_seviyesi"): AKTIF_RISK_SEVIYESI = str(d["risk_seviyesi"])
    if "kaldirac" in d and F(d["kaldirac"]) >= 1: KALDIRAC = M(1, N(125, int(F(d["kaldirac"]))))
    if "maks_marjin" in d and F(d["maks_marjin"]) >= 5: MAKS_MARJIN_USDT = F(d["maks_marjin"])
    if "islem_risk" in d and F(d["islem_risk"]) >= 0.1: ISLEM_BASI_RISK_USDT = F(d["islem_risk"])
    if "rr_orani" in d and F(d["rr_orani"]) >= 0.5:
        RISK_ODUL_ORANI = F(d["rr_orani"])
        NIHAI_TP_RR = F(d.get("nihai_tp_rr") or M(NIHAI_TP_RR, RISK_ODUL_ORANI + 1.0))
    if "min_skor" in d and F(d["min_skor"]) >= 10: MIN_CONFLUENCE_SKORU = M(10, N(100, int(F(d["min_skor"]))))
    if "parite_limiti" in d: ae = M(0, int(F(d["parite_limiti"])))
    if "kysy_htf_atr" in d: KYSY_HTF_ATR_CARPANI = M(0.6, N(4.0, F(d["kysy_htf_atr"])))
    if "kysy_ltf_atr" in d: KYSY_LTF_ATR_CARPANI = M(0.5, N(3.5, F(d["kysy_ltf_atr"])))
    if "eqh_tol_atr" in d: EQH_EQL_TOL_ATR = M(0.08, N(1.2, F(d["eqh_tol_atr"])))
    if "sfp_min_atr" in d: SFP_MIN_IGNE_ATR = M(0.03, N(0.8, F(d["sfp_min_atr"])))
    if "ikincil_bolge_aktif" in d: IKINCIL_BOLGE_GIRIS_AKTIF = bool(d["ikincil_bolge_aktif"])
    if "birincil_olcek_carpani" in d: BIRINCIL_BOLGE_OLCEK_CARPANI = M(1.5, N(10.0, F(d["birincil_olcek_carpani"])))

def _api_kaydet_tam():
    """Tüm ayarları kalıcı diske ve Flet client_storage hafızasına tam kaydeder."""
    try:
        mev = masaustu_ayar_sozlugu_uret()
        mev.update({
            "api_key": API_KEY, "api_secret": API_SECRET, "testnet": bool(TESTNET_AKTIF),
            "telegram_token": TELEGRAM_TOKEN, "telegram_chat_id": TELEGRAM_CHAT_ID,
            "github_repo": GITHUB_REPO_ADRESI, "github_token": GITHUB_TOKEN
        })
        for d_yol in (bd, "binance_api_config.json"):
            try:
                with open(d_yol, "w", encoding="utf-8") as f:
                    json.dump(mev, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        if _AKTIF_PAGE_REF is not None:
            try:
                _AKTIF_PAGE_REF.client_storage.set("alfa_api_config", mev)
            except Exception:
                pass
    except Exception:
        pass

try:
    _api_yukle()
except Exception:
    pass

def _github_headers(token_str=""):
    tok = (token_str or GITHUB_TOKEN or "").strip()
    hdr = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AlfaTradeBot-OTA",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    if tok:
        hdr["Authorization"] = f"Bearer {tok}" if tok.startswith("github_pat_") else f"token {tok}"
    return hdr

def _github_dosya_indir(hedef_repo: str, dosya_adi: str, hedef_token: str = ""):
    ts = int(time.time())
    hdr = _github_headers(hedef_token)
    try:
        hdr_raw = dict(hdr)
        hdr_raw["Accept"] = "application/vnd.github.v3.raw"
        api_url = f"https://api.github.com/repos/{hedef_repo}/contents/{dosya_adi}?ref=main&t={ts}"
        r = _HTTP_SES.get(api_url, headers=hdr_raw, timeout=15)
        if r.status_code == 200 and len(r.text) > 500 and not r.text.strip().startswith('{"message":'):
            return r.text
    except Exception:
        pass
    try:
        api_url = f"https://api.github.com/repos/{hedef_repo}/contents/{dosya_adi}?ref=main&t={ts}"
        r = _HTTP_SES.get(api_url, headers=hdr, timeout=15)
        if r.status_code == 200 and isinstance(r.json(), dict) and "content" in r.json():
            return _b64.b64decode(r.json()["content"]).decode("utf-8")
    except Exception:
        pass
    try:
        raw_url = f"https://raw.githubusercontent.com/{hedef_repo}/main/{dosya_adi}?t={ts}"
        r2 = _HTTP_SES.get(raw_url, headers=hdr, timeout=15)
        if r2.status_code == 200 and len(r2.text) > 500:
            return r2.text
    except Exception:
        pass
    return None

def _repodaki_guncel_bot_dosyalarini_bul(hedef_repo: str, hedef_token: str = ""):
    varsayilan = ["botv4.1.0.py", "botv4.0.9.py", "botv4.0.8.py", "botv4.0.7.py", "botv4.0.6.py", "botv4.0.5.py", "botv4.0.4.py", "botv4.0.3.py", "botv4.0.2.py"]
    try:
        hdr = _github_headers(hedef_token)
        url = f"https://api.github.com/repos/{hedef_repo}/contents?t={int(time.time())}"
        r = _HTTP_SES.get(url, headers=hdr, timeout=10)
        if r.status_code == 200 and isinstance(r.json(), list):
            bulunanlar = []
            for item in r.json():
                ad = str(item.get("name", ""))
                if ad.startswith("botv") and ad.endswith(".py"):
                    sayilar = tuple(int(x) for x in _re.findall(r"\d+", ad))
                    bulunanlar.append((sayilar, ad))
            if bulunanlar:
                bulunanlar.sort(key=lambda x: x[0], reverse=True)
                return [ad for _, ad in bulunanlar]
    except Exception:
        pass
    return varsayilan

def masaustu_kodunu_mobil_cekirdege_ayikla(kaynak_kod: str) -> str:
    """botv4.0.9.py içindeki tüm yeni strateji ve islem_rontgeni_olustur fonksiyonlarını kesmeden alır;
    ancak kullanıcının ayarlarını, açık işlemlerini ve borsa bağlantısını ASLA ezmez!"""
    ek_ust = [
        "import re",
        "BOT_VERSIYONU='v4.0.9';BOT_DOSYA_ADI='botv4.0.9.py';",
        "if 'BIRINCIL_BOLGE_OLCEK_CARPANI' not in globals(): BIRINCIL_BOLGE_OLCEK_CARPANI=5.0",
        "if 'BIRINCIL_VIP_EK_SLOT' not in globals(): BIRINCIL_VIP_EK_SLOT=3",
        "if 'IKINCIL_REZERV_SLOT' not in globals(): IKINCIL_REZERV_SLOT=2",
        "if 'KYSY_HTF_ATR_CARPANI' not in globals(): KYSY_HTF_ATR_CARPANI=1.85",
        "if 'KYSY_LTF_ATR_CARPANI' not in globals(): KYSY_LTF_ATR_CARPANI=1.30",
        "if 'EQH_EQL_TOL_ATR' not in globals(): EQH_EQL_TOL_ATR=0.30",
        "if 'SFP_MIN_IGNE_ATR' not in globals(): SFP_MIN_IGNE_ATR=0.12",
        "if 'IKINCIL_BOLGE_GIRIS_AKTIF' not in globals(): IKINCIL_BOLGE_GIRIS_AKTIF=True",
        "if 'htf_1_oncelik_radar_cache' not in globals(): htf_1_oncelik_radar_cache={}"
    ]
    if "def indiktorleri_ekle(df):" in kaynak_kod:
        ana_govde = kaynak_kod[kaynak_kod.index("def indiktorleri_ekle(df):"):]
    elif "def _f(d,c,i=-2):" in kaynak_kod:
        ana_govde = kaynak_kod[kaynak_kod.index("def _f(d,c,i=-2):"):]
    else:
        ana_govde = kaynak_kod

    # Sadece masaüstü GUI sınıfından (TradingBotGUI) veya mobil yeniden tanımlamadan kes!
    # Böylece islem_rontgeni_olustur() fonksiyonu da çekirdeğin içinde kalır ve grafikler çökmez.
    for bitis_isareti in (
        "def _github_headers(",
        "def masaustu_ayar_sozlugu_uret(",
        "def masaustu_kodunu_mobil_cekirdege_ayikla",
        "ctk.set_appearance_mode",
        "class TradingBotGUI",
        "class AlfaMobileBotEngine",
        "def main(page"
    ):
        if bitis_isareti in ana_govde:
            ana_govde = ana_govde[:ana_govde.index(bitis_isareti)]

    yasak_kelimeler = (
        "import customtkinter", "from tkinter", "matplotlib", "NavigationToolbar2Tk",
        "FigureCanvasTkAgg", "import ccxt", "acik_islemler={}", "aC=None",
        "bd='binance_api_config.json'", "_api_yukle();_ig_yukle();_ak_yukle();",
        "GITHUB_REPO_ADRESI =", "GITHUB_TOKEN ="
    )
    cikti = list(ek_ust)
    for s in ana_govde.splitlines():
        if any(y in s for y in yasak_kelimeler):
            continue
        cikti.append(s)

    metin = "\n".join(cikti)
    metin = metin.replace(
        'dosya_yolu=os.path.abspath(f"tv_canli_{O.replace(\':\',\'_\').replace(\'/\',\'_\')}_{tf_secim}.html")',
        'dosya_yolu=os.path.join(ANDROID_VERI_DIZINI, f"tv_canli_{O.replace(\':\',\'_\').replace(\'/\',\'_\')}_{tf_secim}.html")'
    )
    # Android'de FileUriExposedException hatasını önlemek için webbrowser.open('file://...') çağrısını devre dışı bırak
    metin = metin.replace(
        "if os.name=='nt':os.startfile(dosya_yolu)\n  else:webbrowser.open(Path(dosya_yolu).as_uri())",
        "if os.name=='nt' and 'KALICI_VERI_DIZINI' not in globals():os.startfile(dosya_yolu)"
    )
    metin = metin.replace("webbrowser.open(Path(dosya_yolu).as_uri())", "None")
    metin = metin.replace("webbrowser.open('file://'+dosya_yolu)", "None")
    return metin

def masaustu_gui_ozelliklerini_ayikla(kaynak_kod: str) -> dict:
    meta = {"versiyon": "", "baslik": ""}
    try:
        m_all = _re.findall(r"v\d+\.\d+\.\d+", kaynak_kod)
        if m_all:
            m_all.sort(key=lambda v: tuple(int(x) for x in _re.findall(r"\d+", v)), reverse=True)
            meta["versiyon"] = m_all[0]
        m_title = _re.search(r"q\.title\(['\"]([^'\"]+)['\"]\)", kaynak_kod)
        if m_title:
            meta["baslik"] = m_title.group(1)
    except Exception:
        pass
    return meta

def ota_strateji_guncelle(repo_adresi=None, token=None, yerel_dosya_yolu=None):
    global GITHUB_REPO_ADRESI, GITHUB_TOKEN, AKTIF_OTA_SURUM_BILGISI
    hedef_repo = (repo_adresi or GITHUB_REPO_ADRESI or "emrhozbr/bot").strip()
    hedef_token = (token if token is not None else GITHUB_TOKEN).strip()
    GITHUB_REPO_ADRESI = hedef_repo
    if hedef_token:
        GITHUB_TOKEN = hedef_token

    kaynak_kod = None
    kaynak_adi = ""
    if yerel_dosya_yolu and os.path.exists(yerel_dosya_yolu):
        with open(yerel_dosya_yolu, "r", encoding="utf-8") as f:
            kaynak_kod = f.read()
        kaynak_adi = os.path.basename(yerel_dosya_yolu)
    else:
        bot_dosyalari = _repodaki_guncel_bot_dosyalarini_bul(hedef_repo, hedef_token)
        for dosya in bot_dosyalari:
            indirilen = _github_dosya_indir(hedef_repo, dosya, hedef_token)
            if indirilen and len(indirilen) > 1000:
                kaynak_kod = indirilen
                kaynak_adi = dosya
                break
        if not kaynak_kod:
            main_indirilen = _github_dosya_indir(hedef_repo, "main.py", hedef_token)
            if main_indirilen and len(main_indirilen) > 1000:
                kaynak_kod = main_indirilen
                kaynak_adi = "main.py"

    if not kaynak_kod or len(kaynak_kod) < 500:
        return (False, "⚠️ GitHub üzerinden güncel dosya okunamadı! Ayarlar'dan GitHub Token kontrol edin.")

    try:
        yedek_acik = dict(acik_islemler)
        yedek_s, yedek_w = F(S), F(W)
        yedek_calisiyor = bool(bot_calisiyor)
        yedek_ayar = masaustu_ayar_sozlugu_uret()
        yedek_api = (API_KEY, API_SECRET, TESTNET_AKTIF, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PIYASA_MODU, GITHUB_REPO_ADRESI, GITHUB_TOKEN)

        cekirdek_kod = masaustu_kodunu_mobil_cekirdege_ayikla(kaynak_kod)
        with open(_OTA_YEREL_CEKIRDEK, "w", encoding="utf-8") as f:
            f.write(cekirdek_kod)
        exec(compile(cekirdek_kod, _OTA_YEREL_CEKIRDEK, "exec"), globals())

        meta = masaustu_gui_ozelliklerini_ayikla(kaynak_kod)
        ver_str = meta.get("versiyon") or globals().get("BOT_VERSIYONU", "v4.0.9")
        AKTIF_OTA_SURUM_BILGISI = f"{ver_str} [{kaynak_adi}] ({datetime.now().strftime('%H:%M:%S')})"
        try:
            with open(_OTA_META_DOSYA, "w", encoding="utf-8") as f:
                json.dump({"aktif_surum": AKTIF_OTA_SURUM_BILGISI, "kaynak_dosya": kaynak_adi}, f, ensure_ascii=False)
        except Exception:
            pass

        acik_islemler.clear()
        acik_islemler.update(yedek_acik)
        globals()["S"] = yedek_s
        globals()["W"] = yedek_w
        globals()["bot_calisiyor"] = yedek_calisiyor
        (
            globals()["API_KEY"], globals()["API_SECRET"], globals()["TESTNET_AKTIF"],
            globals()["TELEGRAM_TOKEN"], globals()["TELEGRAM_CHAT_ID"], globals()["PIYASA_MODU"],
            globals()["GITHUB_REPO_ADRESI"], globals()["GITHUB_TOKEN"]
        ) = yedek_api
        # Kullanıcının mevcut ayarlarını geri yükle (OTA'nın ayarları bozmasını engelle)
        _sozlukten_ayarlari_uygula(yedek_ayar)
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
        _ak_kaydet()
        return (True, f"✅ OTA Güncelleme Başarılı! Aktif Sürüm: {AKTIF_OTA_SURUM_BILGISI}")
    except Exception as ex:
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
        return (False, f"⚠️ OTA Kod Dönüştürme Hatası: {ex}")

def _kayitli_ota_varsa_yukle():
    global AKTIF_OTA_SURUM_BILGISI
    try:
        if os.path.exists(_OTA_META_DOSYA):
            with open(_OTA_META_DOSYA, "r", encoding="utf-8") as f:
                md = json.load(f)
                if isinstance(md, dict) and md.get("aktif_surum"):
                    AKTIF_OTA_SURUM_BILGISI = str(md["aktif_surum"])
        yedek_acik = dict(acik_islemler)
        yedek_s, yedek_w = F(S), F(W)
        yedek_calisiyor = bool(bot_calisiyor)
        yedek_ayar = masaustu_ayar_sozlugu_uret()
        if os.path.exists(_OTA_YEREL_CEKIRDEK):
            with open(_OTA_YEREL_CEKIRDEK, "r", encoding="utf-8") as f:
                kod = f.read()
            if "def indiktorleri_ekle(df):" in kod:
                kod = masaustu_kodunu_mobil_cekirdege_ayikla(kod)
                with open(_OTA_YEREL_CEKIRDEK, "w", encoding="utf-8") as f:
                    f.write(kod)
            if len(kod) > 500:
                exec(compile(kod, _OTA_YEREL_CEKIRDEK, "exec"), globals())
        acik_islemler.update(yedek_acik)
        globals()["S"], globals()["W"] = yedek_s, yedek_w
        globals()["bot_calisiyor"] = yedek_calisiyor
        _sozlukten_ayarlari_uygula(yedek_ayar)
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
    except Exception:
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)

def bulut_durum_gonder(zorla=False):
    global _SON_BULUT_YAZMA_HASH
    if not BULUT_SENK_AKTIF or not GITHUB_TOKEN or not GITHUB_REPO_ADRESI:
        return False
    try:
        nQ = {k: v for k, v in acik_islemler.items() if I(v, dict)}
        veri = {
            "guncelleme_ts": time.time(),
            "guncelleyen_cihaz": "ANDROID_MOBIL",
            "bot_versiyonu": globals().get("BOT_VERSIYONU", "v4.0.9"),
            "ayarlar": masaustu_ayar_sozlugu_uret(),
            "acik_islemler": nQ,
            "demo_vadeli_bakiye": F(S),
            "gerceklesen_pnl": F(W),
            "islem_gecmisi": ah[:150]
        }
        ozet_str = json.dumps({"a": list(nQ.keys()), "s": R(F(S), 2), "w": R(F(W), 2), "h": L(ah)}, sort_keys=True)
        if not zorla and ozet_str == _SON_BULUT_YAZMA_HASH:
            return True
        _SON_BULUT_YAZMA_HASH = ozet_str
        api_url = f"https://api.github.com/repos/{GITHUB_REPO_ADRESI.strip()}/contents/{_BULUT_DOSYA_ADI}"
        hdr = _github_headers(GITHUB_TOKEN)
        mevcut_sha = None
        r_get = _HTTP_SES.get(api_url, headers=hdr, timeout=6)
        if r_get.status_code == 200 and isinstance(r_get.json(), dict):
            mevcut_sha = r_get.json().get("sha")
        icerik_b64 = _b64.b64encode(json.dumps(veri, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
        payload = {
            "message": f"Sync: ANDROID_MOBIL ({datetime.now().strftime('%H:%M:%S')})",
            "content": icerik_b64
        }
        if mevcut_sha:
            payload["sha"] = mevcut_sha
        r_put = _HTTP_SES.put(api_url, headers=hdr, json=payload, timeout=8)
        return r_put.status_code in (200, 201)
    except Exception:
        return False

def bulut_durum_cek(zorla=False):
    """Masaüstünde (PC) yapılan ayar, sürüm veya işlem değişikliklerini otomatik algılayıp telefona uygular!"""
    global _SON_BULUT_OKUMA_TS, _SON_PC_AYAR_TS, S, W, ah
    simdi = time.time()
    if not zorla and (simdi - _SON_BULUT_OKUMA_TS < 12.0):
        return False
    _SON_BULUT_OKUMA_TS = simdi
    degisti = False
    if BULUT_SENK_AKTIF and GITHUB_REPO_ADRESI:
        try:
            hdr = _github_headers(GITHUB_TOKEN)
            api_url = f"https://api.github.com/repos/{GITHUB_REPO_ADRESI.strip()}/contents/{_BULUT_DOSYA_ADI}?t={int(simdi)}"
            r = _HTTP_SES.get(api_url, headers=hdr, timeout=6)
            if r.status_code == 200 and isinstance(r.json(), dict) and "content" in r.json():
                d = json.loads(_b64.b64decode(r.json()["content"]).decode("utf-8"))
                if I(d, dict):
                    uzak_ts = F(d.get("guncelleme_ts") or 0.0)
                    # 1) MASAÜSTÜNDE AYAR VEYA SÜRÜM DEĞİŞTİYSE TELEFONA OTOMATİK UYGULA!
                    if d.get("guncelleyen_cihaz") == "PC_MASAUSTU":
                        uzak_ayar = d.get("ayarlar")
                        if I(uzak_ayar, dict):
                            ayar_ts = F(uzak_ayar.get("guncelleme_ts") or uzak_ts)
                            if ayar_ts > _SON_PC_AYAR_TS:
                                _SON_PC_AYAR_TS = ayar_ts
                                _sozlukten_ayarlari_uygula(uzak_ayar)
                                _api_kaydet_tam()
                                degisti = True
                        uzak_ver = str(d.get("bot_versiyonu") or "")
                        if uzak_ver and uzak_ver not in str(AKTIF_OTA_SURUM_BILGISI):
                            threading.Thread(target=ota_strateji_guncelle, args=(GITHUB_REPO_ADRESI, GITHUB_TOKEN), daemon=True).start()
                    # 2) AÇIK İŞLEMLERİ SENKRONİZE ET (Yerel açık işlemleri boş veriyle silme)
                    uzak_acik = d.get("acik_islemler")
                    mevcut_anahtarlar = {k for k, v in acik_islemler.items() if I(v, dict)}
                    uzak_anahtarlar = {k for k, v in uzak_acik.items() if I(v, dict)} if I(uzak_acik, dict) else set()
                    if mevcut_anahtarlar and not uzak_anahtarlar:
                        if GITHUB_TOKEN:
                            threading.Thread(target=bulut_durum_gonder, args=(True,), daemon=True).start()
                    elif I(uzak_acik, dict) and uzak_anahtarlar:
                        for k_u, v_u in uzak_acik.items():
                            if I(v_u, dict):
                                if not I(acik_islemler.get(k_u), dict):
                                    acik_islemler[k_u] = v_u
                                    degisti = True
                                elif v_u.get("kismi_tp_alindi") and not acik_islemler[k_u].get("kismi_tp_alindi"):
                                    acik_islemler[k_u].update(v_u)
                                    degisti = True
                    uzak_ig = d.get("islem_gecmisi")
                    if I(uzak_ig, list) and L(uzak_ig) > L(ah):
                        ah = uzak_ig
                        degisti = True
                    if degisti:
                        _ak_kaydet()
        except Exception:
            pass
    return degisti
