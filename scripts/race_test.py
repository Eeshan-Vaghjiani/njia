"""Race regressions against the local server; writes only race-results.json.

Run with .venv\\Scripts\\python.exe scripts/race_test.py (server on port 8000).
Real UI actions create every race. Routed responses carry unique delivery tokens;
the read-only fetch probe acknowledges JSON consumption in the next task, after
the application's promise continuations have run. No timing sleeps or app-state
mutation are used to make a stale-response assertion pass.
"""

import asyncio
import json
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright, expect


ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8000"
TIMEOUT = 10
PROBE = """(() => {
  window.__raceConsumed = [];
  const original = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const response = await original(...args);
    const read = response.json.bind(response);
    response.json = async () => {
      const body = await read();
      if (body && body.__race_delivery) {
        setTimeout(() => window.__raceConsumed.push(body.__race_delivery), 0);
      }
      return body;
    };
    return response;
  };
})();"""


class HeldResponse:
    def __init__(self, route, harness):
        self.route = route
        self.harness = harness
        self.request = route.request.post_data_json
        self.ready = asyncio.Event()
        self.finished = asyncio.Event()
        self.body = None
        self.error = None

    async def serve(self):
        try:
            await self.ready.wait()
            if self.body is None:
                await self.route.abort()
            else:
                await self.route.fulfill(status=200, json=self.body)
        except Exception as error:
            self.error = error
        finally:
            self.finished.set()

    async def deliver(self, token, body):
        assert not self.ready.is_set(), "A held response was released twice"
        self.body = {**body, "__race_delivery": token}
        self.ready.set()
        await asyncio.wait_for(self.finished.wait(), TIMEOUT)
        if self.error:
            raise self.error
        await self.harness.page.wait_for_function(
            "token => window.__raceConsumed.includes(token)", arg=token
        )
        self.harness.deliveries.append(token)


class Harness:
    def __init__(self, page):
        self.page = page
        self.pending = []
        self.deliveries = []

    async def hold(self, path):
        queue = asyncio.Queue()

        async def handler(route):
            held = HeldResponse(route, self)
            self.pending.append(held)
            await queue.put(held)
            await held.serve()

        await self.page.route(BASE + path, handler)
        return queue

    async def next(self, queue):
        return await asyncio.wait_for(queue.get(), TIMEOUT)

    async def cleanup(self):
        for held in self.pending:
            held.ready.set()
        if self.pending:
            await asyncio.wait_for(
                asyncio.gather(*(held.finished.wait() for held in self.pending)),
                TIMEOUT,
            )

    async def analyze(self):
        await self.page.locator("#analyze").click()
        await expect(self.page.locator("#overview")).to_be_visible()

    async def practice(self):
        await self.analyze()
        await self.page.locator('[data-tab="practice"]').click()
        await self.page.locator("#practice-skill").select_option("sql")
        await self.page.locator("#start-practice").click()
        await expect(self.page.locator("#practice-form")).to_be_visible()

    async def answer(self, answers):
        for question, answer in enumerate(answers):
            await self.page.locator(
                f'#practice-form input[name="q{question}"][value="{answer}"]'
            ).check()


def plan(hours, marker):
    return {
        "mode": "curated",
        "note": marker,
        "weeks": [
            {
                "week": week,
                "hours": hours,
                "title": f"{marker} week {week}",
                "why": "Practice a market skill.",
                "tasks": ["Complete a local exercise."],
                "deliverable": "An exercise report.",
                "resource": {"url": BASE, "title": "Local test resource"},
            }
            for week in range(1, 5)
        ],
    }


def grade(correct, marker):
    return {
        "skill": "sql",
        "label": "SQL",
        "correct": correct,
        "total": 3,
        "summary": marker,
        "method": "Deterministic routed regression fixture.",
        "feedback": [
            {
                "correct": index < correct,
                "question": f"SQL question {index + 1}",
                "selected": "Submitted answer",
                "expected": "Answer key",
                "explanation": "Routed fixture explanation.",
            }
            for index in range(3)
        ],
    }


