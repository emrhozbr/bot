# ==============================================================================
# ALFA TRADE CLUB (MAHŞERİN 4 ATLISI + YT PART 1-13) — NATIVE ANDROID APK (FLET)
# ==============================================================================
import os, sys, gc, json, webbrowser, time, threading, socket, math, hmac, hashlib, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
import requests
import flet as ft

# ------------------------------------------------------------------------------
# ANDROID SAF PYTHON (PURE-PYTHON) NUMPY, PANDAS & CCXT MOTORU
# (C Derleyicisi Gerektirmez & sys.modules Kaydı İle Her Türlü Import'u Destekler)
# ------------------------------------------------------------------------------
try:
    np = __import__('numpy')
except ImportError:
    class _NPArray(list):
        def min(self): return min(self) if self else 0.0
        def max(self): return max(self) if self else 0.0
        def mean(self): return (sum(self) / len(self)) if self else 0.0
        def astype(self, dtype=float): return _NPArray([dtype(x) for x in self])
        @property
        def values(self): return self
        def __getitem__(self, item):
            res = super().__getitem__(item)
            return _NPArray(res) if isinstance(item, slice) else res

    class _NPModule:
        nan = float("nan")
        integer = int
        ndarray = _NPArray
        float64 = float
        @staticmethod
        def arange(n): return _NPArray(range(int(n)))
        @staticmethod
        def array(v, dtype=float): return _NPArray([dtype(x) for x in v])

    np = _NPModule()
    sys.modules["numpy"] = np

try:
    pd = __import__('pandas')
except ImportError:
    class _Series:
        def __init__(self, data):
            self._data = [float(x) if x is not None and x == x else float("nan") for x in data]
        def __len__(self): return len(self._data)
        def __iter__(self): return iter(self._data)
        @property
        def empty(self): return len(self._data) == 0
        @property
        def values(self): return np.array(self._data)
        def astype(self, dtype=float):
            return _Series([0.0 if (x != x or x is None) else dtype(x) for x in self._data])
        def to_numpy(self, dtype=float, copy=False):
            return np.array([0.0 if (x != x or x is None) else float(x) for x in self._data])
        @property
        def iloc(self): return self
        def __getitem__(self, idx):
            if isinstance(idx, slice): return _Series(self._data[idx])
            return self._data[idx]
        def _op(self, other, fn):
            if isinstance(other, _Series):
                return _Series([fn(a, b) for a, b in zip(self._data, other._data)])
            return _Series([fn(a, float(other)) for a in self._data])
        def __sub__(self, o): return self._op(o, lambda a, b: a - b)
        def __add__(self, o): return self._op(o, lambda a, b: a + b)
        def __mul__(self, o): return self._op(o, lambda a, b: a * b)
        def __truediv__(self, o): return self._op(o, lambda a, b: a / b if b != 0 and b == b else float("nan"))
        def __rsub__(self, o): return self._op(o, lambda a, b: float(o) - a)
        def __radd__(self, o): return self._op(o, lambda a, b: float(o) + a)
        def __rmul__(self, o): return self._op(o, lambda a, b: float(o) * a)
        def __rtruediv__(self, o): return self._op(o, lambda a, b: float(o) / a if a != 0 and a == a else float("nan"))
        def __neg__(self): return _Series([-a for a in self._data])
        def __gt__(self, o):
            vals = o._data if isinstance(o, _Series) else [o]*len(self._data)
            return [a > b for a, b in zip(self._data, vals)]
        def __lt__(self, o):
            vals = o._data if isinstance(o, _Series) else [o]*len(self._data)
            return [a < b for a, b in zip(self._data, vals)]
        def __ge__(self, o):
            vals = o._data if isinstance(o, _Series) else [o]*len(self._data)
            return [a >= b for a, b in zip(self._data, vals)]
        def __le__(self, o):
            vals = o._data if isinstance(o, _Series) else [o]*len(self._data)
            return [a <= b for a, b in zip(self._data, vals)]
        def abs(self): return _Series([abs(a) for a in self._data])
        def shift(self, n=1):
            if n <= 0: return _Series(self._data[:])
            return _Series([float("nan")]*n + self._data[:-n])
        def diff(self, n=1): return self - self.shift(n)
        def where(self, cond, other=0.0):
            return _Series([a if c else float(other) for a, c in zip(self._data, cond)])
        def replace(self, old, new):
            return _Series([new if a == old else a for a in self._data])
        def fillna(self, val):
            return _Series([float(val) if (a != a or a is None) else a for a in self._data])
        def bfill(self):
            out = self._data[:]
            last = 0.0
            for i in range(len(out)-1, -1, -1):
                if out[i] == out[i] and out[i] is not None: last = out[i]
                else: out[i] = last
            return _Series(out)
        def rolling(self, win):
            data = self._data
            class _Roll:
                def mean(s):
                    res = []
                    for i in range(len(data)):
                        if i + 1 < win: res.append(float("nan"))
                        else:
                            w = [x for x in data[i+1-win:i+1] if x == x]
                            res.append(sum(w)/len(w) if w else float("nan"))
                    return _Series(res)
            return _Roll()
        def cumsum(self):
            s = 0.0; out = []
            for a in self._data:
                if a == a and a is not None: s += a
                out.append(s)
            return _Series(out)
        def min(self):
            v = [x for x in self._data if x == x]
            return min(v) if v else 0.0
        def max(self):
            v = [x for x in self._data if x == x]
            return max(v) if v else 0.0
        def mean(self):
            v = [x for x in self._data if x == x]
            return (sum(v)/len(v)) if v else 0.0
        def idxmin(self):
            v = [(x, idx) for idx, x in enumerate(self._data) if x == x]
            return min(v)[1] if v else 0
        def idxmax(self):
            v = [(x, idx) for idx, x in enumerate(self._data) if x == x]
            return max(v)[1] if v else 0

    class _DataFrame:
        def __init__(self, data=None, columns=None):
            self._cols = {}
            self.__dict__['_np_c'] = {}
            if isinstance(data, dict):
                for k, v in data.items():
                    self._cols[k] = _Series(v)
            elif isinstance(data, list):
                cols = columns or []
                for idx, c in enumerate(cols):
                    self._cols[c] = _Series([r[idx] for r in data])
        @property
        def columns(self): return list(self._cols.keys())
        @property
        def empty(self): return len(self) == 0
        def __len__(self):
            return len(next(iter(self._cols.values()))) if self._cols else 0
        def copy(self):
            d = _DataFrame()
            for k, v in self._cols.items(): d._cols[k] = _Series(v._data[:])
            return d
        def __getitem__(self, key):
            if isinstance(key, str): return self._cols[key]
            if isinstance(key, list):
                if key and isinstance(key[0], bool):
                    idxs = [i for i, b in enumerate(key) if b]
                    return self._take(idxs)
                d = _DataFrame()
                for k in key: d._cols[k] = self._cols[k]
                return d
            return self
        def __setitem__(self, key, val):
            self._cols[key] = val if isinstance(val, _Series) else _Series(val)
            if '_np_c' in self.__dict__: self.__dict__['_np_c'].pop(key, None)
        def max(self, axis=0):
            n = len(self)
            return _Series([max(self._cols[c]._data[i] for c in self._cols) for i in range(n)])
        def min(self, axis=0):
            n = len(self)
            return _Series([min(self._cols[c]._data[i] for c in self._cols) for i in range(n)])
        def _take(self, idxs):
            d = _DataFrame()
            for k, v in self._cols.items():
                d._cols[k] = _Series([v._data[i] for i in idxs if 0 <= i < len(v._data)])
            return d
        @property
        def iloc(self):
            df_ref = self
            class _ILoc:
                def __getitem__(s, item):
                    n = len(df_ref)
                    if isinstance(item, slice):
                        return df_ref._take(range(*item.indices(n)))
                    i = item if item >= 0 else n + item
                    return {k: v._data[i] for k, v in df_ref._cols.items()}
            return _ILoc()
        @property
        def loc(self):
            df_ref = self
            class _Loc:
                def __getitem__(s, mask):
                    return df_ref[mask]
            return _Loc()
        def reset_index(self, drop=True): return self.copy()
        def iterrows(self):
            n = len(self)
            for i in range(n):
                yield i, {k: v._data[i] for k, v in self._cols.items()}

    class _PDModule:
        DataFrame = _DataFrame
        Series = _Series
        @staticmethod
        def concat(objs, axis=0):
            d = _DataFrame()
            for idx, s in enumerate(objs): d[str(idx)] = s
            return d
        @staticmethod
        def to_datetime(ser, unit='ms', utc=True):
            dts = [datetime.fromtimestamp(float(x)/1000.0, tz=timezone.utc) for x in ser._data]
            class _DTSeries:
                @property
                def iloc(s): return dts
                @property
                def dt(s):
                    class _DTAcc:
                        @property
                        def date(a): return _DTCol([d.date() for d in dts])
                        @property
                        def hour(a): return _DTCol([d.hour for d in dts])
                        @property
                        def weekday(a): return _DTCol([d.weekday() for d in dts])
                    return _DTAcc()
            class _DTCol(list):
                def __eq__(s, o): return _BoolMask([x == o for x in s])
                def __lt__(s, o): return _BoolMask([x < o for x in s])
                def __ge__(s, o): return _BoolMask([x >= o for x in s])
            class _BoolMask(list):
                def __and__(s, o): return _BoolMask([a and b for a, b in zip(s, o)])
            return _DTSeries()

    pd = _PDModule()
    sys.modules["pandas"] = pd

try:
    ccxt = __import__('ccxt')
except ImportError:
    class _BinanceLite:
        def __init__(self, config=None):
            cfg = config or {}
            self.apiKey = cfg.get('apiKey', '')
            self.secret = cfg.get('secret', '')
            self.defaultType = cfg.get('options', {}).get('defaultType', 'future')
            self.sandbox = False
            self.ses = requests.Session()
        def set_sandbox_mode(self, enabled): self.sandbox = bool(enabled)
        def enable_demo_trading(self, enabled): self.sandbox = bool(enabled)
        def _base(self):
            if self.defaultType == 'spot':
                return 'https://testnet.binance.vision' if self.sandbox else 'https://api.binance.com'
            return 'https://testnet.binancefuture.com' if self.sandbox else 'https://fapi.binance.com'
        def _raw_sym(self, sym): return str(sym).split(':')[0].replace('/', '').upper()
        def amount_to_precision(self, sym, amt): return f"{float(amt):.6f}".rstrip('0').rstrip('.') or "0"
        def price_to_precision(self, sym, prc): return f"{float(prc):.6f}".rstrip('0').rstrip('.') or "0"
        def load_markets(self, reload=False):
            url = f"{self._base()}/api/v3/exchangeInfo" if self.defaultType == 'spot' else f"{self._base()}/fapi/v1/exchangeInfo"
            r = self.ses.get(url, timeout=10).json()
            out = {}
            for s in r.get('symbols', []):
                if s.get('quoteAsset') != 'USDT': continue
                sym = f"{s['baseAsset']}/{s['quoteAsset']}"
                out[sym] = {
                    'id': s['symbol'], 'base': s['baseAsset'], 'quote': s['quoteAsset'],
                    'active': s.get('status') == 'TRADING',
                    'spot': self.defaultType == 'spot',
                    'future': self.defaultType != 'spot',
                    'swap': self.defaultType != 'spot',
                    'linear': True
                }
            return out
        def fetch_tickers(self):
            url = f"{self._base()}/api/v3/ticker/24hr" if self.defaultType == 'spot' else f"{self._base()}/fapi/v1/ticker/24hr"
            r = self.ses.get(url, timeout=10).json()
            out = {}
            if isinstance(r, list):
                for t in r:
                    s = t.get('symbol', '')
                    if s.endswith('USDT'):
                        k = f"{s[:-4]}/USDT"
                        out[k] = {'last': float(t.get('lastPrice') or 0), 'quoteVolume': float(t.get('quoteVolume') or 0)}
            return out
        def fetch_ticker(self, sym):
            rs = self._raw_sym(sym)
            url = f"{self._base()}/api/v3/ticker/price?symbol={rs}" if self.defaultType == 'spot' else f"{self._base()}/fapi/v1/ticker/price?symbol={rs}"
            r = self.ses.get(url, timeout=5).json()
            p = float(r.get('price') or 0.0)
            return {'last': p, 'close': p, 'info': r}
        def fetch_ohlcv(self, sym, timeframe='15m', limit=300):
            rs = self._raw_sym(sym)
            url = f"{self._base()}/api/v3/klines" if self.defaultType == 'spot' else f"{self._base()}/fapi/v1/klines"
            r = self.ses.get(url, params={'symbol': rs, 'interval': timeframe, 'limit': limit}, timeout=10).json()
            return [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in r]
        def _signed_req(self, method, path, params=None):
            if not self.apiKey or not self.secret: return {}
            p = dict(params or {})
            p['timestamp'] = int(time.time() * 1000)
            qs = urllib.parse.urlencode(p)
            sig = hmac.new(self.secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
            url = f"{self._base()}{path}?{qs}&signature={sig}"
            hdr = {'X-MBX-APIKEY': self.apiKey}
            resp = self.ses.request(method, url, headers=hdr, timeout=10)
            return resp.json()
        def fetch_balance(self):
            if self.defaultType == 'spot':
                r = self._signed_req('GET', '/api/v3/account')
                for b in r.get('balances', []):
                    if b.get('asset') == 'USDT':
                        fr = float(b.get('free') or 0); lk = float(b.get('locked') or 0)
                        return {'USDT': {'free': fr, 'total': fr + lk}, 'info': r}
            else:
                r = self._signed_req('GET', '/fapi/v2/account')
                tw = float(r.get('totalWalletBalance') or 0); av = float(r.get('availableBalance') or tw)
                return {'USDT': {'free': av, 'total': tw}, 'info': r}
            return {'USDT': {'free': 0.0, 'total': 0.0}}
        def set_leverage(self, lev, sym):
            return self._signed_req('POST', '/fapi/v1/leverage', {'symbol': self._raw_sym(sym), 'leverage': int(lev)})
        def set_margin_mode(self, mode, sym):
            return self._signed_req('POST', '/fapi/v1/marginType', {'symbol': self._raw_sym(sym), 'marginType': str(mode).upper()})
        def cancel_all_orders(self, sym):
            path = '/api/v3/openOrders' if self.defaultType == 'spot' else '/fapi/v1/allOpenOrders'
            return self._signed_req('DELETE', path, {'symbol': self._raw_sym(sym)})
        def create_market_buy_order(self, sym, amt, params=None):
            return self.create_order(sym, 'MARKET', 'BUY', amt, None, params)
        def create_market_sell_order(self, sym, amt, params=None):
            return self.create_order(sym, 'MARKET', 'SELL', amt, None, params)
        def create_order(self, sym, otype, side, amt, price=None, params=None):
            path = '/api/v3/order' if self.defaultType == 'spot' else '/fapi/v1/order'
            p = {'symbol': self._raw_sym(sym), 'side': str(side).upper(), 'type': str(otype).upper(), 'quantity': self.amount_to_precision(sym, amt)}
            if price is not None: p['price'] = self.price_to_precision(sym, price)
            if params: p.update(params)
            return self._signed_req('POST', path, p)

    class _CCXTModule:
        binance = _BinanceLite

    ccxt = _CCXTModule()
    sys.modules["ccxt"] = ccxt

# Masaustu (PC) kutuphaneleri (customtkinter, tkinter, matplotlib) Android'de import edilirse hata vermemesi icin Bos (Mock) Moduller
class _DummyMod:
    def __init__(self, *a, **kw): pass
    def __call__(self, *a, **kw): return self
    def __getattr__(self, name): return self
    def pack(self, *a, **kw): return self
    def grid(self, *a, **kw): return self
    def configure(self, *a, **kw): return self
    def set(self, *a, **kw): return self
    def get(self, *a, **kw): return ""

for _m_name in (
    "customtkinter", "tkinter", "tkinter.ttk", "tkinter.messagebox",
    "matplotlib", "matplotlib.pyplot", "matplotlib.gridspec",
    "matplotlib.patches", "matplotlib.backends", "matplotlib.backends.backend_tkagg"
):
    if _m_name not in sys.modules:
        sys.modules[_m_name] = _DummyMod()


_HTTP_SES = requests.Session()
F, I, R, X, M, N, L, A, G = (float, isinstance, round, Exception, max, min, len, abs, range)
jC, aR, cR, eD = (('Segoe UI', 10, 'bold'), ('Segoe UI', 11, 'bold'), ('Segoe UI', 12, 'bold'), ('Segoe UI', 13, 'bold'))

# Android Kalıcı Depolama Dizini Ayarı
ANDROID_VERI_DIZINI = os.environ.get("FLET_APP_STORAGE_DATA") or os.path.abspath(".")

def _f(d,c,i=-2):
 try:
  m=d.__dict__.get('_np_c')
  if m is None:m={};d.__dict__['_np_c']=m
  a=m.get(c)
  if a is None:
   if c not in d.columns:return 0.0
   a=d[c].to_numpy(dtype=F,copy=False);m[c]=a
  v=F(a[i])
  return 0.0 if v!=v else v
 except X:return 0.0
def _r(r,*cs):
 return tuple((F(r[c])for c in cs))
PIYASA_MODU='her_ikisi';TESTNET_AKTIF=True;KALDIRAC=5;MARJIN_TIPI='ISOLATED';cQ=True;ae=0;bH=150000.0;bs=1000.0;dd=0.01;ISLEM_BASI_RISK_USDT=10.0;dL=2.0;RISK_ODUL_ORANI=3.0;NIHAI_TP_RR=4.0;KISMI_KAR_AL_AKTIF=True;TOPLAM_KAR_KAPAT_USDT=None;MAKS_MARJIN_USDT=100.0;aW=0.0018;a4=6;MIN_CONFLUENCE_SKORU=70;dM=5.5;bI=True;dj=14;eC=1.5;MTF_SABLONLARI={'4h / 1h / 15m (Swing)':('4h','1h','15m'),'4h / 1h / 5m (Alfa Pine MTF)':('4h','1h','5m'),'4h / 30m / 3m (Sniper)':('4h','30m','3m'),'1d / 2h / 15m (Pozisyon)':('1d','2h','15m'),'1d / 1h / 5m (Günlük MTF)':('1d','1h','5m'),'1M / 2h / 15m (Aylık Macro)':('1M','2h','15m'),'1d / 4h / 1h (Pozisyon)':('1d','4h','1h'),'2h / 30m / 5m (Gün İçi)':('2h','30m','5m'),'1h / 15m / 5m (Intraday)':('1h','15m','5m'),'15m / 5m / 1m (Scalp)':('15m','5m','1m')};AKTIF_MTF_SABLONU='4h / 1h / 15m (Swing)';HTF_ZAMAN_DILIMLERI=['4h','1d','1M'];MTF_ZAMAN_DILIMLERI=['2h','1h','30m'];LTF_ZAMAN_DILIMLERI=['15m','5m','3m'];TUM_ZAMAN_DILIMLERI=['1m','3m','5m','15m','30m','1h','2h','4h','6h','12h','1d','1M'];HTF_PERIYOT='4h';MTF_PERIYOT='1h';LTF_PERIYOT='15m';SWING_PENCERE=5;RISK_SEVIYESI_SECENEKLERI={'Düşük Risk (Skor 80+ | 0.75x)':(80,0.75),'Orta Risk (Skor 70+ | 1.0x)':(70,1.0),'Yüksek Risk (Skor 60+ | 1.35x)':(60,1.35),'Agresif Risk (Skor 50+ | 1.75x)':(50,1.75),'Özel (Manuel Skor & Risk)':(MIN_CONFLUENCE_SKORU,1.0)};AKTIF_RISK_SEVIYESI='Orta Risk (Skor 70+ | 1.0x)';RISK_CARPANI=1.0;ISLEM_TARZI_MODU='DayTrade';STOP_BELIRLEME_SECENEKLERI=['HTF Yapıya Göre (Dip/Tepe & OB)','LTF Yapıya Göre (Kırılım/Mum & POI)','Otomatik (Duruma Göre HTF/LTF)'];STOP_BELIRLEME_MODU='HTF Yapıya Göre (Dip/Tepe & OB)';
def mtf_sablonu_uygula(aA, rr_koru=False):
 global AKTIF_MTF_SABLONU,HTF_PERIYOT,MTF_PERIYOT,LTF_PERIYOT,ISLEM_TARZI_MODU,RISK_ODUL_ORANI,NIHAI_TP_RR,a4
 eski_rr = F(RISK_ODUL_ORANI)
 if aA in MTF_SABLONLARI:AKTIF_MTF_SABLONU=aA;HTF_PERIYOT,MTF_PERIYOT,LTF_PERIYOT=MTF_SABLONLARI[aA]
 elif'/'in str(aA):
  of=[p.strip().split()[0]for p in str(aA).split('/')]
  if L(of)==3:AKTIF_MTF_SABLONU=str(aA);HTF_PERIYOT,MTF_PERIYOT,LTF_PERIYOT=(of[0],of[1],of[2])
 if'Scalp'in str(AKTIF_MTF_SABLONU)or LTF_PERIYOT in('1m','3m')or HTF_PERIYOT in('15m','30m'):
  ISLEM_TARZI_MODU='Scalp'
  if not rr_koru:RISK_ODUL_ORANI=1.5;NIHAI_TP_RR=2.5
  a4=10
 else:
  ISLEM_TARZI_MODU='DayTrade'
  if not rr_koru:RISK_ODUL_ORANI=3.0;NIHAI_TP_RR=4.0
  a4=6
 if rr_koru and eski_rr>=0.5:
  RISK_ODUL_ORANI=eski_rr;NIHAI_TP_RR=M(NIHAI_TP_RR,RISK_ODUL_ORANI+1.0)
 return(HTF_PERIYOT,MTF_PERIYOT,LTF_PERIYOT)
am=['BTC/USDT','ETH/USDT','SOL/USDT','BNB/USDT','AVAX/USDT','ARB/USDT','LINK/USDT','ADA/USDT','XRP/USDT','DOGE/USDT','SUI/USDT','OP/USDT'];bo={'USDC','FDUSD','TUSD','BUSD','DAI','USDP','EUR','AEUR','USDT','UST','USTC','PAXG','WBTC','BTCST','USD1','RLUSD','USDE','PYUSD','USDD','FRAX','LUSD','GUSD','XAU'};API_KEY='jerhczXTaGA2GJ41NZfcEv8CZ7plOhtri7wE8SvkL5uKGEvdA2zLxyo5RmtrCiY2';API_SECRET='FyIdXFGMinl6AyzyDEtlG6Et007ih5lHHNtNRHiPJpHfzf8VmJQEiAmpxkuYQ6XV';TELEGRAM_AKTIF=True;TELEGRAM_TOKEN='8547267304:AAGgiawKO7z9qLIrkgUFPnyklEDslJk_KsQ';TELEGRAM_CHAT_ID='485280043';ab=[];bk=list(am);acik_islemler={};a1={};analiz_hafizasi={};an={'1h':{},'15m':{}};S=bs;aQ=0.0;T=0.0;V=0.0;ay=0.0;aq=0.0;W=0.0;lG=0.0;bot_calisiyor=False;bE=0;au=0;aC=None;aw=None;aG=None;ao=None;cm=None;
def borsa_kur(b6=PIYASA_MODU,hj=TESTNET_AKTIF):
 global aC,aw,aG,ao,cm,PIYASA_MODU,TESTNET_AKTIF;PIYASA_MODU,TESTNET_AKTIF=(b6,hj)
 def _mk(t,o8=False):
  qX={'enableRateLimit':True,'timeout':10000,'options':{'defaultType':t,'fetchCurrencies':False,'adjustForTimeDifference':True}}
  if o8:qX.update({'apiKey':API_KEY,'secret':API_SECRET})
  return ccxt.binance(qX)
 aC,aw,aG,ao=(_mk('spot'),_mk('future'),_mk('spot',True),_mk('future',True))
 if TESTNET_AKTIF:
  for fn in[lambda:aG.set_sandbox_mode(True),lambda:ao.enable_demo_trading(True)if hasattr(ao,'enable_demo_trading')else None]:
   try:fn()
   except X:pass
 cm=aC if b6=='spot'else aw;return(aG,ao)
def borsa_baglantisi_olustur(dk='future'):
 borsa_kur(dk,TESTNET_AKTIF);return cm
def _kalici_dizin_hazirla():
    adaylar = []
    env_d = os.environ.get("FLET_APP_STORAGE_DATA")
    if env_d:
        adaylar.append(env_d)
    try:
        ev_d = os.path.join(os.path.expanduser("~"), "alfa_trade_kalici")
        adaylar.append(ev_d)
    except Exception:
        pass
    adaylar.append(os.path.abspath("."))
    for d_yol in adaylar:
        try:
            os.makedirs(d_yol, exist_ok=True)
            test_f = os.path.join(d_yol, ".yazma_test")
            with open(test_f, "w", encoding="utf-8") as tf:
                tf.write("ok")
            os.remove(test_f)
            return d_yol
        except Exception:
            continue
    return ANDROID_VERI_DIZINI

KALICI_VERI_DIZINI = _kalici_dizin_hazirla()
_ESKI_VERI_DIZINI = ANDROID_VERI_DIZINI
ANDROID_VERI_DIZINI = KALICI_VERI_DIZINI
bd = os.path.join(ANDROID_VERI_DIZINI, "binance_api_config.json")
ap = os.path.join(KALICI_VERI_DIZINI, 'islem_gecmisi.json')
aN = os.path.join(KALICI_VERI_DIZINI, 'acik_islemler_durum.json')
_aN_yedek = os.path.join(KALICI_VERI_DIZINI, 'acik_islemler.json')
ah = []
_SON_YEREL_KAYIT_TS = 0.0
_AKTIF_PAGE_REF = None
_ARKA_PLANDA_MI = [False]
_SON_TARAMA_KALP_ATISI = [time.time()]

_SON_PC_AYAR_TS = 0.0
_UI_AYAR_YENILE_FN = None

def masaustu_ayar_sozlugu_uret():
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
    global API_KEY, API_SECRET, TESTNET_AKTIF, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, GITHUB_REPO_ADRESI, GITHUB_TOKEN
    global STOP_BELIRLEME_MODU, PIYASA_MODU, MARJIN_TIPI, KALDIRAC, MAKS_MARJIN_USDT, ISLEM_BASI_RISK_USDT
    global RISK_ODUL_ORANI, NIHAI_TP_RR, MIN_CONFLUENCE_SKORU, AKTIF_MTF_SABLONU, AKTIF_RISK_SEVIYESI, ae
    if not I(d, dict):
        return
    if d.get('api_key'): API_KEY = str(d['api_key']).strip()
    if d.get('api_secret'): API_SECRET = str(d['api_secret']).strip()
    if 'testnet' in d: TESTNET_AKTIF = bool(d['testnet'])
    if d.get('telegram_token'): TELEGRAM_TOKEN = str(d['telegram_token']).strip()
    if d.get('telegram_chat_id'): TELEGRAM_CHAT_ID = str(d['telegram_chat_id']).strip()
    if d.get('github_repo'): globals()['GITHUB_REPO_ADRESI'] = str(d['github_repo']).strip()
    if d.get('github_token'): globals()['GITHUB_TOKEN'] = str(d['github_token']).strip()
    if d.get('stop_modu'): STOP_BELIRLEME_MODU = str(d['stop_modu']).strip()
    if d.get('piyasa_modu'): PIYASA_MODU = str(d['piyasa_modu']).strip()
    if d.get('marjin_tipi'): MARJIN_TIPI = str(d['marjin_tipi']).strip()
    if d.get('mtf_sablon'): mtf_sablonu_uygula(str(d['mtf_sablon']), rr_koru=True)
    if d.get('risk_seviyesi'): AKTIF_RISK_SEVIYESI = str(d['risk_seviyesi'])
    if 'kaldirac' in d and F(d['kaldirac']) >= 1: KALDIRAC = M(1, N(125, int(F(d['kaldirac']))))
    if 'maks_marjin' in d and F(d['maks_marjin']) >= 5: MAKS_MARJIN_USDT = F(d['maks_marjin'])
    if 'islem_risk' in d and F(d['islem_risk']) >= 0.1: ISLEM_BASI_RISK_USDT = F(d['islem_risk'])
    if 'rr_orani' in d and F(d['rr_orani']) >= 0.5:
        RISK_ODUL_ORANI = F(d['rr_orani'])
        NIHAI_TP_RR = F(d.get('nihai_tp_rr') or M(NIHAI_TP_RR, RISK_ODUL_ORANI + 1.0))
    if 'min_skor' in d and F(d['min_skor']) >= 10: MIN_CONFLUENCE_SKORU = M(10, N(100, int(F(d['min_skor']))))
    if 'parite_limiti' in d: ae = M(0, int(F(d['parite_limiti'])))
    if 'kysy_htf_atr' in d: globals()['KYSY_HTF_ATR_CARPANI'] = M(0.6, N(4.0, F(d['kysy_htf_atr'])))
    if 'kysy_ltf_atr' in d: globals()['KYSY_LTF_ATR_CARPANI'] = M(0.5, N(3.5, F(d['kysy_ltf_atr'])))
    if 'eqh_tol_atr' in d: globals()['EQH_EQL_TOL_ATR'] = M(0.08, N(1.2, F(d['eqh_tol_atr'])))
    if 'sfp_min_atr' in d: globals()['SFP_MIN_IGNE_ATR'] = M(0.03, N(0.8, F(d['sfp_min_atr'])))
    if 'ikincil_bolge_aktif' in d: globals()['IKINCIL_BOLGE_GIRIS_AKTIF'] = bool(d['ikincil_bolge_aktif'])
    if 'birincil_olcek_carpani' in d: globals()['BIRINCIL_BOLGE_OLCEK_CARPANI'] = M(1.5, N(10.0, F(d['birincil_olcek_carpani'])))

def _api_kaydet_tam():
    try:
        mev = masaustu_ayar_sozlugu_uret()
        mev.update({
            "api_key": API_KEY, "api_secret": API_SECRET, "testnet": bool(TESTNET_AKTIF),
            "telegram_token": TELEGRAM_TOKEN, "telegram_chat_id": TELEGRAM_CHAT_ID,
            "github_repo": globals().get("GITHUB_REPO_ADRESI", "emrhozbr/bot"),
            "github_token": globals().get("GITHUB_TOKEN", "")
        })
        for d_yol in (bd, "binance_api_config.json"):
            try:
                with open(d_yol, "w", encoding="utf-8") as f:
                    json.dump(mev, f, ensure_ascii=False, indent=2)
            except X:
                pass
        if _AKTIF_PAGE_REF is not None:
            try:
                _AKTIF_PAGE_REF.client_storage.set("alfa_api_config", mev)
            except X:
                pass
    except X:
        pass

def _api_yukle():
    global _SON_PC_AYAR_TS
    dosya_adaylari = [bd, os.path.join(_ESKI_VERI_DIZINI, 'binance_api_config.json'), 'binance_api_config.json']
    yuklendi = False
    for d_yol in dosya_adaylari:
        try:
            if os.path.exists(d_yol):
                with open(d_yol, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                if I(d, dict):
                    _sozlukten_ayarlari_uygula(d)
                    _SON_PC_AYAR_TS = M(_SON_PC_AYAR_TS, F(d.get('guncelleme_ts') or 0.0))
                    yuklendi = True
                    break
        except X:
            pass
    if _AKTIF_PAGE_REF is not None:
        try:
            cs_api = _AKTIF_PAGE_REF.client_storage.get("alfa_api_config")
            if I(cs_api, dict):
                if not yuklendi or F(cs_api.get("guncelleme_ts") or 0.0) > _SON_PC_AYAR_TS:
                    _sozlukten_ayarlari_uygula(cs_api)
                    _SON_PC_AYAR_TS = M(_SON_PC_AYAR_TS, F(cs_api.get("guncelleme_ts") or 0.0))
                else:
                    if cs_api.get("github_token") and not globals().get("GITHUB_TOKEN"):
                        globals()["GITHUB_TOKEN"] = str(cs_api["github_token"]).strip()
                    if cs_api.get("github_repo"):
                        globals()["GITHUB_REPO_ADRESI"] = str(cs_api["github_repo"]).strip()
        except X:
            pass

def _ig_yukle():
    global ah
    for d_yol in (ap, os.path.join(_ESKI_VERI_DIZINI, 'islem_gecmisi.json'), 'islem_gecmisi.json'):
        try:
            if os.path.exists(d_yol):
                with open(d_yol, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                if I(d, list) and L(d) > L(ah):
                    ah = d
        except X:
            pass

def _ak_kaydet():
    global _SON_YEREL_KAYIT_TS
    try:
        _SON_YEREL_KAYIT_TS = time.time()
        nQ = {k: v for k, v in acik_islemler.items() if I(v, dict)}
        payload = {
            'guncelleme_ts': _SON_YEREL_KAYIT_TS,
            'acik_islemler': nQ,
            'demo_vadeli_bakiye': F(S),
            'gerceklesen_pnl': F(W),
            'bot_calisiyor': bool(bot_calisiyor)
        }
        for hedef_f in (aN, _aN_yedek):
            try:
                with open(hedef_f, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False)
            except X:
                pass
        if _AKTIF_PAGE_REF is not None:
            try:
                _AKTIF_PAGE_REF.client_storage.set("alfa_durum_yedek", payload)
            except X:
                pass
        if 'bulut_durum_gonder' in globals() and GITHUB_TOKEN:
            threading.Thread(target=bulut_durum_gonder, daemon=True).start()
    except X:
        pass

def _ak_yukle():
    global acik_islemler, S, W, _SON_YEREL_KAYIT_TS
    aday_dosyalar = [
        aN,
        _aN_yedek,
        os.path.join(_ESKI_VERI_DIZINI, 'acik_islemler_durum.json'),
        os.path.join(_ESKI_VERI_DIZINI, 'acik_islemler.json'),
        'acik_islemler_durum.json',
        'acik_islemler.json'
    ]
    en_iyi_veri = None
    en_yeni_ts = -1.0
    for d_yol in aday_dosyalar:
        try:
            if os.path.exists(d_yol):
                with open(d_yol, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                if I(d, dict):
                    ts_d = F(d.get('guncelleme_ts') or os.path.getmtime(d_yol) or 0.0)
                    acik_d = d.get('acik_islemler')
                    acik_say = L([k for k, v in acik_d.items() if I(v, dict)]) if I(acik_d, dict) else 0
                    skor_ts = ts_d + (1000000.0 if acik_say > 0 else 0.0)
                    if skor_ts > en_yeni_ts:
                        en_yeni_ts = skor_ts
                        en_iyi_veri = d
        except X:
            pass
    if _AKTIF_PAGE_REF is not None:
        try:
            cs_d = _AKTIF_PAGE_REF.client_storage.get("alfa_durum_yedek")
            if I(cs_d, dict):
                acik_cs = cs_d.get('acik_islemler')
                acik_say_cs = L([k for k, v in acik_cs.items() if I(v, dict)]) if I(acik_cs, dict) else 0
                skor_cs = F(cs_d.get('guncelleme_ts') or 0.0) + (1000000.0 if acik_say_cs > 0 else 0.0)
                if skor_cs > en_yeni_ts:
                    en_iyi_veri = cs_d
        except X:
            pass
    if I(en_iyi_veri, dict):
        if I(en_iyi_veri.get('acik_islemler'), dict):
            for k_i, v_i in en_iyi_veri['acik_islemler'].items():
                if I(v_i, dict):
                    acik_islemler[k_i] = v_i
        if 'demo_vadeli_bakiye' in en_iyi_veri:
            S = F(en_iyi_veri['demo_vadeli_bakiye'])
        if 'gerceklesen_pnl' in en_iyi_veri:
            W = F(en_iyi_veri['gerceklesen_pnl'])
        _SON_YEREL_KAYIT_TS = F(en_iyi_veri.get('guncelleme_ts') or time.time())
        return bool(en_iyi_veri.get('bot_calisiyor', False))
    return False

def _ig_kaydet(J,jD,bt,lH,lI,Y,fq,eE,dl,lJ=''):
    global ah
    k={'tarih':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'sembol':f"{('FUT' if jD=='future' else 'SPOT')}:{J.split(':')[0]}",'yon':bt,'giris':R(F(lH),6),'cikis':R(F(lI),6),'miktar':R(F(Y),6),'pnl_usdt':R(F(fq),2),'pnl_yuzde':R(F(eE),2),'neden':dl,'model':str(lJ)[:80]}
    ah.insert(0,k)
    try:
        with open(ap,'w',encoding='utf-8')as f:json.dump(ah[:500],f,ensure_ascii=False)
    except X:pass
    return k

_ONCEKI_BOT_AKTIF = _ak_yukle()
_api_yukle()
_ig_yukle()
borsa_kur(PIYASA_MODU,TESTNET_AKTIF)

def veri_ist(D):
    global aC, aw
    if aC is None or aw is None:
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
    return aC if D=='spot' else aw

def emir_ist(D):
    global aG, ao
    if aG is None or ao is None:
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
    return aG if D=='spot' else ao
def anahtar_yap(J,D):
 return f"{('FUT' if D=='future' else 'SPOT')}:{J.split(':')[0]}"
def tek_borsa_paritelerini_cek(D):
 a9=veri_ist(D);hk=a9.load_markets(True)
 try:o9=a9.fetch_tickers()
 except X:o9={}
 nI=[]
 for qY,m in hk.items():
  mR,mS=(m.get('base',''),m.get('quote',''))
  if not m.get('active',True)or mS!='USDT'or mR in bo or any((mR.endswith(ek)for ek in('UP','DOWN','BULL','BEAR'))):continue
  if D=='future'and(not(m.get('linear',True)and(m.get('swap',False)or m.get('future',False)))or'_'in m.get('id','')):continue
  elif D!='future'and not m.get('spot',True):continue
  iz=F(o9.get(qY,{}).get('quoteVolume')or 0.0)
  if o9 and 0<iz<bH:continue
  nI.append((qY,D,iz))
 nI.sort(key=lambda x:x[2],reverse=True);return nI[:ae]if ae>0 else nI
def pariteleri_yukle(ba=None):
 global ab,bk,au;nJ,qZ,fE=([],0,0)
 for pa,pb in[('future','Vadeli (Futures)'),('spot','Spot')]:
  if PIYASA_MODU in(pa,'her_ikisi'):
   try:
    ad=tek_borsa_paritelerini_cek(pa);nJ.extend(ad)
    if pa=='future':qZ=L(ad)
    else:fE=L(ad)
   except X as e:
    if ba:ba(f'⚠️ {pb} parite listesi çekilirken uyarı: {e}')
 if nJ:
  nJ.sort(key=lambda x:x[2],reverse=True);ab=[(s,p)for s,p,_ in nJ];bk=[s for s,_ in ab];au=L(ab)
  if ba:ba(f'🌐 Otomatik Borsa Taraması Hazır -> Vadeli: {qZ} parite | Spot: {fE} parite | Toplam: {au} aktif USDT paritesi taranacak!')
  return bk
 ab=[(s,'future')for s in am]+[(s,'spot')for s in am]if PIYASA_MODU=='her_ikisi'else[(s,'spot'if PIYASA_MODU=='spot'else'future')for s in am];bk=[s for s,_ in ab];au=L(ab);return bk
def tg_bildir(fs):
 if TELEGRAM_AKTIF and TELEGRAM_TOKEN:
  try:requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',json={'chat_id':TELEGRAM_CHAT_ID,'text':fs,'parse_mode':'HTML'},timeout=5)
  except X as e:print(f'Telegram Hatası: {e}')
def bakiye_oku(a9):
 try:
  b=a9.fetch_balance();rf,og=(F(b.get('USDT',{}).get('free',0.0)or 0.0),F(b.get('USDT',{}).get('total',0.0)or 0.0))
  if og==0.0 and'info'in b:og=F(b.get('info',{}).get('totalWalletBalance',0.0)or 0.0);rf=F(b.get('info',{}).get('availableBalance',0.0)or og)
  return(rf,og)
 except X:return(0.0,0.0)
def bakiye_getir():
 global ay,aq
 if TESTNET_AKTIF:
  r_fut=sum((F(d.get('miktar')or 0.0)*F(d.get('giris')or 0.0)/M(F(d.get('kaldirac')or KALDIRAC),1.0)for d in acik_islemler.values()if I(d,dict)and d.get('piyasa','future')=='future'))
  r_spot=sum((F(d.get('miktar')or 0.0)*F(d.get('giris')or 0.0)for d in acik_islemler.values()if I(d,dict)and d.get('piyasa')=='spot'))
  toplam_sim=M(0.0,F(S))
  serbest_sim=M(0.0,toplam_sim-r_fut-r_spot)
  ay=0.0 if PIYASA_MODU=='future'else serbest_sim*0.5
  aq=serbest_sim if PIYASA_MODU=='future'else serbest_sim*0.5
  return(serbest_sim,toplam_sim)
 simdi_b=time.time()
 if simdi_b-getattr(bakiye_getir,'_son_ts',0.0)<10.0 and(V>0 or T>0):return(V,T)
 jS,rV=bakiye_oku(aG)if PIYASA_MODU in('spot','her_ikisi')else(0.0,0.0)
 nR,pc=bakiye_oku(ao)if PIYASA_MODU in('future','her_ikisi')else(0.0,0.0)
 bakiye_getir._son_ts=simdi_b
 ay,aq=(jS,nR);return(jS+nR,rV+pc)
def veri_cek(J,bN,limit=300,D=None):
 oP=veri_ist(D if D else'spot'if PIYASA_MODU=='spot'else'future').fetch_ohlcv(J,timeframe=bN,limit=limit);df=indiktorleri_ekle(pd.DataFrame(oP,columns=['timestamp','open','high','low','close','volume']));eF=J.split(':')[0]
 if eF in('BTC/USDT','ETH/USDT','SOL/USDT'):an.setdefault(bN,{})[eF]=df
 return df
def _fmt_f(v):
 v=F(v or 0.0);av=A(v)
 return f'{v:.6f}'if 0<av<1.0 else f'{v:.4f}'if av<100.0 else f'{v:.2f}'
def _fmt_pnl(v):
 v=F(v or 0.0);av=A(v)
 return f'{v:+.4f} USDT'if 0<av<0.05 else f'{v:+.2f} USDT'
def anlik_fiyat_getir(J,D='future'):
 raw_s=str(J).split(':')[0].replace('/','').upper()
 urls=(f'https://fapi.binance.com/fapi/v1/ticker/price?symbol={raw_s}',f'https://api.binance.com/api/v3/ticker/price?symbol={raw_s}')if D=='future'else(f'https://api.binance.com/api/v3/ticker/price?symbol={raw_s}',f'https://fapi.binance.com/fapi/v1/ticker/price?symbol={raw_s}')
 for u in urls:
  try:
   r=_HTTP_SES.get(u,timeout=1.5)
   if r.status_code==200:
    p=F(r.json().get('price')or 0.0)
    if p>0:return p
  except X:pass
 cl_ist=veri_ist(D)
 for s_try in(J,J.split(':')[0],f"{J.split(':')[0]}:USDT"if D=='future'and':'not in J else J):
  try:
   tk=cl_ist.fetch_ticker(s_try)
   pz=tk.get('last')or tk.get('close')or tk.get('bid')or tk.get('ask')or tk.get('info',{}).get('lastPrice')
   if pz is not None and F(pz)>0:return F(pz)
  except X:pass
 try:
  ak_k=anahtar_yap(J,D)
  if ak_k in a1 and F(a1[ak_k].get('fiyat')or 0)>0:return F(a1[ak_k]['fiyat'])
  if ak_k in analiz_hafizasi and'df_15m_full'in analiz_hafizasi[ak_k]:return _f(analiz_hafizasi[ak_k]['df_15m_full'],'close',-1)
 except X:pass
 raise X(f'{J} anlik fiyat alinamadi')
def islem_kar_zarar_hesapla(O,bq):
 if not I(bq,dict):return(0.0,0.0,0.0,0.0,0.0,1,0.0)
 bt=str(bq.get('yon','LONG')).upper()
 b0=bq.get('piyasa','spot'if str(O).startswith('SPOT:')else'future')
 bZ=F(bq.get('giris')or 0.0)
 bM=F(bq.get('anlik')or 0.0)
 if bM<=0 and O in a1 and F(a1[O].get('fiyat')or 0.0)>0:bM=F(a1[O]['fiyat'])
 if bM<=0:bM=bZ
 k1=M(1,int(F(bq.get('kaldirac')or(KALDIRAC if b0=='future'else 1))))
 Y=F(bq.get('miktar')or 0.0)
 sl=F(bq.get('sl')or 0.0)
 if Y<=0 and bZ>0:
  Y=R((MAKS_MARJIN_USDT*k1)/bZ,6)
  bq['miktar']=Y
 fk=(Y*bZ)/M(k1,1)if bZ>0 else F(bq.get('marjin_usdt')or MAKS_MARJIN_USDT)
 k0=F(bq.get('risk_usdt')or(A(bZ-sl)*Y if sl>0 else ISLEM_BASI_RISK_USDT))
 fark=(bZ-bM)if bt=='SHORT'else(bM-bZ)
 gW=fark*Y
 nD=(fark/M(bZ,1e-09))*100.0*k1 if bZ>0 else 0.0
 bq['anlik']=bM;bq['pnl_usdt']=R(gW,6);bq['pnl_yuzde']=R(nD,3);bq['marjin_usdt']=R(fk,2)
 return(gW,nD,bZ,bM,fk,k1,k0)
import re
BOT_VERSIYONU='v4.0.9';BOT_DOSYA_ADI='botv4.0.9.py';
if 'BIRINCIL_BOLGE_OLCEK_CARPANI' not in globals(): BIRINCIL_BOLGE_OLCEK_CARPANI=5.0
if 'BIRINCIL_VIP_EK_SLOT' not in globals(): BIRINCIL_VIP_EK_SLOT=3
if 'IKINCIL_REZERV_SLOT' not in globals(): IKINCIL_REZERV_SLOT=2
if 'KYSY_HTF_ATR_CARPANI' not in globals(): KYSY_HTF_ATR_CARPANI=1.85
if 'KYSY_LTF_ATR_CARPANI' not in globals(): KYSY_LTF_ATR_CARPANI=1.30
if 'EQH_EQL_TOL_ATR' not in globals(): EQH_EQL_TOL_ATR=0.30
if 'SFP_MIN_IGNE_ATR' not in globals(): SFP_MIN_IGNE_ATR=0.12
if 'IKINCIL_BOLGE_GIRIS_AKTIF' not in globals(): IKINCIL_BOLGE_GIRIS_AKTIF=True
if 'htf_1_oncelik_radar_cache' not in globals(): htf_1_oncelik_radar_cache={}
def indiktorleri_ekle(df):
 df=df.copy();tr=pd.concat([df['high']-df['low'],(df['high']-df['close'].shift()).abs(),(df['low']-df['close'].shift()).abs()],axis=1).max(axis=1);df['atr']=tr.rolling(dj).mean().bfill();d=df['close'].diff();rs=d.where(d>0,0.0).rolling(14).mean()/(-d.where(d<0,0.0)).rolling(14).mean().replace(0,np.nan);df['rsi']=(100.0-100.0/(1.0+rs)).fillna(50.0);qH=(df['high']+df['low'])/2.0;df['ao']=(qH.rolling(5).mean()-qH.rolling(34).mean()).fillna(0.0);df['cvd']=((df['close']-df['low']-(df['high']-df['close']))/(df['high']-df['low']).replace(0,1e-09)*df['volume']).cumsum();return df
def _mum_kapanis_onayli_tepe_mi(df,i,E):
 h,l,o,c=(_f(df,'high',i),_f(df,'low',i),_f(df,'open',i),_f(df,'close',i))
 govde_ust=M(o,c);govde=A(c-o);ust_igne=h-govde_ust
 if ust_igne<=M(govde*1.8,E*1.1):return True
 w1=M(0,i-3);w2=N(L(df)-1,i+3)
 esik=govde_ust+ust_igne*0.45
 return any((_f(df,'close',j)>=esik for j in G(w1,w2+1)if j!=i))
def _mum_kapanis_onayli_dip_mi(df,i,E):
 h,l,o,c=(_f(df,'high',i),_f(df,'low',i),_f(df,'open',i),_f(df,'close',i))
 govde_alt=N(o,c);govde=A(c-o);alt_igne=govde_alt-l
 if alt_igne<=M(govde*1.8,E*1.1):return True
 w1=M(0,i-3);w2=N(L(df)-1,i+3)
 esik=govde_alt-alt_igne*0.45
 return any((_f(df,'close',j)<=esik for j in G(w1,w2+1)if j!=i))
def _df_periyot_sn_bul(df):
 """DataFrame zaman damgalarindan mum periyodunu saniye cinsinden bulur (1h = 3600sn)."""
 try:
  if df is not None and'timestamp'in df.columns and L(df)>=3:
   t1=F(_f(df,'timestamp',-1));t2=F(_f(df,'timestamp',-2));t3=F(_f(df,'timestamp',-3))
   d1=A(t1-t2);d2=A(t2-t3)
   ms=N(d1,d2)if(d1>0 and d2>0)else M(d1,d2)
   if ms>10000:return ms/1000.0
   if ms>0:return ms
 except X:pass
 return 14400.0
def _df_1h_ve_alti_mi(df,n=SWING_PENCERE):
 """1h ve alti (1h, 30m, 15m, 5m, 3m, 1m -> <= 3600sn) ise True, 1h ustu HTF (2h, 4h, 1d, 1M) ise False doner."""
 if n<=3:return True
 return _df_periyot_sn_bul(df)<=3660.0
def _net_sert_tepe_mi(df,i,E,n=SWING_PENCERE):
 if not _mum_kapanis_onayli_tepe_mi(df,i,E):return False
 if n<=1:return True
 hassas_1h_alti=_df_1h_ve_alti_mi(df,n)
 ct=L(df);h=_f(df,'high',i);l_0=_f(df,'low',i);l_arr=df.__dict__['_np_c']['low']
 w=3 if hassas_1h_alti else M(3,n+1)
 b1=M(0,i-w);b2=N(ct-1,i+w)
 min_sol=F(l_arr[b1:i+1].min())if i>b1 else l_0
 min_sag=F(l_arr[i:b2+1].min())if b2>i else l_0
 esik=E*(0.82 if hassas_1h_alti else(1.55 if n>=4 else 1.1))
 sag_esik=esik*0.5 if i>=ct-3 else esik
 return(h-min_sol)>=esik and(h-min_sag)>=sag_esik
def _net_sert_dip_mi(df,i,E,n=SWING_PENCERE):
 if not _mum_kapanis_onayli_dip_mi(df,i,E):return False
 if n<=1:return True
 hassas_1h_alti=_df_1h_ve_alti_mi(df,n)
 ct=L(df);l=_f(df,'low',i);h_0=_f(df,'high',i);h_arr=df.__dict__['_np_c']['high']
 w=3 if hassas_1h_alti else M(3,n+1)
 b1=M(0,i-w);b2=N(ct-1,i+w)
 max_sol=F(h_arr[b1:i+1].max())if i>b1 else h_0
 max_sag=F(h_arr[i:b2+1].max())if b2>i else h_0
 esik=E*(0.82 if hassas_1h_alti else(1.55 if n>=4 else 1.1))
 sag_esik=esik*0.5 if i>=ct-3 else esik
 return(max_sol-l)>=esik and(max_sag-l)>=sag_esik
def ham_swing_noktalarini_bul(df,n=SWING_PENCERE,cn=False):
 aa,ar=([],[])
 hassas_1h_alti=_df_1h_ve_alti_mi(df,n)
 n_eff=2 if hassas_1h_alti else(3 if n>=4 else M(1,n))
 if L(df)<2*n_eff+2:return(aa,ar)
 E=M(_f(df,'atr',-2)if'atr'in df.columns else _f(df,'close',-2)*0.002,_f(df,'close',-2)*0.001)
 _f(df,'high',0);_f(df,'low',0)
 h_np=df.__dict__['_np_c']['high'];l_np=df.__dict__['_np_c']['low']
 for i in G(n_eff,L(df)-n_eff):
  if h_np[i]==h_np[i-n_eff:i+n_eff+1].max()and(not cn or(l_np[i]>=l_np[i-1]and l_np[i]>=l_np[i+1])):
   if _net_sert_tepe_mi(df,i,E,n):aa.append((i,F(h_np[i])))
  if l_np[i]==l_np[i-n_eff:i+n_eff+1].min()and(not cn or(h_np[i]<=h_np[i-1]and h_np[i]<=h_np[i+1])):
   if _net_sert_dip_mi(df,i,E,n):ar.append((i,F(l_np[i])))
 if n>=2 and(L(aa)<2 or L(ar)<2):
  aa,ar=([],[])
  for i in G(n_eff,L(df)-n_eff):
   if h_np[i]==h_np[i-n_eff:i+n_eff+1].max()and _mum_kapanis_onayli_tepe_mi(df,i,E):aa.append((i,F(h_np[i])))
   if l_np[i]==l_np[i-n_eff:i+n_eff+1].min()and _mum_kapanis_onayli_dip_mi(df,i,E):ar.append((i,F(l_np[i])))
 return(aa,ar)
def _aralikta_gecerli_tepe_bul(df,bas,bit,E):
 Bas=M(0,int(bas));Bit=N(L(df)-1,int(bit))
 if Bit<Bas:return(Bas,_f(df,'high',Bas))
 en_i,en_v=(None,-1e18)
 for j in G(Bas,Bit+1):
  hj=_f(df,'high',j)
  if _mum_kapanis_onayli_tepe_mi(df,j,E)and hj>en_v:en_i,en_v=(j,hj)
 if en_i is None:
  for j in G(Bas,Bit+1):
   bj=M(_f(df,'open',j),_f(df,'close',j))
   if bj>en_v:en_i,en_v=(j,_f(df,'high',j))
 return(en_i if en_i is not None else Bas,en_v if en_i is not None else _f(df,'high',Bas))
def _aralikta_gecerli_dip_bul(df,bas,bit,E):
 Bas=M(0,int(bas));Bit=N(L(df)-1,int(bit))
 if Bit<Bas:return(Bas,_f(df,'low',Bas))
 en_i,en_v=(None,1e18)
 for j in G(Bas,Bit+1):
  lj=_f(df,'low',j)
  if _mum_kapanis_onayli_dip_mi(df,j,E)and lj<en_v:en_i,en_v=(j,lj)
 if en_i is None:
  for j in G(Bas,Bit+1):
   bj=N(_f(df,'open',j),_f(df,'close',j))
   if bj<en_v:en_i,en_v=(j,_f(df,'low',j))
 return(en_i if en_i is not None else Bas,en_v if en_i is not None else _f(df,'low',Bas))
def _sert_salinim_onayli_mi(df,bas_i,bas_v,bit_i,bit_v,E,n=2,ana_bacak=0.0):
 genlik=A(F(bit_v)-F(bas_v));bar_fark=M(1,A(int(bit_i)-int(bit_i if bas_i is None else bas_i)))
 hassas_1h_alti=_df_1h_ve_alti_mi(df,n)
 tf_sn=_df_periyot_sn_bul(df)
 if hassas_1h_alti:
  min_genlik=E*(N(1.05,KYSY_LTF_ATR_CARPANI*0.82)if tf_sn>=1800 else N(0.88,KYSY_LTF_ATR_CARPANI*0.72))
 else:
  min_genlik=E*(KYSY_HTF_ATR_CARPANI if n>=4 else KYSY_LTF_ATR_CARPANI)
 if genlik<min_genlik:return False
 if not hassas_1h_alti and ana_bacak>E*3.2 and genlik<N(ana_bacak*0.18,E*2.6):return False
 if hassas_1h_alti and ana_bacak>E*4.0 and genlik<N(ana_bacak*0.12,E*1.6):return False
 min_b=2 if hassas_1h_alti else(3 if n>=4 else 2)
 if bar_fark<min_b and genlik<min_genlik*(1.35 if hassas_1h_alti else 1.75):return False
 B1,B2=M(0,N(int(bas_i),int(bit_i))),N(L(df)-1,M(int(bas_i),int(bit_i)))
 dusus_mu=F(bit_v)<F(bas_v)
 zit_say=sum((1 for j in G(B1+1,B2+1)if(_f(df,'close',j)<_f(df,'open',j)if dusus_mu else _f(df,'close',j)>_f(df,'open',j))))
 max_mum=M((A(_f(df,'close',j)-_f(df,'open',j))for j in G(B1,B2+1)),default=0.0)
 if not hassas_1h_alti and n>=4 and zit_say<2 and genlik<min_genlik*1.55:return False
 return max_mum>=E*(0.30 if hassas_1h_alti else 0.42)or genlik>=min_genlik*(1.12 if hassas_1h_alti else 1.3)
def _qml_yapisi_bul(uH,uL,yon=None,df=None):
 # QML olması için onaylı ZigZag üzerinde en az 3 salınım (4 onaylı nokta: p0 -> p1 -> p2 -> p3 ve p0 gerçek swing) şarttır!
 zz=sorted([(int(i),F(v),'H')for i,v in uH]+[(int(i),F(v),'L')for i,v in uL],key=lambda x:x[0])
 temiz=[]
 for item in zz:
  if not temiz or temiz[-1][2]!=item[2]:temiz.append(item)
  else:
   if item[2]=='H'and item[1]>=temiz[-1][1]:temiz[-1]=item
   elif item[2]=='L'and item[1]<=temiz[-1][1]:temiz[-1]=item
 if L(temiz)<4:return None
 bull_qml,bear_qml=(None,None)
 bull_any,bear_any=(None,None)
 for m in G(L(temiz)-1,2,-1):
  p0,p1,p2,p3=(temiz[m-3],temiz[m-2],temiz[m-1],temiz[m])
  if p0[0]<=0 and m==3:continue
  # Bullish QML Şablonu (En az 3 salınım): Sol Dip (L1: p0) -> Tepe (H1/CHoCH: p1) -> Daha Düşük Dip / Baş (LL: p2 < p0) -> CHoCH Kırılımı (HH: p3 > p1) => QML = p0 (L1)
  if p0[2]=='L'and p1[2]=='H'and p2[2]=='L'and p3[2]=='H':
   if p2[1]<p0[1]and p3[1]>p1[1]and p1[1]>p0[1]:
    cand=(int(p0[0]),R(F(p0[1]),6),int(p2[0]),R(F(p2[1]),6),int(p1[0]),R(F(p1[1]),6),int(p3[0]),R(F(p3[1]),6))
    if bull_any is None:bull_any=cand
    sonraki_daha_dusuk=any((x[1]<p2[1]for x in temiz[m+1:]if x[2]=='L'))
    if bull_qml is None and not sonraki_daha_dusuk and(df is None or F(df['low'].iloc[p3[0]:].min())>=p2[1]):
     bull_qml=cand
  # Bearish QML Şablonu (En az 3 salınım): Sol Tepe (H1: p0) -> Dip (L1/CHoCH: p1) -> Daha Yüksek Tepe / Baş (HH: p2 > p0) -> CHoCH Kırılımı (LL: p3 < p1) => QML = p0 (H1)
  if p0[2]=='H'and p1[2]=='L'and p2[2]=='H'and p3[2]=='L':
   if p2[1]>p0[1]and p3[1]<p1[1]and p0[1]>p1[1]:
    cand=(int(p0[0]),R(F(p0[1]),6),int(p2[0]),R(F(p2[1]),6),int(p1[0]),R(F(p1[1]),6),int(p3[0]),R(F(p3[1]),6))
    if bear_any is None:bear_any=cand
    sonraki_daha_yuksek=any((x[1]>p2[1]for x in temiz[m+1:]if x[2]=='H'))
    if bear_qml is None and not sonraki_daha_yuksek and(df is None or F(df['high'].iloc[p3[0]:].max())<=p2[1]):
     bear_qml=cand
 b_sec=bull_qml or bull_any
 br_sec=bear_qml or bear_any
 if yon=='BULLISH':return b_sec or br_sec
 if yon=='BEARISH':return br_sec or b_sec
 if bull_qml and bear_qml:return bull_qml if bull_qml[6]>=bear_qml[6]else bear_qml
 if bull_qml or bear_qml:return bull_qml or bear_qml
 if b_sec and br_sec:return b_sec if b_sec[6]>=br_sec[6]else br_sec
 return b_sec or br_sec
def _kysy_ltf_swing_analizi(df,n=2,cn=False):
 rH,rL=ham_swing_noktalarini_bul(df,n,cn);mt={'kysy_onay':False,'bos_list':[],'elenen_highs':[],'elenen_lows':[],'elenen_sayi':0,'son_kirilim_tipi':'YOK','son_kirilim_yon':'NOTR','son_kirilim_seviye':None,'son_kirilim_idx':None,'aktif_aralik_kirildi':False,'qml_seviyesi':None,'qml_idx':None,'bull_qml_meta':None,'bear_qml_meta':None}
 if L(df)<8 or L(rH)<1 or L(rL)<1:return([],[],mt)
 E=M(_f(df,'atr',-2)if'atr'in df.columns else _f(df,'close',-2)*0.002,_f(df,'close',-2)*0.001)
 hassas_1h_alti=_df_1h_ve_alti_mi(df,n)
 tf_sn=_df_periyot_sn_bul(df)
 n_piv=2 if hassas_1h_alti else(3 if n>=4 else M(1,n))
 min_pb=E*((N(1.05,KYSY_LTF_ATR_CARPANI*0.82)if tf_sn>=1800 else N(0.88,KYSY_LTF_ATR_CARPANI*0.72))if hassas_1h_alti else(KYSY_HTF_ATR_CARPANI if n>=4 else KYSY_LTF_ATR_CARPANI))
 min_bar=2 if hassas_1h_alti else(3 if n>=4 else 2)
 if rH[0][0]>=min_bar:
  i0_l,v0_l=_aralikta_gecerli_dip_bul(df,0,rH[0][0]-1,E)
  if(rH[0][1]-v0_l)>=min_pb*0.85 and(not rL or i0_l<rL[0][0]):rL.insert(0,(i0_l,v0_l))
 if rL[0][0]>=min_bar:
  i0_h,v0_h=_aralikta_gecerli_tepe_bul(df,0,rL[0][0]-1,E)
  if(v0_h-rL[0][1])>=min_pb*0.85 and(not rH or i0_h<rH[0][0]):rH.insert(0,(i0_h,v0_h))
 rH_map={i:v for i,v in rH};rL_map={i:v for i,v in rL}
 hi,hv=rH[0];li,lv=rL[0];tr=0;oH,oL,bL=([],[],[]);sI=M(1,N(hi,li)+1);kilit_h,kilit_l=(False,False)
 for k in G(sI,L(df)):
  cl,ch,clw=(_f(df,'close',k),_f(df,'high',k),_f(df,'low',k))
  tepe_onay=_mum_kapanis_onayli_tepe_mi(df,k,E)
  dip_onay=_mum_kapanis_onayli_dip_mi(df,k,E)
  aktif_leg=A(hv-lv)
  if tr==0:
   if k>hi+min_bar and cl>hv+E*0.12 and tepe_onay:
    mI,mV=_aralikta_gecerli_dip_bul(df,hi+1,k-1,E)
    if(hv-mV)>=min_pb*0.85 and(mI-hi)>=min_bar:
     bI,bV=_aralikta_gecerli_dip_bul(df,0,M(0,hi-1),E)if hi>=min_bar else(mI,mV)
     yv=ch if tepe_onay else cl
     if hi>=min_bar and bI<hi and(hv-bV)>=min_pb*0.85:
      if mV>=bV-E*0.2:
       oL=[(bI,bV),(mI,mV)];oH=[(hi,hv),(k,yv)]
       bL.append((k,hv,mI,mV,'BULLISH','BULL_BOS'))
      else:
       tI,tV=_aralikta_gecerli_tepe_bul(df,0,M(0,bI-1),E)if bI>=min_bar else(hi,hv)
       if bI>=min_bar and tI<bI and(tV-bV)>=min_pb*0.85 and tV>hv:
        oH=[(tI,tV),(hi,hv),(k,yv)];oL=[(bI,bV),(mI,mV)]
        bL.append((k,hv,mI,mV,'BULLISH','BULL_MSB_CHOCH'))
       else:
        oH=[(hi,hv),(k,yv)];oL=[(mI,mV)]
     else:
      oH=[(hi,hv),(k,yv)];oL=[(mI,mV)]
     li,lv=(mI,mV);hi,hv=(k,yv);tr=1;kilit_h=False
    elif ch>hv:
     hi,hv=(k,ch)
   elif k>li+min_bar and cl<lv-E*0.12 and dip_onay:
    xI,xV=_aralikta_gecerli_tepe_bul(df,li+1,k-1,E)
    if(xV-lv)>=min_pb*0.85 and(xI-li)>=min_bar:
     tI,tV=_aralikta_gecerli_tepe_bul(df,0,M(0,li-1),E)if li>=min_bar else(xI,xV)
     yv=clw if dip_onay else cl
     if li>=min_bar and tI<li and(tV-lv)>=min_pb*0.85:
      if xV<=tV+E*0.2:
       oH=[(tI,tV),(xI,xV)];oL=[(li,lv),(k,yv)]
       bL.append((k,lv,xI,xV,'BEARISH','BEAR_BOS'))
      else:
       bI,bV=_aralikta_gecerli_dip_bul(df,0,M(0,tI-1),E)if tI>=min_bar else(li,lv)
       if tI>=min_bar and bI<tI and(tV-bV)>=min_pb*0.85 and bV<lv:
        oL=[(bI,bV),(li,lv),(k,yv)];oH=[(tI,tV),(xI,xV)]
        bL.append((k,lv,xI,xV,'BEARISH','BEAR_MSB_CHOCH'))
       else:
        oL=[(li,lv),(k,yv)];oH=[(xI,xV)]
     else:
      oL=[(li,lv),(k,yv)];oH=[(xI,xV)]
     hi,hv=(xI,xV);li,lv=(k,yv);tr=-1;kilit_l=False
    elif clw<lv:
     li,lv=(k,clw)
   else:
    if k in rH_map and ch>hv and k<=li+n_piv*4:hi,hv=(k,ch)
    if k in rL_map and clw<lv and k<=hi+n_piv*4:li,lv=(k,clw)
  elif tr==1:
   if not kilit_h:
    if ch>=hv:
     hi,hv=(k,ch)
     if oH:oH[-1]=(hi,hv)
    elif(k-n_piv in rL_map and k-n_piv>=hi+min_bar and _sert_salinim_onayli_mi(df,hi,hv,k-n_piv,_f(df,'low',k-n_piv),E,n,aktif_leg))or(k>=hi+min_bar and _sert_salinim_onayli_mi(df,hi,hv,k,clw,E,n,aktif_leg)):
     kilit_h=True
   if kilit_h and k>hi+min_bar and cl>hv+E*0.10 and tepe_onay:
    mI,mV=_aralikta_gecerli_dip_bul(df,hi+1,k-1,E)
    if _sert_salinim_onayli_mi(df,hi,hv,mI,mV,E,n,aktif_leg)and(ch-mV)>=min_pb and(mI-hi)>=min_bar and(k-mI)>=2:
     if not oL or oL[-1][0]!=mI:oL.append((mI,mV))
     li,lv=(mI,mV);yv=ch if tepe_onay else cl
     bL.append((k,hv,li,lv,'BULLISH','BULL_BOS'));hi,hv=(k,yv);oH.append((hi,hv));kilit_h=False
    elif ch>=hv:
     hi,hv=(k,ch)
     if oH:oH[-1]=(hi,hv)
     kilit_h=False
   elif kilit_h and ch>hv and not(cl>hv+E*0.10 and tepe_onay):
    mI,mV=_aralikta_gecerli_dip_bul(df,hi+1,k-1,E)
    if not(_sert_salinim_onayli_mi(df,hi,hv,mI,mV,E,n,aktif_leg)and(mI-hi)>=min_bar):
     hi,hv=(k,ch)
     if oH:oH[-1]=(hi,hv)
     kilit_h=False
   elif k>li+min_bar and cl<lv-E*0.12 and dip_onay:
    xI,xV=_aralikta_gecerli_tepe_bul(df,li+1,k-1,E)if k-1>=li+1 else(hi,hv)
    if _sert_salinim_onayli_mi(df,xI,xV,k,clw,E,n):
     if not kilit_h and oH:
      hi,hv=(xI,xV);oH[-1]=(hi,hv)
     yv=clw if dip_onay else cl
     choch_ok=bool(L(oH)>=2 and L(oL)>=2 and(oH[-1][1]>oH[-2][1]or oL[-1][1]>oL[-2][1]))
     bL.append((k,lv,hi,hv,'BEARISH','BEAR_MSB_CHOCH'if choch_ok else'BEAR_BOS'));li,lv=(k,yv);oL.append((li,lv));tr=-1;kilit_l=False
  elif tr==-1:
   if not kilit_l:
    if clw<=lv:
     li,lv=(k,clw)
     if oL:oL[-1]=(li,lv)
    elif(k-n_piv in rH_map and k-n_piv>=li+min_bar and _sert_salinim_onayli_mi(df,li,lv,k-n_piv,_f(df,'high',k-n_piv),E,n,aktif_leg))or(k>=li+min_bar and _sert_salinim_onayli_mi(df,li,lv,k,ch,E,n,aktif_leg)):
     kilit_l=True
   if kilit_l and k>li+min_bar and cl<lv-E*0.10 and dip_onay:
    xI,xV=_aralikta_gecerli_tepe_bul(df,li+1,k-1,E)
    if _sert_salinim_onayli_mi(df,li,lv,xI,xV,E,n,aktif_leg)and(xV-clw)>=min_pb and(xI-li)>=min_bar and(k-xI)>=2:
     if not oH or oH[-1][0]!=xI:oH.append((xI,xV))
     hi,hv=(xI,xV);yv=clw if dip_onay else cl
     bL.append((k,lv,hi,hv,'BEARISH','BEAR_BOS'));li,lv=(k,yv);oL.append((li,lv));kilit_l=False
    elif clw<=lv:
     li,lv=(k,clw)
     if oL:oL[-1]=(li,lv)
     kilit_l=False
   elif kilit_l and clw<lv and not(cl<lv-E*0.10 and dip_onay):
    xI,xV=_aralikta_gecerli_tepe_bul(df,li+1,k-1,E)
    if not(_sert_salinim_onayli_mi(df,li,lv,xI,xV,E,n,aktif_leg)and(xI-li)>=min_bar):
     li,lv=(k,clw)
     if oL:oL[-1]=(li,lv)
     kilit_l=False
   elif k>hi+min_bar and cl>hv+E*0.12 and tepe_onay:
    mI,mV=_aralikta_gecerli_dip_bul(df,hi+1,k-1,E)if k-1>=hi+1 else(li,lv)
    if _sert_salinim_onayli_mi(df,mI,mV,k,ch,E,n):
     if not kilit_l and oL:
      li,lv=(mI,mV);oL[-1]=(li,lv)
     yv=ch if tepe_onay else cl
     choch_ok=bool(L(oH)>=2 and L(oL)>=2 and(oL[-1][1]<oL[-2][1]or oH[-1][1]<oH[-2][1]))
     bL.append((k,hv,li,lv,'BULLISH','BULL_MSB_CHOCH'if choch_ok else'BULL_BOS'));hi,hv=(k,yv);oH.append((hi,hv));tr=1;kilit_h=False
 uH,uL=([],[])
 for idx,val in oH:
  if not uH or uH[-1][0]!=idx:uH.append((int(idx),F(val)))
 for idx,val in oL:
  if not uL or uL[-1][0]!=idx:uL.append((int(idx),F(val)))
 hS={x[0]for x in uH};lS={x[0]for x in uL};eH=[(i,v)for i,v in rH if all(A(i-x)>1 for x in hS)];eL=[(i,v)for i,v in rL if all(A(i-x)>1 for x in lS)]
 mt['bos_list']=bL;mt['elenen_highs']=eH;mt['elenen_lows']=eL;mt['elenen_sayi']=L(eH)+L(eL)
 bull_qm=_qml_yapisi_bul(uH,uL,'BULLISH',df);bear_qm=_qml_yapisi_bul(uH,uL,'BEARISH',df)
 mt['bull_qml_meta']=bull_qm;mt['bear_qml_meta']=bear_qm
 if bL:
  lb=bL[-1];mt['kysy_onay']=True;mt['son_kirilim_idx']=lb[0];mt['son_kirilim_seviye']=R(lb[1],6);mt['son_kirilim_yon']=lb[4];mt['son_kirilim_tipi']=lb[5];mt['aktif_aralik_kirildi']=(L(df)-2-lb[0])<=50
  aktif_qm=_qml_yapisi_bul(uH,uL,None,df)or(bull_qm if lb[4]=='BULLISH'else bear_qm)or bull_qm or bear_qm
  if aktif_qm is not None:
   mt['qml_idx']=int(aktif_qm[0]);mt['qml_seviyesi']=R(F(aktif_qm[1]),6)
 return(uH,uL,mt)
def kirilim_yoksa_swing_yoktur_analizi(df,n=SWING_PENCERE,cn=False):
 # Tüm zaman dilimlerinde grafiğin tamamındaki tüm onaylı swing noktalarını belirle
 return _kysy_ltf_swing_analizi(df,n,cn)
def swing_noktalarini_bul(df,n=SWING_PENCERE,cn=False,kirilim_sarti=True):
 if n<=1 or not kirilim_sarti:return ham_swing_noktalarini_bul(df,n,cn)
 uH,uL,_=kirilim_yoksa_swing_yoktur_analizi(df,n,cn);return(uH,uL)
def wyckoff_analizi(df,aa,ar):
 a5={'wyckoff_fazi':'TREND_IMPULSIVE','konsolidasyon_mu':False,'egimli_flama_mi':False,'spring_manipulasyon':False,'utad_manipulasyon':False,'aciklama':''}
 if L(df)<35 or L(aa)<2 or L(ar)<2:return a5
 ak=_f(df,'close',-2);E=M(_f(df,'atr',-2),ak*0.001);qI=(_f(df,'close',-14)-_f(df,'close',-34))/M(_f(df,'close',-34),1e-09);lK=df.iloc[-14:-3];iA,hp=(F(lK['high'].max()),F(lK['low'].min()))
 if L(aa)>=3 and L(ar)>=3:
  he,le=(aa[-1][1]-aa[-3][1],ar[-1][1]-ar[-3][1])
  if he*le>0 and A(he)<=E*4.5 and A(le)<=E*4.5:a5['egimli_flama_mi']=True
 ft=F(df['low'].iloc[-4:-1].min())<hp and ak>hp;fu=F(df['high'].iloc[-4:-1].max())>iA and ak<iA;a5['spring_manipulasyon'],a5['utad_manipulasyon']=(ft,fu)
 if iA-hp<=E*4.2 or a5['egimli_flama_mi']:
  a5['konsolidasyon_mu']=True
  if qI<=-0.015:a5['wyckoff_fazi']='ACCUMULATION_SPRING'if ft else'RE_DISTRIBUTION'if fu else'ACCUMULATION_RANGE';a5['aciklama']='Wyckoff Accumulation + Spring/PO3 Süpürmesi (YT-Part1&2)'if ft else'Wyckoff Re-Distribution (Üst Likidite Operasyonu) (YT-Part1&2)'if fu else'Wyckoff Accumulation Talep Alanı (YT-Part1&2)'
  elif qI>=0.015:a5['wyckoff_fazi']='DISTRIBUTION_UTAD'if fu else'RE_ACCUMULATION'if ft else'DISTRIBUTION_RANGE';a5['aciklama']='Wyckoff Distribution + UTAD/PO3 Süpürmesi (YT-Part1&2)'if fu else'Wyckoff Re-Accumulation (Alt Likidite Yakıt Operasyonu) (YT-Part1&2)'if ft else'Wyckoff Konsolidasyon Alanı (YT-Part1&2)'
  else:a5['wyckoff_fazi'],a5['aciklama']=('CONSOLIDATION_RANGE','Alıcı-Satıcı Dengesi / Range Konsolidasyonu (YT-Part1&2)')
 return a5
def ext_int_swing_ayristir(df,aa,ar):
 cS={'external_yon':'NOTR','strong_point':None,'strong_idx':None,'weak_point':None,'weak_idx':None,'break_line_fl':None,'break_line_idx':None,'internal_yon':'NOTR','internal_choch':'YOK','external_msb':False,'kuru_kafa_trendline_tuzagi':False,'uc_istasyon':{}}
 if L(aa)<1 or L(ar)<1:return cS
 aa_p=([aa[0]]*(3-L(aa))+list(aa))if L(aa)<3 else list(aa)
 ar_p=([ar[0]]*(3-L(ar))+list(ar))if L(ar)<3 else list(ar)
 cl,bb,bc=(_f(df,'close',-2),_f(df,'low',-2),_f(df,'high',-2));E=M(_f(df,'atr',-2),cl*0.001);(hS,H0),(gd,H1),(hf,H2)=(aa_p[-3],aa_p[-2],aa_p[-1]);(hT,L0),(ge,L1),(hg,L2)=(ar_p[-3],ar_p[-2],ar_p[-1])
 # Tüm grafikteki belirlenen salınımlara göre her zaman dilimi için piyasa yönü ve Strong/Weak Point hesabı
 hq=(hf>hg and H2>=H1)or(H2>H1 and cl>=L2)
 cS['external_yon']='BULLISH'if hq else'BEARISH'
 if hq:
  gf,hh=(hg,L2)
  w_i,w_v=(hf,H2)
  fl_i,fl_v=(gd,H1)
  cS['external_msb']=bool(L2<L1 and H2>H1)
 else:
  gf,hh=(hf,H2)
  w_i,w_v=(hg,L2)
  fl_i,fl_v=(ge,L1)
  cS['external_msb']=bool(H2>H1 and L2<L1)
 cS['strong_point'],cS['strong_idx']=(F(hh),int(gf))
 cS['weak_point'],cS['weak_idx']=(F(w_v),int(w_i))
 cS['break_line_fl'],cS['break_line_idx']=(F(fl_v),int(fl_i))
 be,hV=(cS['break_line_fl'],cS['weak_point'])
 bF=(be-(be-hh)*0.25 if be>hh else be-E*0.35)if hq else(be+(hh-be)*0.25 if hh>be else be+E*0.35)
 lX=(be+(hV-be)*0.25 if hV>be else be+E*0.4)if hq else(be-(be-hV)*0.25 if be>hV else be-E*0.4)
 cS['uc_istasyon']={'ITZ':R(bF,6),'FL':R(be,6),'FO':R(lX,6),'FTR':R(lX,6),'VALID_ORIGIN':R(hh,6)}
 if(cl<hh)if hq else(cl>hh):cS['external_yon'],cS['external_msb']=('BEARISH'if hq else'BULLISH',True)
 d0,d4=_kysy_ltf_swing_analizi(df,2)[:2]
 if L(d0)>=2 and L(d4)>=2:
  pN,oh,pO,oi=(d0[-2][1],d0[-1][1],d4[-2][1],d4[-1][1])
  if cl>oh:cS['internal_yon'],cS['internal_choch']=('BULLISH','BULL_STRONG_CHOCH'if oi<pO else'BULL_IBOS'if oh>pN and oi>pO else'BULL_WEAK_CHOCH')
  elif cl<oi:cS['internal_yon'],cS['internal_choch']=('BEARISH','BEAR_STRONG_CHOCH'if oh>pN else'BEAR_IBOS'if oi<pO and oh<pN else'BEAR_WEAK_CHOCH')
 return cS
def rbr_dbd_analizi(df,bu,aH,aJ,B='BULLISH'):
 g=B=='BULLISH';a5={'kalip_adi':'DBR'if g else'RBD','hidden_base_dp':False,'v_shape_1mum':False,'patlama_ayrilis':False,'imbalance_koku':aJ if g else aH,'yaklasim_ipuclari':[],'yaklasim_ek_puan':0.0}
 if bu<4 or bu>=L(df)-3:return a5
 E=M(_f(df,'atr',-2),_f(df,'close',-2)*0.001);qJ=_f(df,'close',bu-1)-_f(df,'open',M(0,bu-4));a5['kalip_adi']=('RBR_FTR'if qJ>E*0.5 else'DBR')if g else('DBD_FTR'if qJ<-E*0.5 else'RBD');jT,hr=(df.iloc[bu],df.iloc[N(L(df)-2,bu+1)]);o1,c1,h1,l1=_r(jT,'open','close','high','low');o2,c2,h2,l2=_r(hr,'open','close','high','low');a5['imbalance_koku']=(o2 if c2>o2 else aJ)if g else(o2 if c2<o2 else aH)
 if(c1>o1 and c2>o2 and h1-c1>E*0.15 and o2-l2>E*0.15)if g else(c1<o1 and c2<o2 and c1-l1>E*0.15 and h2-o2>E*0.15):a5['hidden_base_dp']=True
 if A(c2-o2)>=E*1.15 or A(o2-c1)>E*0.12:a5['patlama_ayrilis']=True
 jE=sum((1 for k in G(bu,N(L(df)-2,bu+5))if aH-E*0.1<=_f(df,'close',k)<=aJ+E*0.1));a5['v_shape_1mum']=jE<=1;qK=L(df)-2-(bu+M(jE,1))
 if jE<=2 and qK>=8:a5['yaklasim_ipuclari'].append(f'YavasDonus(2m->{qK}m)');a5['yaklasim_ek_puan']+=1.0
 if L(df)>=8:
  q0=F((df['close'].iloc[-8:-5]-df['open'].iloc[-8:-5]).abs().mean());lY=F((df['close'].iloc[-5:-2]-df['open'].iloc[-5:-2]).abs().mean())
  if q0>0 and lY<=q0*0.72:a5['yaklasim_ipuclari'].append('GovdeKuculmesi/Doji');a5['yaklasim_ek_puan']+=1.0
  yd=df.iloc[-5:-2];lZ=(yd['high']-yd[['open','close']].max(axis=1)).mean();l4=(yd[['open','close']].min(axis=1)-yd['low']).mean()
  if(lZ>l4*1.25)if g else(l4>lZ*1.25):a5['yaklasim_ipuclari'].append('TersUstIgneUzamasi'if g else'TersAltIgneUzamasi');a5['yaklasim_ek_puan']+=1.0
  mp,mc=(df.iloc[-3],df.iloc[-2]);pg=A(F(mp['close'])-F(mp['open']))
  if(F(mp['close'])<F(mp['open'])and pg>E*0.65 and F(mc['close'])>F(mc['open']))if g else(F(mp['close'])>F(mp['open'])and pg>E*0.65 and F(mc['close'])<F(mc['open'])):a5['yaklasim_ipuclari'].append('BankerManipulasyonMumu');a5['yaklasim_ek_puan']+=1.0
 return a5
def ftr_fo_itz_taramasi(df,z,C,a='1H',B='BULLISH'):
 l5,K,az,bz,pe=([],[],[],None,False)
 if L(df)<15:return(l5,bz,K,az,pe)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);qL=z.get('uc_istasyon',{});a6=z.get('strong_point');g=B=='BULLISH';aX='Bullish'if g else'Bearish'
 for i in G(M(3,L(df)-28),L(df)-4):
  oj,iV,ok=(df.iloc[i-1],df.iloc[i],df.iloc[i+1]);iB=F(oj['close'])-F(oj['open']);fF=A(F(iV['close'])-F(iV['open']));fG=F(ok['close'])-F(ok['open']);nS=df['close'].iloc[i+2:-2];jU=(iB>E*0.5 and fF<=E*0.55 and fG>E*0.55 and F(ok['close'])>F(oj['high']))if g else(iB<-E*0.5 and fF<=E*0.55 and fG<-E*0.55 and F(ok['close'])<F(oj['low']))
  if jU:
   jc,jd=(F(iV['low']),M(F(iV['open']),F(iV['close'])))if g else(N(F(iV['open']),F(iV['close'])),F(iV['high']));r5=(not nS.empty and F(nS.min())<jc-E*0.1)if g else(not nS.empty and F(nS.max())>jd+E*0.1)
   if not r5 and((jc-E*0.2<=bb<=jd+E*0.15 and ak>=jc)if g else(jc-E*0.15<=bc<=jd+E*0.2 and ak<=jd)):l5.append(f"{a}_{('1Mum_FTR' if g else 'Bear_1Mum_FTR')}");K.append(f"[{a}] {aX} 1 Mumluk {('RBR' if g else 'DBD')} Trend Devam FTR Testi ({jc:.4f}-{jd:.4f}) (08.pdf & YT-Part3)");az.append(('BB/FL',i,jc,jd));bz=(jc if bz is None else N(bz,jc))if g else(jd if bz is None else M(bz,jd));break
 d5,g7=(qL.get('FO'),qL.get('ITZ'));de=bb if g else bc
 if d5 and A(de-d5)<=E*0.35 and(ak>=d5 if g else ak<=d5):l5.append(f"{a}_{('FirstObstacle_FO' if g else 'Bear_FirstObstacle_FO')}");K.append(f'[{a}] {aX} First Obstacle (FO - Kırılım Sonrası İlk Engel: {d5:.4f}) Testi (YT-Part3)');fH=d5-E*0.45 if g else d5+E*0.45;bz=fH if bz is None else N(bz,fH)if g else M(bz,fH)
 if g7 and A(de-g7)<=E*0.38 and(ak>=g7 if g else ak<=g7):
  l5.append(f"{a}_{('ITZ' if g else 'Bear_ITZ')}")
  if a6 and L(C)>0 and(g7-a6>E*0.8 if g else a6-g7>E*0.8):pe=True;bz=a6;K.append(f"[{a}] {aX} ITZ ({g7:.4f}) Testi + UYARI: ITZ ile Origin OB ({a6:.4f}) arasında açık Imbalance var; stop Origin OB'ye çekildi! (YT-Part3)")
  else:K.append(f'[{a}] {aX} ITZ (Kırılım Öncesi Son Yapı: {g7:.4f}) Testi (08.pdf & YT-Part3)');pP=g7-E*0.45 if g else g7+E*0.45;bz=pP if bz is None else N(bz,pP)if g else M(bz,pP)
 return(l5,bz,K,az,pe)
def dp_ve_fl_analizi(df,z,C,a='1H',B='BULLISH'):
 l6,l7,l8,l9=([],[],[],None);hl={'magic_line':None,'fl_turu':'YOK','dp_turu':'YOK','swing_modeli':'V_Shape'};aa,ar=(z.get('highs',[]),z.get('lows',[]))
 if L(df)<18 or L(aa)<1 or L(ar)<1:return(l6,l9,l7,l8,hl)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);g=B=='BULLISH'
 def _dpt(hs,ht):
  for k in G(M(2,hs),N(L(df)-3,ht)+1):
   c1,c2=(df.iloc[k-1],df.iloc[k]);a0,bi,cg,ch=_r(c1,'open','close','high','low');br,a8,cI,cJ=_r(c2,'open','close','high','low');kH,h9=(A(bi-a0),A(a8-br));nh,ni=(cg-M(a0,bi),N(a0,bi)-ch);nj,nk=(cI-M(br,a8),N(br,a8)-cJ);mT=(a8>br)if g else(a8<br);rg=(bi<a0)if g else(bi>a0)
   if((bi>a0 and mT and nh>E*0.08 and nk>E*0.08 and cJ<=cg)if g else(bi<a0 and mT and ni>E*0.08 and nj>E*0.08 and cI>=ch))and kH>E*0.3 and h9>E*0.3:return('HiddenBase_DP',N(cJ,M(a0,bi)-E*0.15)if g else N(ch,M(br,a8)-E*0.15),M(cg,N(br,a8)+E*0.15)if g else M(cI,N(a0,bi)+E*0.15),k)
   if rg and((cI>cg and cJ<=ch and a8>a0)if g else(cI>=cg and cJ<ch and a8<a0)):return('MeraMera_QML_DP',cJ if g else ch,cg if g else cI,k)
   if rg and mT and(a8>=a0 if g else a8<=a0)and h9>M(kH*1.05,E*0.38):return('BuE_Engulf_DP'if g else'BE_Engulf_DP',N(ch,cJ)if g else a0,a0 if g else M(cg,cI),k)
   if kH<=E*0.25 and mT and h9>E*0.45:return('Doji_DP',ch,cg,k-1)
   if mT and h9>E*0.38 and A((M(a0,bi)-N(br,a8))if g else(N(a0,bi)-M(br,a8)))<=E*0.1:return('WBS_DP',N(ch,cJ)if g else(N(a0,bi)+M(br,a8))/2.0-E*0.1,(M(a0,bi)+N(br,a8))/2.0+E*0.1 if g else M(cg,cI),k)
  return('Standart_Base',None,None,None)
 k9,bh=(aa[-2]if L(aa)>=2 else aa[-1])if g else(ar[-2]if L(ar)>=2 else ar[-1])
 if k9<3 or k9>=L(df)-3:return(l6,l9,l7,l8,hl)
 bP=next((k for k in G(k9+1,L(df)-2)if(_f(df,'close',k)>bh if g else _f(df,'close',k)<bh)),None)
 if bP is None:return(l6,l9,l7,l8,hl)
 hl['magic_line']=R(bh,5);fv='high'if g else'low';oQ=[v for r7,v in(ar if g else aa)if r7<bP];qM=sum((1 for dN in G(M(0,k9-2),N(L(df)-2,k9+3))if A(F(df[fv].iloc[dN])-bh)<=E*0.25));ma,nT=(False,'W_Model'if g else'M_Model')
 if L(oQ)>=2:
  lp,mU=(oQ[-2],oQ[-1]);pf=A(mU-lp)/M(lp,1e-09)
  if pf<=0.008:ma,nT=(True,'W_EsitIkiliDip'if g else'M_EsitIkiliTepe')
  elif(mU>lp if g else mU<lp)and pf<=0.018:ma,nT=(True,'W_SagAyakYuksek'if g else'M_SagOmuzAlcak')
  elif(mU<lp if g else mU>lp)and pf<=0.018:ma,nT=(True,'W_SolAyakYuksek_QML'if g else'M_SolOmuzAlcak_QML')
 hl['swing_modeli']=nT if ma else('Keskin_V_Shape'if g else'Keskin_Ters_V_Shape')if qM<=1 else('Yayvan_V_Shape'if g else'Yayvan_Ters_V_Shape')if qM<=4 else'Cup_U_Canak'if g else'Ters_Cup_U_Canak';cT=sum((1 for dN in G(M(0,k9-12),bP)if A(F(df[fv].iloc[dN])-bh)<=E*0.35));oR=cT>=3;hm,fI=(False,bP)
 if bP+4<L(df)-2:
  mb=df.iloc[bP+1:N(L(df)-2,bP+9)];q1=sum((1 for _,r in mb.iterrows()if(F(r['close'])<F(r['open'])if g else F(r['close'])>F(r['open']))))
  if g:
   if q1>=2 and F(mb['low'].min())<=bh+E*0.2 and(F(df['high'].iloc[bP+1:-1].max())>_f(df,'high',bP)+E*0.4):hm,fI=(True,int(mb['low'].idxmin()))
  elif q1>=2 and F(mb['high'].max())>=bh-E*0.2 and(F(df['low'].iloc[bP+1:-1].min())<_f(df,'low',bP)-E*0.4):hm,fI=(True,int(mb['high'].idxmax()))
 lL=df.iloc[bP];la,nU,rW,ph=_r(lL,'open','close','high','low');qN=nU-la if g else la-nU;oS=(la<bh<nU if g else nU<bh<la)and qN>=E*0.7 and(qN/M(rW-ph,1e-09)>=0.68);qO=fI if hm else bP;lM,eO,g8,fJ=_dpt(qO-1,qO+1);hl['dp_turu']=lM;eq=''if g else'Bear_'
 if hm:
  jF=f'{eq}Genis_FL_BaseKing'
  if g:gg=eO if eO is not None else _f(df,'low',fI);gh=g8 if g8 is not None else M(bh,gg+E*0.35)
  else:gh=g8 if g8 is not None else _f(df,'high',fI);gg=eO if eO is not None else N(bh,gh-E*0.35)
 elif oR:jF=f'{eq}WickingBase_FL';gg=eO if eO is not None else bh-E*(0.25 if g else 0.2);gh=g8 if g8 is not None else bh+E*(0.2 if g else 0.25)
 elif ma and lM!='Standart_Base':jF='W_Kink_FL'if g else'M_Kink_FL';gg=eO if eO is not None else bh-E*0.2;gh=g8 if g8 is not None else bh+E*0.2
 elif oS and lM=='Standart_Base':jF=f'{eq}BlindSpot_FL';gg=M(la,bh-E*0.3)if g else bh-E*0.2;gh=bh+E*0.2 if g else N(la,bh+E*0.3)
 else:jF=f'{eq}Dar_FL';gg=eO if eO is not None else bh-E*0.22;gh=g8 if g8 is not None else bh+E*0.22
 hl['fl_turu']=jF;dS=bb if g else bc;cU=ak>=gg if g else ak<=gh
 if gg-E*0.2<=dS<=gh+E*0.2 and cU:jV=f'{a}_{jF}+{lM}';l6.append(jV);l7.append(f"[{a}] {('Bullish' if g else 'Bearish')} {jF} (Magic Line: {bh:.4f} | Swing: {hl['swing_modeli']} | Sniper DP: {lM} [{gg:.4f}-{gh:.4f}]) (10,11,12.pdf & YT-Part4)");l8.append(('BB/FL',fJ if fJ else bP,gg,gh));l9=gg if g else gh
 return(l6,l9,l7,l8,hl)
def quasimodo_mpl_analizi(df,z,C,a='1H',B='BULLISH'):
 lc,iC,iD,dO=([],[],[],None);dg={'qm_tipi':'YOK','qml_seviyesi':None,'mpl_seviyesi':None,'yaklasim_modeli':'Standart','karsi_fresh_hedef':None};aa,ar=(z.get('highs',[]),z.get('lows',[]))
 if L(df)<22 or L(aa)<2 or L(ar)<2:return(lc,dO,iC,iD,dg)
 aa_p=([aa[0]]*(3-L(aa))+list(aa))if L(aa)<3 else list(aa)
 ar_p=([ar[0]]*(3-L(ar))+list(ar))if L(ar)<3 else list(ar)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);(hS,H0),(gd,H1),(hf,H2)=(aa_p[-3],aa_p[-2],aa_p[-1]);(hT,L0),(ge,L1),(hg,L2)=(ar_p[-3],ar_p[-2],ar_p[-1]);d0,d4=swing_noktalarini_bul(df.iloc[-26:],1,False,False);cu=[];g=B=='BULLISH';aX='Bullish'if g else'Bearish';dg['karsi_fresh_hedef']=R(M(H1,H2)if g else N(L1,L2),5);k4=d4 if g else d0;de=bb if g else bc
 if L(k4)>=2:
  nV=[v for _,v in k4[-4:]];fK=sum((1 for u in nV[:-1]if A(u-nV[-1])<=E*0.28))
  if fK>=1 and(bb<N(nV[:-1])if g else bc>M(nV[:-1]))and(L(C)>0):cu.append(f"Fakeout_{('S1S' if g else 'R1R')}{fK + 1}")
 if L(d4)>=2 and L(d0)>=2:
  if(d4[-1][1]<d4[-2][1]and d0[-1][1]>d0[-2][1])if g else(d0[-1][1]>d0[-2][1]and d4[-1][1]<d4[-2][1]):cu.append('Fakeout+QML_Kombo'if any(('Fakeout'in y for y in cu))else'QML_Yaklasimi')
 nK=df.iloc[-9:-2];cw,cP=(nK['high'].values,nK['low'].values);dT=F((nK['high']-nK['low']).mean());eG=_f(df,'open',-3)-_f(df,'close',-3)if g else _f(df,'close',-3)-_f(df,'open',-3)
 if L(cw)>=5 and(cw[-1]<cw[0]and cP[-1]<cP[0]if g else cw[-1]>cw[0]and cP[-1]>cP[0])and(dT<=E*1.15):cu.append('CPLQ_Compression+Liq'if eG>=E*0.7 else'CP_Compression')
 if L(k4)>=3:
  d1,d2,d3=(k4[-3][1],k4[-2][1],k4[-1][1])
  if d1>d2>d3 if g else d1<d2<d3:cu.append('ThreeDrive_3D')
 if L(d0)>=2 and L(d4)>=2:
  if(F(df['high'].iloc[-6:-2].max())>d0[-2][1]if g else bc>d0[-2][1])and(bb<d4[-2][1]if g else F(df['low'].iloc[-6:-2].min())<d4[-2][1]):cu.append('Diamond_PO3_Box')
 qm_bul=_qml_yapisi_bul(aa,ar,'BULLISH'if g else'BEARISH')
 fw=qm_bul is not None
 if fw:
  gi,ku,ol_i,ol,h1_i,h1_v,h2_i,h2_v=qm_bul
  md=(ku>L0 and h1_v>H0)if g else(ku<H0 and h1_v<L0);dg['qml_seviyesi']=R(ku,5);jW=(L0<ku and L0<ol and A(ku-(L0+(ol-L0)/M(ol_i-hT,1)*M(L(df)-2-hT,1)))<=E*0.45)if g else(H0>ku and H0>ol and A(ku-(H0+(ol-H0)/M(ol_i-hS,1)*M(L(df)-2-hS,1)))<=E*0.45);aE=''if g else'Bear_';pi=f'{aE}QMC_Hibrit'if md and jW else f'{aE}QMC'if md else f'{aE}QMR'
  # HTF QML Toleransı: Fiyat OTE / QML / En Dip (ol..ku) koridoruna girdiğinde veya yaklaştığında QML aktif!
  qml_mesafe_ok=(ol-E*0.3<=de<=ku+E*1.65 and ak>=ol)if g else(ku-E*1.65<=de<=ol+E*0.3 and ak<=ol)
  if qml_mesafe_ok:
   dg['qm_tipi']=pi;lc.append(f"{a}_{('Bull_' if g else '')}{pi}");pQ=' | Yaklaşım: '+'+'.join(cu)if cu else''
   iC.append(f'[{a}] {aX} {pi} (Sol Omuz QML: {ku:.4f}, Baş: {ol:.4f}{pQ}) (13,14.pdf & YT-Part5)')
   iD.append(('QML',gi,N(ol,ku),M(ol,ku+E*0.18)if g else M(ol,ku)))
   dO=ol if dO is None else(N(dO,ol)if g else M(dO,ol))
 jG=(H1>H0 and L1<L0 and ak>H0 and F(df['close'].iloc[M(gd,ge):-1].max())>H1 and A(bb-H0)<=E*0.42)if g else(L1<L0 and H1>H0 and ak<L0 and F(df['close'].iloc[M(gd,ge):-1].min())<L1 and A(bc-L0)<=E*0.42)
 if jG:lq,mV=(H0,hS)if g else(L0,hT);dg['qm_tipi'],dg['qml_seviyesi']=('QMM_Flip'if g else'Bear_QMM_Flip',R(lq,5));lc.append(f"{a}_{('Bull' if g else 'Bear')}_QMM_Flip");iC.append(f'[{a}] {aX} QMM (Çalışmayan QML/OBO-TOBO [{lq:.4f}] kırıldı ve Flip oldu!) (YT-Part5)');iD.append(('QML',mV,lq-E*0.18,lq+E*0.18));pj=lq-E*0.4 if g else lq+E*0.4;dO=pj if dO is None else(N(dO,pj)if g else M(dO,pj))
 for k in G(M(4,L(df)-24),L(df)-4):
  ld=df.iloc[k+1]
  if g:
   lv,je=(_f(df,'low',k-2),_f(df,'low',k))
   if je<lv and F(ld['close'])-F(ld['open'])>E*0.55 and F(ld['close'])>_f(df,'high',k-1):
    oB=F(df['close'].iloc[k+2:-2].min())if k+2<L(df)-2 else lv
    if oB>=je and je-E*0.15<=bb<=lv+E*0.2 and ak>=je:dg['mpl_seviyesi']=R(lv,5);dg['qm_tipi']='MPL_IntermediateQML'if dg['qm_tipi']=='YOK'else dg['qm_tipi'];lc.append(f'{a}_Bull_MPL');iC.append(f'[{a}] Bullish MPL (Intermediate QML: {lv:.4f}, Stop: {je:.4f}) (15.pdf & YT-Part5)');iD.append(('QML',k,je,lv));dO=je if dO is None else N(dO,je);break
  else:
   lx,jf=(_f(df,'high',k-2),_f(df,'high',k))
   if jf>lx and F(ld['open'])-F(ld['close'])>E*0.55 and F(ld['close'])<_f(df,'low',k-1):
    oC=F(df['close'].iloc[k+2:-2].max())if k+2<L(df)-2 else lx
    if oC<=jf and lx-E*0.2<=bc<=jf+E*0.15 and ak<=jf:dg['mpl_seviyesi']=R(lx,5);dg['qm_tipi']='Bear_MPL_IntermediateQML'if dg['qm_tipi']=='YOK'else dg['qm_tipi'];lc.append(f'{a}_Bear_MPL');iC.append(f'[{a}] Bearish MPL (Intermediate QML: {lx:.4f}, Stop: {jf:.4f}) (15.pdf & YT-Part5)');iD.append(('QML',k,lx,jf));dO=jf if dO is None else M(dO,jf);break
 if cu:dg['yaklasim_modeli']=' + '.join(cu)
 return(lc,dO,iC,iD,dg)
def imbalance_fvg_koku_analizi(df,z,C,a='1H',B='BULLISH'):
 hu,hv,jX,dp=([],[],[],None);g4={'imbalance_tipi':'YOK','acik_imbalance_sayisi':L(C),'fvg_origin_koku':None,'erken_donus_fake_choch_uyarisi':False,'three_drive_d3_onay':False}
 if L(df)<25:return(hu,dp,hv,jX,g4)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);aa,ar=(z.get('highs',[]),z.get('lows',[]));a6=z.get('strong_point');g=B=='BULLISH';aX='Bullish'if g else'Bearish'
 for i in G(M(3,L(df)-36),L(df)-3):
  m0,m1,m2=(df.iloc[i-1],df.iloc[i],df.iloc[i+1]);c5,c6=(F(m0['high']),F(m0['low']));bB,cD,bC,bD=_r(m1,'open','close','high','low');aM,aD,cG,cH=_r(m2,'open','close','high','low');iF=df['low'if g else'high'].iloc[i+2:-2];jY=(cH>c5 and cD-bB>E*0.45 and not(not iF.empty and F(iF.min())<=c5))if g else(c6>cG and bB-cD>E*0.45 and not(not iF.empty and F(iF.max())>=c6))
  if jY:
   jg,ji=(N(c6,bD),c5)if g else(c6,M(c5,bC));g4['fvg_origin_koku']=R(ji if g else jg,5)
   if(jg-E*0.15<=bb<=ji+E*0.2 and ak>=jg)if g else(jg-E*0.2<=bc<=ji+E*0.15 and ak<=ji):g4['imbalance_tipi']=f"{('' if g else 'Bear_')}FVG+OriginKoku";hu.append(f"{a}_{('' if g else 'Bear_')}FVG_OriginKoku");hv.append(f'[{a}] {aX} FVG + Orijin Kök Testi ({jg:.4f}-{ji:.4f}) (19.pdf & YT-Part6)');jX.append(('FVG',i-1,jg,ji));dp=(jg if dp is None else N(dp,jg))if g else(ji if dp is None else M(dp,ji));break
  me=(cD>bB and aD>aM and aD-bB>=E*1.15 and cH<=c5 and not(not iF.empty and F(iF.min())<=bB))if g else(cD<bB and aD<aM and bB-aD>=E*1.15 and cG>=c6 and not(not iF.empty and F(iF.max())>=bB))
  if me:
   kI,kJ=(c6,bB)if g else(bB,c5)
   if(kI-E*0.15<=bb<=kJ+E*0.2 and ak>=kI)if g else(kI-E*0.2<=bc<=kJ+E*0.15 and ak<=kJ):g4['imbalance_tipi']=f"{('' if g else 'Bear_')}LiquidityVoid+OriginKoku";hu.append(f"{a}_{('' if g else 'Bear_')}LiqVoid_OriginKoku");hv.append(f'[{a}] {aX} Liquidity Void (2 Mumluk Boşluk) + Orijin Kök Testi ({kI:.4f}-{kJ:.4f}) (YT-Part6)');jX.append(('FVG',i-1,kI,kJ));dp=(kI if dp is None else N(dp,kI))if g else(kJ if dp is None else M(dp,kJ));break
 for i in G(M(4,L(df)-34),L(df)-6):
  nW=df.iloc[i];hw=A(F(nW['close'])-F(nW['open']));bV,bU=(F(nW['low']),F(nW['high']));fL=df.iloc[i+2:N(L(df)-2,i+14)];mf=(_f(df,'open',i-1)-_f(df,'close',i-1))if g else(_f(df,'close',i-1)-_f(df,'open',i-1));jZ=(_f(df,'open',i+1)-_f(df,'close',i+1))if g else(_f(df,'close',i+1)-_f(df,'open',i+1))
  if mf>E*0.45 and hw<=E*0.5 and jZ>E*0.45:
   gj=any((_f(fL,'close',m)>bU+E*0.15 and _f(fL,'close',m)-_f(fL,'open',M(0,m-1))>E*0.9 for m in G(L(fL))))if g else any((_f(fL,'close',m)<bV-E*0.15 and _f(fL,'open',M(0,m-1))-_f(fL,'close',m)>E*0.9 for m in G(L(fL))))
   if gj and(bV-E*0.15<=(bb if g else bc)<=bU+E*0.15)and(ak>=bV if g else ak<=bU):jj='TersBayrak_DBD_Flip'if g else'Bear_TersBayrak_RBR_Flip';g4['imbalance_tipi']=jj;hu.append(f'{a}_{jj}');hv.append(f'[{a}] {aX} Ters Bayrak (Kırılan DBD/RBR Base / IFVG Kaynağı: {bV:.4f}-{bU:.4f}) Flip Oldu! (YT-Part6)');jX.append(('IFVG',i,bV,bU));dp=(bV if dp is None else N(dp,bV))if g else(bU if dp is None else M(dp,bU));break
 nL=ar if g else aa
 if L(nL)>=3:
  d1,d2,d3=(nL[-3][1],nL[-2][1],nL[-1][1])
  if(d1>d2>d3 if g else d1<d2<d3)and(L(hu)>0 or(a6 and A((bb if g else bc)-a6)<=E*0.6)):g4['three_drive_d3_onay']=True;hu.append(f"{a}_{('' if g else 'Bear_')}ThreeDrive_D3_FreshPOI");hv.append(f'[{a}] {aX} Three Drive ({d1:.4f}->{d2:.4f}->{d3:.4f}) 3. Adımı Taze POI Bölgesiyle Çakıştı (YT-Part6)')
 if a6 and L(C)>0:
  nX=F(df['low'].iloc[-8:-2].min())if g else F(df['high'].iloc[-8:-2].max());fM=(a6+E*0.25<nX<=a6+E*1.15 and bb<=nX)if g else(a6-E*1.15<=nX<a6-E*0.25 and bc>=nX)
  if fM:hu.append(f"{a}_{('' if g else 'Bear_')}FakeCHoCH_Sweep_Onayi");hv.append(f'[{a}] {aX} Erken Dönüş Likiditesi Süpürüldü: Ana bölge ({a6:.4f}) önü stop birikimi temizlendi! (YT-Part6)')
  elif(bb>a6+E*0.35 if g else bc<a6-E*0.35)and L(hu)==0:g4['erken_donus_fake_choch_uyarisi']=True
 return(hu,dp,hv,jX,g4)
def gap_vib_fibo_analizi(df,z,Z,a='1H',B='BULLISH'):
 g9,fl,lf,fm=([],[],[],None);er={'gap_vib_durumu':'YOK','fibo_05_saygi':False,'fibo_istasyon_uyumu':'YOK','manipulasyon_236_382':False}
 if L(df)<25:return(g9,fm,fl,lf,er)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);hb,fN=(z.get('swing_max',0.0),z.get('swing_min',0.0));dU=hb-fN;qP=z.get('break_line_fl');g=B=='BULLISH';aX='Bullish'if g else'Bearish';de=bb if g else bc
 if dU>E*1.5 and sum((1 for k in G(M(2,L(df)-32),L(df)-4)if A(_f(df,'close',k)-(fN+dU*0.5))<=E*0.28))>=2:er['fibo_05_saygi']=True
 for i in G(M(3,L(df)-30),L(df)-3):
  c1,c2=(df.iloc[i-1],df.iloc[i]);a0,bi,cg,ch=_r(c1,'open','close','high','low');br,a8,cI,cJ=_r(c2,'open','close','high','low');nY=br-bi;cP,cw=(N(bi,br),M(bi,br));fo=df['low'if g else'high'].iloc[i+1:-2];j0=(nY>=E*0.08 and a8>bi and not(not fo.empty and F(fo.min())<cP-E*0.05))if g else(nY<=-E*0.08 and a8<bi and not(not fo.empty and F(fo.max())>cw+E*0.05))
  if j0 and cP-E*0.2<=de<=cw+E*0.2 and(ak>=cP if g else ak<=cw):rh=cJ>cg if g else cI<ch;r6=qP is not None and A((cP if g else cw)-qP)<=E*0.6;aE=''if g else'Bear_';lr=f'{aE}Breakaway_Gap'if rh and r6 else f'{aE}Runaway_Gap'if rh else f"{('Bull' if g else 'Bear')}_VIB";er['gap_vib_durumu']=lr;g9.append(f'{a}_{lr}');fl.append(f'[{a}] {aX} {lr} Testi ({cP:.4f}-{cw:.4f}) (20.pdf & YT-Part7)');lf.append(('FVG',i,cP,cw));fm=(cP if fm is None else N(fm,cP))if g else(cw if fm is None else M(fm,cw));break
  hx=(nY<=-E*0.08 and a8>cg and cP-E*0.18<=bb<=cw+E*0.18 and ak>=cP)if g else(nY>=E*0.08 and a8<ch and cP-E*0.18<=bc<=cw+E*0.18 and ak<=cw)
  if hx:lr='Bull_VIB_Flip'if g else'Bear_VIB_Flip';er['gap_vib_durumu']=lr;g9.append(f'{a}_{lr}');fl.append(f'[{a}] {aX} VIB Flip ({cP:.4f}-{cw:.4f}): Ters Volume Imbalance yutulup Flip oldu! (YT-Part7)');lf.append(('IFVG',i,cP,cw));fm=(cP if fm is None else N(fm,cP))if g else(cw if fm is None else M(fm,cw));break
 ff=z.get('geri_cekilme_oran'if g else'fibo_oran',0.5);nM=' + 0.50 AvgPrice Saygılı'if er['fibo_05_saygi']else''
 if 0.21<=ff<=0.41 and any((x in p for p in Z for x in('FTR','FirstObstacle_FO'))):er['fibo_istasyon_uyumu']=f'GucluTrend_236_382_FTR_FO({ff:.3f})';g9.append(f'{a}_Fibo236_382_GucluTrend_FTR_FO');fl.append(f'[{a}] Güçlü Trend 0.236-0.382 ({ff:.3f}) + FTR/FO Eşleşmesi{nM} (YT-Part7)')
 elif 0.48<=ff<=0.64 and any((x in p for p in Z for x in('FL','BB/FL','TersBayrak'))):er['fibo_istasyon_uyumu']=f'GoldenZone_05_618_FL({ff:.3f})';g9.append(f'{a}_Fibo05_618_FL_Onayi');fl.append(f'[{a}] Sihirli Fibo 0.50-0.618 ({ff:.3f}) + Flag Limit Eşleşmesi{nM} (YT-Part7)')
 elif 0.68<=ff<=0.82 and any((x in p for p in Z for x in('OB','Valid','QML','QMR','QMC','ITZ','MPL'))):er['fibo_istasyon_uyumu']=f'OTE_705_786_OB_QML_ITZ({ff:.3f})';g9.append(f'{a}_Fibo705_786_OB_QML_Onayi');fl.append(f'[{a}] Sihirli Fibo OTE 0.705-0.786 ({ff:.3f}) + OB/QML/ITZ/Valid Eşleşmesi{nM} (YT-Part7)')
 elif 0.84<=ff<=0.94 and any((x in p for p in Z for x in('OB','Valid','QML','QMR'))):er['fibo_istasyon_uyumu']=f'Istisnai_886_DerinOB({ff:.3f})';g9.append(f'{a}_Fibo886_Istisnai_DerinOB');fl.append(f'[{a}] Sihirli Fibo 0.886 ({ff:.3f}) İstisnai Derin OB{nM} (YT-Part7)')
 if dU>E*2.0 and L(df)>=28:
  q2=df.iloc[-16:-4];mW,mX=(F(q2['high'].max()),F(q2['low'].min()))
  if mW-mX<=E*3.2:
   if g and mX<=fN+dU*0.382 and bb<mX and ak>=mX:er['manipulasyon_236_382']=True;g9.append(f'{a}_Bull_236_382_Manipulasyon_PO3');fl.append(f'[{a}] Bullish 0.236-0.382 Sıkıştırma Manipülasyonu & -0.236 Devyasyon Dönüşü ({mX:.4f}) (YT-Part7)')
   elif not g and mW>=hb-dU*0.382 and bc>mW and ak<=mW:er['manipulasyon_236_382']=True;g9.append(f'{a}_Bear_236_382_Manipulasyon_PO3');fl.append(f'[{a}] Bearish 0.236-0.382 Sıkıştırma Manipülasyonu & -0.236 Devyasyon Dönüşü ({mW:.4f}) (YT-Part7)')
 return(g9,fm,fl,lf,er)
def _likidite_ve_sfp_yapilarini_bul(df_c,uH=None,uL=None,ts_arr=None):
 liq_list=[];sfp_list=[]
 meta={'aktif_eqh':[],'aktif_eql':[],'swept_eqh':[],'swept_eql':[],'aktif_idm_bsl':None,'aktif_idm_ssl':None,'swept_idm_bull':None,'swept_idm_bear':None,'mss_displacement_bull':False,'mss_displacement_bear':False,'trendline_bsl':[],'trendline_ssl':[],'ext_bsl':None,'ext_ssl':None,'int_bsl':None,'int_ssl':None,'son_bull_sfp':None,'son_bear_sfp':None}
 if df_c is None or L(df_c)<8:return(liq_list,sfp_list,meta)
 ct=L(df_c)
 if ts_arr is None or L(ts_arr)!=ct:
  ts_arr=[int(F(_f(df_c,'timestamp',i))/1000)if'timestamp'in df_c.columns and _f(df_c,'timestamp',i)>0 else(1700000000+i*300)for i in G(ct)]
 son_c=_f(df_c,'close',-1)
 E=M(_f(df_c,'atr',-2)if'atr'in df_c.columns else son_c*0.003,son_c*0.001)
 jn_raw,jo_raw=swing_noktalarini_bul(df_c,2,False,False)
 h_map={int(i):F(v)for i,v in(jn_raw or[])if 0<=int(i)<ct}
 l_map={int(i):F(v)for i,v in(jo_raw or[])if 0<=int(i)<ct}
 for i,v in(uH or[]):
  if 0<=int(i)<ct:h_map[int(i)]=M(h_map.get(int(i),F(v)),F(v))
 for i,v in(uL or[]):
  if 0<=int(i)<ct:l_map[int(i)]=N(l_map.get(int(i),F(v)),F(v))
 jn=sorted(h_map.items(),key=lambda x:x[0])
 jo=sorted(l_map.items(),key=lambda x:x[0])
 tol_eq=N(M(E*EQH_EQL_TOL_ATR,son_c*0.0007),son_c*0.0045)
 kullanilan_h=set();kullanilan_l=set()
 sfp_eklenen=set()
 # 1) EQH (Buy-Side Liquidity - 16-fakeout.pdf, 22-likidite.pdf, 27-tt3.pdf, YT-Part8 & Drive Video Ders-02): Sadece kırılmamış (Taze Bedava Yakıt) veya iğneyle süpürülüp içeride kapanmış (SFP/TT3) eşit tepeler
 for k in G(L(jn)):
  i1,h1=jn[k]
  if i1 in kullanilan_h:continue
  es_grup=[(i1,h1)]
  for m in G(k+1,N(L(jn),k+5)):
   im,hm=jn[m]
   if im-es_grup[-1][0]<3:continue
   if A(hm-h1)<=tol_eq:
    tavan_ara=M(h1,hm)
    ara_kirildi=any((_f(df_c,'high',b)>tavan_ara+E*0.08 for b in G(es_grup[-1][0]+1,im)))
    if not ara_kirildi:es_grup.append((im,hm))
  if L(es_grup)>=2:
   i_son,h_son=es_grup[-1]
   ort_h=sum((v for _,v in es_grup))/F(L(es_grup))
   tavan_h=M((v for _,v in es_grup))
   govde_kirildi=False;sweep_idx=None;sweep_hi=0.0
   for b in G(i_son+1,ct):
    cb,hb,ob=(_f(df_c,'close',b),_f(df_c,'high',b),_f(df_c,'open',b))
    if cb>tavan_h+E*0.10:
     govde_kirildi=True;break
    if hb>tavan_h+E*0.02 and cb<=tavan_h+E*0.02 and(hb-M(ob,cb))>=E*0.12:
     if sweep_idx is None:sweep_idx=b;sweep_hi=hb
    elif hb>tavan_h+E*0.25 and cb>tavan_h:
     govde_kirildi=True;break
   if govde_kirildi:continue
   for idx_e,_ in es_grup:kullanilan_h.add(idx_e)
   tt_etiket='$$$ 3x EQH (TT3 BSL)'if L(es_grup)>=3 else'$$$ EQH (BSL)'
   if sweep_idx is not None:
    if sweep_idx>=ct-35:
     meta['swept_eqh'].append((i1,sweep_idx,ort_h))
     liq_list.append({'tip':'💧 EQH Sweep (SFP)','idx1':int(i1),'idx2':int(sweep_idx),'t1':ts_arr[i1],'t2':ts_arr[sweep_idx],'p1':F(ort_h),'p2':F(ort_h),'renk':'#f43f5e','aktif':False})
     if('BEAR',sweep_idx)not in sfp_eklenen:
      sfp_eklenen.add(('BEAR',sweep_idx))
      sfp_obj={'tip':'▼ Bear SFP (EQH)','idx':int(sweep_idx),'orig_idx':int(i1),'time':ts_arr[sweep_idx],'orig_time':ts_arr[i1],'price':F(sweep_hi),'level':F(ort_h),'yon':'BEAR'}
      sfp_list.append(sfp_obj);meta['son_bear_sfp']=sfp_obj
   else:
    meta['aktif_eqh'].append((i1,ct-1,ort_h))
    liq_list.append({'tip':tt_etiket,'idx1':int(i1),'idx2':int(ct-1),'t1':ts_arr[i1],'t2':ts_arr[ct-1],'p1':F(ort_h),'p2':F(ort_h),'renk':'#fbbf24','aktif':True})
 # 2) EQL (Sell-Side Liquidity - 16-fakeout.pdf, 22-likidite.pdf, 27-tt3.pdf, YT-Part8 & Drive Video Ders-02): Sadece kırılmamış (Taze Bedava Yakıt) veya iğneyle süpürülüp içeride kapanmış (SFP/TT3) eşit dipler
 for k in G(L(jo)):
  i1,l1=jo[k]
  if i1 in kullanilan_l:continue
  es_grup=[(i1,l1)]
  for m in G(k+1,N(L(jo),k+5)):
   im,lm=jo[m]
   if im-es_grup[-1][0]<3:continue
   if A(lm-l1)<=tol_eq:
    taban_ara=N(l1,lm)
    ara_kirildi=any((_f(df_c,'low',b)<taban_ara-E*0.08 for b in G(es_grup[-1][0]+1,im)))
    if not ara_kirildi:es_grup.append((im,lm))
  if L(es_grup)>=2:
   i_son,l_son=es_grup[-1]
   ort_l=sum((v for _,v in es_grup))/F(L(es_grup))
   taban_l=N((v for _,v in es_grup))
   govde_kirildi=False;sweep_idx=None;sweep_lo=1e18
   for b in G(i_son+1,ct):
    cb,lb,ob=(_f(df_c,'close',b),_f(df_c,'low',b),_f(df_c,'open',b))
    if cb<taban_l-E*0.10:
     govde_kirildi=True;break
    if lb<taban_l-E*0.02 and cb>=taban_l-E*0.02 and(N(ob,cb)-lb)>=E*0.12:
     if sweep_idx is None:sweep_idx=b;sweep_lo=lb
    elif lb<taban_l-E*0.25 and cb<taban_l:
     govde_kirildi=True;break
   if govde_kirildi:continue
   for idx_e,_ in es_grup:kullanilan_l.add(idx_e)
   tt_etiket='$$$ 3x EQL (TT3 SSL)'if L(es_grup)>=3 else'$$$ EQL (SSL)'
   if sweep_idx is not None:
    if sweep_idx>=ct-35:
     meta['swept_eql'].append((i1,sweep_idx,ort_l))
     liq_list.append({'tip':'💧 EQL Sweep (SFP)','idx1':int(i1),'idx2':int(sweep_idx),'t1':ts_arr[i1],'t2':ts_arr[sweep_idx],'p1':F(ort_l),'p2':F(ort_l),'renk':'#10b981','aktif':False})
     if('BULL',sweep_idx)not in sfp_eklenen:
      sfp_eklenen.add(('BULL',sweep_idx))
      sfp_obj={'tip':'▲ Bull SFP (EQL)','idx':int(sweep_idx),'orig_idx':int(i1),'time':ts_arr[sweep_idx],'orig_time':ts_arr[i1],'price':F(sweep_lo),'level':F(ort_l),'yon':'BULL'}
      sfp_list.append(sfp_obj);meta['son_bull_sfp']=sfp_obj
   else:
    meta['aktif_eql'].append((i1,ct-1,ort_l))
    liq_list.append({'tip':tt_etiket,'idx1':int(i1),'idx2':int(ct-1),'t1':ts_arr[i1],'t2':ts_arr[ct-1],'p1':F(ort_l),'p2':F(ort_l),'renk':'#38bdf8','aktif':True})
 # 3) Tekil Swing SFP vs Gerçek Gövde Kırılımı (23-sfp.pdf, YT-Part8 & Drive Video Ders-04/05: İğneyle delip içeride kapanan = Likidite Süpürmesi / SFP, Gövde Kapanışı = BOS/MSS)
 for i_h,v_h in jn[-8:]:
  if i_h>=ct-2:continue
  ilk_gecis=None
  for b in G(i_h+1,ct):
   if _f(df_c,'high',b)>v_h+E*0.02:ilk_gecis=b;break
  if ilk_gecis is not None and ilk_gecis>=M(i_h+2,ct-35):
   cb,hb,ob=(_f(df_c,'close',ilk_gecis),_f(df_c,'high',ilk_gecis),_f(df_c,'open',ilk_gecis))
   ust_igne=hb-M(ob,cb)
   sonraki_bozdu=any((_f(df_c,'close',m)>hb for m in G(ilk_gecis+1,ct)))
   if cb<v_h and ust_igne>=E*0.14 and not sonraki_bozdu and('BEAR',ilk_gecis)not in sfp_eklenen:
    sfp_eklenen.add(('BEAR',ilk_gecis))
    sfp_obj={'tip':'▼ Bear SFP (İğne Avı)','idx':int(ilk_gecis),'orig_idx':int(i_h),'time':ts_arr[ilk_gecis],'orig_time':ts_arr[i_h],'price':F(hb),'level':F(v_h),'yon':'BEAR'}
    sfp_list.append(sfp_obj);meta['son_bear_sfp']=sfp_obj
    if i_h not in kullanilan_h:
     liq_list.append({'tip':'💧 BSL Sweep (SFP)','idx1':int(i_h),'idx2':int(ilk_gecis),'t1':ts_arr[i_h],'t2':ts_arr[ilk_gecis],'p1':F(v_h),'p2':F(v_h),'renk':'#fb7185','aktif':False})
 for i_l,v_l in jo[-8:]:
  if i_l>=ct-2:continue
  ilk_gecis=None
  for b in G(i_l+1,ct):
   if _f(df_c,'low',b)<v_l-E*0.02:ilk_gecis=b;break
  if ilk_gecis is not None and ilk_gecis>=M(i_l+2,ct-35):
   cb,lb,ob=(_f(df_c,'close',ilk_gecis),_f(df_c,'low',ilk_gecis),_f(df_c,'open',ilk_gecis))
   alt_igne=N(ob,cb)-lb
   sonraki_bozdu=any((_f(df_c,'close',m)<lb for m in G(ilk_gecis+1,ct)))
   if cb>v_l and alt_igne>=E*0.14 and not sonraki_bozdu and('BULL',ilk_gecis)not in sfp_eklenen:
    sfp_eklenen.add(('BULL',ilk_gecis))
    sfp_obj={'tip':'▲ Bull SFP (İğne Avı)','idx':int(ilk_gecis),'orig_idx':int(i_l),'time':ts_arr[ilk_gecis],'orig_time':ts_arr[i_l],'price':F(lb),'level':F(v_l),'yon':'BULL'}
    sfp_list.append(sfp_obj);meta['son_bull_sfp']=sfp_obj
    if i_l not in kullanilan_l:
     liq_list.append({'tip':'💧 SSL Sweep (SFP)','idx1':int(i_l),'idx2':int(ilk_gecis),'t1':ts_arr[i_l],'t2':ts_arr[ilk_gecis],'p1':F(v_l),'p2':F(v_l),'renk':'#34d399','aktif':False})
 # 4) Inducement / IDM (Likidite Yemi - Drive Video Klasörü Ders-03 & YT-Part3/6/8: Gerçek POI öncesi yarı yoldaki küçük tepe/dip tuzağı)
 if L(jn)>=2 and L(jo)>=2:
  son_h_i,son_h_v=jn[-1];son_l_i,son_l_v=jo[-1]
  ic_h,ic_l=swing_noktalarini_bul(df_c,1,False,False)
  # Bullish Yapıda IDM: Son ana dip (Origin) ile son tepe sonrasında gerçek talep bölgesine inmeden önce yarı yolda oluşan ilk küçük dip
  onceki_ana_l=[(il,vl)for il,vl in jo if il<son_h_i]
  if onceki_ana_l:
   orig_l_i,orig_l_v=onceki_ana_l[-1]
   bacak_boy=son_h_v-orig_l_v
   if bacak_boy>=E*1.6 and son_h_i<ct-2:
    aday_idm_l=[(il,vl)for il,vl in ic_l if son_h_i<il<ct-1 and orig_l_v+bacak_boy*0.18<=vl<=orig_l_v+bacak_boy*0.72]
    if aday_idm_l:
     idm_i,idm_v=aday_idm_l[0]
     idm_supuruldu=None
     for b in G(idm_i+1,ct):
      if _f(df_c,'low',b)<idm_v-E*0.02 and _f(df_c,'close',b)>orig_l_v:
       idm_supuruldu=b;break
     if idm_supuruldu is not None:
      meta['swept_idm_bull']=(idm_i,idm_supuruldu,F(idm_v))
      liq_list.append({'tip':'💧 IDM Sweep (Yem Yutuldu ✓)','idx1':int(idm_i),'idx2':int(idm_supuruldu),'t1':ts_arr[idm_i],'t2':ts_arr[idm_supuruldu],'p1':F(idm_v),'p2':F(idm_v),'renk':'#2dd4bf','aktif':False})
     elif son_c>idm_v:
      meta['aktif_idm_ssl']=(idm_i,ct-1,F(idm_v))
      liq_list.append({'tip':'🎣 IDM (Likidite Yemi SSL)','idx1':int(idm_i),'idx2':int(ct-1),'t1':ts_arr[idm_i],'t2':ts_arr[ct-1],'p1':F(idm_v),'p2':F(idm_v),'renk':'#e879f9','aktif':True})
  # Bearish Yapıda IDM: Son ana tepe (Origin) ile son dip sonrasında gerçek arz bölgesine çıkmadan önce yarı yolda oluşan ilk küçük tepe
  onceki_ana_h=[(ih,vh)for ih,vh in jn if ih<son_l_i]
  if onceki_ana_h:
   orig_h_i,orig_h_v=onceki_ana_h[-1]
   bacak_boy_b=orig_h_v-son_l_v
   if bacak_boy_b>=E*1.6 and son_l_i<ct-2:
    aday_idm_h=[(ih,vh)for ih,vh in ic_h if son_l_i<ih<ct-1 and son_l_v+bacak_boy_b*0.28<=vh<=orig_h_v-bacak_boy_b*0.18]
    if aday_idm_h:
     idm_hi,idm_hv=aday_idm_h[0]
     idm_h_sup=None
     for b in G(idm_hi+1,ct):
      if _f(df_c,'high',b)>idm_hv+E*0.02 and _f(df_c,'close',b)<orig_h_v:
       idm_h_sup=b;break
     if idm_h_sup is not None:
      meta['swept_idm_bear']=(idm_hi,idm_h_sup,F(idm_hv))
      liq_list.append({'tip':'💧 IDM Sweep (Yem Yutuldu ✓)','idx1':int(idm_hi),'idx2':int(idm_h_sup),'t1':ts_arr[idm_hi],'t2':ts_arr[idm_h_sup],'p1':F(idm_hv),'p2':F(idm_hv),'renk':'#fb7185','aktif':False})
     elif son_c<idm_hv:
      meta['aktif_idm_bsl']=(idm_hi,ct-1,F(idm_hv))
      liq_list.append({'tip':'🎣 IDM (Likidite Yemi BSL)','idx1':int(idm_hi),'idx2':int(ct-1),'t1':ts_arr[idm_hi],'t2':ts_arr[ct-1],'p1':F(idm_hv),'p2':F(idm_hv),'renk':'#e879f9','aktif':True})
 # 5) Aktif External & Internal (Old High BSL / Old Low SSL) Likidite Havuzları (22-likidite.pdf, YT-Part8 & Drive Video Ders-02/10)
 taze_highs=[(i_h,v_h)for i_h,v_h in jn if i_h<ct-2 and v_h>son_c and all((_f(df_c,'high',b)<=v_h+E*0.03 for b in G(i_h+1,ct)))]
 taze_lows=[(i_l,v_l)for i_l,v_l in jo if i_l<ct-2 and v_l<son_c and all((_f(df_c,'low',b)>=v_l-E*0.03 for b in G(i_l+1,ct)))]
 if taze_highs:
  ext_h_i,ext_h_v=max(taze_highs,key=lambda x:x[1])
  int_h_i,int_h_v=min(taze_highs,key=lambda x:x[1])
  meta['ext_bsl']=F(ext_h_v);meta['int_bsl']=F(int_h_v)
  if all((A(ext_h_v-lq['p1'])>tol_eq for lq in liq_list)):
   liq_list.append({'tip':'$$$ Ext BSL (Eski Tepe)','idx1':int(ext_h_i),'idx2':int(ct-1),'t1':ts_arr[ext_h_i],'t2':ts_arr[ct-1],'p1':F(ext_h_v),'p2':F(ext_h_v),'renk':'#f59e0b','aktif':True})
 if taze_lows:
  ext_l_i,ext_l_v=min(taze_lows,key=lambda x:x[1])
  int_l_i,int_l_v=max(taze_lows,key=lambda x:x[1])
  meta['ext_ssl']=F(ext_l_v);meta['int_ssl']=F(int_l_v)
  if all((A(ext_l_v-lq['p1'])>tol_eq for lq in liq_list)):
   liq_list.append({'tip':'$$$ Ext SSL (Eski Dip)','idx1':int(ext_l_i),'idx2':int(ct-1),'t1':ts_arr[ext_l_i],'t2':ts_arr[ct-1],'p1':F(ext_l_v),'p2':F(ext_l_v),'renk':'#0ea5e9','aktif':True})
 # 6) 3-Temaslı Doğrulanmış Trendline Likiditesi (Kuru Kafa / Trendline Liq - 16, 22.pdf & YT-Part1, Part8 & Drive Video Ders-01)
 if L(jn)>=3:
  son_h_aday=jn[-6:]
  tl_bulundu=False
  for a_i in G(L(son_h_aday)-2):
   if tl_bulundu:break
   for b_i in G(a_i+1,L(son_h_aday)-1):
    if tl_bulundu:break
    for c_i in G(b_i+1,L(son_h_aday)):
     (x1,y1),(x2,y2),(x3,y3)=(son_h_aday[a_i],son_h_aday[b_i],son_h_aday[c_i])
     if x3-x1>=6 and y1>y2>y3:
      egim=(y3-y1)/F(M(1,x3-x1))
      y2_hat=y1+egim*(x2-x1)
      if A(y2-y2_hat)<=E*0.35:
       ihlal_ara=any((_f(df_c,'high',m)>(y1+egim*(m-x1))+E*0.16 for m in G(x1+1,x3)))
       ihlal_sonra=any((_f(df_c,'close',m)>(y1+egim*(m-x1))+E*0.20 for m in G(x3+1,ct)))
       if not ihlal_ara and not ihlal_sonra:
        x_bit=N(ct-1,x3+12)
        y_bit=y1+egim*(x_bit-x1)
        meta['trendline_bsl'].append((x1,x_bit,y1,y_bit))
        liq_list.append({'tip':'📐 Trendline BSL ($$$)','idx1':int(x1),'idx2':int(x_bit),'t1':ts_arr[x1],'t2':ts_arr[x_bit],'p1':F(y1),'p2':F(y_bit),'renk':'#f59e0b','aktif':True})
        tl_bulundu=True;break
 if L(jo)>=3:
  son_l_aday=jo[-6:]
  tl_bulundu=False
  for a_i in G(L(son_l_aday)-2):
   if tl_bulundu:break
   for b_i in G(a_i+1,L(son_l_aday)-1):
    if tl_bulundu:break
    for c_i in G(b_i+1,L(son_l_aday)):
     (x1,y1),(x2,y2),(x3,y3)=(son_l_aday[a_i],son_l_aday[b_i],son_l_aday[c_i])
     if x3-x1>=6 and y1<y2<y3:
      egim=(y3-y1)/F(M(1,x3-x1))
      y2_hat=y1+egim*(x2-x1)
      if A(y2-y2_hat)<=E*0.35:
       ihlal_ara=any((_f(df_c,'low',m)<(y1+egim*(m-x1))-E*0.16 for m in G(x1+1,x3)))
       ihlal_sonra=any((_f(df_c,'close',m)<(y1+egim*(m-x1))-E*0.20 for m in G(x3+1,ct)))
       if not ihlal_ara and not ihlal_sonra:
        x_bit=N(ct-1,x3+12)
        y_bit=y1+egim*(x_bit-x1)
        meta['trendline_ssl'].append((x1,x_bit,y1,y_bit))
        liq_list.append({'tip':'📐 Trendline SSL ($$$)','idx1':int(x1),'idx2':int(x_bit),'t1':ts_arr[x1],'t2':ts_arr[x_bit],'p1':F(y1),'p2':F(y_bit),'renk':'#38bdf8','aktif':True})
        tl_bulundu=True;break
 return(liq_list[-11:],sfp_list[-6:],meta)
def likidite_ve_sfp_analizi(bJ,af,a2,Z,B='BULLISH'):
 lg,lh,li=([],[],0);dh={'external_likidite_hedefi':None,'internal_ilk_engel_hedefi':None,'sfp_durumu':'YOK','likidite_turu':'YOK','idm_durumu':'YOK','akis_protokolu_onay':False}
 if L(bJ)<20 or L(af)<20:return(li,lg,lh,dh)
 pl,pm=(a2.get('highs',[]),a2.get('lows',[]));d0,d4=swing_noktalarini_bul(af,n=1);lN=af.iloc[-2];d6,iG,n1,n2=(F(lN['close']),F(lN['open']),F(lN['high']),F(lN['low']));jH=M(F(lN['atr']),d6*0.001);qQ=M(_f(bJ,'atr',-2),d6*0.001);a6=a2.get('strong_point');g=B=='BULLISH'
 _,_,mtf_lm=_likidite_ve_sfp_yapilarini_bul(bJ,pl,pm)
 _,ltf_sfp_l,ltf_lm=_likidite_ve_sfp_yapilarini_bul(af)
 nN=(mtf_lm.get('ext_bsl')or ltf_lm.get('ext_bsl')or M([h for _,h in pl[-3:]if h>d6],default=d6*1.03))if g else(mtf_lm.get('ext_ssl')or ltf_lm.get('ext_ssl')or N([l for _,l in pm[-3:]if l<d6],default=d6*0.97))
 dh['external_likidite_hedefi']=R(F(nN),5)
 int_h=(ltf_lm.get('int_bsl')or mtf_lm.get('int_bsl'))if g else(ltf_lm.get('int_ssl')or mtf_lm.get('int_ssl'))
 dh['internal_ilk_engel_hedefi']=R(F(int_h if int_h and(d6<int_h<=nN if g else nN<=int_h<d6)else nN),5)
 # 1) Inducement (IDM - Likidite Yemi Süpürmesi: Drive Video Klasörü Ders-03 & YT-Part8)
 swept_idm=(mtf_lm.get('swept_idm_bull')or ltf_lm.get('swept_idm_bull'))if g else(mtf_lm.get('swept_idm_bear')or ltf_lm.get('swept_idm_bear'))
 aktif_idm=(mtf_lm.get('aktif_idm_ssl')or ltf_lm.get('aktif_idm_ssl'))if g else(mtf_lm.get('aktif_idm_bsl')or ltf_lm.get('aktif_idm_bsl'))
 if swept_idm:
  idm_f=F(swept_idm[2])
  dh['idm_durumu']=f'IDM_Sweep_Onayli({idm_f:.4f})'
  if dh['likidite_turu']=='YOK':dh['likidite_turu']='IDM_Inducement_Sweep'
  lg.append('Bull_IDM_Inducement_Sweep'if g else'Bear_IDM_Inducement_Sweep')
  lh.append(f"[{MTF_PERIYOT.upper()}/{LTF_PERIYOT}] Inducement (IDM Likidite Yemi: {idm_f:.4f}) Süpürüldü, Sabırsız Stoplar Temizlendi -> Gerçek Kurumsal Bölge Aktif! (Drive Video Ders-03 & YT-Part8)")
  li+=5
 elif aktif_idm:
  dh['idm_durumu']=f'Aktif_IDM_Yemi_Bekleniyor({F(aktif_idm[2]):.4f})'
 # 2) Doğrulanmış SFP (EQL/EQH & Old Low/High İğne Avı: 23-sfp.pdf, YT-Part8 & Drive Video Ders-02/04)
 son_sfp=ltf_lm.get('son_bull_sfp'if g else'son_bear_sfp')
 if son_sfp and int(son_sfp.get('idx',0))>=L(af)-6:
  eq_mi='EQ'in str(son_sfp.get('tip',''))
  pR=('Bull_EQL_SFP'if eq_mi else'Bull_OldLow_SFP')if g else('Bear_EQH_SFP'if eq_mi else'Bear_OldHigh_SFP')
  mg=F(son_sfp.get('level')or son_sfp.get('price')or d6)
  dh['sfp_durumu'],dh['likidite_turu']=(pR,('EQL'if g else'EQH')+'_StopPool'if eq_mi else('OldLow'if g else'OldHigh')+'_StopPool')
  lg.append(pR);lh.append(f'[{LTF_PERIYOT}] {pR}: {mg:.4f} likiditesi iğneyle süpürüldü (Sahte Kırılım / İğne Avı) ve içeride ({d6:.4f}) kapandı! (23-sfp.pdf, YT-Part8 & Ders-02/04)');li+=6
 elif(ltf_lm.get('aktif_eql')if g else ltf_lm.get('aktif_eqh')):
  dh['likidite_turu']='Taze_EQL_SSL_Havuzu'if g else'Taze_EQH_BSL_Havuzu'
 fy=d4 if g else d0
 if a6 and L(fy)>=2:
  om,on=(fy[-1][1],fy[-2][1]);mh=N(om,on)if g else M(om,on);fO=(A(om-on)<=jH*0.32 and a6<mh<=a6+qQ*1.1 and(n2<mh or _f(af,'low',-3)<mh)and d6>=a6)if g else(A(om-on)<=jH*0.32 and a6-qQ*1.1<=mh<a6 and(n1>mh or _f(af,'high',-3)>mh)and d6<=a6)
  if fO:dh['likidite_turu']='Yakin_EQL+Imbalance_Sweep'if g else'Yakin_EQH+Imbalance_Sweep';lg.append('Bull_YakinEQL_Imb_Sweep'if g else'Bear_YakinEQH_Imb_Sweep');lh.append(f'[{MTF_PERIYOT.upper()}/{LTF_PERIYOT}] Valid Bölge ({a6:.4f}) Önü Yakın EQL/EQH ({mh:.4f}) + Imbalance İğneyle Süpürüldü! (YT-Part8 & Ders-03)');li+=5
 tl_list=ltf_lm.get('trendline_ssl'if g else'trendline_bsl',[])
 if tl_list:
  x1,x2,y1,y2=tl_list[-1]
  gl=y2
  if(n2<gl and d6>gl)if g else(n1>gl and d6<gl):
   if dh['likidite_turu']=='YOK':dh['likidite_turu']='Trendline_Liquidity_Sweep'if g else'Bear_Trendline_Liquidity_Sweep'
   lg.append('Bull_TrendlineLiq_SFP'if g else'Bear_TrendlineLiq_SFP');lh.append(f'[{LTF_PERIYOT}] 3-Temaslı Trend Çizgisi Likiditesi ({gl:.4f}) iğneyle süpürüldü ve içeride kapandı! (16,22.pdf, YT-Part8 & Ders-01)');li+=4
 if L(Z)>0 and(dh['sfp_durumu']!='YOK'or'Sweep'in str(dh['likidite_turu'])):dh['akis_protokolu_onay']=True;lg.append('AkisProtokolu_POI+LiqSweep'if g else'Bear_AkisProtokolu_POI+LiqSweep');lh.append(f"[{MTF_PERIYOT.upper()}/{LTF_PERIYOT}] 4 Adımlı Akış & ICT A+ Protokolü: Likidite/IDM Süpürmesi + Taze POI -> İlk Engel: {dh['internal_ilk_engel_hedefi']}, Ext Hedef (BSL/SSL): {dh['external_likidite_hedefi']} (YT-Part8 & Ders-10)");li+=4
 return(li,lg,lh,dh)
def range_po3_tt3_analizi(df,z,C,a='1H',B='BULLISH'):
 hy,fP,iH,cX=([],[],[],None);fg={'range_aktif':False,'r_low':None,'r_high':None,'r_050_avg':None,'r_025':None,'r_075':None,'dev_272_ust':None,'dev_272_alt':None,'dev_500_ust':None,'dev_500_alt':None,'avg_050_saygi':False,'range_modu':'YOK','tt3_durumu':'YOK','asya_monday_po3':'YOK','dinamit_hedef':False}
 if L(df)<26:return(hy,cX,fP,iH,fg)
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);aa,ar=(z.get('highs',[]),z.get('lows',[]));g=B=='BULLISH';aX='Bullish'if g else'Bearish';aE=''if g else'Bear_';qR=df.iloc[-28:-5];hc,cx=(F(qR['high'].max()),F(qR['low'].min()));fh=hc-cx;qS=sum((1 for _,v in aa[-5:]if A(v-hc)<=E*0.45));qT=sum((1 for _,v in ar[-5:]if A(v-cx)<=E*0.45));de=bb if g else bc
 if E*1.6<=fh<=E*9.5 and qS+qT>=3:
  hW,mY,mZ=(cx+fh*0.5,cx+fh*0.25,cx+fh*0.75);ri,rj=(cx+fh*1.272,cx-fh*0.272);rk,rl,rm,rn=(cx+fh*1.414,cx+fh*1.618,cx-fh*0.414,cx-fh*0.618);pS,pT=(cx+fh*1.5,cx-fh*0.5);q3=sum((1 for k in G(M(2,L(df)-26),L(df)-3)if A(_f(df,'close',k)-hW)<=E*0.25 or A(_f(df,'low',k)-hW)<=E*0.18 or A(_f(df,'high',k)-hW)<=E*0.18))>=3;fg.update({'range_aktif':True,'r_low':R(cx,5),'r_high':R(hc,5),'r_050_avg':R(hW,5),'r_025':R(mY,5),'r_075':R(mZ,5),'dev_272_ust':R(ri,5),'dev_272_alt':R(rj,5),'dev_500_ust':R(pS,5),'dev_500_alt':R(pT,5),'avg_050_saygi':q3,'dinamit_hedef':bool((qS>=2 if g else qT>=2)and L(C)>0)});oo,op=(F(df['low'].iloc[-6:-1].min()),F(df['high'].iloc[-6:-1].max()));eP=rj if g else ri;n4=cx if g else hc
  if A(de-eP)<=E*0.35 and(ak>=cx if g else ak<=hc):fg['range_modu']=f'{aE}RangeDev_272_SFP';hy.append(f'{a}_{aE}RangeDev_272_SFP');fP.append(f'[{a}] {aX} Range 272 Devyasyon İğne/SFP Dönüşü ({eP:.4f} -> Sınır:{n4:.4f}, Avg:{hW:.4f}) (24,25.pdf & YT-Part9)');iH.append(('BB/FL',L(df)-4,N(eP,n4),M(eP,n4)));cX=eP-E*0.25 if g else eP+E*0.25
  elif(rn-E*0.2<=bb<=rm+E*0.2 and ak>=pT)if g else(rk-E*0.2<=bc<=rl+E*0.2 and ak<=pS):qv,rJ,rK=(pT,rn,rm)if g else(pS,rk,rl);fg['range_modu']=f'{aE}RangeDev_414_618_ABCD';hy.append(f'{a}_{aE}RangeDev_414_618_ABCD');fP.append(f'[{a}] {aX} Range 414/500/618 Yarım Devyasyon (AB=CD) + POI Dönüşü ({qv:.4f}) (YT-Part9)');iH.append(('OB',L(df)-4,rJ,rK));cX=rJ-E*0.25 if g else rK+E*0.25
  q4=sum((1 for k in G(-6,-2)if(_f(df,'low',k)<cx if g else _f(df,'high',k)>hc)));d7=(F(df['high'].iloc[-14:-5].max())>hc)if g else(F(df['low'].iloc[-14:-5].min())<cx);d8=(oo<cx and ak>cx and cx-E*0.18<=bb<=mY+E*0.12)if g else(op>hc and ak<hc and mZ-E*0.12<=bc<=hc+E*0.18)
  if d8:pU=f'{aE}PO3_Igne+Devyasyon_ReEntry'if d7 and q4>=2 else f'{aE}PO3_Box_ReEntry_Test'if q4>=2 else f'{aE}Range_ReEntry_Test';fg['range_modu']=pU;hy.append(f'{a}_{pU}');fP.append(f'[{a}] {aX} {pU}: Range sınırı ({n4:.4f}) manipülasyonu sonrası içeri girildi ve sınır testi tamamlandı! (25.pdf & YT-Part9)');iH.append(('BB/FL',L(df)-5,oo if g else mZ,mY if g else op));cX=(oo if cX is None else N(cX,oo))if g else(op if cX is None else M(cX,op))
  if q3 and A(de-hW)<=E*0.28 and(ak>=hW if g else ak<=hW)and L(C)>0:fg['range_modu']=f'{aE}Range_050_AvgPrice_Kalp_POI';hy.append(f'{a}_{aE}Range_050_AvgPrice_POI');fP.append(f"[{a}] {aX} Range'in Kalbi 0.50 Average Price ({hW:.4f}) + Taze POI Onayı (YT-Part9)");cX=(mY if cX is None else N(cX,mY))if g else(mZ if cX is None else M(cX,mZ))
 oT=ar if g else aa
 if L(oT)>=2:
  (qp,e9),(r8,cj)=(oT[-2],oT[-1]);d9=(e9-cj)if g else(cj-e9)
  if 0<d9<=E*1.1 and(A(de-e9)<=E*0.32 or A(de-cj)<=E*0.28)and(ak>=cj if g else ak<=cj):gm='+Imbalance'if L(C)>0 else'';gn=f"{('Bull' if g else 'Bear')}_TT3_ThreeTap{gm}";fg['tt3_durumu']=gn;hy.append(f'{a}_{gn}');fP.append(f'[{a}] {aX} Three Tap Setup (TT3: 1.Temas {e9:.4f} -> 2.Temas Sweep {cj:.4f} -> 3.Temas Giriş{gm}) (27.pdf & YT-Part9)');iH.append(('QML',qp,N(e9,cj),M(e9,cj)));cX=(cj-E*0.25 if cX is None else N(cX,cj-E*0.25))if g else(cj+E*0.25 if cX is None else M(cX,cj+E*0.25))
 if'timestamp'in df.columns:
  try:
   e6=pd.to_datetime(df['timestamp'],unit='ms',utc=True);oq=e6.iloc[-2];ro=int(oq.hour);pV=df.loc[(e6.dt.date==oq.date())&(e6.dt.hour<6)]
   if L(pV)>=3 and 6<=ro<=17:
    nw,nx=(F(pV['high'].max()),F(pV['low'].min()));gC=nw-nx
    if E*0.8<=gC<=E*4.5:
     jt='Londra_Killzone'if ro<=11 else'NY_Killzone';ju=df.loc[(e6.dt.date==oq.date())&(e6.dt.hour>=6)];ih=(F(ju['low'].min())<nx and ak>nx and bb<=nx+gC*0.5)if g else(F(ju['high'].max())>nw and ak<nw and bc>=nw-gC*0.5)
     if ih:rT=f"Asya_{jt}_{('Bull' if g else 'Bear')}_PO3";fg['asya_monday_po3']=rT;hy.append(f'{a}_{rT}');fP.append(f'[{a}] Asya Range ({nx:.4f}-{nw:.4f}) {jt} Manipülasyonu & PO3 İçeri Giriş! (26.pdf & YT-Part9)')
   pW=df.loc[e6.dt.weekday==0]
   if oq.weekday()in(1,2,3,4)and L(pW)>=3:
    oL,oM=(F(pW['high'].max()),F(pW['low'].min()));kK=(F(df['low'].iloc[-8:-1].min())<oM and ak>oM and A(bb-oM)<=E*0.8)if g else(F(df['high'].iloc[-8:-1].max())>oL and ak<oL and A(bc-oL)<=E*0.8)
    if kK:gN=f"Monday_Range_{('Bull' if g else 'Bear')}_PO3";fg['asya_monday_po3']=gN;hy.append(f'{a}_{gN}');fP.append(f'[{a}] Monday Range ({oM:.4f}-{oL:.4f}) Devyasyon Süpürmesi & PO3 İçeri Giriş! (YT-Part9)')
  except X:pass
 return(hy,cX,fP,iH,fg)
def bobin_atnali_mw_analizi(df,z,C,a='1H',B='BULLISH'):
 cy,b9,cz,aL=([],[],[],None);bQ={'bobin_durumu':'YOK','bobin_alt':None,'bobin_ust':None,'atnali_testere':'YOK','mw_modeli':'YOK','momentum_marubozu':'YOK','yingyang_hidden_base':'YOK','giris_onay_tipi':'YOK'}
 if L(df)<24:return(cy,aL,b9,cz,bQ)
 bb,bc,ak,pn=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2),_f(df,'open',-2));E=M(_f(df,'atr',-2),ak*0.001);aa,ar=(z.get('highs',[]),z.get('lows',[]));g=B=='BULLISH';aX='Bullish'if g else'Bearish';aE=''if g else'Bear_';de=bb if g else bc
 for i in G(M(4,L(df)-26),L(df)-3):
  if i+3>=L(df)-1:break
  iI=[1 if _f(df,'close',i+q_i)>=_f(df,'open',i+q_i)else-1 for q_i in G(4)];bU=M(M(_f(df,'open',i+q_i),_f(df,'close',i+q_i))for q_i in G(4));bV=N(N(_f(df,'open',i+q_i),_f(df,'close',i+q_i))for q_i in G(4));mi=bU-bV;cY=all((iI[k]!=iI[k+1]for k in G(L(iI)-1)))or(L(set(iI[:3]))==2 and iI[0]==iI[2]and iI[0]!=iI[1])
  if cY and E*0.18<=mi<=E*1.85:
   bQ['bobin_alt'],bQ['bobin_ust']=(R(bV,5),R(bU,5));pX=i+3
   if pX>=L(df)-4:
    ia=(ak>bU and(bb<=bU+E*0.18 or _f(df,'low',-3)<=bU+E*0.18))if g else(ak<bV and(bc>=bV-E*0.18 or _f(df,'high',-3)>=bV-E*0.18))
    if ia:gO=f'{aE}Bobin_Cozulme_IgneTest';bQ['bobin_durumu']=gO;cy.append(f'{a}_{gO}');b9.append(f'[{a}] {aX} Bobin (3-4 Mumlu Gövde Kümesi: {bV:.4f}-{bU:.4f}) Çözüldü & Anlık İğne Testi Tamamlandı! (28-bobinler.pdf & YT-Part10)');cz.append(('BB/FL',i,bV,bU));aL=(bV-E*0.2 if aL is None else N(aL,bV-E*0.2))if g else(bU+E*0.2 if aL is None else M(aL,bU+E*0.2))
   else:
    gj=any((_f(df,'close',r_i)>bU+E*0.35 if g else _f(df,'close',r_i)<bV-E*0.35 for r_i in G(pX+1,L(df)-2)));qa=any((_f(df,'close',r_i)<bV-E*0.15 if g else _f(df,'close',r_i)>bU+E*0.15 for r_i in G(pX+1,L(df)-2)))
    if gj and not qa and bV-E*0.2<=de<=bU+E*0.2 and(ak>=bV if g else ak<=bU):gO=f'{aE}Bobin_Bolge_Testi_POI';bQ['bobin_durumu']=gO;cy.append(f'{a}_{gO}');b9.append(f'[{a}] {aX} Bobin Bölge Testi (HTF Bobin = LTF Range Gövde Kutusu: {bV:.4f}-{bU:.4f}) Taze POI Olarak Çalıştı! (28.pdf & YT-Part10)');cz.append(('OB',i,bV,bU));aL=(bV-E*0.2 if aL is None else N(aL,bV-E*0.2))if g else(bU+E*0.2 if aL is None else M(aL,bU+E*0.2))
    for r9 in G(pX+1,L(df)-2):
     nE,nF,k2,k3=(_f(df,'open',r9),_f(df,'close',r9),_f(df,'high',r9),_f(df,'low',r9));ep=(k3<bV-E*0.15 and N(nE,nF)>=bV and ak>bU)if g else(k2>bU+E*0.15 and M(nE,nF)<=bU and ak<bV)
     if ep:nG=f'{aE}Testere_DerinIgne_Bobin';bQ['atnali_testere']=nG;cy.append(f'{a}_{nG}');b9.append(f'[{a}] {aX} Testere (Bobin [{bV:.4f}-{bU:.4f}] Derin İğneyle Yıpratıldı ve Karşı Yöne Dolduruldu!) (28.pdf & YT-Part10)');aL=(k3-E*0.15 if aL is None else N(aL,k3-E*0.15))if g else(k2+E*0.15 if aL is None else M(aL,k2+E*0.15));break
 for k in G(M(4,L(df)-16),L(df)-2):
  if k+3>=L(df)-1:break
  hX,m4,a0,bi,br,a8,m5,hY=(_f(df,'open',k),_f(df,'close',k),_f(df,'open',k+1),_f(df,'close',k+1),_f(df,'open',k+2),_f(df,'close',k+2),_f(df,'open',k+3),_f(df,'close',k+3));pY,pZ=(M(_f(df,'high',k),_f(df,'high',k+1)),N(_f(df,'low',k),_f(df,'low',k+1)));p0,p5=(M(_f(df,'high',k+2),_f(df,'high',k+3)),N(_f(df,'low',k+2),_f(df,'low',k+3)));eQ=(m4<hX and bi<=a0 and a8>=br and hY>m5 and hY>M(hX,a0))if g else(m4>hX and bi>=a0 and a8<=br and hY<m5 and hY<N(hX,a0))
  if eQ:
   go='Extended_AtNali'if(p5<pZ if g else p0>pY)else'ShortFormed_AtNali'if(p5>pZ+E*0.05 if g else p0<pY-E*0.05)else'Simple_AtNali';lt=M(a0,a8)if g else N(a0,a8);kw=N(pZ,p5)if g else M(pY,p0)
   if A(de-lt)<=E*0.45 and(ak>=lt if g else ak<=lt):jk=f'{aE}{go}_U_Turn';bQ['atnali_testere']=jk;cy.append(f'{a}_{jk}');b9.append(f'[{a}] {aX} {go} (4 Mumlu U-Dönüşü = LTF M/W Kırılımı | Giriş:{lt:.4f}, Stop:{kw:.4f}) (28,29.pdf & YT-Part10)');cz.append(('QML',k+1,N(kw,lt),M(kw,lt)));aL=(kw-E*0.15 if aL is None else N(aL,kw-E*0.15))if g else(kw+E*0.15 if aL is None else M(aL,kw+E*0.15));break
 fz=ar if g else aa
 if L(fz)>=2:
  (qq,da),(sa,ck)=(fz[-2],fz[-1]);pp=(ck-da)if g else(da-ck)
  if A(pp)<=E*1.35 and A(de-ck)<=E*0.42 and(ak>=ck if g else ak<=ck):p6='W'if g else'M';p7=f'Simple_{p6}_Trade'if A(pp)<=E*0.22 else f'ShortFormed_{p6}_2ndLeg'if pp>0 else f'Extended_{p6}_TurtleSoup_SFP';kx=z.get('ote_bull_mu'if g else'ote_bear_mu',False);p8=('+OTE'if kx else'')+('+FVG'if L(C)>0 else'');bQ['mw_modeli']=f'{p7}{p8}';cy.append(f'{a}_{p7}{p8}');b9.append(f'[{a}] {aX} {p7}{p8} (1.Bacak:{da:.4f} -> 2.Bacak Giriş:{ck:.4f} | HTF At Nalı Karşılığı) (29-m-w-trade.pdf & YT-Part10)');cz.append(('QML',qq,N(da,ck),M(da,ck)));aL=(N(da,ck)-E*0.22 if aL is None else N(aL,N(da,ck)-E*0.22))if g else(M(da,ck)+E*0.22 if aL is None else M(aL,M(da,ck)+E*0.22))
 for j in G(M(3,L(df)-18),L(df)-2):
  c8,c9,hZ,h4=(_f(df,'open',j),_f(df,'close',j),_f(df,'high',j),_f(df,'low',j));j2=A(c9-c8);ot,ou=(hZ-M(c8,c9),N(c8,c9)-h4);ml=(c9>c8)if g else(c9<c8);cZ=ml and j2>=E*0.65 and((ou>=j2*0.35 and ou>ot*1.6)if g else(ot>=j2*0.35 and ot>ou*1.6))
  if cZ:
   ly,lz=(h4,c8)if g else(c8,hZ)
   if ly-E*0.18<=de<=lz+E*0.18 and(ak>=ly if g else ak<=lz):jm=f'{aE}TersIgneli_Momentum_POI';bQ['momentum_marubozu']=jm;cy.append(f'{a}_{jm}');b9.append(f'[{a}] {aX} Ters İğneli Momentum Mumu İğne İçi Gizli POI Testi ({ly:.4f}-{lz:.4f}) (35.pdf & YT-Part10)');cz.append(('BB/FL',j,ly,lz));aL=(ly-E*0.15 if aL is None else N(aL,ly-E*0.15))if g else(lz+E*0.15 if aL is None else M(aL,lz+E*0.15));break
  if j+1<L(df)-2:
   fa,nl,kL,kM=(_f(df,'open',j+1),_f(df,'close',j+1),_f(df,'high',j+1),_f(df,'low',j+1));h5=(c9>c8 and nl>fa and ot>E*0.18 and fa-kM>E*0.18 and kM<=hZ)if g else(c9<c8 and nl<fa and ou>E*0.18 and kL-fa>E*0.18 and kL>=h4)
   if h5:
    lD,lE=(N(kM,c9),M(hZ,fa))if g else(N(h4,fa),M(kL,c9))
    if lD-E*0.15<=de<=lE+E*0.15 and(ak>=lD if g else ak<=lE):jv=f'{aE}YingYang_HiddenBase_Test';bQ['yingyang_hidden_base']=jv;cy.append(f'{a}_{jv}');b9.append(f'[{a}] {aX} Ying-Yang (Hidden Base İğne Kesişimi: {lD:.4f}-{lE:.4f}) Bölge Testi! (35-ying-yang.pdf & YT-Part10)');cz.append(('BB/FL',j,lD,lE));aL=(lD-E*0.15 if aL is None else N(aL,lD-E*0.15))if g else(lE+E*0.15 if aL is None else M(aL,lE+E*0.15));break
 eR,eS,pq,pr=(_f(df,'open',-3),_f(df,'close',-3),_f(df,'high',-3),_f(df,'low',-3));eT,eU,ps,pt=(_f(df,'open',-2),_f(df,'close',-2),_f(df,'high',-2),_f(df,'low',-2));eH=A(eU-eT);iJ,iK=(ps-M(eT,eU),N(eT,eU)-pt);mm,mo=(pq-M(eR,eS),N(eR,eS)-pr);dV=(eU>eT and eH>=E*0.48 and iK<=eH*0.08 and(eS<eR and mo<=A(eS-eR)*0.12 or iJ<=eH*0.12))if g else(eU<eT and eH>=E*0.48 and iJ<=eH*0.08 and(eS>eR and mm<=A(eS-eR)*0.12 or iK<=eH*0.12))
 if dV:iL=f"{('Bull' if g else 'Bear')}_Istekli_Marubozu";bQ['momentum_marubozu']=iL;cy.append(f'{a}_{iL}');b9.append(f'[{a}] {aX} İstekli Mum / Marubozu Open (Bölgeden İğnesiz Sıfır Mukavemetli Çıkış: {eT:.4f}->{eU:.4f}) (35.pdf & YT-Part10)')
 return(cy,aL,b9,cz,bQ)
def engulf_pinbar_analizi(df,z,C,a='1H',B='BULLISH'):
 bW,bA,dq,aS=([],[],[],None);bl={'engulf_outside_mera':'YOK','star_turu':'YOK','pinbar_spike':'YOK','railroad_tracks':'YOK','bosalt_doldur_kademe':'YOK','kombo_patern':'YOK','sentetik_mum':'YOK'}
 if L(df)<20:return(bW,aS,bA,dq,bl)
 bb,bc,ak,pn=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2),_f(df,'open',-2));E=M(_f(df,'atr',-2),ak*0.001);g=B=='BULLISH';aX='Bullish'if g else'Bearish';aE='Bull'if g else'Bear';de=bb if g else bc;m0,m1,m2,m3=(df.iloc[-5],df.iloc[-4],df.iloc[-3],df.iloc[-2]);o0,c0,h0,l0,o1,c1,h1,l1=(*_r(m0,'open','close','high','low'),*_r(m1,'open','close','high','low'));o2,c2,h2,l2,o3,c3,h3,l3=(*_r(m2,'open','close','high','low'),*_r(m3,'open','close','high','low'));g1,g2,g3=(A(c1-o1),A(c2-o2),A(c3-o3));mq,mr,n5,n6=(M(o2,c2),N(o2,c2),M(o3,c3),N(o3,c3));pv,pw,n7,n8=(h2-mq,mr-l2,h3-n5,n6-l3);oU=(c2<o2 and c3>o3 and n5>=mq and n6<=mr)if g else(c2>o2 and c3<o3 and n5>=mq and n6<=mr);oV=h3>=h2 and l3<=l2 and(h3>h2 or l3<l2)and(c3>o3 if g else c3<o3);hn=h3>=h2 and l3<=l2 and((n8>=g2*0.75 and mr<=n6 and l3<l2 and c3>o3)or(c2<o2 and c3>h2 and l3<=l2)if g else(n7>=g2*0.75 and mq>=n5 and h3>h2 and c3<o3)or(c2>o2 and c3<l2 and h3>=h2))
 if hn:ad=f'{aE}_MeraMera_Outside_QML';bl['engulf_outside_mera']=ad;bW.append(f'{a}_{ad}');bA.append(f'[{a}] {aX} Mera Mera (Outside Bar + İğne İçi Gövde Yutuşu = LTF Gizli QML) (30.pdf & YT-Part11)');dq.append(('QML',L(df)-3,l3 if g else mr,mq if g else h3));aS=l3-E*0.18 if g else h3+E*0.18
 elif oU and oV:ad=f'{aE}_Engulf+Outside_Super';bl['engulf_outside_mera']=ad;bW.append(f'{a}_{ad}');bA.append(f'[{a}] {aX} Çifte Güçlü Engulf + Outside Bar (Hem Gövde Hem High-Low Yutuldu!) (30.pdf & YT-Part11)');dq.append(('OB',L(df)-3,N(l2,l3)if g else o2,o2 if g else M(h2,h3)));aS=N(l2,l3)-E*0.18 if g else M(h2,h3)+E*0.18
 elif oU:gD=g3>=g2*1.45 and g3>=E*0.45;ad=f"{aE}_{('Kaliteli_Imb_Engulf' if gD else 'Weak_Engulf')}";bl['engulf_outside_mera']=ad;bW.append(f'{a}_{ad}');bA.append(f'[{a}] {aX} {ad} (Zıt Renkli Gövde Yutuşu: {o3:.4f}->{c3:.4f}) (30.pdf & YT-Part11)');aS=N(l2,l3)-E*0.18 if g else M(h2,h3)+E*0.18
 elif oV:ad=f'{aE}_OutsideBar_HL';bl['engulf_outside_mera']=ad;bW.append(f'{a}_{ad}');bA.append(f'[{a}] {aX} Outside Bar (High-Low Yutuşu: {l3:.4f}-{h3:.4f}) (30.pdf & YT-Part11)');aS=l3-E*0.18 if g else h3+E*0.18
 jI=(c1<o1 and g1>=E*0.4 and g2<=g1*0.5 and c3>o3)if g else(c1>o1 and g1>=E*0.4 and g2<=g1*0.5 and c3<o3)
 if jI:
  q5=(c3>=o1)if g else(c3<=o1);j3=(c3>=o1-g1*0.35)if g else(c3<=o1+g1*0.35)
  if q5 or j3:p9=f"{aE}_{('Strong_Engulf_Star' if q5 else 'Railroad_Star_70pct')}";bl['star_turu']=p9;bW.append(f'{a}_{p9}');bA.append(f"[{a}] {aX} {('Sabah' if g else 'Akşam')} Yıldızı ({p9}: 3 Mum Toplamı = Sentetik Pinbar) (YT-Part11)");oB,oC=(N(l1,l2,l3),M(h1,h2,h3));aS=(oB-E*0.18 if aS is None else N(aS,oB-E*0.18))if g else(oC+E*0.18 if aS is None else M(aS,oC+E*0.18))
 lO=(c2<o2 and c3>o3 and g2>=E*0.45 and g2*0.62<=g3<g2*1.02)if g else(c2>o2 and c3<o3 and g2>=E*0.45 and g2*0.62<=g3<g2*1.02)
 if lO:n9=(N(l2,l3)+M(h2,h3))/2.0;ad=f'{aE}_Railroad_Tracks_Pinbar';bl['railroad_tracks']=ad;bl['sentetik_mum']=f'2Mum_RR_Pinbar(50%:{n9:.4f})';bW.append(f'{a}_{ad}');bA.append(f'[{a}] {aX} Railroad Tracks (%65-%98 Gövde Dönüşü = Sentetik Pinbar | %50 Seviyesi: {n9:.4f}) (31.pdf & YT-Part11)');dq.append(('BB/FL',L(df)-3,N(l2,l3)if g else n9,n9 if g else M(h2,h3)));aS=(N(l2,l3)-E*0.18 if aS is None else N(aS,N(l2,l3)-E*0.18))if g else(M(h2,h3)+E*0.18 if aS is None else M(aS,M(h2,h3)+E*0.18))
 jJ=(n8>=M(g3*1.55,E*0.32)and n8>n7*1.35)if g else(n7>=M(g3*1.55,E*0.32)and n7>n8*1.35);k6=(pw>=M(g2*1.55,E*0.32)and pw>pv*1.35)if g else(pv>=M(g2*1.55,E*0.32)and pv>pw*1.35)
 if jJ or k6:mt=((l3+h3)/2.0)if jJ else((l2+h2)/2.0);eV=(c3>=o3 if jJ else c2>=o2)if g else(c3<=o3 if jJ else c2<=o2);iM='50pct_Retest'if k6 and not jJ and(l2<=bb<=mt+E*0.12 if g else mt-E*0.12<=bc<=h2)and(ak>=mt if g else ak<=mt)else'Break_Entry'if k6 and(ak>h2 if g else ak<l2)else'Kapanis_Onayli'if eV else'Spike_Tepki';iN=f'{aE}_Pinbar_{iM}';bl['pinbar_spike']=iN;bW.append(f'{a}_{iN}');bA.append(f'[{a}] {aX} Reversal Pinbar ({iM} | %50 HL:{mt:.4f}) (31-spike-pinbar.pdf & YT-Part11)');hz=(N(l2,l3)-E*0.18)if g else(M(h2,h3)+E*0.18);aS=(hz if aS is None else N(aS,hz))if g else(hz if aS is None else M(aS,hz))
 if k6 and jJ:iO=f'{aE}_Double_Pinbar_Combo';bl['kombo_patern']=iO;bW.append(f'{a}_{iO}');bA.append(f'[{a}] {aX} Double Pinbar (Çift İğne Reddiyesi Kombo Patern!) (YT-Part11)')
 elif k6 and(oU or oV):iO=f'{aE}_Pinbar+Engulf_Outside_Combo';bl['kombo_patern']=iO;bW.append(f'{a}_{iO}');bA.append(f'[{a}] {aX} Pinbar + Engulf/Outside Bar Çifte Kanıt Kombo Patern! (YT-Part11)')
 elif(jJ and h3<=h2 and l3>=l2)or(k6 and h3<=h2 and l3>=l2 and(c3>o3 if g else c3<o3)):iO=f'{aE}_Pinbar+InsideBar_Combo';bl['kombo_patern']=iO;bW.append(f'{a}_{iO}');bA.append(f'[{a}] {aX} Pinbar + Inside Bar Kombo Patern! (YT-Part11)')
 for k in G(M(4,L(df)-14),L(df)-2):
  ko,kc,kh,kl=(_f(df,'open',k),_f(df,'close',k),_f(df,'high',k),_f(df,'low',k));kg=A(kc-ko);s_k=M(0,k-4);fQ=M((_f(df,'high',q_k)-M(_f(df,'open',q_k),_f(df,'close',q_k)))for q_k in G(s_k,k));hA=M(_f(df,'high',q_k)for q_k in G(s_k,k));fR=M((N(_f(df,'open',q_k),_f(df,'close',q_k))-_f(df,'low',q_k))for q_k in G(s_k,k));hB=N(_f(df,'low',q_k)for q_k in G(s_k,k));fS=(kc>ko and kg>=E*0.58 and fQ>=E*0.22 and kc>=hA-E*0.08)if g else(kc<ko and kg>=E*0.58 and fR>=E*0.22 and kc<=hB+E*0.08)
  if fS:
   if k==L(df)-2:nm=f'{aE}_BosaltDoldur_Kademe2_Doldurma';bl['bosalt_doldur_kademe']=nm;bW.append(f'{a}_{nm}');bA.append(f'[{a}] {aX} Boşalt-Doldur (2.Kademe: İğnelenmiş Bölge Momentum Mumla Dolduruldu!) (32.pdf & YT-Part11)');aS=(ko-E*0.18 if aS is None else N(aS,ko-E*0.18))if g else(ko+E*0.18 if aS is None else M(aS,ko+E*0.18));break
   elif(ko-E*0.12<=bb<=kc and ak>=ko)if g else(kc<=bc<=ko+E*0.12 and ak<=ko):nm=f'{aE}_BosaltDoldur_Kademe3_TersIgne_Sniper';bl['bosalt_doldur_kademe']=nm;bW.append(f'{a}_{nm}');bA.append(f'[{a}] {aX} Boşalt-Doldur (3.Kademe Sniper: Dolduran Momentum Mumuna [{ko:.4f}-{kc:.4f}] Ters İğne Testi!) (32-bosalt-doldur.pdf & YT-Part11)');dq.append(('BB/FL',k,N(ko,kc),M(ko,kc)));aS=(ko-E*0.18 if aS is None else N(aS,ko-E*0.18))if g else(ko+E*0.18 if aS is None else M(aS,ko+E*0.18));break
 if bl['sentetik_mum']=='YOK':
  ky,kA,m6,m7=(o2,c3,M(h2,h3),N(l2,l3));mu=A(kA-ky);gp,gq=(N(ky,kA)-m7,m6-M(ky,kA))
  if(gp>=M(mu*1.6,E*0.35)and gp>gq*1.4)if g else(gq>=M(mu*1.6,E*0.35)and gq>gp*1.4):bl['sentetik_mum']=f'{aE}_2Mum_Toplam_Pinbar({(m7+m6)/2.0:.4f})'
  elif(c1>o1 and c2>o2 and c3>o3 and c3-o1>=E*1.1)if g else(c1<o1 and c2<o2 and c3<o3 and o1-c3>=E*1.1):bl['sentetik_mum']=f'{aE}_3Mum_Sentetik_Marubozu_LiqVoid'
 return(bW,aS,bA,dq,bl)
def ib_fakey_smt_analizi(df,z,C,a='1H',B='BULLISH',J='BTC/USDT'):
 ca,cA,ea=([],[],[]);fA=None;bg={'inside_bar_durumu':'YOK','fake_setup_tipi':'YOK','dvg_durumu':'YOK','smt_durumu':'YOK','dar_sl_4r':False,'gelis_atr':0.0,'mb_high':None,'mb_low':None,'ib_high':None,'ib_low':None,'fake_idx':None}
 if L(df)<20:return(ca,fA,cA,ea,bg)
 bb,bc,ak,pn=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2),_f(df,'open',-2));eI=F(df['atr'].iloc[-10:-1].mean())if'atr'in df.columns and L(df)>=12 else M(_f(df,'atr',-2),ak*0.001);E=M(eI,ak*0.001);bg['gelis_atr']=R(E,5);g=B=='BULLISH'
 for dN in G(M(4,L(df)-16),L(df)-2):
  bm,bn,m8,m9=(_f(df,'high',dN),_f(df,'low',dN),_f(df,'open',dN),_f(df,'close',dN));c4=bm-bn
  if c4<E*0.65:continue
  iS,b3,b4=(0,-1e18,1e18)
  for j in G(dN+1,N(L(df)-1,dN+5)):
   jh,jl=(_f(df,'high',j),_f(df,'low',j))
   if jh<=bm and jl>=bn:iS+=1;b3=M(b3,jh);b4=N(b4,jl)
   else:break
  if iS==0:continue
  fU=dN+iS;j4=M(b3-b4,1e-9);bO=j4/M(c4,1e-9);uF=m9>m8 and b4>=bn+c4*0.42;aF=m9<m8 and b3<=bm-c4*0.42;dr=bO<=0.55 and((uF if g else aF)or bO<=0.38);aI=any((dN-3<=fi<=dN for fi in C));bg['mb_high'],bg['mb_low'],bg['ib_high'],bg['ib_low']=(R(bm,5),R(bn,5),R(b3,5),R(b4,5))
  if fU<L(df)-1:
   bp=fU+1;db,bL,cK,cM=(_f(df,'open',bp),_f(df,'close',bp),_f(df,'high',bp),_f(df,'low',bp));kB=cK-cM
   if(bL>bm if g else bL<bn):
    fb=kB>E*1.65;fc=(bn<=bb<=bm+E*0.18 and ak>=b4)if g else(bn-E*0.18<=bc<=bm and ak<=b3)
    if bp==L(df)-2 and not fb or(fc and bp<L(df)-2):
     iE=f"{a}_{('Kaliteli_Flama_InsideBar_Brk' if dr else 'InsideBar_Breakout_Retest' if bp<L(df)-2 else 'InsideBar_Breakout_Close')}"
     if iE not in ca:
      ca.append(iE);bg['inside_bar_durumu']=f"{iE}({iS}Bar,Oran:%{bO*100:.0f})"
      if not aI:bg['dar_sl_4r']=True;ca.append(f'{a}_InsideBar_DarSL_4R')
      cA.append(f"[{a}] {('Bullish' if g else 'Bearish')} {iE} (AnaBar:{bn:.4f}-{bm:.4f}, {iS}x InsideBar Oran:%{bO*100:.0f}{', Flama Konumu' if uF or aF else ''}{', Arkada Açık Imb Yok -> Dar SL 2R->4R!' if not aI else ''}) (33-inside-bar.pdf & YT-Part12)");ea.append(('IB_MB',dN,bn,bm));fA=(b4 if not aI else bn)if g else(b3 if not aI else bm)
   gE,gF=(cK-M(bL,db),N(bL,db)-cM)
   if(cM<bn and bL>=bn and gF>A(bL-db)*1.2)if g else(cK>bm and bL<=bm and gE>A(bL-db)*1.2):
    cr=(bL>=b4)if g else(bL<=b3);uK=(bL>b3)if g else(bL<b4)
    if cr and(bp>=L(df)-3 or(bn<=bb<=bm and ak>=b4 if g else bn<=bc<=bm and ak<=b3)):
     fT='Kuralli_Pinbarli_FakeSetup_GucluUst'if uK else'Kuralli_Pinbarli_FakeSetup_IcKapanis';jw=f'{a}_{fT}'
     if jw not in ca:ca.append(jw);bg['fake_setup_tipi'],bg['fake_idx']=(fT,bp);oO=(cM+cK)/2.0;gS='%50 İğne Retest'if(cM<=bb<=oO and ak>=oO if g else oO<=bc<=cK and ak<=oO)else'Pinbar Kapanış/Kırılım';cA.append(f"[{a}] {('Bullish' if g else 'Bearish')} {fT}: Ana Bar ({(bn if g else bm):.4f}) iğneyle süpürüldü ve Inside Bar {('üstünde/altında kırarak' if uK else 'içinde')} kurallı kapandı! Giriş: {gS} (34-fake-setup.pdf & YT-Part12)");ea.append(('FAKEY_PIN',dN,N(bn,cM),M(bm,cK)));fA=cM if g else cK
    elif not cr and bp>=L(df)-3:bg['fake_setup_tipi']='Kuralsiz_Pinbarli_FakeSetup_Zayif'
   if bp+1<L(df):
    fd=bp+1;kW,dc,ny,nz=(_f(df,'open',fd),_f(df,'close',fd),_f(df,'high',fd),_f(df,'low',fd));nA,nB=(A(dc-kW),A(bL-db));gG=(bL<db and dc>kW)if g else(bL>db and dc<kW);dJ=(cM<bn and dc>=b4 and(dc>=b3 or nA>=nB*0.75))if g else(cK>bm and dc<=b3 and(dc<=b4 or nA>=nB*0.75))
    if gG and dJ and(fd>=L(df)-3 or(bn<=bb<=bm and ak>=b4 if g else bn<=bc<=bm and ak<=b3)):
     aK='Engulf_Outside'if(dc>=db if g else dc<=db)else'Railroad_AtNali';jx=f'{a}_Pinbarsiz_FakeSetup_{aK}'
     if jx not in ca:ca.append(jx);bg['fake_setup_tipi'],bg['fake_idx']=(f'Pinbarsiz_FakeSetup_{aK}_PO3',fd);cA.append(f"[{a}] {('Bullish' if g else 'Bearish')} Pinbarsız Fake Setup ({aK} / PO3 Box): 3.Mum Ana Barı ihlal etti, 4.Mum zıt renkle Inside Barı yutarak içeri döndü! (34-fake-setup.pdf & YT-Part12)");ea.append(('FAKEY_NOPIN',dN,N(bn,cM,nz),M(bm,cK,ny)));fA=N(cM,nz)if g else M(cK,ny)
 aa,ar=(z.get('highs',[]),z.get('lows',[]));cV=ar if g else aa
 if L(cV)>=2 and'rsi'in df.columns:
  (i1,w1),(i2,w2)=(cV[-2],cV[-1]);c1,c2=(_f(df,'close',i1),_f(df,'close',i2));bY,ci,gr,kC,gt,gu=(_f(df,'rsi',i1),_f(df,'rsi',i2),_f(df,'ao',i1),_f(df,'ao',i2),_f(df,'cvd',i1),_f(df,'cvd',i2));rO=(bY<=40.0)if g else(bY>=60.0);cp=(c2<c1*0.999 and ci>bY+1.8)if g else(c2>c1*1.001 and ci<bY-1.8);dt=(w2<w1*0.999 and((kC>gr and gr<0)or gu>gt))if g else(w2>w1*1.001 and((kC<gr and gr>0)or gu<gt));eW=A(w2-w1)/M(w1,1e-9)<=0.0038 and((ci>bY+1.5 or kC>gr)if g else(ci<bY-1.5 or kC<gr));du=(w2<w1*0.9985 if g else w2>w1*1.0015)and A(ci-bY)<=0.9;eb=(w2>w1*1.002 and ci<bY-2.0)if g else(w2<w1*0.998 and ci>bY+2.0)
  if cp or dt:
   kY='RSI_Close'if cp else'AO_CVD_Wick';dE=f'{a}_Strong_Regular_DVG_{kY}'
   if rO:dE+='+RSIOver_2_3_Ayak'
   ca.append(dE);bg['dvg_durumu']=dE;cA.append(f"[{a}] {('Pozitif (Bullish)' if g else 'Negatif (Bearish)')} Strong Regular Divergence ({kY}: RSI Kapanış {bY:.1f}->{ci:.1f}{', 1.Ayak RSI Over 2./3.Ayak Onaylı!' if rO else ''}) (38-dvg.pdf & YT-Part12)")
  elif eW:dE=f"{a}_Medium_{('IkiliDip_EQL' if g else 'IkiliTepe_EQH')}_DVG";ca.append(dE);bg['dvg_durumu']=f'{dE}(KisaInternalHedef)';cA.append(f"[{a}] Medium Regular Divergence ({('İkili Dip EQL' if g else 'İkili Tepe EQH')} + Osilatör Uyumsuzluğu -> Arkada Likidite Bıraktığı İçin Kısa/Internal Hedef Odaklı) (38-dvg.pdf & YT-Part12)")
  elif du:bg['dvg_durumu']='Weak_EsitOsilator_DVG(TercihEdilmez)'
  elif eb:bg['dvg_durumu']='Hidden_Gizli_DVG_Red(FailureSwing_Kullanilmaz)'
 eF=J.split(':')[0];rA='ETH/USDT'if eF=='BTC/USDT'else'BTC/USDT';bj=an.get(a.lower(),an.get(LTF_PERIYOT,an.get('15m',{}))).get(rA)
 if bj is not None and L(bj)>=18 and L(df)>=18:
  dv='low'if g else'high';fV=F(df[dv].iloc[-16:-6].min()if g else df[dv].iloc[-16:-6].max());fW=F(df[dv].iloc[-6:-1].min()if g else df[dv].iloc[-6:-1].max());fX=F(bj[dv].iloc[-16:-6].min()if g else bj[dv].iloc[-16:-6].max());fY=F(bj[dv].iloc[-6:-1].min()if g else bj[dv].iloc[-6:-1].max());pL=(fW<fV)if g else(fW>fV);ec=(fY<fX)if g else(fY>fX);iP=A(_f(df,'close',-2)-_f(df,'close',-6))/M(E*4.0,1e-9);mv=M(_f(bj,'atr',-2),_f(bj,'close',-2)*0.001);iQ=A(_f(bj,'close',-2)-_f(bj,'close',-6))/M(mv*4.0,1e-9);hU=M(iP,iQ)/M(N(iP,iQ),0.05)>=1.55
  if pL!=ec:sR='POIye_Takilan_DusukRiskSL'if not pL else'Likidite_Alan_Devyasyon';sE=f'{a}_SMT_{sR}';ca.append(sE);bg['smt_durumu']=f"{sE}({rA}{',HizFarki' if hU else ''})";cA.append(f"[{a}] {rA} ile {('Pozitif (Bullish)' if g else 'Negatif (Bearish)')} SMT: {('Bu parite Fresh POIye takıldı (Düşük Riskli Net Stop!), ' + rA + ' likidite aldı' if not pL else 'Bu parite likiditeyi süpürdü (Devyasyon), ' + rA + ' POIye takıldı')}{' + Hız/İvme Farkı Onaylı' if hU else ''} -> TP1: En Yakın Internal FTR/FL! (39-smt.pdf & YT-Part12)")
  elif hU:bg['smt_durumu']=f'SMT_Hiz_Farki_ErkenUyari({rA})'
 return(ca,fA,cA,ea,bg)
def entry_mtf_3r_analizi(df,z,Z,C,a='1H',B='BULLISH'):
 dw,cC,fZ=([],[],[]);eJ=None;bv={'aktif_entry_modeli':'Beklemede','istisnai_ob_durumu':'YOK','fvgli_choch_entry_alani':'YOK','zayif_choch_filtresi':'YOK','atr_stop_kalkani':'YOK','dogal_rr_orani':0.0,'mtf_ahenk_durumu':'Ahenkli','basabas_winrate':'%25 (1:3 R:R)'}
 if L(df)<20:return(dw,eJ,cC,fZ,bv)
 bb,bc,ak,pn=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2),_f(df,'open',-2));lP=F(df['atr'].iloc[-10:-1].mean())if'atr'in df.columns and L(df)>=12 else M(_f(df,'atr',-2),ak*0.001);E=M(lP,ak*0.001);g=B=='BULLISH';cb,j5,aV=(z.get('qm_meta',{}),z.get('v6_meta',{}),z.get('v12_meta',{}));g5=z.get('uc_istasyon',{});bx,eX=(z.get('strong_point'),z.get('weak_point'));co=cb.get('qml_seviyesi')
 if I(co,(int,F))and I(bx,(int,F))and L(C)>0:
  if(bx<co-E*0.35 if g else bx>co+E*0.35):
   bv['istisnai_ob_durumu']=f'Istisnai_OB({bx:.4f}_vs_QML_{co:.4f})'
   if(bx-E*0.2<=bb<=co+E*0.15 and ak>=bx)if g else(co-E*0.15<=bc<=bx+E*0.2 and ak<=bx):qr=f'{a}_Istisnai_OB_QML_Disi_Imb';dw.append(qr);eJ=bx;cC.append(f"[{a}] {('Bullish' if g else 'Bearish')} İstisnai Order Block ({bx:.4f}): QML ({co:.4f}) gerisinde açık Imbalance olduğu için OB uç noktada ayrıştı! (YT-Part13)")
 cN=z.get('internal_choch','YOK');es=L(C)>0 or any(('FVG'in p or'Imb'in p for p in Z));aT=aV.get('smt_durumu','YOK')!='YOK'or aV.get('dvg_durumu','YOK')!='YOK';fB=('BULL_STRONG_CHOCH'in cN or'BULL_IBOS'in cN)if g else('BEAR_STRONG_CHOCH'in cN or'BEAR_IBOS'in cN);fC=('BULL_WEAK_CHOCH'in cN)if g else('BEAR_WEAK_CHOCH'in cN);be,bF=(g5.get('FL'),g5.get('ITZ'))
 if fB and es:
  ed=N(be,bF)if I(be,(int,F))and I(bF,(int,F))else ak-E*0.6;ee=M(be,bF)if I(be,(int,F))and I(bF,(int,F))else ak+E*0.6;mw=f"{a}_FVGli_Guclu_CHoCH_EntryAlani{'_RetestSMT' if aT else ''}";dw.append(mw);bv['fvgli_choch_entry_alani']=f'{mw}[{ed:.4f}-{ee:.4f}]';bv['aktif_entry_modeli']='Model5_FVGli_CHoCH+RetestSMT'if aT else'Model5_FVGli_Guclu_CHoCH_EntryAlani';fZ.append(('ENTRY_ZONE',M(2,L(df)-6),ed,ee))
  if I(bF,(int,F)):eJ=(bF-E*0.35)if g else(bF+E*0.35)
  cC.append(f"[{a}] FVG'li Güçlü CHoCH Giriş Alanı (FL-ITZ-OB Entry Zone: {ed:.4f}-{ee:.4f}){' + Testte İkinci SMT/DVG Onayı!' if aT else ''} -> Stop HTF arkasına değil LTF kırılım yapısına çekildi! (41.pdf & YT-Part13)")
 elif fC:
  if L(Z)>0 and(es or aT):qs=f'{a}_AnaPOI_FVGli_ZayifCHoCH_Onay';dw.append(qs);bv['zayif_choch_filtresi']='Onayli_AnaPOI_FVGli_ZayifCHoCH';bv['aktif_entry_modeli']='Model5_AnaPOI_FVGli_Zayif_CHoCH';cC.append(f"[{a}] Ana POI İçinde FVG'li Zayıf CHoCH Onayı{' + SMT Destekli' if aT else ''}: Bölge taze ve güçlü olduğu için likiditesiz erken dönüş onaylandı! (YT-Part13)")
  else:bv['zayif_choch_filtresi']='RED_KitabinOrtasi_TersAkis_ZayifCHoCH_Tuzagi'
 elif aT and L(Z)>0:bv['aktif_entry_modeli']='Model2_FreshPOI_SMT_DVG_ErkenGiris';dw.append(f'{a}_FreshPOI_SMT_DVG_ErkenEntry');cC.append(f'[{a}] Fresh POI + SMT/DVG Destekli Erken Giriş: Kırılım beklemeden Imbalance giderildiği anda SMT onayıyla uçtan pozlanma! (YT-Part13)')
 iq=R(ak-E*1.5 if g else ak+E*1.5,5);lQ=R(ak-E*2.0 if g else ak+E*2.0,5);lR=R(ak-E*2.5 if g else ak+E*2.5,5);bv['atr_stop_kalkani']=f'1.5x:{iq}|2.0x:{lQ}(Safe)|2.5x:{lR}';jK=eJ if eJ is not None else(bx if I(bx,(int,F))else iq);dW=M(A(ak-jK),E*1.2);eu=cb.get('karsi_fresh_hedef')or eX or(ak+dW*3.2 if g else ak-dW*3.2);jL=A(F(eu)-ak);bR=R(jL/M(dW,1e-9),2);bv['dogal_rr_orani']=bR
 if bR>=3.0:dw.append(f'{a}_Dogal_3R_Ustu_Potansiyel({bR:.1f}R)');cC.append(f'[{a}] Doğal >= 3R Trade Planı Onayı ({bR:.1f}R -> Hedef: {F(eu):.4f}): Uydurma stop/TP olmadan doğal yapı >= 3R veriyor (%25 Başabaş / %30 Winrate ile +20R Kasa Disiplini)! (44,45.pdf & YT-Part13)')
 lS=cb.get('yaklasim_modeli','Standart');bv['pa_diyagrami_durumu']=f"1.Kalite({'OK' if L(Z)>0 else '-'})|2.Yaklasim({lS})|3.Giris({bv['aktif_entry_modeli']})"
 if L(Z)>0 and(bv['aktif_entry_modeli']!='Beklemede'or I(be,(int,F))or I(bF,(int,F))):dw.append(f'{a}_PA_Diyagrami_3Asama_Onay');cC.append(f"[{a}] Price Action Diyagramı 3 Aşama Onayı (OB->QML[ITZ/DP/MPL]->MagicLine/BB[B.Spot/FL]->FO/FTR | Yaklaşım: {lS} | Giriş: {bv['aktif_entry_modeli']}) (YT-Short Diyagram)")
 # Drive Video Klasörü (Ders 08, 09, 10): Discount/Premium Konumu, OTE 0.705 Golden Pocket + OB + FVG Confluence & ICT A+ 6 Şart Kontrolü
 pd_uygun=bool(z.get('discount_mu')if g else z.get('premium_mu'))
 ote_aktif=bool(z.get('ote_bull_mu')if g else z.get('ote_bear_mu'))
 f_705=F(z.get('fibo_seviyeleri',{}).get('0.705')or 0.0)
 if ote_aktif and f_705>0 and A((bb if g else bc)-f_705)<=E*0.45 and any(('OB'in p or'FVG'in p or'QML'in p for p in Z)):
  dw.append(f'{a}_OTE_705_GoldenPocket_OB_FVG');cC.append(f'[{a}] OTE 0.705 Golden Ratio ({f_705:.4f}) + OB/FVG Kusursuz Confluence! (21-fibo.pdf & Drive Video Ders-09)')
 if pd_uygun and(fB or es)and L(Z)>0 and bR>=2.0:
  aplus_sart=sum([1,int(pd_uygun),int(aT),int(fB and es),int(L(Z)>0),int(bR>=2.5)])
  bv['ict_aplus_skor']=f'{aplus_sart}/6'
  if aplus_sart>=5:
   dw.append(f'{a}_ICT_APlus_Setup_{aplus_sart}_6');cC.append(f'[{a}] ICT Akademi A+ Setup ({aplus_sart}/6 Şart: 1.HTF Yön + 2.Likidite/IDM Avı + 3.SMT + 4.Gövde MSS/Displacement + 5.Discount/Premium FVG-OB-OTE + 6.RR {bR:.1f}R) (Drive Video Ders-10)')
 return(dw,eJ,cC,fZ,bv)
def market_yapisi_ve_fibo_analizi(df,n=SWING_PENCERE):
 aa,ar,kM=kirilim_yoksa_swing_yoktur_analizi(df,n);eK=ext_int_swing_ayristir(df,aa,ar);oW=wyckoff_analizi(df,aa,ar);a5={'yon':'NOTR','bos_var_mi':False,'kirilim_tipi':'YOK','discount_mu':False,'premium_mu':False,'ote_bull_mu':False,'ote_bear_mu':False,'guclu_trend_fibo':False,'range_low_yakin':False,'range_high_yakin':False,'fibo_oran':0.5,'geri_cekilme_oran':0.5,'swing_max':0.0,'swing_min':0.0,'fibo_hedefleri':{},'fibo_seviyeleri':{},'highs':aa,'lows':ar,'external_yon':eK['external_yon'],'strong_point':eK['strong_point'],'weak_point':eK['weak_point'],'break_line_fl':eK['break_line_fl'],'uc_istasyon':eK['uc_istasyon'],'internal_yon':eK['internal_yon'],'internal_choch':eK['internal_choch'],'external_msb':eK['external_msb'],'kuru_kafa_trendline_tuzagi':eK['kuru_kafa_trendline_tuzagi'],'wyckoff_fazi':oW['wyckoff_fazi'],'wyckoff_aciklama':oW['aciklama'],'egimli_flama_mi':oW['egimli_flama_mi'],'kysy_meta':kM,'kysy_onay':kM['kysy_onay'],'elenen_highs':kM['elenen_highs'],'elenen_lows':kM['elenen_lows'],'qml_seviyesi':kM.get('qml_seviyesi'),'qml_idx':kM.get('qml_idx')}
 if L(aa)<1 or L(ar)<1:return a5
 aa_p=([aa[0]]*(3-L(aa))+list(aa))if L(aa)<3 else list(aa)
 ar_p=([ar[0]]*(3-L(ar))+list(ar))if L(ar)<3 else list(ar)
 cl=_f(df,'close',-1);(hS,H0),(gd,H1),(hf,H2)=(aa_p[-3],aa_p[-2],aa_p[-1]);(hT,L0),(ge,L1),(hg,L2)=(ar_p[-3],ar_p[-2],ar_p[-1])
 ir=(H2>H1 and L2>L1)and cl>=L2;it=L2<L1 and(cl>H2 or(H2>H1 and hf>hg));iu=L1<L0 and L2>=L1 and(cl>H2 or(H2>H1 and hf>hg));jM=cl>H2 and L2>=L1
 iv=(H2<H1 and L2<L1)and cl<=H2;iw=H2>H1 and(cl<L2 or(L2<L1 and hg>hf));ix=H1>H0 and H2<=H1 and(cl<L2 or(L2<L1 and hg>hf));jN=cl<L2 and H2<=H1
 kE=f" [Tüm Grafik Swingleri ({L(aa)}H/{L(ar)}L) | {kM['elenen_sayi']} İç Gürültü Elendi]"if kM['elenen_sayi']>0 else f" [Tüm Grafik Onaylı Swingler ({L(aa)}H/{L(ar)}L)]"
 if not kM['kysy_onay']and not(ir or it or iu or jM or iv or iw or ix or jN):a5['yon'],a5['bos_var_mi'],a5['kirilim_tipi']=('NOTR',False,'Kırılım Yok -> Swing Yok (06-no-bos-no-trade.pdf: İç Yapı Gürültüsü)')
 elif(kM['son_kirilim_yon']=='BULLISH'and not(cl<L2 and H2<H1))or((kM['son_kirilim_yon']!='BEARISH'or cl>H2)and(it or iu or ir or jM)):
  a5['yon'],a5['bos_var_mi']=('BULLISH',True)
  a5['kirilim_tipi']=(('Bullish External MSB / QML Kırılımı -> Fresh Talep OB Oluşturdu (YT-Part1,3,5)'if eK['external_msb']or L2<L1 else'Bullish Güçlü CHoCH (Likidite Alımlı Reversal -> Internal OB - YT-Part2&3)')if it else'Bullish Continue BOS / i-BOS -> Valid Demand Oluşturdu (YT-Part1,2,3)')+kE
 elif kM['son_kirilim_yon']=='BEARISH'or iw or ix or iv or jN:
  a5['yon'],a5['bos_var_mi']=('BEARISH',True)
  a5['kirilim_tipi']=(('Bearish External MSB / QML Kırılımı -> Fresh Arz OB Oluşturdu (YT-Part1,3,5)'if eK['external_msb']or H2>H1 else'Bearish Güçlü CHoCH (Likidite Alımlı Reversal -> Internal Bear OB - YT-Part2&3)')if iw else'Bearish Continue BOS / i-BOS -> Valid Supply Oluşturdu (YT-Part1,2,3)')+kE
 # Ters Yönde Fibonacci: Bullish ise Swing Low (L2 = 1) -> Swing High (H2 = 0); Bearish ise Swing High (H2 = 1) -> Swing Low (L2 = 0)
 hb,fN=(F(H2),F(L2))if F(H2)>F(L2)else(M(F(H1),F(H2)),N(F(L1),F(L2)))
 a5['swing_max'],a5['swing_min']=(hb,fN);dU=hb-fN
 if dU>0:
  j6=(cl-fN)/dU;j7=(hb-cl)/dU
  a5['fibo_oran'],a5['geri_cekilme_oran']=(R(j6,3),R(j7,3))
  a5['discount_mu'],a5['premium_mu']=(j6<=0.5,j6>0.5)
  a5['ote_bull_mu'],a5['ote_bear_mu']=(0.60<=j7<=0.886,0.60<=j6<=0.886)
  a5['guclu_trend_fibo']=bool((ir and 0.236<=j7<0.5)or(iv and 0.236<=j6<0.5))
  a5['range_low_yakin'],a5['range_high_yakin']=(j6<=0.25,j6>=0.75)
  if a5['yon']=='BULLISH':
   a5['fibo_seviyeleri']={'-0.236':R(hb+dU*0.236,5),'0':R(hb,5),'0.236':R(hb-dU*0.236,5),'0.382':R(hb-dU*0.382,5),'0.5':R(hb-dU*0.5,5),'0.618':R(hb-dU*0.618,5),'0.705':R(hb-dU*0.705,5),'0.786':R(hb-dU*0.786,5),'1':R(fN,5)}
   a5['fibo_hedefleri']={'TP1_Zero':R(hb,5),'TP2_0236':R(hb+dU*0.236,5),'TP3_Simetrik':R(hb+dU*0.618,5),'TP4_ABCD':R(hb+dU*1.0,5)}
  else:
   a5['fibo_seviyeleri']={'-0.236':R(M(0.0,fN-dU*0.236),5),'0':R(fN,5),'0.236':R(fN+dU*0.236,5),'0.382':R(fN+dU*0.382,5),'0.5':R(fN+dU*0.5,5),'0.618':R(fN+dU*0.618,5),'0.705':R(fN+dU*0.705,5),'0.786':R(fN+dU*0.786,5),'1':R(hb,5)}
   a5['fibo_hedefleri']={'TP1_Zero':R(fN,5),'TP2_0236':R(M(0.0,fN-dU*0.236),5),'TP3_Simetrik':R(M(0.0,fN-dU*0.618),5),'TP4_ABCD':R(M(0.0,fN-dU*1.0),5)}
 return a5
def poi_ve_bolge_analizi(df,z,a='1H',B='BULLISH'):
 bb,bc,ak=(_f(df,'low',-2),_f(df,'high',-2),_f(df,'close',-2));E=M(_f(df,'atr',-2),ak*0.001);aa,ar=(z['highs'],z['lows']);dP,K,az,U,px=([],[],[],None,0.0);C=set();g=B=='BULLISH'
 for i in G(M(2,L(df)-40),L(df)-2):
  bC,bD,aD,aM,cd,cc=(_f(df,'high',i-1),_f(df,'low',i-1),_f(df,'close',i),_f(df,'open',i),_f(df,'low',i+1),_f(df,'high',i+1))
  if(cd>bC and aD-aM>E*0.45)if g else(bD>cc and aM-aD>E*0.45):
   C.add(i);fo=df['low'if g else'high'].iloc[i+2:-2];kN,kO=(bC,cd)if g else(cc,bD);qa=(not fo.empty and F(fo.min())<bC-E*0.1)if g else(not fo.empty and F(fo.max())>bD+E*0.1)
   if not qa and(kN-E*0.25<=bb<=kO+E*0.15 and ak>=kN if g else kN-E*0.15<=bc<=kO+E*0.25 and ak<=kO):
    fvg_ce=(kN+kO)/2.0;ce_dokundu=A((bb if g else bc)-fvg_ce)<=E*0.22 or(kN<=ak<=kO)
    nn=f"{a}_{('FVG' if g else 'SIBI_FVG')}{'_50CE' if ce_dokundu else ''}"
    if nn not in dP:dP.append(nn);K.append(f"[{a}] Taze {('BISI' if g else 'Bearish SIBI')} FVG + %50 CE ({fvg_ce:.4f}) Mıknatıs Dönüşü ({kN:.4f}-{kO:.4f}) (19.pdf, YT-Part3 & Ders-06)");az.append(('FVG',i-1,kN,kO));U=(kN if U is None else N(U,kN))if g else(kO if U is None else M(U,kO))
  if(bD>cc and aM-aD>E*0.45 and ak>bD and cc-E*0.15<=bb<=bD+E*0.2)if g else(cd>bC and aD-aM>E*0.45 and ak<bC and bC-E*0.2<=bc<=cd+E*0.15):
   iW=f"{a}_{('IFVG' if g else 'Bear_IFVG')}";kP,kQ=(cc,bD)if g else(bC,cd)
   if iW not in dP:dP.append(iW);K.append(f"[{a}] {('Bullish' if g else 'Bearish')} Inversion FVG (IFVG Dönüşümü) (19-fvg.pdf)");az.append(('IFVG',i-1,kP,kQ));U=(kP if U is None else N(U,kP))if g else(kQ if U is None else M(U,kQ))
 pz,pA=(ar,aa)if g else(aa,ar);qU=N([h for _,h in aa[-4:]if h>ak*1.005],default=ak*1.05)if g else M([l for _,l in ar[-4:]if l<ak*0.995],default=ak*0.95)
 if L(pz)>=2:
  for bu,lu in pz[-4:]:
   if bu<2 or bu>=L(df)-3:continue
   ov=[kv for ki,kv in pA if ki<bu];e7=df.iloc[M(0,bu-1):N(L(df)-2,bu+2)]
   if g:
    gH=ov[-1]if ov else F(df['high'].iloc[:bu].max());no=F(df['high'].iloc[bu+1:-1].max())
    if no<=gH:continue
    nq=e7[e7['close']<e7['open']];aH,aJ=(lu,F(nq['high'].max())if not nq.empty else lu+E*0.5);qt=no-aH
   else:
    gH=ov[-1]if ov else F(df['low'].iloc[:bu].min());no=F(df['low'].iloc[bu+1:-1].min())
    if no>=gH:continue
    nq=e7[e7['close']>e7['open']];aH,aJ=(F(nq['low'].min())if not nq.empty else lu-E*0.5,lu);qt=aJ-no
   hi=rbr_dbd_analizi(df,bu,aH,aJ,B);qb=M(aJ,hi['imbalance_koku'])if g else N(aH,hi['imbalance_koku']);rp=2.0 if(any((bu<=sd<=bu+4 for sd in C))or hi['patlama_ayrilis'])and qt>=E*2.2 else 1.0 if qt>=E*1.5 else 0.0;jE=sum((1 for k in G(bu,N(L(df)-2,bu+6))if(_f(df,'close',k)<=aJ if g else _f(df,'close',k)>=aH)));rq=2.0 if hi['v_shape_1mum']or jE<=2 else 1.0 if jE<=5 else 0.0;oD,ry=(0,False)
   for k in G(N(L(df)-2,bu+M(jE,2)+1),L(df)-2):
    if _f(df,'close',k)<aH if g else _f(df,'close',k)>aJ:ry=True;break
    if _f(df,'low',k)<=aJ if g else _f(df,'high',k)>=aH:oD+=1
   if ry or oD>=3:continue
   rr=3.0 if oD==0 else 1.5 if oD==1 else 0.0;rt=(qU-aJ if g else aH-qU)/M(aJ-aH,E*0.25);na=3.0 if rt>=3.0 else 1.5 if rt>=2.0 else 0.5;mD=N(10.0,R(rp+rq+rr+na+N(1.0,hi['yaklasim_ek_puan']*0.5),1));qc=[av for ai,av in pz if ai<bu];gv=L(qc)>0 and(lu<qc[-1]if g else lu>qc[-1]);ru='Ext'if a=='1H'else'Int';qd=f"{ru}_{('Reversal_OB' if g else 'Reversal_BearOB')}_{hi['kalip_adi']}"if gv else f"{ru}_{('Continue_ValidDem' if g else 'Continue_ValidSup')}_{hi['kalip_adi']}"
   if hi['hidden_base_dp']:qd+='+HiddenDP'
   if(aH-E*0.25<=bb<=qb+E*0.15 and ak>=aH)if g else(qb-E*0.15<=bc<=aJ+E*0.25 and ak<=aJ):
    ob_mt=(aH+aJ)/2.0;ob_fvg_imza=bool(rp>=1.0 and gv)
    px=M(px,N(10.0,mD+(0.5 if ob_fvg_imza else 0.0)));dP.append(f'{a}_{qd}({mD}/10)')
    if ob_fvg_imza and f'{a}_GercekOB_FVG_SonKale'not in dP:dP.append(f'{a}_GercekOB_FVG_SonKale')
    pQ=', Yaklaşım: '+'+'.join(hi['yaklasim_ipuclari'])if hi['yaklasim_ipuclari']else''
    K.append(f"[{a}] {('Bullish' if g else 'Bearish')} {qd} (%50 Mean Threshold: {ob_mt:.4f} | İmbalans Kökü: {qb:.4f}{' | Gerçek OB+FVG Son Kale İmzası!' if ob_fvg_imza else ''}) | Güç: {mD}/10 (Çıkış:{rp}p, V-Shape:{rq}p, Fresh:{rr}p, RR:{na}p{pQ}) (YT-Part1,2,3 & Ders-07)")
    az.append(('OB',bu,aH,aJ));U=(N(U,aH)if U else aH)if g else(M(U,aJ)if U else aJ);break
 if L(pA)>=2:
  for gw,ow in pA[-4:-1]:
   if gw<2 or gw>=L(df)-5:continue
   fL=df.iloc[gw+1:N(L(df)-2,gw+12)];kR,kS=((_f(df,'open',gw)if _f(df,'close',gw)>_f(df,'open',gw)else ow-E*0.35),ow)if g else(ow,(_f(df,'open',gw)if _f(df,'close',gw)<_f(df,'open',gw)else ow+E*0.35));h6=any((F(r['close'])>kS+E*0.12 and F(r['close'])-F(r['open'])>E*0.5 for _,r in fL.iterrows()))if g else any((F(r['close'])<kR-E*0.12 and F(r['open'])-F(r['close'])>E*0.5 for _,r in fL.iterrows()))
   if h6 and(kR-E*0.2<=(bb if g else bc)<=kS+E*0.2)and(ak>=kR if g else ak<=kS):dP.append(f"{a}_{('TersFlag_Flip' if g else 'Bear_TersFlag_Flip')}");K.append(f"[{a}] {('Bullish' if g else 'Bearish')} Flip Bölge / Ters Flag ({(kS if g else kR):.4f}) (YT-Part1,2,3)");az.append(('BB/FL',gw,kR,kS));U=(kR if U is None else N(U,kR))if g else(kS if U is None else M(U,kS));break
 j8,f0,f1,hC,_=ftr_fo_itz_taramasi(df,z,C,a,B);eY,dx,dy,ef,eg=dp_ve_fl_analizi(df,z,C,a,B);j9,mx,iC,iD,dg=quasimodo_mpl_analizi(df,z,C,a,B);ka,eh,hv,jX,g4=imbalance_fvg_koku_analizi(df,z,C,a,B);z['fl_dp_meta'],z['qm_meta'],z['v6_meta']=(eg,dg,g4)
 for kb,f2,kd,hD in[(j8,f0,f1,hC),(eY,dx,dy,ef),(j9,mx,iC,iD),(ka,eh,hv,jX)]:
  for eZ in kb:
   if eZ not in dP:dP.append(eZ)
  K.extend(kd);az.extend(hD)
  if f2 is not None:U=f2 if U is None else N(U,f2)if g else M(U,f2)
 ke,ei,fl,lf,er=gap_vib_fibo_analizi(df,z,dP,a,B);kf,ej,fP,iH,fg=range_po3_tt3_analizi(df,z,C,a,B);hE,dz,b9,cz,bQ=bobin_atnali_mw_analizi(df,z,C,a,B);hF,dA,bA,dq,bl=engulf_pinbar_analizi(df,z,C,a,B);ev,dB,cA,ea,bg=ib_fakey_smt_analizi(df,z,C,a,B,z.get('sembol','BTC/USDT'));z['v7_meta'],z['v9_meta'],z['v10_meta'],z['v11_meta'],z['v12_meta']=(er,fg,bQ,bl,bg);hG,dC,cC,fZ,bv=entry_mtf_3r_analizi(df,z,dP+ev,C,a,B);z['v13_meta']=bv
 for rX,jS,ph,rY in[(ke,ei,fl,lf),(kf,ej,fP,iH),(hE,dz,b9,cz),(hF,dA,bA,dq),(ev,dB,cA,ea),(hG,dC,cC,fZ)]:
  for vp in rX:
   if vp not in dP:dP.append(vp)
  K.extend(ph);az.extend(rY)
  if jS is not None:U=jS if U is None else N(U,jS)if g else M(U,jS)
 return(dP,U,K,az,px)
def likidite_smt_analizi(J,bJ,af,a2,B='BULLISH'):
 iR,K,a3=([],[],0);pl,pm=(a2['highs'],a2['lows']);nZ,n0=swing_noktalarini_bul(af,n=2,kirilim_sarti=False);cl=_f(af,'close',-2);eF=J.split(':')[0];qV='ETH/USDT'if eF=='BTC/USDT'else'BTC/USDT';k7=an.get(LTF_PERIYOT,an.get('15m',{})).get(qV);oX=a2.get('wyckoff_fazi','');g=B=='BULLISH'
 if(g and oX in('ACCUMULATION_SPRING','RE_ACCUMULATION'))or(not g and oX in('DISTRIBUTION_UTAD','RE_DISTRIBUTION')):iR.append(oX);K.append(f"[{MTF_PERIYOT.upper()}] {a2.get('wyckoff_aciklama', 'Wyckoff Yakıt Operasyonu')}");a3+=7
 hH,pB=(n0 if g else nZ,pm if g else pl)
 _,_,ltf_lmeta=_likidite_ve_sfp_yapilarini_bul(af)
 _,_,mtf_lmeta=_likidite_ve_sfp_yapilarini_bul(bJ,pl,pm)
 sfp_ltf_obj=ltf_lmeta.get('son_bull_sfp'if g else'son_bear_sfp')
 if sfp_ltf_obj and int(sfp_ltf_obj.get('idx',0))>=L(af)-6:
  my=F(sfp_ltf_obj.get('level')or sfp_ltf_obj.get('price')or cl)
  iR.append('Bull_SFP'if g else'Bear_SFP');K.append(f"[{LTF_PERIYOT}] {('Bullish' if g else 'Bearish')} SFP (İğne Avı): Kırılmamış {my:.4f} likiditesi iğneyle süpürüldü ve içeride kapandı (23-sfp.pdf & Ders-02/04)");a3+=9
 idm_sw_obj=(mtf_lmeta.get('swept_idm_bull')or ltf_lmeta.get('swept_idm_bull'))if g else(mtf_lmeta.get('swept_idm_bear')or ltf_lmeta.get('swept_idm_bear'))
 if idm_sw_obj:
  iR.append('IDM_Sweep_Bull'if g else'IDM_Sweep_Bear');K.append(f"[{MTF_PERIYOT.upper()}/{LTF_PERIYOT}] Inducement (IDM Yem: {F(idm_sw_obj[2]):.4f}) süpürüldü, gerçek POI öncesi tuzak temizlendi (Drive Video Ders-03)");a3+=5
 if(mtf_lmeta.get('aktif_eql')or mtf_lmeta.get('swept_eql'))if g else(mtf_lmeta.get('aktif_eqh')or mtf_lmeta.get('swept_eqh')):
  iR.append('EQL_Fakeout'if g else'EQH_Fakeout');K.append(f"[{MTF_PERIYOT.upper()}] Doğrulanmış {('EQL (SSL Bedava Yakıt)' if g else 'EQH (BSL Bedava Yakıt)')} Fake-Out Likidite Havuzu (16-fakeout.pdf, 22-likidite.pdf & Ders-02)");a3+=5
 sfp_mtf_obj=mtf_lmeta.get('son_bull_sfp'if g else'son_bear_sfp')
 if sfp_mtf_obj and int(sfp_mtf_obj.get('idx',0))>=L(bJ)-5:
  iR.append('HTF_TT3/SFP'if g else'HTF_BearTT3');K.append(f"[{MTF_PERIYOT.upper()}] Three Tap Setup (TT3) / HTF Likidite Sapma Dönüşü ({sfp_mtf_obj.get('level',0):.4f}) (27-tt3.pdf)");a3+=8
 if L(hH)>=3:
  d1,d2,d3=(hH[-3][1],hH[-2][1],hH[-1][1])
  if(d1>d2>d3 and d1-d2>0 and 0.45<=(d2-d3)/(d1-d2)<=1.65)if g else(d1<d2<d3 and d2-d1>0 and 0.45<=(d3-d2)/(d2-d1)<=1.65):iR.append('3D_Bull'if g else'3D_Bear');K.append(f"[{LTF_PERIYOT}] {('Bullish' if g else 'Bearish')} Three Drive (3D) Yorulma Yaklaşımı (17.pdf)");a3+=5
 if L(hH)>=2:
  (ib,u1),(ic,u2)=(hH[-2],hH[-1]);nb,nc=(_f(af,'close',ib),_f(af,'close',ic));bY,ci,gr,kC,gt,gu=(_f(af,'rsi',ib),_f(af,'rsi',ic),_f(af,'ao',ib),_f(af,'ao',ic),_f(af,'cvd',ib),_f(af,'cvd',ic));f3=(nc<=nb*1.001 and ci>bY+1.8)if g else(nc>=nb*0.999 and ci<bY-1.8);hI=(u2<=u1*1.0015 and((kC>gr and gr<0)or gu>gt))if g else(u2>=u1*0.9985 and((kC<gr and gr>0)or gu<gt))
  if f3 or hI:gx='Medium_EQ_DVG'if A(u2-u1)/M(u1,1e-9)<=0.0035 else'Strong_Regular_DVG';iR.append(f"{('Bull' if g else 'Bear')}_{gx}");K.append(f"[{LTF_PERIYOT}] {('Bullish' if g else 'Bearish')} {gx} ({'RSI Kapanış' if f3 else 'AO/CVD İğne'} {bY:.0f}->{ci:.0f}) (38-dvg.pdf & YT-Part12)");a3+=7 if'Strong'in gx else 5
 if k7 is not None and L(k7)>=18 and L(af)>=18:
  dv='low'if g else'high';ox,oy=(F(af[dv].iloc[-16:-6].min()if g else af[dv].iloc[-16:-6].max()),F(af[dv].iloc[-6:-1].min()if g else af[dv].iloc[-6:-1].max()));oz,oA=(F(k7[dv].iloc[-16:-6].min()if g else k7[dv].iloc[-16:-6].max()),F(k7[dv].iloc[-6:-1].min()if g else k7[dv].iloc[-6:-1].max()))
  if(oy<ox and oA>=oz or(oy>=ox and oA<oz))if g else(oy>ox and oA<=oz or(oy<=ox and oA>oz)):iR.append('Bull_SMT'if g else'Bear_SMT');K.append(f"[{LTF_PERIYOT}] {qV} ile {('Pozitif (Bullish)' if g else 'Negatif (Bearish)')} SMT Uyuşmazlığı (39-smt.pdf & YT-Part10)");a3+=6
 return(N(25,a3),iR,K)
def ltf_pa_ve_giris_tetikleyici(af,U=None,B='BULLISH'):
 aa,ar=swing_noktalarini_bul(af,n=2)
 if L(af)<2:return(0,[],[],0.0,0.0)
 if L(aa)<1 or L(ar)<1 or L(af)<8:
  g6_fb=_f(af,'close',-1)
  al_fb=R(g6_fb*(0.992 if B=='BULLISH'else 1.008),6)
  return(0,[],[],g6_fb,al_fb)
 m0,m1,m2,m3=(af.iloc[-5],af.iloc[-4],af.iloc[-3],af.iloc[-2]);g6=_f(af,'close',-1);E=M(F(m3['atr']),g6*0.001);rZ,r0,c5,c6,bB,cD,bC,bD=(*_r(m0,'open','close','high','low'),*_r(m1,'open','close','high','low'));aM,aD,cG,cH,bf,at,cc,cd=(*_r(m2,'open','close','high','low'),*_r(m3,'open','close','high','low'));hJ,cq,ce=(A(cD-bB),A(aD-aM),A(at-bf));mz,mA=(N(at,bf)-cd,cc-M(at,bf));pC,pD=(cG-M(aD,aM),N(aD,aM)-cH);f4,lk,f5,ll=(aa[-1][1],aa[-2][1]if L(aa)>=2 else aa[-1][1],ar[-1][1],ar[-2][1]if L(ar)>=2 else ar[-1][1]);pE,q6=(cG<=bC and cH>=bD,bC<=c5 and bD>=c6);el,K,a3=([],[],0);g=B=='BULLISH';eq,aX=('Bull'if g else'Bear','Bullish'if g else'Bearish');oY=(aD<aM and at>cG)if g else(aD>aM and at<cH);jO=(aD<aM and at>bf and at>=aM and ce>cq*1.05)if g else(aD>aM and at<bf and at<=aM and ce>cq*1.05);ho=cc>cG and cd<cH and(at>bf if g else at<bf)
 if oY:el.append(f'{eq}_MeraMera_QML_DP');K.append(f'[{LTF_PERIYOT}] {aX} Mera Mera / Outside Engulf Karar Noktası (DP = LTF Gizli QML) (10, 30.pdf & YT-Part4&5)');a3+=13
 elif jO or ho:el.append(f'{eq}_Engulf/OB');K.append(f'[{LTF_PERIYOT}] {aX} Engulfing / Outside Bar Onay Mumu (30-engulf.pdf)');a3+=12
 jP=(mz>ce*1.6 and mz>mA*1.4 and at>=bf)if g else(mA>ce*1.6 and mA>mz*1.4 and at<=bf);fD=(aD<aM and at>bf if g else aD>aM and at<bf)and cq>E*0.45 and ce>E*0.45 and A(ce-cq)<=cq*0.3
 if jP:el.append(f'{eq}_Pinbar');K.append(f'[{LTF_PERIYOT}] {aX} Tepki Spike / Pinbar Reddiyesi (31-spike-pinbar.pdf)');a3+=10
 elif fD:el.append(f'{eq}_Railroad');K.append(f'[{LTF_PERIYOT}] {aX} Railroad Tracks Dönüş Formasyonu (31-railroad.pdf)');a3+=10
 lT=(aM-aD>E*0.6 and at-bf>E*0.6 and at>=aM or(aD>aM and cq>E*0.55 and aD>bC and aM<=cd<=aD and at>=aD))if g else(aD-aM>E*0.6 and bf-at>E*0.6 and at<=aM or(aD<aM and cq>E*0.55 and aD<bD and aD<=cc<=aM and at<=aD))
 if lT:el.append(f'{eq}_BosaltDoldur');K.append(f'[{LTF_PERIYOT}] {aX} Boşalt-Doldur Momentum + Ters İğne Onayı (32-bosalt-doldur.pdf)');a3+=14
 b1=(pE and cd<bD and at>=cH)if g else(pE and cc>bC and at<=cG);dm=(q6 and cH<c6 and aD<aM and at>bf and at>=bD)if g else(q6 and cG>c5 and aD>aM and at<bf and at<=bC)
 if b1 or dm:el.append(f"{eq}_{('Kuralli_Pinbarli_Fakey' if b1 else 'Pinbarsiz_Fakey_PO3')}");K.append(f"[{LTF_PERIYOT}] {aX} {('Kurallı Pinbarlı Fake Setup (Inside Bar İçinde/Üstünde Kapandı)' if b1 else 'Pinbarsız 4-Mum Fake Setup (Zıt Renkli Dönüş)')} (34-fake-setup.pdf & YT-Part12)");a3+=15
 elif pE and(at>bC if g else at<bD):el.append(f'{eq}_InsideBrk');K.append(f'[{LTF_PERIYOT}] {aX} Inside Bar Kırılımı (33-inside-bar.pdf)');a3+=10
 lU=(aD>aM and at>bf and pC>pD*1.25 and aM<=cd<=aD and at>cG)if g else(aD<aM and at<bf and pD>pC*1.25 and aD<=cc<=aM and at<cH)
 if lU:el.append(f'{eq}_YingYang_HiddenBase');K.append(f'[{LTF_PERIYOT}] {aX} Ying-Yang (Hidden Base) Momentum Devam Formasyonu (35.pdf & YT-Part10)');a3+=12
 eL=(at>bf and ce>=E*0.5 and mz<=ce*0.09 and(aD<aM and pD<=cq*0.12 or mA<=ce*0.1))if g else(at<bf and ce>=E*0.5 and mA<=ce*0.09 and(aD>aM and pC<=cq*0.12 or mz<=ce*0.1))
 if eL:el.append(f'{eq}_Istekli_Marubozu');K.append(f'[{LTF_PERIYOT}] {aX} İstekli Mum / Marubozu (Bölgeden İğnesiz Sıfır Mukavemetli Dönüş) (35.pdf & YT-Part10)');a3+=12
 if(cD<bB and hJ>E*0.45 and cq<=hJ*0.45 and at>bf and at>=(bB+cD)/2.0)if g else(cD>bB and hJ>E*0.45 and cq<=hJ*0.45 and at<bf and at<=(bB+cD)/2.0):el.append('Bull_MorningStar_Doji'if g else'Bear_EveningStar_Doji');K.append(f"[{LTF_PERIYOT}] {aX} {('Sabah' if g else 'Akşam')} Yıldızı (Doji + Güçlü Dönüş Mumu) (YT-Part2&3)");a3+=11
 if g:
  if A(f5-ll)/M(ll,1e-09)<=0.0085 and at>bf and at>f5+E*0.28:iX='Simple_W_Trade'if A(f5-ll)<=E*0.2 else'ShortFormed_W_Trade'if f5>ll else'Extended_W_Trade';el.append(iX);K.append(f'[{LTF_PERIYOT}] {iX} (2. Bacak Onayı + W-Kink Dönüşü) (29.pdf & YT-Part10)');a3+=11
  if at>f4 and aD<=f4:kD=f5<ll;el.append('LTF_Strong_Bull_CHoCH'if kD else'LTF_Weak_Bull_CHoCH');K.append(f"[{LTF_PERIYOT}] LTF {('Güçlü' if kD else 'Zayıf')} Bullish CHoCH (> {f4:.4f}) (YT-Part1,2,3,10)");a3+=13 if kD else 9
  r1=N(f5,ll if f5>=g6*0.996 else f5,F(af['low'].iloc[-15:].min()));al=R(N(r1-M(E*0.5,g6*0.0025),g6*0.996),6)
  if g6<cd:a3=0
 else:
  if A(f4-lk)/M(lk,1e-09)<=0.0085 and at<bf and at<f4-E*0.28:iY='Simple_M_Trade'if A(f4-lk)<=E*0.2 else'ShortFormed_M_Trade'if f4<lk else'Extended_M_Trade';el.append(iY);K.append(f'[{LTF_PERIYOT}] {iY} (2. Bacak Onayı + M-Kink Dönüşü) (29.pdf & YT-Part10)');a3+=11
  if at<f5 and aD>=f5:kD=f4>lk;el.append('LTF_Strong_Bear_CHoCH'if kD else'LTF_Weak_Bear_CHoCH');K.append(f"[{LTF_PERIYOT}] LTF {('Güçlü' if kD else 'Zayıf')} Bearish CHoCH (< {f5:.4f}) (YT-Part1,2,3,10)");a3+=13 if kD else 9
  r2=M(f4,lk if f4<=g6*1.004 else f4,F(af['high'].iloc[-15:].max()));al=R(M(r2+M(E*0.5,g6*0.0025),g6*1.004),6)
  if g6>cc:a3=0
 return(N(25,a3),el,K,g6,al)
def _karne_checklist_olustur(H,html_mi=False,yorum_on_eki=''):
 kFlt=H.get('konum_meta',{})if I(H,dict)else{}
 chk=kFlt.get('checklist',{})
 yon_ok=bool(chk.get('yon_ok',kFlt.get('htf_yon_ok',False)))
 qml_ok=bool(chk.get('qml',kFlt.get('htf_qml_bolgesinde',False)))
 ote_ok=bool(chk.get('ote',kFlt.get('htf_ote_bolgesinde',False)))
 ob_ok=bool(chk.get('ob',kFlt.get('htf_ob_bolgesinde',False)))
 fresh_ok=bool(chk.get('fresh_arz_talep',kFlt.get('htf_arz_talep_bolgesinde',False)))
 choch_ok=bool(chk.get('choch_noktasi',kFlt.get('htf_choch_noktasinda',False)))
 bos_ok=bool(chk.get('bos_noktasi',kFlt.get('htf_bos_noktasinda',False)))
 itz_ok=bool(chk.get('itz',kFlt.get('htf_itz_bolgesinde',False)))
 magic_ok=bool(chk.get('magic_line',kFlt.get('htf_magic_line_bolgesinde',False)))
 ltf_kir_ok=bool(chk.get('ltf_reversal_kirilim',kFlt.get('ltf_reversal_kirilim_onay',False)))
 ltf_mum_ok=bool(chk.get('ltf_reversal_mum',kFlt.get('ltf_reversal_mum_onay',False)))
 safe_sayi=int(kFlt.get('htf_bolge_sayisi',sum([int(qml_ok),int(ote_ok),int(ob_ok),int(fresh_ok),int(choch_ok),int(bos_ok),int(itz_ok),int(magic_ok)])))
 safe_puan=int(kFlt.get('htf_safe_puan',N(100,safe_sayi*15+(15 if yon_ok else 0)+(15 if(ltf_kir_ok or ltf_mum_ok)else 0))))
 safe_derece=str(kFlt.get('htf_safe_derecesi','🛡️ ULTRA SAFE'if safe_sayi>=4 else'🛡️ ÇOK SAFE'if safe_sayi==3 else'🟢 SAFE'if safe_sayi==2 else'🟡 STANDART SAFE'if safe_sayi==1 else'🔴 BÖLGE DIŞI'))
 htf_yon_str=str(H.get('yon_4h',kFlt.get('hedef_yon','-')))
 kir_detay=', '.join(kFlt.get('ltf_kirilim_listesi',[])[:2])or('Onaylı'if ltf_kir_ok else'Bekleniyor')
 mum_detay=', '.join(kFlt.get('ltf_mum_listesi',[])[:2])or('Onaylı'if ltf_mum_ok else'Bekleniyor')
 maddeler=[
  ('1. Yön Belirleme (HTF Ana Yön)',yon_ok,htf_yon_str),
  ('1.Öncelik: QML (Quasimodo Seviyesi)',qml_ok,str(chk.get('qml_fiyat','-'))),
  ('2.Öncelik: OB (HTF Order Block)',ob_ok,str(chk.get('ob_aralik','-'))),
  ('3.Öncelik: Fresh Arz/Talep Bölgesi',fresh_ok,str(chk.get('fresh_aralik','-'))),
  ('4.Öncelik: OTE (Fibo 0.618-0.705-0.786)',ote_ok,str(chk.get('ote_aralik','-'))),
  ('2.Kademe: BOS Yaptıran Nokta (Kırılım)',bos_ok,str(chk.get('bos_fiyat','-'))),
  ('2.Kademe: CHoCH Yapılan Nokta (Kırılım)',choch_ok,str(chk.get('choch_fiyat','-'))),
  ('2.Kademe: ITZ (Kırılım Öncesi Son Yapı)',itz_ok,str(chk.get('itz_fiyat','-'))),
  ('2.Kademe: Magic Line (Flag Limit / FL)',magic_ok,str(chk.get('magic_fiyat','-'))),
  ('3a. LTF Reversal Kırılım Onayı',ltf_kir_ok,kir_detay),
  ('3b. LTF Reversal Mum Konsepti',ltf_mum_ok,mum_detay)
 ]
 if html_mi:
  satirlar=[]
  satirlar.append(f'<div id="karne_checklist_kutu" style="background:#0f172a;border:1px solid #334155;border-radius:6px;padding:6px 8px;margin:5px 0;">')
  satirlar.append(f'<div style="color:#fde047;font-weight:bold;font-size:11.5px;margin-bottom:4px;">📋 STRATEJİ & SEVİYE KARNESİ CHECK-LIST ({safe_sayi}/8 HTF Bölge | {safe_derece} | Safe Puanı: {safe_puan}/100)</div>')
  for ad,ok_mu,dt in maddeler:
   ikon='✅'if ok_mu else'⬜'
   renk='#4ade80'if ok_mu else'#94a3b8'
   agirlik='bold'if ok_mu else'normal'
   satirlar.append(f'<div style="color:{renk};font-weight:{agirlik};font-size:11px;line-height:1.42;">{ikon} {ad}: <span style="color:#cbd5e1;font-weight:normal;">{dt}</span></div>')
  satirlar.append('</div>')
  return''.join(satirlar)
 satirlar=[
  f"{yorum_on_eki}========================================",
  f"{yorum_on_eki}📋 STRATEJİ & SEVİYE KARNESİ CHECK-LIST",
  f"{yorum_on_eki}🛡️ SAFE SKORU: {safe_sayi}/8 HTF Bölge Sağlandı | {safe_derece} ({safe_puan}/100 Puan)",
  f"{yorum_on_eki}========================================"
 ]
 for ad,ok_mu,dt in maddeler:
  ikon='[✅]'if ok_mu else'[⬜]'
  satirlar.append(f"{yorum_on_eki} {ikon} {ad:<36} : {dt}")
 return'\n'.join(satirlar)+'\n'
def ilk_kontrol_arz_talep_ob_ote_qml(bS,aP=None,anlik_fiyat=None,de_fiyat=None,B=None,f4h=None,hN=None,bw=None,Q=None,f6=None,q7=None):
 """ADIM 0 (İLK ÖNCELİK KAPISI): Her işlem kontrolünde ve market taramasında İLK OLARAK fiyatın
 Arz/Talep, OB (Order Block), OTE (0.618-0.705-0.786) ve QML (Quasimodo Level) bölgesinde olup olmadığını kontrol eder.
 Market sürekli bu 4 ana bölgeye göre taranır ve 0-10000 puanlık ölçekle derecelendirilir."""
 if bS is None or L(bS)<10:
  return{'ilk_kontrol_gecti':False,'birincil_bolge_sayisi':0,'htf_arz_talep_bolgesinde':False,'htf_ob_bolgesinde':False,'htf_ote_bolgesinde':False,'htf_qml_bolgesinde':False,'aktif_birincil_bolgeler':[],'oncelik_vektor':(0,0,0,0),'en_yakin_birincil_atr':99.0,'birincil_pusuda_onay':False,'birincil_radar_kademesi':0,'birincil_olcek_skoru':0,'birincil_olcek_carpani_etkin':0.35,'qml_lvl':0.0,'ote_lo':0.0,'ote_hi':0.0,'ob_lo':0.0,'ob_hi':0.0,'fresh_lo':0.0,'fresh_hi':0.0,'htf_at_list':[],'htf_imb_list':[],'htf_yon_at':[],'htf_ob_list':[],'sMax':0.0,'sMin':0.0,'dU':0.0,'E_htf':0.0,'hedef_yon':B or'BULLISH','htf_yon_ok':False}
 if not I(aP,dict)or not aP:
  aP=market_yapisi_ve_fibo_analizi(bS)
 hedef_B=B if B in('BULLISH','BEARISH')else(aP.get('yon')if aP.get('yon')in('BULLISH','BEARISH')else'BULLISH')
 g=(hedef_B=='BULLISH')
 ak=F(anlik_fiyat)if anlik_fiyat is not None and F(anlik_fiyat)>0 else _f(bS,'close',-1)
 son_dip_htf=N(_f(bS,'low',-3),_f(bS,'low',-2),_f(bS,'low',-1),ak)
 son_tepe_htf=M(_f(bS,'high',-3),_f(bS,'high',-2),_f(bS,'high',-1),ak)
 de=F(de_fiyat)if de_fiyat is not None and F(de_fiyat)>0 else(son_dip_htf if g else son_tepe_htf)
 de_uc=N(de,son_dip_htf)if g else M(de,son_tepe_htf)
 scalp_aktif=(ISLEM_TARZI_MODU=='Scalp'or HTF_PERIYOT in('1h','30m','15m'))
 tol_k=1.45 if scalp_aktif else 1.15
 E_htf=M(_f(bS,'atr',-2)if'atr'in bS.columns else ak*0.003,ak*0.001)*tol_k
 htf_yon_ok=(aP.get('yon')==hedef_B)
 ts_htf=list(G(L(bS)))
 htf_bos_raw=aP.get('kysy_meta',{}).get('bos_list',[])
 bs_htf=[{'orig_idx':b[2],'idx2':b[0],'yon':b[4],'tip':b[5]}for b in htf_bos_raw]
 htf_qml_lvl=F(aP.get('qml_seviyesi')or aP.get('qm_meta',{}).get('qml_seviyesi')or aP.get('qm_meta',{}).get('mpl_seviyesi')or 0.0)
 if htf_qml_lvl<=0 and aP.get('highs')and aP.get('lows'):
  try:
   qm_c=_qml_yapisi_bul(aP.get('highs',[]),aP.get('lows',[]),hedef_B,bS)
   if qm_c:htf_qml_lvl=F(qm_c[1])
  except X:pass
 mtf_qml_lvl=F((Q.get('qml_seviyesi')or Q.get('qm_meta',{}).get('qml_seviyesi')or Q.get('qm_meta',{}).get('mpl_seviyesi')or 0.0)if I(Q,dict)else 0.0)
 if htf_qml_lvl<=0 and mtf_qml_lvl>0:htf_qml_lvl=mtf_qml_lvl
 htf_at_list,htf_imb_list=_arz_talep_ve_imbalance_sablon_hesapla(bS,ts_htf,bs_htf,E_htf,htf_qml_lvl if htf_qml_lvl>0 else None)
 hedef_tur='TALEP'if g else'ARZ'
 htf_yon_at=[z for z in htf_at_list if z.get('tur')==hedef_tur]
 if bw is not None and I(Q,dict)and L(bw)>=10:
  try:
   E_mtf=M(_f(bw,'atr',-2)if'atr'in bw.columns else ak*0.002,ak*0.0008)
   mtf_bos_raw=Q.get('kysy_meta',{}).get('bos_list',[])
   bs_mtf=[{'orig_idx':b[2],'idx2':b[0],'yon':b[4],'tip':b[5]}for b in mtf_bos_raw]
   mtf_at_l,_=_arz_talep_ve_imbalance_sablon_hesapla(bw,list(G(L(bw))),bs_mtf,E_mtf,mtf_qml_lvl if mtf_qml_lvl>0 else None)
   for zm in mtf_at_l:
    if zm.get('tur')==hedef_tur:htf_yon_at.append(zm)
  except X:pass
 sMax,sMin=(F(aP.get('swing_max')or 0.0),F(aP.get('swing_min')or 0.0))
 dU=M(0.0,sMax-sMin)
 f4h_l=(f4h if I(f4h,list)else[])+(f6 if I(f6,list)else[])
 hN_l=(hN if I(hN,list)else[])+(q7 if I(q7,list)else[])
 # 1) ARZ / TALEP BÖLGESİ KONTROLÜ (Fresh Talep / Fresh Arz / RBR-DBD / Flip Breaker)
 fresh_lo,fresh_hi=(0.0,0.0)
 if dU>0:
  if g:
   fresh_lo=sMin
   fresh_hi=M(sMax-dU*0.72,htf_qml_lvl if sMin<htf_qml_lvl<=sMax-dU*0.48 else sMax-dU*0.72)
  else:
   fresh_hi=sMax
   fresh_lo=N(sMin+dU*0.72,htf_qml_lvl if sMin+dU*0.48<=htf_qml_lvl<sMax else sMin+dU*0.72)
 fresh_kutu_temas=(
  any((z['lo']-E_htf*0.38<=de<=z['hi']+E_htf*0.38)or(z['lo']-E_htf*0.38<=de_uc<=z['hi']+E_htf*0.38)or(z['lo']-E_htf*0.38<=ak<=z['hi']+E_htf*0.38)for z in htf_yon_at)
  or any((lo-E_htf*0.38<=de<=hi+E_htf*0.38)or(lo-E_htf*0.38<=de_uc<=hi+E_htf*0.38)or(lo-E_htf*0.38<=ak<=hi+E_htf*0.38)for ktip,_,lo,hi in hN_l if any(x in str(ktip).upper()for x in('BB','FL','OB','TALEP','ARZ','FTR')))
  or any(any(x in str(p)for x in('ValidDem','ValidSup','Fresh','TersFlag_Flip','FTR','RBR','DBD','DBR','RBD'))for p in f4h_l)
 )
 fresh_grafik_bolge_temas=bool(fresh_hi>fresh_lo>0 and((fresh_lo-E_htf*0.32<=de<=fresh_hi+E_htf*0.32)or(fresh_lo-E_htf*0.32<=de_uc<=fresh_hi+E_htf*0.32)or(fresh_lo-E_htf*0.32<=ak<=fresh_hi+E_htf*0.32))and(ak>=fresh_lo-E_htf*0.20 if g else ak<=fresh_hi+E_htf*0.20))
 htf_arz_talep_bolgesinde=bool(fresh_kutu_temas or fresh_grafik_bolge_temas)
 # 2) OB (ORDER BLOCK & %50 MT) BÖLGESİ KONTROLÜ
 htf_ob_list=[z for z in htf_yon_at if z.get('alt_tur')in('REVERSAL_OB','VALID_DEMAND','VALID_SUPPLY')]
 ob_lo,ob_hi=(0.0,0.0)
 if htf_ob_list:
  ob_lo,ob_hi=(F(htf_ob_list[-1]['lo']),F(htf_ob_list[-1]['hi']))
 elif dU>0:
  ob_lo,ob_hi=((sMin,sMin+N(dU*0.24,E_htf*1.45))if g else(sMax-N(dU*0.24,E_htf*1.45),sMax))
 htf_ob_temas=(
  any((z['lo']-E_htf*0.38<=de<=z['hi']+E_htf*0.38)or(z['lo']-E_htf*0.38<=de_uc<=z['hi']+E_htf*0.38)or(z['lo']-E_htf*0.38<=ak<=z['hi']+E_htf*0.38)for z in htf_ob_list)
  or any((lo-E_htf*0.38<=de<=hi+E_htf*0.38)or(lo-E_htf*0.38<=de_uc<=hi+E_htf*0.38)or(lo-E_htf*0.38<=ak<=hi+E_htf*0.38)for ktip,_,lo,hi in hN_l if'OB'in str(ktip).upper())
  or any(any(x in str(p)for x in('Reversal_OB','Reversal_BearOB','GercekOB','OB'))for p in f4h_l)
  or(ob_hi>ob_lo>0 and((ob_lo-E_htf*0.32<=de<=ob_hi+E_htf*0.32 or ob_lo-E_htf*0.32<=de_uc<=ob_hi+E_htf*0.32 or ob_lo-E_htf*0.32<=ak<=ob_hi+E_htf*0.32)and(ak>=ob_lo-E_htf*0.20 if g else ak<=ob_hi+E_htf*0.20)))
 )
 htf_ob_bolgesinde=bool(htf_ob_temas)
 # 3) OTE (OPTIMAL TRADE ENTRY: 0.618 - 0.705 - 0.786) BÖLGESİ KONTROLÜ
 ote_lo,ote_hi=(0.0,0.0)
 mtf_ote_ok=bool(I(Q,dict)and(Q.get('ote_bull_mu')if g else Q.get('ote_bear_mu')))
 if dU>0:
  ote_lo,ote_hi=(sMax-dU*0.79,sMax-dU*0.60)if g else(sMin+dU*0.60,sMin+dU*0.79)
  htf_ote_bolgesinde=bool(
   (ote_lo-E_htf*0.28<=de<=ote_hi+E_htf*0.28)
   or(ote_lo-E_htf*0.28<=de_uc<=ote_hi+E_htf*0.28)
   or(ote_lo-E_htf*0.28<=ak<=ote_hi+E_htf*0.28)
   or bool(aP.get('ote_bull_mu')if g else aP.get('ote_bear_mu'))
   or mtf_ote_ok
   or any(any(x in str(p)for x in('OTE','AltinOran','705','618'))for p in f4h_l)
  )
 else:
  htf_ote_bolgesinde=bool(mtf_ote_ok)
 # 4) QML (QUASIMODO LEVEL) BÖLGESİ KONTROLÜ
 qml_band_ok=False
 if htf_qml_lvl>0 and dU>0:
  if g and sMin<=htf_qml_lvl<=sMin+dU*0.48:
   qml_band_ok=bool((sMin-E_htf*0.25<=de<=htf_qml_lvl+E_htf*0.45 or sMin-E_htf*0.25<=de_uc<=htf_qml_lvl+E_htf*0.45 or sMin-E_htf*0.25<=ak<=htf_qml_lvl+E_htf*0.45)and ak>=sMin-E_htf*0.15)
  elif not g and sMax-dU*0.48<=htf_qml_lvl<=sMax:
   qml_band_ok=bool((htf_qml_lvl-E_htf*0.45<=de<=sMax+E_htf*0.25 or htf_qml_lvl-E_htf*0.45<=de_uc<=sMax+E_htf*0.25 or htf_qml_lvl-E_htf*0.45<=ak<=sMax+E_htf*0.25)and ak<=sMax+E_htf*0.15)
 htf_qml_bolgesinde=bool(
  (htf_qml_lvl>0 and(A(de-htf_qml_lvl)<=E_htf*0.78 or A(de_uc-htf_qml_lvl)<=E_htf*0.78 or A(ak-htf_qml_lvl)<=E_htf*0.78))
  or(mtf_qml_lvl>0 and(A(de-mtf_qml_lvl)<=E_htf*0.65 or A(ak-mtf_qml_lvl)<=E_htf*0.65))
  or qml_band_ok
  or any('QM'in str(p)or'MPL'in str(p)for p in f4h_l)
 )
 # 1. ÖNCELİK İLK KONTROL SONUCU VE MESAFE RADARI
 birincil_bolge_sayisi=sum([int(htf_qml_bolgesinde),int(htf_ob_bolgesinde),int(htf_arz_talep_bolgesinde),int(htf_ote_bolgesinde)])
 ilk_kontrol_gecti=(birincil_bolge_sayisi>=1)
 mesafe_adaylari=[]
 if htf_qml_lvl>0:mesafe_adaylari.append(0.0 if htf_qml_bolgesinde else A(ak-htf_qml_lvl)/M(E_htf,1e-09))
 if ob_hi>ob_lo>0:mesafe_adaylari.append(0.0 if(htf_ob_bolgesinde or ob_lo<=ak<=ob_hi)else N(A(ak-ob_lo),A(ak-ob_hi))/M(E_htf,1e-09))
 if fresh_hi>fresh_lo>0:mesafe_adaylari.append(0.0 if(htf_arz_talep_bolgesinde or fresh_lo<=ak<=fresh_hi)else N(A(ak-fresh_lo),A(ak-fresh_hi))/M(E_htf,1e-09))
 if ote_hi>ote_lo>0:mesafe_adaylari.append(0.0 if(htf_ote_bolgesinde or N(ote_lo,ote_hi)<=ak<=M(ote_lo,ote_hi))else N(A(ak-ote_lo),A(ak-ote_hi))/M(E_htf,1e-09))
 for z_m in htf_yon_at:
  zlo,zhi=(F(z_m.get('lo',0)),F(z_m.get('hi',0)))
  if zhi>zlo>0:mesafe_adaylari.append(0.0 if zlo<=ak<=zhi else N(A(ak-zlo),A(ak-zhi))/M(E_htf,1e-09))
 en_yakin_birincil_atr=R(N(mesafe_adaylari),2)if mesafe_adaylari else 99.0
 birincil_pusuda_onay=bool((not ilk_kontrol_gecti)and htf_yon_ok and en_yakin_birincil_atr<=1.50)
 aktif_birincil_bolgeler=[]
 if htf_qml_bolgesinde:aktif_birincil_bolgeler.append('QML')
 if htf_ob_bolgesinde:aktif_birincil_bolgeler.append('OB')
 if htf_arz_talep_bolgesinde:aktif_birincil_bolgeler.append('Arz/Talep')
 if htf_ote_bolgesinde:aktif_birincil_bolgeler.append('OTE')
 oncelik_vektor=(int(htf_qml_bolgesinde),int(htf_ob_bolgesinde),int(htf_arz_talep_bolgesinde),int(htf_ote_bolgesinde))
 # 10,000 PUANLIK MUTLAK ÖNCELİK ÖLÇEĞİ (BIRINCIL_BOLGE_OLCEK_CARPANI İLE ÖLÇEKLENİR)
 olcek_k=M(1.5,F(BIRINCIL_BOLGE_OLCEK_CARPANI))/5.0
 birincil_agirlik=(480 if htf_qml_bolgesinde else 0)+(450 if htf_ob_bolgesinde else 0)+(440 if htf_arz_talep_bolgesinde else 0)+(410 if htf_ote_bolgesinde else 0)
 if ilk_kontrol_gecti:
  taban_10k=(9200 if birincil_bolge_sayisi>=4 else 7800 if birincil_bolge_sayisi==3 else 6400 if birincil_bolge_sayisi==2 else 5000)
  birincil_olcek_skoru=N(10000,int(R((taban_10k+birincil_agirlik)*M(0.85,N(1.25,olcek_k)),0)))
  birincil_olcek_carpani_etkin=R((5.0 if birincil_bolge_sayisi>=4 else 4.2 if birincil_bolge_sayisi==3 else 3.5 if birincil_bolge_sayisi==2 else 2.8)*olcek_k,2)
  birincil_radar_kademesi=2
 elif birincil_pusuda_onay:
  birincil_olcek_skoru=int(M(1800,R(4200-en_yakin_birincil_atr*1450,0)))
  birincil_olcek_carpani_etkin=1.5
  birincil_radar_kademesi=1
 else:
  birincil_olcek_skoru=0
  birincil_olcek_carpani_etkin=0.35
  birincil_radar_kademesi=0
 return{'ilk_kontrol_gecti':ilk_kontrol_gecti,'birincil_bolge_sayisi':birincil_bolge_sayisi,'htf_arz_talep_bolgesinde':htf_arz_talep_bolgesinde,'htf_ob_bolgesinde':htf_ob_bolgesinde,'htf_ote_bolgesinde':htf_ote_bolgesinde,'htf_qml_bolgesinde':htf_qml_bolgesinde,'aktif_birincil_bolgeler':aktif_birincil_bolgeler,'oncelik_vektor':oncelik_vektor,'en_yakin_birincil_atr':en_yakin_birincil_atr,'birincil_pusuda_onay':birincil_pusuda_onay,'birincil_radar_kademesi':birincil_radar_kademesi,'birincil_olcek_skoru':birincil_olcek_skoru,'birincil_olcek_carpani_etkin':birincil_olcek_carpani_etkin,'qml_lvl':htf_qml_lvl,'ote_lo':ote_lo,'ote_hi':ote_hi,'ob_lo':ob_lo,'ob_hi':ob_hi,'fresh_lo':fresh_lo,'fresh_hi':fresh_hi,'htf_at_list':htf_at_list,'htf_imb_list':htf_imb_list,'htf_yon_at':htf_yon_at,'htf_ob_list':htf_ob_list,'sMax':sMax,'sMin':sMin,'dU':dU,'E_htf':E_htf,'hedef_yon':hedef_B,'htf_yon_ok':htf_yon_ok,'aP':aP}
def _htf_adimlari_ve_ltf_tetik_kontrolu(bS,bw,aY,aP,Q,aj,f4h,f6,q8,hN,q7,ra,kk,B='BULLISH'):
 g=B=='BULLISH';ak=_f(aY,'close',-1);bb=N(_f(aY,'low',-3),_f(aY,'low',-2),_f(aY,'low',-1));bc=M(_f(aY,'high',-3),_f(aY,'high',-2),_f(aY,'high',-1))
 de=bb if g else bc
 scalp_aktif=(ISLEM_TARZI_MODU=='Scalp')
 E_ltf=M(_f(aY,'atr',-2)if'atr'in aY.columns else ak*0.0015,ak*0.0005)
 # ADIM 0 (İLK ÖNCELİĞİMİZ): HER SEFERİNDE İLK ÖNCE FİYATIN ARZ/TALEP, OB, OTE VE QML BÖLGESİNDE OLUP OLMADIĞINI KONTROL ET!
 ilk_k=ilk_kontrol_arz_talep_ob_ote_qml(bS,aP,ak,de,B,f4h,hN,bw,Q,f6,q7)
 htf_yon_ok=bool(ilk_k['htf_yon_ok'])
 E_htf=F(ilk_k['E_htf'])
 htf_qml_lvl=F(ilk_k['qml_lvl'])
 ote_lo,ote_hi=(F(ilk_k['ote_lo']),F(ilk_k['ote_hi']))
 ob_lo,ob_hi=(F(ilk_k['ob_lo']),F(ilk_k['ob_hi']))
 fresh_lo,fresh_hi=(F(ilk_k['fresh_lo']),F(ilk_k['fresh_hi']))
 sMax,sMin,dU=(F(ilk_k['sMax']),F(ilk_k['sMin']),F(ilk_k['dU']))
 htf_at_list,htf_imb_list,htf_yon_at=(ilk_k['htf_at_list'],ilk_k['htf_imb_list'],ilk_k['htf_yon_at'])
 htf_arz_talep_bolgesinde=bool(ilk_k['htf_arz_talep_bolgesinde'])
 htf_ob_bolgesinde=bool(ilk_k['htf_ob_bolgesinde'])
 htf_ote_bolgesinde=bool(ilk_k['htf_ote_bolgesinde'])
 htf_qml_bolgesinde=bool(ilk_k['htf_qml_bolgesinde'])
 htf_oncelikli_bolge_sayisi=int(ilk_k['birincil_bolge_sayisi'])
 htf_oncelikli_bolge_onay=bool(ilk_k['ilk_kontrol_gecti'])
 hedef_tur='TALEP'if g else'ARZ'
 htf_sp=F(aP.get('strong_point')or 0.0)
 htf_bos_raw=aP.get('kysy_meta',{}).get('bos_list',[])
 # ADIM 2 (YEDEK GİRİŞ YERLERİ): EĞER ARZ/TALEP, OB, OTE VE QML YOKSA KULLANILACAK DİĞER GİRİŞ YERLERİ (BOS, CHoCH, ITZ, Magic Line)
 choch_list=[b for b in htf_bos_raw if b[4]==B and('CHOCH'in str(b[5])or'MSB'in str(b[5]))]
 choch_lvl=F(choch_list[-1][1])if choch_list else 0.0
 choch_orig=F(choch_list[-1][3])if choch_list else 0.0
 son_kir_tip=str(aP.get('kysy_meta',{}).get('son_kirilim_tipi',''))
 aktif_yapi_choch=bool(('CHOCH'in son_kir_tip or'MSB'in son_kir_tip or aP.get('external_msb'))and aP.get('yon')==B)
 htf_choch_noktasinda=bool((choch_lvl>0 and(A(de-choch_lvl)<=E_htf*0.32 or A(ak-choch_lvl)<=E_htf*0.32))or(choch_orig>0 and(A(de-choch_orig)<=E_htf*0.38 or A(ak-choch_orig)<=E_htf*0.38)))
 bos_only_list=[b for b in htf_bos_raw if b[4]==B and'BOS'in str(b[5])and'CHOCH'not in str(b[5])]
 bos_lvl=F(bos_only_list[-1][1])if bos_only_list else 0.0
 bos_orig=F(bos_only_list[-1][3])if bos_only_list else(htf_sp if htf_sp>0 else 0.0)
 htf_bos_noktasinda=bool((bos_orig>0 and(A(de-bos_orig)<=E_htf*0.38 or A(ak-bos_orig)<=E_htf*0.38))or(bos_lvl>0 and(A(de-bos_lvl)<=E_htf*0.32 or A(ak-bos_lvl)<=E_htf*0.32)))
 htf_ist=aP.get('uc_istasyon',{})
 htf_itz_lvl=F(htf_ist.get('ITZ')or 0.0)
 htf_itz_bolgesinde=bool(htf_itz_lvl>0 and(A(de-htf_itz_lvl)<=E_htf*0.28 or A(ak-htf_itz_lvl)<=E_htf*0.28))
 htf_magic_lvl=F(aP.get('fl_dp_meta',{}).get('magic_line')or htf_ist.get('FL')or aP.get('break_line_fl')or 0.0)
 htf_magic_line_bolgesinde=bool(htf_magic_lvl>0 and(A(de-htf_magic_lvl)<=E_htf*0.28 or A(ak-htf_magic_lvl)<=E_htf*0.28))
 htf_ikincil_bolge_sayisi=sum([int(htf_bos_noktasinda),int(htf_choch_noktasinda),int(htf_itz_bolgesinde),int(htf_magic_line_bolgesinde)])
 htf_ikincil_bolge_onay=(htf_ikincil_bolge_sayisi>=1)
 htf_bolge_sayisi=htf_oncelikli_bolge_sayisi+htf_ikincil_bolge_sayisi
 htf_zorunlu_bolge_onay=bool(htf_oncelikli_bolge_onay or(IKINCIL_BOLGE_GIRIS_AKTIF and htf_ikincil_bolge_onay))
 yon_kisa='BULL'if g else'BEAR'
 htf_yon_imbalance=[im for im in htf_imb_list if im.get('yon')==yon_kisa]
 htf_imbalance_sayisi=L(htf_yon_imbalance)+sum(1 for p in f4h if'FVG'in p or'LiqVoid'in p or'VIB'in p or'Gap'in p)
 htf_lq_l,htf_sfp_l,htf_lq_m=_likidite_ve_sfp_yapilarini_bul(bS,aP.get('highs'),aP.get('lows'))
 eq_havuz=L(htf_lq_m.get('aktif_eqh',[]))+L(htf_lq_m.get('aktif_eql',[]))+L(htf_lq_m.get('swept_eql'if g else'swept_eqh',[]))
 tl_havuz=L(htf_lq_m.get('trendline_bsl',[]))+L(htf_lq_m.get('trendline_ssl',[]))
 idm_havuz=1 if(htf_lq_m.get('swept_idm_bull'if g else'swept_idm_bear')is not None or htf_lq_m.get('aktif_idm_ssl'if g else'aktif_idm_bsl')is not None)else 0
 sfp_htf=1 if(htf_lq_m.get('son_bull_sfp'if g else'son_bear_sfp')is not None)else 0
 ext_var=1 if(htf_lq_m.get('ext_bsl'if g else'ext_ssl')is not None)else 0
 htf_likidite_sayisi=eq_havuz+tl_havuz+idm_havuz+sfp_htf+ext_var
 mtf_yon_onay=bool(Q.get('yon')==B or Q.get('external_yon')==B or Q.get('internal_yon')==B)
 # ADIM 3: LTF ONAY BULMA (REVERSAL KIRILIMLAR & REVERSAL MUM KONSEPTLERİ)
 ltf_kysy=aj.get('kysy_meta',{})
 ltf_son_bos_yon=ltf_kysy.get('son_kirilim_yon','NOTR')
 ltf_son_kir_tip=str(ltf_kysy.get('son_kirilim_tipi',''))
 ltf_int_choch=str(aj.get('internal_choch','YOK'))
 ltf_kirilim_listesi=[]
 for p_k in(kk+q8):
  if any(x in p_k for x in('CHoCH','MSB','BOS','InsideBrk','Fakey','FakeSetup','Simple_W','ShortFormed_W','Extended_W','Simple_M','ShortFormed_M','Extended_M','AtNali','QMM_Flip','TersBayrak','TersFlag_Flip','W_Kink','M_Kink')):
   if p_k not in ltf_kirilim_listesi:ltf_kirilim_listesi.append(p_k)
 if yon_kisa in ltf_int_choch and ltf_int_choch not in ltf_kirilim_listesi:
  ltf_kirilim_listesi.append(ltf_int_choch)
 if aj.get('yon')==B and ltf_son_bos_yon==B and ltf_son_kir_tip and ltf_son_kir_tip!='YOK':
  if ltf_son_kir_tip not in ltf_kirilim_listesi:ltf_kirilim_listesi.append(f"LTF_{ltf_son_kir_tip}")
 ltf_reversal_kirilim_onay=bool(L(ltf_kirilim_listesi)>0)
 ltf_mum_listesi=[]
 for p_m in(kk+q8):
  if any(x in p_m for x in('Engulf','Outside','MeraMera','Pinbar','Spike','Railroad','Star','MorningStar','EveningStar','BosaltDoldur','Marubozu','YingYang','Bobin','Fakey','FakeSetup')):
   if p_m not in ltf_mum_listesi:ltf_mum_listesi.append(p_m)
 if(htf_oncelikli_bolge_onay or scalp_aktif)and not ltf_mum_listesi and L(aY)>=4:
  c_s1,o_s1,h_s1,l_s1=(_f(aY,'close',-2),_f(aY,'open',-2),_f(aY,'high',-2),_f(aY,'low',-2))
  c_s0,o_s0,h_s0,l_s0=(_f(aY,'close',-3),_f(aY,'open',-3),_f(aY,'high',-3),_f(aY,'low',-3))
  alt_ig1=N(o_s1,c_s1)-l_s1;ust_ig1=h_s1-M(o_s1,c_s1)
  if g and((c_s1>o_s1 and(c_s1-o_s1)>=E_ltf*0.24 and(c_s1>=M(o_s0,c_s0)or ak>=c_s1))or(htf_oncelikli_bolge_onay and alt_ig1>=E_ltf*0.30 and ak>=o_s1)):
   ltf_mum_listesi.append(f"{LTF_PERIYOT}_BirincilBolge_Tepki_Mumu"if htf_oncelikli_bolge_onay else f"{LTF_PERIYOT}_Scalp_Momentum_Mum")
  elif(not g)and((c_s1<o_s1 and(o_s1-c_s1)>=E_ltf*0.24 and(c_s1<=N(o_s0,c_s0)or ak<=c_s1))or(htf_oncelikli_bolge_onay and ust_ig1>=E_ltf*0.30 and ak<=o_s1)):
   ltf_mum_listesi.append(f"{LTF_PERIYOT}_BirincilBolge_Tepki_Mumu"if htf_oncelikli_bolge_onay else f"{LTF_PERIYOT}_Scalp_Momentum_Mum")
 ltf_reversal_mum_onay=bool(L(ltf_mum_listesi)>0)
 ltf_choch_var=bool(ltf_reversal_kirilim_onay)
 ltf_qml_lvl=F(aj.get('qml_seviyesi')or aj.get('qm_meta',{}).get('qml_seviyesi')or 0.0)
 ltf_qml_temas=bool((ltf_qml_lvl>0 and A(de-ltf_qml_lvl)<=E_ltf*1.85 and(ak>=ltf_qml_lvl-E_ltf*0.5 if g else ak<=ltf_qml_lvl+E_ltf*0.5))or any('QM'in p or'MPL'in p or'MeraMera'in p for p in(q8+kk)))
 ltf_ist=aj.get('uc_istasyon',{})
 ltf_fl_lvl=F(aj.get('fl_dp_meta',{}).get('magic_line')or ltf_ist.get('FL')or ltf_kysy.get('son_kirilim_seviye')or 0.0)
 ltf_itz_lvl=F(ltf_ist.get('ITZ')or 0.0)
 ltf_kirilim_yeri_temas=bool((ltf_fl_lvl>0 and A(de-ltf_fl_lvl)<=E_ltf*1.85)or(ltf_itz_lvl>0 and A(de-ltf_itz_lvl)<=E_ltf*1.85)or L(q8)>0 or L(ra)>0 or ltf_reversal_kirilim_onay)
 ltf_a_choch_kirilim_yeri=bool(ltf_reversal_kirilim_onay and ltf_kirilim_yeri_temas)
 ltf_b_choch_qml_seviyesi=bool(ltf_reversal_kirilim_onay and ltf_qml_temas)
 ltf_c_mum_yapisi=bool(ltf_reversal_mum_onay)
 ltf_herhangi_tetik=bool(ltf_reversal_kirilim_onay or ltf_reversal_mum_onay)
 alt_tetik_kodlari=[]
 if ltf_reversal_kirilim_onay:alt_tetik_kodlari.append(f"LTF_Reversal_Kirilim({'/'.join(ltf_kirilim_listesi[:2])})")
 if ltf_reversal_mum_onay:alt_tetik_kodlari.append(f"LTF_Reversal_Mum({'/'.join(ltf_mum_listesi[:2])})")
 if ltf_b_choch_qml_seviyesi and'LTF_QML'not in'/'.join(alt_tetik_kodlari):alt_tetik_kodlari.append('LTF_CHoCH+QML')
 # 1. ÖNCELİK (ARZ/TALEP, OB, OTE, QML) vs 2. KADEME YEDEK GİRİŞ ŞARTLARI
 sart1_htf_poi_giris=bool(htf_arz_talep_bolgesinde and ltf_herhangi_tetik)
 sart2_htf_ob_giris=bool(htf_ob_bolgesinde and ltf_herhangi_tetik)
 sart3_htf_ote_giris=bool(htf_ote_bolgesinde and ltf_herhangi_tetik)
 sart4_htf_qml_giris=bool(htf_qml_bolgesinde and ltf_herhangi_tetik)
 ikincil_cift_ltf_tetik=bool((not htf_oncelikli_bolge_onay)and ltf_reversal_kirilim_onay and ltf_reversal_mum_onay and mtf_yon_onay)
 sart5_htf_choch_giris=bool(htf_choch_noktasinda and ikincil_cift_ltf_tetik)
 sart6_htf_bos_giris=bool(htf_bos_noktasinda and ikincil_cift_ltf_tetik)
 sart7_htf_itz_giris=bool(htf_itz_bolgesinde and ikincil_cift_ltf_tetik)
 sart8_htf_magic_giris=bool(htf_magic_line_bolgesinde and ikincil_cift_ltf_tetik)
 oncelikli_giris_sart_sayisi=sum([int(sart1_htf_poi_giris),int(sart2_htf_ob_giris),int(sart3_htf_ote_giris),int(sart4_htf_qml_giris)])
 ikincil_giris_sart_sayisi=sum([int(sart5_htf_choch_giris),int(sart6_htf_bos_giris),int(sart7_htf_itz_giris),int(sart8_htf_magic_giris)])
 saglanan_giris_sart_sayisi=oncelikli_giris_sart_sayisi+(ikincil_giris_sart_sayisi if IKINCIL_BOLGE_GIRIS_AKTIF else 0)
 saglanan_alt_kural_sayisi=saglanan_giris_sart_sayisi*M(1,L(alt_tetik_kodlari))
 en_yakin_birincil_atr=F(ilk_k['en_yakin_birincil_atr'])
 birincil_pusuda_onay=bool(ilk_k['birincil_pusuda_onay'])
 birincil_olcek_carpani_etkin=F(ilk_k['birincil_olcek_carpani_etkin'])
 birincil_radar_kademesi=(3 if(htf_oncelikli_bolge_onay and ltf_herhangi_tetik)else(2 if htf_oncelikli_bolge_onay else(1 if birincil_pusuda_onay else 0)))
 # 10,000 PUANLIK ÖLÇEK SKORU HESABI (1. ÖNCELİK: 5000-10000p | PUSUDA: 1800-4200p | 2. KADEME YEDEK: 150-480p)
 if htf_oncelikli_bolge_onay:
  birincil_olcek_skoru=N(10000,int(ilk_k['birincil_olcek_skoru'])+(350 if ltf_herhangi_tetik else 0)+(180 if(ltf_reversal_kirilim_onay and ltf_reversal_mum_onay)else 0))
 elif birincil_pusuda_onay:
  birincil_olcek_skoru=int(ilk_k['birincil_olcek_skoru'])
 elif htf_ikincil_bolge_onay:
  birincil_olcek_skoru=N(480,150+htf_ikincil_bolge_sayisi*65+(70 if ltf_herhangi_tetik else 0))
 else:
  birincil_olcek_skoru=0
 htf_safe_puan=N(100,int(R((22 if htf_yon_ok else 0)+htf_oncelikli_bolge_sayisi*24.0+htf_ikincil_bolge_sayisi*2.5+(14 if ltf_reversal_kirilim_onay else 0)+(14 if ltf_reversal_mum_onay else 0),0)))
 if not htf_oncelikli_bolge_onay and htf_ikincil_bolge_onay:
  htf_safe_puan=N(58,htf_safe_puan)
 if htf_oncelikli_bolge_sayisi>=4:
  htf_safe_derecesi=f"💎 1.ÖNCELİK 4/4 TAM BÖLGE ({birincil_olcek_carpani_etkin:.1f}x ULTRA SAFE A++++)"
 elif htf_oncelikli_bolge_sayisi==3:
  htf_safe_derecesi=f"👑 1.ÖNCELİK 3/4 ANA BÖLGE ({birincil_olcek_carpani_etkin:.1f}x ÇOK SAFE A+++)"
 elif htf_oncelikli_bolge_sayisi==2:
  htf_safe_derecesi=f"🔥 1.ÖNCELİK 2/4 ÇİFTE BÖLGE ({birincil_olcek_carpani_etkin:.1f}x SAFE A++)"
 elif htf_oncelikli_bolge_sayisi==1:
  htf_safe_derecesi=f"🎯 1.ÖNCELİK ANA BÖLGE ({birincil_olcek_carpani_etkin:.1f}x SAFE A+)"
 elif htf_ikincil_bolge_onay:
  htf_safe_derecesi="🧭 2.KADEME YEDEK BÖLGE (0.35x BOS/CHoCH/ITZ/FL)"
 elif birincil_pusuda_onay:
  htf_safe_derecesi=f"🔭 1.ÖNCELİK PUSUDA ({en_yakin_birincil_atr:.1f}x ATR Yakında)"
 else:
  htf_safe_derecesi="🔴 BÖLGE DIŞI (GİRİLMEZ)"
 aktif_htf_bolgeler=[]
 aktif_birincil_bolgeler=list(ilk_k['aktif_birincil_bolgeler'])
 if htf_qml_bolgesinde:aktif_htf_bolgeler.append(f"QML({htf_qml_lvl:.4f})"if htf_qml_lvl>0 else"QML")
 if htf_ob_bolgesinde:aktif_htf_bolgeler.append("OB")
 if htf_arz_talep_bolgesinde:aktif_htf_bolgeler.append(f"Fresh_{hedef_tur}")
 if htf_ote_bolgesinde:aktif_htf_bolgeler.append("OTE")
 if htf_bos_noktasinda:aktif_htf_bolgeler.append("BOS_Noktasi")
 if htf_choch_noktasinda:aktif_htf_bolgeler.append("CHoCH_Noktasi")
 if htf_itz_bolgesinde:aktif_htf_bolgeler.append("ITZ")
 if htf_magic_line_bolgesinde:aktif_htf_bolgeler.append("MagicLine")
 oncelik_vektor=tuple(ilk_k['oncelik_vektor'])
 giris_oncelik_vektor=(int(sart4_htf_qml_giris),int(sart2_htf_ob_giris),int(sart1_htf_poi_giris),int(sart3_htf_ote_giris))
 ikincil_vektor=(int(htf_bos_noktasinda),int(htf_choch_noktasinda),int(htf_itz_bolgesinde),int(htf_magic_line_bolgesinde))
 en_yuksek_oncelik_sira=(1 if htf_qml_bolgesinde else 2 if htf_ob_bolgesinde else 3 if htf_arz_talep_bolgesinde else 4 if htf_ote_bolgesinde else(5 if htf_ikincil_bolge_onay else(6 if birincil_pusuda_onay else 9)))
 en_yuksek_oncelik_etiket=(f"1.ÖNCELİK ({htf_oncelikli_bolge_sayisi}/4 [{birincil_olcek_carpani_etkin:.1f}x]: {'+'.join(aktif_birincil_bolgeler)})"if htf_oncelikli_bolge_onay else('2.Kademe Yedek [0.35x]: BOS/CHoCH/ITZ/Magic'if htf_ikincil_bolge_onay else(f"1.Öncelik Pusuda ({en_yakin_birincil_atr:.1f}x ATR)"if birincil_pusuda_onay else'Bölge Dışı')))
 aktif_ltf_tetikler=list(alt_tetik_kodlari)
 checklist_dict={'ilk_kontrol_gecti':bool(htf_oncelikli_bolge_onay),'yon_ok':bool(htf_yon_ok),'qml':bool(htf_qml_bolgesinde),'qml_fiyat':f"{htf_qml_lvl:.4f}"if htf_qml_lvl>0 else'-','ote':bool(htf_ote_bolgesinde),'ote_aralik':f"{N(ote_lo,ote_hi):.4f}-{M(ote_lo,ote_hi):.4f}"if ote_hi>0 and ote_lo>0 else'-','ob':bool(htf_ob_bolgesinde),'ob_aralik':f"{N(ob_lo,ob_hi):.4f}-{M(ob_lo,ob_hi):.4f}"if ob_hi>0 and ob_lo>0 else'-','fresh_arz_talep':bool(htf_arz_talep_bolgesinde),'fresh_aralik':f"{N(fresh_lo,fresh_hi):.4f}-{M(fresh_lo,fresh_hi):.4f}"if fresh_hi>0 and fresh_lo>0 else'-','choch_noktasi':bool(htf_choch_noktasinda),'choch_fiyat':f"{choch_lvl:.4f}"if choch_lvl>0 else(f"Origin:{choch_orig:.4f}"if choch_orig>0 else'-'),'bos_noktasi':bool(htf_bos_noktasinda),'bos_fiyat':f"{bos_lvl:.4f} (Origin:{bos_orig:.4f})"if bos_lvl>0 and bos_orig>0 else(f"{bos_orig:.4f}"if bos_orig>0 else'-'),'itz':bool(htf_itz_bolgesinde),'itz_fiyat':f"{htf_itz_lvl:.4f}"if htf_itz_lvl>0 else'-','magic_line':bool(htf_magic_line_bolgesinde),'magic_fiyat':f"{htf_magic_lvl:.4f}"if htf_magic_lvl>0 else'-','ltf_reversal_kirilim':bool(ltf_reversal_kirilim_onay),'ltf_reversal_mum':bool(ltf_reversal_mum_onay),'safe_sayisi':int(htf_bolge_sayisi),'safe_puan':int(htf_safe_puan),'safe_derece':htf_safe_derecesi,'birincil_olcek_skoru':int(birincil_olcek_skoru),'birincil_olcek_carpani':F(birincil_olcek_carpani_etkin)}
 htf_trend_degistiren_nokta=F(htf_bos_raw[-1][3])if htf_bos_raw else F(aP.get('strong_point')or(sMin if g else sMax))
 if g:
  if htf_sp>0 and htf_trend_degistiren_nokta>0:htf_trend_degistiren_nokta=N(htf_trend_degistiren_nokta,htf_sp,sMin if sMin>0 else htf_sp)
 else:
  if htf_sp>0 and htf_trend_degistiren_nokta>0:htf_trend_degistiren_nokta=M(htf_trend_degistiren_nokta,htf_sp,sMax if sMax>0 else htf_sp)
 return{'ilk_kontrol_birincil_4_bolge_mi':htf_oncelikli_bolge_onay,'hedef_yon':B,'htf_yon_ok':htf_yon_ok,'mtf_yon_onay':mtf_yon_onay,'htf_zorunlu_bolge_onay':htf_zorunlu_bolge_onay,'htf_arz_talep_bolgesinde':htf_arz_talep_bolgesinde,'htf_ob_bolgesinde':htf_ob_bolgesinde,'htf_ote_bolgesinde':htf_ote_bolgesinde,'htf_qml_bolgesinde':htf_qml_bolgesinde,'htf_choch_noktasinda':htf_choch_noktasinda,'htf_bos_noktasinda':htf_bos_noktasinda,'htf_itz_bolgesinde':htf_itz_bolgesinde,'htf_magic_line_bolgesinde':htf_magic_line_bolgesinde,'htf_bolge_sayisi':htf_bolge_sayisi,'htf_safe_puan':htf_safe_puan,'htf_safe_derecesi':htf_safe_derecesi,'aktif_htf_bolgeler':aktif_htf_bolgeler,'htf_imbalance_sayisi':htf_imbalance_sayisi,'htf_likidite_sayisi':htf_likidite_sayisi,'ltf_choch_var':ltf_choch_var,'ltf_reversal_kirilim_onay':ltf_reversal_kirilim_onay,'ltf_reversal_mum_onay':ltf_reversal_mum_onay,'ltf_kirilim_listesi':ltf_kirilim_listesi,'ltf_mum_listesi':ltf_mum_listesi,'ltf_herhangi_tetik':ltf_herhangi_tetik,'ltf_qml_giris':ltf_b_choch_qml_seviyesi,'ltf_kirilim_yeri_giris':ltf_a_choch_kirilim_yeri,'ltf_mum_yapisi_giris':ltf_c_mum_yapisi,'aktif_ltf_tetikler':aktif_ltf_tetikler,'sart1_htf_poi_giris':sart1_htf_poi_giris,'sart2_htf_ob_giris':sart2_htf_ob_giris,'sart3_htf_ote_giris':sart3_htf_ote_giris,'sart4_htf_qml_giris':sart4_htf_qml_giris,'sart5_htf_choch_giris':sart5_htf_choch_giris,'sart6_htf_bos_giris':sart6_htf_bos_giris,'sart7_htf_itz_giris':sart7_htf_itz_giris,'sart8_htf_magic_giris':sart8_htf_magic_giris,'htf_oncelikli_bolge_onay':htf_oncelikli_bolge_onay,'htf_oncelikli_bolge_sayisi':htf_oncelikli_bolge_sayisi,'oncelikli_giris_sart_sayisi':oncelikli_giris_sart_sayisi,'htf_ikincil_bolge_onay':htf_ikincil_bolge_onay,'htf_ikincil_bolge_sayisi':htf_ikincil_bolge_sayisi,'ikincil_giris_sart_sayisi':ikincil_giris_sart_sayisi,'oncelik_vektor':oncelik_vektor,'giris_oncelik_vektor':giris_oncelik_vektor,'ikincil_vektor':ikincil_vektor,'en_yuksek_oncelik_sira':en_yuksek_oncelik_sira,'en_yuksek_oncelik_etiket':en_yuksek_oncelik_etiket,'bolge_kademesi':(1 if htf_oncelikli_bolge_onay else(2 if htf_ikincil_bolge_onay else 0)),'saglanan_giris_sart_sayisi':saglanan_giris_sart_sayisi,'saglanan_alt_kural_sayisi':saglanan_alt_kural_sayisi,'htf_trend_degistiren_nokta':htf_trend_degistiren_nokta,'birincil_olcek_skoru':birincil_olcek_skoru,'birincil_olcek_carpani_etkin':birincil_olcek_carpani_etkin,'birincil_radar_kademesi':birincil_radar_kademesi,'birincil_pusuda_onay':birincil_pusuda_onay,'en_yakin_birincil_atr':en_yakin_birincil_atr,'aktif_birincil_bolgeler':aktif_birincil_bolgeler,'checklist':checklist_dict}
def konum_ve_karar_bolgesi_filtresi(bS,bw,aY,aP,Q,aj,f4h,f6,q8,hN,q7,ra,kk,B='BULLISH'):
 adim=_htf_adimlari_ve_ltf_tetik_kontrolu(bS,bw,aY,aP,Q,aj,f4h,f6,q8,hN,q7,ra,kk,B)
 konum_onay=bool(adim['htf_zorunlu_bolge_onay'])
 flip_var=any(x in p for p in(f4h+f6+q8)for x in('Flip','TersFlag','TersBayrak','QMM_Flip','VIB_Flip','Breakaway_Gap','1Mum_FTR','FirstObstacle_FO','IFVG'))
 if not konum_onay:
  durum='RED_HTF_BOLGE_DISI_YASAK'
  senaryo='HTF_1_ONCELIK_ARZ_TALEP_OB_OTE_QML_BEKLENIYOR'
  aciklama=f"[1.ÖNCELİK FİLTRESİ RED] Fiyat HTF ({HTF_PERIYOT.upper()}) Arz/Talep, OB, OTE, QML (veya yedek BOS/CHoCH/ITZ/Magic) bölgesinde değil!"
 else:
  bolge_str='+'.join(adim['aktif_htf_bolgeler'])
  kademe_str=f"1.ÖNCELİK_{adim['htf_oncelikli_bolge_sayisi']}_4({adim['birincil_olcek_skoru']}/10000p)"if adim['htf_oncelikli_bolge_onay']else f"2.KADEME_YEDEK({adim['birincil_olcek_skoru']}/10000p)"
  durum=f"ONAY_{kademe_str}[{bolge_str}]"
  senaryo=f"{adim['htf_safe_derecesi']} | Ölçek:{adim['birincil_olcek_skoru']}/10000p"if adim['saglanan_giris_sart_sayisi']>0 else f"HTF_BOLGEDE({bolge_str})_LTF_ONAY_BEKLENIYOR"
  aciklama=f"[{kademe_str} -> {adim['htf_safe_derecesi']}] LTF Onay: {'+'.join(adim['aktif_ltf_tetikler'])or'Reversal Kırılım / Mum Bekleniyor'}"
 adim.update({'konum_onay':konum_onay,'konum_durumu':durum,'karar_senaryosu':senaryo,'htf_poi_aktif':adim['htf_arz_talep_bolgesinde']or adim['htf_ob_bolgesinde'],'mtf_poi_aktif':L(f6)>0 or L(q7)>0,'fibo_konum_uygun':adim['htf_ote_bolgesinde'],'flip_devam_mi':flip_var,'ters_bolge_engeli':not konum_onay,'tuzak_choch_mu':bool(adim['ltf_choch_var']and not konum_onay),'aciklama':aciklama})
 return adim
def stop_noktasi_belirle(bS,bw,aY,aP,Q,aj,kFlt,P,B='BULLISH',sl4h=None,f7=None,q9=None,al_ltf=None,mod=None):
 sec_mod=str(mod or STOP_BELIRLEME_MODU)
 g=(B=='BULLISH')
 E_htf=M(_f(bS,'atr',-2)if bS is not None and'atr'in bS.columns else P*0.003,P*0.0015)
 E_ltf=M(_f(aY,'atr',-2)if aY is not None and'atr'in aY.columns else P*0.0015,P*0.0008)
 htf_td=F(kFlt.get('htf_trend_degistiren_nokta')or 0.0)if I(kFlt,dict)else 0.0
 htf_sp=F(aP.get('strong_point')or 0.0)if I(aP,dict)else 0.0
 htf_sw=F((aP.get('swing_min')if g else aP.get('swing_max'))or 0.0)if I(aP,dict)else 0.0
 htf_poi_sl=F(sl4h or 0.0)if I(sl4h,(int,F))else 0.0
 if g:
  htf_adaylar=[x for x in(htf_td,htf_sp,htf_sw,htf_poi_sl)if 0<x<P]
  htf_baz=N(htf_adaylar)if htf_adaylar else(htf_td if htf_td>0 and htf_td<P else P*0.988)
  al_htf=R(N(htf_baz-E_htf*0.15,P*(1.0-aW)),6)
 else:
  htf_adaylar=[x for x in(htf_td,htf_sp,htf_sw,htf_poi_sl)if x>P]
  htf_baz=M(htf_adaylar)if htf_adaylar else(htf_td if htf_td>P else P*1.012)
  al_htf=R(M(htf_baz+E_htf*0.15,P*(1.0+aW)),6)
 v10=aj.get('v10_meta',{})if I(aj,dict)else{}
 v12=aj.get('v12_meta',{})if I(aj,dict)else{}
 v13=aj.get('v13_meta',{})if I(aj,dict)else{}
 ltf_ist=aj.get('uc_istasyon',{})if I(aj,dict)else{}
 ltf_sp=F(aj.get('strong_point')or 0.0)if I(aj,dict)else 0.0
 ltf_itz=F(ltf_ist.get('ITZ')or 0.0)
 ltf_poi_sl=F(q9 or 0.0)if I(q9,(int,F))else 0.0
 ltf_pa_sl=F(al_ltf or 0.0)if I(al_ltf,(int,F))else 0.0
 ib_sl=0.0
 if v12.get('dar_sl_4r')and I(v12.get('ib_low'if g else'ib_high'),(int,F)):
  ib_sl=F(v12['ib_low'])-E_ltf*0.12 if g else F(v12['ib_high'])+E_ltf*0.12
 elif I(v12.get('mb_low'if g else'mb_high'),(int,F))and v12.get('inside_bar_durumu','YOK')!='YOK':
  ib_sl=F(v12['mb_low'])-E_ltf*0.15 if g else F(v12['mb_high'])+E_ltf*0.15
 bobin_sl=0.0
 if I(v10.get('bobin_alt'if g else'bobin_ust'),(int,F)):
  bobin_sl=F(v10['bobin_alt'])-E_ltf*0.18 if g else F(v10['bobin_ust'])+E_ltf*0.18
 ltf_sw_son=0.0
 if I(aj,dict):
  sw_l=aj.get('lows'if g else'highs',[])
  if sw_l:ltf_sw_son=F(sw_l[-1][1])
 ltf_mum_uc=0.0
 if aY is not None and L(aY)>=6:
  ltf_mum_uc=F(aY['low'].iloc[-6:].min())-E_ltf*0.22 if g else F(aY['high'].iloc[-6:].max())+E_ltf*0.22
 min_ltf_mes=M(E_ltf*0.55,P*aW)
 max_ltf_mes=M(E_ltf*3.2,P*(0.008 if ISLEM_TARZI_MODU=='Scalp'else 0.022))
 if g:
  ltf_ham_adaylar=[x for x in(ib_sl,ltf_poi_sl,ltf_itz-E_ltf*0.25 if ltf_itz>0 else 0.0,bobin_sl,ltf_sp-E_ltf*0.2 if ltf_sp>0 else 0.0,ltf_sw_son-E_ltf*0.2 if ltf_sw_son>0 else 0.0,ltf_mum_uc,ltf_pa_sl)if 0<x<P]
  ltf_sec=M(ltf_ham_adaylar)if v12.get('dar_sl_4r')and ib_sl>0 and ib_sl<P else(ltf_poi_sl if 0<ltf_poi_sl<P else(ltf_mum_uc if 0<ltf_mum_uc<P else(N(ltf_ham_adaylar)if ltf_ham_adaylar else P-min_ltf_mes)))
  mes_ltf=M(min_ltf_mes,N(max_ltf_mes,P-ltf_sec))
  al_ltf_son=R(P-mes_ltf,6)
 else:
  ltf_ham_adaylar=[x for x in(ib_sl,ltf_poi_sl,ltf_itz+E_ltf*0.25 if ltf_itz>0 else 0.0,bobin_sl,ltf_sp+E_ltf*0.2 if ltf_sp>0 else 0.0,ltf_sw_son+E_ltf*0.2 if ltf_sw_son>0 else 0.0,ltf_mum_uc,ltf_pa_sl)if x>P]
  ltf_sec=N(ltf_ham_adaylar)if v12.get('dar_sl_4r')and ib_sl>P else(ltf_poi_sl if ltf_poi_sl>P else(ltf_mum_uc if ltf_mum_uc>P else(M(ltf_ham_adaylar)if ltf_ham_adaylar else P+min_ltf_mes)))
  mes_ltf=M(min_ltf_mes,N(max_ltf_mes,ltf_sec-P))
  al_ltf_son=R(P+mes_ltf,6)
 if'LTF'in sec_mod and'Otomatik'not in sec_mod:
  return(al_ltf_son,f'LTF Yapısal Stop ({LTF_PERIYOT} Kırılım/Mum/POI + ATR Kalkanı)')
 if'Otomatik'in sec_mod:
  ltf_onay_aktif=bool((I(kFlt,dict)and(kFlt.get('ltf_reversal_kirilim_onay')or kFlt.get('ltf_reversal_mum_onay')))or v12.get('dar_sl_4r')or v13.get('aktif_entry_modeli','Beklemede')!='Beklemede'or ISLEM_TARZI_MODU=='Scalp')
  if ltf_onay_aktif:
   return(al_ltf_son,f'Otomatik -> LTF Yapısal Stop ({LTF_PERIYOT} Onaylı Kırılım/Mum)')
  return(al_htf,f'Otomatik -> HTF Yapısal Stop ({HTF_PERIYOT.upper()} Dip/Tepe & OB)')
 return(al_htf,f'HTF Yapısal Stop ({HTF_PERIYOT.upper()} Dip/Tepe & OB)')
def tek_yon_4_atli_hesapla(J,bS,bw,aY,aP,Q,aj,B='BULLISH'):
 fj=[];bT=[];b2=0;aP['sembol'],Q['sembol'],aj['sembol']=(J,J,J)
 # İLK ADIM: FİYATIN ARZ/TALEP, OB, OTE VE QML BÖLGESİNDE OLUP OLMADIĞINI İLK KONTROL KAPISIYLA DENETLE
 f4h,sl4h,em4h,hN,e4h=poi_ve_bolge_analizi(bS,aP,HTF_PERIYOT.upper(),B);f6,f7,em,q7,e0=poi_ve_bolge_analizi(bw,Q,MTF_PERIYOT.upper(),B);q8,q9,dD,ra,en=poi_ve_bolge_analizi(aY,aj,LTF_PERIYOT,B);b8=f4h+f6+q8;oZ=M(e4h,e0,en)
 dn,hK,oa=likidite_smt_analizi(J,bw,aY,Q,B)
 hL,jQ,kj,dh=likidite_ve_sfp_analizi(bw,aY,Q,b8,B);Q['v8_meta']=dh
 for vs in jQ:
  if vs not in hK:hK.append(vs)
 oa.extend(kj)
 eM=sl4h if sl4h is not None else(f7 if f7 is not None else q9);mB_raw,kk,hM,P,al_ltf=ltf_pa_ve_giris_tetikleyici(aY,eM,B)
 son_kapanis_ltf=_f(aY,'close',-1)if L(aY)>0 else(_f(bw,'close',-1)if L(bw)>0 else 1.0)
 P=F(P)if I(P,(int,F))and F(P)>0 else F(son_kapanis_ltf)
 al_ltf=F(al_ltf)if I(al_ltf,(int,F))and F(al_ltf)>0 else R(P*(0.992 if B=='BULLISH'else 1.008),6)
 kFlt=konum_ve_karar_bolgesi_filtresi(bS,bw,aY,aP,Q,aj,f4h,f6,q8,hN,q7,ra,kk,B);Q['konum_meta'],aj['konum_meta']=(kFlt,kFlt)
 al,stop_kaynak_bilgi=stop_noktasi_belirle(bS,bw,aY,aP,Q,aj,kFlt,P,B,sl4h,f7,q9,al_ltf,STOP_BELIRLEME_MODU)
 kFlt['stop_kaynak_bilgi']=stop_kaynak_bilgi
 chk=kFlt.get('checklist',{})
 # 1. ATLI (0-25 Puan): YÖN BELİRLEMEK (HTF Ana Yön + MTF Uyum + OTE Konumu)
 if kFlt['htf_yon_ok']:
  b2+=15;fj.append(f"{HTF_PERIYOT.upper()}_YON:{B[:4]}");bT.append(f"✅ 1. Adım [Yön Belirleme - {HTF_PERIYOT.upper()}]: {aP['kirilim_tipi']} (+15p)")
 else:
  bT.append(f"⬜ 1. Adım [Yön Belirleme - {HTF_PERIYOT.upper()}]: HTF yönü {aP.get('yon')} ({B} ile uyumsuz) (0p)")
 if kFlt['mtf_yon_onay']:
  b2+=6;fj.append(f"{MTF_PERIYOT.upper()}_ONAY:{B[:4]}");bT.append(f"✅ Ara TF [{MTF_PERIYOT.upper()} Yön Onayı]: {Q['kirilim_tipi']} (+6p)")
 if kFlt['htf_ote_bolgesinde']:
  b2+=4
 b2=N(25,b2)
 # 2. ATLI (0-25 Puan): ÖLÇEKLENDİRİLMİŞ 1. ÖNCELİK (ARZ/TALEP, OB, OTE, QML: +16..+18p) vs 2. KADEME YEDEK (+2p)
 aO=0
 htf_kriter_log=[
  ('QML [1.ÖNCELİK ANA BÖLGE]',kFlt['htf_qml_bolgesinde'],chk.get('qml_fiyat','-'),18),
  ('OB [1.ÖNCELİK ANA BÖLGE]',kFlt['htf_ob_bolgesinde'],chk.get('ob_aralik','-'),17),
  ('Fresh Arz/Talep [1.ÖNCELİK ANA BÖLGE]',kFlt['htf_arz_talep_bolgesinde'],chk.get('fresh_aralik','-'),17),
  ('OTE [1.ÖNCELİK ANA BÖLGE]',kFlt['htf_ote_bolgesinde'],chk.get('ote_aralik','-'),16),
  ('BOS Yaptıran Nokta [2.Kademe Yedek]',kFlt['htf_bos_noktasinda'],chk.get('bos_fiyat','-'),2),
  ('CHoCH Yapılan Nokta [2.Kademe Yedek]',kFlt['htf_choch_noktasinda'],chk.get('choch_fiyat','-'),2),
  ('ITZ [2.Kademe Yedek]',kFlt['htf_itz_bolgesinde'],chk.get('itz_fiyat','-'),2),
  ('Magic Line [2.Kademe Yedek]',kFlt['htf_magic_line_bolgesinde'],chk.get('magic_fiyat','-'),2)
 ]
 for k_ad,k_ok,k_fiyat,k_puan in htf_kriter_log:
  if k_ok:
   aO+=k_puan;fj.append(f"HTF_{k_ad.split()[0]}");bT.append(f"✅ 2. Adım HTF Bölge [{k_ad}]: Sağlandı ({k_fiyat}) (+{k_puan}p)")
  else:
   bT.append(f"⬜ 2. Adım HTF Bölge [{k_ad}]: Sağlanmadı ({k_fiyat})")
 if kFlt['htf_oncelikli_bolge_onay']:
  aO=N(25,M(22,aO+7))
 elif kFlt['htf_ikincil_bolge_onay']:
  aO=N(6,aO)
 else:
  aO=0;bT.append(f"⛔ {kFlt['aciklama']}")
 bT.append(f"🛡️ 1.ÖNCELİK İLK KONTROL & ÖLÇEK: Arz/Talep+OB+OTE+QML={kFlt['htf_oncelikli_bolge_sayisi']}/4 ({'+'.join(kFlt.get('aktif_birincil_bolgeler',[]))or'Yok'}) | Toplam:{kFlt['htf_bolge_sayisi']}/8 -> {kFlt['htf_safe_derecesi']} (Ölçek Puanı: {kFlt.get('birincil_olcek_skoru',0)}/10000 | Çarpan: {kFlt.get('birincil_olcek_carpani_etkin',0.35):.2f}x) | Stop: {al:.4f}")
 bT.extend([f'HTF/MTF Bölge Detayı: {k}'for k in em4h+em+dD])
 # 3. ATLI (0-25 Puan): 1. ÖNCELİK YOĞUNLUĞU + HTF IMBALANCE & LİKİDİTE
 safe_ek_puan=N(18,kFlt['htf_oncelikli_bolge_sayisi']*7+(4 if kFlt['htf_oncelikli_bolge_onay']else 0))
 imb_puan=N(6,kFlt['htf_imbalance_sayisi']*3)
 liq_puan=N(7,kFlt['htf_likidite_sayisi']*2+(3 if dn>=8 else 0))
 dn_toplam=N(25,safe_ek_puan+imb_puan+liq_puan)
 fj.extend(hK);bT.extend([f'Likidite/SMT Detayı: {k}'for k in oa])
 # 4. ATLI (0-25 Puan): LTF ONAY (REVERSAL KIRILIMLAR & REVERSAL MUM KONSEPTLERİ)
 mB=0
 if kFlt['ltf_reversal_kirilim_onay']:
  mB+=14;fj.append(f"{LTF_PERIYOT}_Reversal_Kirilim")
  bT.append(f"✅ 3. Adım LTF Onay [Reversal Kırılımlar]: {', '.join(kFlt['ltf_kirilim_listesi'][:3])} (+14p)")
 else:
  bT.append(f"⬜ 3. Adım LTF Onay [Reversal Kırılımlar]: Henüz LTF CHoCH/MSB/i-BOS/M-W kırılımı yok")
 if kFlt['ltf_reversal_mum_onay']:
  mB+=14;fj.append(f"{LTF_PERIYOT}_Reversal_Mum")
  bT.append(f"✅ 3. Adım LTF Onay [Reversal Mum Konseptleri]: {', '.join(kFlt['ltf_mum_listesi'][:3])} (+14p)")
 else:
  bT.append(f"⬜ 3. Adım LTF Onay [Reversal Mum Konseptleri]: Henüz LTF Engulf/Pinbar/MeraMera/RR/BoşaltDoldur mum onayı yok")
 if not kFlt['htf_zorunlu_bolge_onay']or not kFlt['ltf_herhangi_tetik']:
  mB=N(6,mB)
 mB=N(25,mB)
 kural_ozet_str=f"1.Öncelik:{kFlt['htf_oncelikli_bolge_sayisi']}/4 ({kFlt['birincil_olcek_skoru']}/10000p) | Safe:{kFlt['htf_bolge_sayisi']}/8 | LTF:{'Kırılım+Mum'if(kFlt['ltf_reversal_kirilim_onay']and kFlt['ltf_reversal_mum_onay'])else'Reversal Kırılım'if kFlt['ltf_reversal_kirilim_onay']else'Reversal Mum'if kFlt['ltf_reversal_mum_onay']else'Bekleniyor'}"
 bT.insert(0,f"📊 [İLK KONTROL ÖZETİ]: 0.İlk Kontrol (Arz/Talep,OB,OTE,QML):{'✅ '+str(kFlt['htf_oncelikli_bolge_sayisi'])+'/4 ('+str(kFlt['birincil_olcek_skoru'])+'/10000p)'if kFlt['htf_oncelikli_bolge_onay']else'⬜ Yok (Yedek Kontrol)'} | 1.Yön:{'✅'if kFlt['htf_yon_ok']else'⬜'} | 2.Bölge:{'+'.join(kFlt['aktif_htf_bolgeler'])or'Yok'} | 3.LTF Onay:{'✅'if kFlt['ltf_herhangi_tetik']else'⬜'}")
 bT.extend([f'LTF Mum/PA Detayı: {k}'for k in hM])
 fj.insert(0,f"Safe:{kFlt['htf_bolge_sayisi']}/8({kFlt['htf_safe_puan']}p)")
 fj.extend(b8);fj.extend(kk)
 olcek_carp=M(0.8,F(BIRINCIL_BOLGE_OLCEK_CARPANI)/5.0)
 birincil_olcek_bonusu=int(R((12+kFlt['htf_oncelikli_bolge_sayisi']*7)*olcek_carp,0))if(kFlt['htf_oncelikli_bolge_onay']and kFlt['ltf_herhangi_tetik'])else(int(R(5*kFlt['htf_oncelikli_bolge_sayisi']*olcek_carp,0))if kFlt['htf_oncelikli_bolge_onay']else 0)
 nO=N(100,b2+aO+dn_toplam+mB+birincil_olcek_bonusu)
 if not kFlt['htf_zorunlu_bolge_onay']:
  nO=N(45,nO)
  di=f"🔭 1.Öncelik Pusuda ({kFlt.get('en_yakin_birincil_atr',9.9):.1f}x ATR)"if kFlt.get('birincil_pusuda_onay')else f"HTF Bölge Dışı ({HTF_PERIYOT.upper()} Arz/Talep, OB, OTE, QML Aranıyor)"
 elif kFlt['ltf_herhangi_tetik']:
  if kFlt['htf_oncelikli_bolge_onay']:
   if kFlt['htf_yon_ok']:
    nO=N(100,M(nO,MIN_CONFLUENCE_SKORU+6+kFlt['htf_oncelikli_bolge_sayisi']*4))
   di=f"🔥 1.ÖNCELİK [{kFlt['htf_oncelikli_bolge_sayisi']}/4 ({kFlt['birincil_olcek_skoru']}p): {'+'.join(kFlt.get('aktif_birincil_bolgeler',[]))}] + {'/'.join(kFlt['aktif_ltf_tetikler'][:2])}"
  else:
   nO=N(MIN_CONFLUENCE_SKORU,M(0,nO-10))if kFlt.get('ikincil_giris_sart_sayisi',0)>=2 else N(MIN_CONFLUENCE_SKORU-2,M(0,nO-14))
   di=f"🧭 2.KADEME YEDEK [{'+'.join(kFlt['aktif_htf_bolgeler'][:3])}] + {'/'.join(kFlt['aktif_ltf_tetikler'][:2])}"
 else:
  nO=N(M(54 if kFlt['htf_oncelikli_bolge_onay']else 46,MIN_CONFLUENCE_SKORU-4),nO)
  di=(f"🎯 1.ÖNCELİK BÖLGEDE ({kFlt['htf_oncelikli_bolge_sayisi']}/4: {'+'.join(kFlt.get('aktif_birincil_bolgeler',[]))}) -> {LTF_PERIYOT} Onay Bekleniyor"if kFlt['htf_oncelikli_bolge_onay']else f"🧭 2.Kademe Bölgede ({'+'.join(kFlt['aktif_htf_bolgeler'][:3])}) -> {LTF_PERIYOT} Onay Bekleniyor")
 dX=aj.get('v10_meta',Q.get('v10_meta',{}));dX['giris_onay_tipi']='+'.join(kFlt['aktif_ltf_tetikler'])if kFlt['aktif_ltf_tetikler']else'Beklemede'
 return{'hedef_yon':B,'skor':nO,'bolge_10p_skor':oZ,'giris_modeli':di,'atli_puanlar':(b2,aO,dn_toplam,mB),'giris':P,'sl':al,'detay_etiketleri':fj,'detayli_kurallar':bT,'kutular':ra+q7[:2],'kutular_15m':ra,'kutular_1h':q7,'kutular_4h':hN,'poi_4h':f4h,'poi_1h':f6,'poi_15m':q8,'konum_meta':kFlt,'uygun_kural_sayisi':kFlt['htf_bolge_sayisi'],'uygun_alt_kural_sayisi':kFlt['saglanan_alt_kural_sayisi'],'kural_ozeti':kural_ozet_str}
def mahserin_4_atlisi_confluence_analizi(J,bS,bw,aY,D=None):
 jR=D if D else'spot'if PIYASA_MODU=='spot'else'future';aP=market_yapisi_ve_fibo_analizi(bS);Q=market_yapisi_ve_fibo_analizi(bw);aj=market_yapisi_ve_fibo_analizi(aY,n=2)
 if jR!='future'or aP['yon']=='BULLISH':
  dQ=tek_yon_4_atli_hesapla(J,bS,bw,aY,aP,Q,aj,'BULLISH')
 elif aP['yon']=='BEARISH':
  dQ=tek_yon_4_atli_hesapla(J,bS,bw,aY,aP,Q,aj,'BEARISH')
 else:
  o5=tek_yon_4_atli_hesapla(J,bS,bw,aY,aP,Q,aj,'BULLISH');qe,qf=(dict(Q),dict(aj));rc=tek_yon_4_atli_hesapla(J,bS,bw,aY,aP,Q,aj,'BEARISH')
  if rc['skor']>o5['skor']:dQ=rc
  else:dQ=o5;Q.update(qe);aj.update(qf)
 iy=dQ['hedef_yon'];p1,p2,p3,p4=dQ['atli_puanlar'];nO=dQ['skor'];kFlt=dQ.get('konum_meta',{'konum_onay':False,'htf_zorunlu_bolge_onay':False,'saglanan_giris_sart_sayisi':0});kysy_ok=bool(aP.get('kysy_onay',True))
 if aP['yon']=='BEARISH'and Q['yon']=='BEARISH':mC='BEARISH'
 elif aP['yon']=='BULLISH'and Q['yon']=='BULLISH':mC='BULLISH'
 else:mC=aP['yon']if aP['yon']in('BULLISH','BEARISH')else iy
 # 3 ADIMLI KESİN GİRİŞ KURALI:
 # 1. HTF Yön Belirlendi (aP['yon'] == iy)
 # 2. HTF Bölge Belirlendi (8 HTF noktasından en az 1'i sağlandı: QML, OTE, OB, Fresh Arz/Talep, CHoCH Noktası, BOS Noktası, ITZ, Magic Line)
 # 3. Fiyat bu noktaya geldiğinde LTF Onay (Reversal Kırılım veya Reversal Mum Konsepti) bulundu!
 htf_bolge_ve_ltf_onay_ok=bool(kFlt.get('htf_zorunlu_bolge_onay',False)and kFlt.get('ltf_herhangi_tetik',False)and kFlt.get('saglanan_giris_sart_sayisi',0)>=1)
 aU='BEKLE'
 if htf_bolge_ve_ltf_onay_ok and kysy_ok and(nO>=MIN_CONFLUENCE_SKORU):
  if iy=='BULLISH'and aP['yon']=='BULLISH':aU='LONG';mC='BULLISH'
  elif iy=='BEARISH'and jR=='future'and aP['yon']=='BEARISH':aU='SHORT';mC='BEARISH'
 dY=' + '.join(dQ['detay_etiketleri'][:5])if dQ['detay_etiketleri']else'Kurulum Bekleniyor';hN=dQ.get('kutular_4h')or poi_ve_bolge_analizi(bS,aP,HTF_PERIYOT.upper(),iy)[3];o6={'sembol':J,'piyasa':jR,'htf_periyot':HTF_PERIYOT,'mtf_periyot':MTF_PERIYOT,'ltf_periyot':LTF_PERIYOT,'mtf_sablonu':AKTIF_MTF_SABLONU,'yon_4h':aP['yon'],'yon_1h':Q['yon'],'ana_yon':mC,'skor':nO,'bolge_10p_skor':dQ['bolge_10p_skor'],'giris_modeli':dQ['giris_modeli'],'atli_puanlar':dQ['atli_puanlar'],'sinyal':aU,'giris':dQ['giris'],'sl':dQ['sl'],'ozet':dY,'detayli_kurallar':dQ['detayli_kurallar'],'df_4h_full':bS,'df_1h_full':bw,'df_15m_full':aY,'df_4h':bS,'df_1h':bw,'df_5m':aY,'df_15m':aY,'yapi_4h':aP,'yapi_1h':Q,'yapi_5m':aj,'yapi_15m':aj,'kutular_4h':hN,'kutular_1h':dQ.get('kutular_1h',[]),'kutular_5m':dQ['kutular'],'cizim_kutulari_4h':hN,'cizim_kutulari_1h':dQ.get('kutular_1h',[]),'cizim_kutulari_15m':dQ['kutular'],'cizim_kutulari_ltf_saf':dQ.get('kutular_15m',[]),'fibo_oran':Q['fibo_oran'],'fibo_hedefleri':Q['fibo_hedefleri'],'wyckoff_fazi':Q.get('wyckoff_fazi','TREND_IMPULSIVE'),'strong_point':Q.get('strong_point'),'weak_point':Q.get('weak_point'),'uc_istasyon':Q.get('uc_istasyon',{}),'internal_choch':aj.get('internal_choch','YOK'),'fl_dp_meta':Q.get('fl_dp_meta',{}),'qm_meta':aj.get('qm_meta',Q.get('qm_meta',{})),'v6_meta':aj.get('v6_meta',Q.get('v6_meta',{})),'v7_meta':Q.get('v7_meta',aj.get('v7_meta',{})),'v8_meta':Q.get('v8_meta',{}),'v9_meta':aj.get('v9_meta',Q.get('v9_meta',{})),'v10_meta':aj.get('v10_meta',Q.get('v10_meta',{})),'v11_meta':aj.get('v11_meta',Q.get('v11_meta',{})),'v12_meta':aj.get('v12_meta',Q.get('v12_meta',{})),'v13_meta':aj.get('v13_meta',Q.get('v13_meta',{})),'konum_meta':kFlt,'kysy_4h':aP.get('kysy_meta',{}),'kysy_1h':Q.get('kysy_meta',{}),'kysy_ltf':aj.get('kysy_meta',{}),'_ts_mem':time.time()};O=anahtar_yap(J,jR);analiz_hafizasi[O]=o6
 df_tutulan=[k_m for k_m,v_m in analiz_hafizasi.items()if I(v_m,dict)and'df_15m'in v_m and not I(acik_islemler.get(k_m),dict)]
 if L(df_tutulan)>24:
  df_tutulan.sort(key=lambda k_m:F(analiz_hafizasi[k_m].get('_ts_mem',0.0)))
  for eski_k in df_tutulan[:-18]:
   eski_d=analiz_hafizasi.get(eski_k)
   if I(eski_d,dict):
    for df_k_sil in('df_4h_full','df_1h_full','df_15m_full','df_4h','df_1h','df_15m'):eski_d.pop(df_k_sil,None)
 return o6
def tek_tf_canli_pa_analizi(J,bN,D='future',B=None,limit=300):
 lV=veri_cek(J,bN,limit,D);k8=market_yapisi_ve_fibo_analizi(lV,n=SWING_PENCERE);iy=B if B in('BULLISH','BEARISH')else k8['yon']if k8['yon']in('BULLISH','BEARISH')else'BULLISH';dP,ob,K,az,mD=poi_ve_bolge_analizi(lV,k8,bN.upper(),iy);_,_,_,dh=likidite_ve_sfp_analizi(lV,lV,k8,dP,iy);k8['v8_meta']=dh;return{'df_full':lV,'yapi':k8,'kutular':az,'poi_list':dP,'kurallar':K,'bolge_10p_skor':mD,'hedef_yon':iy}
def puana_gore_risk_hesapla(mN=0):
 # Stopta alınan risk her zaman arayüzde yazılan 'İşlem Başı Risk($)' tutarı kadardır
 return R(M(0.1,F(ISLEM_BASI_RISK_USDT)),2)
def dinamik_miktar_hesapla(J,P,al,D=None,mN=0):
 jR=D if D else'spot'if PIYASA_MODU=='spot'else'future';cv=veri_ist(jR);nP=M(A(P-al),P*1e-05)
 o7=KALDIRAC if jR=='future'else 1;aktif_risk=puana_gore_risk_hesapla(mN);lW=aktif_risk/nP;dZ=lW*P;fk=dZ/M(o7,1)
 if dZ<6.0:
  dZ=6.0;fk=dZ/M(o7,1);lW=dZ/M(P,1e-09)
 try:Y=F(cv.amount_to_precision(J,lW))
 except X:Y=R(lW,6)
 if Y<=0 and lW>0:Y=M(R(lW,6),1e-06)
 fk=(Y*P)/M(o7,1)
 do=R(aktif_risk,2);return(Y,fk,do)
def _parite_mtf_periyotlarini_bul(O_key=None,J=None,D='future',H_mevcut=None):
 dR=acik_islemler.get(O_key)if O_key else None
 if not I(dR,dict)and J:
  dR=acik_islemler.get(anahtar_yap(J,D))or acik_islemler.get(f"FUT:{J}")or acik_islemler.get(f"SPOT:{J}")
 if I(dR,dict):
  hp=str(dR.get('htf_periyot')or(H_mevcut.get('htf_periyot')if I(H_mevcut,dict)else None)or HTF_PERIYOT)
  mp=str(dR.get('mtf_periyot')or(H_mevcut.get('mtf_periyot')if I(H_mevcut,dict)else None)or MTF_PERIYOT)
  lp=str(dR.get('ltf_periyot')or(H_mevcut.get('ltf_periyot')if I(H_mevcut,dict)else None)or LTF_PERIYOT)
  sb=str(dR.get('mtf_sablonu')or f"{hp} / {mp} / {lp}")
  return(hp,mp,lp,sb)
 hp=str((H_mevcut.get('htf_periyot')if I(H_mevcut,dict)else None)or HTF_PERIYOT)
 mp=str((H_mevcut.get('mtf_periyot')if I(H_mevcut,dict)else None)or MTF_PERIYOT)
 lp=str((H_mevcut.get('ltf_periyot')if I(H_mevcut,dict)else None)or LTF_PERIYOT)
 sb=str((H_mevcut.get('mtf_sablonu')if I(H_mevcut,dict)else None)or AKTIF_MTF_SABLONU)
 return(hp,mp,lp,sb)
def pine_icin_4h_1h_5m_veri_hazirla(J,D='future',H_mevcut=None,O_key=None):
 htf_p,mtf_p,ltf_p,mtf_sb=_parite_mtf_periyotlarini_bul(O_key,J,D,H_mevcut)
 b4h=H_mevcut.get('df_4h_full')if H_mevcut and H_mevcut.get('htf_periyot')==htf_p and'df_4h_full'in H_mevcut else None
 b1h=H_mevcut.get('df_1h_full')if H_mevcut and H_mevcut.get('mtf_periyot')==mtf_p and'df_1h_full'in H_mevcut else None
 b5m=H_mevcut.get('df_15m_full')if H_mevcut and H_mevcut.get('ltf_periyot')==ltf_p and'df_15m_full'in H_mevcut else None
 try:
  if b4h is None:b4h=veri_cek(J,htf_p,300,D)
 except X:b4h=H_mevcut.get('df_4h_full')if H_mevcut else None
 try:
  if b1h is None:b1h=veri_cek(J,mtf_p,300,D)
 except X:b1h=H_mevcut.get('df_1h_full')if H_mevcut else None
 try:
  if b5m is None:b5m=veri_cek(J,ltf_p,300,D)
 except X:b5m=H_mevcut.get('df_15m_full')if H_mevcut else None
 if b4h is None or b1h is None or b5m is None:return H_mevcut or{}
 y4=market_yapisi_ve_fibo_analizi(b4h);y1=market_yapisi_ve_fibo_analizi(b1h);y5=market_yapisi_ve_fibo_analizi(b5m,n=2)
 rB=tek_yon_4_atli_hesapla(J,b4h,b1h,b5m,y4,y1,y5,'BULLISH')
 if D=='future':
  q1c,q5c=(dict(y1),dict(y5));rS=tek_yon_4_atli_hesapla(J,b4h,b1h,b5m,y4,y1,y5,'BEARISH')
  if rS['skor']>rB['skor']:dQ=rS
  else:dQ=rB;y1.update(q1c);y5.update(q5c)
 else:dQ=rB
 iy=dQ['hedef_yon'];p1,p2,p3,p4=dQ['atli_puanlar'];nO=dQ['skor'];kFlt=dQ.get('konum_meta',{'konum_onay':False,'htf_zorunlu_bolge_onay':False,'saglanan_giris_sart_sayisi':0});kysy_ok=bool(y4.get('kysy_onay',True))
 htf_bolge_kesin_ok=bool(kFlt.get('htf_zorunlu_bolge_onay',False)and kFlt.get('ltf_herhangi_tetik',False)and kFlt.get('saglanan_giris_sart_sayisi',0)>=1)
 aU='LONG'if(htf_bolge_kesin_ok and kysy_ok and nO>=MIN_CONFLUENCE_SKORU and iy=='BULLISH'and y4['yon']=='BULLISH')else'SHORT'if(D=='future'and htf_bolge_kesin_ok and kysy_ok and nO>=MIN_CONFLUENCE_SKORU and iy=='BEARISH'and y4['yon']=='BEARISH')else'BEKLE'
 return{'sembol':J,'piyasa':D,'htf_periyot':htf_p,'mtf_periyot':mtf_p,'ltf_periyot':ltf_p,'mtf_sablonu':mtf_sb,'yon_4h':y4['yon'],'yon_1h':y1['yon'],'yon_5m':y5['yon'],'ana_yon':iy,'skor':nO,'bolge_10p_skor':dQ['bolge_10p_skor'],'giris_modeli':dQ['giris_modeli'],'atli_puanlar':dQ['atli_puanlar'],'sinyal':aU,'giris':dQ['giris']or _f(b5m,'close',-1),'sl':dQ['sl'],'df_4h_full':b4h,'df_1h_full':b1h,'df_15m_full':b5m,'df_4h':b4h,'df_1h':b1h,'df_5m':b5m,'df_15m':b5m,'yapi_4h':y4,'yapi_1h':y1,'yapi_5m':y5,'yapi_15m':y5,'kutular_4h':dQ.get('kutular_4h',[]),'kutular_1h':dQ.get('kutular_1h',[]),'kutular_5m':dQ.get('kutular_15m',[]),'cizim_kutulari_4h':dQ.get('kutular_4h',[]),'cizim_kutulari_1h':dQ.get('kutular_1h',[]),'cizim_kutulari_15m':dQ.get('kutular_15m',[]),'konum_meta':kFlt,'detayli_kurallar':dQ.get('detayli_kurallar',[])}
def pine_script_uret_4h_1h_5m(O,tf_secim='4h',H_ozel=None):
 H=H_ozel or analiz_hafizasi.get(O)or analiz_hafizasi.get(str(O).split(':',1)[-1])or{}
 J=H.get('sembol',str(O).split(':',1)[-1]);D=H.get('piyasa','spot'if str(O).startswith('SPOT:')else'future');tv_sym=J.split(':')[0].replace('/','')+('.P'if D=='future'else'')
 htf_p,mtf_p,ltf_p,_=_parite_mtf_periyotlarini_bul(O,J,D,H)
 if tf_secim in('4h',htf_p):
  tf_secim='4h';gercek_tf=htf_p;df=H.get('df_4h',H.get('df_4h_full'));yp=H.get('yapi_4h',{});kt=H.get('kutular_4h',H.get('cizim_kutulari_4h',[]));tf_lbl=f'{htf_p.upper()} (HTF Ana Yapı & Major Arz/Talep POI)';tv_tf=htf_p
 elif tf_secim in('1h',mtf_p):
  tf_secim='1h';gercek_tf=mtf_p;df=H.get('df_1h',H.get('df_1h_full'));yp=H.get('yapi_1h',{});kt=H.get('kutular_1h',H.get('cizim_kutulari_1h',[]));tf_lbl=f'{mtf_p.upper()} (MTF Konum Filtresi & İstasyonlar)';tv_tf=mtf_p
 else:
  tf_secim='5m';gercek_tf=ltf_p;df=H.get('df_5m',H.get('df_15m_full'));yp=H.get('yapi_5m',H.get('yapi_15m',{}));kt=H.get('kutular_5m',H.get('cizim_kutulari_15m',[]));tf_lbl=f'{ltf_p} (LTF İcra, Reversal Onay & Giriş/SL/TP)';tv_tf=ltf_p
 k4h=H.get('kutular_4h',H.get('cizim_kutulari_4h',[]));k1h=H.get('kutular_1h',H.get('cizim_kutulari_1h',[]))
 sp=F(yp.get('strong_point')or H.get('strong_point')or 0.0);wp=F(yp.get('weak_point')or H.get('weak_point')or 0.0)
 ist=yp.get('uc_istasyon',H.get('uc_istasyon',{}));fl_m=yp.get('fl_dp_meta',H.get('fl_dp_meta',{}));qm_m=yp.get('qm_meta',H.get('qm_meta',{}))
 kFlt=H.get('konum_meta',{'konum_onay':True,'konum_durumu':'ONAY','karar_senaryosu':'STANDART'});kysy=yp.get('kysy_meta',{})
 magic_lvl=F(fl_m.get('magic_line')or ist.get('FL')or 0.0);itz_lvl=F(ist.get('ITZ')or 0.0);fo_lvl=F(ist.get('FO')or 0.0);qml_lvl=F(yp.get('qml_seviyesi')or qm_m.get('qml_seviyesi')or 0.0)
 sMax=F(yp.get('swing_max',0.0)or 0.0);sMin=F(yp.get('swing_min',0.0)or 0.0)
 dR=acik_islemler.get(O);aktif_sinyal_var=bool(I(dR,dict)or H.get('sinyal')in('LONG','SHORT'))
 giris=F(dR['giris']if I(dR,dict)else(H.get('giris')if aktif_sinyal_var else 0.0));sl=F(dR['sl']if I(dR,dict)else(H.get('sl')if aktif_sinyal_var else 0.0))
 yon_islem=dR['yon']if I(dR,dict)else(H.get('sinyal')if H.get('sinyal')in('LONG','SHORT')else'BEKLE');rk=A(giris-sl)if giris>0 and sl>0 else 0.0;mO=-1.0 if yon_islem=='SHORT'else 1.0
 tp1=F(dR['tp']if I(dR,dict)else(giris+mO*rk*RISK_ODUL_ORANI if rk>0 else 0.0));tp2=F(dR.get('tp_nihai',tp1)if I(dR,dict)else(giris+mO*rk*M(NIHAI_TP_RR,RISK_ODUL_ORANI+1.0)if rk>0 else 0.0))
 pnl_u,pnl_y=(0.0,0.0)
 if I(dR,dict):pnl_u,pnl_y,_,_,_,_,_=islem_kar_zarar_hesapla(O,dR)
 pnl_etiket=f"{_fmt_pnl(pnl_u)} (%{pnl_y:+.2f})"if I(dR,dict)else"Açık İşlem Yok"
 p1,p2,p3,p4=H.get('atli_puanlar',(0,0,0,0));skor=H.get('skor',0);sinyal=H.get('sinyal','BEKLE')
 def _kutu_satirlari(k_list,renk_kodu,etiket_on):
  satirlar=[]
  for idx,(ktip,b_idx,lo,hi)in enumerate(k_list[:5],1):
   satirlar.append(f"    box.new(bar_index - 35, {F(hi):.6f}, bar_index + 8, {F(lo):.6f}, border_color={renk_kodu}, bgcolor=color.new({renk_kodu}, 84), text='{etiket_on} {ktip} [{F(lo):.4f}-{F(hi):.4f}]', text_color=color.white, text_size=size.small)")
  return"\n".join(satirlar)if satirlar else"    // Bot tarafinda bu katmanda aktif kutu bulunmuyor"
 bot_kutu_code=_kutu_satirlari(kt,('color.teal'if tf_secim=='4h'else'color.blue'if tf_secim=='1h'else'color.purple'),f'[{tf_secim.upper()} BOT]')
 htf_overlay_code=_kutu_satirlari(k4h[:3],'color.orange','[4H KONUM POI]')if tf_secim in('1h','5m')else"    // 4H Ana Grafik"
 mtf_overlay_code=_kutu_satirlari(k1h[:3],'color.aqua','[1H KONUM POI]')if tf_secim=='5m'else"    // 1H Katmani"
 pine_chk_yorum=_karne_checklist_olustur(H,html_mi=False,yorum_on_eki='// ')
 pine=f"""//@version=6
indicator("Alfa Trade Club [{tf_secim.upper()}] — Kırılım Yoksa Swing Yoktur & Konum Filtresi ({tv_sym})", shorttitle="Alfa_{tf_secim.upper()}_PA", overlay=true, max_boxes_count=500, max_lines_count=500, max_labels_count=500)

// ============================================================================
// PARİTE: {O} ({tv_sym}) | ZAMAN DİLİMİ MODÜLÜ: {tf_lbl}
// ANLIK İŞLEM KÂR/ZARAR: {pnl_etiket}
{pine_chk_yorum.rstrip()}
// KURAL 1: "KIRILIM YOKSA SWING YOKTUR" (No Break No Swing - İç Gürültü Filtresi)
// KURAL 2: "KONUM (ARZ/TALEP BÖLGESİ) FİLTRESİ" (Bağlamsız Kırılım = Tuzak)
// KURAL 3: "2 NUMARALI KARAR BÖLGESİ" (Red/Reversal vs İhlal/Flip Devam)
// ============================================================================

grp1 = "1. Kırılım Yoksa Swing Yoktur & Yapı Ayarları"
swing_len = input.int({SWING_PENCERE}, "Fraktal Aday Swing Penceresi", minval=1, maxval=10, group=grp1)
goster_kysy_zigzag = input.bool({'true' if tf_secim == '4h' else 'false'}, "Onaylı Swing ZigZag & BOS/CHoCH Göster (Sadece HTF)", group=grp1)
goster_elenen_gurultu = input.bool(false, "Elenen İç Yapı (Kırılımsız Gürültü) Noktalarını Göster", group=grp1)

grp2 = "2. Konum (Arz/Talep) Filtresi & İstasyonlar"
goster_dinamik_poi = input.bool({'true' if tf_secim == '4h' else 'false'}, "Dinamik OB / FVG / Konum Kutularını Çiz (Sadece HTF)", group=grp2)
goster_bot_kutulari = input.bool({'true' if tf_secim == '4h' else 'false'}, "Python Botun Tespit Ettiği HTF Kutularını Çiz (Sadece HTF)", group=grp2)
goster_fibo_ote = input.bool({'true' if tf_secim == '4h' else 'false'}, "Sihirli Fibo 0.50 EQ & OTE (0.618-0.786) Göster (Sadece HTF)", group=grp2)
goster_tuzak_etiket = input.bool({'true' if tf_secim == '4h' else 'false'}, "Bağlamsız Tuzak CHoCH & Konum Hatalarını İşaretle (Sadece HTF)", group=grp2)
goster_islem_rr = input.bool(true, "Bot Giriş / Stop-Loss (1R) / TP1 (3R) / TP2 (4R) Çiz", group=grp2)

atr_val = ta.atr(14)
rsi_val = ta.rsi(close, 14)

// --- 4H ve 1H ÜST ZAMAN DİLİMİ KONUM (ARZ/TALEP) BAĞLAMI ---
[htf_high, htf_low, htf_close] = request.security(syminfo.tickerid, "240", [ta.highest(high, 40), ta.lowest(low, 40), close], lookahead=barmerge.lookahead_off)
[mtf_high, mtf_low, mtf_close] = request.security(syminfo.tickerid, "60", [ta.highest(high, 40), ta.lowest(low, 40), close], lookahead=barmerge.lookahead_off)

htf_eq = (htf_high + htf_low) / 2.0
mtf_eq = (mtf_high + mtf_low) / 2.0
htf_fibo_oran = htf_high > htf_low ? (close - htf_low) / (htf_high - htf_low) : 0.5
mtf_fibo_oran = mtf_high > mtf_low ? (close - mtf_low) / (mtf_high - mtf_low) : 0.5

discount_konum = htf_fibo_oran <= 0.52 or mtf_fibo_oran <= 0.50
premium_konum  = htf_fibo_oran >= 0.48 or mtf_fibo_oran >= 0.50
bull_ote_konum = (htf_fibo_oran >= 0.214 and htf_fibo_oran <= 0.40) or (mtf_fibo_oran >= 0.214 and mtf_fibo_oran <= 0.40)
bear_ote_konum = (htf_fibo_oran >= 0.60 and htf_fibo_oran <= 0.786) or (mtf_fibo_oran >= 0.60 and mtf_fibo_oran <= 0.786)

// --- KURAL 1: "KIRILIM YOKSA SWING YOKTUR" DURUM MAKİNESİ ---
ph = ta.pivothigh(high, swing_len, swing_len)
pl = ta.pivotlow(low, swing_len, swing_len)

var float aktif_sh = high
var int   aktif_sh_bar = bar_index
var float aktif_sl = low
var int   aktif_sl_bar = bar_index
var int   yapi_yon = 0
var float onayli_strong_low = low
var float onayli_strong_high = high
var int   son_zz_bar = bar_index
var float son_zz_fiyat = close
var int   elenen_sayac = 0
var bool  pb_olustu = true

if not na(ph)
    p_bar = bar_index - swing_len
    if yapi_yon == -1
        pb_olustu := true
    if yapi_yon == 1 and ph > aktif_sh
        aktif_sh := ph
        aktif_sh_bar := p_bar
    else if ph <= aktif_sh and ph >= aktif_sl
        elenen_sayac += 1
        if goster_elenen_gurultu
            label.new(p_bar, ph, "×", color=color.new(color.gray, 100), textcolor=color.new(color.silver, 35), style=label.style_label_down, size=size.tiny, tooltip="Kırılım Yok -> Swing Yok (İç Yapı Gürültüsü Elendi)")

if not na(pl)
    p_bar = bar_index - swing_len
    if yapi_yon == 1
        pb_olustu := true
    if yapi_yon == -1 and pl < aktif_sl
        aktif_sl := pl
        aktif_sl_bar := p_bar
    else if pl >= aktif_sl and pl <= aktif_sh
        elenen_sayac += 1
        if goster_elenen_gurultu
            label.new(p_bar, pl, "×", color=color.new(color.gray, 100), textcolor=color.new(color.silver, 35), style=label.style_label_up, size=size.tiny, tooltip="Kırılım Yok -> Swing Yok (İç Yapı Gürültüsü Elendi)")

bull_kirilim = pb_olustu and close > aktif_sh and bar_index > aktif_sh_bar + 1
bear_kirilim = pb_olustu and close < aktif_sl and bar_index > aktif_sl_bar + 1

var float son_demand_ust = na
var float son_demand_alt = na
var float son_supply_ust = na
var float son_supply_alt = na

if bull_kirilim
    kirilim_etiket = yapi_yon == 1 ? "BOS (KYSY Onaylı)" : "MSB / Güçlü CHoCH"
    onayli_strong_low := aktif_sl
    son_demand_alt := aktif_sl
    son_demand_ust := aktif_sl + atr_val * 0.65
    orta_bar_b = int(math.round((aktif_sh_bar + bar_index) / 2.0))
    if goster_kysy_zigzag
        line.new(aktif_sh_bar, aktif_sh, bar_index, aktif_sh, color=color.lime, style=line.style_dashed, width=2)
        label.new(orta_bar_b, aktif_sh, "⚡ " + kirilim_etiket, color=color.new(color.black, 20), textcolor=color.lime, style=label.style_label_down, size=size.small)
        line.new(son_zz_bar, son_zz_fiyat, aktif_sl_bar, aktif_sl, color=color.new(color.teal, 15), style=line.style_solid, width=2)
        label.new(aktif_sl_bar, aktif_sl, yapi_yon == 1 ? "HL (Onaylı)" : "LL->Strong Origin", color=color.new(color.teal, 15), textcolor=color.white, style=label.style_label_up, size=size.tiny)
    if goster_dinamik_poi
        box.new(aktif_sl_bar, son_demand_ust, bar_index + 12, son_demand_alt, border_color=color.new(color.blue, 20), bgcolor=color.new(color.blue, 85), text="[{tf_secim.upper()}] Onaylı Demand OB", text_color=color.white, text_size=size.tiny)
    son_zz_bar := aktif_sl_bar
    son_zz_fiyat := aktif_sl
    yapi_yon := 1
    aktif_sh := high
    aktif_sh_bar := bar_index
    pb_olustu := false

if bear_kirilim
    kirilim_etiket = yapi_yon == -1 ? "BOS (KYSY Onaylı)" : "MSB / Güçlü CHoCH"
    onayli_strong_high := aktif_sh
    son_supply_ust := aktif_sh
    son_supply_alt := aktif_sh - atr_val * 0.65
    orta_bar_s = int(math.round((aktif_sl_bar + bar_index) / 2.0))
    if goster_kysy_zigzag
        line.new(aktif_sl_bar, aktif_sl, bar_index, aktif_sl, color=color.red, style=line.style_dashed, width=2)
        label.new(orta_bar_s, aktif_sl, "⚡ " + kirilim_etiket, color=color.new(color.black, 20), textcolor=color.red, style=label.style_label_up, size=size.small)
        line.new(son_zz_bar, son_zz_fiyat, aktif_sh_bar, aktif_sh, color=color.new(color.maroon, 15), style=line.style_solid, width=2)
        label.new(aktif_sh_bar, aktif_sh, yapi_yon == -1 ? "LH (Onaylı)" : "HH->Strong Origin", color=color.new(color.maroon, 15), textcolor=color.white, style=label.style_label_down, size=size.tiny)
    if goster_dinamik_poi
        box.new(aktif_sh_bar, son_supply_ust, bar_index + 12, son_supply_alt, border_color=color.new(color.red, 20), bgcolor=color.new(color.red, 85), text="[{tf_secim.upper()}] Onaylı Supply OB", text_color=color.white, text_size=size.tiny)
    son_zz_bar := aktif_sh_bar
    son_zz_fiyat := aktif_sh
    yapi_yon := -1
    aktif_sl := low
    aktif_sl_bar := bar_index
    pb_olustu := false

if yapi_yon == 1 and high > aktif_sh
    aktif_sh := high
    aktif_sh_bar := bar_index
if yapi_yon == -1 and low < aktif_sl
    aktif_sl := low
    aktif_sl_bar := bar_index

// --- KURAL 2 & 3: KONUM (ARZ/TALEP BÖLGESİ) FİLTRESİ & HATA/TUZAK TESPİTİ ---
demand_temas = (not na(son_demand_ust) and low <= son_demand_ust + atr_val * 0.25 and close >= son_demand_alt) or discount_konum
supply_temas = (not na(son_supply_alt) and high >= son_supply_alt - atr_val * 0.25 and close <= son_supply_ust) or premium_konum

tuzak_bull_choch = bull_kirilim and not demand_temas and htf_fibo_oran > 0.72
tuzak_bear_choch = bear_kirilim and not supply_temas and htf_fibo_oran < 0.28

if goster_tuzak_etiket and tuzak_bull_choch
    label.new(bar_index, high + atr_val * 0.3, "❌ TUZAK KIRILIM (Konum Hatası: Premium Tepede/Boşlukta!)", color=color.orange, textcolor=color.black, style=label.style_label_down, size=size.small)

if goster_tuzak_etiket and tuzak_bear_choch
    label.new(bar_index, low - atr_val * 0.3, "❌ TUZAK KIRILIM (Konum Hatası: Discount Dipte/Boşlukta!)", color=color.orange, textcolor=color.black, style=label.style_label_up, size=size.small)

// --- PYTHON BOTUN HESAPLADIĞI GERÇEK {tf_secim.upper()} SEVİYELERİ VE KUTULARI ---
var float bot_sp = {sp:.6f}
var float bot_wp = {wp:.6f}
var float bot_magic = {magic_lvl:.6f}
var float bot_itz = {itz_lvl:.6f}
var float bot_qml = {qml_lvl:.6f}
var float bot_smax = {sMax:.6f}
var float bot_smin = {sMin:.6f}
var float bot_giris = {giris:.6f}
var float bot_sl = {sl:.6f}
var float bot_tp1 = {tp1:.6f}
var float bot_tp2 = {tp2:.6f}

if barstate.islast and goster_bot_kutulari
{bot_kutu_code}
{htf_overlay_code}
{mtf_overlay_code}

if barstate.islast and goster_bot_kutulari
    if bot_sp > 0.0
        line.new(bar_index - 40, bot_sp, bar_index + 8, bot_sp, color=color.yellow, style=line.style_dashed, width=2)
        label.new(bar_index + 8, bot_sp, "🛡️ Strong Origin ({sp:.4f})", color=color.new(color.yellow, 80), textcolor=color.yellow, style=label.style_label_left, size=size.small)
    if bot_wp > 0.0
        line.new(bar_index - 40, bot_wp, bar_index + 8, bot_wp, color=color.silver, style=line.style_dotted, width=2)
        label.new(bar_index + 8, bot_wp, "🎯 Weak Target ({wp:.4f})", color=color.new(color.silver, 80), textcolor=color.white, style=label.style_label_left, size=size.small)
    if bot_magic > 0.0
        line.new(bar_index - 30, bot_magic, bar_index + 8, bot_magic, color=color.fuchsia, style=line.style_dashed, width=1)
        label.new(bar_index + 8, bot_magic, "✨ Magic Line / FL ({magic_lvl:.4f})", color=color.new(color.fuchsia, 80), textcolor=color.fuchsia, style=label.style_label_left, size=size.tiny)
    if bot_itz > 0.0
        line.new(bar_index - 30, bot_itz, bar_index + 8, bot_itz, color=color.aqua, style=line.style_dotted, width=1)
        label.new(bar_index + 8, bot_itz, "🏛️ ITZ ({itz_lvl:.4f})", color=color.new(color.aqua, 80), textcolor=color.aqua, style=label.style_label_left, size=size.tiny)
    if bot_qml > 0.0
        line.new(bar_index - 30, bot_qml, bar_index + 8, bot_qml, color=color.purple, style=line.style_dashed, width=1)
        label.new(bar_index + 8, bot_qml, "👑 QML ({qml_lvl:.4f})", color=color.new(color.purple, 80), textcolor=color.purple, style=label.style_label_left, size=size.tiny)

if barstate.islast and goster_fibo_ote and bot_smax > bot_smin and bot_smin > 0.0
    eq_f = (bot_smax + bot_smin) / 2.0
    rng_f = bot_smax - bot_smin
    ote1 = "{yp.get('yon','BULLISH')}" == "BULLISH" ? bot_smax - rng_f * 0.618 : bot_smin + rng_f * 0.618
    ote2 = "{yp.get('yon','BULLISH')}" == "BULLISH" ? bot_smax - rng_f * 0.786 : bot_smin + rng_f * 0.786
    line.new(bar_index - 45, eq_f, bar_index + 8, eq_f, color=color.gray, style=line.style_dashed, width=1)
    label.new(bar_index + 8, eq_f, "0.50 EQ (" + str.tostring(eq_f, "#.####") + ")", color=color.new(color.gray, 80), textcolor=color.silver, style=label.style_label_left, size=size.tiny)
    box.new(bar_index - 45, math.max(ote1, ote2), bar_index + 8, math.min(ote1, ote2), border_color=color.new(color.teal, 50), bgcolor=color.new(color.teal, 90), text="Sihirli Fibo OTE (0.618-0.786)", text_color=color.teal, text_size=size.tiny)

if barstate.islast and goster_islem_rr and bot_giris > 0.0 and bot_sl > 0.0
    box.new(bar_index - 12, math.max(bot_giris, bot_sl), bar_index + 10, math.min(bot_giris, bot_sl), border_color=color.red, bgcolor=color.new(color.red, 86), text="STOP (1R): {sl:.4f}", text_color=color.white, text_size=size.tiny)
    box.new(bar_index - 12, math.max(bot_giris, bot_tp1), bar_index + 10, math.min(bot_giris, bot_tp1), border_color=color.green, bgcolor=color.new(color.green, 86), text="TP1 (3R %50+BE): {tp1:.4f}", text_color=color.white, text_size=size.tiny)
    line.new(bar_index - 14, bot_giris, bar_index + 12, bot_giris, color=color.aqua, style=line.style_solid, width=2)
    line.new(bar_index - 14, bot_tp2, bar_index + 12, bot_tp2, color=color.lime, style=line.style_dotted, width=2)

// --- SAĞ ÜST ALFA TRADE CLUB HATA DENETİM & STRATEJİ KARNESİ TABLOSU ---
var table panel = table.new(position.top_right, 2, 12, bgcolor=color.rgb(17, 17, 27, 10), border_color=color.rgb(49, 50, 68), border_width=1)
if barstate.islast
    table.cell(panel, 0, 0, "🌲 ALFA PA [{tf_secim.upper()}]", text_color=color.aqua, text_size=size.small, bgcolor=color.rgb(24, 24, 37))
    table.cell(panel, 1, 0, "{O} ({tv_sym})", text_color=color.white, text_size=size.small, bgcolor=color.rgb(24, 24, 37))
    table.cell(panel, 0, 1, "1. Yön & KYSY Onayı", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 1, "{'✅' if kFlt.get('htf_yon_ok', True) else '⬜'} HTF:{H.get('yon_4h','-')} | MTF:{H.get('yon_1h','-')} | LTF:{yp.get('yon','-')}", text_color={'color.lime' if kFlt.get('htf_yon_ok', True) else 'color.orange'}, text_size=size.tiny)
    table.cell(panel, 0, 2, "2. HTF Safe Bölge Puanı", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 2, "{kFlt.get('htf_bolge_sayisi', 0)}/8 Bölge | {kFlt.get('htf_safe_derecesi', 'STANDART')} ({kFlt.get('htf_safe_puan', 0)}p)", text_color={'color.lime' if kFlt.get('konum_onay', True) else 'color.red'}, text_size=size.tiny)
    table.cell(panel, 0, 3, "Check: QML / OTE / OB / Fresh", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 3, "{'✅' if kFlt.get('htf_qml_bolgesinde') else '⬜'}QML {'✅' if kFlt.get('htf_ote_bolgesinde') else '⬜'}OTE {'✅' if kFlt.get('htf_ob_bolgesinde') else '⬜'}OB {'✅' if kFlt.get('htf_arz_talep_bolgesinde') else '⬜'}Fresh", text_color=color.yellow, text_size=size.tiny)
    table.cell(panel, 0, 4, "Check: CHoCH / BOS / ITZ / Magic", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 4, "{'✅' if kFlt.get('htf_choch_noktasinda') else '⬜'}CHoCH {'✅' if kFlt.get('htf_bos_noktasinda') else '⬜'}BOS {'✅' if kFlt.get('htf_itz_bolgesinde') else '⬜'}ITZ {'✅' if kFlt.get('htf_magic_line_bolgesinde') else '⬜'}Magic", text_color=color.yellow, text_size=size.tiny)
    table.cell(panel, 0, 5, "3. LTF Reversal Kırılım & Mum", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 5, "{'✅' if kFlt.get('ltf_reversal_kirilim_onay') else '⬜'}Reversal Kırılım | {'✅' if kFlt.get('ltf_reversal_mum_onay') else '⬜'}Reversal Mum", text_color={'color.lime' if kFlt.get('ltf_herhangi_tetik') else 'color.orange'}, text_size=size.tiny)
    table.cell(panel, 0, 6, "Mahşerin 4 Atlısı Skoru", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 6, "{skor}/100 ({p1}/{p2}/{p3}/{p4}) -> {sinyal}", text_color={'color.lime' if sinyal=='LONG' else 'color.red' if sinyal=='SHORT' else 'color.orange'}, text_size=size.tiny)
    table.cell(panel, 0, 7, "Bölge Gücü & Wyckoff", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 7, "{H.get('bolge_10p_skor',0)}/10 | {yp.get('wyckoff_fazi','TREND')}", text_color=color.white, text_size=size.tiny)
    table.cell(panel, 0, 8, "Strong Origin / Weak Target", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 8, "{sp:.4f} / {wp:.4f}", text_color=color.yellow, text_size=size.tiny)
    table.cell(panel, 0, 9, "Giriş / Stop-Loss (1R)", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 9, "{giris:.4f} / {sl:.4f} ({yon_islem})", text_color=color.aqua, text_size=size.tiny)
    table.cell(panel, 0, 10, "TP1 (3R %50+BE) / TP2 (4R)", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 10, "{tp1:.4f} / {tp2:.4f}", text_color=color.lime, text_size=size.tiny)
    table.cell(panel, 0, 11, "Anlık Kâr / Zarar Tutarı", text_color=color.silver, text_size=size.tiny)
    table.cell(panel, 1, 11, "{pnl_etiket}", text_color={'color.lime' if pnl_u >= 0 else 'color.red'}, text_size=size.tiny)
"""
 return pine
def _arz_talep_ve_imbalance_sablon_hesapla(df_c,ts_arr,bos_list,E,qml_seviye=None):
 arz_talep_list=[];imbalance_list=[]
 ct=L(df_c)
 if ct<6:return(arz_talep_list,imbalance_list)
 son_kapanis=_f(df_c,'close',-1)
 eklenen_at=set()
 # Hem ana HTF kırılımını hem de lokal impulsif kırılımları birleştir (Arz/Talep bölgelerinin eksiksiz görünmesi için)
 tum_bos=list(bos_list or[])
 try:
  _,_,ltf_m=_kysy_ltf_swing_analizi(df_c,3,False)
  for b_i,lvl,o_i,o_v,yon_b,ktip in ltf_m.get('bos_list',[])[-10:]:
   if 0<=o_i<ct and 0<=b_i<ct:
    tum_bos.append({'orig_idx':int(o_i),'idx2':int(b_i),'yon':yon_b,'tip':ktip})
 except X:pass
 for idx_b,b in enumerate(tum_bos):
  oi=M(0,N(ct-3,int(b.get('orig_idx',b.get('idx1',0)))))
  bi=M(oi+1,N(ct-1,int(b.get('idx2',ct-1))))
  yon_b=b.get('yon','BULLISH')
  ktip=str(b.get('tip','BOS'))
  rev_mi='MSB'in ktip or'CHOCH'in ktip or idx_b==0
  if yon_b=='BULLISH':
   lo=N(_f(df_c,'low',oi),_f(df_c,'low',M(0,oi-1)))
   base_ust=_f(df_c,'open',oi)
   for j in G(M(0,oi-1),N(ct-1,oi+3)):
    oj,cj,hj,lj=(_f(df_c,'open',j),_f(df_c,'close',j),_f(df_c,'high',j),_f(df_c,'low',j))
    if cj<oj:base_ust=M(base_ust,oj,hj if(hj-lo)<=E*1.35 else oj)
    elif cj>oj and(cj-oj)>=E*0.45:
     base_ust=M(base_ust,oj);break
   if idx_b==0 and qml_seviye and lo<qml_seviye<=lo+E*2.5:
    hi=F(qml_seviye)
   else:
    hi=M(lo+E*0.25,N(base_ust,lo+E*1.35))
   kirildi=False;test_sayisi=0;kirilma_idx=None
   for m in G(bi+1,ct):
    cm,lm=(_f(df_c,'close',m),_f(df_c,'low',m))
    if cm<lo-E*0.05:kirildi=True;kirilma_idx=m;break
    if lm<=hi and cm>=lo:test_sayisi+=1
   anahtar=('DEMAND',R(lo,2))
   if not kirildi and anahtar not in eklenen_at:
    eklenen_at.add(anahtar)
    durum='Taze'if test_sayisi==0 else f'{test_sayisi}x Test'
    kalip='Fresh Talep Noktası (QML+OB)'if idx_b==0 else('Talep OB (DBR)'if rev_mi else'Valid Talep (RBR)')
    arz_talep_list.append({'tur':'TALEP','alt_tur':'REVERSAL_OB'if rev_mi else'VALID_DEMAND','idx1':int(oi),'t1':ts_arr[oi],'lo':F(lo),'hi':F(hi),'eq':F((lo+hi)/2.0),'taze':test_sayisi==0,'test':test_sayisi,'etiket':f'{kalip} [{durum}]'})
   elif kirildi and kirilma_idx is not None and kirilma_idx<ct-2:
    hala_altinda=all((_f(df_c,'close',m)<=hi+E*0.1 for m in G(kirilma_idx+1,ct)))
    if hala_altinda and A(son_kapanis-hi)<=E*6.0 and anahtar not in eklenen_at:
     eklenen_at.add(anahtar)
     arz_talep_list.append({'tur':'ARZ','alt_tur':'FLIP_ARZ','idx1':int(kirilma_idx),'t1':ts_arr[kirilma_idx],'lo':F(lo),'hi':F(hi),'eq':F((lo+hi)/2.0),'taze':True,'test':0,'etiket':'Flip Arz (Breaker)'})
  else:
   hi=M(_f(df_c,'high',oi),_f(df_c,'high',M(0,oi-1)))
   base_alt=_f(df_c,'open',oi)
   for j in G(M(0,oi-1),N(ct-1,oi+3)):
    oj,cj,hj,lj=(_f(df_c,'open',j),_f(df_c,'close',j),_f(df_c,'high',j),_f(df_c,'low',j))
    if cj>oj:base_alt=N(base_alt,oj,lj if(hi-lj)<=E*1.35 else oj)
    elif cj<oj and(oj-cj)>=E*0.45:
     base_alt=N(base_alt,oj);break
   if idx_b==0 and qml_seviye and hi-E*2.5<=qml_seviye<hi:
    lo=F(qml_seviye)
   else:
    lo=N(hi-E*0.25,M(base_alt,hi-E*1.35))
   kirildi=False;test_sayisi=0;kirilma_idx=None
   for m in G(bi+1,ct):
    cm,hm=(_f(df_c,'close',m),_f(df_c,'high',m))
    if cm>hi+E*0.05:kirildi=True;kirilma_idx=m;break
    if hm>=lo and cm<=hi:test_sayisi+=1
   anahtar=('SUPPLY',R(hi,2))
   if not kirildi and anahtar not in eklenen_at:
    eklenen_at.add(anahtar)
    durum='Taze'if test_sayisi==0 else f'{test_sayisi}x Test'
    kalip='Fresh Arz Noktası (QML+OB)'if idx_b==0 else('Arz OB (RBD)'if rev_mi else'Valid Arz (DBD)')
    arz_talep_list.append({'tur':'ARZ','alt_tur':'REVERSAL_OB'if rev_mi else'VALID_SUPPLY','idx1':int(oi),'t1':ts_arr[oi],'lo':F(lo),'hi':F(hi),'eq':F((lo+hi)/2.0),'taze':test_sayisi==0,'test':test_sayisi,'etiket':f'{kalip} [{durum}]'})
   elif kirildi and kirilma_idx is not None and kirilma_idx<ct-2:
    hala_ustunde=all((_f(df_c,'close',m)>=lo-E*0.1 for m in G(kirilma_idx+1,ct)))
    if hala_ustunde and A(son_kapanis-lo)<=E*6.0 and anahtar not in eklenen_at:
     eklenen_at.add(anahtar)
     arz_talep_list.append({'tur':'TALEP','alt_tur':'FLIP_TALEP','idx1':int(kirilma_idx),'t1':ts_arr[kirilma_idx],'lo':F(lo),'hi':F(hi),'eq':F((lo+hi)/2.0),'taze':True,'test':0,'etiket':'Flip Talep (Breaker)'})
 arz_talep_list=arz_talep_list[:2]+arz_talep_list[-8:]if L(arz_talep_list)>10 else arz_talep_list
 eklenen_imb=set()
 for i in G(1,ct-1):
  h0,l0,o0,c0=(_f(df_c,'high',i-1),_f(df_c,'low',i-1),_f(df_c,'open',i-1),_f(df_c,'close',i-1))
  h1,l1,o1,c1=(_f(df_c,'high',i),_f(df_c,'low',i),_f(df_c,'open',i),_f(df_c,'close',i))
  h2,l2,o2,c2=(_f(df_c,'high',i+1),_f(df_c,'low',i+1),_f(df_c,'open',i+1),_f(df_c,'close',i+1))
  govde1=c1-o1
  if l2>h0 and govde1>=E*0.32 and(l2-h0)>=E*0.08:
   alt_fvg,ust_fvg=(h0,l2);gap_boy=ust_fvg-alt_fvg;kok=N(l0,l1)
   kirildi=False;min_low=ust_fvg;k_idx=None
   for m in G(i+2,ct):
    cm,lm=(_f(df_c,'close',m),_f(df_c,'low',m))
    if cm<alt_fvg:kirildi=True;k_idx=m;break
    if lm<min_low:min_low=lm
   if not kirildi:
    aktif_ust=M(alt_fvg,N(ust_fvg,min_low))
    if(aktif_ust-alt_fvg)>=gap_boy*0.22:
     durum='Taze'if min_low>=ust_fvg else'Kısmi'
     anahtar=('BISI',R(alt_fvg,4),R(aktif_ust,4))
     if anahtar not in eklenen_imb:
      eklenen_imb.add(anahtar)
      imbalance_list.append({'tip':'BISI_FVG','yon':'BULL','idx1':int(i-1),'t1':ts_arr[i-1],'lo':F(alt_fvg),'hi':F(aktif_ust),'ce':F((alt_fvg+aktif_ust)/2.0),'kok':F(kok),'taze':min_low>=ust_fvg,'etiket':f'BISI FVG ({durum})'})
   elif k_idx is not None and k_idx>=ct-45:
    if all((_f(df_c,'close',m)<=ust_fvg+E*0.1 for m in G(k_idx+1,ct)))and A(son_kapanis-ust_fvg)<=E*4.5:
     anahtar=('IFVG_BEAR',R(alt_fvg,4),R(ust_fvg,4))
     if anahtar not in eklenen_imb:
      eklenen_imb.add(anahtar)
      imbalance_list.append({'tip':'IFVG','yon':'BEAR','idx1':int(k_idx),'t1':ts_arr[k_idx],'lo':F(alt_fvg),'hi':F(ust_fvg),'ce':F((alt_fvg+ust_fvg)/2.0),'kok':F(ust_fvg),'taze':True,'etiket':'Bear IFVG (Flip)'})
  elif l0>h2 and(-govde1)>=E*0.32 and(l0-h2)>=E*0.08:
   alt_fvg,ust_fvg=(h2,l0);gap_boy=ust_fvg-alt_fvg;kok=M(h0,h1)
   kirildi=False;max_high=alt_fvg;k_idx=None
   for m in G(i+2,ct):
    cm,hm=(_f(df_c,'close',m),_f(df_c,'high',m))
    if cm>ust_fvg:kirildi=True;k_idx=m;break
    if hm>max_high:max_high=hm
   if not kirildi:
    aktif_alt=N(ust_fvg,M(alt_fvg,max_high))
    if(ust_fvg-aktif_alt)>=gap_boy*0.22:
     durum='Taze'if max_high<=alt_fvg else'Kısmi'
     anahtar=('SIBI',R(aktif_alt,4),R(ust_fvg,4))
     if anahtar not in eklenen_imb:
      eklenen_imb.add(anahtar)
      imbalance_list.append({'tip':'SIBI_FVG','yon':'BEAR','idx1':int(i-1),'t1':ts_arr[i-1],'lo':F(aktif_alt),'hi':F(ust_fvg),'ce':F((aktif_alt+ust_fvg)/2.0),'kok':F(kok),'taze':max_high<=alt_fvg,'etiket':f'SIBI FVG ({durum})'})
   elif k_idx is not None and k_idx>=ct-45:
    if all((_f(df_c,'close',m)>=alt_fvg-E*0.1 for m in G(k_idx+1,ct)))and A(son_kapanis-alt_fvg)<=E*4.5:
     anahtar=('IFVG_BULL',R(alt_fvg,4),R(ust_fvg,4))
     if anahtar not in eklenen_imb:
      eklenen_imb.add(anahtar)
      imbalance_list.append({'tip':'IFVG','yon':'BULL','idx1':int(k_idx),'t1':ts_arr[k_idx],'lo':F(alt_fvg),'hi':F(ust_fvg),'ce':F((alt_fvg+ust_fvg)/2.0),'kok':F(alt_fvg),'taze':True,'etiket':'Bull IFVG (Flip)'})
  if i>=ct-60 and A(o1-c0)>=E*0.12:
   v_lo,v_hi=(N(c0,o1),M(c0,o1))
   if c1>o1 and o1>c0:
    dolduruldu=any((_f(df_c,'low',m)<=v_lo for m in G(i+1,ct)))
    if not dolduruldu:
     imbalance_list.append({'tip':'VIB','yon':'BULL','idx1':int(i-1),'t1':ts_arr[i-1],'lo':F(v_lo),'hi':F(v_hi),'ce':F((v_lo+v_hi)/2.0),'kok':F(v_lo),'taze':True,'etiket':'Bull VIB/Gap'})
   elif c1<o1 and o1<c0:
    dolduruldu=any((_f(df_c,'high',m)>=v_hi for m in G(i+1,ct)))
    if not dolduruldu:
     imbalance_list.append({'tip':'VIB','yon':'BEAR','idx1':int(i-1),'t1':ts_arr[i-1],'lo':F(v_lo),'hi':F(v_hi),'ce':F((v_lo+v_hi)/2.0),'kok':F(v_hi),'taze':True,'etiket':'Bear VIB/Gap'})
 imbalance_list=imbalance_list[-12:]
 return(arz_talep_list,imbalance_list)
def _df_to_tv_json(df,yp,kt):
 mum_list=[];zz_list=[];elenen_list=[];bos_list=[];kutu_list=[];arz_talep_list=[];imbalance_list=[];liq_list=[];sfp_list=[]
 if df is None or L(df)<5:return{'mumlar':mum_list,'zigzag':zz_list,'elenen':elenen_list,'bos':bos_list,'kutular':kutu_list,'arz_talep':arz_talep_list,'imbalance':imbalance_list,'likidite':liq_list,'sfp':sfp_list}
 oc=M(0,L(df)-300)
 df_c=df.iloc[oc:].reset_index(drop=True)
 ct=L(df_c)
 ts_arr=[]
 son_t=0
 for idx,r in df_c.iterrows():
  ts_s=int(F(r['timestamp'])/1000)if'timestamp'in df_c.columns and F(r['timestamp'])>0 else(1700000000+int(idx)*300)
  if ts_s<=son_t:ts_s=son_t+60
  son_t=ts_s;ts_arr.append(ts_s)
  mum_list.append({'time':ts_s,'idx':int(idx),'open':F(r['open']),'high':F(r['high']),'low':F(r['low']),'close':F(r['close'])})
 E=M(_f(df_c,'atr',-2)if'atr'in df_c.columns else _f(df_c,'close',-1)*0.003,_f(df_c,'close',-1)*0.001)
 try:
  n_sw=2 if I(yp,dict)and yp.get('internal_choch')is not None and L(df_c)<=300 and'internal_yon'in yp and L(yp.get('highs',[]))>8 else SWING_PENCERE
  uH,uL,kysy_m=kirilim_yoksa_swing_yoktur_analizi(df_c,n_sw)
  zz_raw=sorted([(i,v,'H')for i,v in uH]+[(i,v,'L')for i,v in uL],key=lambda x:x[0])
  prev_h=None;prev_l=None
  for idx_z,(i,v,tip)in enumerate(zz_raw):
   if 0<=i<L(ts_arr):
    if tip=='H':lbl='HH'if prev_h is None or v>=prev_h else'LH';prev_h=v
    else:
     if prev_l is None:lbl='LL'if(idx_z>0 and zz_raw[idx_z-1][2]=='H')else'HL'
     else:lbl='HL'if v>=prev_l else'LL'
     prev_l=v
    zz_list.append({'time':ts_arr[i],'idx':int(i),'value':F(v),'tip':tip,'lbl':lbl})
  for b_i,lvl,o_i,o_v,yon_b,ktip in kysy_m.get('bos_list',[]):
   if 0<=b_i<L(ts_arr):
    s_i=M(0,N(L(ts_arr)-1,int(o_i)))
    bos_list.append({'t1':ts_arr[s_i],'t2':ts_arr[b_i],'idx1':int(s_i),'idx2':int(b_i),'price':F(lvl),'yon':yon_b,'tip':ktip,'orig_idx':int(s_i),'orig_val':F(o_v)})
 except X:pass
 try:
  arz_talep_list,imbalance_list=_arz_talep_ve_imbalance_sablon_hesapla(df_c,ts_arr,bos_list,E,kysy_m.get('qml_seviyesi'))
 except X:pass
 for ktip,b_idx,lo,hi in(kt or[])[:6]:
  ns=M(0,N(ct-4,int(b_idx)-oc))if I(b_idx,(int,np.integer))else M(0,ct-35)
  kutu_list.append({'tip':str(ktip),'idx1':int(ns),'t1':ts_arr[ns],'lo':F(lo),'hi':F(hi)})
 try:
  liq_list,sfp_list,_=_likidite_ve_sfp_yapilarini_bul(df_c,uH if'uH'in locals()else None,uL if'uL'in locals()else None,ts_arr)
 except X:pass
 q_idx_tv=kysy_m.get('qml_idx')if'kysy_m'in locals()else None
 q_t1_tv=ts_arr[int(q_idx_tv)]if q_idx_tv is not None and 0<=int(q_idx_tv)<L(ts_arr)else None
 q_val_tv=F(kysy_m.get('qml_seviyesi')or 0.0)if'kysy_m'in locals()else 0.0
 return{'mumlar':mum_list,'zigzag':zz_list,'elenen':elenen_list,'bos':bos_list,'kutular':kutu_list,'arz_talep':arz_talep_list,'imbalance':imbalance_list,'likidite':liq_list,'sfp':sfp_list,'qml':q_val_tv,'qml_t1':q_t1_tv,'qml_idx':int(q_idx_tv)if q_idx_tv is not None else None}
def tradingview_kopyala_yapistirsiz_html_ac(O,tf_secim='5m',H_ozel=None):
 from pathlib import Path
 H=H_ozel or analiz_hafizasi.get(O)or analiz_hafizasi.get(str(O).split(':',1)[-1])or{}
 J=H.get('sembol',str(O).split(':',1)[-1]);D=H.get('piyasa','spot'if str(O).startswith('SPOT:')else'future')
 htf_p,mtf_p,ltf_p,mtf_sb=_parite_mtf_periyotlarini_bul(O,J,D,H)
 if not H or H.get('df_4h')is None or(H.get('df_5m')is None and H.get('df_15m')is None)or H.get('htf_periyot')!=htf_p or H.get('mtf_periyot')!=mtf_p or H.get('ltf_periyot')!=ltf_p:
  try:H=pine_icin_4h_1h_5m_veri_hazirla(J,D,H,O)
  except X:pass
 if tf_secim==htf_p:tf_secim='4h'
 elif tf_secim==mtf_p:tf_secim='1h'
 elif tf_secim not in('4h','1h','5m'):tf_secim='5m'
 raw_sym=J.split(':')[0].replace('/','').upper()
 tv_sym=raw_sym+('.P'if D=='future'else'')
 tf_data={}
 for t_k,df_k,yp_k,kt_k in[('4h','df_4h','yapi_4h','kutular_4h'),('1h','df_1h','yapi_1h','kutular_1h'),('5m','df_5m','yapi_5m','kutular_5m')]:
  df_t=H.get(df_k,H.get('df_4h_full'if t_k=='4h'else'df_1h_full'if t_k=='1h'else'df_15m_full'))
  yp_t=H.get(yp_k,H.get('yapi_15m'if t_k=='5m'else yp_k,{}))
  kt_t=H.get(kt_k,H.get('cizim_kutulari_4h'if t_k=='4h'else'cizim_kutulari_1h'if t_k=='1h'else'cizim_kutulari_15m',[]))
  tf_data[t_k]=_df_to_tv_json(df_t,yp_t,kt_t)
  tf_data[t_k]['pine']=pine_script_uret_4h_1h_5m(O,t_k,H)
  tf_data[t_k]['yon']=yp_t.get('yon','-')
  tf_data[t_k]['kirilim_tipi']=yp_t.get('kirilim_tipi','-')
  tf_data[t_k]['fibo_oran']=F(yp_t.get('fibo_oran',0.5)or 0.5)
  tf_data[t_k]['wyckoff']=yp_t.get('wyckoff_fazi','TREND')
  tf_data[t_k]['sp']=F(yp_t.get('strong_point')or H.get('strong_point')or 0.0)
  tf_data[t_k]['wp']=F(yp_t.get('weak_point')or H.get('weak_point')or 0.0)
  ist_t=yp_t.get('uc_istasyon',H.get('uc_istasyon',{}));fl_t=yp_t.get('fl_dp_meta',H.get('fl_dp_meta',{}));qm_t=yp_t.get('qm_meta',H.get('qm_meta',{}))
  tf_data[t_k]['magic']=F(fl_t.get('magic_line')or ist_t.get('FL')or 0.0)
  tf_data[t_k]['fl_turu']=str(fl_t.get('fl_turu','FL'))
  tf_data[t_k]['dp_turu']=str(fl_t.get('dp_turu','DP'))
  tf_data[t_k]['itz']=F(ist_t.get('ITZ')or 0.0)
  tf_data[t_k]['qml']=F(tf_data[t_k].get('qml')or yp_t.get('qml_seviyesi')or qm_t.get('qml_seviyesi')or 0.0)
  tf_data[t_k]['qm_tipi']=str(qm_t.get('qm_tipi','QML'))
  tf_data[t_k]['smax']=F(yp_t.get('swing_max')or 0.0)
  tf_data[t_k]['smin']=F(yp_t.get('swing_min')or 0.0)
  kysy_t=yp_t.get('kysy_meta',{})
  tf_data[t_k]['kysy_onay']=bool(kysy_t.get('kysy_onay',True))
  tf_data[t_k]['elenen_sayi']=int(kysy_t.get('elenen_sayi',0))
 dR=acik_islemler.get(O)
 aktif_sinyal_var=bool(I(dR,dict)or H.get('sinyal')in('LONG','SHORT'))
 giris=F(dR['giris']if I(dR,dict)else(H.get('giris')if aktif_sinyal_var else 0.0))
 sl=F(dR['sl']if I(dR,dict)else(H.get('sl')if aktif_sinyal_var else 0.0))
 yon_islem=dR['yon']if I(dR,dict)else(H.get('sinyal')if H.get('sinyal')in('LONG','SHORT')else'BEKLE (Bölge Dışı)')
 rk=A(giris-sl)if giris>0 and sl>0 else 0.0;mO=-1.0 if yon_islem=='SHORT'else 1.0
 tp1=F(dR['tp']if I(dR,dict)else(giris+mO*rk*RISK_ODUL_ORANI if rk>0 else 0.0))
 tp2=F(dR.get('tp_nihai',tp1)if I(dR,dict)else(giris+mO*rk*M(NIHAI_TP_RR,RISK_ODUL_ORANI+1.0)if rk>0 else 0.0))
 pnl_u,pnl_y=(0.0,0.0)
 if I(dR,dict):pnl_u,pnl_y,_,_,_,_,_=islem_kar_zarar_hesapla(O,dR)
 pnl_html=f"{_fmt_pnl(pnl_u)} (%{pnl_y:+.2f})"if I(dR,dict)else"Açık İşlem Yok (Analiz Modu)"
 pnl_renk="#4ade80"if pnl_u>=0 else"#f87171"
 kFlt=H.get('konum_meta',{'konum_onay':True,'konum_durumu':'ONAY','karar_senaryosu':'STANDART'})
 p1,p2,p3,p4=H.get('atli_puanlar',(0,0,0,0));skor=H.get('skor',0);sinyal=H.get('sinyal','BEKLE')
 bolge_guc=H.get('bolge_10p_skor',0)
 pine_kodu=tf_data.get(tf_secim,tf_data['5m'])['pine']
 checklist_html=_karne_checklist_olustur(H,html_mi=True)
 html_icerik=f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>TradingView Canlı PA & Pine v6 Çizim Şablonları — {O} [{tf_secim.upper()}]</title>
<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js" onerror="var s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js';document.head.appendChild(s);"></script>
<script src="https://s3.tradingview.com/tv.js" async></script>
<style>
body {{ margin:0; padding:0; background:#0f172a; color:#f8fafc; font-family:'Segoe UI',sans-serif; display:flex; flex-direction:column; height:100vh; overflow:hidden; }}
.topbar {{ background:#1e293b; padding:6px 12px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #334155; flex-wrap:wrap; gap:6px; z-index:40; }}
.badge {{ padding:3px 8px; border-radius:6px; font-weight:bold; font-size:11.5px; margin-right:3px; display:inline-block; }}
.btn {{ background:#10b981; color:#fff; border:none; padding:5px 10px; border-radius:6px; font-weight:bold; cursor:pointer; text-decoration:none; font-size:11.5px; margin-left:3px; transition:0.15s; }}
.btn:hover {{ opacity:0.92; }}
.btn.active {{ outline:2px solid #fde047; }}
.layerbar {{ background:#131722; padding:5px 12px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #2a2e39; flex-wrap:wrap; gap:8px; font-size:11.5px; z-index:35; }}
.chk-group {{ display:flex; align-items:center; flex-wrap:wrap; gap:8px; }}
.chk-lbl {{ cursor:pointer; user-select:none; display:inline-flex; align-items:center; gap:4px; background:#1e222d; border:1px solid #334155; padding:3px 8px; border-radius:5px; color:#e2e8f0; font-weight:600; }}
.chk-lbl:hover {{ border-color:#38bdf8; }}
.chk-lbl input {{ accent-color:#10b981; width:14px; height:14px; cursor:pointer; margin:0; }}
.main {{ display:flex; flex:1; overflow:hidden; position:relative; }}
.tv-left-bar {{ width:38px; background:#131722; border-right:1px solid #2a2e39; display:flex; flex-direction:column; align-items:center; padding-top:8px; gap:8px; z-index:30; user-select:none; }}
.tv-tool-icon {{ width:28px; height:28px; border-radius:5px; display:flex; align-items:center; justify-content:center; color:#cbd5e1; font-size:13px; cursor:pointer; background:#1e222d; border:1px solid #2a2e39; }}
.tv-tool-icon:hover, .tv-tool-icon.active {{ color:#38bdf8; border-color:#38bdf8; background:#1e293b; }}
.chart-area {{ flex:7; height:100%; display:flex; flex-direction:column; position:relative; background:#131722; overflow:hidden; }}
.chart-stage {{ flex:1; position:relative; width:100%; overflow:hidden; background:#131722; }}
#tv_chart {{ width:100%; height:100%; position:absolute; top:0; left:0; z-index:2; }}
#pine_canvas {{ width:100%; height:100%; position:absolute; top:0; left:0; z-index:6; pointer-events:none; }}
#rsi_pane {{ height:110px; width:100%; border-top:1px solid #2a2e39; background:#131722; position:relative; display:none; z-index:5; }}
#rsi_pane.show {{ display:block; }}
.side {{ flex:3; min-width:320px; max-width:400px; background:#11111b; border-left:1px solid #334155; padding:9px; display:flex; flex-direction:column; overflow-y:auto; z-index:30; transition:all 0.18s ease; }}
.side.gizli {{ display:none !important; width:0 !important; min-width:0 !important; max-width:0 !important; padding:0 !important; border:none !important; }}
.bilgi-ac-fab {{ position:absolute; top:10px; right:82px; z-index:25; background:#f59e0b; color:#11111b; border:1px solid #fde047; border-radius:6px; padding:5px 10px; font-size:11.5px; font-weight:bold; cursor:pointer; display:none; box-shadow:0 2px 10px rgba(0,0,0,0.45); }}
.bilgi-ac-fab.goster {{ display:inline-flex; align-items:center; gap:4px; }}
.card {{ background:#181825; border:1px solid #313244; border-radius:8px; padding:8px; margin-bottom:7px; font-size:11.5px; line-height:1.48; }}
textarea {{ width:100%; flex:1; min-height:175px; background:#090d16; color:#38bdf8; border:1px solid #334155; border-radius:6px; padding:7px; font-family:Consolas,monospace; font-size:10.5px; resize:none; box-sizing:border-box; }}
</style>
</head>
<body>
<div class="topbar">
  <div>
    <span class="badge" style="background:#2563eb;">🌲 ALFA PA {BOT_VERSIYONU} — CANLI TRADINGVIEW</span>
    <span class="badge" style="background:#0d9488;" id="lbl_parite">{O} ({tv_sym}) | {tf_secim.upper()}</span>
    <span class="badge" style="background:#059669;" id="lbl_anlik_fiyat">⚡ Anlık: Yükleniyor...</span>
    <span class="badge" style="background:{'#10b981' if sinyal=='LONG' else '#ef4444' if sinyal=='SHORT' else '#f59e0b'};">{sinyal} ({skor}/100)</span>
    <span class="badge" style="background:#1e1e2e;border:1px solid {pnl_renk};color:{pnl_renk};">💰 K/Z: {pnl_html}</span>
  </div>
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;">
    <span style="font-size:11.5px;font-weight:bold;color:#a78bfa;">⏱️ MTF Şablon:</span>
    <select id="sel_mtf_sablon" onchange="mtfSablonDegistirJS(this.value)" style="background:#4c1d95;color:#fff;border:1px solid #7c3aed;border-radius:6px;padding:4px 7px;font-size:11.5px;font-weight:bold;cursor:pointer;">
      <option value="4h,1h,15m" {'selected' if (htf_p,mtf_p,ltf_p)==('4h','1h','15m') else ''}>4h / 1h / 15m (Swing)</option>
      <option value="4h,1h,5m" {'selected' if (htf_p,mtf_p,ltf_p)==('4h','1h','5m') else ''}>4h / 1h / 5m (Alfa Pine MTF)</option>
      <option value="4h,30m,3m" {'selected' if (htf_p,mtf_p,ltf_p)==('4h','30m','3m') else ''}>4h / 30m / 3m (Sniper)</option>
      <option value="1d,2h,15m" {'selected' if (htf_p,mtf_p,ltf_p)==('1d','2h','15m') else ''}>1d / 2h / 15m (Pozisyon)</option>
      <option value="1d,1h,5m" {'selected' if (htf_p,mtf_p,ltf_p)==('1d','1h','5m') else ''}>1d / 1h / 5m (Günlük MTF)</option>
      <option value="1M,2h,15m" {'selected' if (htf_p,mtf_p,ltf_p)==('1M','2h','15m') else ''}>1M / 2h / 15m (Aylık Macro)</option>
      <option value="1d,4h,1h" {'selected' if (htf_p,mtf_p,ltf_p)==('1d','4h','1h') else ''}>1d / 4h / 1h (Pozisyon)</option>
      <option value="2h,30m,5m" {'selected' if (htf_p,mtf_p,ltf_p)==('2h','30m','5m') else ''}>2h / 30m / 5m (Gün İçi)</option>
      <option value="1h,15m,5m" {'selected' if (htf_p,mtf_p,ltf_p)==('1h','15m','5m') else ''}>1h / 15m / 5m (Intraday)</option>
      <option value="15m,5m,1m" {'selected' if (htf_p,mtf_p,ltf_p)==('15m','5m','1m') else ''}>15m / 5m / 1m (Scalp)</option>
    </select>
    <button class="btn" id="btn_4h" style="background:#2563eb;" onclick="periyotDegistir('4h')">🏛️ HTF ({htf_p.upper()})</button>
    <button class="btn" id="btn_1h" style="background:#7c3aed;" onclick="periyotDegistir('1h')">🧭 MTF ({mtf_p.upper()})</button>
    <button class="btn" id="btn_5m" style="background:#0d9488;" onclick="periyotDegistir('5m')">🎯 LTF ({ltf_p})</button>
    <button class="btn" id="btn_mod" style="background:#8b5cf6;" onclick="gorunumDegistir()">🌐 Canlı TV Widget Göster</button>
    <button class="btn" style="background:#0284c7;" onclick="anlikGrafigeOdaklan()">🎯 Anlık Muma Git</button>
    <button class="btn" style="background:#eab308;color:#111;" onclick="kopyalaPine()">📋 Kopyala</button>
    <button class="btn" id="btn_bilgi_toggle" style="background:#f59e0b;color:#11111b;" onclick="bilgiPaneliToggle()">📊 Bilgi Ekranı: Açık ◀▶</button>
  </div>
</div>
<div class="layerbar">
  <div class="chk-group">
    <span style="color:#38bdf8;font-weight:bold;">🎨 Çizim Şablonları (İsteğe Göre Ekle):</span>
    <label class="chk-lbl"><input type="checkbox" id="chk_zz" onchange="katmanlariSimdiGuncelle()">Swing / BOS & QML</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_arztalep" onchange="katmanlariSimdiGuncelle()">Arz / Talep Bölgeleri</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_kutu" onchange="katmanlariSimdiGuncelle()">Imbalance & FVG</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_ist" onchange="katmanlariSimdiGuncelle()">İstasyonlar / Magic Line</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_fibo" onchange="katmanlariSimdiGuncelle()">Sihirli Fibo / OTE</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_liq" onchange="katmanlariSimdiGuncelle()">Likidite / SFP</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_rr" onchange="katmanlariSimdiGuncelle()">İşlem & R:R</label>
    <label class="chk-lbl"><input type="checkbox" id="chk_rsi" onchange="rsiPanelToggle()">RSI(14)</label>
  </div>
  <div style="font-size:11px;color:#94a3b8;" id="durum_cubugu">🟢 Canlı Binance Akışı Aktif</div>
</div>
<div class="main">
  <div class="tv-left-bar" id="tv_left_bar">
    <div class="tv-tool-icon active" title="Artı İşareti (Crosshair)">✜</div>
    <div class="tv-tool-icon" id="ico_zz" title="Swing / BOS" onclick="katmanToggle('zz')">📐</div>
    <div class="tv-tool-icon" id="ico_arztalep" title="Arz / Talep Bölgeleri (OB / RBR / DBD / Flip)" onclick="katmanToggle('arztalep')">🧱</div>
    <div class="tv-tool-icon" id="ico_kutu" title="Imbalance & FVG (BISI / SIBI / IFVG / VIB)" onclick="katmanToggle('kutu')">▭</div>
    <div class="tv-tool-icon" id="ico_ist" title="İstasyonlar / Magic Line" onclick="katmanToggle('ist')">🏛</div>
    <div class="tv-tool-icon" id="ico_fibo" title="Sihirli Fibo / OTE" onclick="katmanToggle('fibo')">☰</div>
    <div class="tv-tool-icon" id="ico_liq" title="Likidite / SFP" onclick="katmanToggle('liq')">💧</div>
    <div class="tv-tool-icon" id="ico_rr" title="İşlem & R:R" onclick="katmanToggle('rr')">🎯</div>
  </div>
  <div class="chart-area">
    <button class="bilgi-ac-fab" id="btn_bilgi_fab" onclick="bilgiPaneliToggle()">📊 Bilgilendirme Ekranını Aç ◀</button>
    <div class="chart-stage" id="chart_stage" style="min-height:420px;">
      <div id="tv_chart"></div>
      <canvas id="pine_canvas"></canvas>
      <div id="tv_native_widget" style="width:100%;height:100%;position:absolute;top:0;left:0;z-index:12;display:none;background:#131722;"></div>
    </div>
    <div id="rsi_pane"></div>
  </div>
  <div class="side" id="side_panel">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;gap:6px;">
        <div style="color:#38bdf8;font-weight:bold;font-size:13px;cursor:pointer;" id="karne_baslik" onclick="karneIcerikToggle()" title="Daraltmak/Genişletmek için tıklayın">📊 {O} [{tf_secim.upper()}] — Strateji & Seviye Karnesi ▾</div>
        <button class="btn" style="background:#334155;color:#f8fafc;padding:2px 7px;font-size:10.5px;margin:0;" onclick="bilgiPaneliToggle()" title="Bilgilendirme Ekranını Gizle">✖ Gizle</button>
      </div>
      <div id="karne_icerik_kapsayici">
      <div style="background:#11111b;padding:5px 8px;border-radius:6px;margin-bottom:5px;border-left:3px solid {pnl_renk};">
        <b>💰 Anlık İşlem Kâr/Zarar:</b> <span style="color:{pnl_renk};font-weight:bold;font-size:12.5px;">{pnl_html}</span>
      </div>
      {checklist_html}
      <div id="kysy_satir">• <b>Kırılım Yoksa Swing Yoktur:</b> ONAYLI</div>
      <div>• <b>HTF Safe Bölge Durumu:</b> {kFlt.get('konum_durumu','ONAY')}</div>
      <div>• <b>Safe Derecesi & Senaryo:</b> {kFlt.get('karar_senaryosu','STANDART')}</div>
      <div id="yon_satir">• <b>{htf_p.upper()} / {mtf_p.upper()} / {ltf_p} Yapı Yönü:</b> {H.get('yon_4h','-')} / {H.get('yon_1h','-')} / {H.get('yon_5m',H.get('yapi_15m',{}).get('yon','-'))}</div>
      <div>• <b>4 Atlı Puanları:</b> {p1}/25 | {p2}/25 | {p3}/25 | {p4}/25 (Toplam: {skor}/100)</div>
      <hr style="border-color:#313244;margin:5px 0;">
      <div>• <b style="color:#38bdf8;">Giriş Fiyatı ({yon_islem}):</b> {_fmt_f(giris)}</div>
      <div>• <b style="color:#f87171;">Stop-Loss (1R):</b> {_fmt_f(sl)}</div>
      <div>• <b style="color:#4ade80;">TP1 ({RISK_ODUL_ORANI}R %50+BE):</b> {_fmt_f(tp1)}</div>
      <div>• <b style="color:#a3e635;">Nihai TP ({NIHAI_TP_RR}R):</b> {_fmt_f(tp2)}</div>
      <div id="sp_wp_satir">• <b style="color:#eab308;">Strong Origin / Weak Target:</b> -</div>
      <div id="ist_satir">• <b style="color:#f472b6;">Magic Line (FL) / ITZ / QML:</b> -</div>
      </div>
    </div>
    <div class="card" style="border-color:#8b5cf6;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
        <span style="color:#c084fc;font-weight:bold;font-size:12.5px;">🤖 Gemini AI İşlem Röntgeni & Canlı Soru-Cevap</span>
        <span class="badge" style="background:#4c1d95;color:#e9d5ff;font-size:10px;margin:0;">{BOT_VERSIYONU}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:6px;">
        <button class="btn" style="background:#2563eb;padding:3px 7px;font-size:10.5px;margin:0;" onclick="geminiHizliSor('Bu işlemi neye göre açtın? Giriş yerini nasıl belirledin?')">❓ Neye Göre Açtın?</button>
        <button class="btn" style="background:#0d9488;padding:3px 7px;font-size:10.5px;margin:0;" onclick="geminiHizliSor('Stop-Loss ve TP1/TP2 seviyelerini nasıl hesapladın?')">🛡️ Stop & TP Hesabı</button>
        <button class="btn" style="background:#d97706;padding:3px 7px;font-size:10.5px;margin:0;" onclick="geminiKatmanGoster()">📊 Tüm Giriş & Likiditeyi Çiz</button>
        <button class="btn" style="background:#dc2626;padding:3px 7px;font-size:10.5px;margin:0;" onclick="geminiHizliSor('Bu işlemde veya likidite/stop seçiminde herhangi bir hata veya risk var mı?')">🔍 Hata Denetimi</button>
      </div>
      <div id="gemini_tv_cevap" style="background:#090d16;border:1px solid #334155;border-radius:6px;padding:7px;font-size:11px;color:#e2e8f0;max-height:165px;overflow-y:auto;white-space:pre-wrap;margin-bottom:6px;">💡 Yukarıdaki butonlara tıklayarak veya aşağıya sorunuzu yazarak işlemin tüm röntgenini, giriş/stop hesabını ve hata denetimini anında görebilirsiniz.</div>
      <div style="display:flex;gap:4px;">
        <input id="gemini_tv_soru" type="text" placeholder="İşlemle ilgili her şeyi sorun..." style="flex:1;background:#090d16;color:#fff;border:1px solid #475569;border-radius:5px;padding:5px 7px;font-size:11px;" onkeydown="if(event.key==='Enter')geminiSorJS()">
        <button class="btn" style="background:#8b5cf6;padding:5px 9px;font-size:11px;margin:0;" onclick="geminiSorJS()">Gönder</button>
      </div>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
      <span style="font-weight:bold;color:#fde047;font-size:11.5px;" id="pine_baslik">📜 Aktif Pine Script v6 Kodu ({tf_secim.upper()}):</span>
      <button class="btn" style="background:#0d9488;padding:3px 7px;font-size:10.5px;" onclick="pineKodunuSimdiUygula()">🔄 Kodu Uygula</button>
    </div>
    <textarea id="pine_box" oninput="pineKodunuSimdiUygula()">{pine_kodu}</textarea>
  </div>
</div>
<script>
const TUM_VERI = {json.dumps(tf_data)};
const RAW_SYM = "{raw_sym}";
const IS_FUT = {'true' if D=='future' else 'false'};
const TV_SYM = "{tv_sym}";
const PARITE_ETIKET = "{O}";
let GIRIS = {giris:.8f};
let SL = {sl:.8f};
let TP1 = {tp1:.8f};
let TP2 = {tp2:.8f};
const YON_ISLEM = "{yon_islem}";
let aktifTf = "{tf_secim}";
const TF_GERCEK_HARITA = {{ '4h': "{htf_p}", '1h': "{mtf_p}", '5m': "{ltf_p}" }};
let widgetModu = false;
let aktifMumlar = [];
let parseEdilenPine = {{ kutular: [], sp: 0, wp: 0, magic: 0, itz: 0, qml: 0, smax: 0, smin: 0, giris: GIRIS, sl: SL, tp1: TP1, tp2: TP2 }};
let wsBaglanti = null;
let fiyatTimer = null;

const stageEl = document.getElementById('chart_stage');
const container = document.getElementById('tv_chart');
const pineCanvas = document.getElementById('pine_canvas');
const rsiContainer = document.getElementById('rsi_pane');

const ilkGenislik = Math.max(480, stageEl.clientWidth || (window.innerWidth - 380));
const ilkYukseklik = Math.max(360, stageEl.clientHeight || (window.innerHeight - 95));
const chart = LightweightCharts.createChart(container, {{
  width: ilkGenislik,
  height: ilkYukseklik,
  layout: {{ background: {{ type: 'solid', color: '#131722' }}, textColor: '#d1d4dc' }},
  grid: {{ vertLines: {{ color: 'rgba(30,34,45,0.85)' }}, horzLines: {{ color: 'rgba(30,34,45,0.85)' }} }},
  crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
  rightPriceScale: {{ borderColor: '#2a2e39', autoScale: true, scaleMargins: {{ top: 0.08, bottom: 0.10 }} }},
  timeScale: {{ borderColor: '#2a2e39', timeVisible: true, secondsVisible: false, rightOffset: 10, barSpacing: 5.5 }}
}});

const rsiChart = LightweightCharts.createChart(rsiContainer, {{
  layout: {{ background: {{ type: 'solid', color: '#131722' }}, textColor: '#94a3b8' }},
  grid: {{ vertLines: {{ color: '#1e222d' }}, horzLines: {{ color: '#1e222d' }} }},
  rightPriceScale: {{ borderColor: '#2a2e39' }},
  timeScale: {{ borderColor: '#2a2e39', timeVisible: true, visible: false }}
}});
const rsiSeries = rsiChart.addLineSeries({{ color: '#a78bfa', lineWidth: 2, title: 'RSI(14)' }});
rsiSeries.createPriceLine({{ price: 70, color: '#f87171', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dotted, axisLabelVisible: false, title: '' }});
rsiSeries.createPriceLine({{ price: 50, color: '#64748b', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: false, title: '' }});
rsiSeries.createPriceLine({{ price: 30, color: '#4ade80', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dotted, axisLabelVisible: false, title: '' }});

let candleSeries = null;
let zzSeries = null;
let bosSerileri = [];
let aktifPriceLines = [];

function fiyatFormatla(v) {{
  const n = Number(v || 0);
  const a = Math.abs(n);
  if (a > 0 && a < 1) return n.toFixed(6);
  if (a < 100) return n.toFixed(4);
  return n.toFixed(2);
}}

function pineKodunuParseEt(pineText, fallbackVeri) {{
  const sonuc = {{
    kutular: [],
    sp: fallbackVeri.sp || 0,
    wp: fallbackVeri.wp || 0,
    magic: fallbackVeri.magic || 0,
    itz: fallbackVeri.itz || 0,
    qml: fallbackVeri.qml || 0,
    smax: fallbackVeri.smax || 0,
    smin: fallbackVeri.smin || 0,
    giris: GIRIS,
    sl: SL,
    tp1: TP1,
    tp2: TP2
  }};
  if (fallbackVeri.kutular && fallbackVeri.kutular.length > 0) {{
    fallbackVeri.kutular.forEach(k => {{
      sonuc.kutular.push({{
        tip: k.tip,
        idx1: typeof k.idx1 === 'number' ? k.idx1 : null,
        t1: k.t1 || null,
        solOffset: 32,
        sagOffset: 8,
        hi: k.hi,
        lo: k.lo
      }});
    }});
  }}
  if (!pineText) return sonuc;
  const flt = (rx, defVal) => {{
    const m = pineText.match(rx);
    return m ? parseFloat(m[1]) : defVal;
  }};
  sonuc.sp = flt(/var\s+float\s+bot_sp\s*=\s*([0-9.]+)/, sonuc.sp);
  sonuc.wp = flt(/var\s+float\s+bot_wp\s*=\s*([0-9.]+)/, sonuc.wp);
  sonuc.magic = flt(/var\s+float\s+bot_magic\s*=\s*([0-9.]+)/, sonuc.magic);
  sonuc.itz = flt(/var\s+float\s+bot_itz\s*=\s*([0-9.]+)/, sonuc.itz);
  sonuc.qml = flt(/var\s+float\s+bot_qml\s*=\s*([0-9.]+)/, sonuc.qml);
  sonuc.smax = flt(/var\s+float\s+bot_smax\s*=\s*([0-9.]+)/, sonuc.smax);
  sonuc.smin = flt(/var\s+float\s+bot_smin\s*=\s*([0-9.]+)/, sonuc.smin);
  sonuc.giris = flt(/var\s+float\s+bot_giris\s*=\s*([0-9.]+)/, sonuc.giris);
  sonuc.sl = flt(/var\s+float\s+bot_sl\s*=\s*([0-9.]+)/, sonuc.sl);
  sonuc.tp1 = flt(/var\s+float\s+bot_tp1\s*=\s*([0-9.]+)/, sonuc.tp1);
  sonuc.tp2 = flt(/var\s+float\s+bot_tp2\s*=\s*([0-9.]+)/, sonuc.tp2);
  return sonuc;
}}

function arzTalepStilCoz(z) {{
  const tur = String(z.tur || 'TALEP');
  const alt = String(z.alt_tur || '');
  if (tur === 'TALEP') {{
    if (alt.includes('FLIP')) return ['rgba(20,184,166,0.16)', '#14b8a6', z.etiket || 'Flip Talep'];
    if (z.taze) return ['rgba(16,185,129,0.18)', '#10b981', z.etiket || 'Talep OB (Taze)'];
    return ['rgba(59,130,246,0.15)', '#3b82f6', z.etiket || 'Talep Bölgesi'];
  }} else {{
    if (alt.includes('FLIP')) return ['rgba(244,63,94,0.16)', '#f43f5e', z.etiket || 'Flip Arz'];
    if (z.taze) return ['rgba(239,68,68,0.18)', '#ef4444', z.etiket || 'Arz OB (Taze)'];
    return ['rgba(249,115,22,0.15)', '#f97316', z.etiket || 'Arz Bölgesi'];
  }}
}}

function imbalanceStilCoz(im) {{
  const t = String(im.tip || 'FVG');
  if (t.includes('BISI')) return ['rgba(245,158,11,0.17)', '#f59e0b', im.etiket || 'BISI FVG'];
  if (t.includes('SIBI')) return ['rgba(168,85,247,0.17)', '#a855f7', im.etiket || 'SIBI FVG'];
  if (t.includes('IFVG')) return ['rgba(20,184,166,0.17)', '#14b8a6', im.etiket || 'IFVG Flip'];
  if (t.includes('VIB')) return ['rgba(250,204,21,0.18)', '#eab308', im.etiket || 'VIB/Gap'];
  return ['rgba(6,182,212,0.15)', '#06b6d4', im.etiket || 'Imbalance'];
}}

function fiyatCizgileriniTemizle() {{
  if (!candleSeries) return;
  aktifPriceLines.forEach(pl => {{
    try {{ candleSeries.removePriceLine(pl); }} catch (e) {{}}
  }});
  aktifPriceLines = [];
}}

function seriKatmanlariniGuncelle() {{
  if (!candleSeries) return;
  const veri = TUM_VERI[aktifTf] || TUM_VERI['5m'];
  const isHTF = (aktifTf === '4h');
  const gosterZz  = document.getElementById('chk_zz').checked;
  const gosterIst = document.getElementById('chk_ist').checked;
  const gosterFibo = document.getElementById('chk_fibo').checked;
  const gosterRr  = document.getElementById('chk_rr').checked;
  const gosterLiq = document.getElementById('chk_liq').checked;

  ['zz','arztalep','kutu','ist','fibo','liq','rr'].forEach(k => {{
    const ic = document.getElementById('ico_' + k);
    const ch = document.getElementById('chk_' + k);
    if (ic && ch) ic.classList.toggle('active', ch.checked);
  }});

  if (zzSeries) {{ try {{ chart.removeSeries(zzSeries); }} catch(e){{}} zzSeries = null; }}
  bosSerileri.forEach(s => {{ try {{ chart.removeSeries(s); }} catch(e){{}} }});
  bosSerileri = [];

  const markers = [];
  if (gosterZz && veri.zigzag && veri.zigzag.length > 1) {{
    zzSeries = chart.addLineSeries({{ color: '#cbd5e1', lineWidth: 1.5, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false }});
    zzSeries.setData(veri.zigzag.map(z => ({{ time: z.time, value: z.value }})));
    veri.zigzag.forEach(z => {{
      const renkM = z.lbl === 'HH' ? '#4ade80' : z.lbl === 'LH' ? '#fb7185' : z.lbl === 'HL' ? '#38bdf8' : '#f97316';
      markers.push({{
        time: z.time,
        position: z.tip === 'H' ? 'aboveBar' : 'belowBar',
        color: renkM,
        shape: z.tip === 'H' ? 'arrowDown' : 'arrowUp',
        text: z.lbl
      }});
    }});
  }}
  if (gosterLiq && veri.sfp && veri.sfp.length > 0) {{
    veri.sfp.forEach(sf => {{
      markers.push({{
        time: sf.time,
        position: sf.yon === 'BULL' ? 'belowBar' : 'aboveBar',
        color: sf.yon === 'BULL' ? '#10b981' : '#f43f5e',
        shape: sf.yon === 'BULL' ? 'arrowUp' : 'arrowDown',
        text: sf.yon === 'BULL' ? 'SFP▲' : 'SFP▼'
      }});
    }});
  }}
  markers.sort((a, b) => a.time - b.time);
  candleSeries.setMarkers(markers);

  if (gosterZz && veri.bos && veri.bos.length > 0) {{
    veri.bos.forEach(b => {{
      if (b.t1 < b.t2) {{
        const bs = chart.addLineSeries({{
          color: b.yon === 'BULLISH' ? '#22c55e' : '#f43f5e',
          lineWidth: 1.5,
          lineStyle: LightweightCharts.LineStyle.Dashed,
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: false
        }});
        bs.setData([{{ time: b.t1, value: b.price }}, {{ time: b.t2, value: b.price }}]);
        bosSerileri.push(bs);
      }}
    }});
  }}

  fiyatCizgileriniTemizle();
  function seviyeEkle(fiyat, baslik, renk, stil, kalinlik=1) {{
    if (fiyat && fiyat > 0) {{
      const pl = candleSeries.createPriceLine({{ price: fiyat, color: renk, lineWidth: kalinlik, lineStyle: stil, axisLabelVisible: true, title: baslik }});
      aktifPriceLines.push(pl);
    }}
  }}
  if (gosterRr) {{
    seviyeEkle(parseEdilenPine.giris, 'Giriş', '#38bdf8', LightweightCharts.LineStyle.Dashed, 2);
    seviyeEkle(parseEdilenPine.sl, 'SL(1R)', '#ef4444', LightweightCharts.LineStyle.Solid, 2);
    seviyeEkle(parseEdilenPine.tp1, 'TP1(3R)', '#10b981', LightweightCharts.LineStyle.Solid, 2);
    seviyeEkle(parseEdilenPine.tp2, 'TP2(4R)', '#a3e635', LightweightCharts.LineStyle.Dotted, 1);
  }}
  if (gosterIst) {{
    seviyeEkle(parseEdilenPine.sp, 'Origin', '#eab308', LightweightCharts.LineStyle.Dashed, 1);
    seviyeEkle(parseEdilenPine.wp, 'Weak', '#94a3b8', LightweightCharts.LineStyle.Dotted, 1);
    seviyeEkle(parseEdilenPine.magic, 'Magic/FL', '#ec4899', LightweightCharts.LineStyle.Dashed, 1);
    seviyeEkle(parseEdilenPine.itz, 'ITZ', '#06b6d4', LightweightCharts.LineStyle.Dotted, 1);
  }}
  if (gosterZz || gosterIst) {{
    const qmlPl = (veri.qml && veri.qml > 0) ? veri.qml : (parseEdilenPine.qml || 0);
    seviyeEkle(qmlPl, 'QML', '#c084fc', LightweightCharts.LineStyle.Dashed, 1);
  }}
  if (gosterFibo && parseEdilenPine.smax > parseEdilenPine.smin && parseEdilenPine.smin > 0) {{
    const eq = (parseEdilenPine.smax + parseEdilenPine.smin) / 2.0;
    seviyeEkle(eq, '0.50 EQ', '#64748b', LightweightCharts.LineStyle.Dashed, 1);
  }}
}}

function cizPineGostergeKatmani() {{
  if (!pineCanvas || !candleSeries || aktifMumlar.length < 3) return;
  const rect = stageEl.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  pineCanvas.width = Math.floor(rect.width * dpr);
  pineCanvas.height = Math.floor(rect.height * dpr);
  const ctx = pineCanvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);

  const isHTF = (aktifTf === '4h');
  const gosterArzTalep = document.getElementById('chk_arztalep') ? document.getElementById('chk_arztalep').checked : false;
  const gosterKutu = document.getElementById('chk_kutu').checked;
  const gosterFibo = document.getElementById('chk_fibo').checked;
  const gosterIst  = document.getElementById('chk_ist').checked;
  const gosterRr   = document.getElementById('chk_rr').checked;
  const gosterZz   = document.getElementById('chk_zz').checked;
  const gosterLiq  = document.getElementById('chk_liq').checked;

  const sonIdx = aktifMumlar.length - 1;
  const tSon = chart.timeScale().timeToCoordinate(aktifMumlar[sonIdx].time);
  const tOnceki = chart.timeScale().timeToCoordinate(aktifMumlar[Math.max(0, sonIdx - 10)].time);
  const barGenislik = (tSon !== null && tOnceki !== null && sonIdx >= 10) ? Math.max(3.5, (tSon - tOnceki) / 10.0) : 6.5;

  function timeOrIdxToX(tVal, idxVal) {{
    if (tVal) {{
      const xt = chart.timeScale().timeToCoordinate(tVal);
      if (xt !== null) return xt;
    }}
    if (typeof idxVal === 'number' && idxVal >= 0 && idxVal <= sonIdx) {{
      const xi = chart.timeScale().timeToCoordinate(aktifMumlar[idxVal].time);
      if (xi !== null) return xi;
    }}
    const rel = (typeof idxVal === 'number') ? (idxVal - sonIdx) : -25;
    if (tSon !== null) return tSon + rel * barGenislik;
    return rect.width - 110 + rel * barGenislik;
  }}

  function barIndexToX(relOffset) {{
    return timeOrIdxToX(null, sonIdx + relOffset);
  }}

  function gelismisKutuCiz(x1, x2, fUst, fAlt, bgRenk, kenarRenk, kisaEtiket, metinRenk='#ffffff', solDikCizgi=true, ortaCizgiFiyat=null, kesikliKenar=false) {{
    if (!fUst || !fAlt || fUst <= 0 || fAlt <= 0) return;
    const y1 = candleSeries.priceToCoordinate(Math.max(fUst, fAlt));
    const y2 = candleSeries.priceToCoordinate(Math.min(fUst, fAlt));
    if (y1 === null || y2 === null) return;
    const left = Math.max(4, Math.min(x1, x2));
    const right = Math.min(rect.width - 70, Math.max(x1, x2));
    if (right <= left + 4) return;
    const top = Math.min(y1, y2);
    const h = Math.max(4, Math.abs(y2 - y1));
    ctx.save();
    ctx.fillStyle = bgRenk;
    ctx.fillRect(left, top, right - left, h);
    ctx.strokeStyle = kenarRenk;
    ctx.lineWidth = 1.15;
    if (kesikliKenar) ctx.setLineDash([4, 3]);
    ctx.strokeRect(left, top, right - left, h);
    ctx.setLineDash([]);
    if (solDikCizgi) {{
      ctx.beginPath();
      ctx.moveTo(left, top);
      ctx.lineTo(left, top + h);
      ctx.lineWidth = 3.0;
      ctx.strokeStyle = kenarRenk;
      ctx.stroke();
    }}
    if (ortaCizgiFiyat && ortaCizgiFiyat > 0 && h >= 10) {{
      const yOrta = candleSeries.priceToCoordinate(ortaCizgiFiyat);
      if (yOrta !== null && yOrta > top + 2 && yOrta < top + h - 2) {{
        ctx.beginPath();
        ctx.setLineDash([3, 3]);
        ctx.moveTo(left + 2, yOrta);
        ctx.lineTo(right - 2, yOrta);
        ctx.lineWidth = 0.9;
        ctx.strokeStyle = kenarRenk;
        ctx.stroke();
        ctx.setLineDash([]);
      }}
    }}
    if (kisaEtiket) {{
      ctx.font = 'bold 9.5px Segoe UI, sans-serif';
      ctx.fillStyle = metinRenk;
      ctx.textAlign = 'right';
      ctx.fillText(kisaEtiket, right - 5, top + Math.min(11, h - 2));
    }}
    ctx.restore();
  }}

  const veri = TUM_VERI[aktifTf] || TUM_VERI['5m'];

  // 1. Sihirli Fibo / Ters Yönde OTE Bölgesi (-0.236, 0, 0.236, 0.382, 0.5, 0.618, 0.705, 0.786, 1) & 4H QML Çizgisi
  if (gosterFibo && parseEdilenPine.smax > parseEdilenPine.smin && parseEdilenPine.smin > 0) {{
    const i4 = parseEdilenPine.smax;
    const i5 = parseEdilenPine.smin;
    const dK = i4 - i5;
    const lA = (veri.yon || 'BULLISH') !== 'BEARISH';
    const xFiboBas = veri.fibo_t1 ? timeOrIdxToX(veri.fibo_t1, null) : barIndexToX(-140);
    const xFiboBit = barIndexToX(8);
    const fibSeviyeler = [
      {{ r: -0.236, c: '#cbd5e1', lbl: '-0.236' }},
      {{ r: 0.0,    c: '#22c55e', lbl: '0' }},
      {{ r: 0.236,  c: '#ef4444', lbl: '0.236' }},
      {{ r: 0.382,  c: '#3b82f6', lbl: '0.382' }},
      {{ r: 0.5,    c: '#06b6d4', lbl: '0.5' }},
      {{ r: 0.618,  c: '#10b981', lbl: '0.618' }},
      {{ r: 0.705,  c: '#4ade80', lbl: '0.705' }},
      {{ r: 0.786,  c: '#60a5fa', lbl: '0.786' }},
      {{ r: 1.0,    c: '#f43f5e', lbl: '1' }}
    ];
    fibSeviyeler.forEach(fb => {{
      const fVal = lA ? (i4 - dK * fb.r) : (i5 + dK * fb.r);
      const yF = candleSeries.priceToCoordinate(fVal);
      if (yF !== null && yF > 4 && yF < rect.height - 4) {{
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(Math.max(4, xFiboBas), yF);
        ctx.lineTo(Math.min(rect.width - 72, xFiboBit), yF);
        ctx.strokeStyle = fb.c;
        ctx.lineWidth = (fb.r === 0 || fb.r === 1) ? 1.5 : 1.05;
        ctx.stroke();
        ctx.font = 'bold 9.5px Segoe UI, sans-serif';
        ctx.fillStyle = fb.c;
        ctx.textAlign = 'left';
        ctx.fillText(`${{fb.lbl}} (${{fiyatFormatla(fVal)}})`, Math.min(rect.width - 145, xFiboBit - 65), yF - 3);
        ctx.restore();
      }}
    }});
    const ote1 = lA ? i4 - dK * 0.618 : i5 + dK * 0.618;
    const ote705 = lA ? i4 - dK * 0.705 : i5 + dK * 0.705;
    const ote2 = lA ? i4 - dK * 0.786 : i5 + dK * 0.786;
    const oteBg = lA ? 'rgba(244,63,94,0.16)' : 'rgba(59,130,246,0.16)';
    const oteBrd = lA ? '#fb7185' : '#60a5fa';
    const oteLbl = lA ? 'Bullish OTE (0.618-0.786)' : 'Bearish OTE (0.618-0.786)';
    gelismisKutuCiz(Math.max(xFiboBas + 30, barIndexToX(-95)), xFiboBit, ote1, ote2, oteBg, oteBrd, oteLbl, '#3b82f6', false, ote705, false);
  }}
  const aktifQmlFiyat = (veri.qml && veri.qml > 0) ? veri.qml : (parseEdilenPine.qml || 0);
  if (isHTF && (gosterZz || gosterIst || gosterFibo) && aktifQmlFiyat > 0) {{
    const yQml = candleSeries.priceToCoordinate(aktifQmlFiyat);
    const xQmlBas = (veri.qml_t1 || typeof veri.qml_idx === 'number') ? timeOrIdxToX(veri.qml_t1, veri.qml_idx) : barIndexToX(-160);
    const xQmlBit = barIndexToX(8);
    if (yQml !== null && yQml >= 2 && yQml <= rect.height - 2) {{
      const x1Q = Math.max(6, Math.min(rect.width - 120, xQmlBas));
      const x2Q = Math.min(rect.width - 70, Math.max(x1Q + 30, xQmlBit));
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(x1Q, yQml);
      ctx.lineTo(x2Q, yQml);
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2.2;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x1Q, yQml, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = '#fde047';
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#ef4444';
      ctx.stroke();
      ctx.font = 'bold 11px Segoe UI, sans-serif';
      ctx.fillStyle = '#fde047';
      ctx.textAlign = 'left';
      ctx.fillText('QML', x1Q + 7, Math.max(13, yQml - 6));
      ctx.fillStyle = '#38bdf8';
      ctx.textAlign = 'right';
      ctx.fillText(`QML (${{fiyatFormatla(aktifQmlFiyat)}})`, x2Q - 4, Math.max(13, yQml - 6));
      ctx.restore();
    }}
  }}

  // 2. YENİ ARZ / TALEP BÖLGELERİ ÇİZİM ŞABLONU (Talep OB / Valid RBR-DBR / Arz OB / Valid RBD-DBD / Flip Breaker + %50 EQ)
  if (gosterArzTalep && veri.arz_talep && veri.arz_talep.length > 0) {{
    veri.arz_talep.forEach(z => {{
      const [bg, brd, et] = arzTalepStilCoz(z);
      const xStart = timeOrIdxToX(z.t1, z.idx1);
      const xEnd = barIndexToX(7);
      const eqFiyat = z.eq || ((z.lo + z.hi) / 2.0);
      gelismisKutuCiz(xStart, xEnd, z.hi, z.lo, bg, brd, et, brd, true, eqFiyat, !z.taze);
    }});
  }}

  // 3. GÜNCELLENMİŞ IMBALANCE & FVG ÇİZİM ŞABLONU (BISI FVG, SIBI FVG, Kısmi FVG, IFVG Flip, VIB/Gap + %50 CE)
  if (gosterKutu && veri.imbalance && veri.imbalance.length > 0) {{
    veri.imbalance.forEach(im => {{
      const [bg, brd, et] = imbalanceStilCoz(im);
      const xStart = timeOrIdxToX(im.t1, im.idx1);
      const xEnd = barIndexToX(6);
      const ceFiyat = im.ce || ((im.lo + im.hi) / 2.0);
      gelismisKutuCiz(xStart, xEnd, im.hi, im.lo, bg, brd, et, brd, true, ceFiyat, im.tip === 'IFVG' || !im.taze);
    }});
  }}

  // 4. Likidite & SFP Çizgileri (Doğrulanmış Kırılmamış EQH / EQL / IDM Inducement / Ext BSL-SSL / 3-Temas Trendline Liq & SFP Sweep)
  if (gosterLiq && veri.likidite && veri.likidite.length > 0) {{
    veri.likidite.forEach(lq => {{
      const x1 = timeOrIdxToX(lq.t1, lq.idx1);
      const x2 = lq.aktif ? Math.min(rect.width - 72, Math.max(timeOrIdxToX(lq.t2, lq.idx2), barIndexToX(4))) : timeOrIdxToX(lq.t2, lq.idx2);
      const y1 = candleSeries.priceToCoordinate(lq.p1);
      const y2 = candleSeries.priceToCoordinate(lq.p2);
      if (x1 !== null && x2 !== null && y1 !== null && y2 !== null && Math.abs(x2 - x1) >= 4) {{
        ctx.save();
        ctx.beginPath();
        if (String(lq.tip || '').includes('Sweep')) ctx.setLineDash([2, 3]);
        else if (String(lq.tip || '').includes('Trendline')) ctx.setLineDash([6, 3]);
        else if (String(lq.tip || '').includes('IDM')) ctx.setLineDash([3, 2]);
        else ctx.setLineDash([4, 3]);
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = lq.renk || '#fbbf24';
        ctx.lineWidth = lq.aktif ? 1.55 : 1.25;
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(x1, y1, 3.0, 0, Math.PI * 2);
        ctx.fillStyle = lq.renk || '#fbbf24';
        ctx.fill();
        ctx.font = 'bold 9.5px Segoe UI, sans-serif';
        ctx.fillStyle = lq.renk || '#fbbf24';
        ctx.textAlign = 'right';
        const lblTxt = `${{lq.tip}} (${{fiyatFormatla(lq.p2)}})`;
        ctx.fillText(lblTxt, Math.min(rect.width - 74, Math.max(x1 + 55, x2 - 4)), (y1 + y2) / 2 - 4);
        ctx.restore();
      }}
    }});
  }}

  // 5. İşlem & R:R Kutuları (Giriş - SL - TP1: MTF Geçişlerinde Sabit Fiyat Eksenine Kilitli)
  const rrGiris = GIRIS > 0 ? GIRIS : (parseEdilenPine.giris || 0);
  const rrSl    = SL > 0 ? SL : (parseEdilenPine.sl || 0);
  const rrTp1   = TP1 > 0 ? TP1 : (parseEdilenPine.tp1 || 0);
  if (gosterRr && rrGiris > 0 && rrSl > 0) {{
    const yG = candleSeries.priceToCoordinate(rrGiris);
    const yS = candleSeries.priceToCoordinate(rrSl);
    const yT = rrTp1 > 0 ? candleSeries.priceToCoordinate(rrTp1) : null;
    const xL = Math.max(8, barIndexToX(-10));
    const xR = Math.min(rect.width - 70, Math.max(xL + 36, barIndexToX(6)));
    if (yG !== null && yS !== null && xR > xL + 4) {{
      ctx.save();
      const topR = Math.min(yG, yS), hR = Math.max(2, Math.abs(yS - yG));
      ctx.fillStyle = 'rgba(239,68,68,0.15)';
      ctx.fillRect(xL, topR, xR - xL, hR);
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1.2;
      ctx.strokeRect(xL, topR, xR - xL, hR);
      if (hR >= 10) {{
        ctx.font = 'bold 9.5px Segoe UI, sans-serif';
        ctx.fillStyle = '#fca5a5';
        ctx.textAlign = 'right';
        ctx.fillText('1R Risk', xR - 5, yS > yG ? (yS - 4) : (topR + 11));
      }}
      if (yT !== null) {{
        const topT = Math.min(yG, yT), hT = Math.max(2, Math.abs(yT - yG));
        ctx.fillStyle = 'rgba(16,185,129,0.14)';
        ctx.fillRect(xL, topT, xR - xL, hT);
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 1.2;
        ctx.strokeRect(xL, topT, xR - xL, hT);
        if (hT >= 10) {{
          ctx.font = 'bold 9.5px Segoe UI, sans-serif';
          ctx.fillStyle = '#86efac';
          ctx.textAlign = 'right';
          ctx.fillText('Hedef TP1', xR - 5, yT < yG ? (topT + 11) : (yT - 4));
        }}
      }}
      ctx.beginPath();
      ctx.moveTo(xL, yG);
      ctx.lineTo(xR, yG);
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.0;
      ctx.stroke();
      ctx.restore();
    }}
  }}

  // 6. BOS / CHoCH Kısa Etiketleri
  if (gosterZz && veri.bos && veri.bos.length > 0) {{
    veri.bos.forEach(b => {{
      const x1 = chart.timeScale().timeToCoordinate(b.t1);
      const x2 = chart.timeScale().timeToCoordinate(b.t2);
      const y = candleSeries.priceToCoordinate(b.price);
      if (x1 !== null && x2 !== null && y !== null) {{
        const ortaX = (x1 + x2) / 2.0;
        const renk = b.yon === 'BULLISH' ? '#4ade80' : '#f87171';
        ctx.save();
        ctx.font = 'bold 9.5px Segoe UI, sans-serif';
        const lbl = b.tip && b.tip.includes('CHOCH') ? 'CHoCH' : 'BOS';
        ctx.fillStyle = renk;
        ctx.textAlign = 'center';
        ctx.fillText(lbl, ortaX, y - 4);
        ctx.restore();
      }}
    }});
  }}
}}

function katmanlariSimdiGuncelle() {{
  seriKatmanlariniGuncelle();
  requestAnimationFrame(() => cizPineGostergeKatmani());
}}

function katmanToggle(tip) {{
  const map = {{ arztalep: 'chk_arztalep', kutu: 'chk_kutu', zz: 'chk_zz', ist: 'chk_ist', fibo: 'chk_fibo', liq: 'chk_liq', rr: 'chk_rr' }};
  const el = document.getElementById(map[tip]);
  if (el) {{
    el.checked = !el.checked;
    katmanlariSimdiGuncelle();
  }}
}}

function rsiHesapla(mumlar, periyot=14) {{
  const out = [];
  if (!mumlar || mumlar.length < periyot + 1) return out;
  let kazanc = 0, kayip = 0;
  for (let i = 1; i <= periyot; i++) {{
    const f = mumlar[i].close - mumlar[i - 1].close;
    if (f >= 0) kazanc += f; else kayip -= f;
  }}
  let ortKazanc = kazanc / periyot;
  let ortKayip = kayip / periyot;
  for (let i = periyot; i < mumlar.length; i++) {{
    if (i > periyot) {{
      const f = mumlar[i].close - mumlar[i - 1].close;
      ortKazanc = (ortKazanc * (periyot - 1) + (f > 0 ? f : 0)) / periyot;
      ortKayip = (ortKayip * (periyot - 1) + (f < 0 ? -f : 0)) / periyot;
    }}
    const rs = ortKayip === 0 ? 100 : ortKazanc / ortKayip;
    const rsi = 100 - (100 / (1 + rs));
    out.push({{ time: mumlar[i].time, value: rsi }});
  }}
  return out;
}}

function arzTalepVeImbalanceHesaplaJS(mumlar, bosList, E) {{
  const arzTalep = [], imbalance = [];
  const ct = mumlar ? mumlar.length : 0;
  if (ct < 6) return {{ arz_talep: arzTalep, imbalance: imbalance }};
  const sonKapanis = mumlar[ct - 1].close;
  const eklenenAt = new Set();

  (bosList || []).forEach(b => {{
    const oi = Math.max(0, Math.min(ct - 3, b.orig_idx !== undefined ? b.orig_idx : b.idx1));
    const bi = Math.max(oi + 1, Math.min(ct - 1, b.idx2 !== undefined ? b.idx2 : ct - 1));
    const revMi = String(b.tip || '').includes('MSB') || String(b.tip || '').includes('CHOCH');
    if (b.yon === 'BULLISH') {{
      const lo = Math.min(mumlar[oi].low, mumlar[Math.max(0, oi - 1)].low);
      let baseUst = mumlar[oi].open;
      for (let j = Math.max(0, oi - 1); j <= Math.min(ct - 1, oi + 2); j++) {{
        const mj = mumlar[j];
        if (mj.close < mj.open) baseUst = Math.max(baseUst, mj.open, (mj.high - lo) <= E * 1.35 ? mj.high : mj.open);
        else if (mj.close > mj.open && (mj.close - mj.open) >= E * 0.45) {{ baseUst = Math.max(baseUst, mj.open); break; }}
      }}
      const hi = Math.max(lo + E * 0.25, Math.min(baseUst, lo + E * 1.35));
      let kirildi = false, testSayisi = 0, kIdx = null;
      for (let m = bi + 1; m < ct; m++) {{
        if (mumlar[m].close < lo - E * 0.05) {{ kirildi = true; kIdx = m; break; }}
        if (mumlar[m].low <= hi && mumlar[m].close >= lo) testSayisi++;
      }}
      const key = 'D_' + lo.toFixed(4) + '_' + hi.toFixed(4);
      if (!kirildi && !eklenenAt.has(key)) {{
        eklenenAt.add(key);
        const durum = testSayisi === 0 ? 'Taze' : `${{testSayisi}}x Test`;
        const kalip = revMi ? 'Talep OB (DBR)' : 'Valid Talep (RBR)';
        arzTalep.push({{ tur: 'TALEP', alt_tur: revMi ? 'REVERSAL_OB' : 'VALID_DEMAND', idx1: oi, t1: mumlar[oi].time, lo: lo, hi: hi, eq: (lo + hi) / 2.0, taze: testSayisi === 0, test: testSayisi, etiket: `${{kalip}} [${{durum}}]` }});
      }} else if (kirildi && kIdx !== null && kIdx < ct - 2) {{
        let halaAltinda = true;
        for (let m = kIdx + 1; m < ct; m++) if (mumlar[m].close > hi + E * 0.1) halaAltinda = false;
        if (halaAltinda && Math.abs(sonKapanis - hi) <= E * 6.0 && !eklenenAt.has(key)) {{
          eklenenAt.add(key);
          arzTalep.push({{ tur: 'ARZ', alt_tur: 'FLIP_ARZ', idx1: kIdx, t1: mumlar[kIdx].time, lo: lo, hi: hi, eq: (lo + hi) / 2.0, taze: true, test: 0, etiket: 'Flip Arz (Breaker)' }});
        }}
      }}
    }} else {{
      const hi = Math.max(mumlar[oi].high, mumlar[Math.max(0, oi - 1)].high);
      let baseAlt = mumlar[oi].open;
      for (let j = Math.max(0, oi - 1); j <= Math.min(ct - 1, oi + 2); j++) {{
        const mj = mumlar[j];
        if (mj.close > mj.open) baseAlt = Math.min(baseAlt, mj.open, (hi - mj.low) <= E * 1.35 ? mj.low : mj.open);
        else if (mj.close < mj.open && (mj.open - mj.close) >= E * 0.45) {{ baseAlt = Math.min(baseAlt, mj.open); break; }}
      }}
      const lo = Math.min(hi - E * 0.25, Math.max(baseAlt, hi - E * 1.35));
      let kirildi = false, testSayisi = 0, kIdx = null;
      for (let m = bi + 1; m < ct; m++) {{
        if (mumlar[m].close > hi + E * 0.05) {{ kirildi = true; kIdx = m; break; }}
        if (mumlar[m].high >= lo && mumlar[m].close <= hi) testSayisi++;
      }}
      const key = 'S_' + lo.toFixed(4) + '_' + hi.toFixed(4);
      if (!kirildi && !eklenenAt.has(key)) {{
        eklenenAt.add(key);
        const durum = testSayisi === 0 ? 'Taze' : `${{testSayisi}}x Test`;
        const kalip = revMi ? 'Arz OB (RBD)' : 'Valid Arz (DBD)';
        arzTalep.push({{ tur: 'ARZ', alt_tur: revMi ? 'REVERSAL_OB' : 'VALID_SUPPLY', idx1: oi, t1: mumlar[oi].time, lo: lo, hi: hi, eq: (lo + hi) / 2.0, taze: testSayisi === 0, test: testSayisi, etiket: `${{kalip}} [${{durum}}]` }});
      }} else if (kirildi && kIdx !== null && kIdx < ct - 2) {{
        let halaUstunde = true;
        for (let m = kIdx + 1; m < ct; m++) if (mumlar[m].close < lo - E * 0.1) halaUstunde = false;
        if (halaUstunde && Math.abs(sonKapanis - lo) <= E * 6.0 && !eklenenAt.has(key)) {{
          eklenenAt.add(key);
          arzTalep.push({{ tur: 'TALEP', alt_tur: 'FLIP_TALEP', idx1: kIdx, t1: mumlar[kIdx].time, lo: lo, hi: hi, eq: (lo + hi) / 2.0, taze: true, test: 0, etiket: 'Flip Talep (Breaker)' }});
        }}
      }}
    }}
  }});

  const eklenenImb = new Set();
  for (let i = 1; i < ct - 1; i++) {{
    const m0 = mumlar[i - 1], m1 = mumlar[i], m2 = mumlar[i + 1];
    const govde1 = m1.close - m1.open;
    if (m2.low > m0.high && govde1 >= E * 0.32 && (m2.low - m0.high) >= E * 0.08) {{
      const altFvg = m0.high, ustFvg = m2.low, gapBoy = ustFvg - altFvg;
      let kirildi = false, minLow = ustFvg, kIdx = null;
      for (let m = i + 2; m < ct; m++) {{
        if (mumlar[m].close < altFvg) {{ kirildi = true; kIdx = m; break; }}
        if (mumlar[m].low < minLow) minLow = mumlar[m].low;
      }}
      if (!kirildi) {{
        const aktifUst = Math.max(altFvg, Math.min(ustFvg, minLow));
        if ((aktifUst - altFvg) >= gapBoy * 0.22) {{
          const durum = minLow >= ustFvg ? 'Taze' : 'Kısmi';
          const key = 'BISI_' + altFvg.toFixed(4) + '_' + aktifUst.toFixed(4);
          if (!eklenenImb.has(key)) {{
            eklenenImb.add(key);
            imbalance.push({{ tip: 'BISI_FVG', yon: 'BULL', idx1: i - 1, t1: m0.time, lo: altFvg, hi: aktifUst, ce: (altFvg + aktifUst) / 2.0, taze: minLow >= ustFvg, etiket: `BISI FVG (${{durum}})` }});
          }}
        }}
      }} else if (kIdx !== null && kIdx >= ct - 45) {{
        let altinda = true;
        for (let m = kIdx + 1; m < ct; m++) if (mumlar[m].close > ustFvg + E * 0.1) altinda = false;
        if (altinda && Math.abs(sonKapanis - ustFvg) <= E * 4.5) {{
          imbalance.push({{ tip: 'IFVG', yon: 'BEAR', idx1: kIdx, t1: mumlar[kIdx].time, lo: altFvg, hi: ustFvg, ce: (altFvg + ustFvg) / 2.0, taze: true, etiket: 'Bear IFVG (Flip)' }});
        }}
      }}
    }} else if (m0.low > m2.high && (-govde1) >= E * 0.32 && (m0.low - m2.high) >= E * 0.08) {{
      const altFvg = m2.high, ustFvg = m0.low, gapBoy = ustFvg - altFvg;
      let kirildi = false, maxHigh = altFvg, kIdx = null;
      for (let m = i + 2; m < ct; m++) {{
        if (mumlar[m].close > ustFvg) {{ kirildi = true; kIdx = m; break; }}
        if (mumlar[m].high > maxHigh) maxHigh = mumlar[m].high;
      }}
      if (!kirildi) {{
        const aktifAlt = Math.min(ustFvg, Math.max(altFvg, maxHigh));
        if ((ustFvg - aktifAlt) >= gapBoy * 0.22) {{
          const durum = maxHigh <= altFvg ? 'Taze' : 'Kısmi';
          const key = 'SIBI_' + aktifAlt.toFixed(4) + '_' + ustFvg.toFixed(4);
          if (!eklenenImb.has(key)) {{
            eklenenImb.add(key);
            imbalance.push({{ tip: 'SIBI_FVG', yon: 'BEAR', idx1: i - 1, t1: m0.time, lo: aktifAlt, hi: ustFvg, ce: (aktifAlt + ustFvg) / 2.0, taze: maxHigh <= altFvg, etiket: `SIBI FVG (${{durum}})` }});
          }}
        }}
      }} else if (kIdx !== null && kIdx >= ct - 45) {{
        let ustunde = true;
        for (let m = kIdx + 1; m < ct; m++) if (mumlar[m].close < altFvg - E * 0.1) ustunde = false;
        if (ustunde && Math.abs(sonKapanis - altFvg) <= E * 4.5) {{
          imbalance.push({{ tip: 'IFVG', yon: 'BULL', idx1: kIdx, t1: mumlar[kIdx].time, lo: altFvg, hi: ustFvg, ce: (altFvg + ustFvg) / 2.0, taze: true, etiket: 'Bull IFVG (Flip)' }});
        }}
      }}
    }}
    if (i >= ct - 60 && Math.abs(m1.open - m0.close) >= E * 0.12) {{
      const vLo = Math.min(m0.close, m1.open), vHi = Math.max(m0.close, m1.open);
      if (m1.close > m1.open && m1.open > m0.close) {{
        let doldu = false;
        for (let m = i + 1; m < ct; m++) if (mumlar[m].low <= vLo) doldu = true;
        if (!doldu) imbalance.push({{ tip: 'VIB', yon: 'BULL', idx1: i - 1, t1: m0.time, lo: vLo, hi: vHi, ce: (vLo + vHi) / 2.0, taze: true, etiket: 'Bull VIB/Gap' }});
      }} else if (m1.close < m1.open && m1.open < m0.close) {{
        let doldu = false;
        for (let m = i + 1; m < ct; m++) if (mumlar[m].high >= vHi) doldu = true;
        if (!doldu) imbalance.push({{ tip: 'VIB', yon: 'BEAR', idx1: i - 1, t1: m0.time, lo: vLo, hi: vHi, ce: (vLo + vHi) / 2.0, taze: true, etiket: 'Bear VIB/Gap' }});
      }}
    }}
  }}
  return {{ arz_talep: arzTalep.slice(-10), imbalance: imbalance.slice(-12) }};
}}

function kysySwingHesaplaJS(mumlar, n=2, tf='4h') {{
  const out = {{ zigzag: [], bos: [], arz_talep: [], imbalance: [], yon: 'BULLISH', smax: 0, smin: 0, sp: 0, wp: 0, qml: 0, qml_t1: null, fibo_t1: null, elenen_sayi: 0 }};
  if (!mumlar || mumlar.length < 10) return out;
  let atrSum = 0;
  for (let i = 1; i < mumlar.length; i++) {{
    atrSum += Math.max(mumlar[i].high - mumlar[i].low, Math.abs(mumlar[i].high - mumlar[i-1].close), Math.abs(mumlar[i].low - mumlar[i-1].close));
  }}
  const E = Math.max(atrSum / Math.max(1, mumlar.length - 1), mumlar[mumlar.length - 1].close * 0.001);
  const ct = mumlar.length;
  const dtSn = mumlar.length >= 3 ? Math.abs(mumlar[mumlar.length - 1].time - mumlar[mumlar.length - 2].time) : 3600;
  const hassas1hAlti = (dtSn <= 3660);
  const nPiv = hassas1hAlti ? 2 : (n >= 4 ? 3 : Math.max(1, n));
  function tepeOnayliMi(i) {{
    const m = mumlar[i];
    const gUst = Math.max(m.open, m.close), govde = Math.abs(m.close - m.open), uIgne = m.high - gUst;
    if (uIgne <= Math.max(govde * 1.8, E * 1.1)) return true;
    const esik = gUst + uIgne * 0.45;
    for (let j = Math.max(0, i - 3); j <= Math.min(ct - 1, i + 3); j++) {{
      if (j !== i && mumlar[j].close >= esik) return true;
    }}
    return false;
  }}
  function dipOnayliMi(i) {{
    const m = mumlar[i];
    const gAlt = Math.min(m.open, m.close), govde = Math.abs(m.close - m.open), aIgne = gAlt - m.low;
    if (aIgne <= Math.max(govde * 1.8, E * 1.1)) return true;
    const esik = gAlt - aIgne * 0.45;
    for (let j = Math.max(0, i - 3); j <= Math.min(ct - 1, i + 3); j++) {{
      if (j !== i && mumlar[j].close <= esik) return true;
    }}
    return false;
  }}
  function netSertTepeMi(i) {{
    if (!tepeOnayliMi(i)) return false;
    if (n <= 1) return true;
    const w = hassas1hAlti ? 3 : Math.max(3, nPiv + 1);
    const b1 = Math.max(0, i - w), b2 = Math.min(ct - 1, i + w);
    let minSol = mumlar[i].low, minSag = mumlar[i].low;
    for (let j = b1; j <= i; j++) if (mumlar[j].low < minSol) minSol = mumlar[j].low;
    for (let j = i; j <= b2; j++) if (mumlar[j].low < minSag) minSag = mumlar[j].low;
    const esik = E * (hassas1hAlti ? 0.82 : (n >= 4 ? 1.55 : 1.1));
    const sagEsik = i >= ct - 3 ? esik * 0.5 : esik;
    return (mumlar[i].high - minSol) >= esik && (mumlar[i].high - minSag) >= sagEsik;
  }}
  function netSertDipMi(i) {{
    if (!dipOnayliMi(i)) return false;
    if (n <= 1) return true;
    const w = hassas1hAlti ? 3 : Math.max(3, nPiv + 1);
    const b1 = Math.max(0, i - w), b2 = Math.min(ct - 1, i + w);
    let maxSol = mumlar[i].high, maxSag = mumlar[i].high;
    for (let j = b1; j <= i; j++) if (mumlar[j].high > maxSol) maxSol = mumlar[j].high;
    for (let j = i; j <= b2; j++) if (mumlar[j].high > maxSag) maxSag = mumlar[j].high;
    const esik = E * (hassas1hAlti ? 0.82 : (n >= 4 ? 1.55 : 1.1));
    const sagEsik = i >= ct - 3 ? esik * 0.5 : esik;
    return (maxSol - mumlar[i].low) >= esik && (maxSag - mumlar[i].low) >= sagEsik;
  }}
  function aralikTepeBul(bas, bit) {{
    const b1 = Math.max(0, bas), b2 = Math.min(ct - 1, bit);
    let enI = null, enV = -1e18;
    for (let j = b1; j <= b2; j++) {{
      if (tepeOnayliMi(j) && mumlar[j].high > enV) {{ enI = j; enV = mumlar[j].high; }}
    }}
    if (enI === null) {{
      for (let j = b1; j <= b2; j++) {{
        const bj = Math.max(mumlar[j].open, mumlar[j].close);
        if (bj > enV) {{ enI = j; enV = mumlar[j].high; }}
      }}
    }}
    return [enI !== null ? enI : b1, enI !== null ? enV : mumlar[b1].high];
  }}
  function aralikDipBul(bas, bit) {{
    const b1 = Math.max(0, bas), b2 = Math.min(ct - 1, bit);
    let enI = null, enV = 1e18;
    for (let j = b1; j <= b2; j++) {{
      if (dipOnayliMi(j) && mumlar[j].low < enV) {{ enI = j; enV = mumlar[j].low; }}
    }}
    if (enI === null) {{
      for (let j = b1; j <= b2; j++) {{
        const bj = Math.min(mumlar[j].open, mumlar[j].close);
        if (bj < enV) {{ enI = j; enV = mumlar[j].low; }}
      }}
    }}
    return [enI !== null ? enI : b1, enI !== null ? enV : mumlar[b1].low];
  }}

  const rH = [], rL = [], rHMap = new Set(), rLMap = new Set();
  for (let i = nPiv; i < ct - nPiv; i++) {{
    let isH = true, isL = true;
    for (let j = i - nPiv; j <= i + nPiv; j++) {{
      if (mumlar[j].high > mumlar[i].high) isH = false;
      if (mumlar[j].low < mumlar[i].low) isL = false;
    }}
    if (isH && netSertTepeMi(i)) {{ rH.push([i, mumlar[i].high]); rHMap.add(i); }}
    if (isL && netSertDipMi(i)) {{ rL.push([i, mumlar[i].low]); rLMap.add(i); }}
  }}
  if (rH.length < 2 || rL.length < 2) {{
    rH.length = 0; rL.length = 0; rHMap.clear(); rLMap.clear();
    for (let i = nPiv; i < ct - nPiv; i++) {{
      let isH = true, isL = true;
      for (let j = i - nPiv; j <= i + nPiv; j++) {{
        if (mumlar[j].high > mumlar[i].high) isH = false;
        if (mumlar[j].low < mumlar[i].low) isL = false;
      }}
      if (isH && tepeOnayliMi(i)) {{ rH.push([i, mumlar[i].high]); rHMap.add(i); }}
      if (isL && dipOnayliMi(i)) {{ rL.push([i, mumlar[i].low]); rLMap.add(i); }}
    }}
  }}
  if (rH.length === 0 || rL.length === 0) return out;

  const minPb = E * (hassas1hAlti ? (dtSn >= 1800 ? 1.05 : 0.88) : (n >= 4 ? 1.85 : 1.3));
  const minBar = hassas1hAlti ? 2 : (n >= 4 ? 3 : 2);
  if (rH[0][0] >= minBar) {{
    const [i0L, v0L] = aralikDipBul(0, rH[0][0] - 1);
    if ((rH[0][1] - v0L) >= minPb * 0.85 && (rL.length === 0 || i0L < rL[0][0])) rL.unshift([i0L, v0L]);
  }}
  if (rL[0][0] >= minBar) {{
    const [i0H, v0H] = aralikTepeBul(0, rL[0][0] - 1);
    if ((v0H - rL[0][1]) >= minPb * 0.85 && (rH.length === 0 || i0H < rH[0][0])) rH.unshift([i0H, v0H]);
  }}

  function sertSalinimOnayliMi(basI, basV, bitI, bitV, anaBacak=0) {{
    const genlik = Math.abs(bitV - basV);
    const barFark = Math.max(1, Math.abs(bitI - basI));
    if (genlik < minPb) return false;
    if (anaBacak > E * 3.2 && genlik < Math.min(anaBacak * 0.18, E * 2.6)) return false;
    if (barFark < minBar && genlik < minPb * 1.75) return false;
    const b1 = Math.max(0, Math.min(basI, bitI)), b2 = Math.min(ct - 1, Math.max(basI, bitI));
    const dususMu = bitV < basV;
    let zitSay = 0, maxMum = 0;
    for (let j = b1 + 1; j <= b2; j++) {{
      if (dususMu ? (mumlar[j].close < mumlar[j].open) : (mumlar[j].close > mumlar[j].open)) zitSay++;
      const g = Math.abs(mumlar[j].close - mumlar[j].open);
      if (g > maxMum) maxMum = g;
    }}
    if (!hassas1hAlti && n >= 4 && zitSay < 2 && genlik < minPb * 1.55) return false;
    return maxMum >= E * (hassas1hAlti ? 0.30 : 0.42) || genlik >= minPb * (hassas1hAlti ? 1.12 : 1.3);
  }}

  function qmlYapisiBulJS(uHList, uLList, hedefYon) {{
    const zz = [];
    uHList.forEach(([i, v]) => zz.push([i, v, 'H']));
    uLList.forEach(([i, v]) => zz.push([i, v, 'L']));
    zz.sort((a, b) => a[0] - b[0]);
    const temiz = [];
    zz.forEach(item => {{
      if (temiz.length === 0 || temiz[temiz.length - 1][2] !== item[2]) temiz.push(item);
      else {{
        if (item[2] === 'H' && item[1] >= temiz[temiz.length - 1][1]) temiz[temiz.length - 1] = item;
        else if (item[2] === 'L' && item[1] <= temiz[temiz.length - 1][1]) temiz[temiz.length - 1] = item;
      }}
    }});
    // QML olması için onaylı ZigZag üzerinde en az 3 salınım (4 onaylı nokta: p0 -> p1 -> p2 -> p3 ve p0 gerçek swing) şarttır!
    if (temiz.length < 4) return null;
    let bullQml = null, bearQml = null, bullAny = null, bearAny = null;
    for (let m = temiz.length - 1; m >= 3; m--) {{
      const p0 = temiz[m - 3], p1 = temiz[m - 2], p2 = temiz[m - 1], p3 = temiz[m];
      if (p0[0] <= 0 && m === 3) continue;
      if (p0[2] === 'L' && p1[2] === 'H' && p2[2] === 'L' && p3[2] === 'H') {{
        if (p2[1] < p0[1] && p3[1] > p1[1] && p1[1] > p0[1]) {{
          const cand = {{ qmlIdx: p0[0], qmlVal: p0[1], headIdx: p2[0], headVal: p2[1], bosIdx: p1[0], bosVal: p1[1], hhIdx: p3[0], hhVal: p3[1], yon: 'BULLISH' }};
          if (!bullAny) bullAny = cand;
          let bozuldu = false;
          for (let k = p3[0]; k < ct; k++) if (mumlar[k].low < p2[1]) {{ bozuldu = true; break; }}
          if (!bullQml && !bozuldu) bullQml = cand;
        }}
      }}
      if (p0[2] === 'H' && p1[2] === 'L' && p2[2] === 'H' && p3[2] === 'L') {{
        if (p2[1] > p0[1] && p3[1] < p1[1] && p0[1] > p1[1]) {{
          const cand = {{ qmlIdx: p0[0], qmlVal: p0[1], headIdx: p2[0], headVal: p2[1], bosIdx: p1[0], bosVal: p1[1], hhIdx: p3[0], hhVal: p3[1], yon: 'BEARISH' }};
          if (!bearAny) bearAny = cand;
          let bozuldu = false;
          for (let k = p3[0]; k < ct; k++) if (mumlar[k].high > p2[1]) {{ bozuldu = true; break; }}
          if (!bearQml && !bozuldu) bearQml = cand;
        }}
      }}
    }}
    if (bullQml && bearQml) return bullQml.hhIdx >= bearQml.hhIdx ? bullQml : bearQml;
    if (bullQml || bearQml) return bullQml || bearQml;
    const bSec = bullAny, brSec = bearAny;
    if (hedefYon === 'BULLISH') return bSec || brSec;
    if (hedefYon === 'BEARISH') return brSec || bSec;
    if (bSec && brSec) return bSec.hhIdx >= brSec.hhIdx ? bSec : brSec;
    return bSec || brSec;
  }}

  let hi = rH[0][0], hv = rH[0][1], li = rL[0][0], lv = rL[0][1], tr = 0;
  let oH = [], oL = [], bL = [], kilitH = false, kilitL = false;
  const sI = Math.max(1, Math.min(hi, li) + 1);
  for (let k = sI; k < ct; k++) {{
    const cl = mumlar[k].close, ch = mumlar[k].high, clw = mumlar[k].low;
    const tOk = tepeOnayliMi(k), dOk = dipOnayliMi(k);
    const aktifLeg = Math.abs(hv - lv);
    if (tr === 0) {{
      if (k > hi + minBar && cl > hv + E * 0.12 && tOk) {{
        const [mI, mV] = aralikDipBul(hi + 1, k - 1);
        if ((hv - mV) >= minPb * 0.85 && (mI - hi) >= minBar) {{
          const [bI, bV] = hi >= minBar ? aralikDipBul(0, Math.max(0, hi - 1)) : [mI, mV];
          const yv = tOk ? ch : cl;
          if (hi >= minBar && bI < hi && (hv - bV) >= minPb * 0.85) {{
            if (mV >= bV - E * 0.2) {{
              oL = [[bI, bV], [mI, mV]]; oH = [[hi, hv], [k, yv]];
              bL.push({{ t1: mumlar[hi].time, t2: mumlar[k].time, idx1: hi, idx2: k, orig_idx: mI, orig_val: mV, price: hv, yon: 'BULLISH', tip: 'BULL_BOS' }});
            }} else {{
              const [tI, tV] = bI >= minBar ? aralikTepeBul(0, Math.max(0, bI - 1)) : [hi, hv];
              if (bI >= minBar && tI < bI && (tV - bV) >= minPb * 0.85 && tV > hv) {{
                oH = [[tI, tV], [hi, hv], [k, yv]]; oL = [[bI, bV], [mI, mV]];
                bL.push({{ t1: mumlar[hi].time, t2: mumlar[k].time, idx1: hi, idx2: k, orig_idx: mI, orig_val: mV, price: hv, yon: 'BULLISH', tip: 'BULL_MSB_CHOCH' }});
              }} else {{
                oH = [[hi, hv], [k, yv]]; oL = [[mI, mV]];
              }}
            }}
          }} else {{
            oH = [[hi, hv], [k, yv]]; oL = [[mI, mV]];
          }}
          li = mI; lv = mV; hi = k; hv = yv; tr = 1; kilitH = false;
        }} else if (ch > hv) {{
          hi = k; hv = ch;
        }}
      }} else if (k > li + minBar && cl < lv - E * 0.12 && dOk) {{
        const [xI, xV] = aralikTepeBul(li + 1, k - 1);
        if ((xV - lv) >= minPb * 0.85 && (xI - li) >= minBar) {{
          const [tI, tV] = li >= minBar ? aralikTepeBul(0, Math.max(0, li - 1)) : [xI, xV];
          const yv = dOk ? clw : cl;
          if (li >= minBar && tI < li && (tV - lv) >= minPb * 0.85) {{
            if (xV <= tV + E * 0.2) {{
              oH = [[tI, tV], [xI, xV]]; oL = [[li, lv], [k, yv]];
              bL.push({{ t1: mumlar[li].time, t2: mumlar[k].time, idx1: li, idx2: k, orig_idx: xI, orig_val: xV, price: lv, yon: 'BEARISH', tip: 'BEAR_BOS' }});
            }} else {{
              const [bI, bV] = tI >= minBar ? aralikDipBul(0, Math.max(0, tI - 1)) : [li, lv];
              if (tI >= minBar && bI < tI && (tV - bV) >= minPb * 0.85 && bV < lv) {{
                oL = [[bI, bV], [li, lv], [k, yv]]; oH = [[tI, tV], [xI, xV]];
                bL.push({{ t1: mumlar[li].time, t2: mumlar[k].time, idx1: li, idx2: k, orig_idx: xI, orig_val: xV, price: lv, yon: 'BEARISH', tip: 'BEAR_MSB_CHOCH' }});
              }} else {{
                oL = [[li, lv], [k, yv]]; oH = [[xI, xV]];
              }}
            }}
          }} else {{
            oL = [[li, lv], [k, yv]]; oH = [[xI, xV]];
          }}
          hi = xI; hv = xV; li = k; lv = yv; tr = -1; kilitL = false;
        }} else if (clw < lv) {{
          li = k; lv = clw;
        }}
      }} else {{
        if (rHMap.has(k) && ch > hv && k <= li + nPiv * 4) {{ hi = k; hv = ch; }}
        if (rLMap.has(k) && clw < lv && k <= hi + nPiv * 4) {{ li = k; lv = clw; }}
      }}
    }} else if (tr === 1) {{
      if (!kilitH) {{
        if (ch >= hv) {{
          hi = k; hv = ch;
          if (oH.length > 0) oH[oH.length - 1] = [hi, hv];
        }} else if ((rLMap.has(k - nPiv) && (k - nPiv) >= hi + minBar && sertSalinimOnayliMi(hi, hv, k - nPiv, mumlar[k - nPiv].low, aktifLeg)) || (k >= hi + minBar && sertSalinimOnayliMi(hi, hv, k, clw, aktifLeg))) {{
          kilitH = true;
        }}
      }}
      if (kilitH && k > hi + minBar && cl > hv + E * 0.10 && tOk) {{
        const [mI, mV] = aralikDipBul(hi + 1, k - 1);
        if (sertSalinimOnayliMi(hi, hv, mI, mV, aktifLeg) && (ch - mV) >= minPb && (mI - hi) >= minBar && (k - mI) >= 2) {{
          if (oL.length === 0 || oL[oL.length - 1][0] !== mI) oL.push([mI, mV]);
          li = mI; lv = mV;
          const yv = tOk ? ch : cl;
          bL.push({{ t1: mumlar[hi].time, t2: mumlar[k].time, idx1: hi, idx2: k, orig_idx: mI, orig_val: mV, price: hv, yon: 'BULLISH', tip: 'BULL_BOS' }});
          hi = k; hv = yv; oH.push([hi, hv]); kilitH = false;
        }} else if (ch >= hv) {{
          hi = k; hv = ch;
          if (oH.length > 0) oH[oH.length - 1] = [hi, hv];
          kilitH = false;
        }}
      }} else if (kilitH && ch > hv && !(cl > hv + E * 0.10 && tOk)) {{
        const [mI, mV] = aralikDipBul(hi + 1, k - 1);
        if (!(sertSalinimOnayliMi(hi, hv, mI, mV, aktifLeg) && (mI - hi) >= minBar)) {{
          hi = k; hv = ch;
          if (oH.length > 0) oH[oH.length - 1] = [hi, hv];
          kilitH = false;
        }}
      }} else if (k > li + minBar && cl < lv - E * 0.12 && dOk) {{
        const [xI, xV] = k - 1 >= li + 1 ? aralikTepeBul(li + 1, k - 1) : [hi, hv];
        if (sertSalinimOnayliMi(xI, xV, k, clw)) {{
          if (!kilitH && oH.length > 0) {{
            hi = xI; hv = xV; oH[oH.length - 1] = [hi, hv];
          }}
          const yv = dOk ? clw : cl;
          const chochOk = oH.length >= 2 && oL.length >= 2 && (oH[oH.length - 1][1] > oH[oH.length - 2][1] || oL[oL.length - 1][1] > oL[oL.length - 2][1]);
          bL.push({{ t1: mumlar[li].time, t2: mumlar[k].time, idx1: li, idx2: k, orig_idx: hi, orig_val: hv, price: lv, yon: 'BEARISH', tip: chochOk ? 'BEAR_MSB_CHOCH' : 'BEAR_BOS' }});
          li = k; lv = yv; oL.push([li, lv]); tr = -1; kilitL = false;
        }}
      }}
    }} else if (tr === -1) {{
      if (!kilitL) {{
        if (clw <= lv) {{
          li = k; lv = clw;
          if (oL.length > 0) oL[oL.length - 1] = [li, lv];
        }} else if ((rHMap.has(k - nPiv) && (k - nPiv) >= li + minBar && sertSalinimOnayliMi(li, lv, k - nPiv, mumlar[k - nPiv].high, aktifLeg)) || (k >= li + minBar && sertSalinimOnayliMi(li, lv, k, ch, aktifLeg))) {{
          kilitL = true;
        }}
      }}
      if (kilitL && k > li + minBar && cl < lv - E * 0.10 && dOk) {{
        const [xI, xV] = aralikTepeBul(li + 1, k - 1);
        if (sertSalinimOnayliMi(li, lv, xI, xV, aktifLeg) && (xV - clw) >= minPb && (xI - li) >= minBar && (k - xI) >= 2) {{
          if (oH.length === 0 || oH[oH.length - 1][0] !== xI) oH.push([xI, xV]);
          hi = xI; hv = xV;
          const yv = dOk ? clw : cl;
          bL.push({{ t1: mumlar[li].time, t2: mumlar[k].time, idx1: li, idx2: k, orig_idx: xI, orig_val: xV, price: lv, yon: 'BEARISH', tip: 'BEAR_BOS' }});
          li = k; lv = yv; oL.push([li, lv]); kilitL = false;
        }} else if (clw <= lv) {{
          li = k; lv = clw;
          if (oL.length > 0) oL[oL.length - 1] = [li, lv];
          kilitL = false;
        }}
      }} else if (kilitL && clw < lv && !(cl < lv - E * 0.10 && dOk)) {{
        const [xI, xV] = aralikTepeBul(li + 1, k - 1);
        if (!(sertSalinimOnayliMi(li, lv, xI, xV, aktifLeg) && (xI - li) >= minBar)) {{
          li = k; lv = clw;
          if (oL.length > 0) oL[oL.length - 1] = [li, lv];
          kilitL = false;
        }}
      }} else if (k > hi + minBar && cl > hv + E * 0.12 && tOk) {{
        const [mI, mV] = k - 1 >= hi + 1 ? aralikDipBul(hi + 1, k - 1) : [li, lv];
        if (sertSalinimOnayliMi(mI, mV, k, ch)) {{
          if (!kilitL && oL.length > 0) {{
            li = mI; lv = mV; oL[oL.length - 1] = [li, lv];
          }}
          const yv = dOk ? ch : cl;
          const chochOk = oH.length >= 2 && oL.length >= 2 && (oL[oL.length - 1][1] < oL[oL.length - 2][1] || oH[oH.length - 1][1] < oH[oH.length - 2][1]);
          bL.push({{ t1: mumlar[hi].time, t2: mumlar[k].time, idx1: hi, idx2: k, orig_idx: li, orig_val: lv, price: hv, yon: 'BULLISH', tip: chochOk ? 'BULL_MSB_CHOCH' : 'BULL_BOS' }});
          hi = k; hv = yv; oH.push([hi, hv]); tr = 1; kilitH = false;
        }}
      }}
    }}
  }}

  // Kırılım Yoksa Swing Yoktur: Onaylı swinglerden piyasa yönü ve QML (en az 3 salınım) hesabı
  out.bos = bL;
  out.elenen_sayi = Math.max(0, (rH.length + rL.length) - (oH.length + oL.length));
  if (oH.length > 0 && oL.length > 0) {{
    const [lastHI, lastHV] = oH[oH.length - 1];
    const [prevHI, prevHV] = oH.length >= 2 ? oH[oH.length - 2] : [lastHI, lastHV];
    const [lastLI, lastLV] = oL[oL.length - 1];
    const [prevLI, prevLV] = oL.length >= 2 ? oL[oL.length - 2] : [lastLI, lastLV];
    const sonClose = mumlar[ct - 1].close;
    let yonBelirle = bL.length > 0 ? bL[bL.length - 1].yon : ((lastHI > lastLI && lastHV >= prevHV) ? 'BULLISH' : 'BEARISH');
    if (yonBelirle === 'BULLISH' && sonClose < lastLV && lastHV < prevHV) yonBelirle = 'BEARISH';
    else if (yonBelirle === 'BEARISH' && sonClose > lastHV && lastLV > prevLV) yonBelirle = 'BULLISH';
    out.yon = yonBelirle;
    out.smax = Math.max(lastHV, prevHV);
    out.smin = Math.min(lastLV, prevLV);
    const qmFound = qmlYapisiBulJS(oH, oL, out.yon);
    out.qml = qmFound ? qmFound.qmlVal : 0;
    out.qml_t1 = qmFound ? mumlar[qmFound.qmlIdx].time : null;
    out.qml_idx = qmFound ? qmFound.qmlIdx : null;
    if (out.yon === 'BULLISH') {{
      out.sp = lastLV;
      out.wp = lastHV;
      out.fibo_t1 = mumlar[lastLI].time;
    }} else {{
      out.sp = lastHV;
      out.wp = lastLV;
      out.fibo_t1 = mumlar[lastHI].time;
    }}
  }}

  const rawZz = [];
  oH.forEach(([i, v]) => rawZz.push([i, v, 'H']));
  oL.forEach(([i, v]) => rawZz.push([i, v, 'L']));
  rawZz.sort((a, b) => a[0] - b[0]);
  const darZz = [];
  rawZz.forEach(item => {{
    if (darZz.length === 0 || darZz[darZz.length - 1][2] !== item[2]) darZz.push(item);
    else {{
      if (item[2] === 'H' && item[1] >= darZz[darZz.length - 1][1]) darZz[darZz.length - 1] = item;
      else if (item[2] === 'L' && item[1] <= darZz[darZz.length - 1][1]) darZz[darZz.length - 1] = item;
    }}
  }});
  let prevH = null, prevL = null;
  darZz.forEach(([i, v, tip], idxZ) => {{
    if (i >= 0 && i < mumlar.length) {{
      let lbl = '';
      if (tip === 'H') {{ lbl = (prevH === null || v >= prevH) ? 'HH' : 'LH'; prevH = v; }}
      else {{
        if (prevL === null) lbl = (idxZ > 0 && darZz[idxZ - 1][2] === 'H') ? 'LL' : 'HL';
        else lbl = (v >= prevL) ? 'HL' : 'LL';
        prevL = v;
      }}
      out.zigzag.push({{ time: mumlar[i].time, idx: i, value: v, tip: tip, lbl: lbl }});
    }}
  }});
  const tumBosForAt = (out.bos || []).concat(bL.slice(-10));
  const sablonlar = arzTalepVeImbalanceHesaplaJS(mumlar, tumBosForAt, E);
  if (out.qml > 0 && out.smin > 0 && out.yon === 'BULLISH' && out.qml > out.smin && (out.qml - out.smin) <= E * 3.0) {{
    if (sablonlar.arz_talep.length > 0 && sablonlar.arz_talep[0].tur === 'TALEP') {{
      sablonlar.arz_talep[0].lo = out.smin;
      sablonlar.arz_talep[0].hi = out.qml;
      sablonlar.arz_talep[0].eq = (out.smin + out.qml) / 2.0;
      sablonlar.arz_talep[0].etiket = 'Fresh Talep Noktası (QML+OB)';
    }}
  }}
  out.arz_talep = sablonlar.arz_talep;
  out.imbalance = sablonlar.imbalance;
  const liqSfp = likiditeVeSfpHesaplaJS(mumlar, oH, oL, E);
  out.likidite = liqSfp.likidite;
  out.sfp = liqSfp.sfp;
  return out;
}}

function likiditeVeSfpHesaplaJS(mumlar, oH, oL, E) {{
  const liqList = [], sfpList = [];
  const ct = mumlar ? mumlar.length : 0;
  if (ct < 10) return {{ likidite: liqList, sfp: sfpList }};
  const sonClose = mumlar[ct - 1].close;
  const tolEq = Math.min(Math.max(E * 0.30, sonClose * 0.0007), sonClose * 0.0035);
  const hMap = new Map(), lMap = new Map();
  for (let i = 2; i < ct - 2; i++) {{
    if (mumlar[i].high >= mumlar[i-1].high && mumlar[i].high >= mumlar[i-2].high && mumlar[i].high >= mumlar[i+1].high && mumlar[i].high >= mumlar[i+2].high) hMap.set(i, mumlar[i].high);
    if (mumlar[i].low <= mumlar[i-1].low && mumlar[i].low <= mumlar[i-2].low && mumlar[i].low <= mumlar[i+1].low && mumlar[i].low <= mumlar[i+2].low) lMap.set(i, mumlar[i].low);
  }}
  (oH || []).forEach(([i, v]) => {{ if (i >= 0 && i < ct) hMap.set(i, Math.max(hMap.get(i) || v, v)); }});
  (oL || []).forEach(([i, v]) => {{ if (i >= 0 && i < ct) lMap.set(i, Math.min(lMap.get(i) || v, v)); }});
  const jn = Array.from(hMap.entries()).sort((a, b) => a[0] - b[0]);
  const jo = Array.from(lMap.entries()).sort((a, b) => a[0] - b[0]);
  const kulH = new Set(), kulL = new Set(), sfpEk = new Set();

  // 1) EQH (BSL) - Kırılmamış (Bedava Yakıt) veya yakın zamanda SFP olmuş eşit tepeler (Ders-02 & 16,22,27.pdf)
  for (let k = 0; k < jn.length; k++) {{
    const [i1, h1] = jn[k];
    if (kulH.has(i1)) continue;
    const grup = [[i1, h1]];
    for (let m = k + 1; m < Math.min(jn.length, k + 5); m++) {{
      const [im, hm] = jn[m];
      if (im - grup[grup.length - 1][0] < 3) continue;
      if (Math.abs(hm - h1) <= tolEq) {{
        const tavanAra = Math.max(h1, hm);
        let araKirildi = false;
        for (let b = grup[grup.length - 1][0] + 1; b < im; b++) {{
          if (mumlar[b].high > tavanAra + E * 0.08) {{ araKirildi = true; break; }}
        }}
        if (!araKirildi) grup.push([im, hm]);
      }}
    }}
    if (grup.length >= 2) {{
      const iSon = grup[grup.length - 1][0];
      const ortH = grup.reduce((s, x) => s + x[1], 0) / grup.length;
      const tavanH = Math.max(...grup.map(x => x[1]));
      let govdeKirildi = false, sweepIdx = null, sweepHi = 0;
      for (let b = iSon + 1; b < ct; b++) {{
        const mb = mumlar[b];
        if (mb.close > tavanH + E * 0.10 || (mb.high > tavanH + E * 0.25 && mb.close > tavanH)) {{ govdeKirildi = true; break; }}
        if (mb.high > tavanH + E * 0.02 && mb.close <= tavanH + E * 0.02 && (mb.high - Math.max(mb.open, mb.close)) >= E * 0.12) {{
          if (sweepIdx === null) {{ sweepIdx = b; sweepHi = mb.high; }}
        }}
      }}
      if (govdeKirildi) continue;
      grup.forEach(([idxE]) => kulH.add(idxE));
      if (sweepIdx !== null) {{
        if (sweepIdx >= ct - 35) {{
          liqList.push({{ tip: '💧 EQH Sweep (SFP)', idx1: i1, idx2: sweepIdx, t1: mumlar[i1].time, t2: mumlar[sweepIdx].time, p1: ortH, p2: ortH, renk: '#f43f5e', aktif: false }});
          const sk = 'BEAR_' + sweepIdx;
          if (!sfpEk.has(sk)) {{ sfpEk.add(sk); sfpList.push({{ tip: '▼ Bear SFP (EQH)', idx: sweepIdx, time: mumlar[sweepIdx].time, price: sweepHi, level: ortH, yon: 'BEAR' }}); }}
        }}
      }} else {{
        const et = grup.length >= 3 ? '$$$ 3x EQH (TT3 BSL)' : '$$$ EQH (BSL)';
        liqList.push({{ tip: et, idx1: i1, idx2: ct - 1, t1: mumlar[i1].time, t2: mumlar[ct - 1].time, p1: ortH, p2: ortH, renk: '#fbbf24', aktif: true }});
      }}
    }}
  }}

  // 2) EQL (SSL) - Kırılmamış (Bedava Yakıt) veya yakın zamanda SFP olmuş eşit dipler (Ders-02 & 16,22,27.pdf)
  for (let k = 0; k < jo.length; k++) {{
    const [i1, l1] = jo[k];
    if (kulL.has(i1)) continue;
    const grup = [[i1, l1]];
    for (let m = k + 1; m < Math.min(jo.length, k + 5); m++) {{
      const [im, lm] = jo[m];
      if (im - grup[grup.length - 1][0] < 3) continue;
      if (Math.abs(lm - l1) <= tolEq) {{
        const tabanAra = Math.min(l1, lm);
        let araKirildi = false;
        for (let b = grup[grup.length - 1][0] + 1; b < im; b++) {{
          if (mumlar[b].low < tabanAra - E * 0.08) {{ araKirildi = true; break; }}
        }}
        if (!araKirildi) grup.push([im, lm]);
      }}
    }}
    if (grup.length >= 2) {{
      const iSon = grup[grup.length - 1][0];
      const ortL = grup.reduce((s, x) => s + x[1], 0) / grup.length;
      const tabanL = Math.min(...grup.map(x => x[1]));
      let govdeKirildi = false, sweepIdx = null, sweepLo = 1e18;
      for (let b = iSon + 1; b < ct; b++) {{
        const mb = mumlar[b];
        if (mb.close < tabanL - E * 0.10 || (mb.low < tabanL - E * 0.25 && mb.close < tabanL)) {{ govdeKirildi = true; break; }}
        if (mb.low < tabanL - E * 0.02 && mb.close >= tabanL - E * 0.02 && (Math.min(mb.open, mb.close) - mb.low) >= E * 0.12) {{
          if (sweepIdx === null) {{ sweepIdx = b; sweepLo = mb.low; }}
        }}
      }}
      if (govdeKirildi) continue;
      grup.forEach(([idxE]) => kulL.add(idxE));
      if (sweepIdx !== null) {{
        if (sweepIdx >= ct - 35) {{
          liqList.push({{ tip: '💧 EQL Sweep (SFP)', idx1: i1, idx2: sweepIdx, t1: mumlar[i1].time, t2: mumlar[sweepIdx].time, p1: ortL, p2: ortL, renk: '#10b981', aktif: false }});
          const sk = 'BULL_' + sweepIdx;
          if (!sfpEk.has(sk)) {{ sfpEk.add(sk); sfpList.push({{ tip: '▲ Bull SFP (EQL)', idx: sweepIdx, time: mumlar[sweepIdx].time, price: sweepLo, level: ortL, yon: 'BULL' }}); }}
        }}
      }} else {{
        const et = grup.length >= 3 ? '$$$ 3x EQL (TT3 SSL)' : '$$$ EQL (SSL)';
        liqList.push({{ tip: et, idx1: i1, idx2: ct - 1, t1: mumlar[i1].time, t2: mumlar[ct - 1].time, p1: ortL, p2: ortL, renk: '#38bdf8', aktif: true }});
      }}
    }}
  }}

  // 3) Tekil Swing SFP vs Gövde Kırılımı (23-sfp.pdf & Drive Video Ders-04/05)
  jn.slice(-8).forEach(([iH, vH]) => {{
    if (iH >= ct - 2) return;
    let ilkGecis = null;
    for (let b = iH + 1; b < ct; b++) {{ if (mumlar[b].high > vH + E * 0.02) {{ ilkGecis = b; break; }} }}
    if (ilkGecis !== null && ilkGecis >= Math.max(iH + 2, ct - 35)) {{
      const mb = mumlar[ilkGecis];
      const uIgne = mb.high - Math.max(mb.open, mb.close);
      let sonradanBozdu = false;
      for (let m = ilkGecis + 1; m < ct; m++) if (mumlar[m].close > mb.high) sonradanBozdu = true;
      const sk = 'BEAR_' + ilkGecis;
      if (mb.close < vH && uIgne >= E * 0.14 && !sonradanBozdu && !sfpEk.has(sk)) {{
        sfpEk.add(sk);
        sfpList.push({{ tip: '▼ Bear SFP (İğne Avı)', idx: ilkGecis, time: mumlar[ilkGecis].time, price: mb.high, level: vH, yon: 'BEAR' }});
        if (!kulH.has(iH)) liqList.push({{ tip: '💧 BSL Sweep (SFP)', idx1: iH, idx2: ilkGecis, t1: mumlar[iH].time, t2: mumlar[ilkGecis].time, p1: vH, p2: vH, renk: '#fb7185', aktif: false }});
      }}
    }}
  }});
  jo.slice(-8).forEach(([iL, vL]) => {{
    if (iL >= ct - 2) return;
    let ilkGecis = null;
    for (let b = iL + 1; b < ct; b++) {{ if (mumlar[b].low < vL - E * 0.02) {{ ilkGecis = b; break; }} }}
    if (ilkGecis !== null && ilkGecis >= Math.max(iL + 2, ct - 35)) {{
      const mb = mumlar[ilkGecis];
      const aIgne = Math.min(mb.open, mb.close) - mb.low;
      let sonradanBozdu = false;
      for (let m = ilkGecis + 1; m < ct; m++) if (mumlar[m].close < mb.low) sonradanBozdu = true;
      const sk = 'BULL_' + ilkGecis;
      if (mb.close > vL && aIgne >= E * 0.14 && !sonradanBozdu && !sfpEk.has(sk)) {{
        sfpEk.add(sk);
        sfpList.push({{ tip: '▲ Bull SFP (İğne Avı)', idx: ilkGecis, time: mumlar[ilkGecis].time, price: mb.low, level: vL, yon: 'BULL' }});
        if (!kulL.has(iL)) liqList.push({{ tip: '💧 SSL Sweep (SFP)', idx1: iL, idx2: ilkGecis, t1: mumlar[iL].time, t2: mumlar[ilkGecis].time, p1: vL, p2: vL, renk: '#34d399', aktif: false }});
      }}
    }}
  }});

  // 4) Inducement / IDM (Likidite Yemi - Drive Video Ders-03: Gerçek POI öncesi yarı yoldaki ilk küçük dip/tepe)
  if (jn.length >= 2 && jo.length >= 2) {{
    const [sonHi, sonHv] = jn[jn.length - 1];
    const [sonLi, sonLv] = jo[jo.length - 1];
    const oncekiAnaL = jo.filter(([il]) => il < sonHi);
    if (oncekiAnaL.length > 0 && sonHi < ct - 2) {{
      const [origLi, origLv] = oncekiAnaL[oncekiAnaL.length - 1];
      const bacakBoy = sonHv - origLv;
      if (bacakBoy >= E * 1.6) {{
        for (let b = sonHi + 1; b < ct - 1; b++) {{
          if (mumlar[b].low <= mumlar[b - 1].low && mumlar[b].low <= mumlar[b + 1].low) {{
            const vl = mumlar[b].low;
            if (vl >= origLv + bacakBoy * 0.18 && vl <= origLv + bacakBoy * 0.72) {{
              let supIdx = null;
              for (let m = b + 1; m < ct; m++) {{
                if (mumlar[m].low < vl - E * 0.02 && mumlar[m].close > origLv) {{ supIdx = m; break; }}
              }}
              if (supIdx !== null) {{
                liqList.push({{ tip: '💧 IDM Sweep (Yem Yutuldu ✓)', idx1: b, idx2: supIdx, t1: mumlar[b].time, t2: mumlar[supIdx].time, p1: vl, p2: vl, renk: '#2dd4bf', aktif: false }});
              }} else if (sonClose > vl) {{
                liqList.push({{ tip: '🎣 IDM (Likidite Yemi SSL)', idx1: b, idx2: ct - 1, t1: mumlar[b].time, t2: mumlar[ct - 1].time, p1: vl, p2: vl, renk: '#e879f9', aktif: true }});
              }}
              break;
            }}
          }}
        }}
      }}
    }}
    const oncekiAnaH = jn.filter(([ih]) => ih < sonLi);
    if (oncekiAnaH.length > 0 && sonLi < ct - 2) {{
      const [origHi, origHv] = oncekiAnaH[oncekiAnaH.length - 1];
      const bacakBoyB = origHv - sonLv;
      if (bacakBoyB >= E * 1.6) {{
        for (let b = sonLi + 1; b < ct - 1; b++) {{
          if (mumlar[b].high >= mumlar[b - 1].high && mumlar[b].high >= mumlar[b + 1].high) {{
            const vh = mumlar[b].high;
            if (vh >= sonLv + bacakBoyB * 0.28 && vh <= origHv - bacakBoyB * 0.18) {{
              let supIdx = null;
              for (let m = b + 1; m < ct; m++) {{
                if (mumlar[m].high > vh + E * 0.02 && mumlar[m].close < origHv) {{ supIdx = m; break; }}
              }}
              if (supIdx !== null) {{
                liqList.push({{ tip: '💧 IDM Sweep (Yem Yutuldu ✓)', idx1: b, idx2: supIdx, t1: mumlar[b].time, t2: mumlar[supIdx].time, p1: vh, p2: vh, renk: '#fb7185', aktif: false }});
              }} else if (sonClose < vh) {{
                liqList.push({{ tip: '🎣 IDM (Likidite Yemi BSL)', idx1: b, idx2: ct - 1, t1: mumlar[b].time, t2: mumlar[ct - 1].time, p1: vh, p2: vh, renk: '#e879f9', aktif: true }});
              }}
              break;
            }}
          }}
        }}
      }}
    }}
  }}

  // 5) Aktif External BSL (Eski Tepe) & External SSL (Eski Dip) (Ders-02 & Ders-10)
  const tazeH = jn.filter(([iH, vH]) => {{
    if (iH >= ct - 2 || vH <= sonClose) return false;
    for (let b = iH + 1; b < ct; b++) if (mumlar[b].high > vH + E * 0.03) return false;
    return true;
  }});
  if (tazeH.length > 0) {{
    const [extHi, extHv] = tazeH.reduce((best, cur) => cur[1] > best[1] ? cur : best, tazeH[0]);
    if (liqList.every(lq => Math.abs(extHv - lq.p1) > tolEq)) {{
      liqList.push({{ tip: '$$$ Ext BSL (Eski Tepe)', idx1: extHi, idx2: ct - 1, t1: mumlar[extHi].time, t2: mumlar[ct - 1].time, p1: extHv, p2: extHv, renk: '#f59e0b', aktif: true }});
    }}
  }}
  const tazeL = jo.filter(([iL, vL]) => {{
    if (iL >= ct - 2 || vL >= sonClose) return false;
    for (let b = iL + 1; b < ct; b++) if (mumlar[b].low < vL - E * 0.03) return false;
    return true;
  }});
  if (tazeL.length > 0) {{
    const [extLi, extLv] = tazeL.reduce((best, cur) => cur[1] < best[1] ? cur : best, tazeL[0]);
    if (liqList.every(lq => Math.abs(extLv - lq.p1) > tolEq)) {{
      liqList.push({{ tip: '$$$ Ext SSL (Eski Dip)', idx1: extLi, idx2: ct - 1, t1: mumlar[extLi].time, t2: mumlar[ct - 1].time, p1: extLv, p2: extLv, renk: '#0ea5e9', aktif: true }});
    }}
  }}

  // 6) 3-Temaslı Doğrulanmış Trendline Likiditesi
  const hSon6 = jn.slice(-6);
  let tlHBul = false;
  for (let a = 0; a < hSon6.length - 2 && !tlHBul; a++) {{
    for (let b = a + 1; b < hSon6.length - 1 && !tlHBul; b++) {{
      for (let c = b + 1; c < hSon6.length && !tlHBul; c++) {{
        const [x1, y1] = hSon6[a], [x2, y2] = hSon6[b], [x3, y3] = hSon6[c];
        if (x3 - x1 >= 6 && y1 > y2 && y2 > y3) {{
          const egim = (y3 - y1) / Math.max(1, x3 - x1);
          if (Math.abs(y2 - (y1 + egim * (x2 - x1))) <= E * 0.35) {{
            let ihlal = false;
            for (let m = x1 + 1; m < x3; m++) if (mumlar[m].high > (y1 + egim * (m - x1)) + E * 0.16) {{ ihlal = true; break; }}
            for (let m = x3 + 1; m < ct && !ihlal; m++) if (mumlar[m].close > (y1 + egim * (m - x1)) + E * 0.20) {{ ihlal = true; break; }}
            if (!ihlal) {{
              const xBit = Math.min(ct - 1, x3 + 12);
              liqList.push({{ tip: '📐 Trendline BSL ($$$)', idx1: x1, idx2: xBit, t1: mumlar[x1].time, t2: mumlar[xBit].time, p1: y1, p2: y1 + egim * (xBit - x1), renk: '#f59e0b', aktif: true }});
              tlHBul = true;
            }}
          }}
        }}
      }}
    }}
  }}
  const lSon6 = jo.slice(-6);
  let tlLBul = false;
  for (let a = 0; a < lSon6.length - 2 && !tlLBul; a++) {{
    for (let b = a + 1; b < lSon6.length - 1 && !tlLBul; b++) {{
      for (let c = b + 1; c < lSon6.length && !tlLBul; c++) {{
        const [x1, y1] = lSon6[a], [x2, y2] = lSon6[b], [x3, y3] = lSon6[c];
        if (x3 - x1 >= 6 && y1 < y2 && y2 < y3) {{
          const egim = (y3 - y1) / Math.max(1, x3 - x1);
          if (Math.abs(y2 - (y1 + egim * (x2 - x1))) <= E * 0.35) {{
            let ihlal = false;
            for (let m = x1 + 1; m < x3; m++) if (mumlar[m].low < (y1 + egim * (m - x1)) - E * 0.16) {{ ihlal = true; break; }}
            for (let m = x3 + 1; m < ct && !ihlal; m++) if (mumlar[m].close < (y1 + egim * (m - x1)) - E * 0.20) {{ ihlal = true; break; }}
            if (!ihlal) {{
              const xBit = Math.min(ct - 1, x3 + 12);
              liqList.push({{ tip: '📐 Trendline SSL ($$$)', idx1: x1, idx2: xBit, t1: mumlar[x1].time, t2: mumlar[xBit].time, p1: y1, p2: y1 + egim * (xBit - x1), renk: '#38bdf8', aktif: true }});
              tlLBul = true;
            }}
          }}
        }}
      }}
    }}
  }}
  return {{ likidite: liqList.slice(-11), sfp: sfpList.slice(-6) }};
}}
async function binanceMumCek(tf) {{
  const gercekTf = (typeof TF_GERCEK_HARITA !== 'undefined' && TF_GERCEK_HARITA[tf]) ? TF_GERCEK_HARITA[tf] : tf;
  const urls = IS_FUT
    ? [`https://fapi.binance.com/fapi/v1/klines?symbol=${{RAW_SYM}}&interval=${{gercekTf}}&limit=350`, `https://api.binance.com/api/v3/klines?symbol=${{RAW_SYM}}&interval=${{gercekTf}}&limit=350`]
    : [`https://api.binance.com/api/v3/klines?symbol=${{RAW_SYM}}&interval=${{gercekTf}}&limit=350`, `https://fapi.binance.com/fapi/v1/klines?symbol=${{RAW_SYM}}&interval=${{gercekTf}}&limit=350`];
  for (const url of urls) {{
    try {{
      const r = await fetch(url);
      const d = await r.json();
      if (Array.isArray(d) && d.length > 5) {{
        return d.map((k, idx) => ({{
          time: Math.floor(Number(k[0]) / 1000),
          idx: idx,
          open: parseFloat(k[1]),
          high: parseFloat(k[2]),
          low: parseFloat(k[3]),
          close: parseFloat(k[4]),
          volume: parseFloat(k[5] || 0)
        }}));
      }}
    }} catch (e) {{}}
  }}
  return [];
}}

async function anlikFiyatPolling() {{
  const urls = IS_FUT
    ? [`https://fapi.binance.com/fapi/v1/ticker/price?symbol=${{RAW_SYM}}`, `https://api.binance.com/api/v3/ticker/price?symbol=${{RAW_SYM}}`]
    : [`https://api.binance.com/api/v3/ticker/price?symbol=${{RAW_SYM}}`, `https://fapi.binance.com/fapi/v1/ticker/price?symbol=${{RAW_SYM}}`];
  for (const u of urls) {{
    try {{
      const r = await fetch(u);
      const j = await r.json();
      const p = parseFloat(j.price || 0);
      if (p > 0 && candleSeries && aktifMumlar.length > 0) {{
        const son = Object.assign({{}}, aktifMumlar[aktifMumlar.length - 1]);
        son.close = p;
        if (p > son.high) son.high = p;
        if (p < son.low) son.low = p;
        aktifMumlar[aktifMumlar.length - 1] = son;
        candleSeries.update(son);
        const lbl = document.getElementById('lbl_anlik_fiyat');
        if (lbl) lbl.innerText = `⚡ Anlık: ${{fiyatFormatla(p)}}`;
        requestAnimationFrame(() => cizPineGostergeKatmani());
        break;
      }}
    }} catch (e) {{}}
  }}
}}

function canliWebSocketBaslat(tf) {{
  if (wsBaglanti) {{
    try {{ wsBaglanti.close(); }} catch (e) {{}}
    wsBaglanti = null;
  }}
  if (fiyatTimer) clearInterval(fiyatTimer);
  fiyatTimer = setInterval(anlikFiyatPolling, 1500);
  try {{
    const gercekWsTf = (typeof TF_GERCEK_HARITA !== 'undefined' && TF_GERCEK_HARITA[tf]) ? TF_GERCEK_HARITA[tf] : tf;
    const wsUrl = IS_FUT
      ? `wss://fstream.binance.com/ws/${{RAW_SYM.toLowerCase()}}@kline_${{gercekWsTf}}`
      : `wss://stream.binance.com:9443/ws/${{RAW_SYM.toLowerCase()}}@kline_${{gercekWsTf}}`;
    wsBaglanti = new WebSocket(wsUrl);
    wsBaglanti.onmessage = (ev) => {{
      try {{
        const msg = JSON.parse(ev.data);
        if (msg && msg.k && candleSeries) {{
          const k = msg.k;
          const yeniMum = {{
            time: Math.floor(Number(k.t) / 1000),
            idx: Math.max(0, aktifMumlar.length - 1),
            open: parseFloat(k.o),
            high: parseFloat(k.h),
            low: parseFloat(k.l),
            close: parseFloat(k.c)
          }};
          candleSeries.update(yeniMum);
          if (aktifMumlar.length > 0 && aktifMumlar[aktifMumlar.length - 1].time === yeniMum.time) {{
            aktifMumlar[aktifMumlar.length - 1] = yeniMum;
          }} else if (aktifMumlar.length === 0 || yeniMum.time > aktifMumlar[aktifMumlar.length - 1].time) {{
            yeniMum.idx = aktifMumlar.length;
            aktifMumlar.push(yeniMum);
          }}
          const lbl = document.getElementById('lbl_anlik_fiyat');
          if (lbl) lbl.innerText = `⚡ Anlık: ${{fiyatFormatla(yeniMum.close)}}`;
          requestAnimationFrame(() => cizPineGostergeKatmani());
        }}
      }} catch (err) {{}}
    }};
  }} catch (e) {{}}
}}

function anlikGrafigeOdaklan() {{
  chart.timeScale().scrollToRealTime();
  requestAnimationFrame(() => cizPineGostergeKatmani());
}}

function pineKodunuSimdiUygula() {{
  const veri = TUM_VERI[aktifTf] || TUM_VERI['5m'];
  const pineText = document.getElementById('pine_box').value;
  parseEdilenPine = pineKodunuParseEt(pineText, veri);
  katmanlariSimdiGuncelle();
}}

async function periyotDegistir(tf) {{
  aktifTf = tf;
  ['4h','1h','5m'].forEach(k => {{
    const b = document.getElementById('btn_' + k);
    if (b) b.classList.toggle('active', k === tf);
  }});
  const veri = TUM_VERI[tf] || TUM_VERI['5m'];
  const gTfAd = ((typeof TF_GERCEK_HARITA !== 'undefined' && TF_GERCEK_HARITA[tf]) ? TF_GERCEK_HARITA[tf] : tf).toUpperCase();
  const aktSblStr = `${{(TF_GERCEK_HARITA['4h'] || '4h').toUpperCase()}}/${{(TF_GERCEK_HARITA['1h'] || '1h').toUpperCase()}}/${{TF_GERCEK_HARITA['5m'] || '5m'}}`;
  document.getElementById('lbl_parite').innerText = `{O} (${{TV_SYM}}) | ${{gTfAd}} (Şablon: ${{aktSblStr}})`;
  document.getElementById('karne_baslik').innerText = `📊 {O} [${{gTfAd}}] — Strateji & Seviye Karnesi`;
  document.getElementById('pine_baslik').innerText = `📜 Aktif Pine Script v6 Kodu (${{gTfAd}}):`;
  document.getElementById('pine_box').value = veri.pine || '';
  document.getElementById('kysy_satir').innerHTML = `• <b>Kırılım Yoksa Swing Yoktur:</b> ${{veri.kysy_onay ? '<span style="color:#4ade80">ONAYLI</span>' : '<span style="color:#f59e0b">KIRILIM YOK</span>'}} (Elenen Gürültü: ${{veri.elenen_sayi}})`;
  document.getElementById('sp_wp_satir').innerHTML = `• <b style="color:#eab308;">Strong Origin / Weak Target:</b> ${{veri.sp ? veri.sp.toFixed(4) : '-'}} / ${{veri.wp ? veri.wp.toFixed(4) : '-'}}`;
  document.getElementById('ist_satir').innerHTML = `• <b style="color:#f472b6;">Magic Line (FL) / ITZ / QML:</b> ${{veri.magic ? veri.magic.toFixed(4) : '-'}} / ${{veri.itz ? veri.itz.toFixed(4) : '-'}} / ${{veri.qml ? veri.qml.toFixed(4) : '-'}}`;

  parseEdilenPine = pineKodunuParseEt(veri.pine || '', veri);

  if (candleSeries) {{ try {{ chart.removeSeries(candleSeries); }} catch(e){{}} }}
  candleSeries = chart.addCandlestickSeries({{
    upColor: '#22c55e', downColor: '#ef4444', borderVisible: false, wickUpColor: '#4ade80', wickDownColor: '#f87171'
  }});

  if (veri.mumlar && veri.mumlar.length > 0) {{
    aktifMumlar = veri.mumlar.slice();
    const ilkKysy = kysySwingHesaplaJS(aktifMumlar, tf === '5m' ? 2 : 5, tf);
    veri.zigzag = ilkKysy.zigzag;
    veri.bos = ilkKysy.bos;
    veri.arz_talep = ilkKysy.arz_talep;
    veri.imbalance = ilkKysy.imbalance;
    if (ilkKysy.likidite && ilkKysy.likidite.length > 0) veri.likidite = ilkKysy.likidite;
    if (ilkKysy.sfp) veri.sfp = ilkKysy.sfp;
    if (ilkKysy.qml > 0) {{ veri.qml = ilkKysy.qml; parseEdilenPine.qml = ilkKysy.qml; veri.qml_t1 = ilkKysy.qml_t1; veri.qml_idx = ilkKysy.qml_idx; }} else if (veri.qml > 0) {{ parseEdilenPine.qml = veri.qml; }}
    if (ilkKysy.smax > ilkKysy.smin && ilkKysy.smin > 0) {{
      veri.yon = ilkKysy.yon; veri.smax = ilkKysy.smax; veri.smin = ilkKysy.smin;
      veri.sp = ilkKysy.sp; veri.wp = ilkKysy.wp;
      veri.fibo_t1 = ilkKysy.fibo_t1;
      parseEdilenPine.smax = ilkKysy.smax; parseEdilenPine.smin = ilkKysy.smin;
      parseEdilenPine.sp = ilkKysy.sp; parseEdilenPine.wp = ilkKysy.wp;
    }}
    candleSeries.setData(aktifMumlar);
    const sonF = aktifMumlar[aktifMumlar.length - 1].close;
    document.getElementById('lbl_anlik_fiyat').innerText = `⚡ Anlık: ${{fiyatFormatla(sonF)}}`;
  }}

  seriKatmanlariniGuncelle();
  chart.timeScale().fitContent();
  chart.timeScale().scrollToRealTime();
  setTimeout(boyutlariEsitle, 40);

  const canliMumlar = await binanceMumCek(tf);
  if (canliMumlar && canliMumlar.length > 5 && aktifTf === tf) {{
    const birlesikMap = new Map();
    (veri.mumlar || []).forEach(m => birlesikMap.set(m.time, m));
    canliMumlar.forEach(m => birlesikMap.set(m.time, m));
    const sirali = Array.from(birlesikMap.values()).sort((a, b) => a.time - b.time).slice(-350);
    sirali.forEach((m, i) => {{ m.idx = i; }});
    aktifMumlar = sirali;
    const yeniKysy = kysySwingHesaplaJS(aktifMumlar, tf === '5m' ? 2 : 5, tf);
    veri.zigzag = yeniKysy.zigzag;
    veri.bos = yeniKysy.bos;
    veri.arz_talep = yeniKysy.arz_talep;
    veri.imbalance = yeniKysy.imbalance;
    veri.likidite = yeniKysy.likidite;
    veri.sfp = yeniKysy.sfp;
    veri.elenen = [];
    if (yeniKysy.qml > 0) {{ veri.qml = yeniKysy.qml; parseEdilenPine.qml = yeniKysy.qml; veri.qml_t1 = yeniKysy.qml_t1; veri.qml_idx = yeniKysy.qml_idx; }} else if (veri.qml > 0) {{ parseEdilenPine.qml = veri.qml; }}
    if (yeniKysy.smax > yeniKysy.smin && yeniKysy.smin > 0) {{
      veri.yon = yeniKysy.yon;
      veri.smax = yeniKysy.smax;
      veri.smin = yeniKysy.smin;
      veri.sp = yeniKysy.sp;
      veri.wp = yeniKysy.wp;
      veri.fibo_t1 = yeniKysy.fibo_t1;
      parseEdilenPine.smax = yeniKysy.smax;
      parseEdilenPine.smin = yeniKysy.smin;
      parseEdilenPine.sp = yeniKysy.sp;
      parseEdilenPine.wp = yeniKysy.wp;
      if (GIRIS > 0) parseEdilenPine.giris = GIRIS;
      if (SL > 0) parseEdilenPine.sl = SL;
      if (TP1 > 0) parseEdilenPine.tp1 = TP1;
      if (TP2 > 0) parseEdilenPine.tp2 = TP2;
      document.getElementById('sp_wp_satir').innerHTML = `• <b style="color:#eab308;">Strong Origin (HTF Dip/Tepe) / Weak Target:</b> ${{veri.sp ? veri.sp.toFixed(2) : '-'}} / ${{veri.wp ? veri.wp.toFixed(2) : '-'}}`;
      document.getElementById('ist_satir').innerHTML = `• <b style="color:#f472b6;">Magic Line (FL) / ITZ / 4H QML:</b> ${{veri.magic ? veri.magic.toFixed(2) : '-'}} / ${{veri.itz ? veri.itz.toFixed(2) : '-'}} / ${{veri.qml ? veri.qml.toFixed(2) : '-'}}`;
    }}
    candleSeries.setData(aktifMumlar);
    rsiSeries.setData(rsiHesapla(aktifMumlar, 14));
    const sonCanli = aktifMumlar[aktifMumlar.length - 1].close;
    document.getElementById('lbl_anlik_fiyat').innerText = `⚡ Anlık: ${{fiyatFormatla(sonCanli)}}`;
    seriKatmanlariniGuncelle();
    chart.timeScale().setVisibleLogicalRange({{ from: Math.max(0, aktifMumlar.length - 180), to: aktifMumlar.length + 8 }});
    requestAnimationFrame(() => cizPineGostergeKatmani());
    setTimeout(() => cizPineGostergeKatmani(), 60);
    setTimeout(() => cizPineGostergeKatmani(), 180);
  }} else if (aktifMumlar.length > 0) {{
    rsiSeries.setData(rsiHesapla(aktifMumlar, 14));
    setTimeout(() => cizPineGostergeKatmani(), 60);
  }}

  canliWebSocketBaslat(tf);
  anlikFiyatPolling();
}}

function mtfSablonDegistirJS(deger) {{
  if (!deger) return;
  const parcalar = String(deger).split(',');
  if (parcalar.length === 3) {{
    TF_GERCEK_HARITA['4h'] = parcalar[0].trim();
    TF_GERCEK_HARITA['1h'] = parcalar[1].trim();
    TF_GERCEK_HARITA['5m'] = parcalar[2].trim();
    const b4 = document.getElementById('btn_4h');
    const b1 = document.getElementById('btn_1h');
    const b5 = document.getElementById('btn_5m');
    if (b4) b4.innerText = `🏛️ HTF (${{TF_GERCEK_HARITA['4h'].toUpperCase()}})`;
    if (b1) b1.innerText = `🧭 MTF (${{TF_GERCEK_HARITA['1h'].toUpperCase()}})`;
    if (b5) b5.innerText = `🎯 LTF (${{TF_GERCEK_HARITA['5m']}})`;
    periyotDegistir(aktifTf);
  }}
}}

function bilgiPaneliToggle() {{
  const sp = document.getElementById('side_panel');
  const btn = document.getElementById('btn_bilgi_toggle');
  const fab = document.getElementById('btn_bilgi_fab');
  if (!sp) return;
  const gizlendiMi = sp.classList.toggle('gizli');
  if (btn) {{
    btn.innerText = gizlendiMi ? '📊 Bilgi Ekranı: Kapalı (Aç ◀)' : '📊 Bilgi Ekranı: Açık ◀▶';
    btn.style.background = gizlendiMi ? '#475569' : '#f59e0b';
    btn.style.color = gizlendiMi ? '#f8fafc' : '#11111b';
  }}
  if (fab) fab.classList.toggle('goster', gizlendiMi);
  requestAnimationFrame(boyutlariEsitle);
  setTimeout(boyutlariEsitle, 35);
  setTimeout(boyutlariEsitle, 120);
}}

function karneIcerikToggle() {{
  const ic = document.getElementById('karne_icerik_kapsayici');
  const bs = document.getElementById('karne_baslik');
  if (!ic) return;
  const kapali = ic.style.display === 'none';
  ic.style.display = kapali ? 'block' : 'none';
  if (bs) {{
    bs.innerText = bs.innerText.replace(/[▾▸]/g, '').trim() + (kapali ? ' ▾' : ' ▸');
  }}
}}

function rsiPanelToggle() {{
  const rp = document.getElementById('rsi_pane');
  const ch = document.getElementById('chk_rsi');
  if (ch) rp.classList.toggle('show', ch.checked);
  else rp.classList.toggle('show');
  setTimeout(boyutlariEsitle, 30);
}}

function boyutlariEsitle() {{
  const r = stageEl.getBoundingClientRect();
  if (r.width > 0 && r.height > 0) {{
    chart.applyOptions({{ width: r.width, height: r.height }});
  }}
  const rp = document.getElementById('rsi_pane');
  if (rp && rp.classList.contains('show')) {{
    const rr = rp.getBoundingClientRect();
    if (rr.width > 0 && rr.height > 0) {{
      rsiChart.applyOptions({{ width: rr.width, height: rr.height }});
    }}
  }}
  requestAnimationFrame(() => cizPineGostergeKatmani());
}}

function gorunumDegistir() {{
  widgetModu = !widgetModu;
  const btn = document.getElementById('btn_mod');
  const wDiv = document.getElementById('tv_native_widget');
  if (widgetModu) {{
    btn.innerText = '🌲 Alfa PA Çizimli Grafik Göster';
    btn.classList.add('active');
    if (wDiv) {{
      wDiv.style.display = 'block';
      const gTf = (typeof TF_GERCEK_HARITA !== 'undefined' && TF_GERCEK_HARITA[aktifTf]) ? TF_GERCEK_HARITA[aktifTf] : aktifTf;
      const tvIntervalMap = {{ '1m':'1', '3m':'3', '5m':'5', '15m':'15', '30m':'30', '1h':'60', '2h':'120', '4h':'240', '1d':'D', '1w':'W', '1M':'M' }};
      const tvInt = tvIntervalMap[gTf] || '15';
      const tvFullSym = 'BINANCE:' + RAW_SYM + (IS_FUT ? '.P' : '');
      wDiv.innerHTML = '<div id="tv_widget_inner" style="width:100%;height:100%;"></div>';
      if (typeof TradingView !== 'undefined' && TradingView.widget) {{
        new TradingView.widget({{
          autosize: true,
          symbol: tvFullSym,
          interval: tvInt,
          timezone: 'Europe/Istanbul',
          theme: 'dark',
          style: '1',
          locale: 'tr',
          toolbar_bg: '#131722',
          enable_publishing: false,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          container_id: 'tv_widget_inner'
        }});
      }} else {{
        wDiv.innerHTML = `<iframe src="https://s.tradingview.com/widgetembed/?symbol=${{encodeURIComponent(tvFullSym)}}&interval=${{tvInt}}&theme=dark&style=1&timezone=Europe%2FIstanbul&locale=tr" style="width:100%;height:100%;border:0;" allowfullscreen></iframe>`;
      }}
    }}
  }} else {{
    btn.innerText = '🌐 Canlı TV Widget Göster';
    btn.classList.remove('active');
    if (wDiv) {{
      wDiv.style.display = 'none';
      wDiv.innerHTML = '';
    }}
    boyutlariEsitle();
    anlikGrafigeOdaklan();
  }}
}}

const GEMINI_API_KEY_JS = "{GEMINI_API_KEY}";
const GEMINI_MODEL_JS = "{GEMINI_MODEL}";
const ISLEM_RONTGEN_METNI_JS = {json.dumps(islem_rontgeni_olustur(O, H).get('tam_rapor_metni','') if 'islem_rontgeni_olustur' in globals() else '', ensure_ascii=False)};

function geminiKatmanGoster() {{
  ['chk_zz','chk_arztalep','chk_kutu','chk_ist','chk_fibo','chk_liq','chk_rr'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.checked = true;
  }});
  if (widgetModu) gorunumDegistir();
  katmanlariSimdiGuncelle();
  anlikGrafigeOdaklan();
  const kutu = document.getElementById('gemini_tv_cevap');
  if (kutu) kutu.innerText = "✅ Grafik üzerinde Giriş, SL/TP, KYSY Swing/QML, Gerçek OB (%50 MT), FVG (%50 CE), 3 İstasyon ve Likidite (EQH/EQL, IDM, SFP) katmanlarının tamamı çizildi!\\n\\n" + (ISLEM_RONTGEN_METNI_JS || "");
}}

function geminiHizliSor(s) {{
  const inp = document.getElementById('gemini_tv_soru');
  if (inp) inp.value = s;
  geminiSorJS();
}}

async function geminiSorJS() {{
  const inp = document.getElementById('gemini_tv_soru');
  const kutu = document.getElementById('gemini_tv_cevap');
  if (!inp || !kutu) return;
  const soru = (inp.value || '').trim() || 'Bu işlemi neye göre açtın?';
  if (soru.toLowerCase().includes('çiz') || soru.toLowerCase().includes('göster')) {{
    geminiKatmanGoster();
  }}
  if (!GEMINI_API_KEY_JS) {{
    kutu.innerText = "⏳ Yapay Zeka sorunuzu yanıtlıyor...";
    try {{
      const rFree = await fetch('https://text.pollinations.ai/openai', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          model: 'openai',
          messages: [
            {{ role: 'system', content: 'Sen Alfa Trade Club Bot içindeki özgür Price Action & ICT yapay zeka asistanısın. Hazır kalıp kullanmadan, doğrudan ve net Türkçe cevap ver. Veri: ' + ISLEM_RONTGEN_METNI_JS }},
            {{ role: 'user', content: soru }}
          ]
        }})
      }});
      const jFree = await rFree.json();
      const cvpFree = jFree?.choices?.[0]?.message?.content;
      if (cvpFree) {{ kutu.innerText = "🤖 Gemini AI Asistan:\\n" + cvpFree; return; }}
    }} catch(e) {{}}
    kutu.innerText = "🤖 AI Özeti:\\n" + (ISLEM_RONTGEN_METNI_JS || "İşlem verisi hazır.");
    return;
  }}
  kutu.innerText = "⏳ Gemini AI (" + GEMINI_MODEL_JS + ") işlemi ve grafiği inceliyor...";
  try {{
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${{GEMINI_MODEL_JS}}:generateContent?key=${{GEMINI_API_KEY_JS}}`;
    const prompt = `Sen Alfa Trade Club Bot {BOT_VERSIYONU} içindeki kurumsal Price Action & ICT uzmanısın. Aşağıdaki işlem röntgenine göre kullanıcının sorusunu net, maddeli ve Türkçe yanıtla:\\n\\n${{ISLEM_RONTGEN_METNI_JS}}\\n\\nKullanıcı Sorusu: ${{soru}}`;
    const r = await fetch(url, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ contents: [{{ parts: [{{ text: prompt }}] }}] }})
    }});
    const j = await r.json();
    const cvp = j?.candidates?.[0]?.content?.parts?.[0]?.text;
    kutu.innerText = cvp ? `🤖 Gemini AI (${{GEMINI_MODEL_JS}}):\\n` + cvp : ("🤖 [Dahili Röntgen]:\\n" + ISLEM_RONTGEN_METNI_JS);
  }} catch (e) {{
    kutu.innerText = "🤖 [Dahili Röntgen]:\\n" + ISLEM_RONTGEN_METNI_JS;
  }}
}}

function kopyalaPine() {{
  const el = document.getElementById('pine_box');
  el.select();
  document.execCommand('copy');
}}

chart.timeScale().subscribeVisibleLogicalRangeChange(() => {{
  requestAnimationFrame(() => cizPineGostergeKatmani());
  const lr = chart.timeScale().getVisibleLogicalRange();
  if (lr) rsiChart.timeScale().setVisibleLogicalRange(lr);
}});
chart.subscribeCrosshairMove(() => requestAnimationFrame(() => cizPineGostergeKatmani()));
window.addEventListener('resize', boyutlariEsitle);
if (typeof ResizeObserver !== 'undefined') {{
  new ResizeObserver(() => boyutlariEsitle()).observe(stageEl);
}}
window.addEventListener('load', () => {{
  boyutlariEsitle();
  setTimeout(boyutlariEsitle, 150);
}});
periyotDegistir(aktifTf);
</script>
</body>
</html>"""
 dosya_yolu=os.path.join(ANDROID_VERI_DIZINI, f"tv_canli_{O.replace(':','_').replace('/','_')}_{tf_secim}.html")
 with open(dosya_yolu,'w',encoding='utf-8')as f:f.write(html_icerik)
 if 'KALICI_VERI_DIZINI' not in globals() and globals().get('_AKTIF_PAGE_REF') is None:
  try:
   if os.name=='nt':os.startfile(dosya_yolu)
   else:webbrowser.open(Path(dosya_yolu).as_uri())
  except X:pass
 return(dosya_yolu,pine_kodu)
# ==============================================================================
# BULUT SENKRONİZASYON (PC <-> ANDROID EŞLEŞTİRME) VE TEK TUŞLA OTA GÜNCELLEME
# ==============================================================================
import base64 as _b64

if "GITHUB_REPO_ADRESI" not in globals() or not GITHUB_REPO_ADRESI: GITHUB_REPO_ADRESI = "emrhozbr/bot"
if "GITHUB_TOKEN" not in globals(): GITHUB_TOKEN = ""
BULUT_SENK_AKTIF = True
_SON_BULUT_OKUMA_TS = 0.0
_SON_BULUT_YAZMA_HASH = ""
_BULUT_DOSYA_ADI = "senkron_durum.json"
_OTA_YEREL_CEKIRDEK = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_cekirdek_motor.py')
try:
    _api_yukle()
except Exception:
    pass


def _temiz_etiket_grafik(txt):
 return re.sub(r'[^\x00-\x7FğüşıöçĞÜŞİÖÇâîûÂÎÛ$€£%±×÷≤≥≠≈•–—…✓✔✕✖▲▼◀▶★☆]+','',str(txt)).strip()

def _google_hesap_token_bul():
 """Kullanicinin tanimli GEMINI_API_KEY anahtarini, ortam degiskenlerini veya Google Cloud / OAuth ADC kimligini otomatik bulur."""
 global GEMINI_API_KEY
 if GEMINI_API_KEY and L(str(GEMINI_API_KEY).strip())>10:
  return('api_key',str(GEMINI_API_KEY).strip())
 for env_k in('GEMINI_API_KEY','GOOGLE_API_KEY','GENAI_API_KEY'):
  val=os.environ.get(env_k,'').strip()
  if L(val)>10:
   GEMINI_API_KEY=val
   return('api_key',val)
 try:
  r=_subp.run(['gcloud','auth','application-default','print-access-token'],capture_output=True,text=True,timeout=2.0)
  if r.returncode==0 and L(r.stdout.strip())>20:
   return('oauth_token',r.stdout.strip())
 except Exception:
  pass
 return(None,'')

def gemini_hesap_durumu_getir():
 tip,deger=_google_hesap_token_bul()
 if tip=='api_key':
  maskeli=(deger[:6]+'...'+deger[-4:])if L(deger)>12 else'Aktif'
  return(True,f"🟢 Gemini API Bağlı ({maskeli} | {GEMINI_MODEL})")
 if tip=='oauth_token':
  return(True,f"🟢 Google Hesabı OAuth Bağlı ({GEMINI_MODEL})")
 return(True,'🟢 Özgür Bulut AI + Ajan Modu Aktif (Kendi Gemini API Anahtarınızı da Bağlayabilirsiniz)')

def islem_rontgeni_olustur(O,H_analiz=None,islem_kaydi=None):
 """Secili islem veya parite icin tum yapisal/sayisal verileri (AI baglami icin) derler."""
 O_str=str(O or'FUT:BTC/USDT')
 dR=islem_kaydi if I(islem_kaydi,dict)else(acik_islemler.get(O_str)if I(acik_islemler.get(O_str),dict)else None)
 if dR is None and':'in O_str:
  for g_item in ah:
   if I(g_item,dict)and g_item.get('sembol')==O_str:
    if I(g_item.get('rontgen'),dict):
     return g_item['rontgen']
    dR=g_item
    break
 H=H_analiz if(I(H_analiz,dict)and H_analiz)else(analiz_hafizasi.get(O_str)or analiz_hafizasi.get(O_str.split(':',1)[-1])or{})
 J=(dR.get('sembol')if I(dR,dict)and'/'in str(dR.get('sembol',''))else None)or H.get('sembol')or O_str.split(':',1)[-1]
 D=(dR.get('piyasa')if I(dR,dict)and dR.get('piyasa')else None)or H.get('piyasa')or('spot'if O_str.startswith('SPOT:')else'future')
 htf_p,mtf_p,ltf_p,mtf_sb=_parite_mtf_periyotlarini_bul(O_str,J,D,H)
 yon=(dR.get('yon')if I(dR,dict)else None)or H.get('sinyal')or H.get('ana_yon')or'BEKLE'
 giris=F((dR.get('giris')if I(dR,dict)else None)or H.get('giris')or(_f(H.get('df_15m'),'close',-1)if I(H.get('df_15m'),pd.DataFrame)else 0.0))
 anlik_f=F((dR.get('anlik')if I(dR,dict)and dR.get('anlik')else None)or(_f(H.get('df_15m'),'close',-1)if I(H.get('df_15m'),pd.DataFrame)else giris))
 sl=F((dR.get('sl')if I(dR,dict)else None)or H.get('sl')or 0.0)
 ilk_sl=F((dR.get('ilk_sl')if I(dR,dict)else None)or sl)
 rk=A(giris-ilk_sl)if giris>0 and ilk_sl>0 else 0.0
 mO=-1.0 if yon=='SHORT'else 1.0
 tp1=F((dR.get('tp')if I(dR,dict)else None)or(giris+mO*rk*RISK_ODUL_ORANI if rk>0 else 0.0))
 tp2=F((dR.get('tp_nihai')if I(dR,dict)else None)or(giris+mO*rk*M(NIHAI_TP_RR,RISK_ODUL_ORANI+1.0)if rk>0 else 0.0))
 miktar=F((dR.get('miktar')if I(dR,dict)else None)or 0.0)
 marjin_u=F((dR.get('marjin_usdt')if I(dR,dict)else None)or 0.0)
 risk_u=F((dR.get('risk_usdt')if I(dR,dict)else None)or ISLEM_BASI_RISK_USDT)
 if miktar<=0 and giris>0 and sl>0:
  try:miktar,marjin_u,risk_u=dinamik_miktar_hesapla(J,giris,sl,D,H.get('skor',70))
  except Exception:pass
 kFlt=H.get('konum_meta',{})if I(H.get('konum_meta'),dict)else{}
 chk=kFlt.get('checklist',{})if I(kFlt.get('checklist'),dict)else{}
 p1,p2,p3,p4=H.get('atli_puanlar',(0,0,0,0))
 skor=int(H.get('skor',0)or(dR.get('skor',0)if I(dR,dict)else 0))
 bolge_10p=F(H.get('bolge_10p_skor',0.0))
 aktif_htf_bolgeler=kFlt.get('aktif_htf_bolgeler',[])
 aktif_birincil_bolgeler=kFlt.get('aktif_birincil_bolgeler',[])
 birincil_olcek_skoru=int(kFlt.get('birincil_olcek_skoru',0))
 birincil_olcek_carpani=F(kFlt.get('birincil_olcek_carpani_etkin',0.35))
 oncelik_etiket=kFlt.get('en_yuksek_oncelik_etiket','1.Öncelik:QML/OB/Fresh/OTE')
 bolge_kademesi=int(kFlt.get('bolge_kademesi',1)or 1)
 safe_sayisi=int(kFlt.get('htf_bolge_sayisi',dR.get('uygun_kural_sayisi',1)if I(dR,dict)else 0))
 safe_puan=int(kFlt.get('htf_safe_puan',dR.get('uygun_alt_kural_sayisi',80)if I(dR,dict)else 0))
 safe_derece=kFlt.get('htf_safe_derecesi','🛡️ SAFE')
 ltf_kirilimlar=kFlt.get('ltf_kirilim_listesi',[])
 ltf_mumlar=kFlt.get('ltf_mum_listesi',[])
 aktif_ltf_tetikler=kFlt.get('aktif_ltf_tetikler',[])
 stop_kaynak=kFlt.get('stop_kaynak_bilgi',STOP_BELIRLEME_MODU)
 yapi_4h=H.get('yapi_4h',{})if I(H.get('yapi_4h'),dict)else{}
 yapi_1h=H.get('yapi_1h',{})if I(H.get('yapi_1h'),dict)else{}
 v6=H.get('v6_meta',{})if I(H.get('v6_meta'),dict)else{}
 v8=H.get('v8_meta',{})if I(H.get('v8_meta'),dict)else{}
 v12=H.get('v12_meta',{})if I(H.get('v12_meta'),dict)else{}
 giris_kurallari=(dR.get('giris_kurallari')if I(dR,dict)and dR.get('giris_kurallari')else None)or H.get('detayli_kurallar',[])
 ozet_str=(dR.get('ozet')if I(dR,dict)and dR.get('ozet')else None)or H.get('ozet','-')
 denetim_notlari=[]
 if kFlt.get('htf_oncelikli_bolge_onay'):
  denetim_notlari.append(f"1.Öncelik İlk Kontrol GEÇTİ: Fiyat {kFlt.get('htf_oncelikli_bolge_sayisi',1)}/4 ana bölgede ({'+'.join(aktif_birincil_bolgeler)}) | Ölçek: {birincil_olcek_skoru}/10000p ({birincil_olcek_carpani:.2f}x).")
 elif safe_sayisi>=1:
  denetim_notlari.append(f"2.Kademe Yedek Bölge: Fiyat 1.Öncelik (Arz/Talep, OB, OTE, QML) dışında, yedek bölgede ({', '.join(aktif_htf_bolgeler)}) | Ölçek: {birincil_olcek_skoru}/10000p.")
 else:
  denetim_notlari.append("HTF Bölge Dışı: Fiyat şu an Arz/Talep, OB, OTE, QML veya yedek bölgelerin hiçbirinde değil (giriş kilidi aktif).")
 if ltf_kirilimlar and ltf_mumlar:
  denetim_notlari.append(f"Çifte LTF Onayı (3a+3b): Hem kırılım ({', '.join(ltf_kirilimlar[:2])}) hem mum ({', '.join(ltf_mumlar[:2])}) var.")
 elif ltf_kirilimlar or ltf_mumlar:
  denetim_notlari.append(f"Tekil LTF Onayı: {', '.join((ltf_kirilimlar[:2]+ltf_mumlar[:2]))}.")
 else:
  denetim_notlari.append("LTF Onayı Bekleniyor: Henüz LTF dönüş kırılımı veya mumu oluşmadı.")
 if giris>0 and sl>0:
  sl_yuzde=A(giris-sl)/M(giris,1e-09)*100.0
  if sl_yuzde<0.22:
   denetim_notlari.append(f"Dar Stop Uyarısı: Stop mesafesi %{sl_yuzde:.2f} (iğne avına karşı HTF stopa çekilebilir).")
  elif sl_yuzde>3.8:
   denetim_notlari.append(f"Geniş Stop Notu: Stop mesafesi %{sl_yuzde:.2f} (1R sabit -{risk_u:.2f}$ korunuyor, LTF dar stop ile R:R büyütülebilir).")
  else:
   denetim_notlari.append(f"Optimal Stop Mesafesi: %{sl_yuzde:.2f} ({stop_kaynak}), 1R = -{risk_u:.2f}$.")
 fibo_oran_4h=F(yapi_4h.get('fibo_oran',0.5)or 0.5)*100.0
 tam_metin=(
  f"Parite: {O_str} ({D.upper()}) | Yön: {yon} | Anlık: {_fmt_f(anlik_f)} | Skor: {skor}/100 (1.Atlı:{p1}, 2.Atlı:{p2}, 3.Atlı:{p3}, 4.Atlı:{p4}) | 1.Öncelik Ölçek: {birincil_olcek_skoru}/10000p ({birincil_olcek_carpani:.2f}x)\n"
  f"MTF: {htf_p.upper()}/{mtf_p.upper()}/{ltf_p} | HTF Yön: {H.get('yon_4h',yapi_4h.get('yon','-'))} (Fibo:%{fibo_oran_4h:.1f}) | MTF Yön: {H.get('yon_1h',yapi_1h.get('yon','-'))}\n"
  f"HTF Safe Bölge ({safe_sayisi}/8 - {safe_derece} - {oncelik_etiket}): {', '.join(aktif_htf_bolgeler) if aktif_htf_bolgeler else 'Bölge Dışı'} | QML:{chk.get('qml_fiyat','-')} | OB:{chk.get('ob_aralik','-')} | Fresh:{chk.get('fresh_aralik','-')} | OTE:{chk.get('ote_aralik','-')} | ITZ:{chk.get('itz_fiyat','-')} | Magic:{chk.get('magic_fiyat','-')}\n"
  f"Likidite & Imbalance: {v8.get('likidite_turu','-')} | SFP:{v8.get('sfp_durumu','-')} | FVG:{v6.get('imbalance_tipi','-')} | DVG:{v12.get('dvg_durumu','-')} | SMT:{v12.get('smt_durumu','-')}\n"
  f"LTF Tetikleyiciler: Kırılım(3a)={', '.join(ltf_kirilimlar)or'Yok'} | Mum(3b)={', '.join(ltf_mumlar)or'Yok'}\n"
  f"Giriş/SL/TP: Giriş={_fmt_f(giris)} | SL={_fmt_f(sl)} ({stop_kaynak}) | TP1({RISK_ODUL_ORANI}R)={_fmt_f(tp1)} | TP2({NIHAI_TP_RR}R)={_fmt_f(tp2)} | Miktar={miktar} (Marjin:{marjin_u:.2f}$, 1R Risk:-{risk_u:.2f}$)\n"
  f"Denetim: {' | '.join(denetim_notlari)}"
 )
 return{'parite':O_str,'sembol':J,'piyasa':D,'yon':yon,'anlik':anlik_f,'skor':skor,'giris':giris,'sl':sl,'ilk_sl':ilk_sl,'tp1':tp1,'tp2':tp2,'miktar':miktar,'marjin_usdt':marjin_u,'risk_usdt':risk_u,'htf_periyot':htf_p,'mtf_periyot':mtf_p,'ltf_periyot':ltf_p,'safe_sayisi':safe_sayisi,'safe_puan':safe_puan,'safe_derece':safe_derece,'oncelik_etiket':oncelik_etiket,'bolge_kademesi':bolge_kademesi,'birincil_olcek_skoru':birincil_olcek_skoru,'birincil_olcek_carpani':birincil_olcek_carpani,'aktif_htf_bolgeler':aktif_htf_bolgeler,'aktif_birincil_bolgeler':aktif_birincil_bolgeler,'chk':chk,'ltf_kirilimlar':ltf_kirilimlar,'ltf_mumlar':ltf_mumlar,'stop_kaynak':stop_kaynak,'atli_puanlar':(p1,p2,p3,p4),'likidite_turu':v8.get('likidite_turu','-'),'sfp_durumu':v8.get('sfp_durumu','-'),'imbalance_tipi':v6.get('imbalance_tipi','-'),'bolge_10p':bolge_10p,'denetim_notlari':denetim_notlari,'onerilen_duzeltmeler':[],'giris_kurallari':giris_kurallari,'ozet':ozet_str,'tam_rapor_metni':tam_metin}

def aninda_islem_grafigi_uret(O,mod='temiz_mum',H_ozel=None,kaydet_png=True,ozel_tf=None,bar_sayisi=85,katmanlar=None):
 """Secili islem veya parite icin istenilen zaman dilimi, mum sayisi ve katmanlarla aninda grafik uretir."""
 O_str=str(O or'FUT:BTC/USDT')
 if':'not in O_str:
  O_str=f"FUT:{O_str}"if'/'in O_str else f"FUT:{O_str}/USDT"
 H=H_ozel if(I(H_ozel,dict)and H_ozel)else(analiz_hafizasi.get(O_str)or analiz_hafizasi.get(O_str.split(':',1)[-1])or{})
 dR=acik_islemler.get(O_str)if I(acik_islemler.get(O_str),dict)else None
 J=(dR.get('sembol')if I(dR,dict)else None)or H.get('sembol')or O_str.split(':',1)[-1]
 D=(dR.get('piyasa')if I(dR,dict)else None)or H.get('piyasa')or('spot'if O_str.startswith('SPOT:')else'future')
 htf_p,mtf_p,ltf_p,_=_parite_mtf_periyotlarini_bul(O_str,J,D,H)
 if not H or'df_15m'not in H:
  try:
   H=pine_icin_4h_1h_5m_veri_hazirla(J,D,H,O_str)
   analiz_hafizasi[O_str]=H
  except Exception:pass
 rontgen=islem_rontgeni_olustur(O_str,H,dR)
 fig=plt.figure(figsize=(10.2,6.1),dpi=130,facecolor='#0f172a')
 tbox=dict(boxstyle='round,pad=0.22',fc='#0f172a',ec='#334155',alpha=0.9,lw=0.8)
 ktm={'swing':False,'ob_fvg':False,'qml_fibo':False,'likidite':False,'islem':False}
 if I(katmanlar,dict):
  ktm.update(katmanlar)
 elif mod in('ltf_zoom','mtf_3lu','htf_bolge','likidite_denetim'):
  ktm={'swing':True,'ob_fvg':True,'qml_fibo':True,'likidite':True,'islem':True}
 elif mod=='sadece_likidite':
  ktm={'swing':True,'ob_fvg':False,'qml_fibo':False,'likidite':True,'islem':True}
 elif mod=='sadece_qml_ote':
  ktm={'swing':True,'ob_fvg':False,'qml_fibo':True,'likidite':False,'islem':True}
 elif mod=='sadece_ob_fvg':
  ktm={'swing':False,'ob_fvg':True,'qml_fibo':False,'likidite':False,'islem':True}
 elif mod=='temiz_mum':
  ktm={'swing':False,'ob_fvg':False,'qml_fibo':False,'likidite':False,'islem':False}
 def _tek_panel_detayli_ciz(ax,df_src,yapi_src,tf_etiket,n_bar=90,zoom_islem=True):
  ax.set_facecolor('#0f172a')
  ax.grid(True,ls=':',lw=0.65,color='#334155',alpha=0.6)
  ax.tick_params(colors='#cbd5e1',labelsize=8)
  for sp in ax.spines.values():sp.set_color('#334155')
  if df_src is None or L(df_src)<5:
   ax.set_title(f"{O_str} [{tf_etiket}] — Veri Bekleniyor",color='#f8fafc',fontsize=10,fontweight='bold')
   return
  oc=M(0,L(df_src)-int(n_bar))
  df=df_src.iloc[oc:].reset_index(drop=True)
  ct=L(df)
  lo_all,hi_all=(F(df['low'].min()),F(df['high'].max()))
  cf=M(hi_all-lo_all,hi_all*0.002)
  E_p=M(_f(df,'atr',-2)if'atr'in df.columns else cf*0.04,cf*0.008)
  uH,uL,kysy_m=kirilim_yoksa_swing_yoktur_analizi(df,n=2 if any(x in tf_etiket.lower()for x in('1m','3m','5m','15m'))else SWING_PENCERE)
  if ktm.get('swing',True):
   zz=sorted([(i,v,'H')for i,v in uH]+[(i,v,'L')for i,v in uL],key=lambda x:x[0])
   if L(zz)>=2:
    ax.plot([x[0]for x in zz],[x[1]for x in zz],color='#cbd5e1',lw=1.35,alpha=0.8,zorder=4)
   for eh_i,eh_v in kysy_m.get('elenen_highs',[])[-8:]:
    if 0<=eh_i<ct:ax.scatter([eh_i],[eh_v],color='#64748b',marker='x',s=26,zorder=5)
   for el_i,el_v in kysy_m.get('elenen_lows',[])[-8:]:
    if 0<=el_i<ct:ax.scatter([el_i],[el_v],color='#64748b',marker='x',s=26,zorder=5)
  bs_p=[{'orig_idx':b[2],'idx2':b[0],'yon':b[4],'tip':b[5]}for b in kysy_m.get('bos_list',[])[-10:]]
  qml_v=F(kysy_m.get('qml_seviyesi')or(yapi_src.get('qml_seviyesi')if I(yapi_src,dict)else 0.0)or 0.0)
  if ktm.get('ob_fvg',True):
   at_p,im_p=_arz_talep_ve_imbalance_sablon_hesapla(df,list(G(ct)),bs_p,E_p,qml_v if qml_v>0 else None)
   for z_at in at_p[-5:]:
    ns=M(0,N(ct-2,int(z_at['idx1'])))
    hp,iA=(F(z_at['lo']),F(z_at['hi']))
    mt_50=(hp+iA)/2.0
    gK='#10b981'if z_at['tur']=='TALEP'else'#ef4444'
    ax.add_patch(Rectangle((ns,hp),M(3,ct-ns+2),M(A(iA-hp),cf*0.004),facecolor=gK,edgecolor=gK,alpha=0.18,lw=1.1,zorder=2))
    ax.plot([ns,ct+1],[mt_50,mt_50],color=gK,ls=':',lw=0.9,alpha=0.85,zorder=3)
    ax.text(ct+0.8,mt_50,f"{_temiz_etiket_grafik(z_at['etiket'])} (%50 MT:{_fmt_f(mt_50)})",color=gK,fontsize=7.1,fontweight='bold',ha='right',va='center',bbox=tbox,zorder=8)
   for im_z in im_p[-5:]:
    ns=M(0,N(ct-2,int(im_z['idx1'])))
    hp,iA=(F(im_z['lo']),F(im_z['hi']))
    ce_50=(hp+iA)/2.0
    gK='#f59e0b'if'BISI'in im_z['tip']else'#a855f7'
    ax.add_patch(Rectangle((ns,hp),M(3,ct-ns+1),M(A(iA-hp),cf*0.003),facecolor=gK,edgecolor=gK,alpha=0.15,ls='--',lw=0.9,zorder=2))
    ax.plot([ns,ct],[ce_50,ce_50],color=gK,ls=':',lw=0.85,alpha=0.8,zorder=3)
    ax.text(ct-0.5,ce_50,f"{_temiz_etiket_grafik(im_z['etiket'])} (%50 CE:{_fmt_f(ce_50)})",color=gK,fontsize=6.8,fontweight='bold',ha='right',va='center',bbox=tbox,zorder=7)
  for bu,row in df.iterrows():
   ac,kp,yk,ds=_r(row,'open','close','high','low')
   qj=kp>=ac
   f8,gK=('#22c55e','#4ade80')if qj else('#ef4444','#f87171')
   ax.plot([bu,bu],[ds,yk],color=gK,lw=1.1,zorder=3)
   ax.add_patch(Rectangle((bu-0.34,N(ac,kp)),0.68,M(A(kp-ac),cf*0.0025),facecolor=f8,edgecolor=gK,lw=0.75,zorder=4))
  if ktm.get('qml_fibo',True):
   if qml_v>0 and lo_all-cf*0.3<=qml_v<=hi_all+cf*0.3:
    q_idx=M(0,N(ct-2,int(kysy_m.get('qml_idx')or 0)))
    ax.plot([q_idx,ct+1],[qml_v,qml_v],color='#ef4444',lw=1.8,ls='-',zorder=6)
    ax.text(ct+0.8,qml_v,f"[#1 QML] {_fmt_f(qml_v)}",color='#fde047',fontsize=7.5,fontweight='bold',ha='right',va='bottom',bbox=tbox,zorder=9)
   smax=F((yapi_src.get('swing_max')if I(yapi_src,dict)else 0.0)or hi_all)
   smin=F((yapi_src.get('swing_min')if I(yapi_src,dict)else 0.0)or lo_all)
   if smax>smin:
    du=smax-smin
    yon_b=(yapi_src.get('yon')if I(yapi_src,dict)else rontgen['yon'])=='BULLISH'
    ote_1=smax-du*0.618 if yon_b else smin+du*0.618
    ote_705=smax-du*0.705 if yon_b else smin+du*0.705
    ote_2=smax-du*0.786 if yon_b else smin+du*0.786
    eq_50=(smax+smin)/2.0
    ax.axhspan(N(ote_1,ote_2),M(ote_1,ote_2),color='#3b82f6',alpha=0.11,zorder=1)
    ax.axhline(eq_50,color='#64748b',ls='--',lw=0.85,alpha=0.75,zorder=2)
    ax.axhline(ote_705,color='#fde047',ls=':',lw=1.0,alpha=0.8,zorder=3)
    ax.text(0.5,ote_705,f"OTE 0.705 ({_fmt_f(ote_705)})",color='#fde047',fontsize=7.0,fontweight='bold',ha='left',va='center',bbox=tbox,zorder=8)
  if ktm.get('likidite',True):
   lq_l,sfp_l,_=_likidite_ve_sfp_yapilarini_bul(df,uH,uL)
   for lq in lq_l[-6:]:
    i1,i2,p1_l,p2_l,rk_l=(int(lq['idx1']),int(lq['idx2']),F(lq['p1']),F(lq['p2']),lq.get('renk','#fbbf24'))
    stil='--'if'Trendline'in lq['tip']else('-.'if'IDM'in lq['tip']else':')
    ax.plot([i1,i2],[p1_l,p2_l],color=rk_l,ls=stil,lw=1.45,alpha=0.9,zorder=6)
    ax.text(i2,(p1_l+p2_l)/2.0,f" {_temiz_etiket_grafik(lq['tip'])}",color=rk_l,fontsize=7.0,fontweight='bold',ha='right',va='bottom',bbox=tbox,zorder=8)
   for sf in sfp_l[-4:]:
    kT,sp_f,s_yon=(int(sf['idx']),F(sf['price']),sf.get('yon','BULL'))
    col_s='#f43f5e'if s_yon=='BEAR'else'#10b981'
    ax.scatter([kT],[sp_f],color=col_s,s=65,marker='*',zorder=9)
    ax.text(kT,sp_f+(cf*0.025 if s_yon=='BEAR'else-cf*0.025),_temiz_etiket_grafik(sf.get('tip','SFP')),color=col_s,fontsize=7.2,fontweight='bold',ha='center',bbox=tbox,zorder=9)
  g_f,sl_f,tp1_f,tp2_f=(rontgen['giris'],rontgen['sl'],rontgen['tp1'],rontgen['tp2'])
  if ktm.get('islem',True)and zoom_islem and g_f>0 and sl_f>0:
   oJ=M(0,ct-18)
   ax.add_patch(Rectangle((oJ,N(g_f,sl_f)),ct-oJ+2,A(g_f-sl_f),facecolor='#ef4444',alpha=0.14,zorder=2))
   if tp1_f>0:
    ax.add_patch(Rectangle((oJ,N(g_f,tp1_f)),ct-oJ+2,A(tp1_f-g_f),facecolor='#10b981',alpha=0.12,zorder=2))
   ax.axhline(g_f,color='#38bdf8',ls='--',lw=1.7,zorder=7)
   ax.axhline(sl_f,color='#ef4444',ls='-',lw=1.8,zorder=7)
   if tp1_f>0:ax.axhline(tp1_f,color='#10b981',ls='-',lw=1.7,zorder=7)
   if tp2_f>0:ax.axhline(tp2_f,color='#a3e635',ls=':',lw=1.5,zorder=7)
   tetik_kisa='+'.join((rontgen['ltf_kirilimlar'][:1]+rontgen['ltf_mumlar'][:1]))or rontgen['oncelik_etiket']
   ax.scatter([ct-1],[g_f],color='#38bdf8',edgecolors='#ffffff',s=80,zorder=10)
   ax.annotate(
    _temiz_etiket_grafik(f"[{rontgen['yon']} GİRİŞ: {_fmt_f(g_f)}]\n{rontgen['oncelik_etiket']} ({rontgen['safe_sayisi']}/8 Safe)\nTetik: {tetik_kisa[:36]}"),
    xy=(ct-1,g_f),xytext=(M(2,ct-34),g_f),
    color='#7dd3fc',fontsize=7.4,fontweight='bold',
    arrowprops=dict(arrowstyle='->',color='#38bdf8',lw=1.5),
    bbox=dict(boxstyle='round,pad=0.26',fc='#0f172a',ec='#38bdf8',lw=1.2),zorder=11
   )
   ax.text(0.8,sl_f,_temiz_etiket_grafik(f"[STOP 1R: {_fmt_f(sl_f)}] (-{rontgen['risk_usdt']:.2f}$ | {rontgen['stop_kaynak'][:34]})"),color='#fca5a5',fontsize=7.2,fontweight='bold',ha='left',va='center',bbox=tbox,zorder=10)
   if tp1_f>0:
    ax.text(0.8,tp1_f,f"[TP1 {RISK_ODUL_ORANI}R: {_fmt_f(tp1_f)}] (%50 Kâr Al + BE)",color='#6ee7b7',fontsize=7.2,fontweight='bold',ha='left',va='center',bbox=tbox,zorder=10)
   if tp2_f>0:
    ax.text(0.8,tp2_f,f"[TP2 {NIHAI_TP_RR}R: {_fmt_f(tp2_f)}]",color='#bef264',fontsize=7.1,fontweight='bold',ha='left',va='center',bbox=tbox,zorder=10)
  ax.set_title(
   _temiz_etiket_grafik(f"{O_str} [{tf_etiket}] — Yön: {rontgen['yon']} | Skor: {rontgen['skor']}/100 | {rontgen['safe_derece']} | Öncelik: {rontgen['oncelik_etiket']}"),
   color='#f8fafc',fontsize=9.6,fontweight='bold',pad=8,loc='left'
  )
  ax.set_xlim(-1,ct+3)
 n_b=int(bar_sayisi)if bar_sayisi and int(bar_sayisi)>=20 else 85
 if ozel_tf and ozel_tf in TUM_ZAMAN_DILIMLERI:
  try:
   pk_oz=tek_tf_canli_pa_analizi(J,ozel_tf,D,H.get('ana_yon'),limit=M(110,n_b+20))
   ax=fig.add_subplot(111)
   _tek_panel_detayli_ciz(ax,pk_oz['df_full'],pk_oz['yapi'],f"ÖZEL PERİYOT ({ozel_tf.upper()})",n_bar=n_b,zoom_islem=True)
  except Exception:
   ax=fig.add_subplot(111)
   _tek_panel_detayli_ciz(ax,H.get('df_15m_full',H.get('df_15m')),H.get('yapi_15m',{}),f"LTF ({ltf_p})",n_bar=n_b,zoom_islem=True)
 elif mod=='mtf_3lu':
  gs=GridSpec(3,1,height_ratios=[1,1,1.15],hspace=0.28,figure=fig)
  _tek_panel_detayli_ciz(fig.add_subplot(gs[0]),H.get('df_4h_full',H.get('df_15m')),H.get('yapi_4h',{}),f"HTF {htf_p.upper()}",n_bar=n_b,zoom_islem=False)
  _tek_panel_detayli_ciz(fig.add_subplot(gs[1]),H.get('df_1h_full',H.get('df_15m')),H.get('yapi_1h',{}),f"MTF {mtf_p.upper()}",n_bar=n_b,zoom_islem=True)
  _tek_panel_detayli_ciz(fig.add_subplot(gs[2]),H.get('df_15m_full',H.get('df_15m')),H.get('yapi_15m',{}),f"LTF {ltf_p}",n_bar=n_b,zoom_islem=True)
 elif mod in('htf_bolge','sadece_qml_ote'):
  ax=fig.add_subplot(111)
  _tek_panel_detayli_ciz(ax,H.get('df_4h_full',H.get('df_15m')),H.get('yapi_4h',{}),f"HTF 8 SAFE BÖLGE & QML/OTE ({htf_p.upper()})",n_bar=M(110,n_b),zoom_islem=True)
 elif mod in('likidite_denetim','sadece_likidite','sadece_ob_fvg','temiz_mum'):
  ax=fig.add_subplot(111)
  _tek_panel_detayli_ciz(ax,H.get('df_15m_full',H.get('df_15m')),H.get('yapi_15m',{}),f"ÖZEL KATMAN GRAFİĞİ ({ltf_p} | {mod.upper()})",n_bar=M(95,n_b),zoom_islem=True)
 else:
  gs=GridSpec(2,1,height_ratios=[3.2,1.0],hspace=0.18,figure=fig)
  ax_m=fig.add_subplot(gs[0])
  ax_i=fig.add_subplot(gs[1])
  df_l=H.get('df_15m_full',H.get('df_15m'))
  _tek_panel_detayli_ciz(ax_m,df_l,H.get('yapi_15m',{}),f"LTF GİRİŞ, TETİK MUMU & SL/TP RÖNTGENİ ({ltf_p})",n_bar=n_b,zoom_islem=True)
  if df_l is not None and L(df_l)>=5 and'rsi'in df_l.columns:
   oc_i=M(0,L(df_l)-n_b)
   df_sub=df_l.iloc[oc_i:].reset_index(drop=True)
   ax_i.set_facecolor('#0f172a')
   pF=np.arange(L(df_sub))
   ln=df_sub['rsi'].astype(F).values
   ax_i.plot(pF,ln,color='#a78bfa',lw=1.4,label='RSI(14)')
   ax_i.axhline(70,color='#f87171',ls=':',lw=0.8)
   ax_i.axhline(50,color='#64748b',ls='--',lw=0.8)
   ax_i.axhline(30,color='#4ade80',ls=':',lw=0.8)
   ax_i.set_xlim(-1,L(df_sub)+3)
   ax_i.set_ylim(15,85)
   ax_i.tick_params(colors='#94a3b8',labelsize=7.5)
   ax_i.grid(True,ls=':',alpha=0.25,color='#334155')
   ax_i.set_title(f"DVG & Osilatör Kontrolü (RSI Kapanış: {ln[-1]:.1f} | AO İğne: {_f(df_sub,'ao',-1):+.4f} | CVD: {_f(df_sub,'cvd',-1):+.1f})",color='#cbd5e1',fontsize=8.2,fontweight='bold')
 fig.subplots_adjust(left=0.06,right=0.97,top=0.93,bottom=0.07)
 dosya_png=''
 b64_png=''
 try:
  buf=_io.BytesIO()
  fig.savefig(buf,format='png',dpi=130,bbox_inches='tight',facecolor='#0f172a')
  buf.seek(0)
  b64_png=_b64.b64encode(buf.read()).decode('utf-8')
  if kaydet_png:
   hedef_klasor=ANDROID_VERI_DIZINI if'ANDROID_VERI_DIZINI'in globals()else'.'
   dosya_png=os.path.abspath(os.path.join(hedef_klasor,f"islem_rontgen_{O_str.replace(':','_').replace('/','_')}_{mod}.png"))
   with open(dosya_png,'wb')as fp_out:
    fp_out.write(_b64.b64decode(b64_png))
 except Exception:pass
 return(fig,dosya_png,b64_png,rontgen)

def _metinden_sembol_cikar(metin,varsayilan_o=None):
 """Kullanicinin mesajinda gecen coin adini (orn. ETH, SOL, AVAX, PEPE, XRP) tespit eder."""
 if not metin:return varsayilan_o
 m_up=str(metin).upper()
 m_pair=re.search(r'([A-Z0-9]{2,10})\s*/\s*USDT',m_up)
 if m_pair:
  on='SPOT:'if'SPOT'in m_up else'FUT:'
  return f"{on}{m_pair.group(1)}/USDT"
 bilinen_coinler=['BTC','ETH','SOL','BNB','XRP','DOGE','ADA','AVAX','LINK','DOT','MATIC','ARB','OP','SUI','APT','NEAR','LTC','BCH','ATOM','UNI','PEPE','SHIB','WIF','BONK','FET','RENDER','INJ','TIA','SEI','TRX','TON','AAVE','FIL','ETC','STX','IMX','GALA','SAND','MANA','AXS','CRV','LDO','RUNE','ENS','ORDI','JUP','ENA','WLD','PENDLE','ONDO']
 for k_a in list(acik_islemler.keys())+list(analiz_hafizasi.keys()):
  if':'in str(k_a):
   c_ad=str(k_a).split(':',1)[-1].split('/')[0].upper()
   if c_ad not in bilinen_coinler:bilinen_coinler.append(c_ad)
 for c in bilinen_coinler:
  if re.search(rf'{c}',m_up):
   on='SPOT:'if'SPOT'in m_up else(varsayilan_o.split(':',1)[0]+':'if':'in str(varsayilan_o)else'FUT:')
   return f"{on}{c}/USDT"
 return varsayilan_o

def gemini_komut_ve_hata_duzeltici(metin,O_secili=None,gui_ref=None):
 """Hem dogal dil emirlerini hem de yapay zekanin dondurdugu <AJAN_KOMUTU>{...}</AJAN_KOMUTU> veya <DUZELTME_KOMUTU>{...}</DUZELTME_KOMUTU> aksiyonlarini bota uygular."""
 global STOP_BELIRLEME_MODU,KYSY_HTF_ATR_CARPANI,KYSY_LTF_ATR_CARPANI,EQH_EQL_TOL_ATR,SFP_MIN_IGNE_ATR,IKINCIL_BOLGE_GIRIS_AKTIF,MIN_CONFLUENCE_SKORU,KALDIRAC,ISLEM_BASI_RISK_USDT,MAKS_MARJIN_USDT,RISK_ODUL_ORANI,NIHAI_TP_RR,ISLEM_TARZI_MODU,BIRINCIL_BOLGE_OLCEK_CARPANI
 if not metin:return(False,'',None)
 m_str=str(metin)
 m_low=m_str.lower()
 uygulanan=[]
 cizim_istegi=None
 hedef_o=_metinden_sembol_cikar(m_str,str(O_secili or'FUT:BTC/USDT'))
 dR=acik_islemler.get(hedef_o)if I(acik_islemler.get(hedef_o),dict)else(acik_islemler.get(str(O_secili))if I(acik_islemler.get(str(O_secili)),dict)else None)
 H=analiz_hafizasi.get(hedef_o)or analiz_hafizasi.get(str(O_secili))or{}
 for tag_rx in(r'<AJAN_KOMUTU>(.*?)</AJAN_KOMUTU>',r'<DUZELTME_KOMUTU>(.*?)</DUZELTME_KOMUTU>'):
  for m_js in re.finditer(tag_rx,m_str,re.DOTALL):
   try:
    cmd_d=json.loads(m_js.group(1).strip())
    if not I(cmd_d,dict):continue
    aks=str(cmd_d.get('aksiyon','')).lower()
    if cmd_d.get('parite'):
     hedef_o=_metinden_sembol_cikar(str(cmd_d['parite']),hedef_o)
     dR=acik_islemler.get(hedef_o)if I(acik_islemler.get(hedef_o),dict)else dR
    if aks=='grafik_ciz'or'cizim_modu'in cmd_d:
     cizim_istegi={'parite':hedef_o,'mod':str(cmd_d.get('cizim_modu')or cmd_d.get('mod')or'ltf_zoom'),'tf':cmd_d.get('periyot')or cmd_d.get('tf'),'bar':cmd_d.get('bar_sayisi')or cmd_d.get('mum_sayisi'),'ayri_pencere':bool(cmd_d.get('ayri_pencere',False))}
     uygulanan.append(f"📊 {hedef_o} grafiği ({cizim_istegi['mod']}) çizildi.")
    if aks=='ayri_sohbet_ac'or cmd_d.get('ayri_sohbet_penceresi'):
     if gui_ref and hasattr(gui_ref,'bagimsiz_ai_sohbet_penceresi_ac'):
      gui_ref.after(20,lambda h_o=hedef_o:gui_ref.bagimsiz_ai_sohbet_penceresi_ac(h_o))
      uygulanan.append("🗗 Konuşma bağımsız ayrı pencerede açıldı.")
    if aks=='tradingview_ac':
     if gui_ref:
      gui_ref.after(20,lambda h_o=hedef_o:tradingview_kopyala_yapistirsiz_html_ac(h_o,'5m'))
      uygulanan.append(f"🌐 {hedef_o} Canlı TradingView grafiği tarayıcıda açıldı.")
    if aks=='bot_baslat'and gui_ref and hasattr(gui_ref,'botu_baslat'):
     gui_ref.after(10,gui_ref.botu_baslat)
     uygulanan.append("▶️ Bot taraması başlatıldı.")
    if aks=='bot_durdur'and gui_ref and hasattr(gui_ref,'botu_durdur'):
     gui_ref.after(10,gui_ref.botu_durdur)
     uygulanan.append("⏹️ Bot taraması durduruldu.")
    if aks=='islem_kapat'and gui_ref:
     if cmd_d.get('tumu'):
      for k_ac in[k for k,v in acik_islemler.items()if I(v,dict)]:
       threading.Thread(target=gui_ref._poz_kapat,args=(k_ac,'AI AJAN KOMUTUYLA KAPATILDI'),daemon=True).start()
      uygulanan.append("🚨 Tüm açık işlemler kapatıldı.")
     elif I(acik_islemler.get(hedef_o),dict):
      threading.Thread(target=gui_ref._poz_kapat,args=(hedef_o,'AI AJAN KOMUTUYLA KAPATILDI'),daemon=True).start()
      uygulanan.append(f"🚨 {hedef_o} açık işlemi kapatıldı.")
    if'stop_modu'in cmd_d and cmd_d['stop_modu']:
     STOP_BELIRLEME_MODU=str(cmd_d['stop_modu'])
     uygulanan.append(f"🛡️ Stop Belirleme Modu -> '{STOP_BELIRLEME_MODU}' yapıldı.")
    if'yeni_sl'in cmd_d and I(dR,dict)and F(cmd_d['yeni_sl'])>0:
     dR['sl']=R(F(cmd_d['yeni_sl']),6)
     uygulanan.append(f"🛡️ {hedef_o} Stop-Loss -> {dR['sl']} yapıldı.")
    if'yeni_tp'in cmd_d and I(dR,dict)and F(cmd_d['yeni_tp'])>0:
     dR['tp']=R(F(cmd_d['yeni_tp']),6)
     uygulanan.append(f"🎯 {hedef_o} TP1 -> {dR['tp']} yapıldı.")
    if'kaldirac'in cmd_d and F(cmd_d['kaldirac'])>=1:
     KALDIRAC=M(1,N(125,int(F(cmd_d['kaldirac']))))
     if gui_ref and hasattr(gui_ref,'ent_kaldirac'):
      gui_ref.ent_kaldirac.delete(0,'end');gui_ref.ent_kaldirac.insert(0,str(KALDIRAC))
     uygulanan.append(f"⚙️ Kaldıraç -> {KALDIRAC}x yapıldı.")
    if'risk_usdt'in cmd_d and F(cmd_d['risk_usdt'])>0:
     ISLEM_BASI_RISK_USDT=M(0.1,F(cmd_d['risk_usdt']))
     if gui_ref and hasattr(gui_ref,'ent_risk'):
      gui_ref.ent_risk.delete(0,'end');gui_ref.ent_risk.insert(0,str(ISLEM_BASI_RISK_USDT))
     uygulanan.append(f"💰 İşlem Başı Risk -> {ISLEM_BASI_RISK_USDT}$ (1R) yapıldı.")
    if'marjin_usdt'in cmd_d and F(cmd_d['marjin_usdt'])>=5:
     MAKS_MARJIN_USDT=F(cmd_d['marjin_usdt'])
     if gui_ref and hasattr(gui_ref,'ent_marjin'):
      gui_ref.ent_marjin.delete(0,'end');gui_ref.ent_marjin.insert(0,str(MAKS_MARJIN_USDT))
     uygulanan.append(f"💵 Maks Marjin -> {MAKS_MARJIN_USDT}$ yapıldı.")
    if'rr'in cmd_d and F(cmd_d['rr'])>=0.5:
     RISK_ODUL_ORANI=F(cmd_d['rr'])
     if gui_ref and hasattr(gui_ref,'ent_rr'):
      gui_ref.ent_rr.delete(0,'end');gui_ref.ent_rr.insert(0,str(RISK_ODUL_ORANI))
     uygulanan.append(f"🎯 Risk/Ödül (TP1) -> {RISK_ODUL_ORANI}R yapıldı.")
    if'min_skor'in cmd_d and F(cmd_d['min_skor'])>=10:
     MIN_CONFLUENCE_SKORU=M(10,N(100,int(F(cmd_d['min_skor']))))
     if gui_ref and hasattr(gui_ref,'ent_skor'):
      gui_ref.ent_skor.delete(0,'end');gui_ref.ent_skor.insert(0,str(MIN_CONFLUENCE_SKORU))
     uygulanan.append(f"🔥 Min Confluence Skoru -> {MIN_CONFLUENCE_SKORU} yapıldı.")
    if'eqh_tol_atr'in cmd_d and F(cmd_d['eqh_tol_atr'])>0:
     EQH_EQL_TOL_ATR=M(0.08,N(1.2,F(cmd_d['eqh_tol_atr'])))
     uygulanan.append(f"💧 EQH/EQL Toleransı -> {EQH_EQL_TOL_ATR:.2f}x ATR yapıldı.")
    if'sfp_min_atr'in cmd_d and F(cmd_d['sfp_min_atr'])>0:
     SFP_MIN_IGNE_ATR=M(0.03,N(0.8,F(cmd_d['sfp_min_atr'])))
     uygulanan.append(f"💧 SFP Min İğne Boyu -> {SFP_MIN_IGNE_ATR:.2f}x ATR yapıldı.")
    if'kysy_htf_atr'in cmd_d and F(cmd_d['kysy_htf_atr'])>0:
     KYSY_HTF_ATR_CARPANI=M(0.6,N(4.0,F(cmd_d['kysy_htf_atr'])))
     uygulanan.append(f"📐 KYSY Swing ATR Çarpanı -> {KYSY_HTF_ATR_CARPANI:.2f}x ATR yapıldı.")
    if'birincil_olcek_carpani'in cmd_d and F(cmd_d['birincil_olcek_carpani'])>0:
     BIRINCIL_BOLGE_OLCEK_CARPANI=M(1.5,N(10.0,F(cmd_d['birincil_olcek_carpani'])))
     uygulanan.append(f"🚀 1.Öncelik (Arz/Talep, OB, OTE, QML) Ölçek Çarpanı -> {BIRINCIL_BOLGE_OLCEK_CARPANI:.1f}x yapıldı.")
   except Exception:pass
 if any(k in m_low for k in('ayrı pencere','ayri pencere','yeni pencere','konuşmayı ayır','sohbeti ayır','bağımsız pencere')):
  if'grafik'in m_low and'sohbet'not in m_low and'konuşma'not in m_low:
   cizim_istegi={'parite':hedef_o,'mod':'ltf_zoom','ayri_pencere':True}
   uygulanan.append(f"📈 {hedef_o} grafiği ayrı pencerede açıldı.")
  elif gui_ref and hasattr(gui_ref,'bagimsiz_ai_sohbet_penceresi_ac'):
   gui_ref.after(20,lambda h_o=hedef_o:gui_ref.bagimsiz_ai_sohbet_penceresi_ac(h_o))
   uygulanan.append("🗗 Konuşma bağımsız ayrı pencerede açıldı.")
 m_tf_ozel=re.search(r'(1m|3m|5m|15m|30m|1h|2h|4h|6h|12h|1d|1M)',m_str)
 m_bar_say=re.search(r'(\d{2,3})\s*mum',m_low)
 bar_s=int(m_bar_say.group(1))if m_bar_say else None
 tf_s=m_tf_ozel.group(1)if(m_tf_ozel and any(k in m_low for k in('çiz','göster','grafik','bak','aç')))else None
 if any(k in m_low for k in("tradingview'da aç",'tradingview aç',"tv'de aç",'tarayıcıda aç')):
  if gui_ref:
   gui_ref.after(20,lambda h_o=hedef_o,t_s=tf_s or'5m':tradingview_kopyala_yapistirsiz_html_ac(h_o,t_s))
  uygulanan.append(f"🌐 {hedef_o} Canlı TradingView grafiği tarayıcıda açıldı.")
 elif any(k in m_low for k in('sadece likidite','yalnızca likidite')):
  cizim_istegi={'parite':hedef_o,'mod':'sadece_likidite','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in('sadece qml','sadece fibo','sadece ote')):
  cizim_istegi={'parite':hedef_o,'mod':'sadece_qml_ote','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in('sadece ob','sadece fvg','sadece arz','sadece kutu')):
  cizim_istegi={'parite':hedef_o,'mod':'sadece_ob_fvg','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in('sadece mum','temiz grafik','çizimsiz')):
  cizim_istegi={'parite':hedef_o,'mod':'temiz_mum','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in("3'lü",'3lu','üçlü','mtf çiz','tüm zaman')):
  cizim_istegi={'parite':hedef_o,'mod':'mtf_3lu','tf':None,'bar':bar_s}
 elif any(k in m_low for k in('htf çiz','htf bölge','8 bölge','qml çiz','fibo çiz')):
  cizim_istegi={'parite':hedef_o,'mod':'htf_bolge','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in('likidite çiz','idm çiz','eqh','eql','sfp çiz','likidite göster')):
  cizim_istegi={'parite':hedef_o,'mod':'likidite_denetim','tf':tf_s,'bar':bar_s}
 elif any(k in m_low for k in('grafik çiz','grafiğini çiz','grafikte göster','giriş yerini göster','grafik aç','çiz','zoom')):
  cizim_istegi={'parite':hedef_o,'mod':'ltf_zoom','tf':tf_s,'bar':bar_s}
 if any(k in m_low for k in('botu başlat','taramayı başlat','bot çalışsın'))and gui_ref and hasattr(gui_ref,'botu_baslat'):
  gui_ref.after(10,gui_ref.botu_baslat)
  uygulanan.append("▶️ Bot taraması başlatıldı.")
 elif any(k in m_low for k in('botu durdur','taramayı durdur','bot dursun'))and gui_ref and hasattr(gui_ref,'botu_durdur'):
  gui_ref.after(10,gui_ref.botu_durdur)
  uygulanan.append("⏹️ Bot taraması durduruldu.")
 if any(k in m_low for k in('tüm işlemleri kapat','hepsini kapat','bütün işlemleri kapat'))and gui_ref:
  acik_k_list=[k for k,v in acik_islemler.items()if I(v,dict)]
  for k_ac in acik_k_list:
   threading.Thread(target=gui_ref._poz_kapat,args=(k_ac,'AI KOMUTUYLA KAPATILDI'),daemon=True).start()
  if acik_k_list:uygulanan.append(f"🚨 Açık olan {L(acik_k_list)} işlemin tamamı kapatılıyor.")
 elif any(k in m_low for k in('işlemi kapat','pozisyonu kapat','bu işlemi kapat'))and gui_ref and I(dR,dict):
  threading.Thread(target=gui_ref._poz_kapat,args=(hedef_o,'AI KOMUTUYLA KAPATILDI'),daemon=True).start()
  uygulanan.append(f"🚨 {hedef_o} açık pozisyonu kapatılıyor.")
 if any(k in m_low for k in('stopu htf','htf stop','htf yapıya göre stop')):
  STOP_BELIRLEME_MODU='HTF Yapıya Göre (Dip/Tepe & OB)'
  if gui_ref and hasattr(gui_ref,'cmb_stop_modu'):gui_ref.cmb_stop_modu.set(STOP_BELIRLEME_MODU)
  if I(H,dict)and H.get('giris'):
   y_sl,y_ack=stop_noktasi_belirle(H.get('df_4h'),H.get('df_1h'),H.get('df_15m'),H.get('yapi_4h',{}),H.get('yapi_1h',{}),H.get('yapi_15m',{}),H.get('konum_meta',{}),F(H['giris']),H.get('ana_yon','BULLISH'),None,None,None,H.get('sl'),STOP_BELIRLEME_MODU)
   H['sl']=y_sl
   if I(dR,dict):dR['sl']=y_sl
  uygulanan.append("🛡️ Stop-Loss modu 'HTF Yapıya Göre (Dip/Tepe & OB)' olarak değiştirildi ve yeni SL uygulandı.")
 elif any(k in m_low for k in('stopu ltf','ltf stop','dar stop','ltf yapıya göre stop')):
  STOP_BELIRLEME_MODU='LTF Yapıya Göre (Kırılım/Mum & POI)'
  if gui_ref and hasattr(gui_ref,'cmb_stop_modu'):gui_ref.cmb_stop_modu.set(STOP_BELIRLEME_MODU)
  if I(H,dict)and H.get('giris'):
   y_sl,y_ack=stop_noktasi_belirle(H.get('df_4h'),H.get('df_1h'),H.get('df_15m'),H.get('yapi_4h',{}),H.get('yapi_1h',{}),H.get('yapi_15m',{}),H.get('konum_meta',{}),F(H['giris']),H.get('ana_yon','BULLISH'),None,None,None,H.get('sl'),STOP_BELIRLEME_MODU)
   H['sl']=y_sl
   if I(dR,dict):dR['sl']=y_sl
  uygulanan.append("🛡️ Stop-Loss modu 'LTF Yapıya Göre (Kırılım/Mum & POI)' olarak değiştirildi ve dar SL uygulandı.")
 elif any(k in m_low for k in('stopu girişe çek','break-even yap','breakeven yap','stopu be yap','0 risk yap'))and I(dR,dict):
  dR['sl']=F(dR['giris'])
  dR['risk_usdt']=0.0
  uygulanan.append(f"🛡️ {hedef_o} Stop-Loss seviyesi Giriş Fiyatına ({dR['sl']} — Break-Even / 0 Risk) çekildi!")
 m_sl_fiyat=re.search(r"stop(?:u|unu|loss)?\s*(?:fiyatını\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:yap|çek|ayarla|olsun|'e|'a|e|a)",m_low)
 if m_sl_fiyat and I(dR,dict):
  y_f=F(m_sl_fiyat.group(1))
  if y_f>0:
   dR['sl']=R(y_f,6)
   uygulanan.append(f"🛡️ {hedef_o} Stop-Loss fiyatı {dR['sl']} seviyesine güncellendi.")
 m_tp_fiyat=re.search(r"(?:tp1?|hedef)(?:'i|i|yi|ini)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:yap|çek|ayarla|olsun|'e|'a|e|a)",m_low)
 if m_tp_fiyat and I(dR,dict):
  y_f=F(m_tp_fiyat.group(1))
  if y_f>0:
   dR['tp']=R(y_f,6)
   uygulanan.append(f"🎯 {hedef_o} TP1 hedef fiyatı {dR['tp']} seviyesine güncellendi.")
 m_kald=re.search(r'kaldıra(?:ç|c|cı)\s*([0-9]{1,3})x?\s*(?:yap|olsun|ayarla)?',m_low)
 if m_kald:
  KALDIRAC=M(1,N(125,int(m_kald.group(1))))
  if gui_ref and hasattr(gui_ref,'ent_kaldirac'):
   gui_ref.ent_kaldirac.delete(0,'end');gui_ref.ent_kaldirac.insert(0,str(KALDIRAC))
  uygulanan.append(f"⚙️ Kaldıraç -> {KALDIRAC}x olarak ayarlandı.")
 m_risk_d=re.search(r'(?:işlem başı risk|risk(?:i|ini)?)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:\$|dolar|usdt)?\s*(?:yap|olsun|ayarla)',m_low)
 if m_risk_d:
  ISLEM_BASI_RISK_USDT=M(0.1,F(m_risk_d.group(1)))
  if gui_ref and hasattr(gui_ref,'ent_risk'):
   gui_ref.ent_risk.delete(0,'end');gui_ref.ent_risk.insert(0,str(ISLEM_BASI_RISK_USDT))
  uygulanan.append(f"💰 İşlem Başı Risk (1R) -> {ISLEM_BASI_RISK_USDT:.2f} USDT yapıldı.")
 m_marj_d=re.search(r'marjin(?:i|ini)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:\$|dolar|usdt)?\s*(?:yap|olsun|ayarla)',m_low)
 if m_marj_d:
  MAKS_MARJIN_USDT=M(5.0,F(m_marj_d.group(1)))
  if gui_ref and hasattr(gui_ref,'ent_marjin'):
   gui_ref.ent_marjin.delete(0,'end');gui_ref.ent_marjin.insert(0,str(MAKS_MARJIN_USDT))
  uygulanan.append(f"💵 Maksimum Marjin -> {MAKS_MARJIN_USDT:.2f} USDT yapıldı.")
 m_rr_d=re.search(r'(?:rr|risk ödül)\s*(?:oranını\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:r)?\s*(?:yap|olsun|ayarla)',m_low)
 if m_rr_d:
  RISK_ODUL_ORANI=M(0.5,F(m_rr_d.group(1)))
  NIHAI_TP_RR=M(NIHAI_TP_RR,RISK_ODUL_ORANI+1.0)
  if gui_ref and hasattr(gui_ref,'ent_rr'):
   gui_ref.ent_rr.delete(0,'end');gui_ref.ent_rr.insert(0,str(RISK_ODUL_ORANI))
  uygulanan.append(f"🎯 TP1 Risk/Ödül Oranı -> {RISK_ODUL_ORANI}R (TP2: {NIHAI_TP_RR}R) yapıldı.")
 m_eqh=re.search(r'(?:eqh|eql|eş tepe|likidite tolerans)[a-zğüşıöç\s]*([0-9]+\.[0-9]+)',m_low)
 if m_eqh:
  EQH_EQL_TOL_ATR=M(0.08,N(1.2,F(m_eqh.group(1))))
  uygulanan.append(f"💧 EQH/EQL Eş Tepe/Dip ATR Toleransı -> {EQH_EQL_TOL_ATR:.2f}x ATR yapıldı.")
 m_sfp=re.search(r'(?:sfp|iğne)[a-zğüşıöç\s]*([0-9]+\.[0-9]+)',m_low)
 if m_sfp:
  SFP_MIN_IGNE_ATR=M(0.03,N(0.8,F(m_sfp.group(1))))
  uygulanan.append(f"💧 SFP Minimum İğne Taşması -> {SFP_MIN_IGNE_ATR:.2f}x ATR yapıldı.")
 m_kysy=re.search(r'(?:kysy|swing atr|salınım)[a-zğüşıöç\s]*([0-9]+\.[0-9]+)',m_low)
 if m_kysy:
  KYSY_HTF_ATR_CARPANI=M(0.6,N(4.0,F(m_kysy.group(1))))
  uygulanan.append(f"📐 KYSY HTF Swing ATR Çarpanı -> {KYSY_HTF_ATR_CARPANI:.2f}x ATR yapıldı.")
 m_olcek=re.search(r'(?:öncelik ölçek|ölçek çarpanı|1\.?\s*öncelik)[a-zğüşıöç\s]*([0-9]+(?:\.[0-9]+)?)',m_low)
 if m_olcek:
  BIRINCIL_BOLGE_OLCEK_CARPANI=M(1.5,N(10.0,F(m_olcek.group(1))))
  uygulanan.append(f"🚀 1.Öncelik (Arz/Talep, OB, OTE, QML) Ölçek Çarpanı -> {BIRINCIL_BOLGE_OLCEK_CARPANI:.1f}x yapıldı.")
 m_skor=re.search(r'(?:min skor|minimum skor|eşik skor)[a-zğüşıöç\s]*([0-9]{2})',m_low)
 if m_skor:
  MIN_CONFLUENCE_SKORU=M(10,N(100,int(m_skor.group(1))))
  if gui_ref and hasattr(gui_ref,'ent_skor'):
   gui_ref.ent_skor.delete(0,'end');gui_ref.ent_skor.insert(0,str(MIN_CONFLUENCE_SKORU))
  uygulanan.append(f"🔥 Minimum Confluence Giriş Skoru -> {MIN_CONFLUENCE_SKORU}/100 yapıldı.")
 if'scalp'in m_low and any(k in m_low for k in('geç','yap','mod','aç')):
  if gui_ref and hasattr(gui_ref,'islem_modu_degisti'):gui_ref.islem_modu_degisti('Scalp')
  else:mtf_sablonu_uygula('15m / 5m / 1m (Scalp)')
  uygulanan.append("⚡ İşlem Modu -> SCALP (15m / 5m / 1m | TP1: 1.5R / TP2: 2.5R) olarak değiştirildi.")
 elif('daytrade'in m_low or'swing'in m_low)and any(k in m_low for k in('geç','yap','mod')):
  if gui_ref and hasattr(gui_ref,'islem_modu_degisti'):gui_ref.islem_modu_degisti('DayTrade')
  else:mtf_sablonu_uygula('4h / 1h / 15m (Swing)')
  uygulanan.append("🏛️ İşlem Modu -> DAYTRADE / SWING (4h / 1h / 15m | TP1: 3R / TP2: 4R) olarak değiştirildi.")
 if'2. kademe'in m_low and('kapat'in m_low or'iptal'in m_low or'sadece 1'in m_low):
  IKINCIL_BOLGE_GIRIS_AKTIF=False
  uygulanan.append("🔒 2. Kademe HTF Bölgeleri (BOS/CHoCH/ITZ/Magic) kapatıldı; bot artık SADECE 1. Kademe (Arz/Talep, OB, OTE, QML) bölgelerde işleme girecek.")
 elif'2. kademe'in m_low and('aç'in m_low or'aktif'in m_low):
  IKINCIL_BOLGE_GIRIS_AKTIF=True
  uygulanan.append("🔓 2. Kademe HTF Bölgeleri (BOS/CHoCH/ITZ/Magic) yedek tarama için tekrar aktif edildi.")
 if hedef_o!=str(O_secili or'')and any(k in m_low for k in('analiz','bak','durum','çiz','göster','girilir mi','nasıl')):
  try:
   sem_y=hedef_o.split(':',1)[-1]
   piy_y='spot'if hedef_o.startswith('SPOT:')else'future'
   if hedef_o not in analiz_hafizasi:
    analiz_hafizasi[hedef_o]=pine_icin_4h_1h_5m_veri_hazirla(sem_y,piy_y,{},hedef_o)
   if cizim_istegi is None:
    cizim_istegi={'parite':hedef_o,'mod':'ltf_zoom','tf':tf_s,'bar':bar_s}
  except Exception:pass
 if uygulanan:
  _api_kaydet_tam()
  _ak_kaydet()
  if hedef_o and I(H,dict)and H.get('df_4h')is not None and H.get('df_1h')is not None and H.get('df_15m')is not None:
   try:
    J_u=H.get('sembol',hedef_o.split(':',1)[-1])
    D_u=H.get('piyasa','spot'if hedef_o.startswith('SPOT:')else'future')
    yeni_H=mahserin_4_atlisi_confluence_analizi(J_u,H['df_4h'],H['df_1h'],H['df_15m'],D_u)
    H.update(yeni_H)
    analiz_hafizasi[hedef_o]=H
   except Exception:pass
  if gui_ref:
   try:gui_ref.arayuzu_guncelle()
   except Exception:pass
  return(True,'\n'.join(uygulanan),cizim_istegi or{'parite':hedef_o,'mod':'ltf_zoom'})
 return(False,'',cizim_istegi)

def _bot_canli_baglam_ozeti(O_secili=None):
 """Yapay zekanin tum bot durumuna, acik islemlere, bakiyeye ve en iyi firsatlara hakim olmasi icin kisa canli baglam uretir."""
 acik_l=[]
 for k,v in acik_islemler.items():
  if I(v,dict):
   kz_u,kz_y,_,_,_,_,_=islem_kar_zarar_hesapla(k,v)
   acik_l.append(f"{k} ({v.get('yon')} | Giriş:{_fmt_f(v.get('giris',0))} | Anlık:{_fmt_f(v.get('anlik',0))} | SL:{_fmt_f(v.get('sl',0))} | TP1:{_fmt_f(v.get('tp',0))} | PnL:{kz_u:+.2f}$ [%{kz_y:+.2f}] | Neden:{v.get('ozet','-')})")
 sirali_tarama=sorted(
  [(k,v)for k,v in analiz_hafizasi.items()if I(v,dict)and':'in str(k)],
  key=lambda x:(int(x[1].get('konum_meta',{}).get('birincil_olcek_skoru',0)),int(x[1].get('konum_meta',{}).get('htf_oncelikli_bolge_sayisi',0)),int(x[1].get('skor',0))),
  reverse=True
 )[:6]
 en_iyiler=[f"{k} (Skor:{v.get('skor',0)}/100 | Ölçek:{v.get('konum_meta',{}).get('birincil_olcek_skoru',0)}/10000p | Yön:{v.get('sinyal','BEKLE')} | Bölge:{v.get('konum_meta',{}).get('en_yuksek_oncelik_etiket','-')})"for k,v in sirali_tarama]
 return(
  f"• Bot Durumu: {'ÇALIŞIYOR'if bot_calisiyor else'BEKLEMEDE'} | Mod: {ISLEM_TARZI_MODU} ({HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT}) | Piyasa: {PIYASA_MODU.upper()} ({'TESTNET/DEMO'if TESTNET_AKTIF else'MAINNET'})\n"
  f"• Kasa & Ayarlar: Toplam Bakiye={T:.2f}$ (Gerçekleşen Net PnL:{W:+.2f}$) | Kaldıraç:{KALDIRAC}x ({MARJIN_TIPI}) | İşlem Başı Risk:{ISLEM_BASI_RISK_USDT}$ (1R) | Maks Marjin:{MAKS_MARJIN_USDT}$ | TP1:{RISK_ODUL_ORANI}R / TP2:{NIHAI_TP_RR}R | Min Skor:{MIN_CONFLUENCE_SKORU} | Stop Modu:{STOP_BELIRLEME_MODU}\n"
  f"• 1.Öncelik Ölçek & Kalibrasyon: 1.Öncelik (Arz/Talep,OB,OTE,QML) Ölçek Çarpanı={BIRINCIL_BOLGE_OLCEK_CARPANI:.1f}x (10000p Ölçek) | KYSY HTF={KYSY_HTF_ATR_CARPANI}x ATR, LTF={KYSY_LTF_ATR_CARPANI}x ATR | EQH Tolerans={EQH_EQL_TOL_ATR}x ATR | SFP Min İğne={SFP_MIN_IGNE_ATR}x ATR | 2.Kademe İzni={IKINCIL_BOLGE_GIRIS_AKTIF}\n"
  f"• Açık İşlemler ({L(acik_l)}/{a4}): {'; '.join(acik_l) if acik_l else 'Şu an açık işlem yok.'}\n"
  f"• Taranan En Yüksek Ölçekli 1.Öncelik Pariteler: {'; '.join(en_iyiler) if en_iyiler else 'Henüz tarama yapılmadı.'}"
 )

def dahili_uzman_islem_analizi_uret(soru,O_secili=None,rontgen=None):
 """Tamamen cevrimdisi kalindiginda bile ASLA hazir/kalip 50 satirlik rapor basmaz; sorulan soruyu dogrudan, kisa ve dogal sohbet diliyle yanitlar."""
 hedef_o=_metinden_sembol_cikar(soru,str(O_secili or'FUT:BTC/USDT'))
 rg=rontgen if(I(rontgen,dict)and rontgen.get('parite')==hedef_o)else islem_rontgeni_olustur(hedef_o)
 s_low=str(soru or'').lower().strip()
 chk=rg.get('chk',{})
 p1,p2,p3,p4=rg.get('atli_puanlar',(0,0,0,0))
 if any(k in s_low for k in('merhaba','selam','nasılsın','kimsin','ne yapabilirsin','yardım')):
  return(
   f"Merhaba! Ben Alfa Trade Club ({BOT_VERSIYONU}) içine entegre özgür yapay zeka asistanıyım. Şu an seçili parite **{rg['parite']}** ({rg['yon']}, Skor: {rg['skor']}/100, 1.Öncelik Ölçeği: {rg.get('birincil_olcek_skoru',0)}/10000p).\n\n"
   f"Bana istediğin her şeyi sorabilir veya doğrudan iş yaptırabilirsin:\n"
   f"• *'Bu işlemi neden açtın, giriş yerini nasıl seçtin?'* diye sorabilirsin,\n"
   f"• *'SOL 15m grafiğini çiz'*, *'Sadece likiditeleri göster'*, *'Konuşmayı ayrı pencerede aç'* diyebilirsin,\n"
   f"• *'Stopu 84500 yap'*, *'Kaldıracı 10x yap'*, *'1. öncelik ölçek çarpanını 6 yap'*, *'En iyi 5 fırsatı göster'* gibi emirler verebilirsin."
  )
 if any(k in s_low for k in('en iyi','fırsat','hangi coin','hangisine gir','tara','öneri')):
  sirali=sorted(
   [(k,v)for k,v in analiz_hafizasi.items()if I(v,dict)and':'in str(k)],
   key=lambda x:(int(x[1].get('konum_meta',{}).get('birincil_olcek_skoru',0)),int(x[1].get('konum_meta',{}).get('htf_oncelikli_bolge_sayisi',0)),int(x[1].get('skor',0))),
   reverse=True
  )[:5]
  if not sirali:
   return"Şu an hafızada taranmış parite yok; üstten **▶ Başlat** butonuna basarak veya bana *'Botu başlat'* ya da *'ETH analiz et'* diyerek canlı analiz başlatabilirsin."
  satirlar=[f"Şu an 1. Öncelik (Arz/Talep, OB, OTE, QML) radarına göre en güçlü {L(sirali)} aday:"]
  for idx_s,(k_s,v_s)in enumerate(sirali,1):
   km_s=v_s.get('konum_meta',{})
   satirlar.append(f"{idx_s}. **{k_s}** — Ölçek: **{km_s.get('birincil_olcek_skoru',0)}/10000p** | Skor: **{v_s.get('skor',0)}/100** | Yön: {v_s.get('sinyal','BEKLE')} | Bölge: {km_s.get('en_yuksek_oncelik_etiket','-')} ({km_s.get('htf_safe_derecesi','-')})")
  return'\n'.join(satirlar)
 if any(k in s_low for k in('bakiye','kasam','kasa','kaç para','açık işlem','pozisyonlarım','durum ne')):
  return"📊 **Güncel Bot ve Kasa Durumu:**\n"+_bot_canli_baglam_ozeti(hedef_o)
 if any(k in s_low for k in('hata','yanlış','riskli','risk var','sorun','kusur','denet','kontrol et')):
  return(
   f"🔍 **{rg['parite']} ({rg['yon']}) Hata & Risk Değerlendirmesi:**\n"
   +"\n".join(f"• {n}"for n in rg['denetim_notlari'])
   +"\n\nİstersen bana doğrudan *'Stopu HTF yapıya çek'*, *'Stopu girişe çek'* veya *'EQH toleransını 0.22 yap'* diyerek anında düzelttirebilirsin."
  )
 if any(k in s_low for k in('stop neden','stop nasıl','stop nerede','sl nasıl','tp nasıl','hedef nasıl','hesapla','marjin ne','miktar ne','kaç r')):
  return(
   f"🎯 **{rg['parite']} Giriş, Stop ve Hedef Hesabı:**\n"
   f"• **Giriş:** `{_fmt_f(rg['giris'])}` ({rg['oncelik_etiket']} bölgesinden, Ölçek: `{rg.get('birincil_olcek_skoru',0)}/10000p`)\n"
   f"• **Stop-Loss (1R):** `{_fmt_f(rg['sl'])}` — `{rg['stop_kaynak']}` esas alındı. Stop olursa kasadan tam **-{rg['risk_usdt']:.2f} USDT (1R)** eksilir (Miktar: `{rg['miktar']}`, Marjin: `{rg['marjin_usdt']:.2f}$`).\n"
   f"• **TP1 ({RISK_ODUL_ORANI}R):** `{_fmt_f(rg['tp1'])}` (Pozisyonun %50'si kapatılır ve stop girişe [Break-Even] çekilir).\n"
   f"• **TP2 ({NIHAI_TP_RR}R Nihai):** `{_fmt_f(rg['tp2'])}` (Karşı likidite havuzu hedefi)."
  )
 if any(k in s_low for k in('likidite','idm','sfp','eqh','eql','fvg','imbalance')):
  return(
   f"💧 **{rg['parite']} Likidite ve Imbalance (FVG) Durumu:**\n"
   f"• **Likidite Akışı:** `{rg['likidite_turu']}` | **SFP (İğne Avı):** `{rg['sfp_durumu']}`\n"
   f"• **Imbalance / FVG:** `{rg['imbalance_tipi']}`\n"
   f"• **Kalibrasyon:** Eş tepe/dip (EQH/EQL) toleransı `{EQH_EQL_TOL_ATR:.2f}x ATR`, SFP minimum iğne taşması `{SFP_MIN_IGNE_ATR:.2f}x ATR` olarak çalışıyor. Grafiğini görmek için *'Sadece likiditeyi çiz'* diyebilirsin."
  )
 if any(k in s_low for k in('neye göre','neden','niçin','nasıl belirle','giriş yeri','açtın','açmış','özet')):
  aktif_b=', '.join(rg['aktif_htf_bolgeler'])if rg['aktif_htf_bolgeler']else'Bölge Dışı'
  tetik_l=', '.join((rg['ltf_kirilimlar']+rg['ltf_mumlar']))if(rg['ltf_kirilimlar']or rg['ltf_mumlar'])else'LTF tetik bekleniyor'
  return(
   f"📌 **{rg['parite']} ({rg['yon']}) İşlem Açılış ve Giriş Özeti:**\n"
   f"1. **İlk Kontrol & HTF Konum ({rg['htf_periyot'].upper()}):** İlk önceliğimiz olan **Arz/Talep, OB, OTE ve QML** kontrolünde `{rg['oncelik_etiket']}` (Ölçek: **{rg.get('birincil_olcek_skoru',0)}/10000p**) sağlandı; toplamda **{rg['safe_sayisi']}/8 bölge (`{aktif_b}`)** aktif (QML:`{chk.get('qml_fiyat','-')}`, OB:`{chk.get('ob_aralik','-')}`, Arz/Talep:`{chk.get('fresh_aralik','-')}`, OTE:`{chk.get('ote_aralik','-')}`).\n"
   f"2. **LTF Giriş Tetiği ({rg['ltf_periyot']}):** Bölge içinde **`{tetik_l}`** onaylandığı anda `{_fmt_f(rg['giris'])}` fiyatından giriş belirlendi.\n"
   f"3. **Skor & Risk:** Mahşerin 4 Atlısı skoru **{rg['skor']}/100** (`{p1}+{p2}+{p3}+{p4}`), Stop `{_fmt_f(rg['sl'])}` (`-{rg['risk_usdt']:.2f}$`), TP1 `{_fmt_f(rg['tp1'])}`, TP2 `{_fmt_f(rg['tp2'])}`."
  )
 return(
  f"**{rg['parite']}** şu an `{_fmt_f(rg['anlik'])}` seviyesinde (Yön: **{rg['yon']}**, Skor: **{rg['skor']}/100**, 1.Öncelik Ölçeği: **{rg.get('birincil_olcek_skoru',0)}/10000p**, Bölge: `{', '.join(rg['aktif_htf_bolgeler']) or 'Bölge Dışı'}`). "
  f"Giriş `{_fmt_f(rg['giris'])}`, Stop `{_fmt_f(rg['sl'])}`, TP1 `{_fmt_f(rg['tp1'])}`.\n"
  f"Bana spesifik olarak *'Neden buradan girdin?'*, *'Likiditeyi çiz'*, *'Stopu HTF yap'* veya başka bir parite için *'SOL/USDT analiz et ve çiz'* diyebilirsin."
 )

def _ucretsiz_bulut_ai_sor(sistem_talimati,soru,gecmis_mesajlar=None):
 """Kullanici henuz kendi Gemini API anahtarini girmemisse bile internete bagli PC/Telefonda gercek ucretsiz LLM yaniti uretir."""
 try:
  mesajlar=[{'role':'system','content':sistem_talimati}]
  if I(gecmis_mesajlar,list):
   for gm in gecmis_mesajlar[-6:]:
    mesajlar.append({'role':'user','content':str(gm)})
  mesajlar.append({'role':'user','content':str(soru)})
  r=_HTTP_SES.post(
   'https://text.pollinations.ai/openai',
   headers={'Content-Type':'application/json'},
   json={'model':'openai','messages':mesajlar,'temperature':0.35},
   timeout=16
  )
  if r.status_code==200:
   j=r.json()
   txt=j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
   if txt and L(txt)>5:
    return txt
 except Exception:pass
 return''

def gemini_api_sor(soru,O_secili=None,rontgen=None,grafik_b64=None,gecmis_mesajlar=None,gui_ref=None):
 """Özgür Yapay Zeka Ajanı: Hazir kalip kullanmadan her soruyu dogal yanitlar ve kullanicinin istedigi bot/grafik/islem aksiyonlarini aninda icra eder."""
 hedef_o=_metinden_sembol_cikar(soru,str(O_secili or'FUT:BTC/USDT'))
 duz_yapildi,duz_mesaj,cizim_istegi=gemini_komut_ve_hata_duzeltici(soru,hedef_o,gui_ref)
 rg=islem_rontgeni_olustur(hedef_o)
 bot_baglam=_bot_canli_baglam_ozeti(hedef_o)
 sistem_talimati=(
  f"Sen Alfa Trade Club Bot ({BOT_VERSIYONU}) içindeki özgür, zeki ve tam yetkili Yapay Zeka Ajanısın (Gemini AI).\n"
  "KESİN KURALLARIN:\n"
  "1. ASLA uzun, sıkıcı, hazır kalıp şablonlar veya '=====' çizgileriyle dolu 50 satırlık raporlar basma! Tıpkı gerçek bir insan/uzman trader arkadaş gibi doğal, özgür, doğrudan ve net cevap ver.\n"
  "2. Kullanıcı ne sorduysa SADECE onu net ve anlaşılır şekilde cevapla (Örn: 'Neden açtın?' derse 3-4 net maddede hangi HTF bölge ve LTF mumla açıldığını söyle; genel sohbet veya strateji sorarsa özgürce cevapla).\n"
  "3. Kullanıcının bota yaptırmak istediği her şeyi yapabilirsin! Eğer kullanıcı grafik çizdirmek, periyot değiştirmek, ayrı pencere açmak, stop/hedef değiştirmek, kaldıraç/risk/skor değiştirmek, işlem kapatmak veya botu başlatıp durdurmak isterse yanıtının en sonuna şu JSON komutunu ekle:\n"
  f'<AJAN_KOMUTU>{{"aksiyon": "grafik_ciz|ayri_sohbet_ac|tradingview_ac|bot_baslat|bot_durdur|islem_kapat|ayar_degistir", "parite": "{hedef_o}", "cizim_modu": "ltf_zoom|mtf_3lu|htf_bolge|likidite_denetim|sadece_likidite|sadece_qml_ote|sadece_ob_fvg|temiz_mum", "periyot": "15m", "bar_sayisi": 85, "ayri_pencere": false, "yeni_sl": 0, "yeni_tp": 0, "stop_modu": "", "kaldirac": 0, "risk_usdt": 0, "marjin_usdt": 0, "rr": 0, "min_skor": 0, "eqh_tol_atr": 0, "sfp_min_atr": 0, "kysy_htf_atr": 0, "birincil_olcek_carpani": 0}}</AJAN_KOMUTU>\n\n'
  f"CANLI BOT VE KASA DURUMU:\n{bot_baglam}\n\n"
  f"SEÇİLİ PARİTE ({hedef_o}) VERİSİ:\n{rg['tam_rapor_metni']}"
 )
 tip,anahtar=_google_hesap_token_bul()
 gecmis_metin=''
 if I(gecmis_mesajlar,list)and gecmis_mesajlar:
  gecmis_metin='\nSON KONUŞMALAR:\n'+'\n'.join(gecmis_mesajlar[-6:])+'\n'
 if tip and anahtar:
  parts=[{'text':f"{sistem_talimati}\n{gecmis_metin}\nKULLANICI: {soru}"}]
  if grafik_b64 and L(str(grafik_b64))>100 and any(k in soru.lower()for k in('grafik','görsel','bak','çiz','hata','likidite','mum','nerede','nasıl')):
   parts.append({'inline_data':{'mime_type':'image/png','data':str(grafik_b64)}})
  payload={'contents':[{'parts':parts}],'generationConfig':{'temperature':0.4,'maxOutputTokens':1500}}
  modeller_sirasi=[GEMINI_MODEL]+[m for m in GEMINI_MODELLERI if m!=GEMINI_MODEL]
  for mdl in modeller_sirasi:
   try:
    if tip=='api_key':
     url=f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={anahtar}"
     hdr={'Content-Type':'application/json'}
    else:
     url=f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent"
     hdr={'Content-Type':'application/json','Authorization':f"Bearer {anahtar}"}
    r=_HTTP_SES.post(url,headers=hdr,json=payload,timeout=20)
    if r.status_code==200:
     j=r.json()
     cands=j.get('candidates',[])
     if cands and I(cands[0].get('content'),dict):
      p_list=cands[0]['content'].get('parts',[])
      yanit_txt=''.join(str(p.get('text',''))for p in p_list if I(p,dict)).strip()
      if yanit_txt:
       ai_duz_ok,ai_duz_msg,ai_ciz_ist=gemini_komut_ve_hata_duzeltici(yanit_txt,hedef_o,gui_ref)
       temiz_yanit=re.sub(r'<(?:AJAN_KOMUTU|DUZELTME_KOMUTU)>.*?</(?:AJAN_KOMUTU|DUZELTME_KOMUTU)>','',yanit_txt,flags=re.DOTALL).strip()
       aksiyon_notu='\n'.join(x for x in(duz_mesaj if duz_yapildi else'',ai_duz_msg if ai_duz_ok else'')if x)
       son_metin=(f"⚡ **Uygulanan İşlem:**\n{aksiyon_notu}\n\n{temiz_yanit}")if aksiyon_notu else temiz_yanit
       return(son_metin,ai_ciz_ist or cizim_istegi)
   except Exception:continue
 bulut_yanit=_ucretsiz_bulut_ai_sor(sistem_talimati,soru,gecmis_mesajlar)
 if bulut_yanit:
  ai_duz_ok,ai_duz_msg,ai_ciz_ist=gemini_komut_ve_hata_duzeltici(bulut_yanit,hedef_o,gui_ref)
  temiz_yanit=re.sub(r'<(?:AJAN_KOMUTU|DUZELTME_KOMUTU)>.*?</(?:AJAN_KOMUTU|DUZELTME_KOMUTU)>','',bulut_yanit,flags=re.DOTALL).strip()
  aksiyon_notu='\n'.join(x for x in(duz_mesaj if duz_yapildi else'',ai_duz_msg if ai_duz_ok else'')if x)
  son_metin=(f"⚡ **Uygulanan İşlem:**\n{aksiyon_notu}\n\n{temiz_yanit}")if aksiyon_notu else temiz_yanit
  return(son_metin,ai_ciz_ist or cizim_istegi)
 yerel_yanit=dahili_uzman_islem_analizi_uret(soru,hedef_o,rg)
 if duz_yapildi:
  yerel_yanit=f"⚡ **Uygulanan İşlem:**\n{duz_mesaj}\n\n{yerel_yanit}"
 return(yerel_yanit,cizim_istegi)


# ==============================================================================
# BULUT SENKRONİZASYON (PC <-> ANDROID EŞLEŞTİRME) VE TEK TUŞLA OTA GÜNCELLEME
# ==============================================================================
import base64 as _b64
import re as _re
import re

if "GITHUB_REPO_ADRESI" not in globals() or not GITHUB_REPO_ADRESI: GITHUB_REPO_ADRESI = "emrhozbr/bot"
if "GITHUB_TOKEN" not in globals(): GITHUB_TOKEN = ""
BULUT_SENK_AKTIF = True
AKTIF_OTA_SURUM_BILGISI = "v4.0.9 (Canlı Motor)"
_SON_BULUT_OKUMA_TS = 0.0
_SON_BULUT_YAZMA_HASH = ""
_BULUT_DOSYA_ADI = "senkron_durum.json"
_OTA_YEREL_CEKIRDEK = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_cekirdek_motor.py')
_OTA_YEREL_UI = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_flet_ui.py')
_OTA_META_DOSYA = os.path.join(ANDROID_VERI_DIZINI if 'ANDROID_VERI_DIZINI' in globals() else '.', 'ota_meta_bilgi.json')

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
    f_marker = "def _f(" + "d,c,i=-2):"
    if "def indiktorleri_ekle(df):" in kaynak_kod:
        ana_govde = kaynak_kod[kaynak_kod.index("def indiktorleri_ekle(df):"):]
    elif f_marker in kaynak_kod:
        ana_govde = kaynak_kod[kaynak_kod.index(f_marker):]
    else:
        ana_govde = kaynak_kod
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
        "__YASAK_YOK__"
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
    metin = metin.replace(
        "if os.name=='nt':os.startfile(dosya_yolu)\n  else:webbrowser.open(Path(dosya_yolu).as_uri())",
        "if os.name=='nt' and 'KALICI_VERI_DIZINI' not in globals():os.startfile(dosya_yolu)"
    )
    metin = metin.replace("webbrowser.open(Path(dosya_yolu).as_uri())", "None")
    metin = metin.replace("webbrowser.open('file://'+dosya_yolu)", "None")
    return metin

def masaustu_gui_ozelliklerini_ayikla(kaynak_kod: str) -> dict:
    meta = {
        "versiyon": "",
        "baslik": "",
        "ekstra_metrikler": [],
        "guncellenme_zamani": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
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
    flet_ui_kod = None

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
                kaynak_adi = f"{hedef_repo}/{dosya}"
                break
        main_indirilen = _github_dosya_indir(hedef_repo, "main.py", hedef_token)
        if main_indirilen and len(main_indirilen) > 1000:
            if "class AlfaMobileBotEngine" in main_indirilen and "def main(page: ft.Page):" in main_indirilen:
                flet_ui_kod = main_indirilen[main_indirilen.index("class AlfaMobileBotEngine"):]
                if "if __name__" in flet_ui_kod:
                    flet_ui_kod = flet_ui_kod[:flet_ui_kod.index("if __name__")]
            if not kaynak_kod:
                kaynak_kod = main_indirilen
                kaynak_adi = f"{hedef_repo}/main.py"

    if not kaynak_kod or len(kaynak_kod) < 500:
        return (False, "⚠️ GitHub üzerinden botv4.0.9.py veya main.py okunamadı! Repo gizli (Private) ise Ayarlar'dan GitHub Token girip tekrar deneyin.")

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

        ui_msg = "Strateji Çekirdeği"
        if flet_ui_kod and len(flet_ui_kod) > 500:
            with open(_OTA_YEREL_UI, "w", encoding="utf-8") as f:
                f.write(flet_ui_kod)
            exec(compile(flet_ui_kod, _OTA_YEREL_UI, "exec"), globals())
            ui_msg = "Strateji + Mobil Arayüz"

        meta = masaustu_gui_ozelliklerini_ayikla(kaynak_kod)
        meta["kaynak_dosya"] = kaynak_adi
        ver_str = meta.get("versiyon") or globals().get("BOT_VERSIYONU", "v4.0.9")
        AKTIF_OTA_SURUM_BILGISI = f"{ver_str} [{os.path.basename(kaynak_adi)}] ({datetime.now().strftime('%H:%M:%S')})"
        meta["aktif_surum"] = AKTIF_OTA_SURUM_BILGISI
        try:
            with open(_OTA_META_DOSYA, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False)
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
        _sozlukten_ayarlari_uygula(yedek_ayar)
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
        _ak_kaydet()
        return (True, f"✅ OTA Güncelleme Başarılı! ({ui_msg}: {AKTIF_OTA_SURUM_BILGISI}) -> Ayarlarınız ve açık işlemleriniz korunarak yeni sürüm canlıya alındı!")
    except Exception as ex:
        borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
        return (False, f"⚠️ OTA Kod Dönüştürme Hatası: {ex}")

def _kayitli_ota_varsa_yukle():
    global AKTIF_OTA_SURUM_BILGISI
    try:
        if os.path.exists(_OTA_META_DOSYA):
            try:
                with open(_OTA_META_DOSYA, "r", encoding="utf-8") as f:
                    md = json.load(f)
                    if isinstance(md, dict) and md.get("aktif_surum"):
                        AKTIF_OTA_SURUM_BILGISI = str(md["aktif_surum"])
            except Exception:
                pass
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
        if os.path.exists(_OTA_YEREL_UI):
            with open(_OTA_YEREL_UI, "r", encoding="utf-8") as f:
                ui_kod = f.read()
            if len(ui_kod) > 500 and "def main(page: ft.Page):" in ui_kod:
                exec(compile(ui_kod, _OTA_YEREL_UI, "exec"), globals())
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
        ayar_paketi = masaustu_ayar_sozlugu_uret()
        veri = {
            "guncelleme_ts": time.time(),
            "guncelleyen_cihaz": "ANDROID_MOBIL" if "KALICI_VERI_DIZINI" in globals() else "PC_MASAUSTU",
            "bot_versiyonu": globals().get("BOT_VERSIYONU", "v4.0.9"),
            "ayarlar": ayar_paketi,
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
            "message": f"Sync: {veri['guncelleyen_cihaz']} ({datetime.now().strftime('%H:%M:%S')})",
            "content": icerik_b64
        }
        if mevcut_sha:
            payload["sha"] = mevcut_sha
        r_put = _HTTP_SES.put(api_url, headers=hdr, json=payload, timeout=8)
        return r_put.status_code in (200, 201)
    except Exception:
        return False

def bulut_durum_cek(zorla=False):
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
                    if d.get("guncelleyen_cihaz") == "PC_MASAUSTU":
                        uzak_ayar = d.get("ayarlar")
                        if I(uzak_ayar, dict):
                            ayar_ts = F(uzak_ayar.get("guncelleme_ts") or uzak_ts)
                            if ayar_ts > _SON_PC_AYAR_TS:
                                _SON_PC_AYAR_TS = ayar_ts
                                _sozlukten_ayarlari_uygula(uzak_ayar)
                                _api_kaydet_tam()
                                if callable(_UI_AYAR_YENILE_FN):
                                    try:
                                        _UI_AYAR_YENILE_FN()
                                    except Exception:
                                        pass
                                degisti = True
                        uzak_ver = str(d.get("bot_versiyonu") or "")
                        if uzak_ver and uzak_ver not in str(AKTIF_OTA_SURUM_BILGISI):
                            threading.Thread(target=ota_strateji_guncelle, args=(GITHUB_REPO_ADRESI, GITHUB_TOKEN), daemon=True).start()
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
    if not TESTNET_AKTIF and API_KEY and API_SECRET and PIYASA_MODU in ("future", "her_ikisi"):
        try:
            if hasattr(ao, "_signed_req"):
                acc = ao._signed_req("GET", "/fapi/v2/account")
                positions = acc.get("positions", []) if I(acc, dict) else []
            else:
                positions = []
            for p in positions:
                amt = F(p.get("positionAmt") or 0.0)
                if A(amt) > 0:
                    raw_sym = str(p.get("symbol", ""))
                    if raw_sym.endswith("USDT"):
                        sem = f"{raw_sym[:-4]}/USDT"
                        O_key = f"FUT:{sem}"
                        if not I(acik_islemler.get(O_key), dict):
                            ep = F(p.get("entryPrice") or 0.0)
                            lev = int(F(p.get("leverage") or KALDIRAC))
                            yon_p = "LONG" if amt > 0 else "SHORT"
                            mO = -1.0 if yon_p == "SHORT" else 1.0
                            sl_p = R(ep * (1.0 - mO * 0.01), 6)
                            tp_p = R(ep * (1.0 + mO * 0.01 * RISK_ODUL_ORANI), 6)
                            acik_islemler[O_key] = {
                                "sembol": sem, "yon": yon_p, "piyasa": "future", "simule": False,
                                "kaldirac": lev, "giris": ep, "anlik": ep,
                                "pnl_usdt": F(p.get("unrealizedProfit") or 0.0), "pnl_yuzde": 0.0,
                                "marjin_usdt": R((A(amt) * ep) / M(lev, 1), 2),
                                "sl": sl_p, "ilk_sl": sl_p, "tp": tp_p, "tp_nihai": tp_p,
                                "miktar": A(amt), "risk_usdt": ISLEM_BASI_RISK_USDT,
                                "kismi_tp_alindi": False, "ozet": "[Diğer Cihazdan / Borsadan Senkronize]"
                            }
                            degisti = True
        except Exception:
            pass
    return degisti

def mobil_canli_svg_grafik_uret(O, tf_secim='5m', H_ozel=None):
    """Android Flet uygulama icinde (tarayiciya gerek kalmadan) canli Mum + Arz/Talep OB + FVG + Swing/BOS + QML/OTE + Giris/SL/TP grafigini SVG (base64) olarak uretir."""
    try:
        H = H_ozel or analiz_hafizasi.get(O) or analiz_hafizasi.get(str(O).split(':', 1)[-1]) or {}
        J = H.get('sembol', str(O).split(':', 1)[-1])
        D = H.get('piyasa', 'spot' if str(O).startswith('SPOT:') else 'future')
        htf_p, mtf_p, ltf_p, _ = _parite_mtf_periyotlarini_bul(O, J, D, H)
        if not H or H.get('df_4h') is None or (H.get('df_5m') is None and H.get('df_15m') is None):
            try:
                H = pine_icin_4h_1h_5m_veri_hazirla(J, D, H, O)
                analiz_hafizasi[O] = H
            except Exception:
                pass
        if tf_secim in ('4h', htf_p):
            df_t = H.get('df_4h', H.get('df_4h_full'))
            yp_t = H.get('yapi_4h', {})
            kt_t = H.get('kutular_4h', H.get('cizim_kutulari_4h', []))
            tf_etiket = htf_p.upper()
        elif tf_secim in ('1h', mtf_p):
            df_t = H.get('df_1h', H.get('df_1h_full'))
            yp_t = H.get('yapi_1h', {})
            kt_t = H.get('kutular_1h', H.get('cizim_kutulari_1h', []))
            tf_etiket = mtf_p.upper()
        else:
            df_t = H.get('df_5m', H.get('df_15m', H.get('df_15m_full')))
            yp_t = H.get('yapi_5m', H.get('yapi_15m', {}))
            kt_t = H.get('kutular_5m', H.get('cizim_kutulari_15m', []))
            tf_etiket = ltf_p
        tv_d = _df_to_tv_json(df_t, yp_t, kt_t)
        mumlar = tv_d.get('mumlar', [])[-95:]
        if L(mumlar) < 5:
            return ""
        n_bars = L(mumlar)
        idx_offset = M(0, L(tv_d.get('mumlar', [])) - n_bars)
        w, h = 920, 500
        pad_l, pad_r, pad_t, pad_b = 14, 108, 36, 26
        cw = w - pad_l - pad_r
        ch = h - pad_t - pad_b

        all_hi = M(F(m['high']) for m in mumlar)
        all_lo = N(F(m['low']) for m in mumlar)
        dR = acik_islemler.get(O)
        aktif_sinyal_var = bool(I(dR, dict) or H.get('sinyal') in ('LONG', 'SHORT'))
        giris = F(dR['giris'] if I(dR, dict) else (H.get('giris') if aktif_sinyal_var else 0.0))
        sl = F(dR['sl'] if I(dR, dict) else (H.get('sl') if aktif_sinyal_var else 0.0))
        yon_islem = dR['yon'] if I(dR, dict) else (H.get('sinyal') if H.get('sinyal') in ('LONG', 'SHORT') else 'BEKLE')
        rk = A(giris - sl) if giris > 0 and sl > 0 else 0.0
        mO = -1.0 if yon_islem == 'SHORT' else 1.0
        tp1 = F(dR['tp'] if I(dR, dict) else (giris + mO * rk * RISK_ODUL_ORANI if rk > 0 else 0.0))
        for ekstra_p in (giris, sl, tp1):
            if ekstra_p > 0 and all_lo * 0.88 <= ekstra_p <= all_hi * 1.12:
                all_hi = M(all_hi, ekstra_p)
                all_lo = N(all_lo, ekstra_p)
        rng = M(all_hi - all_lo, all_hi * 0.002)
        p_max = all_hi + rng * 0.06
        p_min = all_lo - rng * 0.06
        p_span = M(p_max - p_min, 1e-9)

        def py(p):
            return R(pad_t + ch * (1.0 - (F(p) - p_min) / p_span), 1)

        def bx(i):
            return R(pad_l + (F(i) + 0.5) * (cw / M(n_bars, 1)), 1)

        bar_w = M(2.5, R((cw / M(n_bars, 1)) * 0.64, 1))
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#0f172a" rx="8"/>'
        ]
        for g_i in G(6):
            p_val = p_min + p_span * (g_i / 5.0)
            yg = py(p_val)
            svg.append(f'<line x1="{pad_l}" y1="{yg}" x2="{w - pad_r}" y2="{yg}" stroke="#1e293b" stroke-width="1"/>')
            svg.append(f'<text x="{w - pad_r + 6}" y="{yg + 3}" fill="#94a3b8" font-family="monospace" font-size="10">{_fmt_f(p_val)}</text>')

        smax = F(yp_t.get('swing_max') or 0.0)
        smin = F(yp_t.get('swing_min') or 0.0)
        if smax > smin > 0:
            du = smax - smin
            yon_b = yp_t.get('yon', 'BULLISH') != 'BEARISH'
            ote1 = smax - du * 0.618 if yon_b else smin + du * 0.618
            ote2 = smax - du * 0.786 if yon_b else smin + du * 0.786
            y_o1, y_o2 = py(M(ote1, ote2)), py(N(ote1, ote2))
            if 0 <= y_o1 <= h and 0 <= y_o2 <= h:
                svg.append(f'<rect x="{pad_l}" y="{N(y_o1, y_o2)}" width="{cw}" height="{M(3.0, A(y_o2 - y_o1))}" fill="#3b82f6" fill-opacity="0.10" stroke="#60a5fa" stroke-opacity="0.35" stroke-dasharray="4,3"/>')
                svg.append(f'<text x="{pad_l + 6}" y="{N(y_o1, y_o2) + 11}" fill="#60a5fa" font-family="sans-serif" font-size="9.5" font-weight="bold">OTE (0.618-0.786)</text>')

        for z in tv_d.get('arz_talep', [])[-6:]:
            i1 = M(0, int(z.get('idx1', 0)) - idx_offset)
            x1 = bx(i1)
            x2 = w - pad_r
            y1, y2 = py(z['hi']), py(z['lo'])
            top_y, box_h = N(y1, y2), M(3.0, A(y2 - y1))
            renk = "#10b981" if z.get('tur') == 'TALEP' else "#ef4444"
            svg.append(f'<rect x="{x1}" y="{top_y}" width="{M(10.0, x2 - x1)}" height="{box_h}" fill="{renk}" fill-opacity="0.18" stroke="{renk}" stroke-width="1"/>')
            etk = str(z.get('etiket', 'OB')).replace('&', '+').replace('<', '').replace('>', '')
            svg.append(f'<text x="{x2 - 4}" y="{top_y + 10}" fill="{renk}" font-family="sans-serif" font-size="9" font-weight="bold" text-anchor="end">{etk}</text>')

        for im in tv_d.get('imbalance', [])[-5:]:
            i1 = M(0, int(im.get('idx1', 0)) - idx_offset)
            x1 = bx(i1)
            x2 = w - pad_r
            y1, y2 = py(im['hi']), py(im['lo'])
            top_y, box_h = N(y1, y2), M(2.5, A(y2 - y1))
            renk = "#f59e0b" if im.get('yon') == 'BULL' else "#a855f7"
            svg.append(f'<rect x="{x1}" y="{top_y}" width="{M(10.0, x2 - x1)}" height="{box_h}" fill="{renk}" fill-opacity="0.14" stroke="{renk}" stroke-width="0.9" stroke-dasharray="3,2"/>')

        for i, m in enumerate(mumlar):
            x = bx(i)
            o_p, h_p, l_p, c_p = F(m['open']), F(m['high']), F(m['low']), F(m['close'])
            renk = "#22c55e" if c_p >= o_p else "#ef4444"
            yh, yl = py(h_p), py(l_p)
            yo, yc = py(o_p), py(c_p)
            svg.append(f'<line x1="{x}" y1="{yh}" x2="{x}" y2="{yl}" stroke="{renk}" stroke-width="1.2"/>')
            b_top = N(yo, yc)
            b_h = M(1.8, A(yc - yo))
            svg.append(f'<rect x="{R(x - bar_w / 2.0, 1)}" y="{b_top}" width="{bar_w}" height="{b_h}" fill="{renk}"/>')

        zz_pts = []
        for z in tv_d.get('zigzag', []):
            zi = int(z.get('idx', 0)) - idx_offset
            if 0 <= zi < n_bars:
                zx, zy = bx(zi), py(z['value'])
                zz_pts.append(f"{zx},{zy}")
                lbl_c = "#4ade80" if z.get('lbl') in ('HH', 'HL') else "#fb7185"
                ly = zy - 5 if z.get('tip') == 'H' else zy + 11
                svg.append(f'<text x="{zx}" y="{ly}" fill="{lbl_c}" font-family="sans-serif" font-size="8.5" font-weight="bold" text-anchor="middle">{z.get("lbl", "")}</text>')
        if L(zz_pts) >= 2:
            svg.append(f'<polyline points="{" ".join(zz_pts)}" fill="none" stroke="#cbd5e1" stroke-width="1.3" stroke-opacity="0.8"/>')

        for b in tv_d.get('bos', [])[-6:]:
            i1 = int(b.get('idx1', 0)) - idx_offset
            i2 = int(b.get('idx2', 0)) - idx_offset
            if i2 >= 0:
                x1, x2 = bx(M(0, i1)), bx(N(n_bars - 1, i2))
                yb = py(b['price'])
                b_col = "#22c55e" if b.get('yon') == 'BULLISH' else "#f43f5e"
                svg.append(f'<line x1="{x1}" y1="{yb}" x2="{x2}" y2="{yb}" stroke="{b_col}" stroke-width="1.3" stroke-dasharray="4,2"/>')
                b_lbl = "CHoCH" if "CHOCH" in str(b.get('tip', '')) else "BOS"
                svg.append(f'<text x="{R((x1 + x2) / 2.0, 1)}" y="{yb - 3}" fill="{b_col}" font-family="sans-serif" font-size="8.5" font-weight="bold" text-anchor="middle">{b_lbl}</text>')

        qml_v = F(tv_d.get('qml') or yp_t.get('qml_seviyesi') or 0.0)
        if qml_v > 0 and p_min <= qml_v <= p_max:
            yq = py(qml_v)
            svg.append(f'<line x1="{pad_l}" y1="{yq}" x2="{w - pad_r}" y2="{yq}" stroke="#c084fc" stroke-width="1.6" stroke-dasharray="5,3"/>')
            svg.append(f'<text x="{w - pad_r + 4}" y="{yq + 3}" fill="#c084fc" font-family="monospace" font-size="9.5" font-weight="bold">QML {_fmt_f(qml_v)}</text>')

        if giris > 0 and p_min <= giris <= p_max:
            yg = py(giris)
            svg.append(f'<line x1="{pad_l}" y1="{yg}" x2="{w - pad_r}" y2="{yg}" stroke="#38bdf8" stroke-width="1.8"/>')
            svg.append(f'<rect x="{w - pad_r + 2}" y="{yg - 8}" width="{pad_r - 4}" height="15" fill="#0284c7" rx="3"/>')
            svg.append(f'<text x="{w - pad_r + 5}" y="{yg + 3}" fill="#ffffff" font-family="monospace" font-size="9.5" font-weight="bold">G:{_fmt_f(giris)}</text>')
        if sl > 0 and p_min <= sl <= p_max:
            ys = py(sl)
            svg.append(f'<line x1="{pad_l}" y1="{ys}" x2="{w - pad_r}" y2="{ys}" stroke="#ef4444" stroke-width="1.8" stroke-dasharray="3,2"/>')
            svg.append(f'<rect x="{w - pad_r + 2}" y="{ys - 8}" width="{pad_r - 4}" height="15" fill="#dc2626" rx="3"/>')
            svg.append(f'<text x="{w - pad_r + 5}" y="{ys + 3}" fill="#ffffff" font-family="monospace" font-size="9.5" font-weight="bold">SL:{_fmt_f(sl)}</text>')
        if tp1 > 0 and p_min <= tp1 <= p_max:
            yt = py(tp1)
            svg.append(f'<line x1="{pad_l}" y1="{yt}" x2="{w - pad_r}" y2="{yt}" stroke="#10b981" stroke-width="1.8" stroke-dasharray="3,2"/>')
            svg.append(f'<rect x="{w - pad_r + 2}" y="{yt - 8}" width="{pad_r - 4}" height="15" fill="#059669" rx="3"/>')
            svg.append(f'<text x="{w - pad_r + 5}" y="{yt + 3}" fill="#ffffff" font-family="monospace" font-size="9.5" font-weight="bold">TP:{_fmt_f(tp1)}</text>')

        son_f = F(mumlar[-1]['close'])
        skor_v = H.get('skor', 0)
        sinyal_v = H.get('sinyal', 'BEKLE')
        baslik_str = f"{O} [{tf_etiket}] | Anlık: {_fmt_f(son_f)} | Yön: {yp_t.get('yon', '-')} | Sinyal: {sinyal_v} ({skor_v}/100)"
        svg.append(f'<text x="{pad_l + 4}" y="22" fill="#38bdf8" font-family="sans-serif" font-size="12.5" font-weight="bold">{baslik_str}</text>')
        svg.append('</svg>')
        svg_str = "".join(svg)
        return _b64.b64encode(svg_str.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""


# ==============================================================================
# YEREL GRAFİK SUNUCUSU (CANLI TRADINGVIEW HTML ÇİZİMLERİ İÇİN)
# ==============================================================================
_YEREL_SUNUCU_PORT = None

def yerel_grafik_sunucusu_baslat():
    global _YEREL_SUNUCU_PORT
    if _YEREL_SUNUCU_PORT is not None:
        return _YEREL_SUNUCU_PORT
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()

        class SessizHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=ANDROID_VERI_DIZINI, **kwargs)
            def log_message(self, format, *args):
                pass

        srv = ThreadingHTTPServer(("127.0.0.1", port), SessizHandler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        _YEREL_SUNUCU_PORT = port
        return port
    except Exception:
        return None

class AlfaMobileBotEngine:
    def __init__(self, ui_callback=None):
        self._kapaniyor = False
        self._acilis_ts = time.time()
        self._bot_baslangic_ts = None
        self._acilis_realize_w = F(W)
        self._bot_baslangic_w = F(W)
        self._log_q = []
        self._durum_metni = "Durum: Beklemede ⏸"
        self._durum_renk = "#f59e0b"
        self._senk_calisiyor = False
        self._tg_son_update_id = 0
        self.ui_callback = ui_callback
        _ak_yukle()
        self._acilis_realize_w = F(W)
        self._bot_baslangic_w = F(W)

    def log_yaz(self, fs):
        satir = f"[{datetime.now().strftime('%H:%M:%S')}] {fs}"
        self._log_q.append(satir)
        if L(self._log_q) > 350:
            del self._log_q[:100]
        if self.ui_callback:
            try:
                self.ui_callback("log")
            except Exception:
                pass

    def durum_guncelle(self, mM, f8="#4ade80"):
        self._durum_metni = mM
        self._durum_renk = f8
        if self.ui_callback:
            try:
                self.ui_callback("durum")
            except Exception:
                pass

    def arayuzu_guncelle(self):
        if self.ui_callback:
            try:
                self.ui_callback("all")
            except Exception:
                pass

    def oturum_pnl_hesapla(self, kU_ozel=None):
        if kU_ozel is None:
            kU_ozel = sum((islem_kar_zarar_hesapla(O, bq)[0] for O, bq in list(acik_islemler.items()) if I(bq, dict)))
        aktif_ts = self._bot_baslangic_ts if self._bot_baslangic_ts is not None else self._acilis_ts
        ref_w = self._bot_baslangic_w if self._bot_baslangic_ts is not None else self._acilis_realize_w
        gecen_sn = int(M(0, time.time() - aktif_ts))
        saat, kalan = divmod(gecen_sn, 3600)
        dk, sn = divmod(kalan, 60)
        sure_str = f"{saat:02d}:{dk:02d}:{sn:02d}"
        bas_tarih_str = datetime.fromtimestamp(aktif_ts).strftime("%H:%M:%S")
        oturum_kapanan = F(W) - F(ref_w)
        oturum_toplam = oturum_kapanan + F(kU_ozel)
        return (oturum_toplam, oturum_kapanan, F(kU_ozel), sure_str, bas_tarih_str)

    def oturum_sayaci_sifirla(self):
        self._bot_baslangic_ts = time.time()
        self._acilis_ts = time.time()
        self._bot_baslangic_w = F(W)
        self._acilis_realize_w = F(W)
        self.arayuzu_guncelle()

    def botu_baslat(self):
        global bot_calisiyor
        if not bot_calisiyor:
            if self._bot_baslangic_ts is None:
                self._bot_baslangic_ts = time.time()
                self._bot_baslangic_w = F(W)
            bot_calisiyor = True
            _ak_kaydet()
            i9 = "SPOT+VADELİ" if PIYASA_MODU == "her_ikisi" else PIYASA_MODU.upper()
            self.durum_guncelle(f"Çalışıyor ({i9}) 🟢", "#4ade80")
            self.log_yaz(f"🚀 Alfa Trade Club Mobil [{i9} | MTF: {HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT} | Kaldıraç: {KALDIRAC}x | Min Skor: {MIN_CONFLUENCE_SKORU}] başlatıldı.")
            threading.Thread(target=self.bot_ana_dongu, daemon=True).start()
            self.arayuzu_guncelle()

    def botu_durdur(self):
        global bot_calisiyor
        bot_calisiyor = False
        _ak_kaydet()
        self.durum_guncelle("Durduruldu 🔴", "#f87171")
        self.log_yaz("⏹ Bot kullanıcı tarafından durduruldu.")
        self.arayuzu_guncelle()

    def _emir_kapat(self, J, D, bt, Y, e5):
        if e5:
            return
        a9 = emir_ist(D)
        try:
            a9.cancel_all_orders(J)
        except Exception:
            pass
        try:
            if D == "future":
                if bt == "LONG":
                    a9.create_market_sell_order(J, Y, {"reduceOnly": True})
                else:
                    a9.create_market_buy_order(J, Y, {"reduceOnly": True})
            else:
                a9.create_market_sell_order(J, Y)
        except Exception:
            pass

    def poz_kapat(self, O, dl="MANUEL KAPATMA", pJ=True):
        global W, S
        try:
            bq = acik_islemler.get(O)
            if not I(bq, dict):
                return
            J, b0, ig = (bq.get("sembol", O.split(":", 1)[-1]), bq.get("piyasa", "future"), bq.get("simule", False))
            Y, bZ, bt = (bq["miktar"], bq["giris"], bq.get("yon", "LONG"))
            bM = anlik_fiyat_getir(J, b0)
            self.log_yaz(f"⏳ {O} ({bt}) pozisyonu market fiyatından kapatılıyor...")
            self._emir_kapat(J, b0, bt, Y, ig)
            kz = (bZ - bM if bt == "SHORT" else bM - bZ) * Y
            W += kz
            if ig and b0 == "future":
                S += kz
            nf = (bZ - bM if bt == "SHORT" else bM - bZ) / M(bZ, 1e-9) * 100 * bq.get("kaldirac", 1)
            _ig_kaydet(J, b0, bt, bZ, bM, Y, kz, nf, dl, bq.get("ozet", ""))
            acik_islemler[O] = None
            _ak_kaydet()
            self.log_yaz(f"✅ {O} ({bt}) [{dl}] kapatıldı! Net Sonuç: {kz:+.2f} USDT")
            tg_bildir(f"🖐 <b>{dl} ({O} - {bt})</b>\nSonuç: {kz:+.2f} USDT")
            if pJ:
                self.pozisyonlari_senkronize_et()
            self.arayuzu_guncelle()
        except Exception as e:
            self.log_yaz(f"⚠️ {O} kapatılırken hata oluştu: {e}")

    def pozisyonlari_senkronize_et(self):
        global acik_islemler, V, T, W, S
        if self._senk_calisiyor:
            return
        self._senk_calisiyor = True
        try:
            try:
                bulut_durum_cek(zorla=False)
            except Exception:
                pass
            for O, bq in list(acik_islemler.items()):
                if not I(bq, dict):
                    continue
                J, b0, ig = (bq.get("sembol", O.split(":", 1)[-1]), bq.get("piyasa", "future"), bq.get("simule", False))
                ja = veri_ist(b0)
                try:
                    bM = anlik_fiyat_getir(J, b0)
                except Exception:
                    continue
                if O in a1:
                    a1[O]["fiyat"] = bM
                bq["anlik"] = bM
                gW, nD, bZ, _, fk, k1, _ = islem_kar_zarar_hesapla(O, bq)
                bt, sl, tp = (bq.get("yon", "LONG"), bq["sl"], bq["tp"])
                oN, Y, gX = (bq.get("tp_nihai", tp), bq["miktar"], bq.get("kismi_tp_alindi", False))
                nt = bt == "SHORT"
                nu = nD
                nv = bM >= sl if nt else bM <= sl
                kV = bM <= tp if nt else bM >= tp
                gM = bM <= (oN if gX else tp) if nt else bM >= (oN if gX else tp)
                if nv:
                    self.log_yaz(f"🛑 [STOP-LOSS / BE] {O} ({bt}) stop seviyesine ({sl}) ulaştı, kapatılıyor...")
                    self._emir_kapat(J, b0, bt, Y, ig)
                    eB = (bZ - bM if nt else bM - bZ) * Y
                    W += eB
                    if ig and b0 == "future":
                        S += eB
                    _ig_kaydet(J, b0, bt, bZ, bM, Y, eB, nu, "STOP-LOSS / BE" if bq.get("kismi_tp_alindi") else "STOP-LOSS", bq.get("ozet", ""))
                    acik_islemler[O] = None
                    _ak_kaydet()
                    tg_bildir(f"🛑 <b>POZİSYON KAPANDI (STOP-LOSS / BE)</b>\n📌 <b>Parite:</b> {O} ({bt})\n📉 <b>Sonuç:</b> {eB:+.2f} USDT")
                    continue
                if KISMI_KAR_AL_AKTIF and (not gX) and kV:
                    try:
                        fe = F(ja.amount_to_precision(J, Y * 0.5))
                        jA = F(ja.amount_to_precision(J, Y - fe))
                    except Exception:
                        fe = R(Y * 0.5, 6)
                        jA = R(Y - fe, 6)
                    if fe > 0 and jA > 0:
                        self.log_yaz(f"🎯 [3R KISMİ KÂR AL] {O} ({bt}) {tp} hedefine ulaştı! %50 ({fe}) kapatılıyor ve SL girişe (BE) çekiliyor...")
                        self._emir_kapat(J, b0, bt, fe, ig)
                        try:
                            rU = F(ja.price_to_precision(J, bZ))
                        except Exception:
                            rU = bZ
                        ip = A(bM - bZ) * fe
                        W += ip
                        if ig and b0 == "future":
                            S += ip
                        _ig_kaydet(J, b0, bt, bZ, bM, fe, ip, nu, "3R %50 KISMİ KÂR AL", bq.get("ozet", ""))
                        bq.update({"miktar": jA, "sl": rU, "tp": oN, "risk_usdt": 0.0, "kismi_tp_alindi": True})
                        _ak_kaydet()
                        tg_bildir(f"🎯 <b>3R KISMİ TAKE-PROFIT (%50) & BREAK-EVEN!</b>\n📌 <b>Parite:</b> {O} ({bt})\n💰 <b>Realize Kâr:</b> +{ip:.2f} USDT (%{nu:+.2f})\n🛡️ <b>Yeni SL:</b> {rU} (0 Risk) | 🎯 <b>Yeni Hedef:</b> {oN}")
                        continue
                if gM:
                    self.log_yaz(f"🏆 [TAKE-PROFIT] {O} ({bt}) hedefe ulaştı! Pozisyon kapatılıyor...")
                    self._emir_kapat(J, b0, bt, Y, ig)
                    ip = A(bM - bZ) * Y
                    W += ip
                    if ig and b0 == "future":
                        S += ip
                    _ig_kaydet(J, b0, bt, bZ, bM, Y, ip, nu, "NİHAİ TAKE-PROFIT", bq.get("ozet", ""))
                    acik_islemler[O] = None
                    _ak_kaydet()
                    tg_bildir(f"🏆 <b>TAKE-PROFIT ({b0.upper()}) GERÇEKLEŞTİ!</b>\n📌 <b>Parite:</b> {O} ({bt})\n💵 <b>Giriş:</b> {bZ} | 🚀 <b>Çıkış:</b> {bM}\n💰 <b>Net Kâr:</b> +{ip:.2f} USDT (%{nu:+.2f})")
            V, T = bakiye_getir()
            _ak_kaydet()
            self.arayuzu_guncelle()
        except Exception as e:
            self.log_yaz(f"⚠️ Senkronizasyon hatası: {e}")
        finally:
            self._senk_calisiyor = False

    def isleme_gir(self, J, aU, P, al, mN=0, bG="", K=None, D=None):
        global acik_islemler, V, T
        hd = D if D else "spot" if PIYASA_MODU == "spot" else "future"
        ja, jb = (veri_ist(hd), emir_ist(hd))
        O = anahtar_yap(J, hd)
        if acik_islemler.get(O) is not None or aU not in ("LONG", "SHORT") or (hd == "spot" and aU == "SHORT"):
            return
        if sum((1 for v in acik_islemler.values() if I(v, dict))) >= a4:
            return
        H_kontrol = analiz_hafizasi.get(O) or analiz_hafizasi.get(J) or {}
        kFlt_kontrol = H_kontrol.get("konum_meta", {})
        if not kFlt_kontrol.get("htf_zorunlu_bolge_onay", False) or not kFlt_kontrol.get("ltf_herhangi_tetik", False) or kFlt_kontrol.get("saglanan_giris_sart_sayisi", 0) < 1:
            return
        try:
            eO = anlik_fiyat_getir(J, hd)
            P = eO if eO else P
        except Exception:
            pass
        if (aU == "LONG" and al >= P) or (aU == "SHORT" and al <= P):
            return
        Y, fk, kF = dinamik_miktar_hesapla(J, P, al, hd, mN)
        if not Y or Y <= 0:
            return
        mO = -1.0 if aU == "SHORT" else 1.0
        try:
            f2 = F(ja.price_to_precision(J, al))
        except Exception:
            f2 = R(al, 6)
        iU_gercek = M(A(P - f2), P * aW)
        Y, fk, kF = dinamik_miktar_hesapla(J, P, f2, hd, mN)
        if not Y or Y <= 0:
            return
        pK = M(NIHAI_TP_RR, RISK_ODUL_ORANI + 1.0)
        try:
            eo = F(ja.price_to_precision(J, M(1e-06, P + mO * iU_gercek * RISK_ODUL_ORANI)))
            gb = F(ja.price_to_precision(J, M(1e-06, P + mO * iU_gercek * pK)))
        except Exception:
            eo = R(M(1e-06, P + mO * iU_gercek * RISK_ODUL_ORANI), 6)
            gb = R(M(1e-06, P + mO * iU_gercek * pK), 6)
        mP = False
        try:
            if hd == "future":
                if TESTNET_AKTIF:
                    mP = True
                else:
                    for fn in [lambda: jb.set_leverage(KALDIRAC, J), lambda: jb.set_margin_mode(MARJIN_TIPI, J)]:
                        try:
                            fn()
                        except Exception:
                            pass
                    if aU == "LONG":
                        jb.create_market_buy_order(J, Y)
                        try:
                            jb.create_order(J, "STOP_MARKET", "sell", Y, None, {"stopPrice": f2, "reduceOnly": True})
                        except Exception:
                            pass
                    else:
                        jb.create_market_sell_order(J, Y)
                        try:
                            jb.create_order(J, "STOP_MARKET", "buy", Y, None, {"stopPrice": f2, "reduceOnly": True})
                        except Exception:
                            pass
            else:
                try:
                    jb.create_market_buy_order(J, Y)
                    try:
                        jb.create_order(J, "STOP_LOSS_LIMIT", "sell", Y, F(ja.price_to_precision(J, f2 * 0.998)), {"stopPrice": f2})
                    except Exception:
                        pass
                except Exception as qG:
                    if TESTNET_AKTIF:
                        mP = True
                    else:
                        raise qG
            u_ana = int(kFlt_kontrol.get("htf_bolge_sayisi", kFlt_kontrol.get("saglanan_giris_sart_sayisi", 1)))
            u_alt = int(kFlt_kontrol.get("htf_safe_puan", 80))
            k_uyum_kisa = f"Safe:{u_ana}/8 ({u_alt}p)"
            bG_kural = f"[{k_uyum_kisa}] {bG}" if k_uyum_kisa not in str(bG) else bG
            acik_islemler[O] = {
                "sembol": J, "yon": aU, "piyasa": hd, "simule": mP,
                "kaldirac": KALDIRAC if hd == "future" else 1,
                "giris": P, "anlik": P, "pnl_usdt": 0.0, "pnl_yuzde": 0.0,
                "marjin_usdt": R(fk, 2), "sl": f2, "ilk_sl": f2, "tp": eo, "tp_nihai": gb,
                "miktar": Y, "risk_usdt": kF, "kismi_tp_alindi": False,
                "ozet": bG_kural, "giris_kurallari": K or [],
                "uygun_kural_sayisi": u_ana, "uygun_alt_kural_sayisi": u_alt,
                "kural_uyum_kisa": k_uyum_kisa, "risk_seviyesi": AKTIF_RISK_SEVIYESI,
                "islem_modu": ISLEM_TARZI_MODU,
                "htf_periyot": H_kontrol.get("htf_periyot", HTF_PERIYOT),
                "mtf_periyot": H_kontrol.get("mtf_periyot", MTF_PERIYOT),
                "ltf_periyot": H_kontrol.get("ltf_periyot", LTF_PERIYOT),
                "mtf_sablonu": H_kontrol.get("mtf_sablonu", AKTIF_MTF_SABLONU)
            }
            _ak_kaydet()
            V, T = bakiye_getir()
            self.arayuzu_guncelle()
            ng = "🟢" if aU == "LONG" else "🔴"
            rw = f"{KALDIRAC}x Vadeli{(' [Canlı Demo]' if mP else '')}" if hd == "future" else f"Spot{(' [Canlı Demo]' if mP else '')}"
            rx = kF * RISK_ODUL_ORANI
            self.log_yaz(f"{ng} YENİ İŞLEM [{rw}]: {O} {aU} | {k_uyum_kisa} | Skor: {mN}/100 | Marjin: {fk:.1f}$ | Risk: -{kF:.2f}$ | Stop: {f2} | Hedef: +{rx:.2f}$")
            tg_bildir(f"{ng} <b>MAHŞERİN 4 ATLISI İŞLEM AÇILDI ({aU} - {rw})</b>\n📌 <b>Parite:</b> {O} | 🔥 <b>Skor:</b> {mN}/100\n✅ <b>Kural:</b> {k_uyum_kisa}\n🧩 <b>Özet:</b> {bG_kural}\n💵 <b>Giriş:</b> {P} | 🛡️ <b>Stop:</b> {f2} (-{kF:.2f}$)\n🎯 <b>TP1 ({RISK_ODUL_ORANI}R):</b> {eo} (+{rx:.2f}$) | 🚀 <b>Nihai:</b> {gb}")
        except Exception as e:
            self.log_yaz(f"⚠️ {O} Emir Hatası: {e}")

    def bot_ana_dongu(self):
        global aQ, V, T, bE
        try:
            if aC is None or aw is None:
                borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
            _SON_TARAMA_KALP_ATISI[0] = time.time()
            pariteleri_yukle(self.log_yaz)
            V, T = bakiye_getir()
            if aQ == 0:
                aQ = T
            self.log_yaz(f"✅ Borsa bağlantısı hazır. Bakiye: {T:.2f} USDT (Spot: {ay:.2f}$ | Vadeli: {aq:.2f}$) | Taranacak Parite: {L(ab)}")
        except Exception as e:
            self.log_yaz(f"⚠️ Borsa bağlantı hatası: {e}")
        while bot_calisiyor and not self._kapaniyor:
            try:
                self.pozisyonlari_senkronize_et()
                jr = "spot" if PIYASA_MODU == "spot" else "future"
                for js in ("BTC/USDT", "ETH/USDT"):
                    if not bot_calisiyor:
                        break
                    try:
                        veri_cek(js, MTF_PERIYOT, 70, jr)
                        veri_cek(js, LTF_PERIYOT, 70, jr)
                    except Exception:
                        pass

                def _tarama_oncelik_anahtari(item):
                    j_s, b_s = item
                    o_s = anahtar_yap(j_s, b_s)
                    h_s = analiz_hafizasi.get(o_s) or analiz_hafizasi.get(j_s)
                    if not h_s:
                        return (2, (0, 0, 0, 0), 0, (0, 0, 0, 0), 0, 0)
                    km_s = h_s.get("konum_meta", {})
                    onc_say = int(km_s.get("htf_oncelikli_bolge_sayisi", 0))
                    ikn_say = int(km_s.get("htf_ikincil_bolge_sayisi", 0))
                    onc_vek = tuple(km_s.get("oncelik_vektor", (0, 0, 0, 0)))
                    ikn_vek = tuple(km_s.get("ikincil_vektor", (0, 0, 0, 0)))
                    kademe = 3 if onc_say > 0 else (1 if ikn_say > 0 else 0)
                    return (kademe, onc_vek, onc_say, ikn_vek, ikn_say, int(h_s.get("skor", 0)))

                qu = sorted(list(ab), key=_tarama_oncelik_anahtari, reverse=True)
                oncelikli_girilen_sayisi = 0
                adaylar_1_qml, adaylar_2_ob, adaylar_3_fresh, adaylar_4_ote, ikincil_bolge_adaylari = [], [], [], [], []
                for bu, (J, b0) in enumerate(qu, start=1):
                    if not bot_calisiyor:
                        break
                    try:
                        _SON_TARAMA_KALP_ATISI[0] = time.time()
                        bE = bu
                        O = anahtar_yap(J, b0)
                        bS = veri_cek(J, HTF_PERIYOT, 250, b0)
                        bw = veri_cek(J, MTF_PERIYOT, 250, b0)
                        aY = veri_cek(J, LTF_PERIYOT, 250, b0)
                        jB = _f(aY, "close", -1)
                        H = mahserin_4_atlisi_confluence_analizi(J, bS, bw, aY, b0)
                        km_tarama = H.get("konum_meta", {})
                        onc_onay = bool(km_tarama.get("htf_oncelikli_bolge_onay", False) and km_tarama.get("oncelikli_giris_sart_sayisi", 0) >= 1)
                        ikn_onay = bool(km_tarama.get("htf_ikincil_bolge_onay", False) and km_tarama.get("ikincil_giris_sart_sayisi", 0) >= 1)
                        onc_vek_t = tuple(km_tarama.get("oncelik_vektor", (0, 0, 0, 0)))
                        ikn_vek_t = tuple(km_tarama.get("ikincil_vektor", (0, 0, 0, 0)))
                        if H["sinyal"] in ("LONG", "SHORT") and acik_islemler.get(O) is None:
                            if onc_onay:
                                kayit_onc = (onc_vek_t, int(km_tarama.get("htf_bolge_sayisi", 1)), int(H["skor"]), J, b0, O, H)
                                if km_tarama.get("sart4_htf_qml_giris", False):
                                    self.isleme_gir(J, H["sinyal"], H["giris"], H["sl"], H["skor"], f"[1.ÖNCELİK #1: QML] {H['ozet']}", H["detayli_kurallar"], b0)
                                    if I(acik_islemler.get(O), dict):
                                        oncelikli_girilen_sayisi += 1
                                    else:
                                        adaylar_1_qml.append(kayit_onc)
                                elif km_tarama.get("sart2_htf_ob_giris", False):
                                    adaylar_2_ob.append(kayit_onc)
                                elif km_tarama.get("sart1_htf_poi_giris", False):
                                    adaylar_3_fresh.append(kayit_onc)
                                elif km_tarama.get("sart3_htf_ote_giris", False):
                                    adaylar_4_ote.append(kayit_onc)
                            elif ikn_onay:
                                ikincil_bolge_adaylari.append((ikn_vek_t, int(km_tarama.get("htf_ikincil_bolge_sayisi", 1)), int(H["skor"]), J, b0, O, H))
                        a1[O] = {
                            "fiyat": jB, "4h": H["yon_4h"], "1h": H["yon_1h"], "ana_yon": H["ana_yon"],
                            "skor": f"{H['skor']}/100",
                            "ltf": f"AÇIK ({acik_islemler[O]['yon']})" if I(acik_islemler.get(O), dict) else H["sinyal"],
                            "setup_detay": H["ozet"],
                            "oncelikli_bolge": int(km_tarama.get("htf_oncelikli_bolge_sayisi", 0)),
                            "oncelik_vektor": onc_vek_t, "ikincil_vektor": ikn_vek_t,
                            "safe_sayisi": int(km_tarama.get("htf_bolge_sayisi", 0))
                        }
                        if I(acik_islemler.get(O), dict):
                            acik_islemler[O]["anlik"] = jB
                        if bu % 4 == 0:
                            self.durum_guncelle(f"Taranıyor: {bu}/{L(qu)} ({HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT}) 🟢", "#4ade80")
                            self.arayuzu_guncelle()
                        if bu % 20 == 0:
                            self.pozisyonlari_senkronize_et()
                            try:
                                gc.collect()
                            except Exception:
                                pass
                        time.sleep(0.08 if ISLEM_TARZI_MODU == "Scalp" else 0.25)
                    except Exception as e:
                        self.log_yaz(f"⚠️ {J} ({b0.upper()}) tarama hatası: {e}")
                        time.sleep(0.35)

                for sira_etiket, aday_grup in [
                    ("1.ÖNCELİK #1: QML", adaylar_1_qml),
                    ("2.ÖNCELİK #2: OB", adaylar_2_ob),
                    ("3.ÖNCELİK #3: Fresh Arz/Talep", adaylar_3_fresh),
                    ("4.ÖNCELİK #4: OTE", adaylar_4_ote)
                ]:
                    if not bot_calisiyor or not aday_grup:
                        continue
                    aday_grup.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
                    for _, _, _, J_pr, b0_pr, O_pr, H_pr in aday_grup:
                        if not bot_calisiyor:
                            break
                        if sum((1 for v in acik_islemler.values() if I(v, dict))) >= a4:
                            break
                        if acik_islemler.get(O_pr) is None:
                            self.isleme_gir(J_pr, H_pr["sinyal"], H_pr["giris"], H_pr["sl"], H_pr["skor"], f"[{sira_etiket}] {H_pr['ozet']}", H_pr["detayli_kurallar"], b0_pr)
                            if I(acik_islemler.get(O_pr), dict):
                                oncelikli_girilen_sayisi += 1

                if oncelikli_girilen_sayisi == 0 and ikincil_bolge_adaylari and bot_calisiyor:
                    ikincil_bolge_adaylari.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
                    self.log_yaz(f"🧭 [2. KADEME HTF BÖLGE TARAMASI] {L(ikincil_bolge_adaylari)} parite değerlendiriliyor...")
                    for _, _, _, J_ik, b0_ik, O_ik, H_ik in ikincil_bolge_adaylari:
                        if not bot_calisiyor:
                            break
                        if sum((1 for v in acik_islemler.values() if I(v, dict))) >= a4:
                            break
                        if acik_islemler.get(O_ik) is None:
                            self.isleme_gir(J_ik, H_ik["sinyal"], H_ik["giris"], H_ik["sl"], H_ik["skor"], f"[2.KADEME HTF: BOS/CHoCH/ITZ/Magic] {H_ik['ozet']}", H_ik["detayli_kurallar"], b0_ik)

                bekle_sn = 3 if ISLEM_TARZI_MODU == "Scalp" else 10
                self.log_yaz(f"🔄 Tarama ({L(qu)} parite | Mod: {ISLEM_TARZI_MODU}) tamamlandı. {bekle_sn}sn sonra yeniden taranacak...")
                for _ in G(bekle_sn):
                    if not bot_calisiyor:
                        break
                    time.sleep(1)
            except BaseException as e:
                if not bot_calisiyor or self._kapaniyor:
                    break
                self.log_yaz(f"🛡️ Döngü hatası izole edildi: {e}")
                time.sleep(3)


# ==============================================================================
# FLET MOBİL ARAYÜZÜ (ANDROID APK & DOKUNMATİK EKRAN UYUMLU)
# ==============================================================================
def main(page: ft.Page):
    global _AKTIF_PAGE_REF
    _AKTIF_PAGE_REF = page
    page.title = "Alfa Trade Club — Mahşerin 4 Atlısı (Mobil APK)"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f172a"
    page.padding = 0
    page.spacing = 0

    def _yasam_dongusu_degisti(e):
        durum_str = str(getattr(e, "data", "") or getattr(e, "state", "")).lower()
        if any(x in durum_str for x in ("pause", "inactive", "hidden", "detach")):
            _ARKA_PLANDA_MI[0] = True
            _ak_kaydet()
        elif "resume" in durum_str:
            _ARKA_PLANDA_MI[0] = False
            try:
                _ekrani_yenile("force")
            except Exception:
                pass

    page.on_app_lifecycle_state_change = _yasam_dongusu_degisti

    yerel_port = yerel_grafik_sunucusu_baslat()
    secili_parite_state = {"anahtar": "FUT:BTC/USDT", "tf": "4h"}

    # --- ÜST ÖZET KARTLARI ---
    lbl_portfoy = ft.Text("0.00 $", size=15, weight=ft.FontWeight.BOLD, color="#38bdf8")
    lbl_serbest = ft.Text("Serbest: 0.00 $", size=11, color="#94a3b8")
    lbl_acik_pnl = ft.Text("+0.00 $ (%0.00)", size=15, weight=ft.FontWeight.BOLD, color="#4ade80")
    lbl_oturum_pnl = ft.Text("Oturum: +0.00 $ (00:00:00)", size=11, color="#22d3ee")
    lbl_net_pnl = ft.Text("+0.00 $", size=15, weight=ft.FontWeight.BOLD, color="#fbbf24")
    lbl_aktif_say = ft.Text(f"Açık: 0 / {a4}", size=11, color="#c084fc")
    lbl_durum_bar = ft.Text("Durum: Beklemede ⏸", size=12, weight=ft.FontWeight.BOLD, color="#f59e0b")

    def mini_kart(baslik, ana_lbl, alt_lbl, kenar_renk):
        return ft.Container(
            content=ft.Column([
                ft.Text(baslik, size=10, weight=ft.FontWeight.BOLD, color="#94a3b8"),
                ana_lbl,
                alt_lbl
            ], spacing=2, tight=True),
            bgcolor="#1e293b",
            border=ft.border.all(1, kenar_renk),
            border_radius=10,
            padding=8,
            expand=True
        )

    ust_kartlar_row = ft.Row([
        mini_kart("💰 PORTFÖY", lbl_portfoy, lbl_serbest, "#3b82f6"),
        mini_kart("📈 AÇIK PNL", lbl_acik_pnl, lbl_oturum_pnl, "#10b981"),
        mini_kart("🏆 NET K/Z", lbl_net_pnl, lbl_aktif_say, "#f59e0b"),
    ], spacing=6)

    # --- KONTROL BUTONLARI ---
    btn_baslat = ft.ElevatedButton(
        "▶ Başlat",
        bgcolor="#10b981",
        color="#ffffff",
        expand=True,
        on_click=lambda e: _bot_baslat_tik()
    )
    btn_durdur = ft.ElevatedButton(
        "⏹ Durdur",
        bgcolor="#ef4444",
        color="#ffffff",
        disabled=True,
        expand=True,
        on_click=lambda e: _bot_durdur_tik()
    )
    lbl_ota_surum = ft.Text(f"📦 Sürüm: {AKTIF_OTA_SURUM_BILGISI}", size=10, color="#a78bfa", weight=ft.FontWeight.BOLD)

    def _tek_tus_ota_tik(e):
        global GITHUB_REPO_ADRESI, GITHUB_TOKEN
        GITHUB_REPO_ADRESI = (tf_gh_repo.value or GITHUB_REPO_ADRESI or "emrhozbr/bot").strip()
        if tf_gh_tok.value and tf_gh_tok.value.strip():
            GITHUB_TOKEN = tf_gh_tok.value.strip()
        _api_kaydet_tam()
        lbl_durum_bar.value = "⏳ OTA Güncelleniyor..."
        lbl_durum_bar.color = "#fde047"
        lbl_ayar_durum.value = "⏳ GitHub üzerinden en güncel sürüm (botv4.0.9+ / main.py) ve PC ayarları indiriliyor..."
        lbl_ayar_durum.color = "#fde047"
        page.update()
        def _ota_bg():
            bulut_durum_cek(zorla=True)
            ok, msg = ota_strateji_guncelle(GITHUB_REPO_ADRESI, GITHUB_TOKEN)
            motor.log_yaz(msg)
            motor.durum_guncelle("OTA Güncellendi ✅" if ok else "OTA Uyarı ⚠️", "#4ade80" if ok else "#f87171")
            lbl_ayar_durum.value = msg
            lbl_ayar_durum.color = "#4ade80" if ok else "#f87171"
            lbl_ota_surum.value = f"📦 Sürüm: {AKTIF_OTA_SURUM_BILGISI}"
            if ok:
                try:
                    dd_mtf_sablon.options = [ft.dropdown.Option(k) for k in MTF_SABLONLARI.keys()]
                    dd_risk_seviye.options = [ft.dropdown.Option(k) for k in RISK_SEVIYESI_SECENEKLERI.keys()]
                    dd_stop_modu.options = [ft.dropdown.Option(k) for k in STOP_BELIRLEME_SECENEKLERI]
                except Exception:
                    pass
            _ekrani_yenile("force")
        threading.Thread(target=_ota_bg, daemon=True).start()

    btn_senk = ft.ElevatedButton(
        "☁️ Eşitle",
        bgcolor="#3b82f6",
        color="#ffffff",
        expand=True,
        on_click=lambda e: threading.Thread(target=lambda: (bulut_durum_cek(True), bulut_durum_gonder(True), motor.pozisyonlari_senkronize_et()), daemon=True).start()
    )
    btn_ota = ft.ElevatedButton(
        "⚡ OTA Güncelle",
        bgcolor="#8b5cf6",
        color="#ffffff",
        expand=True,
        on_click=_tek_tus_ota_tik
    )

    ust_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("🚀 ALFA TRADE CLUB (4 ATLI PA)", size=13, weight=ft.FontWeight.BOLD, color="#f8fafc"),
                    ft.Row([lbl_ota_surum, lbl_durum_bar], spacing=8, wrap=True)
                ], spacing=2, expand=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ust_kartlar_row,
            ft.Row([btn_baslat, btn_durdur], spacing=6),
            ft.Row([btn_senk, btn_ota], spacing=6)
        ], spacing=6),
        bgcolor="#181825",
        padding=ft.padding.only(left=10, right=10, top=34, bottom=10),
        border=ft.border.only(bottom=ft.BorderSide(1, "#334155"))
    )

    # --- SEKME 1: AÇIK İŞLEMLER LİSTESİ ---
    lv_acik_islemler = ft.ListView(expand=True, spacing=8, padding=10)

    # --- SEKME 2: BORSA TARAMASI LİSTESİ ---
    lbl_tarama_info = ft.Text(
        f"🔍 MTF: {HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT} | Eşik: {MIN_CONFLUENCE_SKORU}+ Puan | Öncelik: 1.QML > 2.OB > 3.Fresh > 4.OTE",
        size=11, color="#38bdf8", weight=ft.FontWeight.BOLD
    )
    lv_tarama = ft.ListView(expand=True, spacing=6, padding=10)

    # --- SEKME 3: KARNE, PINE v6 & CANLI TV GRAFİK ---
    dd_karne_parite = ft.Dropdown(
        label="İncelenecek Parite Seçin",
        options=[ft.dropdown.Option( f"FUT:{s}") for s in am],
        value="FUT:BTC/USDT",
        expand=True,
        bgcolor="#1e293b",
        border_color="#3b82f6"
    )
    txt_karne_detay = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=16,
        text_size=11,
        bgcolor="#11111b",
        color="#4ade80",
        border_color="#334155"
    )
    txt_pine_kod = ft.TextField(
        multiline=True,
        read_only=True,
        min_lines=8,
        max_lines=14,
        text_size=10,
        bgcolor="#090d16",
        color="#38bdf8",
        border_color="#334155"
    )
    lbl_pine_bildirim = ft.Text("Canlı analiz veya Pine v6 için yukarıdan zaman dilimi seçin.", size=11, color="#fde047")

    img_canli_grafik = ft.Image(src_base64="", fit=ft.ImageFit.CONTAIN, width=900, height=275)
    kutu_canli_grafik = ft.Container(
        content=ft.InteractiveViewer(
            min_scale=0.8,
            max_scale=5.0,
            content=img_canli_grafik
        ),
        bgcolor="#0f172a",
        border_radius=8,
        border=ft.border.all(1, "#334155"),
        height=285,
        padding=4,
        visible=False
    )

    def _parite_karne_ve_pine_yukle(tf_secim="4h", canli_zorla=False, tv_ac=False):
        secili_parite_state["tf"] = tf_secim
        O = dd_karne_parite.value or secili_parite_state["anahtar"] or "FUT:BTC/USDT"
        secili_parite_state["anahtar"] = O
        lbl_pine_bildirim.value = f"⏳ {O} [{tf_secim.upper()}] verileri, canlı grafik ve PA kutuları hazırlanıyor..."
        page.update()

        def _arka_plan():
            try:
                H = analiz_hafizasi.get(O) or {}
                J = H.get("sembol", str(O).split(":", 1)[-1])
                D = H.get("piyasa", "spot" if str(O).startswith("SPOT:") else "future")
                if canli_zorla or not H or H.get("df_15m_full") is None:
                    H = pine_icin_4h_1h_5m_veri_hazirla(J, D, H, O)
                    analiz_hafizasi[O] = H
                svg_b64 = mobil_canli_svg_grafik_uret(O, tf_secim, H)
                if svg_b64:
                    img_canli_grafik.src_base64 = svg_b64
                    kutu_canli_grafik.visible = True
                karne_metni = _karne_checklist_olustur(H, html_mi=False)
                p1, p2, p3, p4 = H.get("atli_puanlar", (0, 0, 0, 0))
                ek_bilgi = (
                    f"📌 PARİTE: {O} | SİNYAL: {H.get('sinyal', 'BEKLE')} ({H.get('skor', 0)}/100)\n"
                    f"🏇 4 Atlı: 1.Atlı:{p1}/25 | 2.Atlı:{p2}/25 | 3.Atlı:{p3}/25 | 4.Atlı:{p4}/25\n"
                    f"🎯 Giriş Modeli: {H.get('giris_modeli', '-')}\n"
                    f"💵 Giriş: {_fmt_f(H.get('giris', 0))} | 🛡️ Stop: {_fmt_f(H.get('sl', 0))}\n\n"
                    f"✅ DETAYLI KURALLAR:\n" + "\n".join(f"• {k}" for k in H.get("detayli_kurallar", [])[:18])
                )
                txt_karne_detay.value = karne_metni + "\n" + ek_bilgi
                pine_str = pine_script_uret_4h_1h_5m(O, tf_secim, H)
                txt_pine_kod.value = pine_str
                if tv_ac:
                    dosya_yolu, _ = tradingview_kopyala_yapistirsiz_html_ac(O, tf_secim, H)
                    dosya_adi = os.path.basename(dosya_yolu)
                    port_no = yerel_port or yerel_grafik_sunucusu_baslat()
                    if port_no:
                        hedef_url = f"http://127.0.0.1:{port_no}/{dosya_adi}?t={int(time.time())}"
                        page.launch_url(hedef_url)
                    lbl_pine_bildirim.value = f"🚀 {O} [{tf_secim.upper()}] Canlı Grafik hem uygulama içinde hem tarayıcıda açıldı!"
                else:
                    lbl_pine_bildirim.value = f"✅ {O} [{tf_secim.upper()}] Canlı PA Grafiği, Karne ve Pine Script v6 hazır!"
            except Exception as ex:
                lbl_pine_bildirim.value = f"⚠️ Hesaplama hatası: {ex}"
            try:
                page.update()
            except Exception:
                pass

        threading.Thread(target=_arka_plan, daemon=True).start()

    def _pine_kopyala_tik(e):
        if txt_pine_kod.value:
            page.set_clipboard(txt_pine_kod.value)
            lbl_pine_bildirim.value = f"📋 {secili_parite_state['anahtar']} [{secili_parite_state['tf'].upper()}] Pine Script v6 panoya kopyalandı!"
            page.update()

    dd_karne_parite.on_change = lambda e: _parite_karne_ve_pine_yukle(secili_parite_state["tf"], canli_zorla=False)

    sekme_karne_icerik = ft.Container(
        content=ft.Column([
            ft.Row([
                dd_karne_parite,
                ft.ElevatedButton("🔄 Canlı Analiz", bgcolor="#0ea5e9", color="#ffffff", on_click=lambda e: _parite_karne_ve_pine_yukle(secili_parite_state["tf"], canli_zorla=True))
            ], spacing=6),
            ft.Row([
                ft.ElevatedButton("🏛️ HTF Grafik & Pine", bgcolor="#2563eb", color="#ffffff", expand=True, on_click=lambda e: _parite_karne_ve_pine_yukle("4h", False, False)),
                ft.ElevatedButton("🧭 MTF Grafik & Pine", bgcolor="#7c3aed", color="#ffffff", expand=True, on_click=lambda e: _parite_karne_ve_pine_yukle("1h", False, False)),
                ft.ElevatedButton("🎯 LTF Grafik & Pine", bgcolor="#0d9488", color="#ffffff", expand=True, on_click=lambda e: _parite_karne_ve_pine_yukle("5m", False, False)),
            ], spacing=6),
            ft.Row([
                ft.ElevatedButton("🚀 Tam Ekran TV Grafiği Aç", bgcolor="#10b981", color="#ffffff", expand=True, on_click=lambda e: _parite_karne_ve_pine_yukle(secili_parite_state["tf"], False, True)),
                ft.ElevatedButton("📋 Pine Kopyala", bgcolor="#eab308", color="#11111b", expand=True, on_click=_pine_kopyala_tik),
            ], spacing=6),
            lbl_pine_bildirim,
            kutu_canli_grafik,
            ft.Text("📋 STRATEJİ & SEVİYE KARNESİ CHECK-LIST (8 HTF BÖLGE):", size=12, weight=ft.FontWeight.BOLD, color="#38bdf8"),
            txt_karne_detay,
            ft.Text("🌲 PINE SCRIPT v6 KODU:", size=12, weight=ft.FontWeight.BOLD, color="#fde047"),
            txt_pine_kod
        ], scroll=ft.ScrollMode.AUTO, spacing=8),
        padding=10,
        expand=True
    )

    # --- SEKME 4: AYARLAR & BINANCE API ---
    dd_piyasa = ft.Dropdown(
        label="Piyasa Modu",
        options=[
            ft.dropdown.Option("her_ikisi", "HER İKİSİ (SPOT + VADELİ)"),
            ft.dropdown.Option("future", "VADELİ (FUTURES)"),
            ft.dropdown.Option("spot", "SPOT")
        ],
        value=PIYASA_MODU,
        bgcolor="#1e293b"
    )
    dd_ag = ft.Dropdown(
        label="İşlem Ağı Modu",
        options=[
            ft.dropdown.Option("testnet", "TESTNET / CANLI DEMO (Sanal Bakiye)"),
            ft.dropdown.Option("mainnet", "GERÇEK (MAINNET - CANLI İŞLEM)")
        ],
        value="testnet" if TESTNET_AKTIF else "mainnet",
        bgcolor="#1e293b"
    )
    dd_mtf_sablon = ft.Dropdown(
        label="MTF Zaman Dilimi Şablonu",
        options=[ft.dropdown.Option(k) for k in MTF_SABLONLARI.keys()],
        value=AKTIF_MTF_SABLONU,
        bgcolor="#1e293b"
    )
    dd_risk_seviye = ft.Dropdown(
        label="İşlem Risk & Confluence Seviyesi",
        options=[ft.dropdown.Option(k) for k in RISK_SEVIYESI_SECENEKLERI.keys()],
        value=AKTIF_RISK_SEVIYESI,
        bgcolor="#1e293b"
    )
    dd_stop_modu = ft.Dropdown(
        label="🛡️ Stop Noktası Belirleme Modu (v4.0.3)",
        options=[ft.dropdown.Option(k) for k in STOP_BELIRLEME_SECENEKLERI],
        value=STOP_BELIRLEME_MODU,
        bgcolor="#1e293b"
    )
    dd_marjin_tipi = ft.Dropdown(
        label="Vadeli Marjin Tipi",
        options=[ft.dropdown.Option("ISOLATED"), ft.dropdown.Option("CROSSED")],
        value=MARJIN_TIPI,
        bgcolor="#1e293b"
    )
    tf_marjin = ft.TextField(label="Maks Marjin ($)", value=str(MAKS_MARJIN_USDT), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")
    tf_kaldirac = ft.TextField(label="Kaldıraç (x)", value=str(KALDIRAC), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")
    tf_risk = ft.TextField(label="İşlem Başı Risk ($)", value=str(ISLEM_BASI_RISK_USDT), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")
    tf_rr = ft.TextField(label="TP1 Risk/Ödül (RR)", value=str(RISK_ODUL_ORANI), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")
    tf_min_skor = ft.TextField(label="Min 4 Atlı Skoru", value=str(MIN_CONFLUENCE_SKORU), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")
    tf_limit = ft.TextField(label="Parite Limiti (0=Tümü)", value=str(ae), keyboard_type=ft.KeyboardType.NUMBER, expand=True, bgcolor="#1e293b")

    tf_api_key = ft.TextField(label="Binance API Key", value=API_KEY, bgcolor="#1e293b")
    tf_api_sec = ft.TextField(label="Binance Secret Key", value=API_SECRET, password=True, can_reveal_password=True, bgcolor="#1e293b")
    tf_tg_tok = ft.TextField(label="Telegram Bot Token", value=TELEGRAM_TOKEN, bgcolor="#1e293b")
    tf_tg_id = ft.TextField(label="Telegram Chat ID", value=TELEGRAM_CHAT_ID, bgcolor="#1e293b")
    tf_gh_repo = ft.TextField(label="GitHub Repo (OTA & Bulut Senk: kullanici/repo)", value=GITHUB_REPO_ADRESI, bgcolor="#1e293b")
    tf_gh_tok = ft.TextField(label="GitHub Token (Cihazlar Arası Senk & Private Repo İçin)", value=GITHUB_TOKEN, password=True, can_reveal_password=True, bgcolor="#1e293b")
    lbl_ayar_durum = ft.Text("Ayarlar hazır.", size=12, color="#4ade80")

    def _risk_secim_degisti(e):
        sec = dd_risk_seviye.value
        if sec in RISK_SEVIYESI_SECENEKLERI and not sec.startswith("Özel"):
            sk, _ = RISK_SEVIYESI_SECENEKLERI[sec]
            tf_min_skor.value = str(sk)
            page.update()

    dd_risk_seviye.on_change = _risk_secim_degisti

    def _ui_ayar_kontrollerini_guncelle():
        try:
            dd_piyasa.value = PIYASA_MODU
            dd_ag.value = "testnet" if TESTNET_AKTIF else "mainnet"
            dd_mtf_sablon.value = AKTIF_MTF_SABLONU
            dd_risk_seviye.value = AKTIF_RISK_SEVIYESI
            dd_stop_modu.value = STOP_BELIRLEME_MODU
            dd_marjin_tipi.value = MARJIN_TIPI
            tf_marjin.value = str(MAKS_MARJIN_USDT)
            tf_kaldirac.value = str(KALDIRAC)
            tf_risk.value = str(ISLEM_BASI_RISK_USDT)
            tf_rr.value = str(RISK_ODUL_ORANI)
            tf_min_skor.value = str(MIN_CONFLUENCE_SKORU)
            tf_limit.value = str(ae)
            lbl_tarama_info.value = f"🔍 MTF: {HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT} | Eşik: {MIN_CONFLUENCE_SKORU}+ Puan | Kaldıraç: {KALDIRAC}x"
            page.update()
        except Exception:
            pass
    globals()["_UI_AYAR_YENILE_FN"] = _ui_ayar_kontrollerini_guncelle

    def _ayarlari_kaydet_tik(e):
        global PIYASA_MODU, TESTNET_AKTIF, MARJIN_TIPI, KALDIRAC, MAKS_MARJIN_USDT
        global ISLEM_BASI_RISK_USDT, RISK_ODUL_ORANI, NIHAI_TP_RR, MIN_CONFLUENCE_SKORU, ae
        global API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, AKTIF_RISK_SEVIYESI, V, T
        try:
            PIYASA_MODU = dd_piyasa.value or "her_ikisi"
            TESTNET_AKTIF = (dd_ag.value == "testnet")
            MARJIN_TIPI = dd_marjin_tipi.value or "ISOLATED"
            global STOP_BELIRLEME_MODU
            AKTIF_RISK_SEVIYESI = dd_risk_seviye.value or AKTIF_RISK_SEVIYESI
            STOP_BELIRLEME_MODU = dd_stop_modu.value or STOP_BELIRLEME_MODU
            if dd_mtf_sablon.value in MTF_SABLONLARI:
                mtf_sablonu_uygula(dd_mtf_sablon.value)
            MAKS_MARJIN_USDT = M(5.0, F(tf_marjin.value))
            KALDIRAC = M(1, N(125, int(F(tf_kaldirac.value))))
            ISLEM_BASI_RISK_USDT = M(0.1, F(tf_risk.value))
            RISK_ODUL_ORANI = M(0.5, F(tf_rr.value))
            NIHAI_TP_RR = M(NIHAI_TP_RR, RISK_ODUL_ORANI + 1.0)
            MIN_CONFLUENCE_SKORU = M(10, N(100, int(F(tf_min_skor.value))))
            ae = M(0, int(F(tf_limit.value)))
            global GITHUB_REPO_ADRESI, GITHUB_TOKEN
            API_KEY = tf_api_key.value.strip()
            API_SECRET = tf_api_sec.value.strip()
            TELEGRAM_TOKEN = tf_tg_tok.value.strip()
            TELEGRAM_CHAT_ID = tf_tg_id.value.strip()
            GITHUB_REPO_ADRESI = tf_gh_repo.value.strip() or "emrhozbr/bot"
            GITHUB_TOKEN = tf_gh_tok.value.strip()
            _api_kaydet_tam()
            if GITHUB_TOKEN:
                threading.Thread(target=bulut_durum_gonder, args=(True,), daemon=True).start()
            borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
            V, T = bakiye_getir()
            threading.Thread(target=lambda: pariteleri_yukle(motor.log_yaz), daemon=True).start()
            lbl_tarama_info.value = f"🔍 MTF: {HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT} | Eşik: {MIN_CONFLUENCE_SKORU}+ Puan | Kaldıraç: {KALDIRAC}x"
            lbl_ayar_durum.value = f"✅ Ayarlar ve API kaydedildi! Bakiye: {T:.2f} USDT"
            lbl_ayar_durum.color = "#4ade80"
            motor.log_yaz(f"⚙️ Mobil Ayarlar Güncellendi -> MTF: {HTF_PERIYOT.upper()}/{MTF_PERIYOT.upper()}/{LTF_PERIYOT} | Risk: {ISLEM_BASI_RISK_USDT}$ | Skor: {MIN_CONFLUENCE_SKORU}+")
            _ekrani_yenile()
        except Exception as ex:
            lbl_ayar_durum.value = f"⚠️ Hata: {ex}"
            lbl_ayar_durum.color = "#f87171"
            page.update()

    sekme_ayarlar_icerik = ft.Container(
        content=ft.Column([
            ft.Text("⚙️ STRATEJİ, RİSK & MTF AYARLARI", size=13, weight=ft.FontWeight.BOLD, color="#38bdf8"),
            dd_piyasa,
            dd_ag,
            dd_mtf_sablon,
            dd_risk_seviye,
            dd_stop_modu,
            dd_marjin_tipi,
            ft.Row([tf_marjin, tf_kaldirac], spacing=8),
            ft.Row([tf_risk, tf_rr], spacing=8),
            ft.Row([tf_min_skor, tf_limit], spacing=8),
            ft.Divider(color="#334155"),
            ft.Text("🔑 BINANCE API & TELEGRAM AYARLARI", size=13, weight=ft.FontWeight.BOLD, color="#fde047"),
            tf_api_key,
            tf_api_sec,
            tf_tg_tok,
            tf_tg_id,
            ft.Divider(color="#334155"),
            ft.Text("☁️ TEK TUŞLA OTA & ÇOKLU CİHAZ SENKRONİZASYONU (PC <-> TELEFON)", size=13, weight=ft.FontWeight.BOLD, color="#c084fc"),
            tf_gh_repo,
            tf_gh_tok,
            ft.Row([
                ft.ElevatedButton("⚡ GitHub'dan OTA Güncelle (En Son Sürüm)", bgcolor="#8b5cf6", color="#ffffff", expand=True, on_click=_tek_tus_ota_tik),
                ft.ElevatedButton("☁️ Cihazları Eşitle", bgcolor="#0ea5e9", color="#ffffff", expand=True, on_click=lambda e: threading.Thread(target=lambda: (bulut_durum_cek(True), bulut_durum_gonder(True), _ekrani_yenile("force")), daemon=True).start()),
            ], spacing=8),
            ft.ElevatedButton("💾 Tüm Ayarları Kaydet ve Uygula", bgcolor="#10b981", color="#ffffff", height=42, on_click=_ayarlari_kaydet_tik),
            lbl_ayar_durum
        ], scroll=ft.ScrollMode.AUTO, spacing=10),
        padding=12,
        expand=True
    )

    # --- SEKME 5: GEÇMİŞ İŞLEMLER & LOGLAR ---
    lbl_gecmis_ozet = ft.Text("📊 Toplam: 0 | Winrate: %0.0 | Net PnL: +0.00 USDT", size=12, weight=ft.FontWeight.BOLD, color="#38bdf8")
    lv_gecmis = ft.ListView(height=210, spacing=5, padding=6)
    lv_loglar = ft.ListView(expand=True, spacing=3, padding=6, auto_scroll=True)

    sekme_log_icerik = ft.Container(
        content=ft.Column([
            ft.Row([
                lbl_gecmis_ozet,
                ft.TextButton("⏱️ Oturum Sıfırla", on_click=lambda e: motor.oturum_sayaci_sifirla())
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=lv_gecmis, bgcolor="#11111b", border_radius=8, border=ft.border.all(1, "#334155")),
            ft.Text("📋 SİSTEM VE TARAMA LOG KAYITLARI", size=12, weight=ft.FontWeight.BOLD, color="#fde047"),
            ft.Container(content=lv_loglar, bgcolor="#11111b", border_radius=8, border=ft.border.all(1, "#334155"), expand=True)
        ], spacing=6, expand=True),
        padding=10,
        expand=True
    )

    # --- ANA SEKMELER (TABS) ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        expand=True,
        tabs=[
            ft.Tab(text="📌 İşlemler", content=lv_acik_islemler),
            ft.Tab(text="🔍 Tarama", content=ft.Column([
                ft.Container(content=lbl_tarama_info, padding=ft.padding.only(left=10, right=10, top=8)),
                lv_tarama
            ], expand=True, spacing=4)),
            ft.Tab(text="📊 Karne & Pine", content=sekme_karne_icerik),
            ft.Tab(text="⚙️ Ayarlar", content=sekme_ayarlar_icerik),
            ft.Tab(text="📜 Geçmiş & Log", content=sekme_log_icerik),
        ]
    )

    def _pariteyi_karneye_ac(O):
        secili_parite_state["anahtar"] = O
        mevcut_opts = [opt.key for opt in dd_karne_parite.options]
        if O not in mevcut_opts:
            dd_karne_parite.options.append(ft.dropdown.Option(O))
        dd_karne_parite.value = O
        tabs.selected_index = 2
        page.update()
        _parite_karne_ve_pine_yukle("4h", canli_zorla=False)

    # --- EKRAN GÜNCELLEME FONKSİYONU ---
    _son_ui_ts = [0.0]

    def _ekrani_yenile(kaynak="all"):
        if _ARKA_PLANDA_MI[0] and kaynak != "force":
            return
        simdi = time.time()
        if kaynak != "force" and (simdi - _son_ui_ts[0] < 0.45):
            return
        _son_ui_ts[0] = simdi
        try:
            lbl_durum_bar.value = motor._durum_metni
            lbl_durum_bar.color = motor._durum_renk
            btn_baslat.disabled = bool(bot_calisiyor)
            btn_durdur.disabled = not bool(bot_calisiyor)

            # Açık işlemler ve portföy hesabı
            kU, rI, jq = 0.0, 0.0, 0
            yeni_acik_kartlar = []
            for O, bq in list(acik_islemler.items()):
                if not I(bq, dict):
                    continue
                jq += 1
                bt = bq.get("yon", "LONG")
                b0 = bq.get("piyasa", "future")
                gW, nD, bZ, bM, fk, k1, k0 = islem_kar_zarar_hesapla(O, bq)
                sl, tp = F(bq.get("sl") or 0.0), F(bq.get("tp") or 0.0)
                kU += gW
                rI += fk
                renk_pnl = "#4ade80" if gW >= 0 else "#f87171"
                yon_renk = "#10b981" if bt == "LONG" else "#ef4444"
                kart = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"{bt} {k1}x" if b0 == "future" else f"{bt} SPOT", size=11, weight=ft.FontWeight.BOLD, color="#ffffff"),
                                    bgcolor=yon_renk, padding=ft.padding.symmetric(horizontal=7, vertical=3), border_radius=6
                                ),
                                ft.Text(O, size=14, weight=ft.FontWeight.BOLD, color="#f8fafc"),
                            ], spacing=6),
                            ft.Text(f"{gW:+.2f} USDT (%{nD:+.2f})", size=14, weight=ft.FontWeight.BOLD, color=renk_pnl)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(f"Giriş: {_fmt_f(bZ)}", size=11, color="#cbd5e1"),
                            ft.Text(f"Anlık: {_fmt_f(bM)}", size=11, color="#38bdf8", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Marjin: {fk:.1f}$ (Risk: -{k0:.1f}$)", size=11, color="#fbbf24")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(f"🛑 SL: {_fmt_f(sl)}", size=11, color="#f87171"),
                            ft.Text(f"🎯 TP1: {_fmt_f(tp)}", size=11, color="#4ade80"),
                            ft.Text(str(bq.get("kural_uyum_kisa", "Safe")), size=11, color="#a78bfa")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.ElevatedButton("📊 Karne & Pine", bgcolor="#2563eb", color="#ffffff", expand=True, on_click=lambda e, k=O: _pariteyi_karneye_ac(k)),
                            ft.ElevatedButton("🚨 Kapat", bgcolor="#f97316", color="#ffffff", expand=True, on_click=lambda e, k=O: threading.Thread(target=motor.poz_kapat, args=(k,), daemon=True).start())
                        ], spacing=8)
                    ], spacing=6),
                    bgcolor="#1e293b",
                    border=ft.border.all(1.2, renk_pnl),
                    border_radius=10,
                    padding=10
                )
                yeni_acik_kartlar.append(kart)

            if not yeni_acik_kartlar:
                yeni_acik_kartlar.append(
                    ft.Container(
                        content=ft.Text(
                            "⏳ Şu anda açık pozisyon bulunmuyor.\nBot 'Kırılım Yoksa Swing Yoktur' ve '8 HTF Safe Bölge (1.QML > 2.OB > 3.Fresh > 4.OTE)' kurallarına uygun sinyal yakaladığında işlemler burada listelenir.",
                            size=12, color="#94a3b8", text_align=ft.TextAlign.CENTER
                        ),
                        padding=24, alignment=ft.alignment.center
                    )
                )
            lv_acik_islemler.controls = yeni_acik_kartlar

            qo = M(V + rI + kU, T + kU)
            oran_marjin = (kU / M(rI, 1e-09) * 100.0) if rI > 0 else 0.0
            i8 = W + kU
            ot_top, _, _, sure_str, _ = motor.oturum_pnl_hesapla(kU)

            lbl_portfoy.value = f"{qo:.2f} $"
            lbl_serbest.value = f"Serbest: {V:.2f} $"
            lbl_acik_pnl.value = f"{kU:+.2f} $ (%{oran_marjin:+.1f})"
            lbl_acik_pnl.color = "#4ade80" if kU >= 0 else "#f87171"
            lbl_oturum_pnl.value = f"Oturum: {ot_top:+.2f}$ ({sure_str})"
            lbl_oturum_pnl.color = "#4ade80" if ot_top >= 0 else "#f87171"
            lbl_net_pnl.value = f"{i8:+.2f} $"
            lbl_net_pnl.color = "#4ade80" if i8 >= 0 else "#f87171"
            lbl_aktif_say.value = f"Açık: {jq}/{a4} ({'DEMO' if TESTNET_AKTIF else 'CANLI'})"

            # Borsa tarama listesi
            kG = sorted(
                a1.items(),
                key=lambda x: (
                    tuple(x[1].get("oncelik_vektor", (0, 0, 0, 0))),
                    int(x[1].get("oncelikli_bolge", 0)),
                    tuple(x[1].get("ikincil_vektor", (0, 0, 0, 0))),
                    int(x[1].get("safe_sayisi", 0)),
                    int(str(x[1].get("skor", "0/100")).split("/")[0]) if str(x[1].get("skor", "0")).split("/")[0].isdigit() else 0
                ),
                reverse=True
            )
            tarama_kartlari = []
            for O, b in kG[:60]:
                yon_renk = "#4ade80" if b.get("ana_yon") == "BULLISH" else "#f87171" if b.get("ana_yon") == "BEARISH" else "#94a3b8"
                safe_s = int(b.get("safe_sayisi", 0))
                satir = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(O, size=13, weight=ft.FontWeight.BOLD, color=yon_renk),
                            ft.Text(f"Fiyat: {_fmt_f(b.get('fiyat', 0))}", size=12, color="#f8fafc"),
                            ft.Container(
                                content=ft.Text(f"Skor: {b.get('skor', '0/100')} | Safe:{safe_s}/8", size=11, weight=ft.FontWeight.BOLD, color="#11111b"),
                                bgcolor="#fde047" if safe_s >= 2 else "#38bdf8",
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border_radius=5
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(f"HTF:{b.get('4h','-')} | MTF:{b.get('1h','-')} | LTF:{b.get('ltf','-')}", size=11, color="#cbd5e1"),
                            ft.TextButton("Karne & Grafik →", on_click=lambda e, k=O: _pariteyi_karneye_ac(k))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(str(b.get("setup_detay", "-"))[:95], size=10, color="#94a3b8")
                    ], spacing=3),
                    bgcolor="#1e293b",
                    border_radius=8,
                    padding=8,
                    border=ft.border.all(1, "#334155")
                )
                tarama_kartlari.append(satir)
            lv_tarama.controls = tarama_kartlari

            # Geçmiş ve Loglar
            _ig_yukle()
            tn = L(ah)
            kz = sum(1 for x in ah if F(x.get("pnl_usdt", 0)) >= 0)
            tp_pnl = sum(F(x.get("pnl_usdt", 0)) for x in ah)
            wr = (kz / tn * 100.0) if tn else 0.0
            lbl_gecmis_ozet.value = f"📊 Toplam: {tn} | ✅ {kz} / ❌ {tn-kz} | Win: %{wr:.1f} | Net: {tp_pnl:+.2f}$"
            lv_gecmis.controls = [
                ft.Text(
                    f"[{x.get('tarih','-')}] {x.get('sembol','-')} ({x.get('yon','-')}) | {F(x.get('pnl_usdt',0)):+.2f}$ (%{F(x.get('pnl_yuzde',0)):+.1f}) | {x.get('neden','-')}",
                    size=11,
                    color="#4ade80" if F(x.get("pnl_usdt", 0)) >= 0 else "#f87171"
                )
                for x in ah[:40]
            ]
            lv_loglar.controls = [ft.Text(lg, size=11, color="#cdd6f4", font_family="monospace") for lg in motor._log_q[-80:]]
            page.update()
        except Exception:
            pass

    motor = AlfaMobileBotEngine(ui_callback=_ekrani_yenile)

    def _bot_baslat_tik():
        motor.botu_baslat()
        _ekrani_yenile("force")

    def _bot_durdur_tik():
        motor.botu_durdur()
        _ekrani_yenile("force")

    page.add(
        ft.Column([
            ust_panel,
            tabs
        ], expand=True, spacing=0)
    )

    # Arka plan periyodik yenileme, Keep-Alive (Uyanık Tutucu) ve Watchdog (Oto-Kurtarma)
    def _periyodik_sayac():
        sayac_iter = 0
        while not motor._kapaniyor:
            try:
                sayac_iter += 1
                # Android arka plan uyanik tutucu (yerel sunucuya hafif loopback ping)
                if yerel_port and sayac_iter % 3 == 0:
                    try:
                        _HTTP_SES.get(f"http://127.0.0.1:{yerel_port}/", timeout=0.5)
                    except Exception:
                        pass
                # Watchdog: Bot calisiyor gorunuyor ama tarama dongusu 75 sn'dir yanit vermiyorsa otomatik yeniden baslat
                if bot_calisiyor and (time.time() - _SON_TARAMA_KALP_ATISI[0] > 75.0):
                    _SON_TARAMA_KALP_ATISI[0] = time.time()
                    threading.Thread(target=motor.bot_ana_dongu, daemon=True).start()
                if acik_islemler and any(I(v, dict) for v in acik_islemler.values()):
                    motor.pozisyonlari_senkronize_et()
                elif not _ARKA_PLANDA_MI[0]:
                    _ekrani_yenile("force")
            except Exception:
                pass
            time.sleep(2.5)

    def _ilk_yukleme():
        global V, T
        try:
            _api_yukle()
            od_aktif = _ak_yukle()
            _kayitli_ota_varsa_yukle()
            borsa_kur(PIYASA_MODU, TESTNET_AKTIF)
            bulut_durum_cek(zorla=True)
            V, T = bakiye_getir()
            nQ = sum(1 for v in acik_islemler.values() if I(v, dict))
            if nQ > 0:
                motor.log_yaz(f"📂 Kalıcı hafızadan {nQ} açık pozisyon ve bakiye ({T:.2f}$) geri yüklendi.")
            motor.log_yaz("📱 Alfa Trade Club Flet Mobil APK hazır. Arka plan koruyucu ve kendi kendini onaran borsa motoru aktif!")
            # Eger uygulama arka planda kapanmadan once bot calisiyorsa veya acik islem varsa otomatik devam et!
            if _ONCEKI_BOT_AKTIF or od_aktif or nQ > 0:
                motor.log_yaz("🔄 Önceki oturumda tarama/işlem aktif olduğu için bot otomatik olarak yeniden başlatılıyor...")
                motor.botu_baslat()
            _ekrani_yenile("force")
        except Exception as ex:
            motor.log_yaz(f"⚠️ İlk yükleme uyarısı: {ex}")

    threading.Thread(target=_ilk_yukleme, daemon=True).start()
    threading.Thread(target=_periyodik_sayac, daemon=True).start()


def _boot_main(page: ft.Page):
    try:
        _api_yukle()
        _kayitli_ota_varsa_yukle()
    except Exception:
        pass
    globals()["main"](page)

if __name__ == "__main__":
    ft.app(target=_boot_main) 
