"""
Tharwa AI - Intelligent Portfolio Analyzer
A screen reader accessible stock portfolio analysis application
"""

import wx
import wx.html2
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Dict, List, Tuple
import threading
import os
from groq import Groq
from tradeglob import TradeGlobFetcher
import json


# Stock tickers data
STOCK_TICKERS = {
    "EGX30": [
        "ABUK", "ADIB", "AMOC", "ARCC", "BTFH", "COMI", "CIEB", "EAST", "HRHO",
        "EFIH", "EGAL", "EMFD", "FWRY", "GBCO", "ISPH", "JUFO", "MASR", "MCQE",
        "MFPC", "ORAS", "ORHD", "ORWE", "PHDC", "CCAP", "RAYA", "SKPC", "TMGH",
        "ETEL", "RMDA", "VLMR", "VLMRA"
    ],
    "EGX70": [
        "ACTF", "KRDI", "ATLC", "ALCN", "AMER", "ACGC", "ARAB", "AMIA", "RREI",
        "AIDC", "AIHC", "ASCM", "ASPI", "BINV", "CIRA", "COSG", "POUL", "CSAG",
        "PRCL", "CLHO", "CNFN", "SUGR", "DSCW", "EFID", "EGCH", "EGTS", "PHAR",
        "MPRC", "ETRS", "EHDR", "ECAP", "ELKA", "KABO", "OBRI", "ELSH", "ELEC",
        "UEGC", "SWDY", "ENGC", "EXPA", "GGCC", "HELI", "HDBK", "IEEC", "IFAP",
        "ICFC", "ISMQ", "ISMA", "LCSW", "MCRO", "MPCO", "MOIL", "MEPA", "MPCI",
        "MENA", "ATQA", "MTIE", "EGAS", "OFH", "OLFI", "ODIN", "PRDC", "SCEM",
        "OCDI", "SVCE", "TAQA", "CERA", "ADPC", "UBEE", "UNIT", "ZMID"
    ]
}


