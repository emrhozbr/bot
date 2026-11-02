# ==============================================================================
# ALFA TRADE CLUB (MAHŞERİN 4 ATLISI + YT PART 1-13) — NATIVE ANDROID APK (FLET)
# ==============================================================================
import os, sys, gc, json, webbrowser, time, threading, socket, math, hmac, hashlib
from urllib.parse import urlencode
from datetime import datetime
from pathlib import Path
import requests
import flet as ft

# --- ANDROID APK ICIN SAF PYTHON NUMPY, PANDAS VE CCXT EMULATORU ---
class _NumpyMock:
    nan = float('nan')
    integer = int
    def array(self, x, *a, **kw): return list(x) if not isinstance(x, list) else x
np = _NumpyMock()

class _MiniSeries:
    def __init__(self, data):
        self._d = [float(x) if x is not None and x == x else float('nan') for x in data]
    def __len__(self): return len(self._d)
    def __iter__(self): return iter(self._d)
    @property
    def empty(self): return len(self._d) == 0
    @property
    def values(self): return self._d
    @property
    def iloc(self): return self
    def __getitem__(self, idx):
        if isinstance(idx, slice): return _MiniSeries(self._d[idx])
        if isinstance(idx, _MiniSeries): return _MiniSeries([v for v, b in zip(self._d, idx._d) if b])
        return self._d[idx]
    def to_numpy(self, dtype=float, copy=False): return self._d
    def _op(self, o, fn):
        if isinstance(o, _MiniSeries): return _MiniSeries([fn(a, b) for a, b in zip(self._d, o._d)])
        return _MiniSeries([fn(a, float(o)) for a in self._d])
    def __sub__(self, o): return self._op(o, lambda a, b: a - b)
    def __add__(self, o): return self._op(o, lambda a, b: a + b)
    def __mul__(self, o): return self._op(o, lambda a, b: a * b)
    def __truediv__(self, o): return self._op(o, lambda a, b: a / b if b != 0 else float('nan'))
    def __rtruediv__(self, o): return _MiniSeries([float(o) / a if a != 0 else float('nan') for a in self._d])
    def __neg__(self): return _MiniSeries([-a for a in self._d])
    def __gt__(self, o): return self._op(o, lambda a, b: a > b)
    def __lt__(self, o): return self._op(o, lambda a, b: a < b)
    def __ge__(self, o): return self._op(o, lambda a, b: a >= b)
    def __le__(self, o): return self._op(o, lambda a, b: a <= b)
    def abs(self): return _MiniSeries([abs(a) for a in self._d])
    def diff(self): return _MiniSeries([float('nan')] + [self._d[i] - self._d[i-1] for i in range(1, len(self._d))])
    def shift(self, n=1): return _MiniSeries([float('nan')]*n + self._d[:-n] if n > 0 else self._d)
    def where(self, cond, other=0.0): return _MiniSeries([a if c else float(other) for a, c in zip(self._d, cond._d)])
    def replace(self, old, new): return _MiniSeries([new if a == old else a for a in self._d])
    def fillna(self, val): return _MiniSeries([float(val) if (a != a or a is None) else a for a in self._d])
    def bfill(self):
        out = list(self._d); last = 0.0
        for i in range(len(out)-1, -1, -1):
            if out[i] == out[i]: last = out[i]
            else: out[i] = last
        return _MiniSeries(out)
    def rolling(self, w):
        d = self._d
        class _Roll:
            def mean(s_self):
                out = []
                for i in range(len(d)):
                     seg = [x for x in d[max(0, i-w+1):i+1] if x == x]
                     out.append(sum(seg)/len(seg) if seg else float('nan'))
                return _MiniSeries(out)
        return _Roll()
    def cumsum(self):
        out, s = [], 0.0
        for a in self._d:
            if a == a: s += a
            out.append(s)
        return _MiniSeries(out)
    def min(self):
        v = [a for a in self._d if a == a]
        return min(v) if v else 0.0
    def max(self):
        v = [a for a in self._d if a == a]
        return max(v) if v else 0.0
    def mean(self):
        v = [a for a in self._d if a == a]
        return sum(v)/len(v) if v else 0.0
    def idxmin(self):
        v = [(a, i) for i, a in enumerate(self._d) if a == a]
        return min(v)[1] if v else 0
    def idxmax(self):
        v = [(a, i) for i, a in enumerate(self._d) if a == a]
        return max(v)[1] if v else 0

