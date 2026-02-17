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

# ASX announcement URL
ASX_URL = "https://www.asx.com.au/asx/v2/statistics/todayAnns.do"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# PLACEHOLDER: Your ticker list (add your actual tickers here)
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

# Biotech/Healthcare tickers to EXCLUDE (too volatile)
BIOTECH_EXCLUDE = {
    "IMU.AX", "PYC.AX", "NEU.AX", "CSL.AX", "RMD.AX", "COH.AX", "SHL.AX", 
    "RHC.AX", "CPU.AX", "DRR.AX", "BOT.AX", "CURE.AX", "DRUG.AX", "HLTH.AX"
    # Add more biotech/pharma tickers as needed
}

# Enhanced keywords focusing on UNEXPECTED POSITIVE results
SURPRISE_KEYWORDS = {
    # Extreme surprises (very high weight)
    "exceeds expectations": 4.0,
    "above expectations": 4.0,
    "beats expectations": 4.0,
    "significantly exceeds": 4.5,
    "well above": 4.0,
    "significantly above": 4.0,
    "surprise profit": 4.0,
    "unexpected profit": 4.0,
    
    # Takeover/M&A (high weight - concrete events)
    "takeover offer": 5.0,
    "acquisition offer": 5.0,
    "acquisition proposal": 4.5,
    "scheme of arrangement": 4.5,
    "takeover bid": 5.0,
    "buyout offer": 5.0,
    
    # Major contract wins (concrete business wins)
    "major contract": 3.5,
    "significant contract": 3.5,
    "contract awarded": 3.5,
    "wins contract": 3.5,
    "secures contract": 3.5,
    
    # Guidance upgrades (concrete improvement)
    "raises guidance": 4.0,
    "upgrades guidance": 4.0,
    "increased guidance": 4.0,
    "guidance upgrade": 4.0,
    "guidance raised": 4.0,
    
    # Strong financial beats
    "record profit": 3.5,
    "record earnings": 3.5,
    "record ebitda": 3.5,
    "record revenue": 3.2,
    "profit surge": 3.5,
    "earnings surge": 3.5,
    
    # Major discoveries (especially mining)
    "significant discovery": 3.8,
    "major discovery": 3.8,
    "high-grade": 3.5,
    "exceptional results": 3.5,
    "outstanding results": 3.5,
    
    # Production/operational surprises
    "production exceeds": 3.5,
    "output exceeds": 3.5,
    "ahead of schedule": 3.0,
    "early production": 3.0,
}

# Regular bullish keywords (moderate weight)
BULLISH_KEYWORDS = {
    # Financial
    "profit": 1.5,
    "earnings": 1.5,
    "revenue growth": 2.0,
    "strong revenue": 2.0,
    "cash flow": 1.8,
    "margin expansion": 2.0,
    
    # Operational
    "new contract": 2.0,
    "contract win": 2.0,
    "production increase": 2.0,
    "capacity expansion": 2.0,
    
    # Strategic
    "strategic partnership": 2.0,
    "market expansion": 2.0,
    "new market": 2.0,
    
    # Shareholder returns
    "dividend increase": 2.5,
    "special dividend": 2.8,
    "share buyback": 2.5,
}

# Exclude routine/expected announcements (these won't surprise anyone)
ROUTINE_ANNOUNCEMENTS = {
    "trading halt",
    "voluntary suspension",
    "appendix 4e",
    "appendix 3b",
    "change of director",
    "change in director",
    "cleansing notice",
    "change of registered",
    "notification of cessation",
    "becomes substantial",
    "ceases to be substantial",
    "daily fund update",
    "net tangible asset",
    "nta",
    "initial director's interest",
    "change of director's interest",
    "weekly investor update",
    "monthly investor update",
}

# Biotech-specific phrases to filter out
BIOTECH_KEYWORDS = {
    "clinical trial",
    "phase 1",
    "phase 2", 
    "phase 3",
    "phase i",
    "phase ii",
    "phase iii",
    "patient enrollment",
    "dose escalation",
    "trial results",
    "fda",
    "tga",
    "regulatory",
    "drug",
    "therapy",
    "treatment",
}

