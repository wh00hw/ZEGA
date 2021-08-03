from .zega_utils import Zutils
import pdb


class ZDownload:
    def __init__(self, zec_wallet):
        self.zec_wallet = zec_wallet

    def download(self, transactions, destination, verbose):
        if not destination[-1] == '/':
            destination = destination+'/'
        transactions.sort(key=lambda x: int(bytes.fromhex(
            x.get('memohex')).decode('ASCII').split("--:--")[0]))
        metadata = transactions.pop(0)["memo"].split("--:--")[1]
        filename = metadata.split(" ")[0]
        file_as_base64 = ""
        eof = False
        for tx in transactions:
            if not eof:
                memo_list = bytes.fromhex(tx['memohex']).decode('ASCII').split("--:--")
                memo = memo_list[1].replace(" ", "").replace("\n", "")
                file_as_base64 += memo
            if ">]EOF]>" in memo:
                eof = True
            if verbose:
                print(memo)
        if verbose:
            print(filename, metadata)
            print(file_as_base64)
        file_as_base64 = file_as_base64.replace(">]EOF]>", "")
        Zutils.write_file(filename, file_as_base64, destination)
        print(f">>> SUCCESS! {destination}{filename} successfully downloaded!")
