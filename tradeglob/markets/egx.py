"""
Egyptian Exchange (EGX) sector definitions and stock groupings.

Stocks are organized by the official EGX sector classification used on the
Egyptian Exchange (www.egx.com.eg).  The tickers match TradingView's EGX
exchange codes so they can be passed directly to TradeGlobFetcher.

Usage::

    from tradeglob.markets.egx import EGX_SECTORS, list_egx_sectors, get_egx_sector_stocks

    # List all sectors
    for sector in list_egx_sectors():
        print(sector)

    # Get stocks in a specific sector
    banking_stocks = get_egx_sector_stocks("Banking")
"""

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Sector → stock-symbol mapping (TradingView / EGX tickers)
# ---------------------------------------------------------------------------
EGX_SECTORS: Dict[str, List[str]] = {
    "Banking": [
        "COMI",   # Commercial International Bank
        "NSGB",   # National Société Générale Bank Egypt (now QNB)
        "EGAL",   # Egyptian Gulf Bank
        "ADIB",   # Abu Dhabi Islamic Bank – Egypt
        "CIBD",   # Cairo Investment & Real Estate Development Bank
        "MFIN",   # Misr Finance (Mashreq Bank)
        "ABIN",   # Arab Banking Corporation Egypt
        "FIBE",   # First Investment Bank Egypt
        "SAUD",   # Arab African International Bank (AAIB)
        "AIEX",   # Arab International Bank
        "HSBC",   # HSBC Egypt
        "ELWA",   # Export Development Bank of Egypt
    ],
    "Real Estate & Housing": [
        "TMGH",   # Talaat Mostafa Group
        "MNHD",   # Madinet Nasr Housing & Development
        "PHDC",   # Palm Hills Development
        "EMFD",   # Egyptian Resorts (Sahl Hasheesh)
        "SODIC",  # Sixth of October Development & Investment
        "ORHD",   # Orascom Development Egypt
        "ARCO",   # Arab Co for Land Reclamation
        "HGAR",   # Hassan Allam Properties
        "LCAP",   # Lifestyle Holding (formerly Memaar Al Morshedy)
        "MFSD",   # Misr for Real-Estate Assets
        "IWAN",   # Iwan Developments
        "CILD",   # Cityscape Real Estate
    ],
    "Telecommunications": [
        "ETEL",   # Telecom Egypt (We)
        "RAYA",   # Raya Holding for Financial Investments
        "AMER",   # Americana Restaurants International
    ],
    "Food & Beverages": [
        "DOMTY",  # Cairo Three A
        "ISPH",   # International Holding for Agricultural Investment
        "SWDY",   # Suwedy Electric
        "ORIE",   # Oriental Weavers
        "JUHD",   # Juhayna Food Industries
        "BADR",   # Badr El Din for Petroleum Products
        "POUL",   # Cairo Poultry Group
        "SUGAR",  # Nile Sugar
        "SALY",   # Saleh Khairy for Investments & Real Estate
        "EFCO",   # Egyptian Stationery Mfg.
    ],
    "Construction & Building Materials": [
        "HELI",   # Heliopolis Housing
        "ORWE",   # Orascom Construction
        "SKPC",   # Sidi Kerir Petrochemicals
        "USOB",   # Upper Egypt Contracting
        "MTIE",   # Memphis Tours for Tourism & Hotels
        "ACGC",   # Arabian Cement Company
        "CCAP",   # Citadel Capital (now Qalaa Holdings)
        "QLAA",   # Qalaa Holdings
        "BILT",   # Beltone Financial Holding
        "ALXF",   # Alexandria Flour Mills
        "ACFD",   # Egyptian Expanded Polystyrene
    ],
    "Healthcare & Pharmaceuticals": [
        "IBAG",   # International Pharmaceuticals – Multipharma
        "CLHO",   # Cleopatra Hospital
        "CARE",   # Pioneers Holding for Real Estate
        "ISID",   # Integrated Diagnostics Holdings (IDH)
        "IMED",   # International Medical Center
        "ANDS",   # Andalusia Group for Medical Services
        "EGAS",   # Egyptian Company for Prefabricated Buildings
    ],
    "Petroleum & Energy": [
        "AMOC",   # Alexandria Mineral Oils Company
        "SKPC",   # Sidi Kerir Petrochemicals
        "POUL",   # Cairo Poultry Group (also Food sector above)
        "ENAP",   # Egyptian Natural Gas
        "EFIC",   # Egyptian Financial & Industrial Company
    ],
    "Financial Services & Investment": [
        "EFG",    # EFG Hermes Holding
        "HRHO",   # Hermes Holding (EFG parent)
        "CICH",   # Cairo Investment & Real Estate Development Bank Holding
        "ECAP",   # Egyptian Chemicals Company
        "BLTF",   # Beltone Financial
        "MCQE",   # Misr Capital
        "ICON",   # Egypt Capital Holdings
        "SFCO",   # Solidere Financial Center
    ],
    "Insurance": [
        "ELHA",   # Al Ahli Insurance
        "INCE",   # Insurance House Egypt (formerly AXA)
        "NLSA",   # Nile Life Insurance
        "MISR",   # Misr Insurance Holding
    ],
    "Tourism & Hotels": [
        "ECOK",   # Egyptian Company for Touristic Constructions
        "MOHA",   # Mövenpick Hotel & Casino El Sokhna
        "ORAS",   # Orascom Investment Holding
        "SLLM",   # Salamlek Palace Hotel
        "CLHO",   # Cleopatra Hotel (also Healthcare above)
    ],
    "Industrial & Manufacturing": [
        "KABO",   # Kabool
        "EGTS",   # Egyptian Transport
        "UNIT",   # Unit (Investment & Finance)
        "CERA",   # Egyptian Iron & Steel (Ezz)
        "ESRS",   # Ezz Steel (formerly Al Ezz)
        "IRON",   # Egyptian Iron & Steel
        "ASMN",   # Asment of Temara
        "ALCO",   # Aluminium Company of Egypt (ALCOA)
        "SPIN",   # Spinning & Weaving (ESCO)
        "ABUK",   # Abu Kir Fertilizers
        "MOPCO",  # Egyptian Fertilizers Company
    ],
    "Media & Entertainment": [
        "MCQE",   # Misr Capital (also Financial Services)
        "ETMM",   # E-Finance for Digital & Financial Investments
    ],
    "Transportation & Logistics": [
        "ALCN",   # Alexandria Container & Cargo Handling
        "EGTS",   # Egyptian Transport & Commercial Services
        "AZER",   # Azertransgas (transit)
        "MPPC",   # Misr Phosphate
    ],
    "Chemicals & Petrochemicals": [
        "SKPC",   # Sidi Kerir Petrochemicals
        "ASMN",   # Asment of Temara
        "MOPCO",  # Egyptian Fertilizers
        "ABUK",   # Abu Kir Fertilizers
        "NCGC",   # National Chemical Industries
    ],
    "Textile & Garments": [
        "SIDY",   # Sidi Salem Cotton Fabric
        "NITA",   # Nile Cotton Ginning
        "ORIE",   # Oriental Weavers (also Food sector)
        "SPIN",   # Spinning & Weaving
        "GCEN",   # Ghazl El Mahalla
    ],
    "Technology": [
        "RAYA",   # Raya Holding for Financial Investments
        "ETMM",   # E-Finance for Digital & Financial Investments
        "EFIH",   # Egyptian For Information Dissemination
        "MCIT",   # Ministry of Communications & IT companies
    ],
}


