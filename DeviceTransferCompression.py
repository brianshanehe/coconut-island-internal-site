import codecs
import gzip
import base64

from Utils import singleton


@singleton
class DeviceTransferCompression(object):
    def _decompress_string(self, compressed_string):
        """decodes to base 64 and then decompresses using gzip, returning the decompressed string"""
        try:
            before_bytes = base64.b64decode(compressed_string)
            zip = gzip.decompress(before_bytes)
            return codecs.decode(zip, "utf-8")
        except:
            raise

    def _compress_string(self, decompressed_string):
        """decodes to binary data and then compresses using gzip, returning the encoded base 64 bytes"""
        try:
            before_bytes = codecs.encode(decompressed_string, "utf-8")
            zip = gzip.compress(before_bytes)
            return base64.b64encode(zip)
        except:
            raise

    def handle_add(self, source_main_dec):
        """decompresses string, adds the flag to force use cloud data, then compresses string"""
        decompressed_string = self._decompress_string(source_main_dec)
        return self._compress_string("return {useCloud=true," + decompressed_string[8:])