# -*- coding: utf-8 -*-
from pandas import Series
from tradeglob.ta._typing import DictLike
from tradeglob.ta.overlap.dema import dema
from tradeglob.ta.overlap.ema import ema
from tradeglob.ta.overlap.fwma import fwma
from tradeglob.ta.overlap.hma import hma
from tradeglob.ta.overlap.linreg import linreg
from tradeglob.ta.overlap.midpoint import midpoint
from tradeglob.ta.overlap.pwma import pwma
from tradeglob.ta.overlap.rma import rma
from tradeglob.ta.overlap.sinwma import sinwma
from tradeglob.ta.overlap.sma import sma
from tradeglob.ta.overlap.ssf import ssf
from tradeglob.ta.overlap.swma import swma
from tradeglob.ta.overlap.t3 import t3
from tradeglob.ta.overlap.tema import tema
from tradeglob.ta.overlap.trima import trima
from tradeglob.ta.overlap.vidya import vidya
from tradeglob.ta.overlap.wma import wma




def ma(name: str = None, source: Series = None, **kwargs: DictLike) -> Series:
    """MA Selection Utility

    Available MAs: dema, ema, fwma, hma, linreg, midpoint, pwma, rma,
    sinwma, sma, ssf, swma, t3, tema, trima, vidya, wma.

    Parameters:
        name (str): One of the Available MAs. Default: "ema"
        source (Series): Input Series ```source```.

    Other Parameters:
        kwargs (**kwargs): Additional args for the MA.

    Returns:
        (Series): Selected MA

    Esourceample:
        ```py linenums="0"
        ema8 = ta.ma("ema", df.close, length=8)
        sma50 = ta.ma("sma", df.close, length=50)
        pwma10 = ta.ma("pwma", df.close, length=10, asc=False)
        ```
    """
    _mas = [
        "dema", "ema", "fwma", "hma", "linreg", "midpoint", "pwma", "rma",
        "sinwma", "sma", "ssf", "swma", "t3", "tema", "trima", "vidya", "wma"
    ]
    if name is None and source is None:
        return _mas
    elif isinstance(name, str) and name.lower() in _mas:
        name = name.lower()
    else:  # "ema"
        name = _mas[1]

    if   name == "dema": return dema(source, **kwargs)
    elif name == "fwma": return fwma(source, **kwargs)
    elif name == "hma": return hma(source, **kwargs)
    elif name == "linreg": return linreg(source, **kwargs)
    elif name == "midpoint": return midpoint(source, **kwargs)
    elif name == "pwma": return pwma(source, **kwargs)
    elif name == "rma": return rma(source, **kwargs)
    elif name == "sinwma": return sinwma(source, **kwargs)
    elif name == "sma": return sma(source, **kwargs)
    elif name == "ssf": return ssf(source, **kwargs)
    elif name == "swma": return swma(source, **kwargs)
    elif name == "t3": return t3(source, **kwargs)
    elif name == "tema": return tema(source, **kwargs)
    elif name == "trima": return trima(source, **kwargs)
    elif name == "vidya": return vidya(source, **kwargs)
    elif name == "wma": return wma(source, **kwargs)
    else: return ema(source, **kwargs)
