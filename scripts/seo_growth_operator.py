#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports" / "seo"
DATA_DIR = REPORTS_DIR / "data"
SEO_SKILL_DIR = Path("/Users/parthantala/.codex/skills/seo")

DEFAULT_SITE_URL = "https://pixeratools.com"
DEFAULT_GA_PROPERTY_ID = "500585866"
DEFAULT_GA_MEASUREMENT_ID = "G-8233939FQQ"
DEFAULT_KEY_FILE = REPO_ROOT / "keys" / "pixera-seo-automation.json"
DEFAULT_GSC_SITES = [
    "sc-domain:pixeratools.com",
    "https://pixeratools.com/",
]
DEFAULT_LOCALE_TZ = os.environ.get("SEO_OPERATOR_LOCALE_TZ", "America/Los_Angeles")
CHECKOUT_API_KEY_VARS = [
    "LEMON_SQUEEZY_API_KEY",
    "LEMONSQUEEZY_API_KEY",
]
CHECKOUT_STORE_ID_VARS = [
    "LEMON_SQUEEZY_STORE_ID",
    "LEMONSQUEEZY_STORE_ID",
]
KEY_EVENTS = [
    "open_guide",
    "open_resource",
    "view_pricing",
    "begin_checkout",
    "download_installer",
    "generate_lead",
    "purchase",
]
FUNNEL_EVENTS = [
    "open_guide",
    "view_pricing",
    "begin_checkout",
    "download_installer",
    "generate_lead",
]


class HttpError(RuntimeError):
    def __init__(self, status_code: int, body: str, url: str):
        super().__init__(f"HTTP {status_code} for {url}")
        self.status_code = status_code
        self.body = body
        self.url = url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh Pixera SEO/growth analytics and write dated/latest reports."
    )
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--ga-property-id", default=DEFAULT_GA_PROPERTY_ID)
    parser.add_argument("--ga-measurement-id", default=DEFAULT_GA_MEASUREMENT_ID)
    parser.add_argument("--service-account-key", default=str(DEFAULT_KEY_FILE))
    parser.add_argument("--locale-tz", default=DEFAULT_LOCALE_TZ)
    parser.add_argument(
        "--gsc-site",
        action="append",
        dest="gsc_sites",
        help="Optional Search Console site URL/property. Can be passed multiple times.",
    )
    parser.add_argument("--force-deep", action="store_true")
    parser.add_argument("--major-batch", action="store_true")
    parser.add_argument("--technical-conflict", action="store_true")
    parser.add_argument(
        "--strategy-shift",
        default="",
        help="Short freeform explanation of a strategy shift to include in the report.",
    )
    parser.add_argument(
        "--run-live-deep-audit",
        action="store_true",
        help="Run the bundled seo skill checks against the live site when deep mode is enabled.",
    )
    return parser.parse_args()


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    *,
    timeout: int | None = None,
) -> str:
    completed = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return completed.stdout


