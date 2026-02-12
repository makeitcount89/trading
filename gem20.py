from dotenv import load_dotenv
import os
import requests
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
import threading
import io
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import base64
import time
import tempfile
from flask_cors import CORS
import yfinance as yf
import numpy as np

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://spage.site"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_routes():
    app.logger.debug('Registered routes: %s', [rule.rule for rule in app.url_map.iter_rules()])

with app.app_context():
    log_routes()

@app.route('/<path:filename>')
def serve_asx_file(filename):
    app.logger.debug(f'Serving ASX file: {filename}')
    try:
        return send_from_directory('.', filename)
    except FileNotFoundError:
        app.logger.error(f'File not found: {filename}')
        return jsonify({"error": f"CSV file {filename} not found"}), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_file(path):
    try:
        return send_from_directory('.', path)
    except FileNotFoundError:
        app.logger.error(f'File not found: {path}')
        return jsonify({"error": f"File {path} not found"}), 404

class EnhancedFinancialDataManager:
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}

    def get_intraday_data(self, ticker, announcement_date=None):
        try:
            if announcement_date is None:
                announcement_date = datetime.today().date()

            cache_key = f"{ticker}_intraday_{announcement_date}"
            if cache_key in self.cache:
                if datetime.now() < self.cache_expiry.get(cache_key, datetime.min):
                    return self.cache[cache_key]

            asx_ticker = f"{ticker}.AX"
            stock = yf.Ticker(asx_ticker)

            start_date = announcement_date
            end_date = announcement_date + timedelta(days=1)

            hist = stock.history(start=start_date, end=end_date, interval="1h")

            if hist.empty:
                app.logger.warning(f"No intraday data available for {ticker} on {announcement_date}")
                return None

            intraday_data = {
                'timestamps': [ts.strftime('%H:%M') for ts in hist.index],
                'prices': hist['Close'].tolist(),
                'volumes': hist['Volume'].tolist(),
                'open': hist['Open'].iloc[0] if len(hist) > 0 else None,
                'close': hist['Close'].iloc[-1] if len(hist) > 0 else None,
                'high': hist['High'].max(),
                'low': hist['Low'].min(),
                'date': announcement_date.strftime('%Y-%m-%d')
            }

            if intraday_data['open'] and intraday_data['close']:
                intraday_data['change_pct'] = ((intraday_data['close'] - intraday_data['open']) / intraday_data['open']) * 100
            else:
                intraday_data['change_pct'] = 0

            self.cache[cache_key] = intraday_data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)

            app.logger.info(f"Fetched {len(hist)} hourly data points for {ticker} on {announcement_date}")
            return intraday_data

        except Exception as e:
            app.logger.error(f"Error fetching intraday data for {ticker}: {e}")
            return None

    def get_comprehensive_stock_data(self, ticker):
        try:
            cache_key = f"{ticker}_comprehensive"
            if cache_key in self.cache:
                if datetime.now() < self.cache_expiry.get(cache_key, datetime.min):
                    return self.cache[cache_key]

            asx_ticker = f"{ticker}.AX"
            stock = yf.Ticker(asx_ticker)

            hist = stock.history(period="3mo")
            info = stock.info

            if hist.empty:
                return self._get_default_data()

            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price

            daily_change = (current_price - previous_close) / previous_close * 100
            five_day_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6] * 100 if len(hist) >= 6 else 0
            thirty_day_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-31]) / hist['Close'].iloc[-31] * 100 if len(hist) >= 31 else 0

            avg_volume = hist['Volume'].tail(20).mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) * 100

            fifty_two_week_high = hist['High'].max()
            fifty_two_week_low = hist['Low'].min()
            price_to_52w_high = (current_price / fifty_two_week_high) * 100
            price_to_52w_low = (current_price / fifty_two_week_low) * 100

            rsi = self._calculate_rsi(hist['Close'])

            sma_20 = hist['Close'].tail(20).mean()
            sma_50 = hist['Close'].tail(50).mean()
            price_vs_sma20 = ((current_price - sma_20) / sma_20) * 100
            price_vs_sma50 = ((current_price - sma_50) / sma_50) * 100

            market_cap = info.get('marketCap', 'N/A')
            pe_ratio = info.get('trailingPE', 'N/A')
            pb_ratio = info.get('priceToBook', 'N/A')
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            beta = info.get('beta', 'N/A')

            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')

            comprehensive_data = {
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "daily_change_pct": round(daily_change, 2),
                "five_day_change_pct": round(five_day_change, 2),
                "thirty_day_change_pct": round(thirty_day_change, 2),
                "current_volume": int(current_volume),
                "avg_volume_20d": int(avg_volume),
                "volume_ratio": round(volume_ratio, 2),
                "rsi_14": round(rsi, 2) if not pd.isna(rsi) else 'N/A',
                "price_vs_sma20_pct": round(price_vs_sma20, 2),
                "price_vs_sma50_pct": round(price_vs_sma50, 2),
                "volatility_annual_pct": round(volatility, 2),
                "fifty_two_week_high": round(fifty_two_week_high, 2),
                "fifty_two_week_low": round(fifty_two_week_low, 2),
                "price_to_52w_high_pct": round(price_to_52w_high, 2),
                "price_to_52w_low_pct": round(price_to_52w_low, 2),
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "dividend_yield_pct": round(dividend_yield, 2),
                "beta": beta,
                "sector": sector,
                "industry": industry,
                "data_quality": "high"
            }

            self.cache[cache_key] = comprehensive_data
            self.cache_expiry[cache_key] = datetime.now() + timedelta(minutes=30)

            return comprehensive_data

        except Exception as e:
            app.logger.error(f"Error fetching comprehensive data for {ticker}: {e}")
            return self._get_default_data()

    def _calculate_rsi(self, prices, window=14):
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return pd.NaN

    def _get_default_data(self):
        return {
            "current_price": 'N/A',
            "previous_close": 'N/A',
            "daily_change_pct": 0,
            "five_day_change_pct": 0,
            "thirty_day_change_pct": 0,
            "current_volume": 'N/A',
            "avg_volume_20d": 'N/A',
            "volume_ratio": 'N/A',
            "rsi_14": 'N/A',
            "price_vs_sma20_pct": 'N/A',
            "price_vs_sma50_pct": 'N/A',
            "volatility_annual_pct": 'N/A',
            "fifty_two_week_high": 'N/A',
            "fifty_two_week_low": 'N/A',
            "price_to_52w_high_pct": 'N/A',
            "price_to_52w_low_pct": 'N/A',
            "market_cap": 'N/A',
            "pe_ratio": 'N/A',
            "pb_ratio": 'N/A',
            "dividend_yield_pct": 0,
            "beta": 'N/A',
            "sector": 'N/A',
            "industry": 'N/A',
            "data_quality": "low"
        }

