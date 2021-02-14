from constants import *
import subprocess
import json
import os
from web3 import Web3
from bit import *
from dotenv import load_dotenv

load_dotenv("example.env")

from web3.middleware import geth_poa_middleware
from eth_account import Account

from pathlib import Path
from getpass import getpass

from bit import wif_to_key, PrivateKeyTestnet
from bit.network import NetworkAPI

mnemonic = os.getenv('MNEMONIC')

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
w3.eth.getBalance("0x0172DBb6C9583D8D4457547016Ad8BfaCDDd138D")
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
from web3.gas_strategies.time_based import medium_gas_price_strategy
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

def derive_wallets(mnemonic, coin, numderive):
    command = f"C:/xampp/php/php.exe ./hd-wallet-derive/hd-wallet-derive.php -g --coin={coin} --numderive={numderive} --cols=path,address,privkey,pubkey --format=json --mnemonic='{mnemonic}'"
    print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys=json.loads(output)
    return keys

derive_wallets("note absent option glide fossil volcano hire cabin cup diamond pond project", "BTC", 3)

coins = {ETH:derive_wallets(mnemonic,'eth', 3), BTCTEST:derive_wallets(mnemonic,'btc-test', 3)}

def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
ETH_key = priv_key_to_account(ETH, '9cb92f6a3745a47f20f9c4f0fa93d3457959bf1c6de442e78ee3b33833540e96')

# CREATE TRANSACTION
def create_tx(coin, account, recipient, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        trx_data = {
            "from": account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
        }
        return trx_data
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])
    
# SEND TRANSACTION
def send_tx(coin, account, recipient, amount):
    tx = create_tx(coin, account, recipient, amount)
    signed_tx = account.sign_transaction(tx)
    if coin == ETH:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
    
send_tx(ETH, ETH_key, "0xaEF84104518e1C2a4Af7Eea85429bBd05c93a9C9", 1)