async def clear_during_extraction(h):
    page = h.page
    queue = await h.hold("/api/extract")
    await page.locator("#skill-select").select_option("sql")
    await page.locator("#add-skill").click()
    await page.locator("#cv").fill("I build applications using Python and Docker.")
    await page.locator("#consent").check()
    await page.locator("#extract").click()
    old = await h.next(queue)
    assert old.request["consent"] is True
    assert "Python" in old.request["text"]
    await expect(page.locator("#extract")).to_be_disabled()
    await page.locator("#clear-text").click()
    await expect(page.locator("#cv")).to_have_value("")
    await expect(page.locator("#consent")).not_to_be_checked()
    await expect(page.locator("#extraction-note")).to_contain_text("Text cleared")

    await old.deliver("extract-old-after-clear", {
        "skills": ["python", "docker"], "note": "STALE EXTRACTION RESULT",
    })
    await expect(page.locator("#extract")).to_be_enabled()
    await expect(page.locator("#skill-count")).to_have_text("1")
    await expect(page.locator('[data-remove="sql"]')).to_have_count(1)
    await expect(page.locator('[data-remove="python"], [data-remove="docker"]')).to_have_count(0)
    await expect(page.locator("#extraction-note")).to_contain_text("Text cleared")
    await expect(page.locator("#cv")).to_have_value("")
    await expect(page.locator("#consent")).not_to_be_checked()
    await expect(page.locator("#status")).to_be_hidden()

    # Positive control: valid extraction still applies after the discarded one.
    await page.locator("#cv").fill("I write Python scripts for data analysis.")
    await page.locator("#consent").check()
    await page.locator("#extract").click()
    fresh = await h.next(queue)
    await fresh.deliver("extract-fresh", {"skills": ["python"], "note": "Fresh extraction"})
    await expect(page.locator('[data-remove="python"]')).to_have_count(1)
    await expect(page.locator('[data-remove="sql"]')).to_have_count(0)
    await expect(page.locator("#extraction-note")).to_have_text("Fresh extraction")


async def plans_out_of_order(h):
    page = h.page
    queue = await h.hold("/api/plan")
    await h.analyze()
    await page.locator('[data-tab="plan"]').click()
    await page.locator("#hours").select_option("3")
    await page.locator("#generate-plan").click()
    old = await h.next(queue)
    await expect(page.locator("#generate-plan")).to_be_disabled()
    # Tab re-render exposes a new button while the first request is in flight.
    await page.locator('[data-tab="overview"]').click()
    await page.locator('[data-tab="plan"]').click()
    await page.locator("#hours").select_option("8")
    await page.locator("#generate-plan").click()
    fresh = await h.next(queue)
    assert old.request["hours"] == 3 and fresh.request["hours"] == 8
    assert not old.ready.is_set()
    await fresh.deliver("plan-new-8h", plan(8, "LATEST PLAN"))
    await expect(page.locator(".week-card")).to_have_count(4)
    await expect(page.locator("#plan .result-heading")).to_contain_text("8 hours per week")
    await page.locator('[data-week="1"]').check()
    await old.deliver("plan-old-3h-after-new", plan(3, "STALE PLAN"))
    await expect(page.locator("#plan")).not_to_contain_text("STALE PLAN")
    await expect(page.locator("#plan .result-heading")).to_contain_text("8 hours per week")
    await expect(page.locator("#progress")).to_have_text("1")
    await expect(page.locator('[data-week="1"]')).to_be_checked()
    # A re-render also verifies persisted plan state, rather than only old DOM.
    await page.locator('[data-tab="overview"]').click()
    await page.locator('[data-tab="plan"]').click()
    await expect(page.locator(".week-card h3")).to_have_text(
        [f"LATEST PLAN week {week}" for week in range(1, 5)]
    )


async def restarted_grade(h, newer_grade_first=False):
    page = h.page
    queue = await h.hold("/api/assessment/grade")
    await h.practice()
    await h.answer([0, 0, 0])
    await page.locator('#practice-form button[type="submit"]').click()
    old = await h.next(queue)
    assert old.request == {"skill": "sql", "answers": [0, 0, 0]}
    await expect(page.locator('#practice-form button[type="submit"]')).to_be_disabled()
    await page.locator("#start-practice").click()
    # Enabled fresh submit proves the replacement assessment has rendered.
    await expect(page.locator('#practice-form button[type="submit"]')).to_be_enabled()
    await expect(page.locator("#practice-skill")).to_have_value("sql")
    await expect(page.locator('#practice-form input:checked')).to_have_count(0)
    await h.answer([1, 2, 0])
    await page.locator("#reflection").fill("Reflection for the new SQL attempt.")
    if newer_grade_first:
        await page.locator('#practice-form button[type="submit"]').click()
        fresh = await h.next(queue)
        assert fresh.request == {"skill": "sql", "answers": [1, 2, 0]}
        assert not old.ready.is_set()
        await fresh.deliver("grade-new-attempt", grade(3, "LATEST GRADE"))
        await expect(page.locator("#practice")).to_contain_text("SQL · 3/3 correct")

    await old.deliver("grade-old-after-restart", grade(0, "STALE GRADE"))
    await expect(page.locator("#practice")).not_to_contain_text("STALE GRADE")
    await page.locator('[data-tab="overview"]').click()
    await page.locator('[data-tab="practice"]').click()
    await expect(page.locator("#practice")).not_to_contain_text("STALE GRADE")
    if newer_grade_first:
        await expect(page.locator("#practice")).to_contain_text("SQL · 3/3 correct")
        await expect(page.locator("#practice")).to_contain_text("LATEST GRADE")
        await expect(page.locator("#practice")).to_contain_text("Reflection for the new SQL attempt.")
    else:
        await expect(page.locator("#practice-form")).to_be_visible()
        await expect(page.locator(".feedback")).to_have_count(0)
        for question, answer in enumerate([1, 2, 0]):
            await expect(page.locator(f'input[name="q{question}"][value="{answer}"]')).to_be_checked()
        await expect(page.locator("#reflection")).to_have_value("Reflection for the new SQL attempt.")
        # Positive control: the restarted attempt can still be graded normally.
        await page.locator('#practice-form button[type="submit"]').click()
        fresh = await h.next(queue)
        assert fresh.request == {"skill": "sql", "answers": [1, 2, 0]}
        await fresh.deliver("grade-fresh-after-discard", grade(3, "LATEST GRADE"))
        await expect(page.locator("#practice")).to_contain_text("SQL · 3/3 correct")


