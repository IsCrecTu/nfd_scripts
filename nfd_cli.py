import argparse
import base64
from algosdk.future import transaction
from algosdk.encoding import encode_address
from algosdk.v2client import algod

algod = algod.AlgodClient('', 'https://mainnet-api.algonode.cloud', headers={'User-Agent': 'algosdk'})

mainnet_registryAppID = int(760937186)

def FindNFDAppIDByName(nfdName, registryAppID):
    nameLSIG = getLookupLSIG("name/", nfdName, registryAppID)

    #Read the local state for our registry SC from this specific accont
    lsig_address = nameLSIG.address()
    account = algod.account_application_info(lsig_address, registryAppID)
    for n in range(len(account['app-local-state']['key-value'])):
        if account['app-local-state']['key-value'][n]['key'] == "aS5hcHBpZA==":  #i.appid
            coded_string = account['app-local-state']['key-value'][n]['value']['bytes']
            decoded_string = base64.b64decode(coded_string)
            nfdAppID = int.from_bytes(decoded_string, 'big')
            print (f"nfdAppID: {nfdAppID}")  
    
    return nfdAppID


def getLookupLSIG(prefixBytes, lookupBytes, registryAppID):
    """#pragma version 5
        intcblock 1                   # 0x20, 0x01, 0x01
        pushbytes 0x0102030405060708  # 0x80, 0x08, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08
        btoi                          # 0x17
        store 0                       # 0x35, 0x00
        txn ApplicationID             # 0x31, 0x18 (? 0x24)
        load 0                        # 0x34, 0x00
        ==                            # 0x12
        txn TypeEnum                  # 0x31, 0x10
        pushint 6                     # 0x81, 0x06
        ==                            # 0x12
        &&                            # 0x10
        txn OnCompletion              # 0x31, 0x19 (?0x25)
        intc_0 // 1                   # 0x22
        ==                            # 0x12
        txn OnCompletion              # 0x31, 0x19 (?0x25)
        pushint 0                     # 0x81, 0x00
        ==                            # 0x12
        ||                            # 0x11
        &&                            # 0x10
        bnz label1                    # 0x40, 0x00, 0x01
        err                           # 0x00
        label1:                       
        intc_0 // 1                   # 0x22
        return                        # 0x43
        bytecblock "xxx" """          # 0x26, 0x01
	    

    output = ""
    prefixBytes_byte = str.encode(prefixBytes)
    lookupBytes_byte = str.encode(lookupBytes)
    
    sigLookupByteCode = bytes([0x05, 0x20, 0x01, 0x01, 0x80, 0x08, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x17, 0x35, 0x00, 0x31, 0x18, 0x34, 0x00, 0x12, 0x31, 0x10, 0x81, 0x06, 0x12, 0x10, 0x31, 0x19, 0x22, 0x12, 0x31, 0x19, 0x81, 0x00, 0x12, 0x11, 0x10, 0x40, 0x00, 0x01, 0x00, 0x22, 0x43, 0x26, 0x01])
    sigLookupByteCode_firstpart = sigLookupByteCode[:6]
    sigLookupByteCode_lastpart = sigLookupByteCode[14:]

    contractSlice = sigLookupByteCode[6:14]
    contractSlice = registryAppID.to_bytes(8, 'big')
    
    sigLookupByteCode = sigLookupByteCode_firstpart + contractSlice + sigLookupByteCode_lastpart
    bytesToAppend = prefixBytes_byte + lookupBytes_byte

    nBytes = len(bytesToAppend).to_bytes(10, 'big')
    nBytes = nBytes.replace(b'\x00', b'')

    composedBytecode = bytes(sigLookupByteCode + nBytes + bytesToAppend )

    escrowAccount = transaction.LogicSigAccount(composedBytecode)
    return escrowAccount

def GetNFDOwner(nfdAppID):
    for n in range(len(nfdAppID['params']['global-state'])):
        if nfdAppID['params']['global-state'][n]['key'] == 'aS5vd25lci5h': # i.owner.a
            coded_string = nfdAppID['params']['global-state'][n]['value']['bytes']
            decoded_string = base64.b64decode(coded_string)
            nfdOwner = encode_address(decoded_string)
    return nfdOwner


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-n", "--name", help='name help')
    group.add_argument("-a", "--address", help='address help')
    args = parser.parse_args()

    registryAppID = mainnet_registryAppID

    if args.name:
        nfdAppID = FindNFDAppIDByName(args.name, registryAppID)
    elif args.address:
        print (f"address is: {args.address}")
    else:
        print("the end")
    
    appData = algod.application_info(nfdAppID)
    nfdOwner = GetNFDOwner(appData)
    print (f"current owner: {nfdOwner}")

if __name__ == "__main__":
    main()