BEARISH_KEYWORDS = {
    "decline": -2.0,
    "loss": -2.5,
    "downgrade": -2.0,
    "miss": -2.5,
    "misses": -2.5,
    "below expectations": -3.0,
    "disappointing": -2.5,
    "weak": -2.0,
    "drop": -2.0,
    "fall": -2.0,
    "decrease": -2.0,
    "impairment": -2.5,
    "write-down": -2.5,
    "guidance downgrade": -3.0,
    "lowers guidance": -3.0,
    "suspends": -2.5,
}

NEGATION_WORDS = {"not", "no", "never", "none"}

# PDF URL scraping functions
HEADERS_PDF = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

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
    """Check if two titles are similar enough"""
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

def is_routine_announcement(title):
    """Check if announcement is routine/expected"""
    title_lower = title.lower()
    return any(phrase in title_lower for phrase in ROUTINE_ANNOUNCEMENTS)

def is_biotech_related(title):
    """Check if announcement contains biotech-related keywords"""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in BIOTECH_KEYWORDS)

def calculate_sentiment_score(title):
    """Enhanced sentiment calculation focusing on surprise factor"""
    title_lower = title.lower()
    score = 0.0

    # Check SURPRISE keywords first (highest priority)
    for phrase, weight in SURPRISE_KEYWORDS.items():
        if phrase in title_lower:
            score += weight
            print(f"  SURPRISE match: '{phrase}' (+{weight})")

    # Check regular bullish keywords
    for phrase, weight in BULLISH_KEYWORDS.items():
        if phrase in title_lower:
            score += weight

    # Check bearish keywords
    for phrase, weight in BEARISH_KEYWORDS.items():
        if phrase in title_lower:
            score += weight

    # Word-level analysis with negation
    words = re.findall(r'\b\w+\b', title_lower)
    for i, word in enumerate(words):
        is_negated = i > 0 and words[i-1] in NEGATION_WORDS

        # Only check single words, not phrases
        if word in BULLISH_KEYWORDS and len(word.split()) == 1:
            word_score = BULLISH_KEYWORDS[word]
            if is_negated:
                score -= word_score * 0.5
        elif word in BEARISH_KEYWORDS and len(word.split()) == 1:
            word_score = BEARISH_KEYWORDS[word]
            if is_negated:
                score -= word_score * 0.5
            else:
                score += word_score

    return round(score, 2)

def get_short_interest(ticker):
    """Get current short interest percentage for a ticker"""
    clean_ticker = ticker.replace('.AX', '')
    url = f"https://www.shortman.com.au/stock?q={clean_ticker}"

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
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

def get_short_interest_for_announcements(announcements):
    """Get short interest data for announcement tickers"""
    print("\n--- Getting short interest data ---")
    short_data = {}

    unique_tickers = set()
    for ann in announcements:
        unique_tickers.add(ann["ticker"] + ".AX")

    for ticker in unique_tickers:
        print(f"Getting short interest for {ticker}...")
        short_interest = get_short_interest(ticker)
        short_data[ticker] = short_interest
        print(f"  {ticker}: {short_interest}")
        time.sleep(0.5)

    return short_data

# Main execution
print("=" * 80)
print("ASX SENTIMENT ANALYZER - FILTERING FOR UNEXPECTED POSITIVE RESULTS")
print("=" * 80)
print(f"\nFetching from URL: {ASX_URL}")
response = requests.get(ASX_URL, headers=HEADERS)
print(f"Response status code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table")

announcements = []

if table:
    for tr in table.find_all("tr")[1:]:  # Skip header row
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        ticker = tds[0].text.strip()
        full_ticker = ticker + ".AX"

        # Filter 1: Must be in ticker list
        if full_ticker not in TICKER_LIST:
            continue

        # Filter 2: Exclude biotech stocks
        if full_ticker in BIOTECH_EXCLUDE:
            print(f"Excluding biotech: {full_ticker}")
            continue

        # Filter 3: Must be price-sensitive
        if not tds[2].find("img", alt="asterix"):
            continue

        # Extract date/time
        date_cell = tds[1]
        date_lines = [line.strip() for line in date_cell.stripped_strings]
        if len(date_lines) >= 2:
            date_time_str = f"{date_lines[0]} {date_lines[1]}"
        elif len(date_lines) == 1:
            date_time_str = date_lines[0]
        else:
            date_time_str = ""

        date_time = parse_announcement_datetime(date_time_str)

        # Extract and clean title
        title_cell = tds[3]
        full_title_text = title_cell.get_text(separator=" ", strip=True)
        title = re.sub(r'\d+\s+pages?\s+\d+\.?\d*KB$', '', full_title_text).strip()

        # Filter 4: Exclude routine announcements
        if is_routine_announcement(title):
            print(f"Excluding routine: {ticker} - {title[:50]}")
            continue

        # Filter 5: Exclude biotech-related content
        if is_biotech_related(title):
            print(f"Excluding biotech content: {ticker} - {title[:50]}")
            continue

        # Calculate sentiment
        print(f"\nAnalyzing: {ticker} - {title}")
        score = calculate_sentiment_score(title)
        print(f"  Final score: {score}")

        # Filter 6: Only include positive sentiment
        if score <= 0:
            print(f"  Excluding: non-positive sentiment")
            continue

        announcements.append({
            "ticker": ticker,
            "title": title,
            "date_time": date_time,
            "sentiment_score": score
        })

