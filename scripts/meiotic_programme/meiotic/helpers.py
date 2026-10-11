"""Logging, download, z-scoring, FDR, AUC and coherence helpers."""
from __future__ import annotations

from .config import *  # noqa: F401,F403


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def post_json(path: str, payload: dict | list, timeout: int = 300) -> object:
    req = urllib.request.Request(
        CBIO + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def download(url: str, dest: Path, skip_if_exists: bool = True) -> Path:
    """Fetch `url` to `dest`. Retries transient failures with backoff."""
    if skip_if_exists and dest.exists() and dest.stat().st_size > 0:
        log(f"  cached: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for attempt in range(4):
        try:
            urllib.request.urlretrieve(url, dest)
            log(f"  downloaded: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
            return dest
        except Exception as exc:  # noqa: BLE001 - report and retry
            last = exc
            log(f"  attempt {attempt + 1} failed ({type(exc).__name__}); retrying")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"could not download {url}: {last}")


def zscore_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Z-score each gene (row) across samples. Zero-variance rows -> NaN."""
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1).replace(0, np.nan), axis=0)


def bh_fdr(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(p, dtype=float)
    ok = ~np.isnan(p)
    out = np.full_like(p, np.nan)
    q = p[ok]
    n = q.size
    order = np.argsort(q)
    ranked = q[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.clip(ranked, 0, 1)
    out[ok] = adj
    return out


def auc(y: np.ndarray, x: np.ndarray) -> float:
    """AUROC via the Mann-Whitney U identity (no sklearn dependency here)."""
    y = np.asarray(y).astype(bool)
    x = np.asarray(x, dtype=float)
    keep = ~np.isnan(x)
    y, x = y[keep], x[keep]
    if y.sum() == 0 or (~y).sum() == 0:
        return np.nan
    u = stats.mannwhitneyu(x[y], x[~y], alternative="two-sided").statistic
    return float(u / (y.sum() * (~y).sum()))


def mean_pairwise_rho(mat: pd.DataFrame) -> float:
    """Mean off-diagonal Spearman rho — the module coherence statistic."""
    if mat.shape[0] < 2 or mat.shape[1] < 3:
        return np.nan
    c = mat.T.corr(method="spearman").values
    iu = np.triu_indices(c.shape[0], 1)
    return float(np.nanmean(c[iu]))


def fmt_p(p: float) -> str:
    return "NA" if p is None or np.isnan(p) else f"{p:.3g}"
