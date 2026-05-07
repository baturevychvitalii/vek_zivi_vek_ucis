# Spanish Deck — Reading Resources

Reading material for Rioplatense Spanish (River Plate dialect, Argentine/Uruguayan authors).
This file is read during lit-search sessions — not part of the card-generation compile chain.

---

## How to Use This File

When recommending books:
1. Read the user's situation (level, recent reads, theme request).
2. Use discovery sources to build a thematic candidate pool.
3. Check fetch sources for availability and EPUB download links.
4. Fetch a short sample passage from each top candidate, assess difficulty against deck level.
5. Present 3–5 options with title, author, difficulty verdict, and direct download link.
6. On confirmation, download EPUB to `cache/epubs/spanish/`.

**Deck level context:** Run `compile-deck-context` (or read `compiled.md` if fresh) to confirm
current level before making difficulty assessments.

---

## Discovery Sources

These are for finding thematic candidates — they don't always provide the EPUB directly.

### Goodreads Lists
Good for thematic search: "Argentine novels," "Rioplatense Spanish," "tango literature," etc.
Search: `https://www.goodreads.com/search?q={theme}+argentina&search_type=books`
Or browse curated lists: `https://www.goodreads.com/list/search?q={theme}+argentina`
Best for: discovering contemporary and mid-20th-century titles not well covered by public-domain sources.
Limitation: does not provide downloads — use to build a candidate list, then check fetch sources.

### Wikipedia Bibliographies
Author pages on `es.wikipedia.org` list complete bibliographies with publication dates.
Useful for: confirming a work exists, finding the correct original title, checking publication year
(pre-1929 works are public domain in most jurisdictions; Argentine copyright is life+70 years).
Search: `https://es.wikipedia.org/wiki/{Author_Name}` then look for "Bibliografía" section.

---

## Fetch Sources

These provide the actual text. Check these after building a candidate pool.

### Project Gutenberg
**Coverage:** 19th–early 20th century. Strong on pre-1929 works: Lugones (El Payador,
Las Fuerzas Extrañas), Macedonio Fernández, Eduardo Wilde, José Hernández (Martín Fierro).
Cortázar and Borges are mostly under copyright and not available.

**Search:** `https://gutenberg.org/ebooks/search/?query={terms}&l=es`
Always include `l=es` to filter to Spanish-language works. Results are ranked by download count.
Sort options: `sort_order=popularity`, `sort_order=release_date`, `sort_order=title`.

**Download format:** From a book's detail page, EPUB links follow this pattern:
- EPUB3 (modern): `https://www.gutenberg.org/ebooks/{ID}.epub3.images`
- EPUB (legacy): `https://www.gutenberg.org/ebooks/{ID}.epub.images`
Fetch the detail page to confirm the ID and available formats before downloading.

**Difficulty range:** Pre-modernist prose is typically denser and more formal than contemporary
Spanish. Hernández's Martín Fierro is gauchesque verse — unusual register. Lugones is lyrical
and lexically rich; expect C1 regardless of the user's level.

---

### Wikisource (Spanish)
**Coverage:** Public-domain texts, including some that Gutenberg doesn't carry. Better for
poetry, essays, and short prose. Author pages are well-organized.

**Navigation:** `https://es.wikisource.org/wiki/Autor:{Author_Name}` (e.g., `Autor:Leopoldo_Lugones`)
Works are grouped by genre. Individual work pages have the full text.

**Download:** Wikisource does not offer EPUB directly from the UI — only PDF and plain HTML.
For EPUB, use the "Descargar como PDF" option or read online. If the user only needs to sample
a passage (for difficulty assessment), read online is sufficient.

**Best use:** Difficulty sampling and reading online. Not the primary EPUB source.

---

### Elejandría
**Coverage:** Broad — contemporary and classic Spanish-language fiction, legally free.
Not limited to pre-1929; includes works under open licenses.
Strong for: Argentine contemporary authors, Latin American fiction, shorter works.

**Search:** `https://www.elejandria.com/buscar?q={query}`
Author page: `https://www.elejandria.com/autor/{author-slug}/{id}`
Individual book: `https://www.elejandria.com/libro/{title-slug}/{author-slug}/{id}`

**Download format:** Primarily PDF. EPUB availability varies by title — check the individual
book page. The site does not expose a search API; WebFetch the search results page and parse
the title/author/link list from the HTML.

**Gotcha:** Link rot is common on older entries. If a download link fails, try the author
page directly and navigate to the work from there.

---

### Internet Archive
**Coverage:** Very broad — scanned books, donated digital texts, some borrowable items.
Useful as a fallback when other sources don't carry a title.

**Search API (JSON):**
`https://archive.org/advancedsearch.php?q={query}+AND+language%3Aspanish+AND+mediatype%3Atexts&fl[]=identifier,title,creator,format&rows=20&output=json`

For Argentine literary fiction specifically:
`q=creator%3A{Author}+AND+language%3Aspanish+AND+mediatype%3Atexts`

**Download:** Once you have an `identifier`, the item page is `https://archive.org/details/{identifier}`.
EPUB, PDF, and plain text are often available from item pages. Direct file URL pattern:
`https://archive.org/download/{identifier}/{identifier}.epub`

**Limitation:** Search results for Argentine literary fiction are mixed in quality — the catalog
skews toward institutional and non-fiction material. Better for known authors/titles than
thematic discovery.

---

## Author Coverage Quick Reference

| Author | Dialect fit | Gutenberg | Wikisource | Elejandría | Notes |
|---|---|---|---|---|---|
| José Hernández | Gauchesque | Yes | Yes | Yes | Martín Fierro — verse, unusual register |
| Leopoldo Lugones | Rioplatense | Yes (3 works) | Yes | Yes | Dense, lexically rich — C1 |
| Roberto Arlt | Rioplatense | No (copyright) | No | Likely | Urban, colloquial Buenos Aires register |
| Jorge Luis Borges | Rioplatense | No (copyright) | Partial | Likely | Some early essays may be public domain |
| Julio Cortázar | Rioplatense | No (copyright) | No | Likely | Check Elejandría or Archive |
| Eduardo Wilde | Rioplatense | Possible | Possible | Unknown | 19th century; worth checking Gutenberg |
