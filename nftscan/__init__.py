"""Top-level package for NFTScan API Python wrapper."""

__author__ = """Alex Ausch"""
__email__ = "hello@ausch.name"
__version__ = '0.1.1'
__all__ = [#"Events", "Asset", "Assets", "Contract", "Collection",
           #"CollectionStats", "Collections", "Bundles", 
           "utils",
           "NftScanAPI"]

# from nftscan.nftscan import Events, Asset, Assets, Contract, Collection, \
#     CollectionStats, Collections, Bundles
# from nftscan.nftscan_api import NftScanAPI
# from nftscan import utils

from .nftscan_api import NftScanAPI
from . import utils