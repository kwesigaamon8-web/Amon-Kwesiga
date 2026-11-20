# B1/B2, Chief D and Enigma — ONE Command, ONE Shared Code per Hierarchy Role

**Owner directive:** `OWNER-20261120-153811-ONE-CENTRAL-COMMAND-SHARED-ROLE-CODE`  
**Date:** 20 November 2026  
**Status:** Source implemented, 210 separate bounded Python role process receipts verified across all 30 roots, actual AI-model comprehension of all worker instances not proven.

## Single command authority

```text
HUMAN OWNER (authenticated instruction in ChatGPT)
       |
       v
Chief D — crypto-agents/chief_D_owner_orders.json   [SOLE COMMAND AUTHORITY]
       |
       +--> crypto-agents/PUBLIC_AGENT_COMMAND.json   [REQUIRED MATCHING MIRROR]
       |
       v
crypto-agents/hierarchy_command_core.py              [ONE SHARED ENGINE]
       |
       +--> role_director.py       D01–D10, every B1/B2/Enigma root
       +--> role_assistant.py      A/B advisers, every root
       +--> role_manager.py        M01–M15 under every director
       +--> role_worker.py         all W, S, G, H workers
                                     |
                                     +--> optional actual AI model adapter:
                                           ai_process_worker.py (one code for all workers)
```

**Do not copy or customize Python files for each individual role.** Individuality is configured by `global_role_index` or `(fleet, role_id)` and exact parent, task and evidence. The same code is used for D01/D02/D10; all managers use the same code, all workers share the same code.

## What the software verifies each time a real process runs

1. Load Chief D's exact latest human owner order and require the public mirror to match character-for-character.
2. Compute and compare the original owner instruction SHA-256 and full standing safety prompt SHA-256.
3. Decode a unique role identity and its entire parent chain across the 30 configured roots.
4. Reject wrong executable role, stale order, unassigned role, invalid index or wrong direct parent.
5. Execute a finite director, assistant, manager or worker source-ledger task; manager assigns 50 virtual W slots but does **not** claim any child process was started.
6. Save an individual JSON output with actual PID, role path, parent, owner order ID, original owner prompt digest, task-result digest and explicit evidence distinctions.
7. In scheduled AI-model mode, use one `role_worker.py --actual-model` entrypoint for all original B1/B2 W/S/G/H roles; it delegates in the **same operating-system process** to the existing shared model adapter. The model adapter itself checks the same owner instruction and runs separate practical comprehension tests. Enigma model workers also call the same central authority engine.

## Examples (each is only a bounded task, not a model inference)

```bash
# All original B1 directors use the SAME program:
python crypto-agents/role_director.py --fleet transferexperiment --role D01

# The SAME code for another B1 director:
python crypto-agents/role_director.py --fleet transferexperiment --role D10

# Any original B2 manager uses the SAME program:
python crypto-agents/role_manager.py --fleet BountyScoutAI --role D06-M11

# ALL original W/S/G/H roles use ONE shared program:
python crypto-agents/role_worker.py --fleet transferexperiment --role D01-M01-W01
python crypto-agents/role_worker.py --fleet transferexperiment --role D01-M01-W01-S001-G001-H001

# Any Enigma role uses its globally indexed slot with the same role program:
python crypto-agents/role_worker.py --role-index 750433628628

# An actual, permissioned scheduled B1 model-worker attempt uses this entrypoint:
python crypto-agents/role_worker.py --actual-model --fleet transferexperiment --role D01-M01-W01
```

The Enigma example selects an H-level role under its first director; a wrong-tier executable is deliberately rejected. The command also rejects invalid or out-of-namespace role indexes.

## Audit evidence

- [**210 real shared-role Python process test**](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44766111921): 30 logical roots × 7 role tiers. Executables used: four shared role files and the one central engine. Each individual role produced a real bounded task record with matching current owner order, matching SHA, parent, actual OS PID and no invented AI understanding, buyer contact or payment.
- [**Owner-to-H full parent relay prototype**](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44763785785): 326 separate local Python parent-child hops, all 30 final H roles completing ledger QA. This proves a local relay mechanism, **not** global hosted delivery to every virtual worker.
- [**Full repository forensic**](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44763501326): checked all tracked Python/JSON/workflow files for parser errors and checked 90 command route samples.

## Critical limitations