class GoogleSheetsManager:
    def __init__(self):
        self.spreadsheet_id = "1Nbk1IyavrHbAETxSB_d3TfTjSj2EHsNuwoEHke3qGmU"

    def append_to_sheet(self, data_rows):
        try:
            sheets_script_url = os.getenv('GOOGLE_SHEETS_SCRIPT_URL')
            if not sheets_script_url:
                app.logger.error("GOOGLE_SHEETS_SCRIPT_URL not set in environment")
                return False

            headers = [
                'Date', 'Ticker', 'Short%', 'Expected Daily Change %', 'Daily Change %',
                'Weekly Change %', 'Title', 'Bullish Score', 'PDF URL', 'Surprise Level',
                'Key Positive Factors', 'Financial Highlights', 'Future Outlook',
                'Market Impact', 'Risk Factors', 'Market Expectations Comparison',
                'Reasoning Summary', 'Prediction Confidence', 'Current Price', 'Market Cap',
                'PE Ratio', 'Volume Ratio', 'RSI', 'Price vs SMA20%', 'Volatility%',
                'Sector', 'Industry', '52W High%', '52W Low%', 'Beta'
            ]

            payload = {
                'spreadsheetId': self.spreadsheet_id,
                'headers': headers,
                'data': data_rows
            }

            resp = requests.post(sheets_script_url, json=payload, timeout=60)
            resp.raise_for_status()

            result = resp.json()
            if result.get('success'):
                app.logger.info(f"Successfully added {len(data_rows)} rows to Google Sheets")
                return True
            else:
                app.logger.error(f"Google Sheets update failed: {result.get('error', 'Unknown error')}")
                return False

        except requests.exceptions.RequestException as e:
            app.logger.error(f"HTTP Request Error when updating Google Sheets: {e}")
            return False
        except Exception as e:
            app.logger.error(f"Error appending to Google Sheets: {e}")
            return False

