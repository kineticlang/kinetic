# Agent guidance fallback

Read [AGENTS.md](AGENTS.md) before editing this repository. It is the canonical
source of project instructions; this file is an alternative entry point for
tools configured to read the singular filename. It does not rely on special
import syntax or guarantee automatic discovery by every tool.

## Essential rules

- Keep compiler modules directly in the [compiler package](compiler/README.md),
  with package-relative imports and a thin [root launcher](kinetic.py).
- Keep Python sources free of explanatory comments and docstrings. Put
  explanations in documentation and examples instead.
- Respect requests for read-only or static-only work. Do not generate IR,
  invoke native tools, or run Kinetic programs when that is prohibited.
- For static-only verification, use the explicit layout suite:

```shell
python -B -m unittest discover -s tests -p test_layout.py -v
```

- The general [runner](tools/check.py) also discovers behavioral suites and is
  not static-only. See [tests](tests/README.md) for the verification boundaries.
- Keep roadmap status factual. The [host interface specification](docs/bootstrap_interface.md)
  is a design, not an implemented host adapter. Bounds checks do not provide
  lifetime safety, and Kinetic is not yet self-hosting.
- Update every Markdown file affected by a change in the same change — root
  guides, docs, directory READMEs, and the agent guidance files — so no
  document is left stale. Static checks do not cover compiler behavior: hosted
  GitHub CI runs the frontend/backend suites with llvmlite and the native
  example suite with Clang, and those results are the behavioral evidence.

Maintain detailed rules in [AGENTS.md](AGENTS.md), not a separate competing copy
here. [CLAUDE.md](CLAUDE.md) is the Claude Code entry point for the same guidance.
