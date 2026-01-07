# Installation Guide

## Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, Linux
- **Browser**: Google Chrome (for authentication)

---

## Installation Methods

### Method 1: Install from GitHub (Recommended)

```bash
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

This installs the latest stable version directly from the repository.

### Method 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/ibrasonic/TradeGlob.git
cd TradeGlob

# Install in development mode
pip install -e .
```

Use this method if you want to modify the source code or contribute.

### Method 3: Install from Local Source

```bash
# Download and extract the source
# Then navigate to the directory and run:
pip install .
```

---

## Dependencies

TradeGlob automatically installs these dependencies:

### Core Dependencies
- `pandas>=1.3.0` - Data manipulation
- `selenium>=4.9.0` - Web automation for authentication
- `tqdm` - Progress bars
- `holidays` - Market calendar

### Technical Analysis Dependencies
- `numba>=0.55.0` - Fast numerical computations
- `scipy>=1.7.0` - Scientific computing

### Additional Dependencies
- `tvDatafeed` - TradingView data fetching
- `chromedriver-autoinstaller` - Automatic ChromeDriver management

---

## Verify Installation

After installation, verify it works:

```python
from tradeglob import TradeGlobFetcher

print("TradeGlob installed successfully!")

# Quick test
fetcher = TradeGlobFetcher()
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', n_bars=10)
print(f"\nFetched {len(df)} bars of AAPL data")
print(df.tail())
```

**Expected output:**
```
TradeGlob installed successfully!

Fetched 10 bars of AAPL data
            symbol   open   high    low  close     volume
Date                                                      
2024-12-13   AAPL  198.0  199.5  197.8  198.2   45234567
2024-12-14   AAPL  198.2  200.1  198.0  199.5   48341234
...
```

---

## Optional: Install in Virtual Environment

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv tradeglob_env

# Activate (Windows)
tradeglob_env\Scripts\activate

# Activate (macOS/Linux)
source tradeglob_env/bin/activate

# Install TradeGlob
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

### Using conda

```bash
# Create conda environment
conda create -n tradeglob python=3.10

# Activate
conda activate tradeglob

# Install TradeGlob
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

---

## Upgrade TradeGlob

To upgrade to the latest version:

```bash
pip install --upgrade git+https://github.com/ibrasonic/TradeGlob.git
```

---

## Troubleshooting

### "No module named 'tradeglob'"

**Cause:** TradeGlob not installed or wrong Python environment

**Solution:**
```bash
# Check if installed
pip list | grep tradeglob

# If not found, install
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

### "Python version too old"

**Cause:** Python < 3.7

**Solution:**
```bash
# Check Python version
python --version

# Upgrade Python to 3.7+
# Download from https://www.python.org/downloads/
```

### "Could not find a version that satisfies the requirement"

**Cause:** pip is outdated

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Then install TradeGlob
pip install git+https://github.com/ibrasonic/TradeGlob.git
```

### "Chrome not found" during authentication

**Cause:** Google Chrome not installed

**Solution:**
- Download and install Chrome from [google.com/chrome](https://www.google.com/chrome/)

### SSL Certificate Errors

**Solution:**
```bash
# Install with certificate verification disabled (not recommended for production)
pip install --trusted-host github.com --trusted-host pypi.org git+https://github.com/ibrasonic/TradeGlob.git
```

### Permission Denied (Windows)

**Solution:**
```bash
# Run Command Prompt as Administrator
# Or install for user only
pip install --user git+https://github.com/ibrasonic/TradeGlob.git
```

### Permission Denied (macOS/Linux)

**Solution:**
```bash
# Don't use sudo with pip
# Instead, install for user
pip install --user git+https://github.com/ibrasonic/TradeGlob.git

# Or use virtual environment (recommended)
```

---

## Jupyter Notebook Setup

### Install in Jupyter

```bash
# Install TradeGlob
pip install git+https://github.com/ibrasonic/TradeGlob.git

# Install Jupyter (if not already installed)
pip install jupyter

# Start Jupyter
jupyter notebook
```

### Use in Jupyter

```python
# In a Jupyter cell
from tradeglob import TradeGlobFetcher

fetcher = TradeGlobFetcher()
df = fetcher.get_ohlcv('AAPL', 'NASDAQ', 'Daily', 100)
df.head()
```

---

## Google Colab Setup

```python
# In the first cell of your Colab notebook
!pip install git+https://github.com/ibrasonic/TradeGlob.git

# Then import and use
from tradeglob import TradeGlobFetcher
fetcher = TradeGlobFetcher()
```

**Note:** Authentication via browser may not work in Colab. Use anonymous mode or pass credentials directly.

---

## Development Installation

For contributing or modifying the source:

```bash
# Clone the repository
git clone https://github.com/ibrasonic/TradeGlob.git
cd TradeGlob

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests (if available)
pytest
```

---

## Uninstall TradeGlob

```bash
pip uninstall tradeglob
```

---

## Next Steps

After installation:
1. Read the [Quick Start Guide](01_QUICK_START.md)
2. Try [Basic Examples](03_BASIC_EXAMPLES.md)
3. Explore [Technical Analysis](05_TECHNICAL_ANALYSIS.md)

---

## System-Specific Notes

### Windows
- Make sure Python is in PATH
- Use Command Prompt or PowerShell
- Chrome must be installed for authentication

### macOS
- Use Terminal
- May need Xcode Command Line Tools: `xcode-select --install`
- Chrome must be installed for authentication

### Linux
- Use terminal
- May need to install Chrome manually:
  ```bash
  # Ubuntu/Debian
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome-stable_current_amd64.deb
  ```

---

## Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Review [FAQ](11_FAQ.md)
3. Check [Error Handling](12_ERROR_HANDLING.md)
4. Open an issue on [GitHub](https://github.com/ibrasonic/TradeGlob/issues)
