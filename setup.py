from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tradeglob",
    version="1.0.0",
    author="Ibrahim Badawy",
    author_email="ibrahim.m.badawy@gmail.com",
    description="Universal Market Data Fetcher - Access 3.5+ million instruments from global exchanges",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ibrasonic/tradeglob",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="trading, stocks, forex, crypto, market data, tradingview, technical analysis, finance, EGX, NASDAQ",
    project_urls={
        "Bug Reports": "https://github.com/ibrasonic/tradeglob/issues",
        "Source": "https://github.com/ibrasonic/tradeglob",
        "Documentation": "https://github.com/ibrasonic/tradeglob/blob/main/README.md",
    },
)
