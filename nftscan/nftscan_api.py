import json
import requests
from datetime import datetime, timedelta
from numbers import Number
from parameters_validation import validate_parameters, parameter_validation, non_blank, non_negative
# from nftscan import utils
from . import utils



# Validators
@parameter_validation
def erc_valid(erc: str):
    if erc not in ["erc721", "erc1155"]:
        raise ValueError("erc must be one of \"erc721\" or \"erc1155\"")

@parameter_validation
def more_than_zero(number: Number,  arg_name: str):
    validation_error = None
    try:
        if number <= 0:
            validation_error = ValueError(
                "Parameter `{arg}` must be 1 or higher".format(arg=arg_name))
    except Exception as e:
        validation_error = RuntimeError(
            "Unable to validate parameter `{arg}`: {error_name}{error}".format(arg=arg_names, error_name=e.__class__.__name__, error=e), e)
    if validation_error:
        raise 

class NftScanAPI:
    MAX_PAGE_SIZE = 100
    @validate_parameters
    def __init__(self, 
                apiKey: non_blank(str),
                apiSecret: non_blank(str),
                base_url="https://restapi.nftscan.com/api/",
                version="v1"):
        """Base class to interact with the NftScan API and fetch NFT data.

        Args:
        base_url (str): NftScan API base URL. Defaults to
        "https://restapi.nftscan.com/api/".
        apikey (str): NftScan API key (you need to request one)
        version (str, optional): API version. Defaults to "v1".
        """
        self.api_url = f"{base_url}/{version}"
        #key and secret are forced to stay in memory!!
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.accessToken = None
        self.headers = {"Content-Type": "application/json"}

    def _authenticate(self):
        """Base class to authenticate against the NftScan API and fetch NFT data.

        see: https://developer.nftscan.com/doc/#section/Authentication

        Note: this is a GET request, unlike the rest of the API implementation

        Args:
        """
        auth_url=f"https://restapi.nftscan.com/gw/token?apiKey={self.apiKey}&apiSecret={self.apiSecret}"
        result = self._make_request(auth_url)
        
        # Note: authentication API uses entirely different error/exception
        # pattern from the rest of the API. So we're forced to check the _content_
        # of the response for a status code as well:

        self.accessToken = result["accessToken"]
        self.expiration = datetime.now() + timedelta(seconds=result["expiration"])
        self.headers["Access-Token"]=self.accessToken


    @validate_parameters
    def _make_request(self, 
        url: non_blank(str), 
        headers=None, 
        data=None,
        export_file_name="",
        return_response=False):
        """Makes a request to an arbitrary url and returns either a response
        object or dictionary.

        Args:
            url (str): url to make a request to
            headers (dict, optional): headers to attach to the request
            params (dict, optional): Query parameters to include in the
            request. Defaults to None.
            export_file_name (str, optional): In case you want to download the
            data into a file,
            specify the filename here. Eg. 'export.json'. Be default, no file
            is created.
            return_response (bool, optional): Set it True if you want it to
            return the actual response object.
            By default, it's False, which means a dictionary will be returned.
            next_url (str, optional): If you want to paginate, provide the
            `next` value here (this is a URL) NftScan provides in the response.
            If this argument is provided, `endpoint` will be ignored.


        Returns:
            Data sent back from the API. Either a response or dict object
            depending on the `return_response` argument.
        """
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 400:
            raise ValueError(response.text)
        elif response.status_code == 401:
            raise requests.exceptions.HTTPError(response.text)
        elif response.status_code == 403:
            # TODO: auth exception?
            raise ConnectionError("The server blocked access.")
        elif response.status_code == 495:
            raise requests.exceptions.SSLError("SSL certificate error")
        elif response.status_code == 504:
            raise TimeoutError("The server reported a gateway time-out error.")

        # It appears the API implementation includes a separate JSON field called status
        # which ...... _also_ encodes a HTTP response status. So we check again...

        json_response = response.json()
        if not "code" in json_response.keys():
            raise Exception("Request failed, no HTTP status code in JSON response")
        status_code = json_response["code"]
        if not "data" in json_response.keys():
            raise Exception("Request failed, no data in JSON response")
        
        data = json_response["data"]

        if status_code == 400:
            raise ValueError(response.text)
        elif status_code == 401:
            raise requests.exceptions.HTTPError(response.text)
        elif status_code == 403:
            # TODO: auth exception?
            raise ConnectionError("The server blocked access.")
        elif status_code == 495:
            raise requests.exceptions.SSLError("SSL certificate error")
        elif status_code == 504:
            raise TimeoutError("The server reported a gateway time-out error.")

        if export_file_name != "":
            utils.export_file(utils.force_encoded_json(data), export_file_name)
        if return_response:
            return response
        return data 


    @validate_parameters
    def _api_request(self, 
        endpoint: non_blank(str), 
        data=None, 
        export_file_name="",
        return_response=False):
        """Makes an authenticated request to the NftScan API and 
        returns either a response object or dictionary.
        
        Note: are these always "POST" requests?
        Args:
            endpoint (str): API endpoint to use for the request.
            params (dict, optional): Query parameters to include in the
            request. Defaults to None.
            export_file_name (str, optional): In case you want to download the
            data into a file,
            specify the filename here. Eg. 'export.json'. Be default, no file
            is created.
            return_response (bool, optional): Set it True if you want it to
            return the actual response object.
            By default, it's False, which means a dictionary will be returned.
            next_url (str, optional): If you want to paginate, provide the
            `next` value here (this is a URL) NftScan provides in the response.
            If this argument is provided, `endpoint` will be ignored.


        Returns:
            Data sent back from the API. Either a response or dict object
            depending on the `return_response` argument.
        """
        url = f"{self.api_url}/{endpoint}"
        result = None
        try:
            result = self._make_request(
                url,
                headers=self.headers,
                data=data,
                export_file_name=export_file_name,
                return_response=return_response
            )
        except Exception as e:
            # TODO: only auth+retry if auth exception 
            self._authenticate()
            result = self._make_request(
                url,
                headers=self.headers,
                data=data,
                export_file_name=export_file_name,
                return_response=return_response
            )
        
        return result


    @validate_parameters
    def getAllNftByUserAddress(
            self,
            erc: erc_valid(str),
            user_address: str,
            page_index: non_negative(int)=0,
            page_size: int=20,
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            see # https://developer.nftscan.com/doc/#operation/getAllNftByUserAddressUsingPOST

            Args:
                erc (str): erc protocol (erc721 or erc1155)
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getAllNftByUserAddress"
            query_params = {
                "erc": erc,
                "walletType": 3,
                "page_index": page_index,
                "page_size": min(page_size, self.MAX_PAGE_SIZE), # TODO: validator?
                "user_address": user_address
            }
            return self._api_request(endpoint, query_params, export_file_name)


    @validate_parameters
    def getGroupByNftContract(
            self,
            erc: erc_valid(str),
            user_address: str,
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getGroupByNftContractUsingPOST

            Args:
                erc (str): erc protocol (erc721 or erc1155)
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getGroupByNftContract"
            data = {
                "erc": erc,
                "user_address": user_address
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getMintByUserAddress(
            self,
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            user_address: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getMintByUserAddressUsingPOST

            Args:
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getMintByUserAddress"
            data = {
                "page_index": page_index,
                "page_size": page_size,
                "user_address": user_address
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getMintByUserAddressAndNftAddress(
            self,
            nft_address: non_blank(str)="",
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            user_address: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getMintByUserAddressAndNftAddressUsingPOST

            Args:
                nft_address (str): NFT contract address
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getMintByUserAddressAndNftAddress"
            data = {
                "nft_address": nft_address,
                "page_index": page_index,
                "page_size": page_size,
                "user_address": user_address
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getNFTRecordByContract(
            self,
            nft_address: non_blank(str)="",
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getNFTRecordByContractUsingPOST

            Args:
                nft_address (str): NFT contract address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getNFTRecordByContract"
            data = {
                "nft_address": nft_address,
                "page_index": page_index,
                "page_size": page_size,
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getNftByContractAndUserAddress(
            self,
            nft_address: non_blank(str)="",
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            user_address: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getNftByContractAndUserAddressUsingPOST

            Args:
                nft_address (str): NFT contract address
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getNftByContractAndUserAddress"
            data = {
                "nft_address": nft_address,
                "page_index": page_index,
                "page_size": page_size,
                "user_address": user_address
            }
            return self._api_request(endpoint, data, export_file_name)
    

    @validate_parameters
    def getRecordByUserAddressAndTokenId(
            self,
            nft_address: non_blank(str)="",
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            token_id: non_blank(str)="",
            user_address: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getRecordByUserAddressAndTokenIdUsingPOST

            Args:
                nft_address (str): NFT contract address
                token_id (str): Token id
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getRecordByUserAddressAndTokenId"
            data = {
                "nft_address": nft_address,
                "page_index": page_index,
                "page_size": page_size,
                "token_id":token_id,
                "user_address": user_address
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getSingleNft(
            self,
            nft_address: non_blank(str)="",
            token_id: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getSingleNftUsingPOST

            Args:
                nft_address (str): NFT contract address
                token_id (str): Token id
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getSingleNft"
            data = {
                "nft_address": nft_address,
                "token_id":token_id
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getSingleNftRecord(
            self,
            nft_address: non_blank(str)="",
            page_index: non_negative(int)=0,
            page_size: non_negative(int)=20,
            token_id: non_blank(str)="",
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getSingleNftRecordUsingPOST

            Args:
                nft_address (str): NFT contract address
                token_id (str): Token id
                user_address (str): User address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getSingleNftRecord"
            data = {
                "nft_address": nft_address,
                "page_index": page_index,
                "page_size": page_size,
                "token_id":token_id
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getStates(
            self,
            nft_address: None,
            export_file_name: str="",
        ):
            """Fetches Nft data from the API. 
            https://developer.nftscan.com/doc/#operation/getStatesUsingPOST

            Args:
                nft_address [(str)]: array of NFT contract address
                export_file_name (str, optional): Exports the JSON data into a the
                specified file.

            Returns:
                [dict]: All Nfts for given protocol and users
            """
            endpoint = f"getStates"
            data = {
                "nft_address": nft_address,
            }
            return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getUserRecordByContract(
        self,
        nft_address: non_blank(str)="",
        page_index: non_negative(int)=0,
        page_size: non_negative(int)=20,
        user_address: non_blank(str)="",
        export_file_name: str="",
    ):
        """Fetches Nft data from the API. 
        https://developer.nftscan.com/doc/#operation/getUserRecordByContractUsingPOST

        Args:
            nft_address (str): NFT contract address
            user_address (str): User address
            export_file_name (str, optional): Exports the JSON data into a the
            specified file.

        Returns:
            [dict]: All Nfts for given protocol and users
        """
        endpoint = f"getUserRecordByContract"
        data = {
            "nft_address": nft_address,
            "page_index": page_index,
            "page_size": page_size,
            "user_address":user_address
        }
        return self._api_request(endpoint, data, export_file_name)


    @validate_parameters
    def getUserRecordByUserAddress(
        self,
        page_index: non_negative(int)=0,
        page_size: non_negative(int)=20,
        user_address: non_blank(str)="",
        export_file_name: str="",
    ):
        """Fetches Nft data from the API. 
        https://developer.nftscan.com/doc/#operation/getUserRecordByUserAddressUsingPOST

        Args:
            user_address (str): User address
            export_file_name (str, optional): Exports the JSON data into a the
            specified file.

        Returns:
            [dict]: All Nfts for given protocol and users
        """
        endpoint = f"getUserRecordByUserAddress"
        data = {
            "page_index": page_index,
            "page_size": page_size,
            "user_address":user_address
        }
        return self._api_request(endpoint, data, export_file_name)