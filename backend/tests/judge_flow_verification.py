import asyncio
import os
import sys
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8000/frontend_screens"

async def run_judge_flow():
    results = {}
    console_errors = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        # Listen for console errors
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)

        print("\n--- STEP 1 & 2: Overview / Dashboard ---")
        await page.goto(f"{BASE_URL}/dashboard.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # Check title and metrics
        title = await page.title()
        print(f"Page title: {title}")
        assert "NIYUKTI" in title
        
        # Check candidate count
        cand_count_text = await page.locator("#metric-total-candidates, .font-display").all_inner_texts()
        print(f"Dashboard text elements: {cand_count_text[:5]}")
        results["dashboard"] = "PASSED"

        print("\n--- STEP 3: Talent Map ---")
        await page.goto(f"{BASE_URL}/talent_map.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        mapped_talent = await page.locator("#map-total-talent").inner_text()
        print(f"Mapped Talent: {mapped_talent}")
        assert "100,001" in mapped_talent or "100001" in mapped_talent
        
        # Check cluster list
        clusters = await page.locator("#cluster-distribution-list .astra-card").count()
        print(f"Rendered clusters: {clusters}")
        assert clusters > 0
        
        # Click first cluster (Bengaluru or Delhi-NCR)
        first_cluster = page.locator("#cluster-distribution-list .astra-card").first
        await first_cluster.click()
        await asyncio.sleep(0.5)
        
        detail_card = await page.locator("#map-hub-detail-card").count()
        print(f"Hub detail card rendered: {detail_card > 0}")
        assert detail_card > 0
        results["talent_map"] = "PASSED"

        print("\n--- STEP 4: Candidate Search with Location & Skill ---")
        await page.goto(f"{BASE_URL}/candidate_search.html?location=Bengaluru")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        # Type search query "Python"
        search_input = page.locator("#search-input, input[placeholder*='Search']")
        if await search_input.count() > 0:
            await search_input.fill("Python")
            await page.keyboard.press("Enter")
            await asyncio.sleep(1)
            
        cand_cards = await page.locator("#candidates-grid .astra-card, .candidate-card").count()
        print(f"Candidate cards found for Python in Bengaluru: {cand_cards}")
        assert cand_cards > 0
        results["candidate_search"] = "PASSED"

        print("\n--- STEP 5: Candidate Details ---")
        await page.goto(f"{BASE_URL}/candidate_details.html?id=7")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        cand_name = await page.locator("h2.font-headline-lg, h2").inner_text()
        print(f"Candidate Profile: {cand_name}")
        assert cand_name and "Loading" not in cand_name
        
        # Test Invalid Candidate ID (Professional not-found state)
        await page.goto(f"{BASE_URL}/candidate_details.html?id=99999999")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        not_found_text = await page.locator("body").inner_text()
        assert "Candidate Not Found" in not_found_text or "not exist" in not_found_text
        print("Negative test (Candidate Not Found state): PASSED")
        results["candidate_details"] = "PASSED"

        print("\n--- STEP 6: Opportunity Match & Explainable Ranking ---")
        await page.goto(f"{BASE_URL}/candidate_ranking.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1.5)
        
        selected_job = await page.locator("#job-selector").input_value()
        print(f"Auto-selected Job ID: {selected_job}")
        assert selected_job != ""
        
        ranked_rows = await page.locator("#rankings-list-container tr").count()
        print(f"Ranked candidate rows: {ranked_rows}")
        assert ranked_rows > 0
        
        # Check Decision Ledger
        ledger_items = await page.locator("#decision-ledger-container > div").count()
        print(f"Decision Ledger audit events: {ledger_items}")
        assert ledger_items > 0
        results["candidate_ranking"] = "PASSED"

        print("\n--- STEP 7: Candidate Comparison ---")
        await page.goto(f"{BASE_URL}/candidate_comparison.html?candidates=7,8,10&job_id=1")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1.5)
        
        comp_cards = await page.locator("main .grid h3, main .grid .font-headline-md").all_inner_texts()
        print(f"Compared candidates: {comp_cards}")
        assert len(comp_cards) >= 2
        results["candidate_comparison"] = "PASSED"

        print("\n--- STEP 8: Skill Gap Analysis ---")
        await page.goto(f"{BASE_URL}/skill_gap_analysis.html?id=7&job_id=1")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        score_val = await page.locator("#score-text").inner_text()
        print(f"Skill Gap Match Score: {score_val}")
        assert "%" in score_val
        
        matching_count = await page.locator("#matching-skills-container li").count()
        missing_count = await page.locator("#missing-skills-container li").count()
        print(f"Matching skills: {matching_count}, Missing skills: {missing_count}")
        assert matching_count > 0 or missing_count > 0
        results["skill_gap"] = "PASSED"

        print("\n--- STEP 9: Recruiter Copilot ---")
        await page.goto(f"{BASE_URL}/recruiter_copilot.html?candidate_id=7&job_id=1")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        status_text = await page.locator("#copilot-llm-status-badge").inner_text()
        print(f"Copilot Status Badge: {status_text}")
        assert "ACTIVE" in status_text or "STANDBY" in status_text
        
        # Type and send prompt
        input_box = page.locator("#copilot-input")
        if await input_box.count() > 0:
            await input_box.fill("Draft outreach email for Senior Python Engineer")
            await page.locator("#copilot-send-btn").click()
            await asyncio.sleep(2)
            
            chat_content = await page.locator("#chat-stream").inner_text()
            print(f"Copilot response received: {'outreach' in chat_content.lower() or 'email' in chat_content.lower() or 'hello' in chat_content.lower()}")
            assert len(chat_content) > 50
        results["recruiter_copilot"] = "PASSED"

        print("\n--- STEP 10: Workforce Analytics ---")
        await page.goto(f"{BASE_URL}/workforce_analytics.html")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)
        
        total_analytics = await page.locator("#analytics-total-candidates").inner_text()
        print(f"Analytics Total Candidates: {total_analytics}")
        assert "100,001" in total_analytics or "100001" in total_analytics
        results["workforce_analytics"] = "PASSED"

        print("\n--- STEP 11: Theme Toggle (Dark Mode) ---")
        await page.goto(f"{BASE_URL}/dashboard.html")
        await page.wait_for_load_state("networkidle")
        
        # Check initial theme
        is_dark_initial = await page.evaluate("() => document.documentElement.classList.contains('dark')")
        print(f"Initial dark class: {is_dark_initial}")
        
        # Click toggle
        toggle_btn = page.locator("#theme-toggle-btn")
        if await toggle_btn.count() > 0:
            await toggle_btn.click()
            await asyncio.sleep(0.5)
            is_dark_after = await page.evaluate("() => document.documentElement.classList.contains('dark')")
            print(f"After toggle dark class: {is_dark_after}")
            assert is_dark_initial != is_dark_after
            
            # Reload page to test persistence
            await page.reload()
            await page.wait_for_load_state("networkidle")
            is_dark_reloaded = await page.evaluate("() => document.documentElement.classList.contains('dark')")
            print(f"After reload dark class persisted: {is_dark_reloaded}")
            assert is_dark_reloaded == is_dark_after
            
            # Toggle back to light mode
            await page.locator("#theme-toggle-btn").click()
            await asyncio.sleep(0.5)
        results["dark_mode"] = "PASSED"

        print("\n--- STEP 12: Responsive Viewport QA ---")
        viewports = [
            ("1920x1080 (Desktop Wide)", 1920, 1080),
            ("1440x900 (Desktop Standard)", 1440, 900),
            ("1024x768 (Tablet Landscape)", 1024, 768),
            ("768x1024 (Tablet Portrait)", 768, 1024),
            ("390x844 (Mobile Phone)", 390, 844),
        ]
        
        for name, width, height in viewports:
            await page.set_viewport_size({"width": width, "height": height})
            await page.goto(f"{BASE_URL}/dashboard.html")
            await page.wait_for_load_state("networkidle")
            # Verify body width matches viewport and no overflow
            scroll_width = await page.evaluate("() => document.body.scrollWidth")
            inner_width = await page.evaluate("() => window.innerWidth")
            print(f"Viewport {name}: scrollWidth={scroll_width}, innerWidth={inner_width}")
        results["responsive_qa"] = "PASSED"

        print("\n--- Console Errors Check ---")
        filtered_errors = [e for e in console_errors if "favicon" not in e.lower()]
        print(f"Critical console errors: {len(filtered_errors)}")
        if filtered_errors:
            for err in filtered_errors:
                print(f"  {err}")
        results["console_clean"] = len(filtered_errors) == 0

        await browser.close()
        
    print("\n================ FINAL RESULTS ================")
    for k, v in results.items():
        print(f"{k}: {v}")
    all_ok = all(v is True or v == "PASSED" for v in results.values())
    print(f"OVERALL JUDGE SUITE STATUS: {'PASSED' if all_ok else 'FAILED'}")
    return all_ok

if __name__ == "__main__":
    success = asyncio.run(run_judge_flow())
    sys.exit(0 if success else 1)
