# Recipes

Each recipe is assembled from parts
the earlier chapters ran for real;
where a recipe recombines them in a
way the lab did not run end to end,
it says so.

## Protect a service you just installed

The whole pattern, once your portal
exists. On the proxy, give the new
service the shared question block
and a location that asks it
(chapter 5's two snippets, with the
service's own name and port). In
the rule book, one line above the
default:

```yaml
    - domain: 'photos.lab.local'
      policy: 'one_factor'
```

Then the chapter 5 check, all
three ways: signed out, signed in,
signed in as someone refused. And
the half everyone forgets: make
sure the service's own port is not
answering the world directly — the
door is only a door if there is no
open window beside it. On the
service's machine that means it
listens on loopback or a private
address, or the firewall refuses
its port from outside:

```bash
# from another machine, this must fail:
curl https://photos.lab.local:8443/
# while the same address through
# the proxy's port answers with a
# redirect to the portal.
```

## One public corner on a protected service

A status page, a shared gallery —
one path anyone may read, on a
service that otherwise asks for a
password. Rules are ordered, so the
corner goes *above* the service's
rule:

```yaml
    - domain: 'app.lab.local'
      resources: ['^/status($|/.*)']
      policy: 'bypass'
    - domain: 'app.lab.local'
      policy: 'one_factor'
```

This is the fall-through of
chapter 6 spent on purpose: the
corner matches its rule first, and
everything else continues down to
the door. Anything placed here is
public in the full sense — bypass
means the request is not even
asked for a session — so choose
corners that contain nothing you
would mind a stranger reading at
3 a.m.

## Ask more of the admins

Stricter proof for one group, on
an ordinary service: a subject
rule above the general one, this
time with the stronger policy
instead of a different door.

```yaml
    - domain: 'app.lab.local'
      subject: 'group:admins'
      policy: 'two_factor'
    - domain: 'app.lab.local'
      policy: 'one_factor'
```

The lab verified subject rules
with groups and both policies
separately (t12, t19); this exact
combination is a recombination,
and its own check is the chapter 6
table — write the expected answers
for an admin and a reader first,
then ask. Note what it does *not*
do: it does not seal the service
against anyone (the general rule
still admits readers) — it only
raises the price of an admin's
session, which is usually the
actual wish.

## Read the refusals

When someone says "I couldn't get
in", the evidence is in two
places. The log narrates:

```bash
grep 'is not authorized\|Unsuccessful\|banned' authelia.log
# Access to https://vault.lab.local:8445/ ...
#   is not authorized to user 'ada' ...
# Unsuccessful 1FA authentication attempt by
#   user 'grace' and they are banned until ...
```

And the storage keeps the ledger —
the `authentication_logs` table of
the SQLite database holds each
attempt, its user, its address and
its verdict, for questions the log
has rotated past. Between the two,
every refusal in this guide's lab
could be explained from the record
alone: wrong group, missing
factor, sealed address, ban. Make
"read the refusal" a habit before
"loosen the rule" — most refusals
are the rules working, described
in the log's own words.

## Back up the three files that matter

Everything Authelia knows lives in
three places: `configuration.yml`
(the rules, the clients, and every
secret), `users.yml` (the people
and their hashes), and the SQLite
database (devices, logs, tokens).
Back up those three together, and
a rebuilt machine comes back with
its users, their second factors
and your rules intact:

```bash
cp configuration.yml users.yml db.sqlite3 \
   /your/backup/authelia-$(date +%F)/
```

Two warnings that are really one:
that folder is now the keys to
every door — the configuration's
secrets and the storage key are in
it — so the backup deserves the
same protection as the portal
itself; and a backup missing the
storage encryption key is a
museum, not a restore, because
the TOTP secrets inside the
database will never open again.
(Sessions are not in the backup
and cannot be: chapter 12 explains
why nobody's login survives even
a restart, let alone a rebuild.)
