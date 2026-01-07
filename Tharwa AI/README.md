# Tharwa AI - Intelligent Portfolio Analyzer

An accessible desktop application for Egyptian stock market portfolio analysis, designed with screen reader compatibility.

## Features

✨ **Smart Portfolio Analysis**
- Analyze EGX30, EGX70, or custom stock selections
- Multiple time ranges (1, 2, 3, 5 years)
- Risk-adjusted recommendations (Conservative, Moderate, Aggressive)

📊 **Comprehensive Metrics**
- Entry points, stop loss, and take profit levels
- Multiple target prices
- Technical indicators (RSI, MACD, Moving Averages)
- Performance metrics and volatility analysis

🤖 **AI-Powered Chat**
- Discuss your portfolio with AI assistant
- Get personalized investment advice
- Context-aware responses based on your analysis

📁 **Excel Export**
- Multi-sheet workbooks
- Summary and detailed data
- Ready for further analysis

♿ **Accessibility**
- Full screen reader support
- Keyboard navigation
- Clear progress updates

## Installation

### Prerequisites

1. **Python 3.8+**
2. **TradeGlob library**
   ```bash
   pip install git+https://github.com/ibrasonic/TradeGlob.git
   ```

3. **Dependencies**
   ```bash
   pip install wxPython groq openpyxl
   ```

### Environment Setup

Set your Groq API key as an environment variable:

**Windows:**
```bash
setx GROQ_API_KEY "your_api_key_here"
```

**macOS/Linux:**
```bash
export GROQ_API_KEY="your_api_key_here"
```

Get your free API key from: https://console.groq.com/

## Usage

### Running the Application

```bash
cd "Tharwa AI"
python tharwa_ai_app.py
```

### Step-by-Step Guide

1. **Select Risk Tolerance**
   - Conservative: Lower risk, smaller returns
   - Moderate: Balanced approach
   - Aggressive: Higher risk, higher potential returns

2. **Choose Time Range**
   - Last 1 Year: Recent market trends
   - Last 2 Years: Medium-term analysis
   - Last 3 Years: Balanced historical view
   - Last 5 Years: Long-term perspective

3. **Select Stocks**
   - **EGX30**: Top 30 Egyptian stocks
   - **EGX70**: Next 70 liquid stocks
   - **Custom**: Enter symbols separated by commas (e.g., COMI,EGAL,ABUK)

4. **Analyze**
   - Click "Analyze Portfolio"
   - Monitor progress in the progress text box
   - View results in HTML report

5. **Review Results**
   - Stocks ranked by score (0-100)
   - Buy/Sell signals
   - Entry points and targets
   - Technical analysis details

6. **Chat with AI**
   - Switch to "AI Chat" tab
   - Ask questions about your portfolio
   - Get personalized advice

7. **Export to Excel**
   - Click "Export to Excel"
   - Choose save location
   - Open in Excel for further analysis

## Understanding the Analysis

### Score System (0-100)
- **70-100**: Strong Buy - High conviction
- **60-69**: Buy - Good opportunity
- **40-59**: Hold - Monitor position
- **30-39**: Sell - Consider exit
- **0-29**: Strong Sell - Avoid or exit

### Trading Levels

- **Entry Point**: Recommended buying price
- **Stop Loss**: Exit if price falls to this level
- **Target 1**: First profit-taking level (50% of target)
- **Target 2**: Second profit-taking level (75% of target)
- **Take Profit**: Final profit target

### Technical Indicators

- **RSI (Relative Strength Index)**
  - < 30: Oversold (potential buy)
  - 30-70: Neutral
  - > 70: Overbought (potential sell)

- **MACD Trend**
  - Bullish: Upward momentum
  - Bearish: Downward momentum

- **MA Trend**
  - Uptrend: SMA 20 > SMA 50
  - Downtrend: SMA 20 < SMA 50

## Accessibility Features

- **Screen Reader Compatible**: All controls properly labeled
- **Keyboard Navigation**: Full keyboard support
- **Progress Updates**: Text-based progress in read-only text box
- **Structured HTML**: Proper heading hierarchy for navigation
- **High Contrast**: Clear visual design

### Keyboard Shortcuts

- **Tab**: Navigate between controls
- **Space**: Activate buttons
- **Arrow Keys**: Navigate choices and lists
- **Enter**: Submit in text fields

## Tips for Best Results

1. **Start with 3-5 years** of data for reliable analysis
2. **Match risk tolerance** to your actual investment profile
3. **Diversify**: Don't put all money in top-ranked stocks
4. **Use stop losses**: Protect your capital
5. **Take profits gradually**: Use Target 1, Target 2, and Take Profit levels
6. **Monitor regularly**: Markets change - reanalyze periodically

## Troubleshooting

### "No data available"
- Check internet connection
- Verify stock symbols are correct
- Some stocks may have limited historical data

### AI Chat not working
- Verify GROQ_API_KEY is set correctly
- Check API key is valid
- Ensure internet connection

### Export fails
- Check you have write permissions
- Close Excel file if already open
- Ensure enough disk space

## Disclaimer

**Important**: This application is for educational and informational purposes only. 

- **Not Financial Advice**: Do not rely solely on this tool for investment decisions
- **Do Your Research**: Always conduct thorough research before investing
- **Market Risks**: Stock markets are volatile and carry inherent risks
- **Past Performance**: Historical data doesn't guarantee future results
- **Consult Professionals**: Consider consulting a licensed financial advisor

## Support

For issues or questions:
- Check the documentation
- Review example workflows
- Open an issue on GitHub

## License

MIT License - See main TradeGlob repository for details

---

**Tharwa AI** - Empowering informed investment decisions 📈
