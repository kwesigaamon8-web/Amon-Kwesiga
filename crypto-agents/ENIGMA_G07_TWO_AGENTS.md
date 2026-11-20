# Enigma G07 — Seventh Google account, two independent B1/B2-style agents

**Scope:** One Google account only, alias `G07`, the seventh connected Gmail account. No other Gmail connection has been linked or accessed by GitHub. Names are proposed *Moltbook* identities, not registered external accounts.

| Worker | Company | Proposed Moltbook handle | Separate AI runtime |
|---|---|---|---|
| ENIGMA-G07-A | Enigma Bitcoin Receipt Verification | EnigmaG07Scout | GitHub Actions agent=A matrix worker |
| ENIGMA-G07-B | Enigma Mining and Energy Research | EnigmaG07Developer | GitHub Actions agent=B matrix worker |

Both have: independent model invocation, source checks, separate JSON evidence artifact, own proposed external account credential slot, same owner with separate company mission, software source catalogue and optional owner BTC payment reference. B1 `transferexperiment` and B2 `BountyScoutAI` stay separate and untouched.

**Run evidence:** https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g07-pair.yml

## Moltbook account status / claiming steps

The Moltbook site instructs actual AI agents to register via `POST https://www.moltbook.com/api/v1/agents/register` with `name` and `description`, which returns a **secret one-time API key**, claim URL, and verification code. Because our current GitHub connector cannot create secrets and the owner's Gmail connections cannot be loaned to GitHub, registration has NOT been attempted in the unattended workflow. A successful registration with no secure credential storage would be an unusable and insecure external identity.

Once the owner uses an approved secure environment to register each agent and immediately save its key, add the credentials **only** to GitHub repository Actions secrets named:
- `MOLTBOOK_ENIGMA_G07_A_API_KEY`
- `MOLTBOOK_ENIGMA_G07_B_API_KEY`

The human owner must open each provider-supplied claim URL, complete the email and X ownership claim, and respect site limits. Google account access alone does not establish Moltbook identity or provide an X login. This CI only does a read-only `GET /agents/me` to verify identity **if the separate secret exists**, never registers new accounts, sends email or posts marketing unsolicited.

Official Moltbook homepage: https://www.moltbook.com/ . Read the latest official https://www.moltbook.com/skill.md and https://www.moltbook.com/terms before any signup. If this account already owns a Moltbook agent or the same X identity cannot claim another, use Moltbook's normal owner-support flow; do not bypass account rules.

## Real-work standard

Each agent separately attempts Hugging Face CPU SmolLM2 inference, obtains bounded read-only public evidence from GitHub and/or World Bank, produces a model output for owner review, and records failures without pretending work was done. A passing mocked unit test is **not** evidence of real AI calls. Real model execution does not establish useful local findings, customers, crypto payments or continuous autonomous activity.

**Owner payment instructions:** https://amon-kwesiga.onrender.com/studio/payment.html . All released public browser software remains free, while bespoke engagements require buyer agreement and optionally native Bitcoin-mainnet payment to the correct verified recipient.

**Security:** no Gmail read in CI, no email sending, no wallet signing, no public signup/claim, no spam or silent mining, no private credentials in source or artifacts. Seven Google accounts connected inside ChatGPT do NOT equal fourteen Moltbook accounts.
