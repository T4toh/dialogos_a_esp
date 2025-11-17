"""
Script principal para conversión de diálogos.
Soporta archivos individuales y procesamiento de carpetas.
"""

import argparse
import sys
from pathlib import Path

from .batch_processor import BatchProcessor
from .converter import DialogConverter
from .odt_handler import ODTProcessor, is_odt_file


def create_parser():
    """Crea y configura el parser de argumentos."""
    parser = argparse.ArgumentParser(
        description="Convierte diálogos con comillas al formato español con raya (—)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Archivo individual
  python -m src.main mi_capitulo.odt

  # Carpeta completa (crea subcarpeta 'convertidos/')
  python -m src.main mi_novela/

  # Especificar carpeta de salida
  python -m src.main mi_novela/ -o resultados/

  # Solo archivos ODT
  python -m src.main mi_novela/ --filter "*.odt"

  # Incluir subcarpetas
  python -m src.main mi_novela/ --recursive

Para más información, ver README.md
    """,
    )

    parser.add_argument(
        "input", type=str, help="Archivo o carpeta a procesar (.txt, .odt)"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Archivo o carpeta de salida (default: _convertido o subcarpeta convertidos/)",
    )

    parser.add_argument(
        "--filter",
        type=str,
        default="*.*",
        help='Patrón de archivos en modo carpeta (ej: "*.odt")',
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Procesar subcarpetas (solo en modo carpeta)",
    )

    parser.add_argument("-q", "--quiet", action="store_true", help="Modo silencioso")

    parser.add_argument(
        "--version", action="version", version="dialogos_a_español 1.4.0"
    )

    return parser


def main():
    """Función principal."""
    parser = create_parser()
    args = parser.parse_args()

    # Validar entrada
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: No existe '{args.input}'")
        sys.exit(1)

    # Determinar modo
    if input_path.is_dir():
        process_directory(input_path, args)
    else:
        process_file(input_path, args)


def process_directory(input_dir: Path, args):
    """Procesa una carpeta completa."""
    output_dir = Path(args.output) if args.output else input_dir / "convertidos"

    converter = DialogConverter()
    batch = BatchProcessor(converter)

    result = batch.process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        pattern=args.filter,
        recursive=args.recursive,
    )

    sys.exit(0 if result["success"] and result["files_processed"] > 0 else 1)


def process_file(input_path: Path, args):
    """Procesa un archivo individual."""
    # Salida
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = (
            input_path.parent / f"{input_path.stem}_convertido{input_path.suffix}"
        )

    log_path = output_path.parent / f"{output_path.stem}.log.txt"

    # Info
    if not args.quiet:
        print(f"Procesando: {input_path}")
        print(f"Formato detectado: {'ODT' if is_odt_file(input_path) else 'TXT'}")
        print(f"Salida: {output_path}")
        print(f"Log: {log_path}\n")

    try:
        converter = DialogConverter()

        if is_odt_file(input_path):
            # ODT
            if not args.quiet:
                print("Leyendo archivo de entrada...")

            processor = ODTProcessor(input_path)
            processor.process_and_save(output_path, converter.convert)
            log_content = converter.logger.generate_report()

        else:
            # TXT
            if not args.quiet:
                print("Leyendo archivo de entrada...")

            with open(input_path, "r", encoding="utf-8") as f:
                input_text = f.read()

            if not args.quiet:
                print(f"  Texto extraído: {len(input_text)} caracteres")
                print("Convirtiendo diálogos...")

            converted_text, logger = converter.convert(input_text)

            if not args.quiet:
                print("Guardando archivos...")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(converted_text)

            log_content = logger.generate_report()

        # Log
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_content)

        # Resumen
        if not args.quiet:
            if is_odt_file(input_path):
                print("  Guardado como ODT (estructura y formato preservados)")

            print("\n✓ Conversión completada exitosamente")

            changes = converter.logger.changes
            rules_applied = set(c[3] for c in changes) if changes else set()

            print(f"  Total de cambios: {len(changes)}")
            print(f"  Reglas aplicadas: {len(rules_applied)}\n")
            print("Archivos generados:")
            print(f"  - {output_path}")
            print(f"  - {log_path}")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
