from fastmcp import FastMCP
import re
import hashlib
import base64

mcp = FastMCP("LangServer")


@mcp.tool
async def tokenize(text: str) -> list[str]:
    """Simple whitespace-and-punctuation tokenizer."""
    tokens = re.findall(r"\w+|[^\	\n\w ]", text, flags=re.UNICODE)
    return tokens


@mcp.tool
async def detokenize(tokens: list[str]) -> str:
    """Join tokens with spaces, simple heuristic."""
    return " ".join(tokens)


@mcp.tool
async def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace into a single space and trim ends.

    Returns a cleaned string with normalized spacing suitable for downstream NLP tasks.
    """
    return re.sub(r"\s+", " ", text).strip()


@mcp.tool
async def remove_punctuation(text: str) -> str:
    """Remove punctuation characters from `text`, leaving words and whitespace.

    Useful for simple token-counting or normalization when punctuation is not needed.
    """
    return re.sub(r"[^\w\s]", "", text)


@mcp.tool
async def count_words(text: str) -> int:
    """Return the number of word tokens in `text` using the server tokenizer."""
    return len(tokenize.__wrapped__(text))


@mcp.tool
async def word_freq(text: str) -> dict:
    """Return a frequency mapping (word -> count) for tokens in `text`.

    Tokens are lowercased so counts are case-insensitive.
    """
    toks = [t.lower() for t in tokenize.__wrapped__(text)]
    freq = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    return freq


@mcp.tool
async def sentence_split(text: str) -> list[str]:
    """Split `text` into sentences using a simple punctuation-based heuristic.

    Returns a list of sentence strings (may not handle all edge cases).
    """
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sents if s]


@mcp.tool
async def simple_summarize(text: str, max_sentences: int = 3) -> str:
    """Very small extractive summarizer by sentence length heuristic."""
    sents = sentence_split.__wrapped__(text)
    ranked = sorted(sents, key=lambda s: len(s), reverse=True)
    return " ".join(ranked[:max_sentences])


@mcp.tool
async def levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between strings `a` and `b`.

    This implementation is memory-efficient (row-wise DP).
    """
    if a == b:
        return 0
    la, lb = len(a), len(b)
    dp = list(range(lb + 1))
    for i in range(1, la + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, lb + 1):
            cur = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return dp[lb]


@mcp.tool
async def jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between token sets of `a` and `b`.

    Returns a float in [0, 1], 1.0 when both inputs have identical token sets.
    """
    sa = set(tokenize.__wrapped__(a))
    sb = set(tokenize.__wrapped__(b))
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


@mcp.tool
async def ngrams(text: str, n: int = 2) -> list[str]:
    """Return a list of n-grams (as space-joined strings) from `text` tokens.

    If there are fewer than `n` tokens an empty list is returned.
    """
    toks = tokenize.__wrapped__(text)
    return [" ".join(toks[i : i + n]) for i in range(max(0, len(toks) - n + 1))]


@mcp.tool
async def to_lower(text: str) -> str:
    """Return `text` converted to lowercase."""
    return text.lower()


@mcp.tool
async def to_upper(text: str) -> str:
    """Return `text` converted to uppercase."""
    return text.upper()


@mcp.tool
async def title_case(text: str) -> str:
    """Return `text` converted to title case."""
    return text.title()


@mcp.tool
async def snake_case(text: str) -> str:
    """Convert `text` to `snake_case` by lowercasing and joining word tokens with underscores."""
    toks = [t.lower() for t in tokenize.__wrapped__(text) if re.match(r"\w+", t)]
    return "_".join(toks)


@mcp.tool
async def camel_case(text: str) -> str:
    """Convert `text` to `camelCase` using word tokens (lower-first, capitalize-following)."""
    toks = [t.lower() for t in tokenize.__wrapped__(text) if re.match(r"\w+", t)]
    return toks[0] + "".join(w.capitalize() for w in toks[1:]) if toks else ""


@mcp.tool
async def slugify(text: str) -> str:
    """Create a URL-friendly slug from `text`: lowercase, remove punctuation, replace spaces with hyphens."""
    s = remove_punctuation.__wrapped__(text).lower()
    s = re.sub(r"\s+", "-", s)
    return s.strip("-")


@mcp.tool
async def extract_numbers(text: str) -> list[float]:
    """Extract all integers and decimal numbers from `text` and return them as floats."""
    found = re.findall(r"-?\d+\.?\d*", text)
    return [float(x) for x in found]


@mcp.tool
async def hash_text(text: str, algo: str = "sha256") -> str:
    """Return a hexadecimal digest of `text` using the specified hashing `algo`.

    The default algorithm is `sha256`.
    """
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


@mcp.tool
async def base64_encode(text: str) -> str:
    """Encode `text` to standard Base64 and return the ASCII string."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@mcp.tool
