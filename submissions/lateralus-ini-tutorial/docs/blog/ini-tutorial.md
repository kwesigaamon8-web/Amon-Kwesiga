# Reading INI configuration files in Lateralus

**Public stdlib module:** [`stdlib/ini.ltl`](https://github.com/bad-antics/lateralus-lang/blob/main/stdlib/ini.ltl)  
**Example source:** [`examples/ini_tutorial.ltl`](../../examples/ini_tutorial.ltl)  
**Purpose:** Parse settings, read typed values safely, and handle missing keys.

An INI file is a plain-text configuration file. Sections appear in square
brackets, and settings use `key = value`.

## A real-world-looking, fictional configuration

```ini
# demo configuration
[app]
name = demo
threads = 4
enabled = yes

[paths]
cache = /tmp/data
```

The Lateralus `ini` module provides `parse`, `get`, `get_int`, `get_bool`,
`get_float`, `set`, `delete`, `has_key`, `has_section`, `sections`,
`section_keys`, `merge` and `to_string`.

### Parsing and reading settings

```lateralus
import ini

fn main() {
    let cfg = ini.parse("[app]\nname = demo\nthreads = 4\nenabled = yes\n")

    print(ini.get(cfg, "app", "name", "missing"))
    print(str(ini.get_int(cfg, "app", "threads", 0)))

    if ini.get_bool(cfg, "app", "enabled", false) {
        print("enabled=yes")
    }
}

main()
```

The `get` accessor returns the supplied fallback only when the section/key
does not exist. `get_int` converts the stored value to an integer.
`get_bool` recognizes `yes` and `true`.

**Important implementation detail:** the underlying `_parse_value` recognizes
`true`/`yes` and `false`/`no`, as well as `nil`/`null`.
Ordinary numeric values such as `4` stay strings after `parse`, until
you request conversion with `get_int` or `get_float`. Do not assume numeric
conversion happens automatically.

### Pinned expected output

For the complete accompanying example, which also checks paths and missing
keys, the exact expected output is:

```text
demo
4
enabled=yes
/tmp/data
missing=absent
```

The input is synthetic and contains no secrets, passwords or live wallet data.

### Handling missing or optional fields

```lateralus
let cfg = ini.parse("[app]\nname = demo\n")
let absent = ini.get(cfg, "app", "region", "not-set")
let present = ini.has_key(cfg, "app", "name")
```

A key that doesn't exist returns the fallback. `has_key` is explicit when the
caller must distinguish an absent key from a present but empty value.

### Updating and writing a configuration

`ini.set(cfg, section, key, value)` updates a section and key; `ini.delete`
creates a configuration with the selected key removed. `ini.to_string`
serializes the configuration with sorted sections and keys, so input order is
not preserved. `ini.merge(base, other)` makes values from `other` override
values from `base`.

### Parser limitations and error-handling cautions

- Empty lines and lines starting with `#` or `;` are ignored.
- The parser strips surrounding whitespace from keys and values.
- Additional `=` characters inside a value are preserved.
- If the entire value starts and ends with double quotes, the surrounding
  quotes are removed, but this is **not** a full escaped-string decoder.
- `parse` creates a `default` section even if the input begins with a
  named section.
- `get_bool` returns false for existing values that are not recognized as
  truthy; absent keys instead use the provided fallback.

## How to verify

After applying this work inside the actual upstream repository, run:

```bash
python -m pip install -e .
lateralus run examples/ini_tutorial.ltl
```

Compare the five-line output with the pinned vector above. The tutorial was
prepared against upstream `stdlib/ini.ltl` source blob
`23380322f9f4cf8dc592abfbe360a52bb9467d30`. Four offline source-contract
checks passed, **but the Lateralus compiler was not accessible** to the
authoring environment, so a real compiler/runtime check must happen before
the work is claimed to be fully tested.

## Bounty and licensing note

This is original documentation prepared for the project's published recurring
single-module tutorial micro-bounty ($25). No slot or payment has been awarded
or verified. Publication in this project branch is a work sample **not** a
contribution to the target repository or proof of a paid customer. If accepted,
the upstream maintainer requires original work, MIT licensing, signed-off
commits and review/merge, and offers BTC/Lightning as payment options.
