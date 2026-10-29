# The Moving Parts

By the end of this chapter you can
name each part of the system and
say which question it answers. When
something later goes wrong, the
name of the part is most of the
repair.

**The portal.** The web page
Authelia itself serves — in the lab
at `https://auth.lab.local:9091`.
Signing in, entering a second
factor, the settings pages where
users register devices, the consent
screen an app may ask for: all of
it lives here. The portal is a
JavaScript application; the file
the server hands a bare HTTP client
is a small shell the browser fills
in (the lab fetched it in t06 and
found an empty `<title>` waiting
for the script to set it).

**The reverse proxy.** nginx in the
lab; Caddy or Traefik would do the
same job. It owns the public names
and ports, terminates HTTPS, and —
the new part — asks Authelia about
every request before serving it.
Authelia never touches your pages;
the proxy never decides who anyone
is. **Check:** that separation is
the design. If a chapter ever seems
to have one doing the other's job,
it is describing a mistake.

**The auth endpoint.** The address
the proxy asks. Authelia offers the
same question in several dialects,
one per proxy family, all under
`/api/authz/`: **auth-request** for
nginx (answered `401` plus a
`Location` header when the visitor
must sign in), **forward-auth** for
Caddy and Traefik (answered `302`
to the portal instead), and others
for other proxies. The question
itself is a handful of headers —
who is asking, for which address,
which page, which method — and the
answer is a status code plus, on
success, identity headers:
`Remote-User`, `Remote-Groups`,
`Remote-Name`, `Remote-Email`
(t08 and t09 show both dialects).

**The user backend.** Where
accounts live. The lab uses the
**file** backend: one YAML file of
users, groups, email addresses and
password *hashes* — never the
passwords themselves (t02 made the
hashes with Authelia's own command).
The grown-up alternative, named
here and not run, is **LDAP**, for
organisations that already keep
their people in a directory.

**The rule book.** The
`access_control` section of the
configuration: a list of rules,
each matching some addresses,
pages, people or groups and
naming a **policy** — `bypass`,
`one_factor`, `two_factor` or
`deny` — plus a default for
anything no rule mentions. Chapter
7 is this part, thoroughly,
because it is the part you will
actually write.

**The session.** After a successful
sign-in, Authelia sets a cookie on
your domain — in the lab
`authelia_session`, scoped to
`lab.local` so every service under
it presents the same cookie. The
cookie's whole content is a short
random session ID; the record it
points to lives in the Authelia
process itself. Chapter 4 shows
the cookie, and chapter 12 draws
the consequence: restart Authelia
and every session ends (proved in
t34, whether you wanted it or not).

**Storage.** A database — SQLite in
the lab, one file — holding what
must survive restarts: TOTP device
secrets (encrypted with a key from
your configuration), the log of
authentication attempts, consent
records, reset tokens. Note what
is *not* in it: the sessions above.
First startup builds the schema by
itself; t05 watched it migrate
from empty to version 29.

**The notifier.** How Authelia
speaks to users when nobody is
looking at the portal: password
reset letters, and the one-time
codes that **elevation** — the
proof of identity Authelia demands
before letting a signed-in user
touch anything sensitive — travels
by. Real deployments use SMTP. The
lab uses the **filesystem**
notifier, which appends each
message to a text file: less
glamorous, and the whole letter is
there to be read (t14, t22).

**The second factors.** Things a
user registers on their own
account: **TOTP** codes from an
authenticator app (chapter 7),
**WebAuthn** security keys and
**passkeys** (documented-only in
this guide — their ceremony needs
a browser and a device), and push
approval through Duo (named,
not run).

**The identity provider.** The
other direction of travel: apps
that bring their *own* login button
can send their users to Authelia
as an **OpenID Connect** provider,
the way big sites offer "sign in
with…" Chapter 8 runs that whole
dance for one pretend app.

Keep the cast small in your head:
the proxy asks, the portal proves,
the rules decide, the session
remembers, the storage keeps, the
notifier tells. Everything in the
remaining chapters is one of those
six sentences with the details
filled in.
