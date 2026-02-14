# coding: utf-8
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import csv
import matplotlib.pyplot as plt
import re
from textwrap import wrap
import pathlib
import numpy as np
import yfinance as yf
import pandas as pd

# ASX announcement URL
ASX_URL = "https://www.asx.com.au/asx/v2/statistics/todayAnns.do"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Your ticker list (unchanged)
TICKER_LIST = {
    "ICN.AX", "RRL.AX", "GGAB.AX", "IFRA.AX", "HDN.AX", "IBAL.AX", "MVE.AX", "IBUY.AX", "AESG.AX", "GHHF.AX", "ALD.AX",
    "WBC.AX", "JHGA.AX", "UMAX.AX", "AAC.AX", "XRO.AX", "IEAT.AX", "BNKS.AX", "EMXC.AX", "BNDS.AX", "ETPMPT.AX",
    "QNDQ.AX", "BCI.AX", "PNI.AX", "GGOV.AX", "YAL.AX", "GNC.AX", "BUGG.AX", "LIC.AX", "CCP.AX", "NXG.AX",
    "CFLO.AX", "GLPR.AX", "360.AX", "FAIR.AX", "FCAP.AX", "MTS.AX", "SGH.AX", "IZZ.AX", "IMU.AX", "FRGG.AX",
    "TLC.AX", "NIC.AX", "ZIM.AX", "COF.AX", "IEL.AX", "DYL.AX", "HJPN.AX", "REH.AX", "PDI.AX", "MQDB.AX",
    "PTM.AX", "CDA.AX", "ERTH.AX", "GOAT.AX", "SGM.AX", "IAF.AX", "IXJ.AX", "IFT.AX", "VEU.AX", "SOL.AX",
    "LEND.AX", "DACE.AX", "NWS.AX", "CQE.AX", "LFS.AX", "VMIN.AX", "BILL.AX", "GMTL.AX", "DMP.AX", "NGI.AX",
    "VBND.AX", "MMKT.AX", "EBO.AX", "BANK.AX", "ORI.AX", "JREG.AX", "CMW.AX", "USIG.AX", "PYC.AX", "FPH.AX",
    "SIQ.AX", "BCOM.AX", "NUGG.AX", "ERA.AX", "SNAS.AX", "CAR.AX", "ETHI.AX", "EVN.AX", "LTR.AX", "RBTZ.AX",
    "IAA.AX", "MVR.AX", "SSM.AX", "QYLD.AX", "CRN.AX", "IMLC.AX", "JIN.AX", "AMP.AX", "MVA.AX", "ZIP.AX",
    "REA.AX", "AGVT.AX", "SNL.AX", "HYGG.AX", "RWC.AX", "OCL.AX", "ALTB.AX", "E200.AX", "IMPQ.AX", "SPR.AX",
    "INIF.AX", "RIO.AX", "MCGG.AX", "US10.AX", "MGOC.AX", "IHWL.AX", "HGEN.AX", "OZF.AX", "TPG.AX", "EMMG.AX",
    "IPAY.AX", "TLS.AX", "DCOR.AX", "CHN.AX", "ETPMPM.AX", "MQEG.AX", "VIF.AX", "UTIP.AX", "NXT.AX", "DAVA.AX",
    "LKE.AX", "NEU.AX", "LNYN.AX", "EINC.AX", "A2M.AX", "GARP.AX", "IDX.AX", "HUB.AX", "WHC.AX", "KAR.AX",
    "PNV.AX", "CKF.AX", "VCX.AX", "ADT.AX", "FANG.AX", "AUB.AX", "VAU.AX", "FBU.AX", "WIRE.AX", "CBO.AX",
    "HGBL.AX", "CGHE.AX", "IPX.AX", "ACL.AX", "MOAT.AX", "NNWH.AX", "RGN.AX", "ISO.AX", "MKAX.AX", "STW.AX",
    "QPON.AX", "WPR.AX", "NSR.AX", "BEN.AX", "KLS.AX", "ARMR.AX", "MHG.AX", "BOE.AX", "QMAX.AX", "JPEQ.AX",
    "FPR.AX", "IKO.AX", "DBBF.AX", "SCG.AX", "AIA.AX", "BGA.AX", "BMN.AX", "MVB.AX", "ASX.AX", "EMKT.AX",
    "CIP.AX", "TYR.AX", "CNEW.AX", "DGGF.AX", "C79.AX", "ASB.AX", "QOZ.AX", "WC8.AX", "DFGH.AX", "EDV.AX",
    "GPT.AX", "GDG.AX", "DOW.AX", "AGL.AX", "BPT.AX", "GWA.AX", "SIG.AX",
    "GIVE.AX", "ASK.AX", "ESPO.AX", "HBRD.AX", "QFN.AX", "MTAV.AX", "EX20.AX", "AD8.AX", "AAA.AX", "ADEF.AX", "GLIN.AX", "DVDY.AX", "GRNV.AX",
    "MAQ.AX", "MND.AX", "SKUK.AX", "VBTC.AX", "LPGD.AX", "RSM.AX", "BBAB.AX", "HQLT.AX", "QHSM.AX", "IIND.AX",
    "VSL.AX", "BHYB.AX", "BGBL.AX", "VBLD.AX", "PRU.AX", "MVW.AX", "ILB.AX", "AYLD.AX", "OOO.AX", "DVP.AX",
    "PAXX.AX", "GOZ.AX", "BWP.AX", "INES.AX", "NDIA.AX", "PLUS.AX", "PMGOLD.AX", "PPC.AX", "QOR.AX", "WGX.AX",
    "GOLD.AX", "GMG.AX", "GOR.AX", "WEB.AX", "CAT.AX", "FASI.AX", "MVOL.AX", "VACF.AX", "SEMI.AX", "VNT.AX",
    "REIT.AX", "OZR.AX", "IHVV.AX", "VDGR.AX", "GPEQ.AX", "NEC.AX", "SMLL.AX", "GOVT.AX", "FFM.AX", "QRE.AX",
    "GGUS.AX", "ING.AX", "CURE.AX", "JBH.AX", "VAS.AX", "OPT.AX", "IOO.AX", "IVV.AX", "SUBD.AX", "AZJ.AX",
    "MEI.AX", "MCCL.AX", "NAB.AX", "ICOR.AX", "QUS.AX", "ASAO.AX", "ALL.AX", "XALG.AX", "IRE.AX", "VLUE.AX",
    "BAP.AX", "CRYP.AX", "UNI.AX", "RUL.AX", "DAOR.AX", "SEK.AX", "ARU.AX", "MQG.AX", "ORA.AX", "FIIN.AX",
    "SGP.AX", "CGF.AX", "TEA.AX", "PMT.AX", "PPT.AX", "GEAR.AX", "PMV.AX", "NVX.AX", "FOOD.AX", "PAC.AX",
    "IHHY.AX", "ALQ.AX", "IFM.AX", "SLX.AX", "QBE.AX", "BAOR.AX", "LOV.AX", "CLDD.AX", "CUV.AX", "BGL.AX",
    "IMM.AX", "DGVA.AX", "ESGI.AX", "AX1.AX", "MICH.AX", "NDQ.AX", "TPW.AX", "NNUK.AX", "ZYAU.AX", "VAE.AX",
    "MNRS.AX", "HETH.AX", "QUB.AX", "CBA.AX", "DDR.AX", "FLT.AX", "SRG.AX", "EVT.AX", "SUN.AX", "DBI.AX",
    "U100.AX", "TLX.AX", "NWL.AX", "DXI.AX", "BXB.AX", "ORG.AX", "XCO2.AX", "BSL.AX", "VEA.AX", "WDIV.AX",
    "IWLD.AX", "FUEL.AX", "GAME.AX", "BOND.AX", "DGSM.AX", "VHY.AX", "BRE.AX", "VVLU.AX", "PRN.AX", "AOV.AX",
    "QRI.AX", "MQAE.AX", "L1HI.AX", "VCF.AX", "WXOZ.AX", "USD.AX", "TUA.AX", "RGB.AX", "YMAX.AX", "SYA.AX",
    "AUST.AX", "IHD.AX", "IHEB.AX", "LNAS.AX", "VEQ.AX", "IVE.AX", "IEM.AX", "WEMG.AX", "ACDC.AX", "GEM.AX",
    "APA.AX", "CETF.AX", "UOS.AX", "GBND.AX", "STX.AX", "MAET.AX", "5GOV.AX", "WCMQ.AX", "INR.AX", "JHLO.AX",
    "IISV.AX", "MIN.AX", "MSTR.AX", "SRV.AX", "ROYL.AX", "QAU.AX", "DTL.AX", "RCB.AX", "MFOA.AX", "EIGA.AX",
    "RFF.AX", "IXI.AX", "MHOT.AX", "NAN.AX", "INCM.AX", "VLC.AX", "IAG.AX", "IGO.AX", "IMD.AX", "G200.AX",
    "QUAL.AX", "PDN.AX", "QAL.AX", "PIXX.AX", "ITEK.AX", "MSB.AX", "MAC.AX", "RINC.AX", "PLS.AX", "ZYUS.AX",
    "SMR.AX", "CTD.AX", "VGB.AX", "OZBD.AX", "SVNP.AX", "SGLLV.AX", "DHHF.AX", "BOQ.AX", "HMC.AX", "VGE.AX",
    "1GOV.AX", "OBM.AX", "QLTY.AX", "WOR.AX", "ETPMAG.AX", "WOW.AX", "JEGA.AX", "MVS.AX", "TNE.AX", "INA.AX",
    "YANK.AX", "CVL.AX", "FHCO.AX", "AUMF.AX", "ANN.AX", "MAH.AX", "ANZ.AX", "TCL.AX", "WA1.AX", "ROBO.AX",
    "ATEC.AX", "BVS.AX", "GDX.AX", "GLDN.AX", "XARO.AX", "MAAT.AX", "PGC.AX", "DHG.AX", "CSC.AX", "MYS.AX",
    "RMS.AX", "S3GO.AX", "GNDQ.AX", "IOZ.AX", "ASIA.AX", "GCO2.AX", "PAVE.AX", "SGR.AX", "MAD.AX", "IEU.AX",
    "ATOM.AX", "SFY.AX", "ULTB.AX", "XMET.AX", "IJH.AX", "VETH.AX", "VNGS.AX", "STO.AX", "BSUB.AX", "CWY.AX",
    "GROW.AX", "RPL.AX", "WDMF.AX", "BBUS.AX", "DJRE.AX", "OFX.AX", "IJP.AX", "ILC.AX", "PME.AX", "F100.AX",
    "HEUR.AX", "FUTR.AX", "IHCB.AX", "MGR.AX", "OZXX.AX", "DXS.AX", "VEFI.AX", "HJZP.AX", "RCAP.AX", "NST.AX",
    "SWTZ.AX", "GXLD.AX", "BBFD.AX", "AGX1.AX", "PNR.AX", "CYL.AX", "JRHG.AX", "IUSG.AX", "BHP.AX", "DFND.AX",
    "DRIV.AX", "VGAD.AX", "AUDS.AX", "HLI.AX", "CIA.AX", "BC8.AX", "MMS.AX", "NXL.AX", "VDHG.AX", "HHIF.AX",
    "NHF.AX", "USTB.AX", "HCW.AX", "GGFD.AX", "WDS.AX", "ESTX.AX", "SFR.AX", "JEPI.AX", "AQLT.AX", "EAFZ.AX",
    "LSGE.AX", "IFL.AX", "ARB.AX", "SUL.AX", "EMR.AX", "AEBD.AX", "ALX.AX", "CHC.AX", "EDOC.AX", "WRLD.AX",
    "WVOL.AX", "LYC.AX", "SKC.AX", "WXHG.AX", "MGH.AX", "ISEC.AX", "BRG.AX", "RARI.AX", "NCK.AX", "SPK.AX",
    "ARF.AX", "IJR.AX", "BLX.AX", "HCRD.AX", "MPL.AX", "NHC.AX", "APE.AX", "IGB.AX", "IPH.AX", "RGOS.AX",
    "PFP.AX", "RHC.AX", "GCAP.AX", "CU6.AX", "EBND.AX", "MOGL.AX", "USHY.AX", "CMM.AX", "QMIX.AX", "MTUM.AX",
    "JHX.AX", "CSL.AX", "MYX.AX", "JNDQ.AX", "VAP.AX", "RMD.AX", "LLC.AX", "GMVW.AX", "UYLD.AX", "QHAL.AX",
    "JGLO.AX", "URNM.AX", "WES.AX", "HSN.AX", "AASF.AX", "JDO.AX", "VISM.AX", "ILU.AX", "ISLM.AX", "WAF.AX",
    "JHPI.AX", "VTS.AX", "DHOF.AX", "MQWS.AX", "MP1.AX", "RDV.AX", "HVN.AX", "MAF.AX", "SYI.AX", "BRN.AX",
    "TBIL.AX", "LFG.AX", "MQIO.AX", "GYG.AX", "ETPMPD.AX", "SDR.AX", "RIC.AX", "TECH.AX", "QAN.AX", "GLOB.AX",
    "VAF.AX", "BKW.AX", "CTT.AX", "VESG.AX", "CGUN.AX", "VGS.AX", "DRR.AX", "XASG.AX", "MFG.AX", "MHHT.AX",
    "SHV.AX", "CRED.AX", "DZZF.AX", "IYLD.AX", "NUF.AX", "S32.AX", "KLS.AX", "DGCE.AX", "JLG.AX", "IIGF.AX",
    "HJZP.AX", "IPG.AX", "WBT.AX", "CNI.AX", "VDBA.AX", "SDF.AX", "GMD.AX", "RDX.AX", "T3MP.AX", "MYR.AX",
    "EQT.AX", "COL.AX", "VSO.AX", "BOT.AX", "DRUG.AX", "CQR.AX", "HLTH.AX", "URW.AX", "PXA.AX", "SSO.AX",
    "HACK.AX", "HVST.AX", "ABG.AX", "IGRO.AX", "L1IF.AX", "MVF.AX", "FRAR.AX", "FLOT.AX", "WTC.AX", "SPY.AX",
    "NWH.AX", "VUL.AX", "A200.AX", "A4N.AX", "REG.AX", "FHNG.AX", "TAH.AX", "BEAR.AX", "CPU.AX", "H100.AX",
    "CLW.AX", "RSG.AX", "FSML.AX", "COH.AX", "ABB.AX", "FMG.AX", "DRO.AX", "JZRO.AX", "TWE.AX", "XGOV.AX",
    "PPM.AX", "IESG.AX", "OML.AX", "AEF.AX", "TANN.AX", "FEMX.AX", "SLF.AX", "BTXX.AX", "CLNE.AX", "SLC.AX",
    "SHL.AX", "KGN.AX", "HQUS.AX", "GXAI.AX", "HNDQ.AX", "QSML.AX", "VDCO.AX", "BBOZ.AX", "IHOO.AX", "HVLU.AX",
    "APX.AX", "PWH.AX", "ELD.AX", "HLS.AX", "DTEC.AX"
}

