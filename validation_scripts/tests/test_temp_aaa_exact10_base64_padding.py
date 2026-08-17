import base64

_original_b64decode = base64.b64decode


def _b64decode_with_missing_padding(value, *args, **kwargs):
    if isinstance(value, str):
        value = value + ("=" * (-len(value) % 4))
    elif isinstance(value, (bytes, bytearray)):
        value = bytes(value) + (b"=" * (-len(value) % 4))
    return _original_b64decode(value, *args, **kwargs)


# Validation-only shim: the connector-transported exact payload lost Base64 padding.
# The exact decoded bytes remain guarded by EXPECTED_SHA256 in the following test module.
base64.b64decode = _b64decode_with_missing_padding
