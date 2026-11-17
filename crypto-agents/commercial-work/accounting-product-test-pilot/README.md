# B1/B2 accounting-software testing — original evidence-first sample

**Portfolio sample prepared 17 November 2026.** This is an independent reproducible rubric, **not** a completed 36-platform test, contract, original client's proprietary rubric, paid invoice, screenshot evidence or endorsement from Forbes Advisor.

## Relevant verified buyer brief

[Worldwide remote accounting software product tester — $1,500 fixed](https://www.upwork.com/freelance-jobs/apply/Freelance-Product-Tester-Accounting-Software_~022120444039866237398/). Public listing describes 36 accounting apps, tested over about two weeks, following five steps per app: company setup/dashboard; four sales invoices and full/partial payment recording; three expense transactions; CSV bank import and reconciling mismatched lines; export a P&L report. Time each task, score 1–5 using the **client-provided** rubric, record failure points and high-quality evidence screenshots labeled with app, step, and date. The listing says the client reimburses software plan charges. **Never personally prepay subscriptions without a clear funded contract and reimbursement terms.** Payment and application follow Upwork's platform rules; do not move them directly to crypto wallets in breach of the marketplace contract.

## Original work sample and acceptance evidence

- [Standard library CSV rubric generator and validator](rubric.py)
- [Ten synthetic regression tests](test_rubric.py)
- [Verified GitHub Actions test workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/b-world-revenue-command.yml)

Generate a truly blank **36 providers × 5 tasks = 180 task rows**:

```sh
python rubric.py init --providers 36 --out accounting_36_platform_testing.csv
python rubric.py validate accounting_36_platform_testing.csv
python -m unittest -q test_rubric.py
```

No provider is marked tested, scored, approved or paid by initialization. The following fields are included in every task row: provider, task number, task name, date, elapsed minutes, score 1–5, status, expected steps, observed behavior, labeled screenshot reference, friction/issues and synthetic-data classification.

**Completion safeguard:** A task marked `COMPLETED` cannot pass validation without an actual test date, execution time, score, factual notes and screenshot reference. The validator rejects missing tasks, improper ratings, missing evidence and duplicate/invalid provider definitions. It does not independently confirm screenshot authenticity or real software access; these remain human review responsibilities.

**Planned paid delivery process:** Obtain client's exact 36 software names, credentials or approved signup route, client-owned test dataset and original scoring rubric through the authenticated Upwork project. Run platform tasks with fictional company records only. Keep original screenshot files and a clear time/issue log; export one completed template per agreed provider set plus a consolidated cross-platform comparison, following the client's real template. Do not claim the provider has already been tested.

## Proposal draft, ready for authorized Upwork submission

> Hello, I can follow your 36-platform bookkeeping-software testing protocol with a consistent, evidence-based rubric. I'm comfortable with invoices and partial receipts, expense recording, CSV bank reconciliation and generating P&L reports. To demonstrate how I control consistency, I've built a Python-standard-library 180-task tracking template, including task timing, 1–5 scoring, dated screenshot references and validation checks: https://github.com/kwesigaamon8-web/Amon-Kwesiga/tree/main/crypto-agents/commercial-work/accounting-product-test-pilot
>
> I would use your own provided test-company data and scoring rubric rather than invent criteria, and test each provider in the agreed sequence. I can deliver task-by-task screenshots, precise friction notes, validated scores and a comparative summary. Before agreeing to the fixed project, please confirm the platform list, trial/plan costs and reimbursement arrangement, required screenshot format, and whether account registrations need to be owned by you.

**Do not submit this through email or a direct Bitcoin request.** The only authenticated commercial route for this listing is a legitimate Upwork application. The current ChatGPT connection cannot file that application or claim the user has won this $1,500 job.

## B1/B2 wallet policy

Owner wallets are **INBOUND RECEIVING ONLY**. No signing, mining spend, swaps, transfers, deposits or withdrawals; verify network/token compatibility before any legitimate independently contracted direct-service settlement. This Upwork job is a **fiat-platform offer**, not an authorized direct BTC payout.

