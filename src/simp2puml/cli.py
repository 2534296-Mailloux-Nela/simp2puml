"""CLI de conversion entre les formats SIMP et PlantUML."""
import argparse
import os
from pathlib import Path
import sys
import tempfile

from . import __version__
from .model import ConversionError
from .puml import parse_puml, write_puml
from .simp import parse_simp, write_simp

MAX_INPUT_SIZE = 20 * 1024 * 1024
EXPERIMENTAL_WARNING = "La génération SIMP est expérimentale et sa compatibilité n'est pas validée."


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simp2puml",
        description="Convertit des diagrammes SIMP en PlantUML ; la conversion inverse est expérimentale.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("source", type=Path, help="fichier source .simp ou .puml")
    parser.add_argument("-o", "--output", type=Path, help="chemin de sortie (extension opposée requise)")
    parser.add_argument("--diagram", help="nom ou identifiant du diagramme (source SIMP uniquement)")

    parser.epilog = "La taille maximale du fichier source est de 20 MiB."
    return parser


def _same_file(source: Path, output: Path) -> bool:
    if source.resolve() == output.resolve():
        return True
    try:
        return os.path.samefile(source, output)
    except FileNotFoundError:
        return False


def _publish(output: Path, content: str) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=output.parent,
                                         prefix=f".{output.name}.", suffix=".tmp", delete=False) as temp:
            temp_path = Path(temp.name)
            temp.write(content)
            temp.flush()
            os.fsync(temp.fileno())
        os.link(temp_path, output)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    source: Path = args.source
    suffix = source.suffix.lower()
    if suffix not in (".simp", ".puml"):
        parser.error("l'extension source doit être .simp ou .puml")
    if args.diagram is not None and suffix != ".simp":
        parser.error("--diagram ne s'applique qu'aux sources .simp")
    expected_suffix = ".puml" if suffix == ".simp" else ".simp"
    output: Path = args.output if args.output is not None else source.with_suffix(expected_suffix)
    if output.suffix.lower() != expected_suffix:
        parser.error(f"l'extension de sortie doit être {expected_suffix}")
    try:
        if _same_file(source, output):
            raise ConversionError("la sortie ne peut pas être le fichier source")
        if output.exists():
            raise ConversionError(f"la sortie existe déjà : {output}")
        if source.stat().st_size > MAX_INPUT_SIZE:
            raise ConversionError("fichier source trop volumineux (maximum : 20 MiB)")
        text = source.read_text(encoding="utf-8-sig")
        if suffix == ".simp":
            diagram = parse_simp(text, diagram=args.diagram)
            content = write_puml(diagram)
        else:
            diagram = parse_puml(text)
            content = write_simp(diagram)
            diagram.warnings.append(EXPERIMENTAL_WARNING)
        _publish(output, content)
    except (OSError, UnicodeError, ConversionError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1

    for warning in diagram.warnings:
        print(f"Avertissement : {warning}", file=sys.stderr)
    print("Conversion terminée")
    print(f"Classes : {sum(cls.kind == 'class' for cls in diagram.classes)}")
    print(f"Relations : {len(diagram.relationships)}")
    for kind, label in (('interface', 'Interfaces'), ('enumeration', 'Énumérations'),
                        ('interface_symbol', 'Symboles d’interface')):
        count = sum(cls.kind == kind for cls in diagram.classes)
        if count:
            print(f"{label} : {count}")
    if diagram.notes:
        print(f"Notes : {len(diagram.notes)}")
    print(f"Avertissements : {len(diagram.warnings)}")
    print(f"Sortie : {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
