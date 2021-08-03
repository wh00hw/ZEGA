import subprocess
import json
import pdb
import regex
import sys


class ZecWalletLite:
    def __init__(self, server=False):
        self.server = f"--server {server}" if server else ""
        self.pattern = regex.compile(r'[\{|\[](?:[^{}]|(?R))*[\}|\]]')

    def run_command(self, args):
        process = subprocess.run(f'zecwallet-cli {self.server} {args}',
                                 check=True, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        output_json = self.pattern.findall(process.stdout)
        try:
            return [json.loads(output_json[i]) for i in range(len(output_json))] if len(output_json) > 1 else json.loads(output_json[0])
        except Exception:
            print(f"Error parsing zecwallet-cli JSON output: {process.stdout}")
            sys.exit()

    def default_fee(self):
        return self.run_command("defaultfee").get("defaultfee")

    def sync(self):
        return True if self.run_command("sync").get("result") == "success" else False

    def info(self):
        return self.run_command("info")

    def height(self):
        return self.run_command("height").get("height")

    def addresses(self):
        return self.run_command("addresses")

    def balance(self):
        return self.run_command("balance")

    def new_z(self):
        return self.run_command("new z")

    def export(self):
        return self.run_command("export")

    def import_viewing_key(self, viewing_key, birthday):
        return self.run_command(f"import {viewing_key} {birthday}")[0]

    def send(self, to, value, memo):
        return self.run_command(f"send {to} {value} \"{memo}\"")

    def sendprogress(self):
        return self.run_command(f"sendprogress")

    def get_wallet_balance(self):
        return self.balance().get("spendable_zbalance")

    def get_address_balance(self, zaddr):
        return next(filter(lambda x: x.get("address") == zaddr, self.balance().get("z_addresses")))

    def list_address_memos_outgoing(self, zaddr):
        return [x.get('outgoing_metadata')[0] for x in list(filter(lambda x: x.get('outgoing_metadata') and x.get('outgoing_metadata')[0].get('address') == zaddr, self.run_command("list allmemos")))]

    def list_address_memos_ingoing(self, zaddr):
        return list(filter(lambda x: x.get('address') == zaddr, self.run_command("list allmemos")))

    def generate_zaddr_vkey(self):
        zaddr = self.new_z()[0]
        return zaddr, next(filter(lambda x: x.get("address") == zaddr, self.export())).get("viewing_key")

    def is_tx_confirmed(self, tx_id):
        return not next(filter(lambda x: x.get('txid') == tx_id, self.run_command("list allmemos"))).get("unconfirmed")

    def get_last_txid(self):
        return self.run_command("lasttxid").get("last_txid")
