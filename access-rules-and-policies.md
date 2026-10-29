# Access Rules and Policies

By the end of this chapter you can
write the rule book for a household:
which services are open, which need
a password, which need a second
factor, which are sealed — and you
will know the two ways rules
surprise people, because the lab
met both. This is the part of
Authelia you will actually write;
the rest is plumbing that carries
its decisions.

## The anatomy of a rule

```yaml
access_control:
  default_policy: 'deny'
  rules:
    - domain: 'app.lab.local'
      resources:
        - '^/admin($|/.*)'
      subject: 'group:admins'
      policy: 'one_factor'
```

A rule is a set of conditions and
one **policy**. The conditions the
lab used:

- **domain** — the name being
  visited. It may name several, or
  use a wildcard.
- **resources** — patterns the
  page path must match, written as
  regular expressions.
- **subject** — who is asking:
  `user:<name>` or `group:<name>`.
  A rule with a subject only ever
  concerns those people.
- (Named for completeness, not run
  in the lab: **networks**, the
  addresses a request may come
  from, and **methods**, the HTTP
  verbs it may use.)

The policies are the whole
vocabulary of answers:

| Policy | Meaning | The lab's site |
|---|---|---|
| `bypass` | No login at all | `public.lab.local` |
| `one_factor` | A password (the first factor) | `app.lab.local` |
| `two_factor` | Password plus a registered second factor | `vault.lab.local` |
| `deny` | Nobody, whatever they present | `blocked.lab.local` |

And beneath the list, the
**default policy**: what happens
to an address no rule mentions.
The lab sets `deny`, and so should
you — a rule book that defaults to
closed fails safe when you forget
a line, and merely inconvenient
when you forget it the other way.

## First match wins — and rules fall through

Rules are read top to bottom, and
the first rule whose conditions
*all* match decides. That sentence
contains both surprises.

The lab wanted the app's `/admin`
corner to be admins-only, and
wrote the natural thing:

```yaml
    - domain: 'app.lab.local'
      resources: ['^/admin($|/.*)']
      subject: 'group:admins'
      policy: 'one_factor'
    - domain: 'app.lab.local'
      policy: 'one_factor'
```

Then it asked, as grace — signed
in, readers group, no business in
`/admin` — and was **let in**
(t10). Nothing had malfunctioned.
For grace the first rule does not
match: its subject condition fails,
so the rule is not "her rule" at
all, and reading continues to the
general app rule, which she
satisfies. A subject rule does not
stand guard over a path; it offers
terms to *its* people and steps
aside for everyone else.

The seal is a second rule that
catches whoever the first one
stepped aside for:

```yaml
    - domain: 'app.lab.local'
      resources: ['^/admin($|/.*)']
      subject: 'group:admins'
      policy: 'one_factor'
    # Everyone else who asks for
    # /admin: without this rule they
    # fall through to the app rule.
    - domain: 'app.lab.local'
      resources: ['^/admin($|/.*)']
      policy: 'deny'
    - domain: 'app.lab.local'
      policy: 'one_factor'
```

Now the lab's answers are the
designed ones (t12): ada in,
grace `403`, and an anonymous
visitor sent to sign in first —
Authelia asks who you are before
it tells you that even knowing
won't help. Order is meaning:
specific before general, seals
before doors.

## The whole book, and its answers

The lab's finished book (in
`authelia-lab/configuration.yml.txt`)
is six rules long — the four sites
and the sealed corner — and its
complete answer table, every line
of it observed, is:

| Asking for | Nobody | grace (readers) | ada (admins), password | ada, + TOTP |
|---|---|---|---|---|
| public | 200 | 200 | 200 | 200 |
| app | login | 200 | 200 | 200 |
| app `/admin` | login | **403** | 200 | 200 |
| vault | login | login* | login* | 200 |
| blocked | login | 403 | 403 | 403 |

*For vault, "login" means the
portal asks for the missing second
factor; grace, who has no device
registered, can never complete it
— the answer stays no, by a
politer road (chapter 7).

Two cells deserve a stare. The
public page answers `200` to
*nobody* — and if that nobody is
in fact signed in, the proxy still
passes their name along (t21 case
9): bypass means "no login
*required*", not "identity
withheld". And `blocked` refuses
even the fully-proven ada: `deny`
is not a stronger lock on the same
door, it is the absence of a door.

**Check:** before you run a single
request, write the answer table
for your own rule book — every
site against every kind of
visitor. Then ask, with the
`authelia-lab/authz.sh` pattern or
your browser, and compare. A cell
that surprises you is a rule you
did not mean, and finding it at
your desk is the entire point of
having written the table first.
