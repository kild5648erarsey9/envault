"""Compare secret values across two environments."""

from __future__ import annotations

from typing import Optional

from envault.vault import get_secret, list_keys


class CompareResult:
    """Holds the result of comparing a single key across two environments."""

    def __init__(self, key: str, env_a: str, env_b: str, match: bool,
                 value_a: Optional[str], value_b: Optional[str]) -> None:
        self.key = key
        self.env_a = env_a
        self.env_b = env_b
        self.match = match
        self.value_a = value_a
        self.value_b = value_b

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CompareResult(key={self.key!r}, match={self.match}, "
            f"env_a={self.env_a!r}, env_b={self.env_b!r})"
        )


def compare_envs(
    vault_path: str,
    password: str,
    env_a: str,
    env_b: str,
    *,
    keys: Optional[list[str]] = None,
) -> list[CompareResult]:
    """Compare secret values that exist in *both* environments.

    Parameters
    ----------
    vault_path:
        Path to the vault file.
    password:
        Master password used to decrypt secrets.
    env_a, env_b:
        The two environment names to compare.
    keys:
        Optional explicit list of keys to compare.  When *None* the union of
        keys present in both environments is used.

    Returns
    -------
    list[CompareResult]
        One entry per key, sorted alphabetically.
    """
    keys_a = set(list_keys(vault_path, password, env_a))
    keys_b = set(list_keys(vault_path, password, env_b))

    if keys is not None:
        target_keys = sorted(set(keys))
    else:
        target_keys = sorted(keys_a | keys_b)

    results: list[CompareResult] = []
    for key in target_keys:
        val_a = get_secret(vault_path, password, env_a, key)
        val_b = get_secret(vault_path, password, env_b, key)
        results.append(
            CompareResult(
                key=key,
                env_a=env_a,
                env_b=env_b,
                match=(val_a == val_b),
                value_a=val_a,
                value_b=val_b,
            )
        )
    return results


def format_compare(results: list[CompareResult], *, reveal: bool = False) -> str:
    """Render a human-readable table of compare results."""
    if not results:
        return "No keys to compare."

    lines: list[str] = []
    env_a = results[0].env_a
    env_b = results[0].env_b
    lines.append(f"{'KEY':<30}  {'STATUS':<10}  {env_a:<20}  {env_b}")
    lines.append("-" * 80)
    for r in results:
        status = "MATCH" if r.match else "DIFFER"
        if reveal:
            a_display = r.value_a if r.value_a is not None else "<missing>"
            b_display = r.value_b if r.value_b is not None else "<missing>"
        else:
            a_display = "***" if r.value_a is not None else "<missing>"
            b_display = "***" if r.value_b is not None else "<missing>"
        lines.append(f"{r.key:<30}  {status:<10}  {a_display:<20}  {b_display}")
    return "\n".join(lines)
