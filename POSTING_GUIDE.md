# Posting guide for the Duke Gallo blog

Every new post is one JSON file in `posts/`, named `YYYY-MM-DD-slug.json`.
Netlify rebuilds the site (`python3 build.py . dist`) on every push to `main`.

## Who it's for (rotate between these)
1. **Homebuyers and homeowners** in Southern California: buying, refinancing, equity, credit, closing costs, loan programs (FHA, VA, jumbo, non-QM, bank statement, DSCR), plain-English market explainers.
2. **Real estate agents and referral partners**: writing stronger offers, financing contingencies, what slows escrow, how to talk financing with buyers, market shifts that affect their clients.
3. **Loan officers Duke could recruit**: building a pipeline, working with realtors, why broker channel, mentorship, leadership, career growth, what a great team culture looks like.

Check `posts/` before choosing a topic. Never repeat a topic or angle that's already covered; rotate audiences so no two consecutive posts target the same one.

## Voice
- First person, as Duke Gallo, Vice President at West Capital Lending, who leads a team of 45 loan officers and staff.
- Warm, direct, confident, practical. Short paragraphs. No fluff, no hype, no clichés ("in today's fast-paced market", "navigating the complex world of").
- Open with a concrete, relatable hook (a client scenario stated generally, a common misconception, a sharp question). Do not invent named clients or specific client stories presented as real.
- End with a clear takeaway section.

## Must-haves for every post
- 900–1,400 words of body.
- `title` under 65 characters with the primary keyword near the front. `description` 140–160 characters.
- 4–6 `keywords`: one primary long-tail keyword plus related terms; include a Southern California / Orange County local variant when natural.
- `category`: one of `Homebuyers`, `Homeowners`, `Agents`, `Loan Officers`, `Market`.
- Body uses `<h2>` sections (4–6) and at least one list; a comparison table where useful (wrap tables in `<div class="tbl">`). No `<h1>` in the body.
- Link to 1–2 earlier posts in `posts/` when relevant (`/blog/<slug>/`).
- 2–4 `faq` entries (question + concise answer) for FAQ rich results.
- A photo from Unsplash: find a relevant photo page with WebSearch/WebFetch on unsplash.com and use its `images.unsplash.com` URL with `?fm=jpg&q=70&w=1600&auto=format&fit=crop`; set `image_alt` (describe the photo), `image_credit` (photographer name) and `image_credit_url` (their unsplash.com profile). Use only photos under the free Unsplash License (not Unsplash+). Never use photos of real public figures, logos, or branded property.

## Compliance rules (non-negotiable)
- **No specific interest rates, APRs, payment amounts, down-payment amounts or percentages tied to a specific offer, or loan terms presented as available from Duke** (these are Regulation Z "triggering terms"). General program facts are fine when accurate and phrased generally (e.g. "VA loans often require no down payment for eligible borrowers").
- Never promise approval, savings, a rate, or timelines. No "guaranteed", "lowest rates", "best rates", "no credit check".
- Market numbers (rates, prices, inventory, loan limits) must come from a source found this run with WebSearch (Freddie Mac PMMS, FHFA, CFPB, HUD, VA, Fannie Mae, CAR, NAR, Census). Name the source in the text and link it. If you can't verify a number, leave it out.
- Recruiting posts: no income or compensation figures or promises. Speak to culture, training, support, and growth.
- No legal or tax advice; suggest consulting a tax professional where relevant.
- Never write about specific named people, competitors by name in a negative way, or politics.
- The site footer already carries the NMLS, Equal Housing Opportunity and "not a commitment to lend" disclosures; don't repeat them in the body.

## JSON shape
```json
{
  "slug": "lowercase-hyphenated",
  "title": "...",
  "description": "...",
  "date": "YYYY-MM-DD",
  "category": "Homebuyers",
  "keywords": ["..."],
  "image": "https://images.unsplash.com/photo-...?fm=jpg&q=70&w=1600&auto=format&fit=crop",
  "image_alt": "...",
  "image_credit": "Photographer Name",
  "image_credit_url": "https://unsplash.com/@handle",
  "faq": [{"q": "...", "a": "..."}],
  "body_html": "<p>...</p>"
}
```
Write the JSON with Python (`json.dump(..., ensure_ascii=False, indent=2)`) so quotes are escaped correctly, run `python3 build.py . /tmp/dist` to confirm it builds, then commit and push.