async def base64_decode(b64: str) -> str:
    """Decode a Base64-encoded ASCII string and return the UTF-8 text."""
    return base64.b64decode(b64.encode("ascii")).decode("utf-8")


@mcp.tool
async def is_palindrome(text: str) -> bool:
    """Return True if `text` is a palindrome when lowercased and alphanumerics only.

    Ignores punctuation and spacing when checking the palindrome property.
    """
    s = re.sub(r"[^a-z0-9]", "", text.lower())
    return s == s[::-1]


@mcp.tool
async def regex_search(pattern: str, text: str) -> list[str]:
    """Return all non-overlapping matches of `pattern` in `text` using `re.findall`."""
    return re.findall(pattern, text)


@mcp.tool
async def replace(pattern: str, repl: str, text: str) -> str:
    """Replace occurrences of `pattern` in `text` with `repl` using regular expressions."""
    return re.sub(pattern, repl, text)


@mcp.tool
async def truncate(text: str, length: int = 100) -> str:
    """Truncate `text` to `length` characters, appending ellipsis if truncated."""
    return text if len(text) <= length else text[: length - 3] + "..."


@mcp.tool
async def read_time_estimate(text: str, wpm: int = 200) -> float:
    """Estimate reading time in minutes for `text` assuming `wpm` words per minute."""
    words = count_words.__wrapped__(text)
    return words / wpm


@mcp.tool
async def remove_stopwords(text: str) -> str:
    """Remove a small set of common English stopwords from `text` and return the filtered text."""
    stop = {"the","and","is","in","to","a","of","it","for","on"}
    toks = [t for t in tokenize.__wrapped__(text) if t.lower() not in stop]
    return " ".join(toks)


@mcp.tool
async def simple_paraphrase(text: str) -> str:
    """A tiny rule-based paraphrase that substitutes a few common words with synonyms.

    This is placeholder, rule-based, and not a replacement for a full paraphrasing model.
    """
    # small, rule-based synonym swaps
    syn = {"quick":"fast","buy":"purchase","error":"mistake","use":"utilize"}
    toks = tokenize.__wrapped__(text)
    return " ".join(syn.get(t.lower(), t) for t in toks)


@mcp.tool
async def syllable_estimate(word: str) -> int:
    """Estimate the number of syllables in `word` using a simple vowel-group heuristic."""
    w = word.lower()
    w = re.sub(r"e$", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


@mcp.tool
async def ordinal(n: int) -> str:
    """Return the ordinal string for integer `n`, e.g. 1 -> '1st', 2 -> '2nd'."""
    if 10 <= (n % 100) <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


@mcp.tool
async def count_chars(text: str) -> int:
    """Return the number of characters in `text` (including whitespace)."""
    return len(text)


@mcp.tool
async def template_render(template: str, values: dict) -> str:
    """Render a simple Python `str.format` template using `values` mapping."""
    return template.format(**values)


@mcp.tool
async def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp integer `value` between `min_val` and `max_val` and return the clamped value."""
    return max(min_val, min(value, max_val))