BULLISH_KEYWORDS = {
    "takeover": 3.0,
    "acquisition offer": 3.0,
    "acquisition proposal": 3.0,
    "non-binding proposal": 3.0,
    "strategic review": 2.8,
    "approach received": 3.0,
    "indicative proposal": 3.0,
    "preliminary discussions": 2.8,
    "scheme of arrangement": 3.0,
    "friendly merger": 2.7,
    "buyout": 3.0,
    "merger": 2.5,
    "strategic acquisition": 2.5,
    "record": 2.5,
    "record result": 2.7,
    "record profit": 2.7,
    "profit": 2.0,
    "earnings": 2.0,
    "eps growth": 2.3,
    "ebitda": 1.8,
    "revenue": 2.0,
    "sales": 2.0,
    "turnover": 2.0,
    "cash flow": 2.0,
    "operating cash flow": 2.0,
    "free cash flow": 2.0,
    "exceeds": 2.5,
    "beats": 2.5,
    "beat": 2.5,
    "above expectations": 2.5,
    "margin expansion": 2.0,
    "net income": 2.0,
    "strong quarter": 2.0,
    "profitability": 2.0,
    "strong performance": 2.2,
    "solid performance": 2.0,
    "better than expected": 2.5,
    "raises guidance": 2.8,
    "increased guidance": 2.8,
    "guidance beat": 2.8,
    "strong guidance": 2.7,
    "positive outlook": 2.7,
    "upgrade": 2.5,
    "upward revision": 2.5,
    "forecast": 1.8,
    "projected growth": 2.2,
    "analyst upgrade": 2.5,
    "guidance maintained": 1.8,
    "long-term outlook": 2.0,
    "expectations exceeded": 2.5,
    "approval": 2.5,
    "regulatory approval": 3.0,
    "fda approval": 3.0,
    "clearance": 2.5,
    "dose escalation": 3.0,
    "trial commencement": 3.0,
    "patient enrollment": 2.8,
    "phase 3": 3.0,
    "phase iii": 3.0,
    "phase 2": 2.8,
    "phase ii": 2.8,
    "positive trial results": 3.0,
    "study met primary endpoint": 3.0,
    "primary endpoint achieved": 3.0,
    "secondary endpoint achieved": 2.7,
    "patent granted": 2.5,
    "orphan drug designation": 3.0,
    "breakthrough therapy designation": 3.0,
    "fast track approval": 3.0,
    "new contract": 2.3,
    "contract win": 2.3,
    "strategic partnership": 2.2,
    "market expansion": 2.3,
    "global expansion": 2.3,
    "new market entry": 2.3,
    "licensing agreement": 2.2,
    "production increase": 2.3,
    "new facility": 2.3,
    "funding secured": 2.5,
    "syndicated loan": 2.0,
    "secured financing": 2.3,
    "project finance approved": 2.3,
    "joint venture": 2.2,
    "alliance": 2.0,
    "distribution agreement": 2.2,
    "supply agreement": 2.2,
    "dividend increase": 2.8,
    "special dividend": 2.8,
    "share repurchase": 2.7,
    "buyback": 2.7,
    "capital return": 2.5,
    "increased payout": 2.7,
    "stock split": 2.5,
    "bonus issue": 2.5,
    "strong demand": 2.3,
    "accelerated growth": 2.3,
    "market leader": 2.0,
    "uptrend": 1.8,
    "robust": 1.8,
    "surge": 2.0,
    "momentum": 1.8,
    "traction": 1.8,
    "strengthening": 1.8,
    "record high": 2.7,
    "milestone": 2.5,
    "breakthrough": 2.5,
    "new product": 2.3,
    "product launch": 2.3,
    "innovation": 1.8,
    "technology breakthrough": 2.5,
    "market share gain": 2.3,
    "capacity expansion": 2.3,
    "operational milestone": 2.2,
}

