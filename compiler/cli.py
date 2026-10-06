import argparse
import subprocess
import sys
from pathlib import Path

from .compiler import compile_with_diagnostics
from .errors import KineticError


def build_command(source_path: Path) -> Path:
    source_text = source_path.read_text(encoding="utf-8")

    result = compile_with_diagnostics(source_text)

    for warning in result.diagnostics.render_warnings():
        print(warning, file=sys.stderr)
    summary = result.diagnostics.summary()
    if summary:
        print(summary, file=sys.stderr)

    ll_file = source_path.with_suffix(".ll")
    ll_file.write_text(result.llvm_ir, encoding="utf-8")

    app_name = source_path.with_suffix(".exe" if sys.platform == "win32" else "")

    print(f"Building {app_name}...")

    try:
        subprocess.run(["clang", str(ll_file), "-o", str(app_name)], check=True)
    except FileNotFoundError:
        print("kinetic: error: could not find 'clang' on PATH", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("kinetic: error: clang failed while building the binary", file=sys.stderr)
        sys.exit(1)

    print("Build successful!")
    return app_name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kinetic Compiler CLI - A systems-level programming language designed for humans."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Compile a .kn file to a binary executable")
    build_parser.add_argument("source", type=Path, help="The Kinetic source file to build")

    run_parser = subparsers.add_parser("run", help="Compile and immediately run a .kn file")
    run_parser.add_argument("source", type=Path, help="The Kinetic source file to run")
    run_parser.add_argument(
        "program_args",
        nargs=argparse.REMAINDER,
        help="arguments passed to the compiled program; use '--' before leading dashes",
    )

    args = parser.parse_args()

    try:
        app_name = build_command(args.source)

        if args.command == "run":
            print(f"Running {app_name.name}...\n{'-'*30}")
            program_args = list(args.program_args)
            if program_args and program_args[0] == "--":
                program_args = program_args[1:]
            result = subprocess.run([str(app_name.resolve()), *program_args])
            return result.returncode if result.returncode >= 0 else 1

    except KineticError as error:
        rendered = str(error)
        if getattr(error, "line", None) is not None:
            rendered = f"kinetic: error: {error.line}:{error.column}: {error.message}"
        else:
            rendered = f"kinetic: error: {error.message}"
        print(rendered, file=sys.stderr)
        return 1
    except (OSError, RuntimeError) as error:
        print(f"kinetic: error: {error}", file=sys.stderr)
        return 1

    return 0