class EnhancedGeminiAnalyzer:
    def __init__(self):
        self.model = self.setup_gemini()
        self.current_analyses = []
        self.analysis_status = {"status": "idle", "progress": 0, "message": ""}
        self.auto_analysis_running = False
        self.sheets_manager = GoogleSheetsManager()
        self.financial_manager = EnhancedFinancialDataManager()
        self.last_sheets_update = None
        self.announcement_date = datetime.today().date()
        self.start_auto_analysis()

    def setup_gemini(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY environment variable not set!")
        genai.configure(api_key=api_key)

        try:
            return genai.GenerativeModel('gemini-3-flash-preview')  # 2026 recommendation: prefer 1.5 over 2.5-flash if available
        except Exception as e:
            app.logger.warning(f"Failed to load gemini-1.5-flash, falling back: {e}")
            try:
                return genai.GenerativeModel('gemini-1.5-flash-latest')
            except Exception as e2:
                raise Exception(f"Gemini model init failed: {e2}")

    def start_auto_analysis(self):
        if not self.auto_analysis_running:
            self.auto_analysis_running = True
            thread = threading.Thread(target=self.auto_analysis_once, daemon=True)
            thread.start()
            app.logger.info("Started one-time automatic enhanced analysis thread")

    def find_latest_csv(self, base_url="https://spage.site/asx/"):
        today = datetime.today().date()
        self.announcement_date = today
        date_str = today.strftime("%Y%m%d")
        filename = f"bullish_announcements_{date_str}.csv"
        if os.path.exists(filename):
            app.logger.debug(f'Found local CSV: {filename}')
            return f"file://{os.path.abspath(filename)}"
        url = f"{base_url}{filename}"
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code == 200:
                app.logger.debug(f'Found remote CSV: {url}')
                return url
            else:
                app.logger.debug(f'Remote CSV {url} returned status: {resp.status_code}')
        except requests.RequestException as e:
            app.logger.debug(f'Failed to access remote CSV {url}: {str(e)}')
        app.logger.error(f"No CSV found for {date_str} locally or remotely")
        return None

    def load_announcements_data(self, csv_source):
        try:
            if csv_source.startswith('file://'):
                local_path = csv_source.replace('file://', '')
                if not os.path.exists(local_path):
                    app.logger.error(f"Local CSV file not found: {local_path}")
                    return None
                df = pd.read_csv(local_path)
                app.logger.debug(f'Loaded local CSV with {len(df)} rows')
            else:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(csv_source, headers=headers, timeout=10)
                resp.raise_for_status()
                df = pd.read_csv(io.StringIO(resp.text))
                app.logger.debug(f'Loaded remote CSV with {len(df)} rows')

            if df.empty:
                app.logger.error(f"CSV is empty: {csv_source}")
                return None

            allowed_file = 'value.csv'
            if not os.path.exists(allowed_file):
                app.logger.error(f"Allowed tickers file not found: {allowed_file}")
                return None

            allowed_df = pd.read_csv(allowed_file)
            allowed_tickers = set(
                allowed_df['Symbol']
                .dropna()
                .str.strip()
                .str.upper()
            )
            app.logger.info(f"Loaded {len(allowed_tickers)} allowed tickers from {allowed_file}")

            valid_announcements = df[
                (df['pdf_url'].notna()) &
                (df['pdf_url'] != 'No PDF URL found') &
                (df['pdf_url'].str.startswith('http')) &
                (df['ticker'].str.strip().str.upper().isin(allowed_tickers))
            ].copy()

            app.logger.info(f"After watchlist filter: {len(valid_announcements)} announcements")

            # Pre-AI hard filters to reduce Gemini calls
            def quick_fundamentals(tkr):
                try:
                    s = yf.Ticker(f"{tkr}.AX")
                    info = s.info
                    mc = info.get('marketCap', np.nan)

                    hist = s.history(period="5d")
                    if not hist.empty:
                        last_close = hist['Close'].iloc[-1]
                        last_vol = hist['Volume'].iloc[-1]
                        yesterday_value = last_close * last_vol if pd.notna(last_close) and pd.notna(last_vol) else np.nan
                    else:
                        yesterday_value = np.nan

                    return mc, yesterday_value
                except:
                    return np.nan, np.nan

            keep_mask = pd.Series(True, index=valid_announcements.index)
            dropped_reasons = {'liquidity': 0, 'market_cap': 0, 'capital_raise': 0, 'biotech_trial': 0}

            for idx, row in valid_announcements.iterrows():
                tkr = row['ticker']
                title_lower = str(row.get('title', '')).lower()

                mc, yest_value = quick_fundamentals(tkr)

                # Liquidity > 300k AUD yesterday
                if pd.isna(yest_value) or yest_value < 300000:
                    keep_mask[idx] = False
                    dropped_reasons['liquidity'] += 1
                    continue

                # Market cap 50M – 1.5B AUD
                if pd.isna(mc) or not (50000000 <= mc <= 1500000000):
                    keep_mask[idx] = False
                    dropped_reasons['market_cap'] += 1
                    continue

                # Capital raise keywords
                capital_keywords = [
                    'placement', 'entitlement', 'rights issue', 'spp', 'share purchase plan',
                    'capital raising', 'capital raise', 'prospectus', 'offer', 'dilution',
                    'renounceable', 'non-renounceable', 'equity raising', 'bookbuild'
                ]
                if any(kw in title_lower for kw in capital_keywords):
                    keep_mask[idx] = False
                    dropped_reasons['capital_raise'] += 1
                    continue

                # Early biotech / trial keywords
                biotech_keywords = [
                    'phase 1', 'phase 2', 'phase 3', 'phase ii', 'phase iii',
                    'clinical trial', 'trial result', 'dosing', 'enrolment', 'cohort',
                    'first patient', 'top-line data', 'interim data', 'tga approval'
                ]
                if any(kw in title_lower for kw in biotech_keywords):
                    keep_mask[idx] = False
                    dropped_reasons['biotech_trial'] += 1
                    continue

            valid_announcements = valid_announcements[keep_mask].copy()

            app.logger.info(
                f"After pre-AI filters: {len(valid_announcements)} remain "
                f"(dropped: liquidity={dropped_reasons['liquidity']}, "
                f"market_cap={dropped_reasons['market_cap']}, "
                f"capital_raise={dropped_reasons['capital_raise']}, "
                f"biotech_trial={dropped_reasons['biotech_trial']})"
            )

            if valid_announcements.empty:
                app.logger.warning(f"No announcements remain after filtering")
                return None

            if 'sentiment_score' in df.columns:
                valid_announcements = valid_announcements.sort_values('sentiment_score', ascending=False)

            app.logger.info(f"Ready to analyze {len(valid_announcements)} stocks")
            return valid_announcements

        except Exception as e:
            app.logger.error(f"Error loading CSV {csv_source}: {str(e)}")
            return None

    def download_pdf(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(resp.content)
                return tmp_file.name
        except Exception as e:
            app.logger.error(f"Error downloading PDF: {e}")
            return None

    def analyze_pdf_with_gemini(self, pdf_path, ticker, title, financial_data):
        retries = 5
        delay = 5
        for i in range(retries):
            try:
                try:
                    uploaded_file = genai.upload_file(
                        path=pdf_path,
                        display_name=f"{ticker}_announcement.pdf"
                    )

                    while uploaded_file.state.name == "PROCESSING":
                        time.sleep(2)
                        uploaded_file = genai.get_file(uploaded_file.name)

                    if uploaded_file.state.name == "FAILED":
                        raise Exception("File processing failed")

                    file_ref = uploaded_file
                    use_file_api = True
                    app.logger.info(f"Successfully uploaded PDF for {ticker} using File API")

                except Exception as upload_error:
                    app.logger.warning(f"File upload failed for {ticker}, using inline: {upload_error}")
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()

                    if len(pdf_data) > 20 * 1024 * 1024:
                        app.logger.error(f"PDF too large for {ticker}: {len(pdf_data)} bytes")
                        return None

                    file_ref = {
                        'mime_type': 'application/pdf',
                        'data': pdf_data
                    }
                    use_file_api = False
                    app.logger.info(f"Using inline PDF data for {ticker} ({len(pdf_data)} bytes)")

                time.sleep(2)

                def format_value(value, suffix=''):
                    if isinstance(value, (int, float)) and not pd.isna(value):
                        if suffix == '$':
                            return f"${value:,.2f}"
                        elif suffix == '%':
                            return f"{value:.2f}%"
                        elif suffix == 'K':
                            return f"{value:,}"
                        return str(value)
                    return 'N/A'

                financial_summary = f"""
**Current Financial Position:**
- Ticker: {ticker}
- Current Price: {format_value(financial_data['current_price'], '$')}
- Previous Close: {format_value(financial_data['previous_close'], '$')}
- Daily Change: {format_value(financial_data['daily_change_pct'], '%')}
- 5-Day Change: {format_value(financial_data['five_day_change_pct'], '%')}
- 30-Day Change: {format_value(financial_data['thirty_day_change_pct'], '%')}
**Technical Indicators:**
- RSI (14-day): {format_value(financial_data['rsi_14'])}
- Price vs 20-day SMA: {format_value(financial_data['price_vs_sma20_pct'], '%')}
- Price vs 50-day SMA: {format_value(financial_data['price_vs_sma50_pct'], '%')}
- Annual Volatility: {format_value(financial_data['volatility_annual_pct'], '%')}
**Volume Analysis:**
- Current Volume: {format_value(financial_data['current_volume'], 'K')}
- 20-Day Avg Volume: {format_value(financial_data['avg_volume_20d'], 'K')}
- Volume Ratio: {format_value(financial_data['volume_ratio'])}
**Valuation Metrics:**
- Market Cap: {format_value(financial_data['market_cap'], '$')}
- P/E Ratio: {format_value(financial_data['pe_ratio'])}
- P/B Ratio: {format_value(financial_data['pb_ratio'])}
- Dividend Yield: {format_value(financial_data['dividend_yield_pct'], '%')}
- Beta: {format_value(financial_data['beta'])}
**Market Position:**
- Sector: {financial_data['sector']}
- Industry: {financial_data['industry']}
- 52W High Distance: {format_value(financial_data['price_to_52w_high_pct'], '%')}
- 52W Low Distance: {format_value(financial_data['price_to_52w_low_pct'], '%')}
"""

                prompt = f"""
Analyze the attached PDF announcement for stock ticker {ticker} titled "{title}".
{financial_summary}
**Analysis Instructions:**
As a sophisticated financial analyst, perform a comprehensive analysis considering:
1. Content Analysis: Extract key financial metrics, operational updates, strategic initiatives, and material changes.
2. Technical Context: Consider RSI levels, price relative to moving averages, momentum, volume patterns.
3. Market Context: How this fits broader market/sector conditions and valuation relative to peers.
4. Surprise Factor: Does this deviate significantly from expectations?
5. Risk Assessment: Identify risks that could block the predicted move.
6. Quantitative Prediction: Estimate next-day % change based on news magnitude, historical reactions, technicals, sentiment.

Output **strictly** in JSON with these exact keys:
{{
  "bullish_score": <1-10 integer>,
  "key_positive_factors": <string>,
  "financial_highlights": <string>,
  "future_outlook": <string>,
  "market_impact": <string>,
  "risk_factors": <string>,
  "market_expectations_comparison": <string>,
  "surprise_level": <"low" | "medium" | "high">,
  "expected_daily_change_pct": <float>,
  "prediction_confidence": <1-5 integer>,
  "reasoning_summary": <string>
}}
"""

                response = self.model.generate_content([file_ref, prompt])

                if use_file_api:
                    try:
                        genai.delete_file(uploaded_file.name)
                        app.logger.debug(f"Cleaned up file for {ticker}")
                    except:
                        pass

                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3].strip()

                analysis_json = json.loads(response_text)
                app.logger.info(f"Successfully analyzed {ticker}")
                return analysis_json

            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "quota" in error_str or "rate limit" in error_str:
                    app.logger.warning(f"Rate limit hit for {ticker}. Waiting {delay}s ({i+1}/{retries})")
                    time.sleep(delay)
                    delay = min(delay * 2, 60)
                else:
                    app.logger.error(f"Analysis error for {ticker} (attempt {i+1}): {e}")
                    if i == retries - 1:
                        return None
                    time.sleep(5)

        app.logger.error(f"Failed to analyze {ticker} after {retries} attempts")
        return None

    def create_results_csv(self):
        try:
            csv_data = []
            for item in self.current_analyses:
                analysis = item['analysis']
                financial_data = item['financial_data']
                csv_row = {
                    'Date': datetime.today().strftime("%Y-%m-%d"),
                    'Ticker': item['ticker'],
                    'Short%': item.get('short_interest', ''),
                    'Expected Daily Change %': analysis.get('expected_daily_change_pct', ''),
                    'Daily Change %': '',
                    'Weekly Change %': '',
                    'Title': item['title'],
                    'Bullish Score': analysis.get('bullish_score', ''),
                    'PDF URL': item['url'],
                    'Surprise Level': analysis.get('surprise_level', ''),
                    'Key Positive Factors': analysis.get('key_positive_factors', ''),
                    'Financial Highlights': analysis.get('financial_highlights', ''),
                    'Future Outlook': analysis.get('future_outlook', ''),
                    'Market Impact': analysis.get('market_impact', ''),
                    'Risk Factors': analysis.get('risk_factors', ''),
                    'Market Expectations Comparison': analysis.get('market_expectations_comparison', ''),
                    'Reasoning Summary': analysis.get('reasoning_summary', ''),
                    'Prediction Confidence': analysis.get('prediction_confidence', ''),
                    'Current Price': financial_data.get('current_price', ''),
                    'Market Cap': financial_data.get('market_cap', ''),
                    'PE Ratio': financial_data.get('pe_ratio', ''),
                    'Volume Ratio': financial_data.get('volume_ratio', ''),
                    'RSI': financial_data.get('rsi_14', ''),
                    'Price vs SMA20%': financial_data.get('price_vs_sma20_pct', ''),
                    'Volatility%': financial_data.get('volatility_annual_pct', ''),
                    'Sector': financial_data.get('sector', ''),
                    'Industry': financial_data.get('industry', ''),
                    '52W High%': financial_data.get('price_to_52w_high_pct', ''),
                    '52W Low%': financial_data.get('price_to_52w_low_pct', ''),
                    'Beta': financial_data.get('beta', '')
                }
                csv_data.append(csv_row)

            df = pd.DataFrame(csv_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            csv_base64 = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
            return csv_base64, csv_content
        except Exception as e:
            app.logger.error(f"Error creating CSV: {e}")
            return None, None

    def append_to_google_sheets(self):
        try:
            if not self.current_analyses:
                app.logger.warning("No analyses to append")
                return False

            current_hash = hash(str(sorted([(item['ticker'], item['title']) for item in self.current_analyses])))
            if self.last_sheets_update == current_hash:
                app.logger.info("Data already sent to Sheets - skipping")
                return True

            data_rows = []
            current_date = datetime.today().strftime("%Y-%m-%d")

            for item in self.current_analyses:
                analysis = item['analysis']
                fd = item['financial_data']

                row = [
                    current_date,
                    item['ticker'],
                    item.get('short_interest', ''),
                    analysis.get('expected_daily_change_pct', ''),
                    '=(INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999)), 2) - INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999)) - 1, 2)) / INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999-7, A999)) - 1, 2) * 100',
                    '=(INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999+4-2, A999+4), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999+4-2, A999+4)), 2) - INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999-3, A999-1), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999-3, A999-1)), 2)) / INDEX(GOOGLEFINANCE("ASX:" & B999, "close", A999-3, A999-1), ROWS(GOOGLEFINANCE("ASX:" & B999, "close", A999-3, A999-1)), 2) * 100',
                    item['title'],
                    analysis.get('bullish_score', ''),
                    item['url'],
                    analysis.get('surprise_level', ''),
                    analysis.get('key_positive_factors', ''),
                    analysis.get('financial_highlights', ''),
                    analysis.get('future_outlook', ''),
                    analysis.get('market_impact', ''),
                    analysis.get('risk_factors', ''),
                    analysis.get('market_expectations_comparison', ''),
                    analysis.get('reasoning_summary', ''),
                    analysis.get('prediction_confidence', ''),
                    fd.get('current_price', ''),
                    fd.get('market_cap', ''),
                    fd.get('pe_ratio', ''),
                    fd.get('volume_ratio', ''),
                    fd.get('rsi_14', ''),
                    fd.get('price_vs_sma20_pct', ''),
                    fd.get('volatility_annual_pct', ''),
                    fd.get('sector', ''),
                    fd.get('industry', ''),
                    fd.get('price_to_52w_high_pct', ''),
                    fd.get('price_to_52w_low_pct', ''),
                    fd.get('beta', '')
                ]
                data_rows.append(row)

            success = self.sheets_manager.append_to_sheet(data_rows)
            if success:
                self.last_sheets_update = current_hash
                app.logger.info(f"Appended {len(data_rows)} rows to Google Sheets")
            return success

        except Exception as e:
            app.logger.error(f"Error appending to Google Sheets: {e}")
            return False

    def send_email_summary(self, summary):
        script_url = os.getenv('GOOGLE_APP_SCRIPT_URL')
        if not script_url:
            app.logger.error("GOOGLE_APP_SCRIPT_URL not set")
            return

        try:
            csv_base64, _ = self.create_results_csv()
            if csv_base64 is None:
                return

            today = datetime.today().strftime("%Y%m%d")
            payload = {
                'summary': summary,
                'csv_attachment': csv_base64,
                'csv_filename': f"bullish_analysis_{today}.csv"
            }

            resp = requests.post(script_url, json=payload, timeout=60)
            resp.raise_for_status()
            app.logger.info("Email summary sent")
        except Exception as e:
            app.logger.error(f"Email send failed: {e}")

    def auto_analysis_once(self):
        try:
            if self.analysis_status["status"] in ["idle", "complete"]:
                csv_source = self.find_latest_csv()
                if csv_source:
                    df = self.load_announcements_data(csv_source)
                    if df is not None and not df.empty:
                        if hasattr(self, 'last_analysis_date') and self.last_analysis_date == datetime.today().strftime("%Y-%m-%d"):
                            app.logger.info("Analysis already done today")
                            return
                        app.logger.info(f"Starting analysis of {len(df)} filtered announcements")
                        self.analyze_announcements_async(df, len(df))
        except Exception as e:
            app.logger.error(f"Auto analysis error: {e}")
        finally:
            self.auto_analysis_running = False

    def analyze_announcements_async(self, df, max_analyze, user_question=None):
        self.analysis_status = {"status": "running", "progress": 0, "message": "Starting analysis..."}
        self.current_analyses = []
        valid_announcements = df.head(max_analyze)
        total = len(valid_announcements)

        for idx, (_, row) in enumerate(valid_announcements.iterrows()):
            ticker = row['ticker']
            title = row['title']
            pdf_url = row['pdf_url']
            short_interest = row.get('short_interest', '')

            self.analysis_status["message"] = f"Analyzing {ticker}: {title}"
            self.analysis_status["progress"] = int((idx / total) * 70)

            financial_data = self.financial_manager.get_comprehensive_stock_data(ticker)
            intraday_data = self.financial_manager.get_intraday_data(ticker, self.announcement_date)

            self.analysis_status["progress"] = int((idx / total) * 80)

            pdf_path = self.download_pdf(pdf_url)
            if pdf_path:
                analysis = self.analyze_pdf_with_gemini(pdf_path, ticker, title, financial_data)
                if analysis:
                    self.current_analyses.append({
                        'ticker': ticker,
                        'title': title,
                        'url': pdf_url,
                        'short_interest': short_interest,
                        'financial_data': financial_data,
                        'intraday_data': intraday_data,
                        'analysis': analysis
                    })
                try:
                    os.unlink(pdf_path)
                except:
                    pass

        self.current_analyses.sort(key=lambda x: x['analysis'].get('expected_daily_change_pct', 0), reverse=True)

        sheets_success = self.append_to_google_sheets()

        summary = "Bullish Announcements Summary:\n\n"
        for i, item in enumerate(self.current_analyses, 1):
            a = item['analysis']
            f = item['financial_data']
            summary += f"{i}. {item['ticker']} - {item['title']}\n"
            summary += f"  Expected: {a.get('expected_daily_change_pct', 'N/A')}%\n"
            summary += f"  Bullish: {a.get('bullish_score', 'N/A')}\n"
            summary += f"  Surprise: {a.get('surprise_level', 'N/A')}\n"
            summary += f"  Confidence: {a.get('prediction_confidence', 'N/A')}\n"
            summary += f"  Price: ${f.get('current_price', 'N/A')}\n"
            summary += "-" * 50 + "\n"

        if sheets_success:
            summary += "\nSaved to Google Sheets ✓"
        else:
            summary += "\nFailed to save to Sheets"

        if self.current_analyses:
            self.send_email_summary(summary)
            self.last_analysis_date = datetime.today().strftime("%Y-%m-%d")

        self.analysis_status = {
            "status": "complete",
            "progress": 100,
            "message": f"Analysis complete – {len(self.current_analyses)} stocks processed"
        }

# Flask API endpoints
@app.route('/api/get_announcements')
def get_announcements():
    global analyzer
    csv_source = analyzer.find_latest_csv()
    if not csv_source:
        return jsonify({"error": "No CSV found"}), 404
    df = analyzer.load_announcements_data(csv_source)
    if df is None or df.empty:
        return jsonify({"error": "No valid announcements"}), 404

    announcements = []
    for _, row in df.head(20).iterrows():
        announcements.append({
            'ticker': row['ticker'],
            'title': row['title'],
            'sentiment_score': row.get('sentiment_score', 'N/A'),
            'short_interest': row.get('short_interest', 'N/A'),
            'pdf_url': row['pdf_url']
        })
    return jsonify({
        "csv_source": csv_source,
        "total_count": len(df),
        "announcements": announcements
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global analyzer
    data = request.get_json()
    max_analyze = data.get('max_analyze', 10)
    if analyzer.analysis_status["status"] != "running":
        thread = threading.Thread(target=analyzer.analyze_announcements_async, args=(analyzer.load_announcements_data(analyzer.find_latest_csv()), max_analyze))
        thread.start()
        return jsonify({"message": "Analysis started"})
    return jsonify({"message": "Analysis already running"})

@app.route('/api/status')
def get_status():
    global analyzer
    return jsonify(analyzer.analysis_status)

@app.route('/api/results')
def get_results():
    global analyzer
    results = []
    for item in analyzer.current_analyses:
        results.append({
            'ticker': item['ticker'],
            'title': item['title'],
            'url': item['url'],
            'short_interest': item.get('short_interest', ''),
            'analysis': item['analysis'],
            'financial_data': item.get('financial_data', {}),
            'intraday_data': item.get('intraday_data', None)
        })
    return jsonify({
        "analyzed_count": len(analyzer.current_analyses),
        "results": results
    })

@app.route('/api/financial_data/<ticker>')
def get_financial_data(ticker):
    global analyzer
    data = analyzer.financial_manager.get_comprehensive_stock_data(ticker)
    return jsonify({"ticker": ticker, "financial_data": data})

@app.route('/api/intraday/<ticker>')
def get_intraday_data(ticker):
    global analyzer
    date_str = request.args.get('date')
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else analyzer.announcement_date
    data = analyzer.financial_manager.get_intraday_data(ticker, target_date)
    if data:
        return jsonify({"ticker": ticker, "date": target_date.strftime('%Y-%m-%d'), "intraday_data": data})
    return jsonify({"error": "No intraday data"}), 404

if __name__ == "__main__":
    analyzer = EnhancedGeminiAnalyzer()

    while analyzer.auto_analysis_running:
        time.sleep(1)

    print("Analysis thread finished. Server running...")
    app.run(debug=True, host='0.0.0.0', port=5000)
