# Troubleshooting

Every entry below happened in this
guide's lab, or in the checking of
its answers. Each names the
symptom, the cause found, and the
check that separates it from its
lookalikes.

## The proxy gets a 400 from Authelia

**Symptom.** Through Caddy or
Traefik (the forward-auth
dialect), every request fails;
calling the endpoint by hand
returns `400` with a small JSON
complaint.

**Cause.** The forward-auth
dialect insists on knowing the
request's method from a header of
its own. Without it, Authelia
refuses the *question*, not the
visitor — the server log says so
in plain words: "header
'X-Forwarded-Method' is empty"
(t09).

**Check.** Send the call by hand
with the headers your proxy is
meant to add (`authelia-lab/authz.sh`
does), one at a time. When the
400 becomes a 302 or a 401-with-
Location, the last header you
added is the one the proxy is not
sending; fix its template, not
Authelia's.

## A rule "does nothing"

**Symptom.** A rule exists for a
page and a group; visitors outside
the group sail through anyway.

**Cause, first suspect.** Fall-
through (chapter 6): a subject
rule only speaks for its own
people. Grace matched nothing in
the admins rule and was judged by
the general rule below it. Seal
the corner with a `deny` rule
under the subject rule (t12).

**Cause, second suspect.** The
proxy is not sending the path you
think it is. The lab's own checker
initially sent `X-Forwarded-Uri: /`
for every address and "proved"
rules that were never consulted
(t11). Before suspecting the rule
book, make the checker — or the
service's own echo — show the
exact address Authelia received.

**Check.** The auth endpoint by
hand, as the user in question,
asking for the exact path. Four
lines of output settle which of
the two suspects you have.

## The page serves itself to strangers

**Symptom.** The protected page
answers anonymous requests with
its real content — no redirect,
no refusal — although the
configuration looks right.

**Cause.** Something in the proxy
answered before the access phase
could ask. In the lab, an nginx
`return 200` inside the same
location answered during the
rewrite phase; `auth_request`
never ran (chapter 5's trap).
Any shortcut that completes the
request early — a cached page, a
`try_files` that finds a file, a
second location that also matches
— has the same shape.

**Check.** Ask anonymously and
look for the *kind* of answer: a
working door answers 302 (or a
login page), never the content.
Then remove shortcuts from the
location until the stranger is
redirected; add them back one at
a time if you must have them.

## Everyone was signed out at once

**Symptom.** The whole household
needs to log in again on the same
morning, passwords grumbled about.

**Cause.** Almost always: Authelia
restarted. Sessions live in its
memory (chapter 12, t34); an
upgrade, a crash or a reboot
clears every one. This is the
system working as built.

**Check.** The process's start
time against the complaints'
start time. If they agree, no
further mystery — and if restarts
keep surprising people, the fix
is scheduling, not configuration.

## The elevation code "didn't match"

**Symptom.** Registering a device,
the one-time code from the letter
is refused: "the code didn't match
any recorded code challenges" —
with the right code, freshly
issued.

**Cause.** The confirmation call
expects the code in a field named
`otc`. The lab sent it under a
longer, plausible name and the
server quite correctly found no
code under it (t15).

**Check.** When an API answers
"no record of that", suspect the
envelope before the contents —
field names, then values. The
project's API documentation names
every field; the lab's working
calls are in t16.

## The user "refused" consent they meant to give

**Symptom.** An OIDC app reports
`access_denied`, "the user denied
your request", for a user who
clicked accept.

**Cause.** The same envelope
trouble, with worse manners: the
consent decision must arrive in a
field named `consent`. The lab's
POST named it `accept` — the
server recorded a decision, all
right: `false` (t28). Consent
sessions are single-use, so the
flow must start over from the
app.

**Check.** Consent questions are
answered in the provider's API
documentation's exact words. If
you are driving the API yourself,
t29 is a known-good transcript.

## The right password is refused

**Symptom.** A user swears the
password is correct — it is — and
the portal still says the generic
"Authentication failed."

**Cause.** Regulation (chapter 9):
enough failures inside the window
and the account is banned for a
few minutes, during which even
the truth is refused, in the same
generic words. The lab produced
exactly this with grace (t33).

**Check.** The server log, not
the user: "banned until …" with a
time on it. Wait it out, or
restart nothing — and if it keeps
happening, read the same log for
the failures' source address
before deciding whether you are
looking at fat fingers or a
stranger's script.

## The portal denies the device exists

**Symptom.** `/api/user/info`
reports `has_totp: false`, but the
user's codes work at the vault.

**Cause.** Observed in the lab and
unresolved there (t32): the info
endpoint's answer lagged the
reality that the settings endpoint
and the database both showed.

**Check.** Ask the device list
directly — `GET /api/secondfactor/totp`
names the device, its creation and
its last use. Believe that one.

## Requests to the portal hang from the proxy machine

**Symptom.** Browsers reach the
portal fine, but the proxy's own
calls to Authelia time out, or
arrive somewhere strange.

**Cause.** A machine-wide HTTP
proxy setting is intercepting the
internal call: the address is
being sent *out* to a proxy
instead of across the loopback.
The lab's sandbox did exactly
this to its own `*.lab.local`
names until they were exempted.

**Check.** `curl` the auth
endpoint from the proxy machine
with `--noproxy '*'` (or inspect
the `NO_PROXY` list). Internal
names — localhost, your portal's
own name — belong on the
exemption list of any machine
that both proxies and is
proxied.
