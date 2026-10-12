# Imported modules

Files in this directory are modules: they are compiled as part of the program
that imports them, not on their own.

| Module | Declarations |
| --- | --- |
| [Text utilities](text_utils.kn) | `is_digit` and `count_digits`, used by the [modules example](../14_modules.kn). |

Rules the compiler enforces:

- An `import` declaration names a string path that is relative to the file
  containing it, uses forward slashes, and ends in `.kn`. Rooted
  (`/lib.kn`, `\lib.kn`), drive-qualified (`C:/lib.kn`), and backslash-separated
  paths are rejected on every host, so imports resolve the same way everywhere.
- Import declarations appear before function and record declarations.
- A module contributes its functions and records to the importing program's
  single top-level namespace, so duplicate names are errors.
- A module must not declare `main`; the program that starts a build does.
- Importing the same file more than once loads it once, and import cycles are
  rejected.

A module has no `main` of its own, so building one directly reports a missing
entry point. Build the program that imports it instead:

```shell
python kinetic.py run examples/14_modules.kn
```

See the [imports section](../../docs/syntax_guide.md) of the syntax guide for
the full rules.