def list_egx_sectors() -> List[str]:
    """
    Return the list of all available EGX sectors.

    Returns:
        List of sector name strings, sorted alphabetically.

    Example::

        >>> from tradeglob.markets.egx import list_egx_sectors
        >>> sectors = list_egx_sectors()
        >>> print(sectors)
        ['Banking', 'Chemicals & Petrochemicals', ...]
    """
    return sorted(EGX_SECTORS.keys())


def get_egx_sector_stocks(sector: str) -> List[str]:
    """
    Return the list of stock tickers for a given EGX sector.

    Lookup is case-insensitive and tolerant of minor spacing differences.

    Args:
        sector: Sector name (e.g. ``"Banking"``, ``"Real Estate & Housing"``).
                Call :func:`list_egx_sectors` for the full list of valid names.

    Returns:
        List of TradingView/EGX ticker symbols for stocks in that sector.

    Raises:
        KeyError: If *sector* is not found.  The error message includes the
                  closest matches to help users correct typos.

    Example::

        >>> from tradeglob.markets.egx import get_egx_sector_stocks
        >>> stocks = get_egx_sector_stocks("Banking")
        >>> print(stocks)
        ['COMI', 'NSGB', 'EGAL', ...]
    """
    # Exact match first
    if sector in EGX_SECTORS:
        return list(EGX_SECTORS[sector])

    # Case-insensitive fallback
    sector_lower = sector.strip().lower()
    for key in EGX_SECTORS:
        if key.lower() == sector_lower:
            return list(EGX_SECTORS[key])

    # Partial / substring match as a convenience
    matches = [key for key in EGX_SECTORS if sector_lower in key.lower()]
    if len(matches) == 1:
        return list(EGX_SECTORS[matches[0]])

    available = ", ".join(f'"{s}"' for s in list_egx_sectors())
    hint = f"  Did you mean one of: {', '.join(matches)}?" if matches else ""
    raise KeyError(
        f"Sector '{sector}' not found.{hint}\n"
        f"Available sectors: {available}"
    )
