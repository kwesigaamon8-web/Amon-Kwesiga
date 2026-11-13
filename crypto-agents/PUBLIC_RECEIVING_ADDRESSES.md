# B & Director D — Public cryptocurrency receiving addresses

**Published on owner request: 13 November 2026.** These are *receiving destinations only*. Publication does not confirm wallet ownership, asset/network compatibility, exchange deposit eligibility, or a successful payment. Never request seed phrases, private keys, account logins, or use these addresses to initiate outgoing transfers.

## Self-custody addresses — proposed receiving destinations

Before instructing any payer, Director D09 must re-confirm the selected receiving address and the **exact asset and network** with the owner. An address displayed below is not an assurance that a particular token can be received.

| Route ID | Network | Receiving address |
| --- | --- | --- |
| BTC-01 | Bitcoin mainnet (native BTC) | `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z` |
| BTC-02 | Bitcoin mainnet (native BTC) | `bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9` |
| EVM-01 | EVM-format; choose and verify a specific network | `0x734989a439F146885C12907cd9Dd191b03d5B07e` |
| EVM-02 | EVM-format; choose and verify a specific network | `0x4A1fd580da92B82E2e5353410a30A93cecc7F0fb` |
| SOL-01 | Solana | `B2THff7E6KpGdkaeE2xcLqLfinyJmbcQSzJSRURKgW4C` |
| SOL-02 | Solana | `9PspGLrFawD8GXWqCwSTpJh6kESHvF2mQksVQZ8LVbBM` |
| TRX-01 | TRON | `TEmngrwxxHqvPUMVDiWzNk3PDyqGuzF1tU` |
| TRX-02 | TRON | `TNkfqx57edT2tAHRFSqPpnWWczFY61443u` |
| XLM-01 | Stellar | `GCXTQFEXZIOEKK4XLCA6JSSDIOCSH2ELZ44JIWVDR6WNTP4O37O3WVD4` |
| XLM-02 | Stellar | `GD245DHDCHSCBPBOAVTKMZULW6YYTI65XGV57EXHD4F67EG36J2XX7BD` |

**Token-specific caveat:** A valid-looking address does not prove support for a specific stablecoin. EVM-compatible networks can share address formats but must not be treated as interchangeable. Solana token mint, Stellar trustline/issuer and TRON token standards may require additional checks.

## Exchange deposit identifiers — PUBLIC REFERENCE ONLY; DO NOT SEND

The owner previously supplied the following as *potential* Binance USDC deposit routes. **None is declared payment-ready here.** They may be unusable without a valid, current deposit screen, correct token/network, mandatory memo, and confirmation of receiving account support. Publicly listing them does **not** authorize anyone to send coins. Mandatory memos are deliberately not posted.

| Candidate | Address/account | Status |
| --- | --- | --- |
| Binance EVM candidate | `0xa43e96d28f37bacf5441fcd9a3e7b662f299a785` | UNVERIFIED — DO NOT SEND |
| Binance Solana candidate | `8by2RbnKEwwDDg9PAgNZwWE8XXiGLCsVFQEE11urvgMr` | UNVERIFIED — DO NOT SEND |
| Binance Stellar candidate | `GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5SZVTGWUKULZJNL6` | UNVERIFIED; MEMO REQUIRED — DO NOT SEND |
| Binance Hedera account candidate | `0.0.1873771` | UNVERIFIED; MEMO REQUIRED — DO NOT SEND |
| Binance Polkadot candidate | `16fbLg3p45xwjdH9FwiqBVy5RDB5VRSfjsdmSd7LEeHTMK9p` | UNVERIFIED — DO NOT SEND |
| Binance Algorand candidate | `NYAGJ5YZR5KZBEZZCU7MRJP5XU64M6265OT3GQOUC6VHRUMT7FEF4UAYXU` | UNVERIFIED — DO NOT SEND |

The three previously supplied 0x-prefixed 32-byte entries of unknown type are **excluded** because they may be hashes or other identifiers instead of receiving addresses.

## Instruction to B, Director D and D09

1. Use this list as public read-only reference; **do not circulate the entire list to a potential payer**. Ask the owner to approve a *single* route for a specific real transaction.
2. Actively find legitimate customers and finish agreed paid work. Share the one confirmed network/address through an authorized channel when a real payer is ready.
3. Never claim earnings from a posted address, promise, testnet point, or self-transfer. Verify transaction and actual exchange credit where applicable.
4. Continue to maintain any private owner directory via restricted repository secrets. Public addresses do not grant permission to access funds or disclose unrelated private data.
5. This file lives in a public GitHub repository; its contents are publicly readable and may associate listed blockchain activity with this repository.
