"""ドメイン信頼度（SOURCE_TIERS / サフィックス / デフォルト）の単体テスト。"""

from __future__ import annotations

import pytest

from app.verify_service import SOURCE_TIERS, credibility_for_url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.reuters.com/article/foo", 1.0),
        ("https://apnews.com/x", 1.0),
        ("https://mobile.twitter.com/user/status/1", 0.2),
        ("https://www.reddit.com/r/test", 0.2),
        ("https://www.wsj.com/articles/x", 0.5),
    ],
)
def test_tier_domains(url: str, expected: float) -> None:
    cred, reason, name = credibility_for_url(url)
    assert cred == expected
    assert name
    assert reason


def test_gov_edu_org_suffix() -> None:
    c1, r1, _ = credibility_for_url("https://www.nih.gov/foo")
    assert c1 == 0.9
    assert "政府" in r1 or "gov" in r1.lower()

    c2, r2, _ = credibility_for_url("https://www.mit.edu/")
    assert c2 == 0.9
    assert "教育" in r2 or "edu" in r2.lower()

    c3, r3, _ = credibility_for_url("https://www.wikipedia.org/wiki/X")
    assert c3 == 0.9
    assert "非営利" in r3 or "org" in r3.lower()


def test_unknown_domain_default_score(capsys: pytest.CaptureFixture[str]) -> None:
    c, r, name = credibility_for_url("https://some-random-unknown-blog.example.net/page")
    assert c == 0.3
    assert "0.3" in r or "デフォルト" in r
    captured = capsys.readouterr()
    assert "Unknown domain, default score applied" in captured.out


def test_source_tiers_has_expected_keys() -> None:
    assert "reuters.com" in SOURCE_TIERS
    assert "nytimes.com" in SOURCE_TIERS
    assert "x.com" in SOURCE_TIERS
