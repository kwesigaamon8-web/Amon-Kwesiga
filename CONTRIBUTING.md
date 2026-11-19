# Contributing to B1/B2 Digital Work Studio

Welcome, real people worldwide. We welcome **consensual, bounded, useful** contributions to our public software, documentation, tests and accessibility. Please read the [public community invitation](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/32) and use the [structured opt-in form](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new?template=collaborator-join.yml) if you want to introduce yourself.

## Easiest first contributions

- Try the [browser tools](docs/software.html) with **fictional data** and report exactly one reproducible bug.
- Improve tests for CSV/JSON conversion, exact-cent matching, duplicate handling, accessibility or keyboard use.
- Improve documentation or translate a short publicly owned page with accurate technical meaning.
- Verify that read-only Bitcoin merchant claims are clear about limitations; do **not** introduce signatures, secrets or a false "paid" status.
- Read [Bitcoin miner collaboration rules](crypto-agents/BITCOIN_MINING_COLLABORATION_REALITY.md) before proposing any hardware involvement.

## Testing

From the repository root, with Node.js available:

```sh
node --test docs/tests/*.test.js
node --test crypto-agents/commercial-work/crypto-ledger-reconciler/*.test.mjs
node --test crypto-agents/commercial-work/africa-bitcoin-merchant-wallet/*.test.mjs
```

The software catalogue lives in `docs/software.html` and the public collaboration page in `docs/join.html`; both are published by the test-gated, renewing no-fee website workflow. Avoid rewriting established wallet logic just to advertise a new function.

## Propose an original contribution

1. Choose an actual issue, explain the scope publicly, and check that nobody already has it in progress. Please do not submit unrequested large code dumps.
2. Make a small, reviewable change and test it with mock/synthetic input; report both the code and observed tests.
3. Submit a pull request only through a legitimate authorized GitHub account. Review/merge is at the project maintainers' discretion. Suggestions and bug reports can be posted in the linked GitHub issues.
4. Do not include private information, bank records, copyrighted third-party content, wallets or keys. Never impersonate teammates or access or mine on someone else's infrastructure.

## Compensation, attribution and mining

This invitation is not a job, hire, bonus, referral bounty, token sale, investment, agency agreement or income guarantee. Open-source feedback can be voluntary. Any commercial work or referral commission requires separate agreement on deliverables, payment, IP/license terms, exact supported payment network, and acceptance **before** performance. Public GitHub accounts that comment are not automatically employees or independent contractors. Public repo content may not all carry the same license; inspect licensing and agree ownership before reuse.

Hardware owners control their own authorized ASIC rigs and pool payouts. Do not redirect miners' compensation to B1/B2, use free hosting to mine, or mix solo/PPLNS/FPPS shares without explicit agreement and proof. Contributions by AI systems must identify genuine execution and rights; mathematical worker IDs are not people.

## Communication policy

No unsolicited mass posts, mail, personal-data scraping, spam, mass account creation, credential sharing or wallet signing. Use public, consent-based GitHub issues and the published opt-in page. Internal hourly scheduled checks only **observe** interest; they do not create relationships or make money.

We want respectful, useful collaboration in which everyone knows what they are agreeing to.
