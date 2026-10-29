# The Neighbours

By the end of this chapter you can
say what Authelia is *next to* —
which of your other tools already
do part of its job, which do a
different job that looks similar
from a distance, and when the
better answer is not Authelia at
all. Links point at guides in this
series that exist; the neighbours
without one are described from
their own documentation and were
not run for this guide.

## Apps with their own front doors

Many services keep their own
accounts and do it well:
[Nextcloud](https://paulsullivan33-dev.github.io/nextcloud-for-mere-mortals/)
has users, groups and its own
two-factor; a
[Jellyfin](https://paulsullivan33-dev.github.io/jellyfin-for-mere-mortals/)
server knows its viewers. For
those, Authelia is not a
replacement — it is one of two
things. Put it *in front* anyway,
and the service's own login becomes
the second door behind the first:
visitors sign in twice, which is
wasteful but simple, and the
outer door still guards the admin
pages and the forgotten corners.
Or register the app as an OIDC
client (chapter 8) and let
Authelia *be* its login: one
account everywhere, the app's own
user list retired. The middle
path — Authelia in front, headers
trusted, the app's login left
enabled for nobody — is the one
to avoid: two systems both half
in charge is how doors get left
open by accident.

## Other portals

**Authentik** and **Keycloak**
solve the same problem from the
organisation end: directories,
enrolment flows, social logins,
an admin console instead of a
YAML file, and a correspondingly
larger machine to feed. If you
have hundreds of users, or users
who must register themselves,
their weight is the point. The
household case runs the other
way: Authelia's whole rule book
fits on one screen, its state is
three files, and a person can
hold all of it in their head —
which, at 11 p.m. with the family
locked out, is a feature no
console matches. (Characterised
from their documentation; neither
was run for this guide.)

## The proxy's own locks

Every reverse proxy in this series
— [nginx](https://paulsullivan33-dev.github.io/nginx-for-mere-mortals/),
[Caddy](https://paulsullivan33-dev.github.io/caddy-for-mere-mortals/),
[Traefik](https://paulsullivan33-dev.github.io/traefik-for-mere-mortals/) —
can ask for a password itself:
`basic auth`, a name and a hashed
password checked by the proxy, no
portal involved. For one service
and one trusted user it is honest
work, set up in two lines. What it
cannot do is everything past that:
no single sign-on (each service
asks again), no second factor, no
groups with different doors, no
"this corner is public", no
sessions that remember anyone —
and the credentials travel with
every request. Authelia is what
you graduate to when the second
service arrives, or the first
visitor who is not you.

## The VPN, which is a different answer

[Tailscale](https://paulsullivan33-dev.github.io/tailscale-for-mere-mortals/)
and [WireGuard](https://paulsullivan33-dev.github.io/wireguard-for-mere-mortals/)
answer "who may reach this
machine at all?" — they put a
device *on* your network. Authelia
answers "who may open this page?"
The VPN is the stronger wall and
the blunter one: a grandparent's
tablet on your tailnet can reach
everything on it, the files and
the printer and the admin pages
alike, and needs software
installed and kept. Authelia
reaches people through nothing
but a browser, one named service
at a time, with rules per service
and per person — and guards
nothing that is not a web page.
Many households end up wanting
both: the VPN for the machines,
the portal for the services
shared with people who will never
install either.

## The hosted cousin

Cloudflare Access — reached
through the tunnel in the
[Cloudflare Tunnel guide](https://paulsullivan33-dev.github.io/cloudflared-for-mere-mortals/)
— is this chapter's idea as a
service: Cloudflare's edge asks
who you are before your traffic
is forwarded home, and sign-in
can lean on an identity provider
you already have. It asks nothing
of your hardware and starts free;
it also means the door to your
house is operated by a company,
under its terms, and stops being
yours to inspect. The choice is
the usual one in this series —
rented convenience against owned
machinery — and Authelia is
simply the owned end of it,
complete with the electric bill
of chapters 12 and 13: when it
breaks, the person who fixes it
is you.

## And the tools that only look adjacent

Password managers —
[Vaultwarden](https://paulsullivan33-dev.github.io/vaultwarden-for-mere-mortals/),
[KeePassXC](https://paulsullivan33-dev.github.io/keepassxc-for-mere-mortals/),
[pass](https://paulsullivan33-dev.github.io/pass-for-mere-mortals/) —
keep *your* passwords for *other
people's* doors; Authelia checks
passwords at *your* door. They
meet in one useful place: the
manager is where your users'
strong, unique portal passwords
should live, and where yours
does. [Fail2Ban](https://paulsullivan33-dev.github.io/fail2ban-for-mere-mortals/)
watches logs and bans addresses
that misbehave — cruder than
regulation (chapter 9), which
counts the actual account, but it
works in front of services that
have no Authelia at all.

**Check:** name, for each service
you run, which neighbour guards
it today — its own login, the
proxy's lock, the VPN, Authelia,
or honestly nothing. The list you
just made is the honest map of
your house; Authelia's job is to
shrink the last entry.
