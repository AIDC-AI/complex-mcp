from fastmcp import FastMCP
import math
import random

mcp = FastMCP("StatsServer")


@mcp.tool
async def mean(numbers: list[float]) -> float:
    """Return the arithmetic mean of `numbers`.

    Raises ValueError if the list is empty.
    """
    if not numbers:
        raise ValueError("empty")
    return sum(numbers) / len(numbers)


@mcp.tool
async def median(numbers: list[float]) -> float:
    """Return the median value from `numbers`.

    Raises ValueError if the list is empty.
    """
    if not numbers:
        raise ValueError("empty")
    s = sorted(numbers)
    n = len(s)
    mid = n // 2
    return (s[mid] + s[mid - 1]) / 2 if n % 2 == 0 else s[mid]


@mcp.tool
async def mode(numbers: list[float]) -> float:
    """Return the mode (most common element) of `numbers`.

    Raises ValueError if the list is empty.
    """
    if not numbers:
        raise ValueError("empty")
    return max(set(numbers), key=numbers.count)


@mcp.tool
async def variance(numbers: list[float], sample: bool = False) -> float:
    """Compute variance of `numbers`.

    If `sample` is True uses sample variance (dividing by n-1 when appropriate).
    """
    if not numbers:
        raise ValueError("empty")
    m = await mean(numbers)
    n = len(numbers)
    denom = n - 1 if sample and n > 1 else n
    return sum((x - m) ** 2 for x in numbers) / denom


@mcp.tool
async def stdev(numbers: list[float], sample: bool = False) -> float:
    """Return the standard deviation of `numbers` (population or sample depending on `sample`)."""
    return math.sqrt(await variance(numbers, sample))


@mcp.tool
async def percentile(numbers: list[float], p: float) -> float:
    """Return the `p`-th percentile (0-100) of `numbers` using linear interpolation."""
    if not numbers:
        raise ValueError("empty")
    s = sorted(numbers)
    k = (len(s) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    d0 = s[int(f)] * (c - k)
    d1 = s[int(c)] * (k - f)
    return d0 + d1


@mcp.tool
async def zscore(numbers: list[float], x: float) -> float:
    """Return the z-score of value `x` relative to `numbers` (standard deviations from mean)."""
    s = await stdev(numbers)
    if s == 0:
        return 0.0
    return (x - await mean(numbers)) / s


@mcp.tool
async def covariance(a: list[float], b: list[float]) -> float:
    """Compute covariance between lists `a` and `b` (must have equal length)."""
    if len(a) != len(b):
        raise ValueError("length mismatch")
    m_a = await mean(a)
    m_b = await mean(b)
    return sum((x - m_a) * (y - m_b) for x, y in zip(a, b)) / len(a)


@mcp.tool
async def pearson_correlation(a: list[float], b: list[float]) -> float:
    """Compute the Pearson correlation coefficient between `a` and `b`."""
    cov = await covariance(a, b)
    sa = await stdev(a)
    sb = await stdev(b)
    if sa == 0 or sb == 0:
        return 0.0
    return cov / (sa * sb)


@mcp.tool
async def linear_regression(xs: list[float], ys: list[float]) -> dict:
    """Fit a simple linear regression y = slope*x + intercept to `(xs, ys)`.

    Returns a dict with `slope` and `intercept`.
    """
    if len(xs) != len(ys) or not xs:
        raise ValueError("invalid")
    n = len(xs)
    xm = sum(xs) / n
    ym = sum(ys) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    den = sum((x - xm) ** 2 for x in xs)
    if den == 0:
        slope = 0.0
    else:
        slope = num / den
    intercept = ym - slope * xm
    return {"slope": slope, "intercept": intercept}


@mcp.tool
async def sample_random(population: list, k: int = 1) -> list:
    """Return `k` unique random samples from `population` (using `random.sample`)."""
    return random.sample(population, k)


@mcp.tool
async def bootstrap_mean(numbers: list[float], iterations: int = 1000) -> float:
    """Estimate the mean via bootstrap resampling over `iterations` draws."""
    res = []
    n = len(numbers)
    for _ in range(iterations):
        samp = [random.choice(numbers) for _ in range(n)]
        res.append(sum(samp) / n)
    return sum(res) / len(res)


@mcp.tool
async def histogram(numbers: list[float], bins: int = 10) -> dict:
    """Return a histogram mapping bin index -> count for `numbers` across `bins` equal-width bins."""
    if not numbers:
        return {}
    mi, ma = min(numbers), max(numbers)
    if mi == ma:
        return {0: len(numbers)}
    width = (ma - mi) / bins
    hist = {i: 0 for i in range(bins)}
    for x in numbers:
        idx = int((x - mi) / width)
        if idx == bins:
            idx = bins - 1
        hist[idx] += 1
    return hist


@mcp.tool
async def skewness(numbers: list[float]) -> float:
    """Return the sample skewness of `numbers` (Fisher-Pearson adjusted estimator)."""
    n = len(numbers)
    if n < 3:
        return 0.0
    m = await mean(numbers)
    s = await stdev(numbers)
    return sum(((x - m) / s) ** 3 for x in numbers) * (n / ((n - 1) * (n - 2)))


@mcp.tool
async def kurtosis(numbers: list[float]) -> float:
    """Return (excess) kurtosis of `numbers` (subtracts 3 for normal distribution)."""
    n = len(numbers)
    if n < 4:
        return 0.0
    m = await mean(numbers)
    s = await stdev(numbers)
    return sum(((x - m) / s) ** 4 for x in numbers) - 3


@mcp.tool
async def cumulative_sum(numbers: list[float]) -> list[float]:
    """Return the cumulative sum list for `numbers` (running totals)."""
    out = []
    total = 0
    for x in numbers:
        total += x
        out.append(total)
    return out


@mcp.tool
async def moving_average(numbers: list[float], window: int = 3) -> list[float]:
    """Return a list of moving averages computed with a sliding `window` over `numbers`."""
    if window <= 0:
        raise ValueError("invalid")
    res = []
    for i in range(len(numbers)):
        window_vals = numbers[max(0, i - window + 1) : i + 1]
        res.append(sum(window_vals) / len(window_vals))
    return res


@mcp.tool
async def z_normalize(numbers: list[float]) -> list[float]:
    """Return z-normalized values (mean 0, std 1) for `numbers`.

    If standard deviation is zero returns a list of zeros.
    """
    m = await mean(numbers)
    s = await stdev(numbers)
    if s == 0:
        return [0 for _ in numbers]
    return [(x - m) / s for x in numbers]


@mcp.tool
async def quantiles(numbers: list[float], q: int = 4) -> list[float]:
    """Return `q-1` quantile cutoff values dividing `numbers` into `q` quantiles."""
    if not numbers:
        return []
    s = sorted(numbers)
    n = len(s)
    return [s[int(i * n / q)] for i in range(1, q)]


@mcp.tool
async def count_greater(numbers: list[float], threshold: float) -> int:
    """Count how many elements in `numbers` are strictly greater than `threshold`."""
    return sum(1 for x in numbers if x > threshold)


@mcp.tool
async def correlation_matrix(columns: list[list[float]]) -> list[list[float]]:
    """Compute a correlation matrix (Pearson) for a list of numeric columns."""
    n = len(columns)
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            mat[i][j] = await pearson_correlation(columns[i], columns[j])
    return mat


@mcp.tool
async def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp `value` between `lo` and `hi` and return the clamped float."""
    return max(lo, min(value, hi))

