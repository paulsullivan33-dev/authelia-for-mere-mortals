# Glossary

The terms this guide uses, in the
order a reader tends to meet them.
Short definitions; the chapters
carry the full stories.

**Portal** — The sign-in pages
Authelia serves itself: login,
second-factor prompts, settings,
consent. One portal guards every
service behind it.

**Reverse proxy** — The program
(nginx, Caddy, Traefik) that
receives visits for your services
and fetches the right page. With
Authelia, it also asks permission
before fetching.

**Auth request / forward auth** —
The two dialects of the proxy's
question to Authelia. Auth-request
(nginx) is answered `401` plus a
`Location`; forward-auth (Caddy,
Traefik) is answered with the
redirect itself. Same question,
different manners.

**Session** — The record, kept by
Authelia after a sign-in, that a
visitor is known. Held in the
server's memory; the browser
carries only its ID, in a cookie.

**Cookie domain** — The parent
domain the session cookie is
scoped to. Every guarded service
must live under it, or the
browser will never present the
cookie there.

**User backend** — Where accounts
live: a YAML file at household
scale (the file backend), or an
LDAP directory at organisational
scale.

**Hash** — The one-way fingerprint
of a password, made here with
Argon2. Backends store hashes;
the password itself is never
stored anywhere.

**Access rule** — One line of the
rule book: conditions (domain,
path, subject, and friends) plus a
policy. Rules are read in order;
the first full match decides.

**Policy** — A rule's answer:
`bypass` (no login), `one_factor`
(password), `two_factor` (password
plus a second factor), `deny`
(nobody). The default policy
covers whatever no rule mentions.

**Subject** — The "who" of a
rule: `user:<name>` or
`group:<name>`. A rule with a
subject concerns only those
people — and steps aside for
everyone else.

**First factor / second factor** —
Something you know (the password),
then something you have (a code,
a key). Two-factor means both,
in that order.

**TOTP** — Time-based one-time
password: six digits derived from
a shared secret and the current
half-minute, by an authenticator
app and the server independently.

**Elevation** — The extra proof —
a one-time code sent through the
notifier — that a signed-in
session must show before it may
do sensitive things, such as
registering a device.

**Notifier** — Authelia's way of
reaching users off-portal:
password-reset letters, elevation
codes, security warnings. SMTP in
production; a file in this lab.

**Regulation** — The counting of
failed sign-ins and the temporary
ban that follows too many: the
portal's answer to guessing.

**WebAuthn / passkey** — The
browser-and-device ceremony in
which a security key or platform
authenticator proves itself with
cryptography rather than a shared
secret. Described, not run, in
this guide (see criteria.md).

**OpenID Connect (OIDC)** — The
protocol by which an application
outsources its sign-in to an
identity provider — here,
Authelia — and receives tokens
saying who arrived.

**Client** — An application
registered with the provider: an
ID, a hashed secret, and an exact
list of redirect URIs it may send
users back to.

**Scope** — A named bundle of
things a client asks for:
`openid`, `profile`, `email`,
`groups`, `offline_access` (the
one that earns a refresh token).

**Consent** — The user's explicit
yes to a client's scopes, asked
on the provider's own page —
unless the client's consent mode
has arranged otherwise.

**Authorization code** — The
one-trip ticket the browser
carries back to the client, which
the client exchanges — secretly,
server to server — for tokens.

**ID token / userinfo** — The
signed statement of the sign-in,
and the endpoint that answers
questions about the person. In
this guide's lab, the name, email
and groups waited at userinfo;
the token carried the sign-in's
facts and an opaque `sub`.

**Header (Remote-User and
friends)** — The identity the
proxy hands a protected service
after Authelia's yes. Services
trust it because the proxy is the
only road in — which is why that
road must be the only one.
