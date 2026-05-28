"""Market-specific data: sector definitions, stock groupings, and exchange metadata."""

from .egx import EGX_SECTORS, get_egx_sector_stocks, list_egx_sectors

__all__ = [
    'EGX_SECTORS',
    'get_egx_sector_stocks',
    'list_egx_sectors',
]