else:
    print("No announcements table found.")

# Sort by sentiment score and take TOP 5 ONLY
announcements.sort(key=lambda x: x["sentiment_score"], reverse=True)
top_announcements = announcements[:5]  # LIMIT TO 5

print("\n" + "=" * 80)
print(f"FOUND {len(announcements)} POSITIVE ANNOUNCEMENTS")
print(f"OUTPUTTING TOP {len(top_announcements)} TO CSV")
print("=" * 80)

for i, ann in enumerate(top_announcements, 1):
    print(f"{i}. {ann['ticker']}: {ann['title']} (Score: {ann['sentiment_score']})")

# Get PDF URLs and short interest for top 5 only
if top_announcements:
    pdf_urls = get_pdf_urls_for_announcements(top_announcements)
    short_interest_data = get_short_interest_for_announcements(top_announcements)
else:
    pdf_urls = {}
    short_interest_data = {}

# CSV writing section - TOP 5 ONLY
today_str = datetime.now(pytz.timezone("Australia/Sydney")).strftime("%Y%m%d")
csv_filename = f"bullish_announcements_{today_str}.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["rank", "date_time", "ticker", "pdf_url", "short_interest", "ChangePct", "title", "sentiment_score"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for idx, ann in enumerate(top_announcements, start=1):
        ticker = ann["ticker"]
        title = ann["title"]
        full_ticker = ticker + ".AX"
        short_interest = short_interest_data.get(full_ticker, "N/A")
        
        pdf_key = f"{ticker}_{title}"
        pdf_url = pdf_urls.get(pdf_key, "No PDF URL found")

        formula = f'=GOOGLEFINANCE("ASX:" & C{idx+1}, "changepct")'

        writer.writerow({
            "rank": idx,
            "date_time": ann["date_time"].strftime("%d/%m/%Y %H:%M") if ann["date_time"] else "N/A",
            "ticker": ticker,
            "pdf_url": pdf_url,
            "short_interest": short_interest,
            "ChangePct": formula,
            "title": title,
            "sentiment_score": ann["sentiment_score"]
        })

print(f"\n✓ Saved CSV file: {csv_filename}")

# Generate chart for top 5
if top_announcements:
    labels = [f"{a['ticker']} ({a['sentiment_score']}): {a['title']}" for a in top_announcements]
    scores = [a["sentiment_score"] for a in top_announcements]
    date_times = [f"{a['date_time'].strftime('%H:%M') if a['date_time'] else ''}" for a in top_announcements]

    plt.figure(figsize=(16, 10))
    bars = plt.barh(labels, scores, color='green')
    plt.gca().invert_yaxis()
    plt.xlabel("Sentiment Score", fontsize=12, fontweight='bold')
    plt.title(f"Top 5 Unexpected Positive ASX Announcements - {datetime.now(pytz.timezone('Australia/Sydney')).strftime('%d/%m/%Y')}", 
              fontsize=14, fontweight='bold')

    # Wrap long labels
    for i, label in enumerate(plt.gca().get_yticklabels()):
        wrapped_label = "\n".join(wrap(label.get_text(), 70))
        label.set_text(wrapped_label)

    plt.gca().set_yticklabels(plt.gca().get_yticklabels(), fontsize=9, ha='right')

    # Add time annotations
    for bar, date_time_str in zip(bars, date_times):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 date_time_str.strip(), va='center', fontsize=9, weight='bold')

    plt.tight_layout()
    png_filename = f"sentiment_chart_{today_str}.png"
    plt.savefig(png_filename, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"✓ Saved chart file: {png_filename}")
else:
    print("\nNo qualifying announcements found.")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)