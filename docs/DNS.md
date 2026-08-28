# DNS & Domain Record — yodacon.org

**Set 27 August 2026**, the day the domain was acquired. Records entered through the
registrar's web interface.

Later the same day the project moved from the personal account `vonglurt` to the
**`yodacon` organization**. The A and AAAA records are unaffected by that move — they
point at GitHub's Pages edge, not at an account — but the `www` CNAME and the domain
verification TXT record both name the account and must change. See *Pending changes*.

## Apex — A records (`@`)

    185.199.108.153
    185.199.109.153
    185.199.110.153
    185.199.111.153

## Apex — AAAA records (`@`)

    2606:50c0:8000::153
    2606:50c0:8001::153
    2606:50c0:8002::153
    2606:50c0:8003::153

## CNAME

    www  ->  vonglurt.github.io.     <- CURRENT, stale after the org move
    www  ->  yodacon.github.io.      <- TARGET

No CNAME on the apex — the apex carries the A/AAAA records above.

## TXT — domain verification

    _github-pages-challenge-vonglurt   "ad58c95aeb398cae9c685b0e902d9a"   <- CURRENT
    _github-pages-challenge-yodacon    <token from the org>               <- NEEDED

Domain verification does not transfer between accounts. Because `yodacon.org` is
verified under `vonglurt`, the organization cannot claim it — the Pages API rejects
the custom domain with:

    You must verify your domain yodacon.org before being able to use it.

The org's token is generated per-domain under **Organization Settings -> Pages ->
Add a domain**. There is no API for it; it has to be read from that page.

## Pending changes

1. Read the new token at <https://github.com/organizations/yodacon/settings/pages>.
2. Add TXT `_github-pages-challenge-yodacon` with that value; verify.
3. Repoint `www` CNAME to `yodacon.github.io.`
4. Set the custom domain on `yodacon/yodacon` (writes the `CNAME` file) and enable
   **Enforce HTTPS** once the certificate issues.
5. Delete the stale `_github-pages-challenge-vonglurt` TXT record, and remove the
   verified domain from the personal account's settings.

## Repo side

Pages is enabled on `yodacon/yodacon`, building from `main` at `/`. Until the custom
domain verifies it serves at <https://yodacon.github.io/yodacon/>.

## Verify

    dig +short yodacon.org A
    dig +short yodacon.org AAAA
    dig +short www.yodacon.org CNAME
    dig +short TXT _github-pages-challenge-yodacon.yodacon.org
