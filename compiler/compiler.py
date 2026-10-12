from pathlib import Path

from .analyzer import TypeAnalyzer
from .diagnostics import CompilationResult, Diagnostics
from .lexer import Lexer
from .modules import resolve_imports
from .parser import Parser


def compile_with_diagnostics(
    source: str, source_path: Path | str | None = None
) -> CompilationResult:
    diagnostics = Diagnostics()
    tokens = Lexer(source, diagnostics).tokenize()
    program = Parser(tokens).parse()
    program = resolve_imports(program, source_path)
    function_types = TypeAnalyzer(program, diagnostics).analyze()

    from .backend import LLVMBackend
    from llvmlite import binding

    llvm_ir = LLVMBackend(program, function_types).generate()

    module = binding.parse_assembly(llvm_ir)
    module.verify()
    return CompilationResult(llvm_ir, diagnostics)


def compile_source(source: str, source_path: Path | str | None = None) -> str:
    return compile_with_diagnostics(source, source_path).llvm_ir
