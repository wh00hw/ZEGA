import base64
import time
import subprocess
import json
from .zega_utils import Zutils
import pdb


class ZUpload:
    def __init__(self, zec_wallet, single_tx_cost=10, wait_sleep=5):
        self.zec_wallet = zec_wallet
        self.single_tx_cost = single_tx_cost
        self.total_tx_cost = self.zec_wallet.default_fee() + self.single_tx_cost
        self.wait_sleep = wait_sleep

    def upload(self, filename, description, zaddr, verbose=False):
        print(f">>> UPLOADING {filename} TO Z-ADDRESS: {zaddr}")
        input_file = Zutils.read_file(filename)
        self.zec_wallet.sync()
        height = self.zec_wallet.height()
        memos = Zutils.generate_memos(filename, height, description, input_file)
        upload_cost = Zutils.zsat2zec(self.total_tx_cost*(len(memos)))
        print(">>> UPLOADING COST: {:.9f} ZEC".format(upload_cost))
        count = 0
        start_time = Zutils.current_time()
        if verbose:
            print(f">>> BEGINNING UPLOAD --> {filename}")
        print(">>> This will take a while ...")
        while count < len(memos):
            if self.zec_wallet.sync():
                last_txid = self.zec_wallet.get_last_txid()
                balance = self.zec_wallet.get_wallet_balance()
                cost_left = upload_cost - self.total_tx_cost*(count+1)
                if balance < cost_left:
                    if verbose:
                        print(f">>> NOT ENOUGH SPENDABLE ZBALANCE: {cost_left} zsat needed, you have {balance} zsat")
                    break
                memo = ("{}--:--{}".format(count, memos[count]))
                if not self.zec_wallet.is_tx_confirmed(last_txid):
                    if verbose:
                        print(f">>> WAITING TX CONFIRMATION: {last_txid}")
                        time.sleep(self.wait_sleep)
                    continue
                tx = self.zec_wallet.send(
                    zaddr, self.single_tx_cost, memo)
                if tx.get("error"):
                    print(">>> TX ERROR: {}".format(tx.get("error")))
                    break
                if verbose:
                    print(tx)
                count += 1
            if verbose:
                print(memo)
            print("{}/{} {}s".format(count, len(memos), Zutils.current_time() - start_time))
        if verbose:
            print(f">>> END UPLOAD ***** --> {filename}")
            print(">>> UPLOAD TIME: {}s".format(Zutils.current_time() - start_time))