def urlsafe_b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def load_service_account(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def mint_google_access_token(service_account: dict[str, Any], scopes: list[str]) -> str:
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    header = {"alg": "RS256", "typ": "JWT"}
    claim_set = {
        "iss": service_account["client_email"],
        "scope": " ".join(scopes),
        "aud": service_account["token_uri"],
        "iat": now,
        "exp": now + 3600,
    }
    signing_input = (
        f"{urlsafe_b64(json.dumps(header, separators=(',', ':')).encode())}."
        f"{urlsafe_b64(json.dumps(claim_set, separators=(',', ':')).encode())}"
    )

    with tempfile.NamedTemporaryFile("w", delete=False) as handle:
        handle.write(service_account["private_key"])
        key_path = handle.name

    try:
        signature = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=signing_input.encode("utf-8"),
            check=True,
            capture_output=True,
        ).stdout
    finally:
        try:
            os.unlink(key_path)
        except FileNotFoundError:
            pass

    assertion = f"{signing_input}.{urlsafe_b64(signature)}"
    payload = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode("utf-8")
    data = fetch_json(
        service_account["token_uri"],
        method="POST",
        payload=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return data["access_token"]


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    payload: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request = urllib.request.Request(url, data=payload, method=method)
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise HttpError(error.code, body, url) from error


def fetch_text(
    url: str,
    *,
    method: str = "GET",
    payload: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    request = urllib.request.Request(url, data=payload, method=method)
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise HttpError(error.code, body, url) from error


def ga_run_report(
    access_token: str,
    property_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    return fetch_json(
        url,
        method="POST",
        payload=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )


def gsc_search_analytics(
    access_token: str,
    site: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    quoted_site = urllib.parse.quote(site, safe="")
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{quoted_site}/searchAnalytics/query"
    return fetch_json(
        url,
        method="POST",
        payload=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )


def get_env_value(names: list[str]) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def today_in_timezone(tz_name: str) -> dt.datetime:
    return dt.datetime.now(ZoneInfo(tz_name))


def date_range(days: int, tz_name: str) -> tuple[str, str]:
    local_now = today_in_timezone(tz_name)
    end_date = local_now.date() - dt.timedelta(days=1)
    start_date = end_date - dt.timedelta(days=days - 1)
    return start_date.isoformat(), end_date.isoformat()


def value_to_number(value: str) -> float:
    try:
        if "." in value:
            return float(value)
        return float(int(value))
    except ValueError:
        return 0.0


def round_metric(value: float, digits: int = 2) -> float:
    if math.isfinite(value):
        return round(value, digits)
    return 0.0


def collect_git_state() -> dict[str, Any]:
    status_output = run_command(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=REPO_ROOT,
    )
    changed_files = []
    for raw_line in status_output.splitlines():
        if not raw_line.strip():
            continue
        status = raw_line[:2].strip()
        path = raw_line[3:].strip()
        changed_files.append({"status": status, "path": path})

    pages_shipped = []
    crawl_files = []
    analytics_files = []
    content_paths = []
    ignored_noise = []
    for entry in changed_files:
        path = entry["path"]
        if path in {".DS_Store"} or path.startswith("output/") or path.startswith("keys/"):
            ignored_noise.append(path)
            continue
        if path.endswith(".html") and (
            path.startswith("blog/")
            or path == "privacy.html"
            or path.endswith("/index.html")
            or path == "index.html"
        ):
            content_paths.append(path)
        if path in {"robots.txt", "sitemap.xml", "llm.txt", "llms.txt", "llms-full.txt"}:
            crawl_files.append(path)
        if path in {"analytics-events.js", "growth-pages.css"}:
            analytics_files.append(path)

    pages_shipped = [
        path
        for path in content_paths
        if path.startswith("blog/")
        or path == "privacy.html"
        or path.endswith("/index.html")
    ]

    return {
        "changed_files": changed_files,
        "pages_shipped": sorted(set(pages_shipped)),
        "content_paths": sorted(set(content_paths)),
        "crawl_files": sorted(set(crawl_files)),
        "analytics_files": sorted(set(analytics_files)),
        "ignored_noise": sorted(set(ignored_noise)),
    }


def collect_ga4(
    access_token: str,
    property_id: str,
    locale_tz: str,
) -> dict[str, Any]:
    start_14, end_14 = date_range(14, locale_tz)
    start_30, end_30 = date_range(30, locale_tz)

    account_summary = fetch_json(
        "https://analyticsadmin.googleapis.com/v1alpha/accountSummaries",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    total_views_report = ga_run_report(
        access_token,
        property_id,
        {
            "dateRanges": [{"startDate": start_30, "endDate": end_30}],
            "metrics": [{"name": "screenPageViews"}],
        },
    )
    total_views = 0
    rows = total_views_report.get("rows") or []
    if rows:
        total_views = int(rows[0]["metricValues"][0]["value"])

    page_report = ga_run_report(
        access_token,
        property_id,
        {
            "dateRanges": [{"startDate": start_30, "endDate": end_30}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [
                {"name": "screenPageViews"},
                {"name": "sessions"},
                {"name": "totalUsers"},
            ],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": 15,
        },
    )
    top_pages = []
    homepage_views = 0
    for row in page_report.get("rows", []):
        path = row["dimensionValues"][0]["value"] or "(not set)"
        views = int(row["metricValues"][0]["value"])
        sessions = int(row["metricValues"][1]["value"])
        users = int(row["metricValues"][2]["value"])
        if path == "/":
            homepage_views = views
        top_pages.append(
            {
                "pagePath": path,
                "screenPageViews": views,
                "sessions": sessions,
                "totalUsers": users,
            }
        )

    event_report = ga_run_report(
        access_token,
        property_id,
        {
            "dateRanges": [{"startDate": start_30, "endDate": end_30}],
            "dimensions": [{"name": "date"}, {"name": "eventName"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "eventName",
                    "inListFilter": {"values": KEY_EVENTS},
                }
            },
            "orderBys": [
                {"dimension": {"dimensionName": "date"}},
                {"dimension": {"dimensionName": "eventName"}},
            ],
            "limit": 1000,
        },
    )

    events_by_name = defaultdict(int)
    events_by_day = defaultdict(lambda: defaultdict(int))
    for row in event_report.get("rows", []):
        day = row["dimensionValues"][0]["value"]
        event_name = row["dimensionValues"][1]["value"]
        event_count = int(row["metricValues"][0]["value"])
        events_by_name[event_name] += event_count
        events_by_day[day][event_name] += event_count

    start_7, end_7 = date_range(7, locale_tz)
    event_totals = {
        "7d": summarize_event_window(events_by_day, start_7, end_7),
        "14d": summarize_event_window(events_by_day, start_14, end_14),
        "30d": dict(events_by_name),
    }

    return {
        "status": "ok",
        "property_id": property_id,
        "measurement_id": DEFAULT_GA_MEASUREMENT_ID,
        "window_14d": {"startDate": start_14, "endDate": end_14},
        "window_30d": {"startDate": start_30, "endDate": end_30},
        "account_summary_count": len(account_summary.get("accountSummaries", [])),
        "top_pages_30d": top_pages,
        "event_totals": event_totals,
        "homepage_concentration_30d": round_metric(
            homepage_views / total_views if total_views else 0.0, 4
        ),
        "site_views_30d": total_views,
    }


def summarize_event_window(
    events_by_day: dict[str, dict[str, int]],
    start_date: str,
    end_date: str,
) -> dict[str, int]:
    start = dt.date.fromisoformat(start_date)
    end = dt.date.fromisoformat(end_date)
    totals = defaultdict(int)
    current = start
    while current <= end:
        key = current.strftime("%Y%m%d")
        for event_name, event_count in events_by_day.get(key, {}).items():
            totals[event_name] += event_count
        current += dt.timedelta(days=1)
    return dict(totals)


def collect_gsc(
    access_token: str,
    sites: list[str],
    locale_tz: str,
) -> dict[str, Any]:
    start_14, end_14 = date_range(14, locale_tz)
    start_30, end_30 = date_range(30, locale_tz)

    best_error: dict[str, Any] | None = None
    for site in sites:
        try:
            totals_14 = gsc_search_analytics(
                access_token,
                site,
                {"startDate": start_14, "endDate": end_14, "rowLimit": 1},
            )
            totals_30 = gsc_search_analytics(
                access_token,
                site,
                {"startDate": start_30, "endDate": end_30, "rowLimit": 1},
            )
            top_queries = gsc_search_analytics(
                access_token,
                site,
                {
                    "startDate": start_30,
                    "endDate": end_30,
                    "dimensions": ["query"],
                    "rowLimit": 10,
                },
            )
            top_pages = gsc_search_analytics(
                access_token,
                site,
                {
                    "startDate": start_30,
                    "endDate": end_30,
                    "dimensions": ["page"],
                    "rowLimit": 10,
                },
            )
            return {
                "status": "ok",
                "site": site,
                "window_14d": {"startDate": start_14, "endDate": end_14},
                "window_30d": {"startDate": start_30, "endDate": end_30},
                "totals_14d": {
                    "clicks": totals_14.get("rows", [{}])[0].get("clicks", 0),
                    "impressions": totals_14.get("rows", [{}])[0].get("impressions", 0),
                    "ctr": totals_14.get("rows", [{}])[0].get("ctr", 0),
                    "position": totals_14.get("rows", [{}])[0].get("position", 0),
                },
                "totals_30d": {
                    "clicks": totals_30.get("rows", [{}])[0].get("clicks", 0),
                    "impressions": totals_30.get("rows", [{}])[0].get("impressions", 0),
                    "ctr": totals_30.get("rows", [{}])[0].get("ctr", 0),
                    "position": totals_30.get("rows", [{}])[0].get("position", 0),
                },
                "top_queries_30d": normalize_gsc_rows(top_queries.get("rows", []), "query"),
                "top_pages_30d": normalize_gsc_rows(top_pages.get("rows", []), "page"),
            }
        except HttpError as error:
            best_error = {
                "status": "error",
                "site": site,
                "status_code": error.status_code,
                "message": humanize_gsc_error(error.status_code, error.body),
            }
        except Exception as error:  # pragma: no cover - defensive only
            best_error = {
                "status": "error",
                "site": site,
                "message": str(error),
            }
    return best_error or {
        "status": "unavailable",
        "message": "No Search Console site candidates were configured.",
    }


def normalize_gsc_rows(rows: list[dict[str, Any]], dimension: str) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        key = row.get("keys", [""])[0]
        normalized.append(
            {
                dimension: key,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round_metric(float(row.get("ctr", 0)), 4),
                "position": round_metric(float(row.get("position", 0)), 2),
            }
        )
    return normalized


def compact_http_error(body: str) -> str:
    compact = re.sub(r"\s+", " ", body).strip()
    return compact[:280] if len(compact) > 280 else compact


def humanize_gsc_error(status_code: int, body: str) -> str:
    compact = compact_http_error(body)
    if "has not been used in project" in compact or "searchconsole.googleapis.com/overview" in compact:
        return (
            "The Search Console API is disabled for Google Cloud project `351755032737` or has not been enabled yet. "
            "Enable `searchconsole.googleapis.com`, then retry with a verified property that this service account can access."
        )
    if status_code == 403:
        return "The service account does not currently have usable Search Console access for the configured property."
    return compact


def collect_checkout(locale_tz: str) -> dict[str, Any]:
    api_key = get_env_value(CHECKOUT_API_KEY_VARS)
    store_id = get_env_value(CHECKOUT_STORE_ID_VARS)
    if not api_key:
        return {
            "status": "unavailable",
            "message": "No Lemon Squeezy API key was present in the environment.",
        }
    if not store_id:
        return {
            "status": "unavailable",
            "message": "Lemon Squeezy API key exists, but no store ID was configured.",
        }

    start_30, end_30 = date_range(30, locale_tz)
    url = (
        "https://api.lemonsqueezy.com/v1/orders"
        f"?filter[store_id]={urllib.parse.quote(store_id)}"
        f"&page[size]=100"
    )
    try:
        response = fetch_json(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/vnd.api+json",
            },
        )
    except HttpError as error:
        return {
            "status": "error",
            "status_code": error.status_code,
            "message": compact_http_error(error.body),
        }

    rows = []
    revenue = 0.0
    order_count = 0
    for entry in response.get("data", []):
        attributes = entry.get("attributes", {})
        created_at = attributes.get("created_at", "")
        if not created_at:
            continue
        created_date = created_at[:10]
        if not (start_30 <= created_date <= end_30):
            continue
        total = attributes.get("total_usd") or attributes.get("total")
        revenue += float(total or 0)
        order_count += 1
        rows.append(
            {
                "identifier": attributes.get("identifier"),
                "created_at": created_at,
                "total_usd": float(total or 0),
                "status": attributes.get("status"),
            }
        )

    return {
        "status": "ok",
        "window_30d": {"startDate": start_30, "endDate": end_30},
        "orders_30d": order_count,
        "revenue_usd_30d": round_metric(revenue, 2),
        "recent_orders": rows[:10],
    }


def load_snapshot_history(limit: int = 14) -> list[dict[str, Any]]:
    if not DATA_DIR.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    for path in sorted(DATA_DIR.glob("*/snapshot.json"))[-limit:]:
        try:
            snapshots.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    return snapshots


def metric_from_snapshot(snapshot: dict[str, Any], path: list[str], default: float = 0) -> float:
    current: Any = snapshot
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    if current is None:
        return default
    if isinstance(current, (int, float)):
        return float(current)
    return default


def compare_snapshots(history: list[dict[str, Any]], current_snapshot: dict[str, Any]) -> dict[str, Any]:
    previous = history[-3:]
    comparison_rows = []
    for snapshot in previous:
        comparison_rows.append(
            {
                "run_date": snapshot.get("run_date") or snapshot.get("report_date"),
                "gsc_clicks_14d": metric_from_snapshot(snapshot, ["gsc", "totals_14d", "clicks"]),
                "gsc_impressions_14d": metric_from_snapshot(snapshot, ["gsc", "totals_14d", "impressions"]),
                "gsc_ctr_14d": metric_from_snapshot(snapshot, ["gsc", "totals_14d", "ctr"]),
                "open_guide_14d": metric_from_snapshot(snapshot, ["ga4", "event_totals", "14d", "open_guide"]),
                "view_pricing_14d": metric_from_snapshot(snapshot, ["ga4", "event_totals", "14d", "view_pricing"]),
                "begin_checkout_14d": metric_from_snapshot(snapshot, ["ga4", "event_totals", "14d", "begin_checkout"]),
                "download_installer_14d": metric_from_snapshot(snapshot, ["ga4", "event_totals", "14d", "download_installer"]),
                "generate_lead_14d": metric_from_snapshot(snapshot, ["ga4", "event_totals", "14d", "generate_lead"]),
            }
        )

    stagnation_reasons = []
    stagnation = False
    if len(previous) >= 3:
        last_three = previous[-3:]
        key_metrics = [
            ("gsc_clicks_14d", ["gsc", "totals_14d", "clicks"]),
            ("open_guide_14d", ["ga4", "event_totals", "14d", "open_guide"]),
            ("begin_checkout_14d", ["ga4", "event_totals", "14d", "begin_checkout"]),
        ]
        for label, path in key_metrics:
            values = [metric_from_snapshot(item, path) for item in last_three]
            if values and all(values[index] <= values[index - 1] for index in range(1, len(values))):
                stagnation = True
                stagnation_reasons.append(
                    f"{label} was flat or down across the last {len(values)} report snapshots: {values}"
                )

    return {
        "last_three_reports": comparison_rows,
        "stagnation": stagnation,
        "stagnation_reasons": stagnation_reasons,
        "current_metrics": {
            "gsc_clicks_14d": metric_from_snapshot(current_snapshot, ["gsc", "totals_14d", "clicks"]),
            "gsc_impressions_14d": metric_from_snapshot(current_snapshot, ["gsc", "totals_14d", "impressions"]),
            "gsc_ctr_14d": metric_from_snapshot(current_snapshot, ["gsc", "totals_14d", "ctr"]),
            "open_guide_14d": metric_from_snapshot(current_snapshot, ["ga4", "event_totals", "14d", "open_guide"]),
            "view_pricing_14d": metric_from_snapshot(current_snapshot, ["ga4", "event_totals", "14d", "view_pricing"]),
            "begin_checkout_14d": metric_from_snapshot(current_snapshot, ["ga4", "event_totals", "14d", "begin_checkout"]),
            "download_installer_14d": metric_from_snapshot(current_snapshot, ["ga4", "event_totals", "14d", "download_installer"]),
            "generate_lead_14d": metric_from_snapshot(current_snapshot, ["ga4", "event_totals", "14d", "generate_lead"]),
        },
    }


def decide_deep_mode(
    *,
    locale_tz: str,
    git_state: dict[str, Any],
    ga4: dict[str, Any],
    gsc: dict[str, Any],
    self_review: dict[str, Any],
    force_deep: bool,
    major_batch: bool,
    technical_conflict: bool,
) -> tuple[bool, list[str]]:
    reasons = []
    local_now = today_in_timezone(locale_tz)
    if local_now.strftime("%A") == "Sunday":
        reasons.append(f"User locale date is {local_now.date().isoformat()} ({local_now.strftime('%A')}).")
    if force_deep:
        reasons.append("Deep mode was explicitly forced for this run.")
    if major_batch:
        reasons.append("A major batch of content or growth pages is shipping in this run.")
    if technical_conflict:
        reasons.append("Technical findings conflicted with the prior content strategy.")
    if len(git_state["pages_shipped"]) >= 2:
        reasons.append("Two or more content pages changed in the current run.")
    if gsc.get("status") != "ok" and ga4.get("homepage_concentration_30d", 0) >= 0.5:
        reasons.append("Homepage traffic concentration remains high while Search Console visibility is still partially blind.")
    if self_review["stagnation"]:
        reasons.extend(self_review["stagnation_reasons"])
    return bool(reasons), reasons


def run_live_deep_audit(site_url: str, report_date: str) -> dict[str, Any]:
    output_dir = DATA_DIR / report_date
    html_report_path = REPORTS_DIR / f"SEO-REPORT-{report_date}.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "status": "ok",
        "output_dir": str(output_dir),
        "html_report_path": str(html_report_path),
        "commands": {},
    }

    commands = {
        "robots": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "robots_checker.py"),
                site_url,
            ],
            "timeout": 60,
        },
        "llms": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "llms_txt_checker.py"),
                site_url,
            ],
            "timeout": 60,
        },
        "broken_links": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "broken_links.py"),
                site_url,
            ],
            "timeout": 120,
        },
        "internal_links": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "internal_links.py"),
                site_url,
                "--depth",
                "1",
                "--max-pages",
                "20",
                "--json",
            ],
            "timeout": 120,
        },
        "social_meta": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "social_meta.py"),
                site_url,
            ],
            "timeout": 60,
        },
        "pagespeed_mobile": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "pagespeed.py"),
                site_url,
                "--strategy",
                "mobile",
                "--json",
            ],
            "timeout": 90,
        },
        "html_report": {
            "cmd": [
                sys.executable,
                str(SEO_SKILL_DIR / "scripts" / "generate_report.py"),
                site_url,
                "--output",
                str(html_report_path),
            ],
            "timeout": 180,
        },
    }

    for key, payload in commands.items():
        try:
            output = run_command(
                payload["cmd"],
                cwd=REPO_ROOT,
                timeout=payload["timeout"],
            )
            result["commands"][key] = {"status": "ok", "output": output}
            extension = {
                "robots": "robots.txt.audit",
                "llms": "llms.audit",
                "broken_links": "broken-links.audit",
                "internal_links": "internal-links.json",
                "social_meta": "social-meta.audit",
                "pagespeed_mobile": "pagespeed-mobile.json",
            }.get(key)
            if extension:
                (output_dir / extension).write_text(output)
        except subprocess.TimeoutExpired as error:
            result["commands"][key] = {
                "status": "timeout",
                "output": (error.stdout or b"").decode("utf-8", errors="replace")
                if isinstance(error.stdout, bytes)
                else (error.stdout or ""),
                "error": f"Timed out after {payload['timeout']} seconds.",
            }
        except subprocess.CalledProcessError as error:
            stderr = error.stderr or ""
            stdout = error.stdout or ""
            result["commands"][key] = {
                "status": "error",
                "output": stdout,
                "error": stderr,
            }

    result["summary"] = summarize_deep_audit(result)
    return result


