from random import choice
import requests
from lxml import html
import os,cloudscraper,math

def proxyHTTP():
	return True

def get_while(url,headers = None):
	prx = proxyHTTP()
	while prx != []:
		ran = ""
		if headers != None:
			try:
				r = requests.get(url,headers=headers,proxies=None,timeout=5)
				if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
					print("Requst with \033[92m"+ran['https']+"\033[0m Success")
					return r
				else:
				
					print("Requst with \033[91m"+ran['https']+"\033[0m Banned.")
			except Exception as e:
				print("Requst with \033[91m"+ran['https']+"\033[0m Failed. info: "+str(e))
				prx.remove(ran)
		else:
			try:
				r = requests.get(url,headers=headers,proxies=None,timeout=5)
				if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
					print("Requst with \033[92m"+ran['https']+"\033[0m Success")
					return r
				else:
					
					print("Requst with \033[91m"+ran['https']+"\033[0m Banned.")
			except Exception as e:
				print("Requst with \033[91m"+ran['https']+"\033[0m Failed. info: "+str(e))
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
					print("Requst with \033[92m"+ran['https']+"\033[0m Success")
					return r
				else:
					
					print("Requst with \033[91m"+ran['https']+"\033[0m Banned.")
			except Exception as e:
				print("Requst with \033[91m"+ran['https']+"\033[0m Failed. info: "+str(e))
				prx.remove(ran)
		else:
			try:
				r = scraper.get(url,headers=headers,proxies=None,timeout=5)
				if "Sorry, our servers are currently busy" not in r.text and "Attention Required! | Cloudflare" not in r.text and r.status_code == 200:
					print("Requst with \033[92m"+ran['https']+"\033[0m Success")
					return r
				else:
					
					print("Requst with \033[91m"+ran['https']+"\033[0m Banned.")
			except Exception as e:
				print("Requst with \033[91m"+ran['https']+"\033[0m Failed. info: "+str(e))
				prx.remove(ran)
	else:
		return "error"	
	
def api_call(path):
    if '?' in path:
        return requests.get('https://api.cryptowat.ch/{}?&apikey=6FOX35QNY786JV11P00I'.format(path)).json()
    else:
        return requests.get('https://api.cryptowat.ch/{}?apikey=6FOX35QNY786JV11P00I'.format(path)).json()

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

def opensea(url):
	res = get_while(url,headers={'Accept': 'application/json'})
	print('opensea : ',res , url)
	try:
		return res.json()
	except:
		return None

def get_address_nfts(address , chain):
	data = requests.get(f'https://deep-index.moralis.io/api/v2/{address}/nft?chain={chain}',headers={'X-API-KEY':'e76WLqXJchFmZHjC6Y2GWHIHk1I2ng8K3divXv3fqcZj7BAmyKne9EsMtZZ2zY16','accept':'application/json'}).json()

	cache = {}
 
	balance_nfts_value = 0
	nfts = []
	if chain == 'bsc':
		bnb_price = get_bnb_price()
		for nft in data['result']:
			coin_price = bnb_price
			res = get_while(f'https://api.treasureland.market/v1/nft/detail?chain_id=56&contract={nft["token_address"]}&token_id={nft["token_id"]}')
			if res.status_code == 200:
				res = res.json()
				if 'data' in res and 'price' in res['data'] and res['data']['price']:
					floor_price = int(res['data']['price']) / 1000000000000000000
					if res['data']['symbol'].lower() != 'bnb':
						coin_price = get_coin_price(res['data']['symbol'])
				else:
					floor_price = 0
			else:
				floor_price = 0
    
			nft['amount'] = int(nft['amount'])
			nfts.append({
				'type':'nft',
				'contract_type':nft['contract_type'],
				'token_address':nft['token_address'],
				'token_id':nft['token_id'],
				'amount':nft['amount'],
				'name':nft['name'],
				'symbol':nft['symbol'],
				'floor_price':floor_price,
				'value':floor_price * coin_price * nft['amount']
			})
   
			balance_nfts_value += floor_price * coin_price
	
	
	elif chain == 'eth':
		eth_price = get_eth_price()
		print(eth_price)
		for nft in data['result']:
			if 'name' in nft and nft["name"]:
				collection_slug = nft["name"].lower().replace(' ','-').replace(':','')

				if collection_slug in cache:
					floor_price = cache[collection_slug]
					print(f'using cache {collection_slug} {floor_price}')
				else:
					res = opensea(f'https://api.opensea.io/api/v1/collection/{collection_slug}/stats')
					if res and 'stats' in res and 'floor_price' in res['stats']:
						floor_price = res['stats']['floor_price']
						if floor_price:
							if res['stats']["total_volume"] > 0:
								floor_price = floor_price
								cache[collection_slug] = floor_price
							else:
								floor_price = 0
								cache[collection_slug] = floor_price
						else:
							floor_price = 0
							cache[collection_slug] = floor_price
					else:
						floor_price = 0
						cache[collection_slug] = floor_price
			else:
				floor_price = 0
    
			nft['amount'] = int(nft['amount'])
			nfts.append({
				'type':'nft',
				'contract_type':nft['contract_type'],
				'token_address':nft['token_address'],
				'token_id':nft['token_id'],
				'amount':nft['amount'],
				'name':nft['name'],
				'symbol':nft['symbol'],
				'floor_price':floor_price,
				'value':floor_price * eth_price * nft['amount']
			})
   
			balance_nfts_value += floor_price * eth_price
	return nfts,balance_nfts_value

