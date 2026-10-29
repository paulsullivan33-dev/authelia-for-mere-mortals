# Writing Criteria for This Series

Every guide in this series is written to the
same standard. The point is not polish for its
own sake; it is that a reader who is about to
trust a tool with their hardware, their network
or their money should be able to tell, quickly,
what is known, what is opinion, and what was
never actually checked.

1. **Audience: the home user.** The reader is
   technically capable but new to this specific
   tool: "mere mortals," not enterprise IT.
   Assume a person at a home desk, on their own
   hardware, with no team and no budget line.
   Anything that only makes sense at company
   scale is labelled as such or left out.

2. **Honest.** Say what the tool is bad at,
   what it costs, and where it stops working.
   No hype, no vendor voice, no hiding the
   limits in footnotes. If a feature is a
   paid tier, a roadmap item, or a rumour,
   the text says so in those words.

3. **Researched, not remembered.** Claims come
   from running the thing and from current
   documentation, not from training-data
   memory of how it probably works. Version
   numbers, menu names, and behaviours are
   checked against the real thing before they
   are written down.

4. **Verified for real.** The procedures in
   the guide were actually executed, on real
   (if small) setups, and the results —
   including the failures — are what the
   chapters describe. Where a step genuinely
   could not be run, it is labelled
   *documented-only* in place, never narrated
   as if it happened.

5. **Plain language, short sentences.** Say
   the thing in the fewest clear words.
   Introduce a technical term only when the
   reader needs it, explain it where it first
   appears, and collect the set in a glossary.
   Long sentences and clever phrasing are
   defects, not style.

6. **Reader outcomes, with a check.** Each
   chapter opens by naming what the reader
   will have when they finish it, and gives
   them a check — a command, a test, an
   observable behaviour — that proves it on
   their own machine. A chapter the reader
   cannot verify is a claim, not a lesson.

7. **Software choices stated honestly.** Where
   this guide picks a tool, a protocol or a
   service, it says plainly that Authelia is
   free, open-source software a household can
   run on hardware it already owns, and it
   names the real costs around it: a machine
   that stays on to serve the portal, a domain
   of your own for real (rather than lab) use,
   and certificates to keep current. The
   neighbours chapter names the genuine
   alternatives — portals with admin consoles
   and directories built in, a hosted access
   service, the proxy's own basic auth — and
   what each costs in money, machinery or
   surrendered control.

8. **An ethics line, drawn early.** This
   guide teaches guarding doors, which is the
   same knowledge, sign aside, as opening
   them. The line is drawn in the first
   chapter and holds throughout: these
   mechanisms are for services that are
   yours, with accounts for people you mean
   to let in. The lab's users are invented,
   its passwords are throwaway and printed
   only so a reader can reproduce the run,
   and nothing in the guide is a technique
   for defeating someone else's portal —
   the failure modes it studies are the
   operator's own mistakes, found by
   operating their own door.

9. **No plagiarism.** The words are original.
   Facts and procedures are learned from the
   tool, its documentation, and the references
   listed below, then written fresh in this
   series' voice. Short quotations (an error
   message, a line of output) are quoted as
   such and attributed to the run that
   produced them.

## Verification notes for this guide

**The machine.** Every run below happened on
one shared Ubuntu 24.04 computer, as root,
with all services bound to loopback and
pretend names (`*.lab.local`) resolved by
`curl --resolve`, so nothing depended on a
hosts file and nothing was reachable from
outside. The lab's full evidence —
configuration (with its throwaway secrets
replaced by placeholders), user file, proxy
configuration, helper scripts, and 35
transcripts — is in `authelia-lab/`.

