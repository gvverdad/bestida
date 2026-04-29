import logging

from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

log = logging.getLogger(__name__)


class CryptField(object):

    def __init__(self, fields):
        if type(fields) is not list:
            fields = [fields]

        self.fields = fields

        secret = "gVv130400I$270406P@Gi111011"
        self.cipher = AesEngine()
        self.cipher._update_key(secret)
        # padding types: 'pkcs5', 'oneandzeroes','zeroes','naive'
        # see sqlalchemy_utils.types.encrypted.padding.py
        self.cipher._set_padding_mechanism("pkcs5")

    def decrypt(self, target):
        encrypted = getattr(target, '_encrypted', True)
        if not encrypted:
            return
        for f in self.fields:
            value = getattr(target, f)
            value = self.cipher.decrypt(value)
            setattr(target, f, value)
        target._encrypted = False

    def load_decrypt(self, target, context):
        self.decrypt(target)

    def refresh_decrypt(self, target, context, attrs):
        self.decrypt(target)

    def encrypt(self, mapper, connection, target):
        encrypted = getattr(target, '_encrypted', False)
        if encrypted:
            self.decrypt(target)
        for f in self.fields:
            value = getattr(target, f)
            value = self.cipher.encrypt(value)
            setattr(target, f, value)
        target._encrypted = True


class CryptText(object):
    def __init__(self, value):
        self.value = value

        secret = "gVv130400I$270406P@Gi111011"
        self.cipher = AesEngine()
        self.cipher._update_key(secret)
        # padding types: 'pkcs5', 'oneandzeroes','zeroes','naive'
        # see sqlalchemy_utils.types.encrypted.padding.py
        self.cipher._set_padding_mechanism("pkcs5")

    def encrypt(self):
        return self.cipher.encrypt(self.value)

    def decrypt(self):
        return self.cipher.decrypt(self.value)


if __name__ == '__main__':
    user = type("user", (object,), {})()
    user.password = "pogi"
    print("Data:", user.password)

    CryptField("password").encrypt(None, None, user)
    print("Encrypted:", user.password, user._encrypted)

    CryptField("password").decrypt(user)
    print("Decrypted:", user.password, user._encrypted)