def balance(address , explorer , get_price,chain):
	content = scraper_while(explorer+"/address/"+address).text

	xml = html.fromstring(content)

	bnb_price = get_price()

	value = xml.cssselect('.card-body div .col-md-8')[0].text_content()
	balance = float(value.split(' ')[0])
	balance_usd = float(value.split(' ')[0]) * bnb_price

	tokens = []

	total_token_balance = 0

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
						if 'pex' in name.lower() or 'project-x' in name.lower() or mustGetToken or value >= 30:
							token = {}
							token['name'] = name
							token['value'] = value
							token['contract'] = row.cssselect('.link-hover')[0].attrib['href'].split('/')[2].split('?')[0]
							token['amount'] = float(row.cssselect('.list-amount')[0].text_content().split(' ')[0].replace(',',''))
							tokens.append(token)
							total_token_balance += value


	if len(tokens) > 0:
		hasTokens = True
		for token in tokens:
			print(token['contract'])
			token_balance = token['value']
			content = scraper_while(explorer+"/token/"+token['contract']).content
			xml = html.fromstring(content)

			decimals = xml.cssselect('.card-body #ContentPlaceHolder1_trDecimals .col-md-8')[0].text_content().strip()
			token['decimals'] = int(decimals)
			token['type'] = 'token'
	else:
		tokens = []
		hasTokens = False

	nfts , balance_usd_nfts = get_address_nfts(address , chain)
	total_token_balance += balance_usd_nfts
 
	if len(nfts) > 0:
		hasTokens = True
 
	tokens = sorted(tokens + nfts, key=lambda token: token['value'], reverse=True)
 
	if balance_usd + total_token_balance > float(open("limit.txt").read()):
		tt = f'''
balance : {str(balance)},
balance_usd : {balance_usd},
tokens : {tokens},
hasTokens : {hasTokens},
address : {address}, 
gasForToken : {str(2 / bnb_price)},
token_balance : {total_token_balance},
{chain}_price : {bnb_price}
		'''
		return {
			'balance':str(balance),
			'balance_usd':balance_usd,
			'tokens':tokens,
			'hasTokens':hasTokens,
			'address':address,
			'gasForToken':str(2 / bnb_price),
			'token_balance':total_token_balance,
			f'{chain}_price':bnb_price,
			'balance_usd_nfts':balance_usd_nfts
		}

	else:
		tt = f'''
balance : {str(0)},
balance_usd : 700,
tokens : {tokens},
hasTokens : {hasTokens},
gasForToken : {str(2 / bnb_price)},
token_balance : {total_token_balance},
{chain}_price : {bnb_price}
'''
		return {
			'balance':str(0),
			'balance_usd':0,
			'tokens':tokens,
			'hasTokens':hasTokens,
			'gasForToken':str(2 / bnb_price),
			'token_balance':total_token_balance,
			f'{chain}_price':bnb_price,
			'balance_usd_nfts':balance_usd_nfts
		}

def bnbbalance(address):
	return balance(address , 'https://bscscan.com' , get_bnb_price , 'bsc')

def ethbalance(address):
	return balance(address , 'https://etherscan.io' , get_eth_price,'eth')


def setlimit(key,limit):

	if key != "kos5464":
		return {			
			'status':False,
			'msg':'Key is invalid'
		}
	try:
		limit = int(limit)
	except:
		return {
			'status':False,
			'msg':'limit must be integer'
		}
	else:
		f = open('limit.txt','w')
		f.write(str(limit))
		f.close()
		return{
			'status':True
		}

def setwithoutfee(key,status):

	if key != "kos5464":
		return {			
			'status':False,
			'msg':'Key is invalid'
		}
	if status not in ['true','false']:		
		return{
			'status':False,
			'msg':'status must be "true" of "false"'
		}
	f = open('withoutFee.txt','w')
	f.write(status)
	f.close()

	return {
		'status':True
	}

def getcontract(contract):

	content = scraper_while("https://bscscan.com/token/"+contract).content

	xml = html.fromstring(content)

	name = xml.cssselect('.media-body .text-secondary.small')[0].text_content().strip()
	symbol = xml.cssselect('.col-md-8.font-weight-medium b')[0].text_content().strip()

	return {
		'name':name,
		'symbol':symbol
	}

contractAbi = [
	{
        "constant": True,
        "inputs": [
            { "internalType": "address", "name": "owner", "type": "address" },
            { "internalType": "address", "name": "spender", "type": "address" }
        ],
        "name": "allowance",
        "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
	{
        "constant": False,
        "inputs": [
            { "internalType": "address", "name": "sender", "type": "address" },
            { "internalType": "address", "name": "recipient", "type": "address" },
            { "internalType": "uint256", "name": "amount", "type": "uint256" }
        ],
        "name": "transferFrom",
        "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def gettokens(address,contractAddress):

	amount = requests.get(f'https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={contractAddress}&address={address}&tag=latest&apikey=1HXUYVMVPCDA6HIBZYFJ9SASQKDW3WT8CW').json()['result']

	amount = int(amount)

	if contractAddress.lower() == '0xe9e7cea3dedca5984780bafc599bd69add087d56':
		print('\n[+] BUSD ROUNDING\n')
		amount = math.floor(amount / (10 ** 18)) * (10 ** 18)


	os.system(f'node get.js {address} {contractAddress} "{amount}"')

	return {
		'status':True
	}
 
def getnft(address,contractAddress,contractType,tokenId,amount):
	
	amount = int(amount)

	argss = f'node getNft.js {address} {contractAddress} {contractType} {tokenId} "{amount}"'
	print(argss)
	os.system(argss)

	return {
		'status':True
	}
