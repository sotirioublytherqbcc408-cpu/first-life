# The First Time

[中文说明](README.md) · English

A searchable handbook for all the "first times" nobody teaches you: taking a train, opening a bank
account, seeing a doctor, signing a lease, filing a police report, handling a layoff.

Every entry answers the same three questions — **what to do / what usually goes wrong / which official
document backs it up** — and carries an evidence grade.

> Live site: <https://thefirst.easymoreai.com/>
> Single-file offline edition: <https://thefirst.easymoreai.com/offline.html> (the whole book in one HTML file, works with no network)

- **438 entries** across 18 chapters (travel, flights, hotels, living alone, money, shopping, school, job hunting, health, documents & law, driving, social, dating & marriage, family, going abroad, digital life, food & entertainment, safety)
- **264 source links**, each one fetched and checked during writing; evidence graded **A** (statutes and official documents) / **B** (official guidance or major media) / **C** (practical consensus, no formal rule)
- **457 standalone URLs**: every entry has its own page, pre-rendered as static HTML, so search engines can index it
- **Zero external dependencies**: system font stack, no images, no CDN, no third-party scripts

The content is written for mainland China: the regulations, hotlines, and procedures cited are the ones
that actually apply there.

## Repository layout

```
content/            The only source of truth: 438 entries in 18 JSON files
web/                Site source: app.css (design tokens) + app.js (interaction)
build.py            Generator: content/ + web/  ->  docs/
verify.py           QA: structure, coverage, duplicates, id uniqueness, link liveness
docs/               Generated output (GitHub Pages serves from here; do not edit by hand)
outline/raw.json    The original 1,028-title outline the content was merged from
STYLE.md            Writing rules: how to merge, how to write, how to source
```

## Preview locally

```bash
python3 build.py                 # writes docs/
python3 -m http.server -d docs   # then open http://localhost:8000
```

Opening `docs/index.html` directly also works, but internal links need an HTTP server to resolve.

## Editing content

Everything lives in `content/NN-name.json`. One entry looks like this:

```json
{
  "id": "trip-01",
  "title": "Buying a train ticket, changing it, refunding it",
  "merged_from": ["Buying a train ticket", "Using the 12306 app", "Waiting-list tickets"],
  "tags": ["transport", "rail"],
  "cost": { "money": "ticket price", "time": "10-30 min", "willpower": "low" },
  "evidence": "A",
  "body": {
    "plain": "Tickets are tied to your real name; buy through the official 12306 site or app...",
    "steps": ["Register on 12306 and complete identity verification", "Pick a train, then a seat class, then pay"],
    "pitfalls": ["Never hand your account and password to a third-party ticket-grabbing service"]
  },
  "sources": [
    { "name": "Railway Passenger Transport Regulations", "url": "https://www.gov.cn/...", "note": "Chapter 5: changes and refunds" }
  ]
}
```

Then run:

```bash
python3 verify.py --fields --cross --urls   # structure, ids, coverage, duplicates, link liveness
python3 build.py --cname your.domain        # regenerate docs/
```

Field definitions, merge rules and sourcing discipline are in **[STYLE.md](STYLE.md)**; please read
**[CONTRIBUTING.md](CONTRIBUTING.md)** before adding an entry.

## Deploying your own copy

**On your own domain (site root)**

Set GitHub Pages to *Settings → Pages → Deploy from a branch → main / docs*, point a CNAME record at
`<your-user>.github.io`, and build with your own domain:

```bash
python3 build.py --cname thefirst.example.com --url https://thefirst.example.com
```

**As a project site (`https://user.github.io/repo/`)**

Sub-path deployments must pass `--base`, otherwise internal links point at the domain root:

```bash
python3 build.py --base /repo/ --url https://user.github.io/repo
```

**Any static host**

`docs/` is a plain static directory. Vercel, Cloudflare Pages, Netlify, object storage, or nginx all work.

## Content rules

1. **Every entry needs a source**, and that source must be an official page you actually opened
   (government portals, ministries, courts, provincial governments, national standards).
2. If the official page cannot be fetched (JavaScript-rendered or bot-protected), use the same authority's
   mirrored copy and say so in `note`, including the keywords you verified on the page.
3. **Never invent numbers or links.** If a fee or deadline is uncertain, write "check the official page"
   and link to it.
4. Describe **procedure and legal basis only** — no medical diagnosis, no investment advice, no legal opinion.

## License

- **Code** (`build.py`, `verify.py`, `web/`, `.github/`): [MIT](LICENSE)
- **Content** (`content/`, `outline/`, entry text under `docs/`): [CC BY 4.0](LICENSE-CONTENT) — reuse and adapt freely with attribution

The site format is inspired by the open-source project
[HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter) (CC BY 4.0); credit is kept in the
site footer. The entry text here was written independently and does not copy that project.

## Disclaimer

Content is for practical reference only; always follow the latest official rules. Nothing here is medical,
legal, or investment advice.
