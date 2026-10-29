# Limits

Everything in this chapter was
either observed in the lab or
follows directly from how the
parts in chapter 2 are built. A
front door deserves its limits
stated before it is hung, not
after the first odd evening.

**Sessions live in the process.**
The cookie is a name; the record
it names sits in Authelia's
memory, and the database — which
holds devices, attempts and
tokens — has no table for
sessions. The lab restarted the
server and a working
password-plus-TOTP session came
back anonymous: the cookie was
still in the jar, and it named
nothing (t34). In practice: every
restart, upgrade and crash signs
out everyone, everywhere, at
once. Usually a shrug — sign in
again — but plan upgrades for
quiet hours, and do not go
hunting for a "session bug" when
the whole house was asked to log
in on the same morning. (Authelia
can be run in redundant
arrangements with shared session
state, using other storage
engines; that is a documented
feature this guide did not run,
and a household rarely needs it.)

**The file backend is a household
tool.** A YAML file of users is
edited by hand, hashed with a
command, and rewritten in place by
the server itself when a password
resets (t23). It has no
self-registration — there is no
"create account" page to offer
the public — and no admin screen;
adding a person is editing a
file. That is exactly right up to
the size where editing the file
*is* somebody's job, at which
point the LDAP backend the
documentation describes, or one
of chapter 11's larger portals,
is the honest next step.

**Authelia guards doors, not
rooms.** It can tell a service
"this is ada, of the admins
group"; what ada may do *inside*
remains the service's own
decision, made with its own
permissions if it has any. A
service that treats "signed in"
as "may do anything" gives every
visitor the run of it — the
portal's answer was only ever
about the door. Groups help where
a rule can see them (chapter 6's
sealed corner works because the
*proxy* refuses, before the
service is asked), but fine
permissions inside an app are
beyond any portal's reach.

**The portal needs a browser.**
Its page is a JavaScript
application; the lab's bare
client received a 2.6-kilobyte
shell with an empty title (t06).
Text browsers, some embedded
clients and very old devices will
see little or nothing. Anything
that must be reached by such a
client needs a different door —
`bypass` for a harmless corner, or
the VPN for the machine itself.

**One door is one point of
failure.** If Authelia stops,
the proxy has nobody to ask, and
protected services answer with
errors rather than pages. That is
the safe direction to fail — the
alternative, serving pages when
the checker is down, would make
killing the checker the master
key — but it means the portal
needs the boring care of any
load-bearing thing: it starts on
boot, its health endpoint is
worth a monitor, and its three
files are backed up (chapter 10).

**A second factor is only as
strong as its clock and its
keeping.** TOTP codes are derived
from the time; a server whose
clock has drifted will refuse
correct codes from correct
phones, which is why Authelia
checks the time against a network
source at startup and why that
check should not be switched off
outside sandboxes like this one.
And TOTP proves possession of a
secret, not of a person: a secret
photographed at registration is
a second factor in two places at
once. WebAuthn keys and passkeys
resist that copying by design —
which is the strongest argument
for them, and this guide could
only describe them (criteria.md
keeps the ledger).

**Small honest print from the
lab.** Two observations rather
than designs: the user-info
endpoint kept reporting
`has_totp: false` for a user whose
device was registered and in use
(t32) — trust the settings
endpoint when they disagree; and
Authelia's answers, while never
leaking *which* part of a login
failed, do tell a signed-in user
exactly which rule refused them
in the server log's phrasing —
the log is an operator's tool and
should be kept as one, not
published.
