# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I call _collection.query() with three arguments:

- query_texts=[query]: the user's question wrapped in a list, since the API is
  built to accept a batch of queries. ChromaDB embeds it with the same
  SentenceTransformer model used at ingest, so the query vector lands in the
  same space as the stored chunks.

- n_results=n_results: caps how many chunks come back, defaulting to N_RESULTS
  from config.py: the number of closest chunks decided at setup.

- include=["documents", "metadatas", "distances"]: requests the three pieces
  I need from each result, which is: the chunk text, the game it belongs to, and the
  cosine distance score.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
One returned item is a flat dict, for example (from my "roll a 7" run):
{
  "text": "Players roll dice to resolve attacks; the attacker rolls up to three...",
  "game": "Risk",
  "distance": 0.613
}

Each field maps to a spot in the query results (i is the result index in the loop):
- "text"     <- results["documents"][0][i]   (the chunk text)
- "game"     <- results["metadatas"][0][i]["game"]   (set in embed_and_store during ingest)
- "distance" <- results["distances"][0][i]   (cosine distance; lower means closer)
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
query() returns a nested list because it's built to handle multiple queries at once,
so it wraps each query's results in its own list. Since I only send one query, I use
index [0] to get my actual results:

  results["documents"][0]  -> chunk texts
  results["metadatas"][0]  -> metadata dicts
  results["distances"][0]  -> distance scores
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
I return all n_results without filtering by distance. A hard cutoff sounds useful but
is tricky to get right, as it's too strict and leads to missing good results. Returning everything keeps it simple and lets generate_response() in
Milestone 3 decide whether the chunks are good enough to answer from. My "roll a 7"
test proved this: the top result was 0.613 (weak) but still came back, so the
generator could handle it rather than getting nothing.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) Empty collection: the `if _collection.count() == 0` guard at the top returns []

    before any query runs, so generate_response() gets nothing and can show a

    "no rules loaded" message instead of crashing.



(b) The query matches no chunks well: since I don't filter by distance, it still returns

    n_results chunks, just with high distance scores. Since nothing’s hidden, the caller

    can judge relevance straight from the distances. My "roll a 7" test showed this:

    the top result came back at 0.613, a weak score, but it was still returned.)



(c) The query matches multiple games, and results are ranked purely by semantic distance

    regardless of which game they came from, so one query can return a mix. A broad

    query like "How do you win?" pulls chunks from several games at once which displays

    correct semantic-search behavior instead of a a bug.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: [What happens when you roll a 7?]
Top result game: [Risk]
Distance score: [0.613]
Does it make sense? [Not as much as I assumed, as the score was on the weaker side. ]
```

**One thing about the query results that surprised you:**

```
The top result was the wrong game at a high distance, which showed me retrieval quality is limited by chunking rather than by the query code. 
```