BEARISH_KEYWORDS = {
    "decline": -1.5,
    "loss": -2.0,
    "downgrade": -1.5,
    "miss": -2.0,
    "weak": -1.5,
    "drop": -1.5,
    "fall": -1.5,
    "decrease": -1.5,
}

NEGATION_WORDS = {"not", "no", "never", "none"}

HEADERS_PDF = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

# ────────────────────────────────────────────────────────────────
# NEW: Strategy 1 & 2 helper functions
# ────────────────────────────────────────────────────────────────

def is_earnings_announcement(title):
    """Detect if announcement is likely an earnings / financial results release"""
    if not isinstance(title, str):
        return False
    title_lower = title.lower()
    earnings_keywords = [
        "result", "results", "earnings", "profit", "loss", "eps", "npata", "ebit",
        "ebitda", "financial report", "quarterly", "half yearly", "full year",
        "annual report", "preliminary final report", "appendix 4e", "appendix 4d",
        "financial statements", "year end", "interim"
    ]
    return any(kw in title_lower for kw in earnings_keywords)


def approximate_sue(ticker, lookback_quarters=8):
    """
    Approximate SUE using seasonal random walk (common proxy when no analyst data).
    SUE = (Actual - Expected) / StdDev(errors), Expected = same quarter last year.
    """
    try:
        stock = yf.Ticker(ticker)
        earnings = stock.quarterly_earnings
        if earnings.empty:
            earnings = stock.earnings  # fallback to annual

        if len(earnings) < lookback_quarters + 4:
            return np.nan

        # Prefer 'Earnings' column; fallback to first numeric
        if 'Earnings' in earnings.columns:
            series = earnings['Earnings'].dropna()
        else:
            series = earnings.select_dtypes(include=[np.number]).iloc[:, 0].dropna()

        series = series.tail(lookback_quarters + 4)
        if len(series) < 5:
            return np.nan

        actual = series.iloc[-1]
        expected = series.iloc[-5]  # 4 quarters prior
        errors = series.diff().dropna().tail(lookback_quarters)
        std = errors.std() if len(errors) > 1 else 1.0

        sue = (actual - expected) / std if std != 0 else 0.0
        return sue
    except Exception as e:
        print(f"SUE calc failed for {ticker}: {e}")
        return np.nan


