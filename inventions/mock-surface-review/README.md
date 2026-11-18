# Mock/native direct-method review — uncommissioned sample

A fake API can expose a method that the actual native binding lacks, allowing a mock-based test to pass while firmware fails. This small offline reviewer compares names of directly defined methods in one Python class against a caller-provided JSON manifest. It never imports or executes the source, invokes native code, accesses wallets or makes network requests.

Problem attribution: [FoundationKen's review of Passport PR 647](https://github.com/Foundation-Devices/passport2/pull/647#discussion_r4129009506) identified a fake `multiply` method that did not match the native API. That finding belongs to the maintainer. This synthetic sample is not a submission to that bounty, a competing fix, or a claim of a new vulnerability.

## Run

Python 3.10+ on a POSIX system; standard library only:

```sh
python -m unittest discover -s . -v
python review.py example_fake.py example_manifest.json
```

The example deliberately reports `multiply` as extra and `verify` as missing. Exit status 0 means a report was generated, not that the names match. Input errors return 2 with a sanitized error category. There are no writes by the reviewer itself.

## Boundaries

Each UTF-8 input is limited to 64 KiB, and each method list to 256 names. File inputs must be regular files. Inheritance, metaclasses, decorators, dynamic attribute hooks, class assignments and conditional class members are rejected. Duplicate matching classes or direct methods are rejected. Source parsing is static; other module statements and method bodies are not analyzed or executed.

The native manifest must be independently reviewed against the exact native binding version. The program does not establish its truth. It compares names only: signatures, behavior, runtime monkeypatching, instance attributes, exported callable objects and correctness are outside scope. Equality is not runtime compatibility, build reproducibility or a security assurance. The explicit unsupported cases are deliberate, not a general Python type system.

## Alternative and possible service

[Python `unittest.mock` autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing) is the stronger everyday alternative when the real object is importable: it can restrict attributes and call signatures. This sample's narrow use is offline review when a native firmware object cannot be imported on the review machine. A hand-reviewed binding manifest is still required; stale stubs are not evidence.

Named public buyer market: Bitcoin firmware maintainers, including the Passport ecosystem. No buyer has commissioned this sample. A possible one-pair review with a verified manifest and concise findings report could be quoted at **15,000 sats payable on Bitcoin mainnet**, subject to independently confirmed scope, buyer, fee, acceptance criteria and payment route. This is an unagreed example price, not an accepted job, invoice or earnings. No offer or application was sent. The existing Passport contribution is already being reviewed and is not an available assignment to assume.
