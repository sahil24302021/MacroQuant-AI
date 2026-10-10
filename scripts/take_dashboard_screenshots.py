"""Capture genuine, high-resolution screenshots of the live Streamlit dashboard.

Iterates through all 5 tabs using Playwright with system Google Chrome:
1. Research Overview
2. Live Intelligence (Real Data)
3. Macro Events (Demo)
4. Strategy Lab
5. Model Evaluation
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TABS = [
    ("01_research_overview.png", "Research Overview"),
    ("02_live_intelligence.png", "Live Intelligence (Real Data)"),
    ("03_macro_events.png", "Macro Events (Demo)"),
    ("04_strategy_lab.png", "Strategy Lab"),
    ("05_model_evaluation.png", "Model Evaluation"),
]


def main():
    print("Launching Playwright with Chrome...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 960}, device_scale_factor=2)
        page = context.new_page()

        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector('[role="tab"]', timeout=15000)
        page.wait_for_timeout(3000)

        # Inject subtle CSS to hide floating helper notifications
        page.add_style_tag(content="""
            div[data-testid="stToolbar"] { display: none !important; }
            [class*="viewerBadge"] { display: none !important; }
            div:has(> button:has-text("Don't show again")) { display: none !important; }
        """)

        tab_buttons = page.locator('[role="tab"]')
        count = tab_buttons.count()
        print(f"Detected {count} tab buttons.")

        for idx, (filename, label) in enumerate(TABS):
            print(f"[{idx+1}/5] Selecting tab '{label}'...")
            tab_buttons.nth(idx).click()
            # Allow charts, dataframes and animations to settle
            page.wait_for_timeout(2500)

            out_path = OUTPUT_DIR / filename
            page.screenshot(path=str(out_path), full_page=False)
            print(f"  -> Saved {out_path.name} ({out_path.stat().st_size:,} bytes)")

        browser.close()
    print("SUCCESS: All genuine dashboard screenshots captured.")


if __name__ == "__main__":
    main()
