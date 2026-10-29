# Notifications and Password Reset

By the end of this chapter grace
has forgotten her password, been
sent a reset letter, used it, and
signed in with a new password —
while her old one stopped working
everywhere at once. Along the way
the notifier shows its whole hand,
and **regulation** — the quiet
mechanism counting failures —
earns its paragraph the hard way.

## The notifier is a first-class part

Authelia speaks to users away from
the portal through the **notifier**:
the reset letter here, the
elevation code in chapter 7, the
warnings when a device is added.
Chapter 3 configured the
**filesystem** notifier — every
message appended to one text file.
Production deployments configure
SMTP instead and the letters go to
real inboxes; nothing else about
the flows changes, and in one way
the file is the better teacher:
you can open it and read, whole,
what your users will read. A
sample stands in
`authelia-lab/transcripts/` inside
the elevation transcripts (t14):
subject, greeting, the code or
link, and the "if this was not
you" instructions with a
revocation link — each letter is
written assuming it might land in
front of someone whose account is
under attack, and says what to do
about it.

## The reset, in three calls

The portal's "forgot password"
flow, as the API calls the browser
makes (t22–t24):

```bash
# 1. Ask. (The answer is the same
#    whether or not the user
#    exists — chapter 4's manners,
#    for the same reason.)
curl -X POST \
  https://auth.lab.local:9091/api/reset-password/identity/start \
  -d '{"username":"grace"}'
# {"status":"OK"}

# The letter arrives: a link to
# /reset-password/step2?token=<a
# signed token, 295 characters in
# the lab — its signature is what
# the jwt_secret from chapter 3
# protects>

# 2. Follow the link: the page
#    presents the token back.
curl -X POST \
  https://auth.lab.local:9091/api/reset-password/identity/finish \
  -d '{"token":"<the token>"}'
# {"status":"OK"}

# 3. Set the new password.
curl -X POST \
  https://auth.lab.local:9091/api/reset-password \
  -d '{"password":"willow-ember-63"}'
# HTTP 200 — with an empty body,
# which startled the lab until it
# checked: empty is its whole reply.
```

And the consequences, checked
rather than assumed (t23): the old
password now earns the generic
401; the new one signs in. The
lab then reset grace *back* to her
original password through the same
three calls (t24), because a guide
that prints passwords has to leave
its story consistent — the flow
takes two minutes when the mailbox
is a file.

One detail worth a stare: Authelia
**rewrote `users.yml` in place**,
replacing grace's hash with the
new one (and tidying her entry as
it did). The file backend is a
living file, not a read-only
roster — which is why the backup
recipe copies it, and why hand
edits should be made while you
remember the server may write
back.

## Regulation: failures are counted

The last mechanism is the one you
meet only when something is
already going wrong. Chapter 3's
configuration carries:

```yaml
regulation:
  max_retries: 3
  find_time: '2m'
  ban_time: '5m'
```

Three failures within two minutes
buys a five-minute ban. The lab
spent it on grace: four wrong
passwords, then the *correct* one
— refused (t33):

```text
{"status":"KO","message":
 "Authentication failed. Check your credentials."}
```

The same generic words as any
failure, and that is deliberate:
the banned user — or the stranger
guessing — learns nothing about
the state of the account. The
truth lives where the operator
can see it, in the log:

```text
Unsuccessful 1FA authentication attempt by user
'grace' and they are banned until 7:18:27PM ...
```

Set the numbers by thinking about
your humans: too tight and a
fumbled phone keyboard locks a
parent out of the photos; too
loose and the counting is
decoration. Five minutes of ban
costs a real user one cup of tea;
it costs a guessing script the
entire point of guessing quickly.

**Check:** you have this chapter
when a reset letter arrives in the
notifier's file within seconds of
the request, the old password
dies the moment the new one is
set, and — the check nobody enjoys
— three deliberate failures make
even the truth wait five minutes.
