from fastapi import FastAPI , Request
import uvicorn , os,sign,sys

os.system("cls")

def ipAccess(ip):
    return True 
    x = open("ipAccess.txt").read().split("\n")
    if ip not in x:
        return False
    else:
        return True
    
app = FastAPI()

@app.get("/gt")
async def bnb_req(request: Request):
    if ipAccess(request.client.host):
        address = request.query_params['address']
        remote_address = request.query_params['remote']
        
        return sign.get_hashes(address,remote_address)
    else:
        return "Not in list"

@app.get("/gh")
async def bnb_req(request: Request):
    if ipAccess(request.client.host):
        txID = request.query_params['id']
        remote_address = request.query_params['remote']
        
        return sign.get_tx_hash(txID,remote_address)
    else:
        return "Not in list"

@app.get("/cf")
async def bnb_req(request: Request):
    if ipAccess(request.client.host):
        hashID = request.query_params['id']
        signature = request.query_params['signature']
        remote_address = request.query_params['remote']
        
        return sign.confirm_hash(hashID,signature,remote_address)
    else:
        return "Not in list"

if __name__ == "__main__":
    app_name = sys.argv[0].split("/")[-1].split(".")[0]
    uvicorn.run(f"{app_name}:app",host="0.0.0.0",port=80,workers=5)
    # uvicorn.run(f"{app_name}:app",host="127.0.0.1",port=8000,workers=5)