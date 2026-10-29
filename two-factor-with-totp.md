# Two-Factor with TOTP

By the end of this chapter ada owns
a working second factor — a TOTP
device registered with Authelia —
and the vault opens for her
password *plus* a code, while the
password alone is turned away. You
will also have met **elevation**,
the proof of identity Authelia
demands before it lets anyone so
much as register that device, and
which surprises everyone the first
time.

**TOTP** — time-based one-time
password — is the familiar six
digits that change every thirty
seconds. An authenticator app and
Authelia share a secret; each
derives the current code from the
secret and the clock, and they
agree without ever speaking. (The
shared clock is load-bearing:
chapter 12 returns to it.)

## First, an unexpected wall

Signed in as ada, the lab went to
register a device, and Authelia
refused with a small structured
no:

```json
{"status":"KO","data":{
  "elevation":true,
  "first_factor":false,
  "second_factor":false}}
```

Read it as a sentence: *this
operation needs an elevated
session, and yours is not one.* A
fresh password login is enough to
read pages; it is not enough to
change the locks — registering a
device, changing a password, the
operations an attacker with a
stolen session would want first.
For those, Authelia asks for
**elevation**: a one-time code,
sent to the user's mailbox through
the notifier, proving the person
at the keyboard also holds the
account's mail.

The dance, all of it visible in
the lab because the "mailbox" is a
file (t14–t16):

```bash
# 1. Ask for elevation
curl -X POST \
  https://auth.lab.local:9091/api/user/session/elevation \
  -b cookies-ada.txt -c cookies-ada.txt
# {"status":"OK","data":{"delete_id":"..."}}

# 2. Read the code in the letter
#    (notifications.txt):  3K4CEL2M

# 3. Present it — the field is
#    called "otc", and the wrong
#    name fails without saying why
curl -X PUT \
  https://auth.lab.local:9091/api/user/session/elevation \
  -d '{"otc":"3K4CEL2M"}' \
  -b cookies-ada.txt -c cookies-ada.txt
# {"status":"OK"}
```

The session now reports
`"elevated": true` with a
countdown — 599 seconds in the
lab. Ten minutes of being treated
as freshly proven, long enough to
do the sensitive thing, short
enough to mean something. The
letter also carries a revocation
link: if the code was not yours,
one click kills it. Remember that
shape; it is the notifier earning
its place a chapter before the
password reset uses it again.

## Registering the device

Registration is three calls, and
the middle one hands over the
secret:

```bash
# 1. What shapes are on offer?
curl https://auth.lab.local:9091/api/secondfactor/totp/register \
  -b cookies-ada.txt
# {"algorithm":"SHA1","algorithms":["SHA1"],
#  "length":6,"lengths":[6],
#  "period":30,"periods":[30]}

# 2. Choose, and receive the secret
curl -X PUT \
  https://auth.lab.local:9091/api/secondfactor/totp/register \
  -d '{"algorithm":"SHA1","period":30,"length":6}' \
  -b cookies-ada.txt -c cookies-ada.txt
# {"base32_secret":"CSXV...",
#  "otpauth_url":"otpauth://totp/lab.local:ada?..."}

# 3. Prove the device works
curl -X POST \
  https://auth.lab.local:9091/api/secondfactor/totp/register \
  -d '{"token":"404490"}' \
  -b cookies-ada.txt
# {"status":"OK"}
```

In a browser, step 2 shows the
`otpauth_url` as a QR code and the
authenticator app drinks it in.
The lab has no phone either, so it
computed the code itself:
`authelia-lab/totp.py` is twelve
lines of the published algorithm
(RFC 6238) — base32 secret, the
current thirty-second window, an
HMAC, six digits. Two honest
details from the run: Authelia
issues the secret unpadded, and
Python's decoder wants the padding
put back; and step 3 is not a
formality — Authelia keeps the
device only after a code from it
has checked out, so a mistyped
secret fails here, at registration,
instead of at the vault door at
midnight.

**Check:** the device exists when
the settings endpoint says so:

```bash
curl https://auth.lab.local:9091/api/secondfactor/totp \
  -b cookies-ada.txt
# {"created_at":"2026-10-29T19:09:27Z",
#  "last_used_at":"...",
#  "issuer":"lab.local","algorithm":"SHA1",
#  "digits":6,"period":30}
```

Use that endpoint, not
`/api/user/info`: in the lab the
info call kept reporting
`has_totp: false` long after the
device was registered *and used*,
while the settings endpoint and
the database agreed with reality
(t32, and chapter 13).

## The vault, at last

Fresh sign-in, and the complete
sequence the guide has been
building towards (t19):

```bash
# password alone
./authz.sh auth-request https://vault.lab.local:8445/ cookies.txt
# HTTP 401 + Location: the portal,
# asking for the rest of the proof

# the code
curl -X POST \
  https://auth.lab.local:9091/api/secondfactor/totp \
  -d '{"token":"583352"}' -b cookies.txt
# {"status":"OK","data":{"redirect":"..."}}

# now
./authz.sh auth-request https://vault.lab.local:8445/ cookies.txt
# HTTP 200 OK
# Remote-User: ada
```

Through nginx the same story is
t21 case 6 (in) against case 7
(password only: redirected to the
portal). Grace's story at the
vault is the other half of the
design: she has no device, so no
amount of password knowledge gets
her past a `two_factor` rule — the
portal would walk her to a second
step she cannot complete. That is
the point of the policy: it is
not "a password, but more
carefully" — it is a second kind
of evidence, from a second place,
and both halves were run here.