- The **11,255,658,980,400** hierarchy members are mathematical **role identifiers**, not 11 trillion independent live agents. One shared codebase makes them addressable and maintainable but does not provide compute, network connections, permission, account logins or funding.
- A source-ledger test is a real deterministic Python task. It is **not** proof that a generative AI model understood the owner directive.
- Manager and director program execution is currently finite supervisory QA and assignment, not proof that every configured manager has an independent model or has personally acknowledged the order.
- No program may read/search/draft/send the owner's Gmail or any email without separate specific authorization. No mass unsolicited marketing, wallet signing/spending or false crypto income.
- **Strict acceptance for the user's final goal:** real worker provisioned → current order delivered with valid SHA and parent → genuine model response in its own words → original scoped task performed and independently reviewed → supervisor receipt → verified buyer or payment evidence if commercial.

## Next engineering actions

1. Keep **one canonical command record** as the only source of truth and protect it with real human approval/branch controls.
2. Refactor legacy director/worker model-specific utilities to import the shared engine rather than embedding prior owner commands. The main original B1/B2 production paths and Enigma model code now check the central engine, but additional historical automation scripts remain.
3. Add a durable, authenticated, network-accessible queue for independently provisioned manager/director/worker processes; each child cannot execute before the correct parent receipt and current owner version are validated.
4. Add a registry of genuinely provisioned processes, model IDs, granted account access and heartbeat; no configured slot enters the active count without an actual process.
5. Audit genuine model comprehension and accepted original deliverables per active worker, then scale capacity responsibly.

**Final verdict:** **ONE CODE PER TIER and ONE AUTHORITATIVE OWNER COMMAND are implemented and tested for representative finite process invocations; universal independent delivery to all virtual role IDs is not achieved.**

## 20 November 2026 — One self-correcting engine for all 11,255,658,980,400 logical roles

**Live source:** [`self_correcting_role_runtime.py`](./self_correcting_role_runtime.py). All actual D/A/M/W/S/G/H invocations now pass through `hierarchy_command_core.execute()` and its shared `self_correcting_execution()` call. The `role_worker.py --actual-model` entrypoint also verifies the exact current owner command and direct parent with this common engine before attempting model work.

**Specific per-process behavior:** validate owner ID/full text hash/standing protocol, global index, role chain and immediate supervisor; derive a bounded safe in-memory public-source view; remove unsafe/malformed/duplicate lead links and hold unsupported payment/acceptance assertions; run only the existing local deterministic tier-specific task; verify the resulting source row count/action shape/result hash; retry a pure local check **at most twice**. No file or wallet changes are made by this worker engine, and no external task submission occurs here. If no safe source remains, output an explicit `BLOCKED_NO_SAFE_PUBLIC_SOURCE` receipt; if the parent/order/result is untrusted, fail closed rather than rewriting authority.

**One source for every role:** no code copies are installed per worker ID. `enigma_universal_owner_order.py` maps all 30 logical root divisions × 375,188,632,680 positions per division; the runtime only executes if a real local/scheduled process invokes the selected role. A created role address or lazy packet is not an independently running model.

**Verified run:** [B1B2 Self-Correcting All Role Tiers, run 44792351552](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44792351552) **SUCCESS**. One test invoked the shared engine for **210 real local role actions** (30 roots × 7 tiers), with deliberate malformed/duplicate/unsupported buyer-claim tests, bounded retry proof, wrong-parent/order/index negatives, and zero emails/payments. A separate existing acceptance test launched **210 distinct bounded role subprocesses** and verified current owner command + individual source task + capability proof. The tests did **not** activate 11 trillion agents or complete separate LLM inferences. Future scheduled daily and source-change tests: [`b1b2-one-self-correction-all-role-tiers.yml`](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/b1b2-one-self-correction-all-role-tiers.yml).

**How to run on one address (inside a checked-out repository):**

```bash
python crypto-agents/role_worker.py --role-index 11255658980399
python crypto-agents/test_self_correcting_all_roles.py
```

The first command executes only the one selected H-tier role and creates its source-only forensic JSON receipt. The test command covers a bounded sample across all 30 divisions; neither command broadcasts to dormant roles. External buyers, authenticated account actions, mining, and on-chain payment confirmation require separate permission and direct evidence. No Gmail/email access, signing, spending or mass communications are authorized.
