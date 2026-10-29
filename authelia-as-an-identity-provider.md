# Authelia as an Identity Provider

By the end of this chapter a
pretend application has sent its
visitor to Authelia to sign in,
received her back with an
authorization code, traded that
code — server to server, with its
own secret — for tokens, and read
who she is from Authelia's
userinfo endpoint. It is the
"sign in with…" button, with
Authelia as the name after "with".

Chapter 5's arrangement works when
a service is happy to be *told*
who is visiting. Some applications
instead speak **OpenID Connect**
(OIDC) natively: they want to run
the sign-in themselves, against an
**identity provider** they trust.
Authelia can be that provider.
The two shapes coexist — the lab
ran both against the same users —
and an app chooses by what it
knows how to speak, not by which
is "better".

## The vocabulary, in one pass

An OIDC **client** is an
application registered with the
provider: it has an ID, a secret
of its own, and a short list of
addresses (**redirect URIs**) the
provider may send users back to.
A **scope** is a named bundle of
things the app asks to know —
`openid` (the sign-in itself),
`profile`, `email`, `groups`.
**Consent** is the user agreeing
to that list. The **authorization
code** is a one-trip ticket: the
provider sends the *browser* back
with it, and the app exchanges it
for **tokens** directly, where no
browser can see them. The
**id token** is a signed statement
of who signed in; the **userinfo**
endpoint answers "tell me about
the person" to whoever holds the
access token.

## Registering the client

Clients live in the same
configuration file, and their
secrets are hashed exactly like
user passwords (t02 made this one
too):

```yaml
identity_providers:
  oidc:
    hmac_secret: '<another random string>'
    jwks:
      - key_id: 'labkey'
        algorithm: 'RS256'
        use: 'sig'
        key: |
          <an RSA private key, made by:
           authelia crypto pair rsa generate>
    clients:
      - client_id: 'lab-app'
        client_name: 'Lab Photo App'
        client_secret: '$argon2id$v=19$...'
        public: false
        authorization_policy: 'one_factor'
        grant_types: ['authorization_code', 'refresh_token']
        response_types: ['code']
        redirect_uris:
          - 'https://app.lab.local:8443/callback'
        scopes: ['openid', 'offline_access',
                 'profile', 'email', 'groups']
        token_endpoint_auth_method: 'client_secret_basic'
```

The signing key is the provider's
own — tokens are signed with it
and apps verify them against the
public half, published at the
`jwks_uri` below. The redirect URI
list is a lock, not a suggestion:
Authelia will send users *only*
to addresses on it, exactly as
written.

**Check:** any OIDC provider
introduces itself at a fixed
address. Before any client exists
in your plans, read yours (t25):

```bash
curl https://auth.lab.local:9091/.well-known/openid-configuration
# {"issuer":"https://auth.lab.local:9091",
#  "authorization_endpoint":".../api/oidc/authorization",
#  "token_endpoint":".../api/oidc/token",
#  "userinfo_endpoint":".../api/oidc/userinfo",
#  "jwks_uri":".../jwks.json", ...}
```

## The dance

Ada is already signed in at the
portal (the app checks nothing
about that; it just sends her
browser over):

```text
GET /api/oidc/authorization?client_id=lab-app
    &redirect_uri=https://app.lab.local:8443/callback
    &response_type=code
    &scope=openid profile email groups offline_access
    &state=labstate123
-> 303 to /consent/openid/decision?flow_id=...
```

The consent screen names the app,
the scopes it wants, and waits.
The lab's first attempt to answer
it taught a precise lesson: the
decision field is named `consent`,
and a POST that called it anything
else was dutifully recorded — as a
*rejection*, which the app then
reported as `access_denied` (t28).
Answered properly:

```bash
curl -X POST \
  https://auth.lab.local:9091/api/oidc/consent \
  -d '{"flow_id":"<the flow id>",
       "client_id":"lab-app",
       "consent":true}' -b cookies-ada.txt
# {"status":"OK"} + a redirect back
# to the authorization endpoint
```

Follow it, and the provider
finally sends the browser to the
app (t29):

```text
-> 303
Location: https://app.lab.local:8443/callback
  ?code=<the code>&state=labstate123&...
```

Consent does not have to be a
conversation every time: a client
may be configured with
`consent_mode` set to remember the
answer for a while (`auto`, with
`pre_configured_consent_duration`)
or to have it pre-arranged. The
lab's client ran in the default
posture — the server's log called
it `explicit`, a question asked
every time — and the alternatives
are described from the
documentation, not run.

## The exchange, and what the tokens say

The code alone is worthless
without the client's secret, and
the exchange happens offstage
(t30):

```bash
curl -X POST \
  https://auth.lab.local:9091/api/oidc/token \
  -u lab-app:<the client's secret> \
  -d grant_type=authorization_code \
  -d code=<the code> \
  -d redirect_uri=https://app.lab.local:8443/callback
# {"token_type":"bearer","expires_in":3599,
#  "scope":"openid profile email groups offline_access",
#  access_token, id_token and a
#  refresh_token all present}
```

Decode the id token's payload and
a fine print lesson falls out: in
this client's configuration it
carries the issuer, the audience,
the sign-in methods (`pwd`, and
`kba` — the knowledge factor of
the second step) and a `sub` that
is an **opaque identifier**, not
"ada":

```json
{"iss":"https://auth.lab.local:9091",
 "sub":"3f35844f-08dc-4b1e-9891-c22daee30bbc",
 "aud":["lab-app"], "amr":["pwd","kba"],
 "name":null, "email":null, "groups":null}
```

The name, email and groups the
app asked for are not in the
token — they are at userinfo,
which is what it is for:

```bash
curl https://auth.lab.local:9091/api/oidc/userinfo \
  -H "Authorization: Bearer <access token>"
# {"sub":"3f35844f-...same...",
#  "name":"Ada Lab",
#  "email":"ada@lab.local",
#  "groups":["admins","readers"]}
```

Same `sub`, so the app can stitch
the two together. Whether claims
ride in the token or wait at
userinfo is configuration and
convention, and it differs between
providers; what the lab can say
is what *this* one did, above.
The refresh token in the response
is why the client asked for
`offline_access` back in chapter
3's validation warning: it lets
the app renew access later without
sending ada through sign-in again
— a convenience to grant on
purpose, never by accident.
