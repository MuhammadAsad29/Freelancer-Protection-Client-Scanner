from engine import LayaEngine

# (job text, expected trap type, expected danger score band as a range)
TEST_JOBS = {
    "Case 1: Unrealistic Budget / Sweatshop Trap": (
        "Need full-stack Uber clone app with AI chat and payment gateway. "
        "Must be completed in 3 days. Fixed budget $30. "
        "You must be available on Skype 16 hours a day for updates. "
        "Do not apply if you cannot deliver this weekend.",
        "unrealistic_budget_sweatshop",
        (3, 5),
    ),
    "Case 2: Off-Platform Scam Trap": (
        "Easy data entry and copy paste job! We pay $45 per hour! "
        "Immediate hiring for 10 freelancers. Do not message here on Upwork. "
        "Directly contact our hiring manager on Telegram: @hr_recruiter_crypto.",
        "telegram_crypto_scam",
        (4, 5),
    ),
    "Case 3: Unpaid Sample Demand Trap": (
        "We need a custom landing page design for our new startup. "
        "Before we hire anyone, send us 3 fully working sample designs "
        "for our evaluation. We will only pay after the contract is signed.",
        "unpaid_sample_demand",
        (2, 4),
    ),
    "Case 4: Nightmare Micromanager Trap": (
        "Looking for a WordPress developer. You must be available 24/7 on WhatsApp "
        "for updates. Daily standup call at 6am, every day, no exceptions. "
        "I will message you at 3am with new feature requests.",
        "nightmare_micromanager",
        (3, 5),
    ),
    "Case 5: Fair Job, Modest Budget": (
        "Need a simple Python script to rename files in a folder. "
        "Budget is $80 fixed for about 2 hours of work. "
        "Please apply with your portfolio and we will chat about the details.",
        "legitimate_fair_client",
        (1, 3),
    ),
    "Case 6: Clean & Fair Job": (
        "We are looking for a Python developer to build a polite web scraper "
        "for public e-commerce pricing data. Budget is $40/hour with clear milestones. "
        "Flexible hours and friendly team. Code must follow clean PEP8 standards.",
        "legitimate_fair_client",
        (1, 2),
    ),
}


def run_tests():
    print("=" * 60)
    print("  FREELANCER PROTECTION RADAR - TEST SUITE")
    print("=" * 60)

    engine = LayaEngine()

    passed = failed = 0

    for title, (job_text, expected_trap, score_range) in TEST_JOBS.items():
        print(f"\n[Testing] {title}")
        print("-" * 50)

        result = engine.analyze_full_job(job_text)

        print(f"• Is Toxic:       {result['is_toxic']}")
        print(f"• Danger Score:   {result['toxicity_score']} / 5 ({result['danger_band']})")
        print(f"• Identified Trap:{result['trap_type']}")
        print(f"• Confidence:     {result['confidence'] * 100:.1f}%")
        print(f"• Toxic Prob:     {result['toxicity_probability'] * 100:.1f}%")
        print(f"• Radar Advice:   {result['reason']}")

        trap_ok = result["trap_type"] == expected_trap
        score_ok = score_range[0] <= result["toxicity_score"] <= score_range[1]
        if trap_ok and score_ok:
            passed += 1
            print("• Result:         PASS")
        else:
            failed += 1
            print(
                f"• Result:         FAIL "
                f"(trap {result['trap_type']!r} != {expected_trap!r}"
                f"{'' if trap_ok else ' | '}"
                f"score {result['toxicity_score']} outside {score_range})"
            )

    print("\n" + "=" * 60)
    print(f"  {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    run_tests()