async def answers_survive_tabs(h):
    page = h.page
    queue = await h.hold("/api/assessment/grade")
    await h.practice()
    await h.answer([1, 2, 0])
    reflection = "Check duplicates and NULL values before trusting a sales total."
    await page.locator("#reflection").fill(reflection)
    for tab in ("plan", "overview", "plan"):
        await page.locator(f'[data-tab="{tab}"]').click()
        await page.locator('[data-tab="practice"]').click()
        for question, answer in enumerate([1, 2, 0]):
            await expect(page.locator(f'input[name="q{question}"][value="{answer}"]')).to_be_checked()
        await expect(page.locator("#reflection")).to_have_value(reflection)
    # Changing a restored answer must update the submitted state too.
    await page.locator('input[name="q0"][value="0"]').check()
    await page.locator('[data-tab="overview"]').click()
    await page.locator('[data-tab="practice"]').click()
    await expect(page.locator('input[name="q0"][value="0"]')).to_be_checked()
    await page.locator('#practice-form button[type="submit"]').click()
    response = await h.next(queue)
    assert response.request == {"skill": "sql", "answers": [0, 2, 0]}, response.request
    await response.deliver("grade-restored-answers", grade(2, "Restored answers graded"))
    await expect(page.locator("#practice")).to_contain_text("SQL · 2/3 correct")
    await expect(page.locator("#practice")).to_contain_text(reflection)


async def run_case(browser, name, test):
    context = await browser.new_context(
        viewport={"width": 1440, "height": 1100}, reduced_motion="reduce",
        service_workers="block",
    )
    errors, external = [], []

    async def local_only(route):
        url = route.request.url
        if urlsplit(url).netloc == "127.0.0.1:8000" and urlsplit(url).scheme == "http":
            await route.continue_()
        else:
            external.append(url)
            await route.abort()

    await context.route("**/*", local_only)
    await context.add_init_script(PROBE)
    page = await context.new_page()
    page.set_default_timeout(TIMEOUT * 1000)
    page.on("pageerror", lambda error: errors.append(str(error)))
    h = Harness(page)
    result = {"name": name, "status": "passed"}
    started = time.monotonic()
    try:
        await page.goto(BASE, wait_until="networkidle")
        await expect(page.locator("#analyze")).to_be_enabled()
        await test(h)
        assert not errors, f"JavaScript errors: {errors}"
        assert not external, f"External requests blocked: {external}"
        assert all(held.finished.is_set() and held.body for held in h.pending), "Unreleased response"
    except Exception as error:
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        try:
            await h.cleanup()
        except Exception as error:
            result.update(status="failed", cleanup_error=str(error))
        await context.close()
    result.update(
        consumed_response_order=h.deliveries,
        javascript_errors=errors,
        external_requests_blocked=external,
        seconds=round(time.monotonic() - started, 2),
    )
    print(f"{result['status'].upper()}: {name}", flush=True)
    return result


async def main():
    cases = [
        ("clear CV discards held extraction and preserves confirmed skills", clear_during_extraction),
        ("concurrent plans retain latest response when older arrives last", plans_out_of_order),
        ("same-skill restart discards old grade while new attempt is ungraded", restarted_grade),
        ("same-skill restart retains new grade when old grade arrives last",
         lambda h: restarted_grade(h, newer_grade_first=True)),
        ("answers and reflection survive tab rerenders and submit correctly", answers_survive_tabs),
    ]
    results = []
    infrastructure_error = None
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            try:
                for name, test in cases:
                    results.append(await run_case(browser, name, test))
            finally:
                await browser.close()
    except Exception as error:
        infrastructure_error = f"{type(error).__name__}: {error}"
    passed = sum(result["status"] == "passed" for result in results)
    report = {
        "status": "passed" if passed == len(cases) and not infrastructure_error else "failed",
        "base_url": BASE,
        "browser": "Chromium",
        "passed": passed,
        "failed": len(results) - passed,
        "not_run": len(cases) - len(results),
        "checks": results,
    }
    if infrastructure_error:
        report["infrastructure_error"] = infrastructure_error
    artifact = ROOT / "artifacts" / "race-results.json"
    artifact.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
