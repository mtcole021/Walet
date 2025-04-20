from web3 import Web3

def buildTransaction(fromAddress , toAddress , data):
    fromAddress = Web3.to_checksum_address(fromAddress)
    toAddress = Web3.to_checksum_address(toAddress)
    
    if data['chain'] == 56:
        web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
    elif data['chain'] == 1:
        web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/a2951bbc2ebb494cbc4a9e3aeea7f7a3'))
        
    if data['type'] == 'ether':        
        estimateGasTx = {'from':fromAddress,'to':toAddress,'value':data['balance']}
        
        tx = {
            'chainId': data['chain'],
            'to': toAddress,
            'value': data['balance'],
            'data': '0x'
        }
        
        return {
            'estimateGasTx':estimateGasTx,
            'tx':tx
        }
    elif data['type'] == 'token':
        contractABI = [
            {
                'constant': False,
                'inputs': [
                {
                    'name': '_to',
                    'type': 'address'
                },
                {
                    'name': '_value',
                    'type': 'uint256'
                }
                ],
                'name': 'transfer',
                'outputs': [
                {
                    'name': '',
                    'type': 'bool'
                }
                ],
                'type': 'function'
            },			
            {
                "constant": False,
                "inputs": [
                    { "internalType": "address", "name": "spender", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "name": "approve",
                "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]        
        
        tokenAddress = Web3.to_checksum_address(data['contract'])
        
        contract = web3.eth.contract(
            address=tokenAddress,
            abi=contractABI
        )
        abi = contract.functions.approve(toAddress ,115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({'chainId':1,'nonec':50,'gas':21000,'gasPrice':5000000000})['data']
        
        estimateGasTx = {'from':fromAddress,'to':tokenAddress,'value':'0x0','data':abi}
        
        tx = {
            'chainId': data['chain'],
            'to': tokenAddress,
            'value': '0x0',
            'data': abi
        }
        
        
        return {
            'estimateGasTx':estimateGasTx,
            'tx':tx
        }
    elif data['type'] == 'nft':
        contractAbiErc721 = [
            {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "from",
                        "type": "address"
                    },
                    {
                        "internalType": "address",
                        "name": "to",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "tokenId",
                        "type": "uint256"
                    }
                ],
                "name": "safeTransferFrom",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        contractAbiErc1155 = [
            {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "from",
                        "type": "address"
                    },
                    {
                        "internalType": "address",
                        "name": "to",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "id",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                    },
                    {
                        "internalType": "bytes",
                        "name": "data",
                        "type": "bytes"
                    }
                ],
                "outputs": [],
                "stateMutability": "nonpayable",
                "name": "safeTransferFrom",
                "type": "function"
            }
        ]
        
        contractType = data['contract_type'].lower()
        tokenAddress = Web3.to_checksum_address(data['token_address'])
        
        if contractType == 'erc721':
            contract = web3.eth.contract(
                address=tokenAddress,
                abi=contractAbiErc721
            )
            
            abi = contract.functions.safeTransferFrom(fromAddress,toAddress,int(data['token_id'])).build_transaction({'chainId':1,'nonec':50,'gas':21000,'gasPrice':5000000000})['data']
        elif contractType == 'erc1155':
            contract = web3.eth.contract(
                address=tokenAddress,
                abi=contractAbiErc1155
            )
            
            abi = contract.functions.safeTransferFrom(fromAddress,toAddress,int(data['token_id']),data['amount'],b'').build_transaction({'chainId':1,'nonec':50,'gas':21000,'gasPrice':5000000000})['data']
        
        estimateGasTx = {'from':fromAddress,'to':tokenAddress,'value':'0x','data':abi}
        
        tx = {
            'chainId': data['chain'],
            'to': data['token_address'],
            'value': '0x',
            'data': abi
        }

        return {
            'estimateGasTx':estimateGasTx,
            'tx':tx
        }