**The software.** Authelia **4.39.28**, the
official `linux-amd64` release tarball from
the project's GitHub releases, its SHA-256
verified against the release's published
`checksums.sha256` before the binary ran.
nginx **1.24.0** (the machine's own package)
as the reverse proxy. The pretend service
behind it is a twelve-line Python program
that echoes the identity headers it
receives. OpenSSL 3.0.13 made the lab's
certificate authority and server
certificate.

**Run live, for real:**

- Download with checksum verification,
  version check, and `validate-config`
  passing — including one warning (a client
  requesting refresh tokens without the
  `offline_access` scope) that was fixed by
  listening to it.
- First start on an empty database: schema
  migrated from nothing to version 29; TLS
  portal answering on loopback; `/api/health`
  returning `{"status":"OK"}`.
- Portal fetched (HTTP 200, application
  shell); login refused with the generic 401
  for a wrong password and accepted for the
  right one; session cookie inspected
  (HttpOnly, Secure, SameSite=Lax, whole
  domain, 32-character ID); `/api/user/info`
  answered with the display name and a masked
  email.
- The auth question asked directly, in both
  dialects: **auth-request** (401 + Location
  for anonymous, 200 + `Remote-User` /
  `Remote-Groups` / `Remote-Name` /
  `Remote-Email` for a session, 403 for a
  sealed address) and **forward-auth** (302
  for anonymous — after discovering it
  refuses to answer at all, with a 400,
  unless `X-Forwarded-Method` is sent).
- The full flow through nginx for four
  sites — public (bypass), app (one
  factor), vault (two factor), blocked
  (deny): anonymous redirected to the
  portal, signed-in users served with their
  names on the page, the sealed site
  refusing even a fully proven user. One
  early run of this check passed *wrongly*
  because an nginx `return` answered before
  the auth check could run; the guide
  teaches that trap from the corrected run.
- Access rules in both directions,
  including the fall-through lesson: a
  subject rule alone left an admin corner
  open to the readers' group; adding the
  sealing `deny` rule made the answers
  match the design (admin in, reader 403,
  anonymous sent to log in).
- Elevation by one-time code through the
  filesystem notifier (including the failed
  first attempt: the code must be sent in
  the JSON field `otc`), then TOTP
  registration in its three calls, the
  device confirmed in the settings endpoint
  and in the database, and the generated
  codes computed locally by a twelve-line
  Python implementation of RFC 6238.
- A two-factor sign-in completed end to
  end: password alone refused at the vault,
  TOTP code accepted, vault then answering
  200 with the user's headers.
- Password reset through the notifier:
  request, token link followed, new
  password set (the confirming call answers
  200 with an empty body), old password
  refused, new one accepted; the file
  backend observed rewriting the user's
  hash in `users.yml` in place.
- Regulation: four wrong passwords, then
  the correct one still refused; the ban
  visible only in the server log, exactly
  as the chapter describes.
- Logout invalidating the session
  server-side.
- A server restart destroying all
  sessions: a cookie that answered 200
  answered 401 after the restart, and the
  database confirmed there is no session
  table — sessions live in the process.
- A complete OpenID Connect authorization
  code flow for a registered client:
  discovery document, consent (including
  the rejection recorded when the decision
  was sent under the wrong field name, and
  the corrected run), code delivered to
  the client's redirect URI, code exchanged
  with the client's secret for access, ID
  and refresh tokens, and `userinfo`
  returning the name, email and groups
  that the ID token itself left null.
- The site itself: built with
  `mkdocs build --strict` from a staging
  copy laid out exactly as the deploy
  workflow lays it out; build clean, title
  present. (Result recorded at build time
  in the guide's lab notes.)

**Documented-only — not run, and labelled
as such wherever the guide touches them:**

- **WebAuthn, security keys and passkeys.**
  Their ceremony needs a browser and an
  authenticator performing cryptographic
  steps a `curl` client cannot imitate.
  Described from the project's
  documentation.
- **Duo push approval** — needs a Duo
  account and a phone; named only.
- **The LDAP/Active Directory user
  backend** — needs a directory to bind
  to; described for shape, not run.
- **The SMTP notifier.** The filesystem
  notifier carried every letter the flows
  produce; SMTP changes the transport, not
  the letters, and no mail server exists
  in this sandbox. (The sandbox also
  forbids the outbound UDP Authelia's
  startup clock check uses, so the check
  was disabled in the lab configuration
  only, and the guide says not to disable
  it in real use.)
- **Caddy and Traefik as the live proxy.**
  Their dialect (forward-auth) was proven
  by direct calls to Authelia; the
  end-to-end proxy run used nginx and the
  auth-request dialect.
- **Consent modes other than the default
  explicit flow** (`auto` with a
  remembered duration, `pre-configured`),
  and OIDC flows beyond authorization
  code — named from the configuration
  reference and the discovery document.
- **Multi-instance setups and external
  session storage** — the memory-session
  limit is documented from the project's
  storage model and from the restart test
  above; the HA remedy was not built.
- **Authenticator apps on a phone** — the
  codes here were computed by a script
  implementing the same published
  algorithm the apps use.
- **Running Authelia as a service**
  (systemd units, Docker, Kubernetes) —
  the release ships units and the guide
  points at them; the lab ran the bare
  binary in the foreground.

**Fixtures.** The lab's people — ada and
grace, their groups, their emails, the
`lab.local` names, the client and its
secret — are invented for this guide, and
their passwords are throwaway values
printed in the text as such. No real
person, organisation, address or
credential appears anywhere in it.

## References

- Authelia's own documentation —
  configuration, integration with each
  proxy, the OpenID Connect provider, and
  the API reference: https://www.authelia.com/
- The Authelia 4.39.28 release and its
  published checksums:
  https://github.com/authelia/authelia/releases
- RFC 6238, *TOTP: Time-Based One-Time
  Password Algorithm* — the algorithm the
  lab's code generator implements.
- The OpenID Connect Core specification —
  for the flow chapter 8 follows.