def summarize_deep_audit(result: dict[str, Any]) -> dict[str, Any]:
    commands = result["commands"]
    summary = {
        "overall_score": None,
        "robots_ok": False,
        "llms_score": None,
        "broken_links": None,
        "internal_link_issues": None,
        "social_score": None,
        "pagespeed_error": None,
    }

    html_report = Path(result.get("html_report_path", ""))
    if html_report.exists():
        html = html_report.read_text(errors="replace")
        match = re.search(r"Overall Score[^0-9]+(\d{1,3})/100", html)
        if match:
            summary["overall_score"] = int(match.group(1))
    if summary["overall_score"] is None:
        html_report_output = commands.get("html_report", {}).get("output", "")
        match = re.search(r"Overall Score:\s*(\d{1,3})/100", html_report_output)
        if match:
            summary["overall_score"] = int(match.group(1))

    robots_output = commands.get("robots", {}).get("output", "")
    summary["robots_ok"] = "explicitly allowed" in robots_output

    llms_output = commands.get("llms", {}).get("output", "")
    llms_match = re.search(r"Quality Score:\s*(\d{1,3})/100", llms_output)
    if llms_match:
        summary["llms_score"] = int(llms_match.group(1))

    broken_output = commands.get("broken_links", {}).get("output", "")
    broken_match = re.search(r"Broken(?: Links)?:\s*(\d+)", broken_output)
    if broken_match:
        summary["broken_links"] = int(broken_match.group(1))

    internal_output = commands.get("internal_links", {}).get("output", "")
    try:
        internal_json = json.loads(internal_output) if internal_output else {}
        summary["internal_link_issues"] = len(internal_json.get("issues", []))
    except json.JSONDecodeError:
        pass

    social_output = commands.get("social_meta", {}).get("output", "")
    social_match = re.search(r"Score:\s*(\d{1,3})/100", social_output)
    if social_match:
        summary["social_score"] = int(social_match.group(1))

    pagespeed_output = commands.get("pagespeed_mobile", {}).get("output", "")
    if pagespeed_output:
        try:
            pagespeed_json = json.loads(pagespeed_output)
            summary["pagespeed_error"] = pagespeed_json.get("error")
        except json.JSONDecodeError:
            summary["pagespeed_error"] = "Pagespeed output was not valid JSON."

    return summary


