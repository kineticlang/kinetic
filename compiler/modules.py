from pathlib import Path

from .ast import Function, ImportDecl, Program, RecordDecl
from .errors import CompileError, KineticError
from .lexer import Lexer
from .parser import Parser


def resolve_imports(program: Program, source_path) -> Program:
    if not program.imports:
        return program
    if source_path is None:
        declaration = program.imports[0]
        _fail(
            declaration,
            "import declarations need a source file path to resolve; "
            "compile the file from disk and pass its path",
        )
    return _ModuleLoader().resolve(program, Path(source_path))


def load_program(source_path) -> Program:
    path = Path(source_path)
    tokens = Lexer(path.read_text(encoding="utf-8")).tokenize()
    program = Parser(tokens).parse()
    return resolve_imports(program, path)


def _fail(declaration: ImportDecl, message: str) -> None:
    location = declaration.location
    raise CompileError(
        message,
        location.line if location else None,
        location.column if location else None,
    )


def _canonical(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _is_relative(path: str) -> bool:
    if path.startswith(("/", "\\")):
        return False
    return not (
        len(path) > 1
        and path[1] == ":"
        and path[0].isascii()
        and path[0].isalpha()
    )


class _ModuleLoader:
    def __init__(self) -> None:
        self._loaded: set[Path] = set()
        self._loading: list[tuple[Path, str]] = []

    def resolve(self, program: Program, source_path: Path) -> Program:
        functions: list[Function] = []
        records: list[RecordDecl] = []
        self._loading.append((_canonical(source_path), source_path.name))
        self._collect(program, source_path, functions, records)
        self._loading.pop()
        return Program(functions, records)

    def _collect(
        self,
        program: Program,
        file_path: Path,
        functions: list[Function],
        records: list[RecordDecl],
    ) -> None:
        for declaration in program.imports:
            module_path = self._module_path(declaration, file_path)
            if module_path in self._loaded:
                continue
            if any(path == module_path for path, _ in self._loading):
                self._report_cycle(declaration, module_path)
            module_program = self._parse_module(declaration, module_path)
            self._reject_entry_point(declaration, module_program)
            self._loading.append((module_path, declaration.path))
            self._collect(module_program, module_path, functions, records)
            self._loading.pop()
            self._loaded.add(module_path)
        functions.extend(program.functions)
        records.extend(program.records)

    def _module_path(self, declaration: ImportDecl, file_path: Path) -> Path:
        path = declaration.path
        if not path:
            _fail(declaration, "import path cannot be empty")
        if not _is_relative(path):
            _fail(
                declaration,
                f"import path {path!r} must be relative to the importing file",
            )
        if "\\" in path:
            _fail(
                declaration,
                f"import path {path!r} must use forward slashes",
            )
        if Path(path).suffix != ".kn":
            _fail(
                declaration,
                f"imported module {path!r} must use the '.kn' extension",
            )
        return _canonical(file_path.parent / path)

    def _parse_module(self, declaration: ImportDecl, module_path: Path) -> Program:
        try:
            text = module_path.read_text(encoding="utf-8")
        except (OSError, ValueError) as error:
            reason = getattr(error, "strerror", None) or error
            _fail(
                declaration,
                f"cannot read imported module {declaration.path!r}: {reason}",
            )
        try:
            return Parser(Lexer(text).tokenize()).parse()
        except KineticError as error:
            raise CompileError(
                f"in imported module {declaration.path!r}: {error.message}",
                error.line,
                error.column,
            ) from error

    def _reject_entry_point(
        self, declaration: ImportDecl, module_program: Program
    ) -> None:
        entry = next(
            (
                function
                for function in module_program.functions
                if function.name == "main"
            ),
            None,
        )
        if entry is None:
            return
        location = entry.location
        raise CompileError(
            f"imported module {declaration.path!r} must not declare 'main'",
            location.line if location else None,
            location.column if location else None,
        )

    def _report_cycle(self, declaration: ImportDecl, module_path: Path) -> None:
        names = [name for _, name in self._loading]
        start = next(
            index
            for index, (path, _) in enumerate(self._loading)
            if path == module_path
        )
        chain = names[start:] + [declaration.path]
        _fail(
            declaration,
            "circular import: " + " -> ".join(repr(name) for name in chain),
        )
