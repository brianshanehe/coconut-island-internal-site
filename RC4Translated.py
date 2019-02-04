import codecs
import hashlib
from Utils import singleton


@singleton
class RC4(object):
    def _ksa(self, s, encrypt_key):
        """key scheduling algorithm"""
        j = 0
        for i in range(256):
            j = (j + s[i] + ord(encrypt_key[i % len(encrypt_key)])) % 256
            s[i], s[j] = s[j], s[i]  # swap values
        return s

    def _prga(self, s, key_schedule, plaintext_length):
        """pseudo random generation algorithm"""
        i = 0
        j = 0
        for k in range(plaintext_length):
            i = (i + 1) % 256
            j = (j + s[i]) % 256
            s[i], s[j] = s[j], s[i]  # swap values
            key_schedule[k] = chr(s[(s[i] + s[j]) % 256])
            k += 1
        return key_schedule

    def _split_key_string(self, key_string, part_len):
        """splits string into substrings of length part_len, with the remainder as the last value
            eg: abcdefg, 2 splits into ab cd ef g       and abcdefg, 3 splits into abc def g"""
        split_list = []
        counter = 0
        while counter < len(key_string):
            split_list.append(key_string[counter:min(part_len, len(key_string) - counter) + counter])
            counter += part_len
        return split_list

    def encrypt(self, plaintext, encrypt_key):
        """handles encryption and decryption for strings"""
        s = list(range(256))
        key_schedule = list(range(len(plaintext)))

        s = self._ksa(s, encrypt_key)
        key_schedule = self._prga(s, key_schedule, len(plaintext))

        builder = ""
        for i in range(len(plaintext)):
            builder += chr(ord(plaintext[i]) ^ ord(key_schedule[i]))
        return builder

    def encrypt_optimize(self, plaintext, encrypt_key):
        """handles encryption and decryption for strings more efficiently, MAYBE"""
        s = list(range(256))
        key_schedule = list(range(len(plaintext)))

        s = self._ksa(s, encrypt_key)
        key_schedule = self._prga(s, key_schedule, len(plaintext))
        cache = []
        for i in range(len(plaintext)):
            cache.append(chr(ord(plaintext[i]) ^ ord(key_schedule[i])))
        return "".join(cache)

    def encrypt_optimize_bytes(self, input_bytes, key):
        """handles encryption and decryption for bytes more efficiently, MAYBE"""
        input_string = codecs.decode(input_bytes, "utf-8")          #translates to text
        output_string = self.encrypt_optimize(input_string, key)
        return codecs.encode(output_string, "utf-8")                #translaters to bytes

    def key_from_id(self, id):
        """scrambles user id, performs an MD5 hash, then returns the hex key for the cipher"""
        #ACTUAL ALGORITHM IS NOT SHOWN HERE
        return id