def format_percent(value: float | int | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def format_float(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.{digits}f}"


def format_int(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return str(int(value))


def compute_funnel_rates(ga4: dict[str, Any]) -> list[str]:
    totals = ga4.get("event_totals", {}).get("14d", {})
    lines = []
    for left, right in zip(FUNNEL_EVENTS, FUNNEL_EVENTS[1:]):
        left_value = totals.get(left, 0)
        right_value = totals.get(right, 0)
        if left_value:
            rate = right_value / left_value
            lines.append(f"- `{left}` -> `{right}`: {right_value}/{left_value} ({format_percent(rate)})")
        else:
            lines.append(f"- `{left}` -> `{right}`: {right_value}/{left_value} (baseline unavailable)")
    return lines


def write_snapshot(report_date: str, snapshot: dict[str, Any]) -> Path:
    target_dir = DATA_DIR / report_date
    target_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = target_dir / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot_path


def report_path(report_date: str, *, deep: bool = False, latest: bool = False) -> Path:
    if latest and deep:
        return REPORTS_DIR / "latest-deep.md"
    if latest:
        return REPORTS_DIR / "latest.md"
    if deep:
        return REPORTS_DIR / f"{report_date}-deep.md"
    return REPORTS_DIR / f"{report_date}.md"


def write_markdown_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def render_growth_report(snapshot: dict[str, Any]) -> str:
    ga4 = snapshot["ga4"]
    gsc = snapshot["gsc"]
    checkout = snapshot["checkout"]
    git_state = snapshot["git"]
    self_review = snapshot["self_review"]
    deep_mode = snapshot["deep_mode"]

    top_pages_lines = []
    for page in ga4.get("top_pages_30d", [])[:8]:
        top_pages_lines.append(
            f"- `{page['pagePath']}`: {page['screenPageViews']} views, {page['sessions']} sessions, {page['totalUsers']} users"
        )
    if not top_pages_lines:
        top_pages_lines.append("- No GA4 page data was returned.")

    report_lines = [
        "# Pixera Growth Operator Run",
        "",
        f"Date: {snapshot['report_date']}",
        f"User locale time: `{snapshot['locale_now']}`",
        f"Repo: `{REPO_ROOT}`",
        f"Domain: `{snapshot['site_url']}`",
        "",
        "## Refresh Status",
        "",
        f"- GA4: `{ga4['status']}` on property `{ga4['property_id']}` with measurement ID `{snapshot['ga_measurement_id']}`.",
    ]

    if gsc.get("status") == "ok":
        report_lines.append(f"- Google Search Console: `ok` on `{gsc['site']}`.")
    else:
        report_lines.append(
            f"- Google Search Console: `{gsc.get('status', 'error')}`. {gsc.get('message', 'No accessible property was returned.')}"
        )

    if checkout.get("status") == "ok":
        report_lines.append(
            f"- Checkout analytics: `ok` with {checkout['orders_30d']} orders and ${checkout['revenue_usd_30d']:.2f} revenue in the last 30 days."
        )
    else:
        report_lines.append(
            f"- Checkout analytics: `{checkout.get('status', 'unavailable')}`. {checkout.get('message', 'No checkout analytics were available.')}"
        )

    report_lines.extend(
        [
            "",
            "## 14-Day Trend",
            "",
            f"- GSC impressions: {format_int(metric_from_snapshot(snapshot, ['gsc', 'totals_14d', 'impressions'], default=None)) if gsc.get('status') == 'ok' else 'unavailable'}",
            f"- GSC clicks: {format_int(metric_from_snapshot(snapshot, ['gsc', 'totals_14d', 'clicks'], default=None)) if gsc.get('status') == 'ok' else 'unavailable'}",
            f"- GSC CTR: {format_percent(metric_from_snapshot(snapshot, ['gsc', 'totals_14d', 'ctr'], default=None), 2) if gsc.get('status') == 'ok' else 'unavailable'}",
            f"- `open_guide`: {ga4['event_totals']['14d'].get('open_guide', 0)}",
            f"- `open_resource`: {ga4['event_totals']['14d'].get('open_resource', 0)}",
            f"- `view_pricing`: {ga4['event_totals']['14d'].get('view_pricing', 0)}",
            f"- `begin_checkout`: {ga4['event_totals']['14d'].get('begin_checkout', 0)}",
            f"- `download_installer`: {ga4['event_totals']['14d'].get('download_installer', 0)}",
            f"- `generate_lead`: {ga4['event_totals']['14d'].get('generate_lead', 0)}",
            "",
            "## Funnel Progression",
            "",
            "- Event ratios are directional only. The current GA4 setup tracks page and CTA events, not stitched user-level funnel sessions yet.",
        ]
    )
    report_lines.extend(compute_funnel_rates(ga4))

    report_lines.extend(
        [
            "",
            "## Self-Review",
            "",
        ]
    )
    if self_review["last_three_reports"]:
        report_lines.append("- Last stored snapshots:")
        for row in self_review["last_three_reports"]:
            report_lines.append(
                "  - "
                f"{row['run_date']}: clicks={format_int(row['gsc_clicks_14d'])}, "
                f"impressions={format_int(row['gsc_impressions_14d'])}, "
                f"CTR={format_percent(row['gsc_ctr_14d'], 2)}, "
                f"open_guide={format_int(row['open_guide_14d'])}, "
                f"begin_checkout={format_int(row['begin_checkout_14d'])}"
            )
    else:
        report_lines.append("- No prior machine-readable snapshots were available, so this run establishes the baseline for future 3-run comparisons.")

    if self_review["stagnation"]:
        report_lines.append(f"- Stagnation status: `yes`. {'; '.join(self_review['stagnation_reasons'])}")
    else:
        report_lines.append("- Stagnation status: `no confirmed 3-run flat/down pattern yet`.")

    report_lines.extend(
        [
            "",
            "## Traffic Concentration",
            "",
            f"- Homepage share of tracked page views over the last 30 days: {format_percent(ga4.get('homepage_concentration_30d', 0), 1)}",
            "- Top GA4 page paths in the last 30 days:",
        ]
    )
    report_lines.extend(top_pages_lines)

    report_lines.extend(
        [
            "",
            "## Actions Shipped In This Run",
            "",
        ]
    )
    if git_state["pages_shipped"]:
        for page in git_state["pages_shipped"]:
            report_lines.append(f"- `{page}`")
    else:
        report_lines.append("- No changed content pages were detected from git status at report time.")

    if git_state["crawl_files"]:
        report_lines.append("- Crawl-file changes: " + ", ".join(f"`{path}`" for path in git_state["crawl_files"]))
    else:
        report_lines.append("- Crawl-file changes: none detected in git status.")

    if git_state["analytics_files"]:
        report_lines.append(
            "- Funnel/instrumentation changes: " + ", ".join(f"`{path}`" for path in git_state["analytics_files"])
        )
    else:
        report_lines.append("- Funnel/instrumentation changes: none detected in git status.")

    report_lines.extend(
        [
            "",
            "## Strategy",
            "",
            f"- Deep audit status: `{'on' if deep_mode['enabled'] else 'off'}`.",
        ]
    )
    for reason in deep_mode["reasons"]:
        report_lines.append(f"- Deep-audit reason: {reason}")
    if snapshot.get("strategy_shift"):
        report_lines.append(f"- Strategy shift: {snapshot['strategy_shift']}")

    report_lines.extend(
        [
            "",
            "## Blockers",
            "",
        ]
    )
    if gsc.get("status") != "ok":
        report_lines.append("- Search Console refresh is blocked until this service account has access to a verified Search Console property.")
    if checkout.get("status") != "ok":
        report_lines.append("- Checkout revenue remains partially blind because Lemon Squeezy API credentials are not available in the environment.")
    if snapshot.get("deep_audit", {}).get("summary", {}).get("pagespeed_error"):
        report_lines.append(
            f"- PageSpeed evidence is incomplete for this run: {snapshot['deep_audit']['summary']['pagespeed_error']}"
        )

    report_lines.extend(
        [
            "",
            "## Next Bets",
            "",
            "1. Deploy the current content and crawl-file batch so GA4 can start distributing traffic beyond the homepage.",
            "2. Grant this service account Search Console access or verify the domain property so impressions, clicks, and CTR can be refreshed directly.",
            "3. Add Lemon Squeezy purchase tracking or API credentials so `begin_checkout` can be tied to actual revenue.",
        ]
    )

    if snapshot.get("proposed_upgrade"):
        report_lines.extend(
            [
                "",
                "## Human Approval Needed",
                "",
                f"- Proposed prompt/strategy upgrade: {snapshot['proposed_upgrade']}",
            ]
        )

    return "\n".join(report_lines)


def render_deep_report(snapshot: dict[str, Any]) -> str:
    deep_audit = snapshot.get("deep_audit", {})
    summary = deep_audit.get("summary", {})
    commands = deep_audit.get("commands", {})
    html_dashboard = deep_audit.get(
        "html_report_path",
        str(REPORTS_DIR / f"SEO-REPORT-{snapshot['report_date']}.html"),
    )

    lines = [
        "# Pixera Deep SEO Audit",
        "",
        f"Date: {snapshot['report_date']}",
        f"Scope: live domain audit for `{snapshot['site_url']}`",
        f"HTML dashboard: `{html_dashboard}`",
        f"Overall score: `{summary.get('overall_score', 'n/a')}/100`",
        "",
        "## Why Deep Analysis Ran",
        "",
    ]
    for reason in snapshot["deep_mode"]["reasons"]:
        lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "## What The Deep Audit Confirmed",
            "",
            f"- AI crawler management explicit: `{summary.get('robots_ok', False)}`",
            f"- `llms.txt` quality score: `{summary.get('llms_score', 'n/a')}/100`",
            f"- Broken links found: `{summary.get('broken_links', 'n/a')}`",
            f"- Internal-link issue count: `{summary.get('internal_link_issues', 'n/a')}`",
            f"- Social metadata score: `{summary.get('social_score', 'n/a')}/100`",
        ]
    )

    lines.extend(
        [
            "",
            "## Evidence",
            "",
        ]
    )
    for key, payload in commands.items():
        status = payload.get("status", "unknown")
        lines.append(f"- `{key}`: `{status}`")
        output = (payload.get("output") or payload.get("error") or "").strip()
        if output:
            preview = "\n".join(output.splitlines()[:10])
            lines.append("```text")
            lines.append(preview)
            lines.append("```")

    lines.extend(
        [
            "",
            "## Remaining Gaps",
            "",
        ]
    )
    if snapshot["gsc"].get("status") != "ok":
        lines.append("- Search Console is still blocked for this service account, so live query and CTR evidence remain incomplete.")
    if snapshot["checkout"].get("status") != "ok":
        lines.append("- Lemon Squeezy purchase analytics are still unavailable in this environment.")
    if summary.get("pagespeed_error"):
        lines.append(f"- PageSpeed API evidence is incomplete: {summary['pagespeed_error']}")

    lines.extend(
        [
            "",
            "## Recommended Next Bets",
            "",
            "1. Deploy the new App Store resource layer and privacy page so the live domain stops wasting existing demand on 404s.",
            "2. Restore Search Console visibility for this service account, then revisit CTR and impression deltas against the new pages.",
            "3. Close revenue attribution by wiring Lemon Squeezy purchase data into the same reporting loop.",
        ]
    )
    return "\n".join(lines)


