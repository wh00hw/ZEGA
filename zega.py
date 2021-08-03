from src.zupload import ZUpload
from src.zdownload import ZDownload
from src.zec_wallet_lite import ZecWalletLite
from src.zega_utils import Zutils
import argparse
import pdb

DEFAULT_OUT_DIR = "./"
DEFAULT_RESCAN_HEIGH = 1500000
TESTNET_SERVER = "https://testnet.lightwalletd.com:9067"


class Zega:
    def __init__(self, server=False, verbose=False):
        self.verbose = verbose
        self.zec_wallet = ZecWalletLite(server=server)
        self.uploader = ZUpload(self.zec_wallet)
        self.downloader = ZDownload(self.zec_wallet)
        print(Zutils.zega_banner())
        if verbose:
            print(Zutils.info_banner(self.zec_wallet.info()))

    def upload_to_custom_zaddr(self, filename, description, zaddr):
        print(">>> WARNING: BE SURE TO HAVE THE CORRISPONDING Z-ADDRESS VIEWING KEY IN ORDER TO DOWNLOAD THE FILE")
        self.uploader.upload(filename, description, zaddr, self.verbose)

    def upload_to_new_zaddr(self, filename, description):
        zaddr, view_key = self.zec_wallet.generate_zaddr_vkey()
        self.uploader.upload(filename, description, zaddr, self.verbose)
        print(f">>> UPLOADED TO Z-ADDRESS: {zaddr}")
        print(f">>> VIEWING KEY: {view_key}")

    def download_from_viewing_key(self, viewing_key, rescan_height=DEFAULT_RESCAN_HEIGH, destination=DEFAULT_OUT_DIR):
        self.zec_wallet.sync()
        if self.verbose:
            print(f">>> IMPORTING VIEWING KEY: {viewing_key}")
        zaddr = self.zec_wallet.import_viewing_key(viewing_key, rescan_height)
        if self.verbose:
            print(f">>> ZADDR IMPORTED CORRECTLY: {zaddr}")
        transactions = self.zec_wallet.list_address_memos_ingoing(zaddr)
        self.downloader.download(transactions, destination, self.verbose)

    def download_from_owned_address(self, zaddr, destination="./"):
        self.zec_wallet.sync()
        transactions = self.zec_wallet.list_address_memos_outgoing(zaddr)
        self.downloader.download(transactions, destination, self.verbose)


def init_argparse() -> argparse.ArgumentParser:
    """
    Define and manage arguments passed to Zega via terminal.
    :return argparse.ArgumentParser
    """

    parser = argparse.ArgumentParser(
        description='Zega - A command line file-sharing protocol using ZecWallet light client')
    base_subparser = argparse.ArgumentParser(add_help=False)
    # Shared arguments
    base_subparser.add_argument('--verbose', '-v', action='store_true', help='Verbose mode')
    base_subparser.add_argument('--zaddr', '-z', type=str, help="Provide a z-address", required=False)
    base_subparser.add_argument('--testnet', '-t', action='store_true',
                                help="Use Zcash Testnet  (Server: testnet.lightwalletd.com)", default=False)
    base_subparser.add_argument('--server', '-s', type=str,
                                help="Connect to custom lightwalletd server", default=False, required=False)
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)
    upload_parser = subparsers.add_parser("upload", parents=[base_subparser])
    download_parser = subparsers.add_parser("download", parents=[base_subparser])
    # Flag for sub-parser
    upload_parser.add_argument('--file', '-f', help="Input file", required=True)
    upload_parser.add_argument('--description', '-d', help="File description", required=True)

    download_parser.add_argument('--viewing-key', '-k', type=str,
                                 help="Download the specified viewing-key related file", required=False)
    download_parser.add_argument('--rescan-height', '-r', help=f"Rescan from block height (Default: {DEFAULT_RESCAN_HEIGH})",
                                 required=False, default=DEFAULT_RESCAN_HEIGH)
    download_parser.add_argument('--destination', '-o', type=str,
                                 help=f"Save file to the specified destination folder (Default: {DEFAULT_OUT_DIR})", default=DEFAULT_OUT_DIR, required=False)

    return parser


args = init_argparse().parse_args()

if __name__ == '__main__':
    if args.testnet:
        server = TESTNET_SERVER
    elif args.server:
        server = args.server
    else:
        server = False
    try:
        zega = Zega(server=server, verbose=args.verbose)
        if args.command == "upload":
            if args.zaddr:
                zega.upload_to_custom_zaddr(args.file, args.description, args.zaddr)
            else:
                zega.upload_to_new_zaddr(args.file, args.description)
        elif args.command == "download":
            if args.zaddr:
                zega.download_from_owned_address(args.zaddr, args.destination)
            else:
                zega.download_from_viewing_key(args.viewing_key, args.rescan_height, args.destination)
    except Exception as e:
        print(e)