class PortfolioAnalyzer:
    """Core portfolio analysis engine"""
    
    def __init__(self):
        self.fetcher = TradeGlobFetcher()
        
    def fetch_data(self, symbols: List[str], years: int, progress_callback=None) -> pd.DataFrame:
        """Fetch historical data for symbols"""
        end_date = date.today()
        start_date = end_date - timedelta(days=years*365)
        
        total = len(symbols)
        all_data = {}
        
        for i, symbol in enumerate(symbols):
            if progress_callback:
                progress_callback(i, total, f"Fetching {symbol}...")
            
            try:
                df = self.fetcher.get_ohlcv(symbol, 'EGX', 'Daily', n_bars=years*252)
                if df is not None and len(df) > 0:
                    all_data[symbol] = df
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                
        return all_data
    
    def calculate_technical_indicators(self, data_dict: Dict, progress_callback=None) -> Dict:
        """Calculate technical indicators for all stocks"""
        results = {}
        total = len(data_dict)
        
        for i, (symbol, df) in enumerate(data_dict.items()):
            if progress_callback:
                progress_callback(i, total, f"Analyzing {symbol}...")
            
            try:
                # Calculate TA indicators using DataFrame .ta accessor
                df_copy = df.copy()
                
                # Calculate common indicators individually
                df_copy.ta.rsi(length=14, append=True)
                df_copy.ta.macd(fast=12, slow=26, signal=9, append=True)
                df_copy.ta.sma(length=20, append=True)
                df_copy.ta.sma(length=50, append=True)
                df_copy.ta.sma(length=200, append=True)
                df_copy.ta.ema(length=12, append=True)
                df_copy.ta.ema(length=26, append=True)
                df_copy.ta.ema(length=50, append=True)
                df_copy.ta.bbands(length=20, std=2, append=True)
                df_copy.ta.atr(length=14, append=True)
                df_copy.ta.adx(length=14, append=True)
                df_copy.ta.cci(length=14, append=True)
                df_copy.ta.willr(length=14, append=True)
                df_copy.ta.stoch(k=14, d=3, append=True)
                df_copy.ta.obv(append=True)
                
                results[symbol] = df_copy
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                results[symbol] = df
                
        return results
    
    def analyze_stock(self, symbol: str, df: pd.DataFrame, risk_tolerance: str) -> Dict:
        """Analyze individual stock and generate signals"""
        if len(df) < 20:
            return None
            
        latest = df.iloc[-1]
        
        # Calculate metrics
        current_price = latest['close']
        
        # RSI signal
        rsi = latest.get('RSI_14', 50)
        rsi_signal = 'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'
        
        # MACD signal
        macd = latest.get('MACD_12_26_9', 0)
        macd_signal = latest.get('MACDs_12_26_9', 0)
        macd_trend = 'Bullish' if macd > macd_signal else 'Bearish'
        
        # Moving averages
        sma_20 = latest.get('SMA_20', current_price)
        sma_50 = latest.get('SMA_50', current_price)
        ma_trend = 'Uptrend' if sma_20 > sma_50 else 'Downtrend'
        
        # Volatility (ATR)
        atr = latest.get('ATRr_14', current_price * 0.02)
        
        # Calculate entry, stop loss, take profit based on risk tolerance
        if risk_tolerance == 'Conservative':
            stop_loss_pct = 0.03  # 3%
            take_profit_pct = 0.06  # 6%
        elif risk_tolerance == 'Moderate':
            stop_loss_pct = 0.05  # 5%
            take_profit_pct = 0.10  # 10%
        else:  # Aggressive
            stop_loss_pct = 0.08  # 8%
            take_profit_pct = 0.15  # 15%
        
        stop_loss = current_price * (1 - stop_loss_pct)
        take_profit = current_price * (1 + take_profit_pct)
        target_1 = current_price * (1 + take_profit_pct * 0.5)
        target_2 = current_price * (1 + take_profit_pct * 0.75)
        
        # Calculate score (0-100)
        score = 50  # Base score
        
        # RSI contribution
        if 30 < rsi < 70:
            score += 10
        elif rsi < 30:
            score += 20  # Oversold is good for buying
        else:
            score -= 10  # Overbought
        
        # MACD contribution
        if macd_trend == 'Bullish':
            score += 15
        else:
            score -= 10
            
        # MA trend contribution
        if ma_trend == 'Uptrend':
            score += 15
        else:
            score -= 10
        
        # Price vs MA contribution
        if current_price > sma_20:
            score += 10
            
        # Ensure score is 0-100
        score = max(0, min(100, score))
        
        # Determine signal
        if score >= 70:
            signal = 'Strong Buy'
        elif score >= 60:
            signal = 'Buy'
        elif score >= 40:
            signal = 'Hold'
        elif score >= 30:
            signal = 'Sell'
        else:
            signal = 'Strong Sell'
        
        # Calculate metrics
        volatility = (df['close'].std() / df['close'].mean()) * 100
        returns_1m = ((current_price / df.iloc[-21]['close']) - 1) * 100 if len(df) > 21 else 0
        returns_3m = ((current_price / df.iloc[-63]['close']) - 1) * 100 if len(df) > 63 else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd_trend': macd_trend,
            'ma_trend': ma_trend,
            'entry_point': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'target_1': target_1,
            'target_2': target_2,
            'score': score,
            'signal': signal,
            'volatility': volatility,
            'returns_1m': returns_1m,
            'returns_3m': returns_3m,
            'volume': latest['volume'],
            'sma_20': sma_20,
            'sma_50': sma_50
        }
    
    def build_portfolio(self, symbols: List[str], years: int, risk_tolerance: str, 
                       progress_callback=None) -> Tuple[List[Dict], Dict]:
        """Build and analyze portfolio"""
        # Fetch data
        if progress_callback:
            progress_callback(0, 100, "Starting data fetch...")
        
        data_dict = self.fetch_data(symbols, years, progress_callback)
        
        if progress_callback:
            progress_callback(50, 100, "Calculating indicators...")
        
        # Calculate indicators
        results_dict = self.calculate_technical_indicators(data_dict, progress_callback)
        
        if progress_callback:
            progress_callback(80, 100, "Analyzing stocks...")
        
        # Analyze each stock
        recommendations = []
        for symbol, df in results_dict.items():
            analysis = self.analyze_stock(symbol, df, risk_tolerance)
            if analysis:
                recommendations.append(analysis)
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        if progress_callback:
            progress_callback(100, 100, "Analysis complete!")
        
        return recommendations, results_dict


