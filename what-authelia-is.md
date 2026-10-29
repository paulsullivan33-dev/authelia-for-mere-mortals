# What Authelia Is

You run a handful of services on a
machine at home: a photo library, a
file browser, a media server, maybe
a dashboard or two. Each keeps its
own list of users. Each has its own
password rules, its own idea of a
login page — and a few have no login
at all, because they were written
expecting to sit on a trusted
network that no longer exists once
you open a port or share the address
with family abroad.

**Authelia is one door in front of
all of them.** It is a program you
run on your own machine. It holds
the list of people who may come in,
it shows them a single sign-in page
— the **portal** — and it remembers
your rules for each service: this
one is open to anyone, that one
needs a password, that one needs a
password *and* a code from your
phone, and that one is closed to
everybody for now.

It works by standing next to your
**reverse proxy**, not in front of
your services. The proxy (nginx,
Caddy, Traefik and their kin) is the
program that already receives every
visit and hands it to the right
service. With Authelia in the
picture, the proxy pauses each
request and asks Authelia a
question: *this visitor, this
address, this page — allowed, or
not, and who are they?* Authelia
checks the visitor's **session** —
the proof, kept in a cookie, that
they signed in earlier — against
your rules, and answers. If the
answer is no, the visitor is sent
to the portal to sign in, or told
plainly that they may not pass. If
the answer is yes, the proxy fetches
the page and tells the service who
is asking, in headers the service
can trust because the public cannot
reach it any other way.

That arrangement is what **single
sign-on** means at household scale:
one account, one login, many doors.
Sign in once in the morning and the
photo library, the files and the
media server all know you; the
sensitive one still asks for your
phone code, because your rules said
it should.

## A first taste

The whole system, reduced to the
four questions the lab asked it
(transcripts t08, t13, t19):

```text
public page,  no login at all      -> 200 OK, come in
app,          no login yet         -> 401, go and sign in
app admin page, signed in, wrong
  group                            -> 403 Forbidden
vault,        password only        -> 401, sign in further
vault,        password + phone
  code                             -> 200 OK, come in
```

Five lines, and they contain the
portal, the rules, the groups and
the second factor. The rest of this
guide is those lines, earned one
chapter at a time.

## What it is not

Authelia is not a **firewall**: it
decides nothing about packets or
ports, only about named visitors
asking for web pages. It is not a
**VPN**: it does not bring a machine
onto your network; it guards web
services one request at a time,
which is a different and often
better-shaped tool (chapter 11
compares them). It is not a
password manager: it *checks*
passwords, it does not keep yours
for you. And it is not the
permission system *inside* your
services: it can tell the photo
library "this is ada, of the admins
group", but which albums ada may
delete remains the library's own
business — chapter 12 is honest
about where that line sits.

**Check:** before moving on, say
the four lab answers out loud from
the rules alone: a service anyone
may read, a service that needs a
password, an admin corner inside
it, a service that needs a second
factor, a service sealed off. If
you can predict which of the five
answers each gets, you already
understand the machine; the rest
is wiring.

## Who it is for

The household with more services
than logins it can keep straight.
The family sharing a photo server
across three time zones, where
"the Wi-Fi is the security" stopped
being true the day the address was
shared. The cautious operator who
wants the admin page of anything
to need more than a password. The
common thread is one person, their
own machines, and doors they would
like guarded by rules they wrote
themselves.

## The honest catch, up front

Authelia becomes the front door,
so it becomes the thing that must
not fall down or be fooled: it
needs the same care as anything
you expose — updates, a proper
certificate, secrets kept secret —
and if it stops, everything behind
it stops too (chapter 12). It also
only guards what the proxy routes
through it: a service still
listening on its own open port is
a window beside the locked door,
and the guide's recipes include
checking for exactly that. What
you get in return is that the care
is spent once, in one place,
instead of a little — or none — in
every service you run.
