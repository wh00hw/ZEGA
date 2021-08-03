import time
import json
import subprocess
from datetime import datetime
import base64
import pdb


class Zutils:

    @staticmethod
    def current_time():
        return int(time.mktime(datetime.today().timetuple()))

    @staticmethod
    def zsat2zec(zsat):
        return zsat/1000000000

    @staticmethod
    def read_file(filename):
        input_file = open(filename, "rb")
        return base64.b64encode(input_file.read()).decode('utf-8') + ">]EOF]>\n"

    @staticmethod
    def write_file(filename, file_as_base64, destination):
        with open(f"{destination}{filename}", "wb") as f:
            f.write(base64.b64decode(file_as_base64))

    @staticmethod
    def generate_memos(filename, height, description, input_file):
        chunks, chunk_size = len(input_file), 500
        memos = [input_file[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
        filename = filename.split("/")[-1]
        metadata = f"{filename} - {height} - {description} >]FILE]>"
        if len(metadata.encode('utf-8')) > 500:
            raise ValueError("Metadata exceeds 500 bytes")
        memos.insert(0, metadata)
        return memos

    @staticmethod
    def info_banner(info):
        return f"Vendor: {info['vendor']}\nLightwalletd Server: {info['server_uri']}\nBlock Height: {info['latest_block_height']}"

    @staticmethod
    def zega_banner():
        return """
███████╗███████╗ ██████╗  █████╗ 
╚══███╔╝██╔════╝██╔════╝ ██╔══██╗
  ███╔╝ █████╗  ██║  ███╗███████║
 ███╔╝  ██╔══╝  ██║   ██║██╔══██║
███████╗███████╗╚██████╔╝██║  ██║
╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
                            
A command line encrypted-file-sharing protocol using Zcash Light Client

Twitter: @nic_whr - ZEC: zs13zdde4mu5rj5yjm2kt6al5yxz2qjjjgxau9zaxs6np9ldxj65cepfyw55qvfp9v8cvd725f7tz7

"""
