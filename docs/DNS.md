# DNS & Domain Record — yodacon.org

**Set 27 August 2026**, the day the domain was acquired and the Yodacon GitHub
organization was created. Records entered through the registrar's web interface.

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

    www  ->  <org>.github.io.

No CNAME on the apex — the apex carries the A/AAAA records above.

## TXT — domain verification

    _github-pages-challenge-<org>   <token>

The token is generated per-domain by GitHub under
**Organization Settings -> Pages -> Add a domain**. It is not reproducible from
this repo; read it there if the record ever needs to be re-entered.

## Repo side

- Custom domain set in **repo Settings -> Pages**, which writes the `CNAME` file.
- **Enforce HTTPS** enabled once the certificate issued.

## Verify

    dig +short yodacon.org A
    dig +short yodacon.org AAAA
    dig +short www.yodacon.org CNAME
    dig +short TXT _github-pages-challenge-<org>.yodacon.org