def passes_advanced_filters(ticker):
    """Liquidity + Momentum (Strategy 2) + basic filters"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        if hist.empty or len(hist) < 40:
            return False

        current_price = hist['Close'].iloc[-1]

        # Liquidity (20-day avg volume > 300k shares)
        avg_vol = hist['Volume'].tail(20).mean()
        if avg_vol < 300_000:
            return False

        # Market cap range (50M - 2B AUD - mid/small focus)
        info = stock.info
        mc = info.get('marketCap', 0)
        if not (50_000_000 <= mc <= 2_000_000_000):
            return False

        # Momentum: 10-day return > +3%
        if len(hist) >= 10:
            mom_10d = (current_price - hist['Close'].iloc[-10]) / hist['Close'].iloc[-10] * 100
            if mom_10d < 3.0:
                return False

        # Trend: Price above 50-day SMA
        sma_50 = hist['Close'].rolling(50).mean().iloc[-1]
        if current_price < sma_50:
            return False

        # RSI not overbought (>75)
        delta = hist['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50
        if rsi > 75:
            return False

        return True
    except Exception as e:
        print(f"Filter error for {ticker}: {e}")
        return False


def first_scrape():
    """Get all announcement data including titles for PDF URL matching"""
    my_url = "https://www.asx.com.au/asx/v2/statistics/todayAnns.do"
    req = requests.get(my_url, headers=HEADERS_PDF)
    if req.status_code != 200:
        print(f"Failed to load page, status code {req.status_code}")
        return []
    
    page_soup = BeautifulSoup(req.content, 'html.parser')
    link_form = "/asx/v2/statistics/displayAnnouncement.do?display=pdf&idsId="
    announcement_data = []
    
    table = page_soup.find("table")
    if not table:
        return []
    
    for tr in table.find_all('tr')[1:]:  # Skip header
        tds = tr.find_all('td')
        if len(tds) < 4:
            continue
            
        ticker = tds[0].text.strip().upper()
        
        # Extract title for matching
        title_cell = tds[3]
        full_title_text = title_cell.get_text(separator=" ", strip=True)
        title = re.sub(r'\d+\s+pages?\s+\d+\.?\d*KB$', '', full_title_text).strip()
        
        # Get PDF link
        a_tag = tds[3].find('a', href=True)
        if not a_tag:
            continue
            
        href_raw = a_tag['href']
        href_clean = href_raw.replace('\n', '').replace('\r', '').replace(' ', '')
        
        if link_form in href_clean:
            full_url = 'https://www.asx.com.au' + href_clean
            announcement_data.append({
                'ticker': ticker,
                'title': title,
                'landing_url': full_url
            })
    
    return announcement_data


def get_pdf_url_from_landing_page(landing_url):
    """Extract the actual PDF URL from a landing page"""
    try:
        response = requests.get(landing_url, headers=HEADERS_PDF)
        if response.status_code != 200:
            return None
            
        content = response.text
        pdf_match = re.search(r'/asxpdf/[^"\']*\.pdf', content)
        if pdf_match:
            return 'https://www.asx.com.au' + pdf_match.group(0)
        return None
    except Exception as e:
        print(f"Error extracting PDF URL from {landing_url}: {e}")
        return None


def get_pdf_urls_for_announcements(announcements):
    """Get PDF URLs that match specific announcements"""
    print("\n--- Getting PDF URLs for announcements ---")
    
    all_announcement_data = first_scrape()
    
    pdf_urls = {}
    
    for ann in announcements:
        ticker = ann["ticker"]
        title = ann["title"]
        
        matching_data = None
        for data in all_announcement_data:
            if (data['ticker'] == ticker and 
                similar_titles(data['title'], title)):
                matching_data = data
                break
        
        if matching_data:
            print(f"Getting PDF URL for {ticker}: {title[:50]}...")
            pdf_url = get_pdf_url_from_landing_page(matching_data['landing_url'])
            if pdf_url:
                pdf_urls[f"{ticker}_{title}"] = pdf_url
                print(f"  Found: {pdf_url}")
            else:
                print(f"  No PDF URL found")
        else:
            print(f"No matching announcement found for {ticker}: {title[:50]}...")
    
    return pdf_urls


def similar_titles(title1, title2, threshold=0.8):
    """Check if two titles are similar enough (simple word-based comparison)"""
    words1 = set(title1.lower().split())
    words2 = set(title2.lower().split())
    
    if not words1 or not words2:
        return False
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union >= threshold


def parse_announcement_datetime(date_time_str):
    formats_to_try = [
        "%d/%m/%Y %I:%M %p",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y\n%I:%M %p",
        "%d/%m/%Y\n%H:%M",
    ]
    
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_time_str, fmt)
            return pytz.timezone("Australia/Sydney").localize(dt)
        except ValueError:
            continue
    return None


def calculate_sentiment_score(title):
    title_lower = title.lower()
    score = 0.0
    
    for phrase, weight in BULLISH_KEYWORDS.items():
        if phrase in title_lower:
            score += weight
    
    words = re.findall(r'\b\w+\b', title_lower)
    for i, word in enumerate(words):
        is_negated = i > 0 and words[i-1] in NEGATION_WORDS
        
        if word in BULLISH_KEYWORDS and BULLISH_KEYWORDS[word] <= 2.0:
            score += BULLISH_KEYWORDS[word] * (-0.5 if is_negated else 1.0)
        elif word in BEARISH_KEYWORDS:
            score += BEARISH_KEYWORDS[word] * (-0.5 if is_negated else 1.0)
    
    return round(score, 2)


def get_short_interest(ticker):
    clean_ticker = ticker.replace('.AX', '')
    url = f"https://www.shortman.com.au/stock?q={clean_ticker}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to get short data for {ticker}, status: {response.status_code}")
            return "N/A"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        short_td = soup.find('td', class_='ca')
        if short_td:
            short_text = short_td.get_text(strip=True)
            short_percentage = short_text.replace('%', '').strip()
            return f"{short_percentage}%"
        else:
            return "N/A"
            
    except Exception as e:
        print(f"Error getting short data for {ticker}: {e}")
        return "N/A"


def get_short_interest_for_announcements(announcements, no_match_tickers=None):
    print("\n--- Getting short interest data ---")
    short_data = {}
    
    unique_tickers = set()
    for ann in announcements:
        unique_tickers.add(ann["ticker"] + ".AX")
    
    if no_match_tickers:
        unique_tickers.update(no_match_tickers)
    
    for ticker in unique_tickers:
        print(f"Getting short interest for {ticker}...")
        short_interest = get_short_interest(ticker)
        short_data[ticker] = short_interest
        print(f"  {ticker}: {short_interest}")
        time.sleep(0.5)
    
    return short_data


# ────────────────────────────────────────────────────────────────
# Main execution - with Strategy 1 & 2 integrated
# ────────────────────────────────────────────────────────────────

print(f"Fetching from URL: {ASX_URL}")
response = requests.get(ASX_URL, headers=HEADERS)
print(f"Response status code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table")

processed_tickers = set()
announcements = []

if table:
    for tr in table.find_all("tr")[1:]:  # Skip header row
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        
        ticker = tds[0].text.strip()
        full_ticker = ticker + ".AX"
        
        if full_ticker not in TICKER_LIST:
            continue
        
        if not tds[2].find("img", alt="asterix"):
            continue
        
        date_cell = tds[1]
        date_lines = [line.strip() for line in date_cell.stripped_strings]
        date_time_str = f"{date_lines[0]} {date_lines[1]}" if len(date_lines) >= 2 else date_lines[0] if date_lines else ""
        date_time = parse_announcement_datetime(date_time_str)
        
        title_cell = tds[3]
        full_title_text = title_cell.get_text(separator=" ", strip=True)
        title = re.sub(r'\d+\s+pages?\s+\d+\.?\d*KB$', '', full_title_text).strip()
        
        score = calculate_sentiment_score(title)

        # ─── NEW: Strategy 1 & 2 Filters ──────────────────────────────

        # Skip weak non-earnings announcements
        if not is_earnings_announcement(title):
            if score < 3.0:
                continue

        # Apply momentum / technical filters (Strategy 2)
        if not passes_advanced_filters(full_ticker):
            continue

        # PEAD filter: require positive earnings surprise (Strategy 1)
        sue = approximate_sue(full_ticker)
        if np.isnan(sue) or sue <= 0.5:
            continue

        # Boost score for strong positive surprise
        score += min(sue * 1.5, 4.0)
        score = round(score, 2)

        # ──────────────────────────────────────────────────────────────
        
        announcements.append({
            "ticker": ticker,
            "title": title,
            "date_time": date_time,
            "sentiment_score": score
        })
        
        processed_tickers.add(full_ticker)

else:
    print("No announcements table found.")

no_match_tickers = TICKER_LIST - processed_tickers
announcements.sort(key=lambda x: x["sentiment_score"], reverse=True)

pdf_urls = get_pdf_urls_for_announcements(announcements)
short_interest_data = get_short_interest_for_announcements(announcements)

today_str = datetime.now(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d")
csv_filename = f"bullish_announcements_{today_str}.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["date_time", "ticker", "pdf_url", "short_interest", "ChangePct", "title", "sentiment_score"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    for idx, ann in enumerate(announcements, start=2):
        ticker = ann["ticker"]
        title = ann["title"]
        full_ticker = ticker + ".AX"
        short_interest = short_interest_data.get(full_ticker, "N/A")
        pdf_key = f"{ticker}_{title}"
        pdf_url = pdf_urls.get(pdf_key, "No PDF URL found")
        
        formula = f'=GOOGLEFINANCE("ASX:" & A{idx}, "changepct")'
        
        writer.writerow({
            "date_time": ann["date_time"].strftime("%d/%m/%Y %H:%M") if ann["date_time"] else "N/A",
            "ticker": ticker,
            "pdf_url": pdf_url,
            "short_interest": short_interest,
            "ChangePct": formula,
            "title": title,
            "sentiment_score": ann["sentiment_score"]
        })
    
    if no_match_tickers:
        writer.writerow({
            "date_time": "",
            "ticker": "",
            "pdf_url": "",
            "short_interest": "",
            "ChangePct": "",
            "title": "No Matching Announcements",
            "sentiment_score": ""
        })
        
        for ticker in sorted(no_match_tickers):
            writer.writerow({
                "date_time": "",
                "ticker": ticker,
                "pdf_url": "No PDF URL found",
                "short_interest": short_interest_data.get(ticker, "N/A"),
                "ChangePct": "",
                "title": "No price-sensitive announcements",
                "sentiment_score": 0
            })

print(f"Saved CSV file: {csv_filename}")

if announcements:
    top = announcements[:7]
    labels = [f"{a['ticker']} ({a['sentiment_score']}): {a['title']}" for a in top]
    scores = [a["sentiment_score"] for a in top]
    date_times = [f"{a['date_time'].strftime('%H:%M') if a['date_time'] else ''}" for a in top]
    
    plt.figure(figsize=(16, 12))
    bars = plt.barh(labels, scores, color=[('green' if s > 0 else 'red') for s in scores])
    plt.gca().invert_yaxis()
    plt.xlabel("Sentiment Score")
    plt.title(f"Top 7 ASX Announcements by Sentiment Score - {datetime.now(pytz.timezone('Australia/Sydney')).strftime('%d/%m/%Y')}")
    
    for i, label in enumerate(plt.gca().get_yticklabels()):
        wrapped_label = "\n".join(wrap(label.get_text(), 60))
        label.set_text(wrapped_label)
    
    plt.gca().set_yticklabels(plt.gca().get_yticklabels(), fontsize=8, ha='right')
    
    for bar, date_time_str in zip(bars, date_times):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 date_time_str.strip(), va='center', fontsize=8, weight='bold')
    
    plt.tight_layout()
    png_filename = f"sentiment_chart_{today_str}.png"
    plt.savefig(png_filename, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved chart file: {png_filename}")
else:
    print("No announcements found.")

if no_match_tickers:
    print("Tickers with no matching announcements:")
    for ticker in sorted(no_match_tickers):
        print(f"  {ticker}")
