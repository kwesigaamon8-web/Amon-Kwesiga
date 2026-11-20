# B1/B2/Chief D — Bounty system 01: Threshold Network / Immunefi
**Owner mission:** Obtain actual, confirmed BTC or any other owner-approved cryptocurrency receipts. **Mode:** one authorized bounty program at a time; 11,255,658,980,400 logical role slots, not independent online bots.

**Verified public sources, 20 November 2026**
- Terms & reward: https://immunefi.com/bug-bounty/thresholdnetwork/information/
- Assets & impacts: https://immunefi.com/bug-bounty/thresholdnetwork/scope/
- Developer resources: https://immunefi.com/bug-bounty/thresholdnetwork/resources/
- Immunefi global conduct rules: https://immunefi.com/rules/
- Target project's own published source: https://github.com/threshold-network/solidity-contracts

## Selection rationale and limits
- Threshold is publicly listed with up to **USD 150,000** advertised bounty, not guaranteed; bug reports need a **genuine reproducible proof of concept** and impact within scope.
- No KYC requirement is stated for this program, but platform account and individual eligibility still need confirmation.
- Rewards are **normally USDC on Ethereum** and may instead be **Threshold T on Ethereum** at the DAO's discretion; the researcher cannot select the asset.
- Owner's BTC addresses are **Bitcoin mainnet**, never valid USDC-on-Ethereum payout destinations. EVM-format wallet candidate is already in `public_payment_routes.json` but its ownership, Ethereum support and token compatibility remain **unverified**. DO NOT direct a payer to it until the owner verifies.
- In this program Immunefi bans live mainnet/public testnet contract testing, high-traffic scans, social engineering, and reporting generic scanner output without validated effect. Review published source and use **offline or entirely locally isolated tests** only, never attack hosted systems.
- Program's scope controls; a repository existing on GitHub does NOT imply all commits or contracts are in scope. Verify selected deployed version before claiming eligibility.

## First specific in-scope target: TokenholderGovernor (governance)
- Immunefi Threshold smart-contract Scope currently names **TokenholderGovernor**, added 27 April 2023, at the displayed Ethereum mainnet address [0xd101f2b25bcbf992bdf55db67c104fe7646f5447](https://etherscan.io/address/0xd101f2b25bcbf992bdf55db67c104fe7646f5447) (asset inclusion evidence, NOT approval to run against it).
- Source read (PUBLIC STATIC ONLY): `contracts/governance/BaseTokenholderGovernor.sol`, blob SHA `4da8e704c67a85c863a249366a9f127307ba0e2d`; it imports OpenZeppelin Governor, AccessControl, late-quorum and timelock modules. Basic preliminary review: visible `cancel()` is gated by `onlyRole(VETO_POWER)`; `_execute()` delegates to super; this is a **description, not a vulnerability finding**.
- Review plan: model each governance state transition in isolated local tests (proposal creation, quorum, veto, cancellation, late quorum voting extension, timelock handoff and administrator grants). Check against known audits and deployed bytecode/source before alleging anything. Do **not** call any actual on-chain contract.
- The bounty **explicitly excludes deprecated staking contracts**, so do not target old `TokenStaking.sol` deployments as bounty-eligible by mere inclusion in the source repository. Treat old source review as reference only.
- **Result so far:** source inspected; no independently proven vulnerability, no PoC, no private report and no paid finding.

## Work already started: source reconnaissance
Connected GitHub read of `threshold-network/solidity-contracts` on default branch `main`:
- `README.adoc` SHA `cbc9fb9d461748007c0d002b0fdf91866e0fc990`: Hardhat, `yarn build`, `yarn test`.
- `SECURITY.md` SHA `bae6b2c5c125938563c9312699b04a6999f020cf`: published bounty details, private disclosure.
- `contracts/governance/TokenholderGovernor.sol` SHA `9628d66211576be2b6ec163dc8033b8837a43505`: constructor passes quorum/proposal threshold and time windows into base governor.
- `contracts/governance/Checkpoints.sol` SHA `d60602e33c8bfcc82ccbfa2f37a8c904fe4986a9`: delegation checkpoints and historical voting power.
- `contracts/staking/TokenStaking.sol` SHA `2fbb04f329fce3b34d4d55a0d6da4a7ab2ca5769`: stake data, application state and authorizations.
**This is source inventory only. No finding, locally executed PoC, bounty submission or payment has been evidenced.** Audit history and published findings must be checked before any independent original report.

## One-target sequential operating system
`python crypto-agents/authorized_bounty_pipeline.py --index N` returns one **country-assigned** role's job, owner-wallet reference, source/scope links, acceptance criteria and safety gates. The existing `enigma_universal_owner_order.py` maps all 30 divisions and **11,255,658,980,400** configured virtual slots into these roles with no huge storage, using deterministic on-demand routing. **No real agent automatically exists for a slot**.

Eight sequential quality lanes (parallel role allocation is organizational only):
1. **RULES** — review current restrictions, Uganda eligibility, candidate deployed-version scope;
2. **SCOPE** — select a single published target contract/impact, no live interaction;
3. **SOURCE** — read the selected public code and exact revision;
4. **INVARIANT** — derive concrete security properties with counterexample conditions;
5. **LOCAL_TEST** — reproduce only on private local code/unit test, never live endpoints;
6. **KNOWN_ISSUES** — review released audit reports and duplicates;
7. **INDEPENDENT_REVIEW** — verify actual impact, precision, reproducibility and embargo;
8. **PAYMENT_QA** — confirm compliant private submission, dashboard identity and correct payout network/wallet.

Every report needs the actual independent role/process identifier, source URL and commit hash, an explicit observed finding (if any), reproducible local test, vulnerability's real impact, and verified acceptance. Keep any non-public details private and submit only through an authorized authenticated Immunefi report; no GitHub public disclosure of unpatched findings.

## Completion gate (do not fake)
A single target is complete only after independent quality review and a verified accepted report or a documented defensible decision to stop/no valid findings. No "success" based merely on role generation, CI passed, views, accepted mining pool shares, a draft, or a claimed customer. Payout is successful only with owner-authorized receiving wallet, correct network, confirmed blockchain transaction hash, credited amount and the sponsoring payer's acceptance.

**Next program**: OpenZeppelin Immunefi (KYC and Ethereum recipient verification needed), then Immunefi's own program; both stay blocked until the present bounty is explicitly closed/reviewed. No email access or outgoing email.