class TharwaAIFrame(wx.Frame):
    """Main application frame"""
    
    def __init__(self):
        super().__init__(None, title="Tharwa AI - Portfolio Analyzer", size=(1200, 800))
        
        self.analyzer = PortfolioAnalyzer()
        self.analysis_results = None
        self.full_data = None
        
        # Initialize Groq client
        try:
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except:
            self.groq_client = None
        
        self.init_ui()
        self.Centre()
        
    def init_ui(self):
        """Initialize user interface"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="Tharwa AI - Intelligent Portfolio Analyzer")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 10)
        
        # Input section
        input_sizer = wx.GridBagSizer(5, 5)
        
        # Risk tolerance
        row = 0
        input_sizer.Add(wx.StaticText(panel, label="Risk Tolerance:"), 
                       pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.risk_choice = wx.Choice(panel, choices=["Conservative", "Moderate", "Aggressive"])
        self.risk_choice.SetSelection(1)
        input_sizer.Add(self.risk_choice, pos=(row, 1), flag=wx.EXPAND)
        
        # Time range
        row += 1
        input_sizer.Add(wx.StaticText(panel, label="Time Range:"), 
                       pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.time_choice = wx.Choice(panel, choices=["Last 1 Year", "Last 2 Years", 
                                                      "Last 3 Years", "Last 5 Years"])
        self.time_choice.SetSelection(2)  # Default 3 years
        input_sizer.Add(self.time_choice, pos=(row, 1), flag=wx.EXPAND)
        
        # Stock selection
        row += 1
        input_sizer.Add(wx.StaticText(panel, label="Stock Selection:"), 
                       pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.stock_choice = wx.Choice(panel, choices=["EGX30", "EGX70", "Custom"])
        self.stock_choice.SetSelection(0)
        self.stock_choice.Bind(wx.EVT_CHOICE, self.on_stock_choice)
        input_sizer.Add(self.stock_choice, pos=(row, 1), flag=wx.EXPAND)
        
        # Custom symbols
        row += 1
        input_sizer.Add(wx.StaticText(panel, label="Custom Symbols:"), 
                       pos=(row, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.custom_symbols = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.custom_symbols.SetHint("e.g., COMI,EGAL,ABUK (comma separated)")
        self.custom_symbols.Enable(False)
        input_sizer.Add(self.custom_symbols, pos=(row, 1), flag=wx.EXPAND)
        
        input_sizer.AddGrowableCol(1)
        main_sizer.Add(input_sizer, 0, wx.ALL | wx.EXPAND, 10)
        
        # Authentication section
        auth_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.auth_status = wx.StaticText(panel, label="Authentication: Not checked")
        auth_sizer.Add(self.auth_status, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.check_auth_btn = wx.Button(panel, label="Check Authentication")
        self.check_auth_btn.Bind(wx.EVT_BUTTON, self.on_check_auth)
        auth_sizer.Add(self.check_auth_btn, 0, wx.RIGHT, 5)
        
        self.authenticate_btn = wx.Button(panel, label="Authenticate")
        self.authenticate_btn.Bind(wx.EVT_BUTTON, self.on_authenticate)
        auth_sizer.Add(self.authenticate_btn, 0)
        
        main_sizer.Add(auth_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        # Analyze button
        self.analyze_btn = wx.Button(panel, label="Analyze Portfolio")
        self.analyze_btn.Bind(wx.EVT_BUTTON, self.on_analyze)
        main_sizer.Add(self.analyze_btn, 0, wx.ALL | wx.CENTER, 10)
        
        # Progress section
        progress_box = wx.StaticBoxSizer(wx.VERTICAL, panel, "Progress")
        
        # Progress gauge
        self.progress_gauge = wx.Gauge(panel, range=100)
        progress_box.Add(self.progress_gauge, 0, wx.EXPAND | wx.ALL, 5)
        
        # Progress text
        self.progress_text = wx.TextCtrl(panel, value="Ready", 
                                        style=wx.TE_READONLY | wx.TE_CENTRE)
        progress_box.Add(self.progress_text, 0, wx.EXPAND | wx.ALL, 5)
        
        main_sizer.Add(progress_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # Results notebook
        self.notebook = wx.Notebook(panel)
        
        # HTML Results tab
        self.html_panel = wx.Panel(self.notebook)
        html_sizer = wx.BoxSizer(wx.VERTICAL)
        self.html_view = wx.html2.WebView.New(self.html_panel)
        html_sizer.Add(self.html_view, 1, wx.EXPAND)
        self.html_panel.SetSizer(html_sizer)
        self.notebook.AddPage(self.html_panel, "Analysis Results")
        
        # AI Chat tab
        self.chat_panel = wx.Panel(self.notebook)
        chat_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.chat_history = wx.TextCtrl(self.chat_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        chat_sizer.Add(self.chat_history, 1, wx.EXPAND | wx.ALL, 5)
        
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chat_input = wx.TextCtrl(self.chat_panel, style=wx.TE_PROCESS_ENTER)
        self.chat_input.SetHint("Ask about your portfolio...")
        self.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_send_chat)
        input_sizer.Add(self.chat_input, 1, wx.EXPAND | wx.RIGHT, 5)
        
        self.send_btn = wx.Button(self.chat_panel, label="Send")
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send_chat)
        input_sizer.Add(self.send_btn, 0)
        
        chat_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.chat_panel.SetSizer(chat_sizer)
        self.notebook.AddPage(self.chat_panel, "AI Chat")
        
        main_sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 10)
        
        # Export button
        self.export_btn = wx.Button(panel, label="Export to Excel")
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        self.export_btn.Enable(False)
        main_sizer.Add(self.export_btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(main_sizer)
        
    def on_stock_choice(self, event):
        """Handle stock selection change"""
        is_custom = self.stock_choice.GetStringSelection() == "Custom"
        self.custom_symbols.Enable(is_custom)
        
    def get_selected_symbols(self) -> List[str]:
        """Get list of symbols to analyze"""
        choice = self.stock_choice.GetStringSelection()
        
        if choice == "Custom":
            symbols_str = self.custom_symbols.GetValue().strip()
            if not symbols_str:
                return []
            return [s.strip().upper() for s in symbols_str.split(',')]
        else:
            return STOCK_TICKERS[choice]
    
    def on_check_auth(self, event):
        """Check authentication status"""
        self.check_auth_btn.Enable(False)
        self.progress_text.SetValue("Checking authentication...")
        
        def check_thread():
            try:
                # Try to fetch a small amount of data to test auth
                test_df = self.analyzer.fetcher.get_ohlcv('COMI', 'EGX', 'Daily', n_bars=5)
                
                if test_df is not None and len(test_df) > 0:
                    wx.CallAfter(self.auth_status.SetLabel, "Authentication: ✓ Connected")
                    wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(0, 128, 0))
                    wx.CallAfter(self.progress_text.SetValue, "Authentication verified!")
                else:
                    wx.CallAfter(self.auth_status.SetLabel, "Authentication: Limited access")
                    wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(255, 140, 0))
                    wx.CallAfter(self.progress_text.SetValue, "Working in anonymous mode")
            except Exception as e:
                wx.CallAfter(self.auth_status.SetLabel, "Authentication: ✗ Error")
                wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(255, 0, 0))
                wx.CallAfter(self.progress_text.SetValue, f"Check failed: {str(e)}")
            finally:
                wx.CallAfter(self.check_auth_btn.Enable, True)
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def on_authenticate(self, event):
        """Authenticate with TradingView"""
        self.authenticate_btn.Enable(False)
        self.progress_text.SetValue("Opening browser for authentication...")
        
        def auth_thread():
            try:
                success = self.analyzer.fetcher.authenticate()
                
                if success:
                    wx.CallAfter(self.auth_status.SetLabel, "Authentication: ✓ Authenticated")
                    wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(0, 128, 0))
                    wx.CallAfter(self.progress_text.SetValue, "Authentication successful!")
                    wx.CallAfter(wx.MessageBox, 
                               "Successfully authenticated with TradingView!\nYou now have access to more data.",
                               "Success", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.CallAfter(self.auth_status.SetLabel, "Authentication: ✗ Failed")
                    wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(255, 0, 0))
                    wx.CallAfter(self.progress_text.SetValue, "Authentication failed")
                    wx.CallAfter(wx.MessageBox,
                               "Authentication failed. Please try again or continue in anonymous mode.",
                               "Authentication Failed", wx.OK | wx.ICON_WARNING)
            except Exception as e:
                wx.CallAfter(self.auth_status.SetLabel, "Authentication: ✗ Error")
                wx.CallAfter(self.auth_status.SetForegroundColour, wx.Colour(255, 0, 0))
                wx.CallAfter(self.progress_text.SetValue, f"Auth error: {str(e)}")
                wx.CallAfter(wx.MessageBox, f"Authentication error: {str(e)}", 
                           "Error", wx.OK | wx.ICON_ERROR)
            finally:
                wx.CallAfter(self.authenticate_btn.Enable, True)
        
        threading.Thread(target=autgauge.SetValue, percentage)
        wx.CallAfter(self.progress_h_thread, daemon=True).start()
    
    def update_progress(self, current, total, message):
        """Update progress display"""
        percentage = int((current / total) * 100) if total > 0 else 0
        wx.CallAfter(self.progress_text.SetValue, f"{message} ({percentage}%)")
        
    def on_analyze(self, event):
        """Handle analyze button click"""
        symbols = self.get_selected_symbols()
        
        if not symbols:
            wx.MessageBox("Please select stocks to analyze", "Error", 
                         wx.OK | wx.ICON_ERROR)
            return
        
        # Get parameters
        risk = self.risk_choice.GetStringSelection()
        time_str = self.time_choice.GetStringSelection()
        years = int(time_str.split()[1])
        
        # Disable controls
        self.analyze_btn.Enable(False)
        
        # Run analysis in thread
        def analyze_thread():
            try:
                results, full_data = self.analyzer.build_portfolio(
                    symbols, years, risk, self.update_progress
                )
                wx.CallAfter(self.display_results, results, full_data, risk)
            except Exception as e:
                wx.CallAfter(wx.MessageBox, f"Analysis error: {str(e)}", 
                           "Error", wx.OK | wx.ICON_ERROR)
            finally:
                wx.CallAfter(self.analyze_btn.Enable, True)
        
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    def display_results(self, results, full_data, risk_tolerance):
        """Display analysis results in HTML view"""
        self.analysis_results = results
        self.full_data = full_data
        self.export_btn.Enable(True)
        
        # Generate HTML
        html = self.generate_html_report(results, risk_tolerance)
        self.html_<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stock-card {{
            background: white;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .strong-buy {{ border-left-color: #27ae60; }}
        .buy {{ border-left-color: #2ecc71; }}
        .hold {{ border-left-color: #f39c12; }}
        .sell {{ border-left-color: #e74c3c; }}
        .strong-sell {{ border-left-color: #c0392b; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #34495e;
            color: white;
        }}
        .metric {{
            display: inline-block;
            margin: 5px 10px;
            padding: 5px 10px;
            background: #ecf0f1;
            border-radius: 4px;
        }}
        .score {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
    </style>
</head>
<body>
    <h1>Portfolio Analysis Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Risk Tolerance:</strong> {risk}</p>
        <p><strong>Total Stocks Analyzed:</strong> {total}</p>
        <p><strong>Analysis Date:</strong> {date_str}</p>
    </div>
""".format(
            risk=risk_tolerance,
            total=len(results),
            date_str<p><strong>Total Stocks Analyzed:</strong> {total}</p>
                <p><strong>Analysis Date:</strong> {date}</p>
            </div>
        """.format(
            risk=risk_tolerance,
            total=len(results),
<div class="summary">
    <h2>Top Recommendations</h2>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Symbol</th>
                <th>Score</th>
                <th>Signal</th>
                <th>Current Price</th>
                <th>Target</th>
            </tr>
        </thead>
        <tbody>
                    <th>Current Price</th>
                            <th>Target</th>
                        </tr>
                    </thead>
            <tr>
                <td>{i}</td>
                <td><strong>{stock['symbol']}</strong></td>
                <td>{stock['score']:.0f}</td>
                <td>{stock['signal']}</td>
                <td>EGP {stock['current_price']:.2f}</td>
                <td>EGP {stock['take_profit']:.2f}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</div>

        html += """
                    </tbody>
                </table>\n"
        
        for stock in results:
            signal_class = stock['signal'].lower().replace(' ', '-')
            stop_pct = ((stock['stop_loss']/stock['current_price']-1)*100)
            t1_pct = ((stock['target_1']/stock['current_price']-1)*100)
            t2_pct = ((stock['target_2']/stock['current_price']-1)*100)
            tp_pct = ((stock['take_profit']/stock['current_price']-1)*100)
            
            html += f"""
<div class="stock-card {signal_class}">
    <h3>{stock['symbol']} - {stock['signal']}</h3>
    <p class="score">Score: {stock['score']:.0f}/100</p>
    
    <h4>Current Market Data</h4>
    <div class="metric">Price: EGP {stock['current_price']:.2f}</div>
    <div class="metric">RSI: {stock['rsi']:.1f} ({stock['rsi_signal']})</div>
    <div class="metric">MACD: {stock['macd_trend']}</div>
    <div class="metric">MA Trend: {stock['ma_trend']}</div>
    
    <h4>Trading Levels</h4>
    <table>
        <tr>
            <th>Entry Point</th>
            <td>EGP {stock['entry_point']:.2f}</td>
        </tr>
        <tr>
            <th>Stop Loss</th>
            <td>EGP {stock['stop_loss']:.2f} ({stop_pct:.1f}%)</td>
        </tr>
        <tr>
            <th>Target 1</th>
            <td>EGP {stock['target_1']:.2f} ({t1_pct:.1f}%)</td>
        </tr>
        <tr>
            <th>Target 2</th>
            <td>EGP {stock['target_2']:.2f} ({t2_pct:.1f}%)</td>
        </tr>
        <tr>
            <th>Take Profit</th>
            <td>EGP {stock['take_profit']:.2f} ({tp_pct:.1f}%)</td>
        </tr>
    </table>
    
    <h4>Performance Metrics</h4>
    <div class="metric">1M Return: {stock['returns_1m']:.2f}%</div>
    <div class="metric">3M Return: {stock['returns_3m']:.2f}%</div>
    <div class="metric">Volatility: {stock['volatility']:.2f}%</div>
    <div class="metric">Volume: {stock['volume']:,.0f}</div>
    
    <h4>Technical Indicators</h4>
    <div class="metric">SMA 20: EGP {stock['sma_20']:.2f}</div>
    <div class="metric">SMA 50: EGP {stock['sma_50']:.2f}</div>
</div>
"""
        
        html += """
</body>
</html>
    """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def on_send_chat(self, event):
        """Handle chat message"""
        if not self.analysis_results:
            wx.MessageBox("Please run an analysis first", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        
        if not self.groq_client:
            wx.MessageBox("Groq API not configured. Please set GROQ_API_KEY environment variable.", 
                         "Error", wx.OK | wx.ICON_ERROR)
            return
        
        user_message = self.chat_input.GetValue().strip()
        if not user_message:
            return
        
        # Display user message
        self.chat_history.AppendText(f"You: {user_message}\n\n")
        self.chat_input.Clear()
        self.send_btn.Enable(False)
        
        # Generate AI response in thread
        def chat_thread():
            try:
                # Prepare context
                context = self.prepare_chat_context()
                
                # Call Groq API
                response = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are Tharwa AI, an expert financial advisor specializing in Egyptian stock market analysis. 
You have access to the following portfolio analysis data:

{context}

Provide helpful, accurate investment advice based on this data. Be concise but informative. 
Consider the user's risk tolerance and current market conditions. Always remind users that 
investing carries risks and they should do their own research."""
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                    max_completion_tokens=1024
                )
                
                ai_response = response.choices[0].message.content
                wx.CallAfter(self.chat_history.AppendText, f"Tharwa AI: {ai_response}\n\n")
                
            except Exception as e:
                wx.CallAfter(self.chat_history.AppendText, 
                           f"Error: {str(e)}\n\n")
            finally:
                wx.CallAfter(self.send_btn.Enable, True)
        
        threading.Thread(target=chat_thread, daemon=True).start()
    
    def prepare_chat_context(self) -> str:
        """Prepare portfolio context for AI"""
        if not self.analysis_results:
            return "No analysis available"
        
        context = f"Total stocks analyzed: {len(self.analysis_results)}\n\n"
        context += "Top 5 Recommendations:\n"
        
        for i, stock in enumerate(self.analysis_results[:5], 1):
            context += f"{i}. {stock['symbol']}: Score {stock['score']:.0f}, {stock['signal']}, "
            context += f"Price: EGP {stock['current_price']:.2f}, "
            context += f"Target: EGP {stock['take_profit']:.2f}, "
            context += f"Stop Loss: EGP {stock['stop_loss']:.2f}\n"
        
        return context
    
    def on_export(self, event):
        """Export results to Excel"""
        if not self.analysis_results or not self.full_data:
            return
        
        # File dialog
        with wx.FileDialog(self, "Save Excel file",
                          defaultFile=f"portfolio_analysis_{date.today()}.xlsx",
                          wildcard="Excel files (*.xlsx)|*.xlsx",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            filepath = fileDialog.GetPath()
            
            try:
                self.export_to_excel(filepath)
                wx.MessageBox(f"Successfully exported to:\n{filepath}", 
                             "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Export failed: {str(e)}", 
                             "Error", wx.OK | wx.ICON_ERROR)
    
    def export_to_excel(self, filepath: str):
        """Export analysis to Excel with multiple sheets"""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            for stock in self.analysis_results:
                summary_data.append({
                    'Symbol': stock['symbol'],
                    'Score': stock['score'],
                    'Signal': stock['signal'],
                    'Current Price': stock['current_price'],
                    'Entry Point': stock['entry_point'],
                    'Stop Loss': stock['stop_loss'],
                    'Target 1': stock['target_1'],
                    'Target 2': stock['target_2'],
                    'Take Profit': stock['take_profit'],
                    'RSI': stock['rsi'],
                    'RSI Signal': stock['rsi_signal'],
                    'MACD Trend': stock['macd_trend'],
                    'MA Trend': stock['ma_trend'],
                    'Volatility %': stock['volatility'],
                    '1M Return %': stock['returns_1m'],
                    '3M Return %': stock['returns_3m'],
                    'Volume': stock['volume']
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Raw data sheets (one per stock)
            for symbol, df in list(self.full_data.items())[:10]:  # Limit to 10 stocks
                df_export = df.copy()
                sheet_name = symbol[:31]  # Excel sheet name limit
                df_export.to_excel(writer, sheet_name=sheet_name)


def main():
    """Main entry point"""
    app = wx.App()
    frame = TharwaAIFrame()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
