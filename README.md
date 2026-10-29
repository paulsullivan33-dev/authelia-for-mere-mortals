# Authelia for Mere Mortals

Every self-hosted service you run —
your photos, your files, your media,
your dashboards — comes with its own
login page, its own password, and its
own idea of security. Some have no
login at all. **Authelia** is the one
door you put in front of all of them:
a single sign-in page of your own,
with your users, your rules, and a
second factor where you want one. A
visitor proves who they are to
Authelia once; your services let them
through because Authelia said so.

Authelia does not replace your
services, and it does not serve a
single page of their content. It sits
beside the **reverse proxy** — the
program that already receives every
request — and answers one question
for it, on every request: *is this
visitor allowed in, and if so, who
are they?* The proxy does the rest.
Chapter 2 names every part of that
arrangement; by chapter 5 a real
proxy is asking the question and a
real service is behind the door.

The lab behind this guide ran the
real thing: the official **Authelia
4.39.28** release binary, checked
against the project's published
checksums, with **nginx 1.24** as
the proxy, on one small Linux
machine. Everything happened on
loopback, under invented names —
`auth.lab.local` for the portal and
four pretend services (`public`,
`app`, `vault`, `blocked`) — with
two invented users: **ada**, in the
admins group, and **grace**, in the
readers group. Both passwords are
throwaway lab passwords, printed in
the lab notes, guarding nothing.

Against that rig the lab fetched
the portal, signed in with a wrong
password and a right one, and read
Authelia's decision for every
combination of site and visitor:
let in, sent to log in, forbidden,
or "password is not enough here".
It registered a TOTP device — which
first demanded a detour through an
*elevation* code sent to the user's
mailbox — and used a twelve-line
Python script as the authenticator
app. It ran a password reset through
the notification file standing in
for email, watched repeated failures
earn a temporary ban, restarted the
server and found every session gone,
and completed a full OpenID Connect
sign-in for a pretend app, consent
screen and all.

What the lab could not do, it did
not fake. There was no browser in
the sandbox, so every "click" in
this guide is the exact API call the
browser makes, shown as it was made;
the pages themselves are described,
not pictured. There was no mailbox,
so notifications went to a file —
which turns out to be the better
teacher, because you can read the
whole message. WebAuthn and passkeys
need a browser and an authenticator
to perform their ceremony, so they
are taught from the documentation
and labelled as such wherever they
appear. `criteria.md` keeps the full
ledger of what was run and what was
only read.

One boundary, stated early because
everything here depends on it: this
machinery is for services that are
*yours*, with accounts for people
you mean to let in. Pointed at
anyone else's door, the same
knowledge is just breaking in.

## What this guide covers

- [**What Authelia is**](what-authelia-is.md) —
  the mental model: one door, one
  login, rules per service, and what
  "single sign-on" actually buys you
- [**The moving parts**](the-moving-parts.md) —
  the portal, the proxy, the user
  list, the rule book, the session,
  the storage, and the notifier —
  and which part answers what
- [**Installing Authelia**](installing-authelia.md) —
  the release download, the checksum,
  the configuration file, hashed
  passwords, and the validation
  check that catches mistakes early
- [**Your first login**](your-first-login.md) —
  the portal answering, a wrong
  password refused the polite way,
  a right one accepted, and what
  the session cookie really holds
- [**Protecting a service end to end**](protecting-a-service.md) —
  nginx asking Authelia about every
  request, the redirect to the
  portal, and the identity headers
  the service receives afterwards
- [**Access rules and policies**](access-rules-and-policies.md) —
  bypass, one-factor, two-factor
  and deny; first match wins; and
  the corner that stayed open until
  it was sealed on purpose
- [**Two-factor with TOTP**](two-factor-with-totp.md) —
  elevation codes, registering a
  device in three calls, and a
  vault that a password alone
  cannot open
- [**Authelia as an identity provider**](authelia-as-an-identity-provider.md) —
  OpenID Connect in plain words:
  discovery, consent, the code, the
  tokens, and where the claims live
- [**Notifications and password reset**](notifications-and-password-reset.md) —
  the notifier, the reset letter,
  the rewritten user file, and the
  ban that repeated failures earn
- [**Recipes**](recipes.md) — protect
  a new service, open one public
  corner, demand more from admins,
  read the refusal log, and back up
  the three files that matter
- [**The neighbours**](the-neighbours.md) —
  apps with their own logins, other
  portals, the VPN that solves a
  different problem, and the hosted
  cousin: what each does that
  Authelia doesn't, and vice versa
- [**Limits**](limits.md) — sessions
  that live in memory, a user file
  that is not a crowd, coarse
  permissions, and a portal that
  needs JavaScript
- [**Troubleshooting**](troubleshooting.md) —
  the 400 with one missing header,
  the rule that fell through, the
  page that served itself to
  strangers, the device the portal
  denied owning, and the ban you
  can only see in the log
- [**Glossary**](glossary.md) — the
  terms, collected in one place

## What it doesn't cover

Running Authelia for a company, with
an LDAP or Active Directory behind
it and a helpdesk in front — the
moving parts are the same, but the
lab's user file is a household tool
and the guide says so. The Docker
and Kubernetes installs are pointed
at, not taught; the lab ran the
bare binary, which is also how you
learn what the containers are
wrapping. And there is no chapter
on attacking a portal: the failure
modes here are the operator's own
mistakes, found by operating.

## How to use this guide

Read chapters 1 and 2 before
installing anything — knowing which
part holds what turns later
confusion into a named problem.
Chapters 3 and 4 give you a running
portal and a first login in one
sitting. Chapter 5 is the heart of
the guide: everything after it is
a variation on the question the
proxy asks there. The lab's
transcripts live in
`authelia-lab/transcripts/`; its
configuration, user file, proxy
files and helper scripts are in
`authelia-lab/` itself.

---

## Part of the series

This guide is one of the [For Mere Mortals](https://paulsullivan33-dev.github.io/mere-mortals/) guides: plain-language guides to the tools programmers and makers use.

Related guides:

- [nginx for Mere Mortals](https://paulsullivan33-dev.github.io/nginx-for-mere-mortals/)
- [Caddy for Mere Mortals](https://paulsullivan33-dev.github.io/caddy-for-mere-mortals/)
- [Traefik for Mere Mortals](https://paulsullivan33-dev.github.io/traefik-for-mere-mortals/)
- [mkcert for Mere Mortals](https://paulsullivan33-dev.github.io/mkcert-for-mere-mortals/)
- [Cybersecurity for Mere Mortals](https://paulsullivan33-dev.github.io/cybersecurity-for-mere-mortals/)

## License

The writing in this guide is licensed under [CC BY 4.0](https://github.com/paulsullivan33-dev/authelia-for-mere-mortals/blob/main/LICENSE). Code examples and lab scripts are licensed under the [MIT License](https://github.com/paulsullivan33-dev/authelia-for-mere-mortals/blob/main/LICENSE-CODE).
