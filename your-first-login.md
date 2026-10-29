# Your First Login

By the end of this chapter ada has
signed in at the portal — once with
a password that fails, once with
the one that works — and you have
seen exactly what the portal hands
back: a session cookie holding
almost nothing, and an API that
knows her name but masks her email.
The lab has no browser, so every
step below is the call the
browser's own JavaScript makes,
run with `curl`. On your desk the
same events happen behind the
portal's pages; the wire does not
care which of you is driving.

## The portal answers

```bash
curl https://auth.lab.local:9091/
# HTTP 200, 2588 bytes
```

What comes back is the application
shell: a `<base>` tag pointing at
the portal's own address, the
script and stylesheet, feature
flags in the page body
(`data-rememberme`, `data-resetpassword`)
— and an empty `<title>`, which the
script fills in once it runs (t06).
A browser shows the sign-in page;
`curl` shows you the honest truth
that the page is a program, not a
document. Remember this in chapter
13, the day a text-only client
reports the portal "blank".

## The wrong password

The sign-in form sends one call:

```bash
curl -X POST \
  https://auth.lab.local:9091/api/firstfactor \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada",
       "password":"wrong-on-purpose",
       "keepMeLoggedIn":false}'
# {"status":"KO","message":
#  "Authentication failed. Check your credentials."}
# HTTP 401
```

Read the refusal carefully, because
it is a small lesson in manners:
the same words whether the user
does not exist or the password is
wrong. The portal will not help a
stranger enumerate your users.
What it *does* record — the failed
attempt, the address it came from —
goes to the server's log and the
storage's authentication log,
which is where chapter 10 reads
refusals back. And failures are
not free forever: repeat them and
**regulation** answers, which
chapter 9's ban demonstrates.

## The right password

```bash
curl -X POST \
  https://auth.lab.local:9091/api/firstfactor \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada",
       "password":"foxglove-lantern-42",
       "keepMeLoggedIn":false}' \
  -c cookies-ada.txt
# {"status":"OK"}        HTTP 200
```

(The password is the lab's
throwaway, printed on purpose.
Yours will be neither printed nor
in any transcript.)

The interesting part is what
arrived with the OK — the cookie
jar now holds one line that
matters:

```text
#HttpOnly_.lab.local  TRUE  /  TRUE  ...  authelia_session  LR$Ar*KvFDcpw31GHfmByQH5t1*xu%qa
```

Four facts in that line. The
cookie is named `authelia_session`
(the name chapter 3 chose). It is
scoped to the whole `lab.local`
domain — every service under it
will be shown the same cookie,
which is the entire trick of
single sign-on. It is marked
`HttpOnly` and `Secure`: scripts
in the page cannot read it, and
browsers will only send it over
HTTPS. And its value is **32
characters of session ID** — not
the session, just its name. The
record it unlocks lives in the
Authelia process (chapter 12 draws
the consequence; t34 proves it).

Ask who the session belongs to:

```bash
curl https://auth.lab.local:9091/api/user/info \
  -b cookies-ada.txt
# {"status":"OK","data":{
#   "display_name":"Ada Lab",
#   "emails":["a*a@lab.local"],
#   "has_totp":false, ... }}
```

Her name in full, her email
masked even from herself through
this endpoint — a small privacy
habit worth noticing — and, for
now, no second factors. Chapter 7
changes that line's meaning, if
not (as the lab discovered, and
chapter 13 records) always its
contents.

## Signing out

```bash
curl -X POST \
  https://auth.lab.local:9091/api/logout \
  -b cookies-ada.txt
# {"status":"OK", ...}
```

The same cookie, presented to the
auth endpoint afterwards, is
anonymous again (t31). Logout is
a server-side event, not just a
forgotten cookie — the record the
ID pointed to is gone.

**Check:** you have a first login
when the wrong password earns the
generic 401, the right one earns
`{"status":"OK"}` and a cookie
whose value is a short ID, and
`/api/user/info` answers with your
user's name. From here the portal
is a known place. Chapter 5 puts
something behind it.