class _MiniDF:
    def __init__(self, rows=None, columns=None):
        self.columns = list(columns or ['timestamp','open','high','low','close','volume'])
        self._data = {c: [] for c in self.columns}
        if isinstance(rows, dict):
            for c in self.columns: self._data[c] = list(rows.get(c, []))
        elif isinstance(rows, list):
            for r in rows:
                for i, c in enumerate(self.columns):
                    self._data[c].append(float(r[i]) if i < len(r) else 0.0)
    def copy(self):
        df = _MiniDF(columns=self.columns)
        for c in self.columns: df._data[c] = list(self._data[c])
        return df
    def __len__(self): return len(self._data[self.columns[0]]) if self.columns else 0
    @property
    def empty(self): return len(self) == 0
    def __getitem__(self, key):
        if isinstance(key, str): return _MiniSeries(self._data[key])
        if isinstance(key, list):
            df = _MiniDF(columns=key)
            for c in key: df._data[c] = list(self._data[c])
            return df
        if isinstance(key, _MiniSeries):
            idxs = [i for i, b in enumerate(key._d) if b]
            df = _MiniDF(columns=self.columns)
            for c in self.columns: df._data[c] = [self._data[c][i] for i in idxs]
            return df
        return None
    def __setitem__(self, key, val):
        if key not in self.columns: self.columns.append(key)
        self._data[key] = list(val._d if isinstance(val, _MiniSeries) else val)
        if '_np_c' in self.__dict__: self.__dict__['_np_c'].pop(key, None)
    @property
    def iloc(self):
        parent = self
        class _Iloc:
            def __getitem__(s_self, idx):
                if isinstance(idx, int):
                    i = idx if idx >= 0 else len(parent) + idx
                    return {c: parent._data[c][i] for c in parent.columns}
                if isinstance(idx, slice):
                    df = _MiniDF(columns=parent.columns)
                    for c in parent.columns: df._data[c] = parent._data[c][idx]
                    return df
        return _Iloc()
    def reset_index(self, drop=True): return self.copy()
    def iterrows(self):
        for i in range(len(self)):
            yield i, {c: self._data[c][i] for c in self.columns}
    def max(self, axis=1):
        n = len(self)
        return _MiniSeries([max(self._data[c][i] for c in self.columns) for i in range(n)])
    def min(self, axis=1):
        n = len(self)
        return _MiniSeries([min(self._data[c][i] for c in self.columns) for i in range(n)])

class _PandasMock:
    DataFrame = _MiniDF
    def concat(self, objs, axis=1):
        df = _MiniDF(columns=[str(i) for i in range(len(objs))])
        for i, s in enumerate(objs): df[str(i)] = s
        return df
    def to_datetime(self, s, unit='ms', utc=True): raise Exception("skip_dt")
pd = _PandasMock()

class _BinanceLite:
    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.apiKey = cfg.get('apiKey', '')
        self.secret = cfg.get('secret', '')
        self.defaultType = cfg.get('options', {}).get('defaultType', 'future')
        self.sandbox = False
    def set_sandbox_mode(self, v): self.sandbox = bool(v)
    def enable_demo_trading(self, v): self.sandbox = bool(v)
    def _base(self):
        if self.defaultType == 'future':
            return 'https://testnet.binancefuture.com' if self.sandbox else 'https://fapi.binance.com'
        return 'https://testnet.binance.vision' if self.sandbox else 'https://api.binance.com'
    def load_markets(self, reload=False):
        url = f"{self._base()}/{'fapi/v1/exchangeInfo' if self.defaultType=='future' else 'api/v3/exchangeInfo'}"
        r = requests.get(url, timeout=10).json()
        out = {}
        for s in r.get('symbols', []):
            if s.get('quoteAsset') != 'USDT': continue
            sym = f"{s['baseAsset']}/USDT"
            out[sym] = {'id': s['symbol'], 'base': s['baseAsset'], 'quote': 'USDT', 'active': s.get('status')=='TRADING', 'spot': self.defaultType!='future', 'future': self.defaultType=='future', 'swap': self.defaultType=='future', 'linear': True}
        return out
    def fetch_tickers(self):
        url = f"{self._base()}/{'fapi/v1/ticker/24hr' if self.defaultType=='future' else 'api/v3/ticker/24hr'}"
        r = requests.get(url, timeout=10).json()
        out = {}
        if isinstance(r, list):
            for t in r:
                s = t.get('symbol', '')
                if s.endswith('USDT'):
                    sym = f"{s[:-4]}/USDT"
                    out[sym] = {'quoteVolume': float(t.get('quoteVolume') or 0.0), 'last': float(t.get('lastPrice') or 0.0)}
        return out
    def fetch_ticker(self, symbol):
        raw = symbol.split(':')[0].replace('/', '')
        url = f"{self._base()}/{'fapi/v1/ticker/price' if self.defaultType=='future' else 'api/v3/ticker/price'}?symbol={raw}"
        r = requests.get(url, timeout=5).json()
        p = float(r.get('price') or 0.0)
        return {'last': p, 'close': p, 'info': r}
    def fetch_ohlcv(self, symbol, timeframe='15m', limit=300):
        raw = symbol.split(':')[0].replace('/', '')
        url = f"{self._base()}/{'fapi/v1/klines' if self.defaultType=='future' else 'api/v3/klines'}?symbol={raw}&interval={timeframe}&limit={limit}"
        r = requests.get(url, timeout=10).json()
        return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in r]
    def amount_to_precision(self, symbol, amount): return round(float(amount), 5)
    def price_to_precision(self, symbol, price): return round(float(price), 6)
    def fetch_balance(self): return {'USDT': {'free': 0.0, 'total': 0.0}}
    def set_leverage(self, lev, symbol): pass
    def set_margin_mode(self, mode, symbol): pass
    def cancel_all_orders(self, symbol): pass
    def create_market_buy_order(self, symbol, amount, params=None): pass
    def create_market_sell_order(self, symbol, amount, params=None): pass
    def create_order(self, symbol, type, side, amount, price=None, params=None): pass

class _CCXTMock:
    binance = _BinanceLite
ccxt = _CCXTMock()

_HTTP_SES = requests.Session()
F, I, R, X, M, N, L, A, G = (float, isinstance, round, Exception, max, min, len, abs, range)
jC, aR, cR, eD = (('Segoe UI', 10, 'bold'), ('Segoe UI', 11, 'bold'), ('Segoe UI', 12, 'bold'), ('Segoe UI', 13, 'bold'))