def maybe_propose_upgrade(snapshot: dict[str, Any]) -> str | None:
    history = snapshot["self_review"]["last_three_reports"]
    stagnation = snapshot["self_review"]["stagnation"]
    if stagnation and len(history) >= 3:
        return (
            "Approve a prompt upgrade that explicitly prioritizes comparison pages against Snagit, Shottr, CleanShot X, "
            "and fast template/programmatic page expansion if two retrospectives in a row still fail to move clicks, "
            "impressions, or `open_guide`."
        )
    return None


def main() -> int:
    args = parse_args()
    report_now = today_in_timezone(args.locale_tz)
    report_date = report_now.date().isoformat()
    service_account = load_service_account(Path(args.service_account_key))
    if not service_account:
        raise SystemExit(f"Service account key not found: {args.service_account_key}")

    access_token = mint_google_access_token(
        service_account,
        scopes=[
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/webmasters.readonly",
        ],
    )

    git_state = collect_git_state()
    ga4 = collect_ga4(access_token, args.ga_property_id, args.locale_tz)
    gsc = collect_gsc(access_token, args.gsc_sites or DEFAULT_GSC_SITES, args.locale_tz)
    checkout = collect_checkout(args.locale_tz)

    snapshot = {
        "report_date": report_date,
        "locale_tz": args.locale_tz,
        "locale_now": report_now.isoformat(),
        "site_url": args.site_url,
        "ga_property_id": args.ga_property_id,
        "ga_measurement_id": args.ga_measurement_id,
        "ga4": ga4,
        "gsc": gsc,
        "checkout": checkout,
        "git": git_state,
        "strategy_shift": args.strategy_shift.strip(),
    }

    history = [
        snapshot_item
        for snapshot_item in load_snapshot_history()
        if snapshot_item.get("report_date") != report_date
    ]
    self_review = compare_snapshots(history, snapshot)
    snapshot["self_review"] = self_review

    deep_enabled, deep_reasons = decide_deep_mode(
        locale_tz=args.locale_tz,
        git_state=git_state,
        ga4=ga4,
        gsc=gsc,
        self_review=self_review,
        force_deep=args.force_deep,
        major_batch=args.major_batch,
        technical_conflict=args.technical_conflict,
    )
    snapshot["deep_mode"] = {"enabled": deep_enabled, "reasons": deep_reasons}

    if deep_enabled and args.run_live_deep_audit:
        snapshot["deep_audit"] = run_live_deep_audit(args.site_url, report_date)
    else:
        snapshot["deep_audit"] = {"status": "skipped", "commands": {}, "summary": {}}

    snapshot["proposed_upgrade"] = maybe_propose_upgrade(snapshot)

    snapshot_path = write_snapshot(report_date, snapshot)

    growth_report = render_growth_report(snapshot)
    write_markdown_report(report_path(report_date), growth_report)
    write_markdown_report(report_path(report_date, latest=True), growth_report)

    if deep_enabled:
        deep_report = render_deep_report(snapshot)
        write_markdown_report(report_path(report_date, deep=True), deep_report)
        write_markdown_report(report_path(report_date, deep=True, latest=True), deep_report)

    print(
        json.dumps(
            {
                "report_date": report_date,
                "snapshot": str(snapshot_path),
                "growth_report": str(report_path(report_date)),
                "latest_report": str(report_path(report_date, latest=True)),
                "deep_enabled": deep_enabled,
                "deep_report": str(report_path(report_date, deep=True)) if deep_enabled else None,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
