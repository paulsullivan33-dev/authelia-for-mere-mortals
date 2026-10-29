# Protecting a Service End to End

By the end of this chapter a real
service sits behind Authelia: an
anonymous visitor asking for it is
sent to the portal, a signed-in
visitor is let through, and the
service itself can say *who* is
visiting — because the proxy told
it, in headers, after Authelia
vouched for them. Everything else
in this guide is a variation on
what happens here.

The lab's service is deliberately
trivial: a twelve-line Python
program (`authelia-lab/appserver.py`)
that answers every request with
the site name, the path, and the
identity headers it received. A
real service — your photo library,
your file manager — differs only
in having something better to say.
nginx stands in front of it; the
same shape works for one service
or forty.

## The proxy asks

For each protected site, nginx
gets two additions. The first is
the question, asked of every
request before anything is served
— an internal location the outside
world cannot call directly:

```nginx
location = /authelia {
  internal;
  proxy_pass https://127.0.0.1:9091/api/authz/auth-request;
  proxy_ssl_trusted_certificate /path/to/ca.crt;
  proxy_ssl_verify on;
  proxy_ssl_server_name on;
  proxy_ssl_name auth.lab.local;
  proxy_http_version 1.1;
  proxy_set_header X-Original-URL
      $scheme://$http_host$request_uri;
  proxy_set_header X-Original-Method $request_method;
  proxy_set_header X-Forwarded-Method $request_method;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_set_header X-Forwarded-Host $http_host;
  proxy_set_header X-Forwarded-Uri $request_uri;
  proxy_set_header X-Forwarded-For $remote_addr;
  proxy_set_header Content-Length "";
  proxy_set_header Connection "";
}
```

That block is
`authelia-lab/nginx-authelia-location.conf.txt`,
shared unchanged by all four lab
sites. Read the headers, because
they *are* the question: the
original address in full
(`X-Original-URL`), its pieces
spread out for convenience, the
method, and — carried along
automatically by nginx — the
visitor's session cookie, if any.
Two details earn their keep. The
call to Authelia is itself HTTPS,
verified against the lab's
certificate authority: the answer
decides who gets in, so it travels
protected even on loopback. And
the path header must carry the
*real* path — chapter 6 tells the
story of a checker that always
sent `/` and proved nothing.

## The four answers

Authelia's reply, in every case
the lab met (t08):

**"Who are you? Go and sign in."**
Status `401`, with a `Location`
header naming the portal and the
original address in its `rd`
parameter, so the visitor returns
to exactly the page they wanted.
nginx turns this into the redirect
the browser actually follows:

```nginx
error_page 401 = @login;
location @login {
  return 302 https://auth.lab.local:9091/?rd=$scheme://$http_host$request_uri&rm=$request_method;
}
```

(The `forward-auth` dialect used
by Caddy and Traefik answers `302`
directly instead — same idea, one
less translation; t09 shows it,
including the extra header it
insists on.)

**"Yes — and here is who it is."**
Status `200`, plus the identity
headers. nginx catches them and
hands them to the service:

```nginx
location / {
  auth_request /authelia;
  auth_request_set $user $upstream_http_remote_user;
  auth_request_set $groups $upstream_http_remote_groups;
  error_page 401 = @login;
  proxy_pass http://127.0.0.1:8000;
  proxy_set_header Remote-User $user;
  proxy_set_header Remote-Groups $groups;
}
```

The service never sees a password
and never checks a cookie. It
reads `Remote-User` the way it
would read the weather — trusting
it because the only road in runs
through the proxy. **That trust is
the security model**, and its
price is absolute: the service's
own port must not be reachable any
other way. The lab's app listens
on loopback only; on a real
machine, the firewall recipe in
chapter 10 is what makes the
sentence true.

**"No."** Status `403`, for a
visitor who is signed in and
*still* not allowed — the wrong
group, a sealed address. nginx
serves its plain forbidden page;
there is nothing to sign into that
would help, and the portal is not
involved (t12, t20 case 4).

**"They need more than they have
given."** Also `401` with a portal
address — a visitor whose password
was enough elsewhere, but not for
*this* rule. The portal takes them
the rest of the way (chapter 7's
vault, t13).

## The whole flow, once

Anonymous, asking for the app
(t20):

```text
$ curl https://app.lab.local:8443/
-> HTTP 302
   Location: https://auth.lab.local:9091/?rd=https://app.lab.local:8443/&rm=GET
```

And with ada's cookie — the same
cookie the portal set, presented
because `app.lab.local` lives
under the cookie's domain:

```text
$ curl https://app.lab.local:8443/ -b cookies-ada.txt
-> HTTP 200
   APP PAGE
   site: app.lab.local:8443
   path: /
   user: ada
   groups: admins,readers
```

The page naming its visitor is
the smallest possible proof, and
the one to build on your own rig:
if your service can greet the
signed-in user by name and a
stranger gets the portal instead,
the door is hung. Everything the
service knows, it learned from
headers the proxy added after
Authelia's yes.

## A trap the lab fell into

The lab's first nginx draft
answered each page itself, with a
`return 200 "..."` line inside the
same location that asked Authelia
— and every page served happily to
anonymous strangers, no question
asked (the first t20 run, kept in
the lab notes' memory if not the
file). The cause is nginx's phase
order: a `return` in a location
answers during the rewrite phase,
*before* the access phase where
`auth_request` lives. The question
was configured; it was never
reached. The fix is the shape
above: let the location do a real
job — proxy to the service — so
the access phase stands between
the visitor and the answer. If a
protected page ever serves a
stranger on your rig, suspect
this shape first (chapter 13).

**Check:** protect one service
and ask for it three ways —
signed out (portal redirect),
signed in (your name on the page),
signed in as somebody the rules
refuse (a plain 403). Three
answers, three different shapes.
That is the door working.
