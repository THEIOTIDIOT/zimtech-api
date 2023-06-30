import base64
import hashlib
import logging
import logging.config
from pathlib import Path
from Crypto import Random
from Crypto.Cipher import AES
import yaml
import os
from pathlib import Path

PROJECTROOT = Path(__name__).parent.resolve()


class MyLogger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        # Setting some package specific customizations
        # (Just aligns the logger for better legibility)
        logging.addLevelName(logging.CRITICAL, "CRITICAL".ljust(8))
        logging.addLevelName(logging.ERROR, "ERROR".ljust(8))
        logging.addLevelName(logging.WARNING, "WARNING".ljust(8))
        logging.addLevelName(logging.INFO, "INFO".ljust(8))
        logging.addLevelName(logging.DEBUG, "DEBUG".ljust(8))
        logging.addLevelName(logging.NOTSET, "NOTSET".ljust(8))


# Setting the custom logger class to the default
logging.setLoggerClass(MyLogger)


def config_logger_options():
    # Parse YAML config as dict and configure logging system
    with open(Path(PROJECTROOT, "logger_config.yml").resolve(), "r") as f:
        config = dict(yaml.safe_load(f))
        logging.config.dictConfig(config)


config_logger_options()


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]