**_Note - this library is now DEFUNCT ~~hosted at https://github.com/nftscan2022/nftscan-api-python-sdk~~ (official NftScan github is now up at https://github.com/nftscan-official)_**


-
# 🚨🚨🚨 DEPRECATED/NOT MAINTAINED 🚨🚨🚨
-

# NFTScan NFT API Python 3 wrapper

A library providing Python 3 bindings for the [NFTScan API](https://developer.nftscan.com/)

This library is in Alpha / Early Alpha state, and is untested / provided as is. Feel free to open PRs or bug reports for issues, features or extensions

# Installation:

```
pip install nftscan-api
```

# Usage:

Get a key and secret. Then, check out the api endpoints listed, eg (getGroupByNftContract)[https://developer.nftscan.com/doc/#operation/getAllNftByUserAddressUsingPOST] - and try to use them

```
from nftscan import NftScanAPI
nftScan = NftScanAPI(
    apiKey=<key>,
    apiSecret=<secret>)
test_wallet = "0x3becf83939f34311b6bee143197872d877501b11"

print(nftScan.getGroupByNftContract(erc="erc721", user_address=test_wallet))
```

Write json encoded response to a file:

```
nftScan.getGroupByNftContract(erc="erc721", user_address=test_wallet, export_file_name='out.txt'))

```
