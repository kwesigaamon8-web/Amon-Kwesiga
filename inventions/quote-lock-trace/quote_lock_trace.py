"""Offline display-state trace review; no payment or security assurance."""
import datetime as dt
import json
import pathlib
import re
import sys

MAX_BYTES = 1_048_576
MAX_SNAPSHOTS = 1000
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z")


def timestamp(value):
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise ValueError("timestamp must be ISO date/time with seconds and explicit timezone")
    if value[-1] != "Z" and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
        raise ValueError("invalid timezone offset")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(dt.timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError("invalid timestamp") from exc


def review(document):
    if not isinstance(document, dict) or set(document) != {"snapshots"}:
        raise ValueError("document must contain only snapshots")
    snapshots = document["snapshots"]
    if not isinstance(snapshots, list) or len(snapshots) > MAX_SNAPSHOTS:
        raise ValueError("snapshots must be a list of at most 1000 entries")
    previous = None
    quote_id = None
    known_expiry = None
    expiry_boundary_observed = False
    events = []
    has_review = False
    has_unknown = not snapshots
    fields = {"quote_id", "observed_at", "expires_at", "locked_claim_visible", "pay_button_enabled"}
    for index, sample in enumerate(snapshots, 1):
        if not isinstance(sample, dict) or set(sample) != fields:
            raise ValueError("snapshot %d has missing or unexpected fields" % index)
        identity = sample["quote_id"]
        if not isinstance(identity, str) or not identity.strip() or len(identity) > 128:
            raise ValueError("quote_id must be a nonempty string of at most 128 characters")
        if quote_id is not None and identity != quote_id:
            raise ValueError("quote_id changes within trace")
        quote_id = identity
        observed = timestamp(sample["observed_at"])
        if previous is not None and observed <= previous:
            raise ValueError("observations must be strictly chronological with no duplicates")
        previous = observed
        if type(sample["locked_claim_visible"]) is not bool or type(sample["pay_button_enabled"]) is not bool:
            raise ValueError("display-state fields must be JSON booleans")
        expiry = None if sample["expires_at"] is None else timestamp(sample["expires_at"])
        if expiry is not None:
            if known_expiry is not None and expiry != known_expiry:
                raise ValueError("known expires_at changes within quote trace")
            known_expiry = expiry
        expired = None if expiry is None else observed >= expiry
        flags = []
        if expired is None:
            has_unknown = True
            flags.append("EXPIRY_UNKNOWN")
        elif expired:
            expiry_boundary_observed = True
            if sample["locked_claim_visible"]:
                flags.append("LOCKED_CLAIM_AT_OR_AFTER_EXPIRY")
                has_review = True
            if sample["pay_button_enabled"]:
                flags.append("PAY_BUTTON_ENABLED_AT_OR_AFTER_EXPIRY")
                has_review = True
        events.append({"snapshot": index, "expired": expired, "flags": flags,
                       "pay_button_enabled_observed": sample["pay_button_enabled"]})
    return {"status": "REVIEW" if has_review else "UNKNOWN" if has_unknown or not expiry_boundary_observed else "PASS",
            "snapshots_reviewed": len(snapshots), "has_unknown_expiry": has_unknown,
            "at_or_after_expiry_observed": expiry_boundary_observed,
            "events": events, "backend_payment_acceptance": "NOT_TESTED",
            "meaning": "Display observations only; PASS means no selected flag in supplied samples, not security assurance."}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def load_document(path):
    with pathlib.Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds 1 MiB")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON number")))


def main(argv):
    if len(argv) != 1:
        print("Usage: python quote_lock_trace.py TRACE.json", file=sys.stderr)
        return 2
    try:
        report = review(load_document(argv[0]))
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        print("Invalid input: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
