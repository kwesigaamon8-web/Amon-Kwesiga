# PC AI Miner — open Bitcoin learning and voluntary mining collaboration

**Public product name:** **PC AI Miner** (B1/B2 Digital Work Studio)  
**Source:** [pc_ai_miner.py](./pc_ai_miner.py) · [unit tests](./test_pc_ai_miner.py) · [web page](../../docs/pc-ai-miner.html)  
**Read-only reference:** [Public Pool](https://web.public-pool.io/) · [official cpuminer-opt upstream](https://github.com/JayDDee/cpuminer-opt/releases)  
**Mission:** Make safe educational software and historical source audits available globally; enable independently consenting hardware owners to opt into manual, explicitly disclosed contribution to B1 or B2.

## Available right now

1. **Actual publicly released Python educational source**: implements SHA256d, independently checks the Bitcoin genesis-block hash, runs a bounded toy nonce puzzle, and generates—but does not apply—voluntary pool configuration. No network request or coin transfer. Run `python pc_ai_miner.py self-test` or `python pc_ai_miner.py demo --tries 12000 --bits 12`.
2. **Public unit tests**: `python -m unittest test_pc_ai_miner.py`. They verify actual Bitcoin genesis hash, source-safe bounded CPU use, Bitcoin-mainnet B1/B2 labels, both pool modes and hard rejection of unconsented donation configuration.
3. **Public interactive HTML**: [PC AI Miner](../../docs/pc-ai-miner.html), voluntary owner-authorization/donation settings and browser WebCrypto demonstration limited to **32 hashes per click**, never background mining.
4. **Older Windows mining families**: **34 original ZIP packages** have been recovered from the owner's Library and examined as **private prerelease archives**, not yet offered as publicly trusted installers. Static ZIP inventory: 801 archive entries, 383 Python entries, 0 CRC failures, 0 unsafe zip paths, 0 Python parser failures. This is *not* malware/AV assurance or a release audit.
5. **Original RecordLow v1.4**: a source-only curator review copy (Python miner, Bitcoin math, original tests, license, example configuration) underwent **15 local offline/mock-pool tests (PASS)**. The archive may be downloaded directly by the owner from the conversation attachment after it is generated. We do NOT place raw binaries, autostart scripts, historical runtime records or unrelated personal data on the public website.

## Why all 34 ZIPs are not publicly installed

- Some versions contain Windows DLLs or a bundled third-party executable, which require stronger provenance, dependency/AV, attribution and functionality review.
- Later versions contain **optional Windows task scheduler autostart**. It must not be installed without the actual hardware owner's meaningful prior consent. No software in this release enrolls a visitor.
- Historic sample wallet configurations may default to a project donation address and must be made fully explicit to volunteers. Operators should independently confirm reward ownership and wallet payout rules.
- **cpuminer-opt 26.1** is externally maintained by JayDDee and governed by its own GPL terms. It is linked to its [original releases](https://github.com/JayDDee/cpuminer-opt/releases), never passed off as PC AI Miner proprietary code.
- The **Monero/XMR starter** is a different coin. It is not Bitcoin SHA256d mining and is not a native BTC-payment product.
- No downloaded archive has been proved profitable, antivirus-clean, thermally safe on every device or compatible with a current mining pool. A successful fake-pool test cannot establish a mainnet payout.

## Voluntary, explicit hardware operator instructions

**No network miner is started by this toolkit.** If you genuinely control and can authorize the physical miner and electricity, and independently agree to direct rewards to B1/B2 rather than your own wallet, run:

```bash
python pc_ai_miner.py manual-config --fleet B1 --pool-mode pplns --worker-label Volunteer01 --i-own-or-control-device --i-agree-to-donate-rewards
```

This only **prints** a configuration for the operator to inspect. B1 BTC mainnet `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z`, B2 mainnet `bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9`. Both require direct consent to route rewards here.

**Live protocol reference:** Public Pool [official page](https://web.public-pool.io/) lists Solo TLS 4333, PPLNS TLS 14333. Solo rewards occur only upon finding a full Bitcoin block; PPLNS depends on pool-found blocks and its published allocation rules. Do not misreport accepted shares as confirmed coins. CPU mining rewards are generally negligible relative to ASIC network hashrate.

## Social platform distribution and 11,255,658,980,400 roles

- **Public GitHub** is available and new HTML/source documentation is actually published. User-controlled external social posts may share the *public GitHub catalogue link* only with community permission.
- **Metricool** is connected as an integration but reports **no social networks linked**. It cannot currently schedule or publish to Twitter/X, Facebook, LinkedIn, Instagram or others on your behalf. Do not claim social posting until an actual account and resulting post URL are verified.
- B1/B2's **11,255,658,980,400 configured worker IDs are virtual names**, not actual devices or social accounts. Any genuinely executed employee/agent can read this public repository's shared instruction upon invocation; none are claimed to be currently connected or mining. GitHub Actions can test/distribute source, **not mine BTC**.
- The web page offers self-serve links and an existing collaborator discussion thread. Do not create bot accounts, spam, post covert redirects, or make unsolicited automatic contact. No Gmail/email read/search/draft/send.

## Testing and reproducibility

Run `python crypto-agents/pc-ai-miner/pc_ai_miner.py self-test` and `python -m unittest discover -s crypto-agents/pc-ai-miner -p 'test_*.py'` from repository root. The separate GitHub Actions [PC AI Miner public release QA](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/pc-ai-miner-release-check.yml) checks source parsing, consent, published web claims and public path consistency. No individual download, wallet receipt, or social post is presumed to have occurred.

**Status:** Public learning/demo source released; archived third-party and executable miners quarantined for further review. New owner Bitcoin mining receipts independently proven by this release: **0 BTC**.
