#!/usr/bin/env python3
"""Print the current TOTP code for a base32 secret (RFC 6238, SHA-1, 30 s, 6 digits)."""
import base64, hashlib, hmac, struct, sys, time
secret = sys.argv[1]
secret += "=" * ((8 - len(secret) % 8) % 8)
key = base64.b32decode(secret)
counter = int(time.time()) // 30
digest = hmac.new(key, struct.pack('>Q', counter), hashlib.sha1).digest()
o = digest[-1] & 0x0F
code = (struct.unpack('>I', digest[o:o+4])[0] & 0x7FFFFFFF) % 1_000_000
print(f'{code:06d}')
