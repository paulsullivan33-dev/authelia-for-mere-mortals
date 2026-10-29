# Installing Authelia

By the end of this chapter Authelia
is running on your machine, with a
configuration it has checked and
accepted, one user in its file, and
its health endpoint answering. No
proxy yet — that is chapter 5. The
reward for the order is that when
something later misbehaves, you
know the foundation was sound.

## Get the program

Authelia ships as a single static
binary. On the project's GitHub
releases page, take the archive for
your machine — the lab's was
`authelia-v4.39.28-linux-amd64.tar.gz`
— and the `checksums.sha256` file
beside it, and prove the download
is the file the project published
before you run anything:

```bash
grep 'linux-amd64.tar.gz$' checksums.sha256 \
  | sha256sum -c -
# authelia-v4.39.28-linux-amd64.tar.gz: OK
./authelia --version
# authelia version v4.39.28
```

Inside the archive: the binary, a
long commented `config.template.yml`
(the whole configuration surface,
worth keeping as a reference), and
systemd units for running it as a
service (t00). There are also
official packages and container
images; the bare binary is what
this guide teaches, because nothing
stands between you and what it does.

## The configuration file

Authelia is run by one YAML file.
The lab's whole file — with its
throwaway secrets replaced by
placeholders — is
`authelia-lab/configuration.yml.txt`;
this chapter builds the parts you
need first and leaves the rule book
to chapter 6 and the identity
provider to chapter 8. The pieces,
in the order the file wants them:

**Where it listens, and its
certificate.** The portal is HTTPS
from the start; there is no plain
HTTP mode worth wanting.

```yaml
server:
  address: 'tcp://127.0.0.1:9091/'
  tls:
    certificate: '/path/to/server.crt'
    key: '/path/to/server.key'
```

The certificate must cover the
portal's name — the lab made a
small local certificate authority
and one certificate naming all five
of its sites (t01); the
[mkcert guide](https://paulsullivan33-dev.github.io/mkcert-for-mere-mortals/)
in this series is the friendly way
to do the same on a real desk.

**The users.** First the file of
people, then the pointer to it.
Passwords enter the file only as
hashes, made by Authelia itself:

```bash
authelia crypto hash generate argon2 \
  --password 'foxglove-lantern-42'
# Digest: $argon2id$v=19$m=65536,t=3,p=4$...
```

```yaml
# users.yml — ada and grace are
# invented; the passwords are
# throwaway lab passwords.
users:
  ada:
    disabled: false
    displayname: 'Ada Lab'
    password: '$argon2id$v=19$...'
    email: ada@lab.local
    groups:
      - admins
      - readers
  grace:
    disabled: false
    displayname: 'Grace Lab'
    password: '$argon2id$v=19$...'
    email: grace@lab.local
    groups:
      - readers
```

```yaml
authentication_backend:
  file:
    path: '/path/to/users.yml'
```

Groups are just names in a list.
They mean nothing until a rule in
chapter 6 uses one.

**The session.** Three decisions:
a secret (a long random string,
used to protect session data), how
long a session may live, and —
the one that shapes everything —
the **cookie domain**: the parent
domain of every service the portal
will guard, because the browser
only presents the cookie to names
under it.

```yaml
session:
  name: 'authelia_session'
  secret: '<a 64-character random string>'
  expiration: '1h'
  inactivity: '10m'
  cookies:
    - domain: 'lab.local'
      authelia_url: 'https://auth.lab.local:9091'
      default_redirection_url: 'https://app.lab.local:8443/'
```

Generate each secret in this
chapter with the tool itself:
`authelia crypto rand --length 64`
(t03). A real deployment writes
its real domain here; the lab's
`lab.local` is a stand-in your
machine resolves to itself.

**Storage and its key.** SQLite,
one file, and an encryption key
that protects the device secrets
inside it:

```yaml
storage:
  encryption_key: '<another random string>'
  local:
    path: '/path/to/db.sqlite3'
```

Lose the key and the stored TOTP
devices are sealed forever — the
backup recipe in chapter 10 exists
because of sentences like that.

**The notifier.** For the lab, a
file. For anyone real, SMTP — the
shape is in the project's
documentation and the rest of this
guide only ever says "the letter
arrives", which the file makes
visible:

```yaml
notifier:
  filesystem:
    filename: '/path/to/notifications.txt'
```

Password reset needs one more
secret of its own:

```yaml
identity_validation:
  reset_password:
    jwt_secret: '<a third random string>'
```

## Check it, then start it

The habit that saves evenings:
Authelia will read the whole
configuration and complain *before*
it runs anything.

```bash
authelia validate-config \
  --config configuration.yml
# Configuration parsed and loaded
# successfully without errors.
```

The lab's first version earned one
warning — a client asking for
refresh tokens without the scope
that makes them meaningful — and
the fix was to listen to it (t04).
Then start it:

```bash
authelia --config configuration.yml
```

First startup creates the database
and migrates its schema to
current, announces the listener,
and stops there, waiting — the
lab's log is t05. **Check:** ask
the health endpoint, exactly as a
monitor would:

```bash
curl https://auth.lab.local:9091/api/health
# {"status":"OK"}
```

If the name does not resolve on
your machine yet, that is the one
piece of plumbing the lab did with
`curl --resolve` flags instead of
a hosts file; on a real desk, a
line in `/etc/hosts` or a record
in your local DNS does it. Either
way: portal running, health green,
one user waiting. Chapter 4 signs
her in.
