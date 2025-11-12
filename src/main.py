"""
CLI principal para la conversión de diálogos.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .converter import DialogConverter
from .odt_handler import ODTReader, ODTWriter, ODTProcessor, is_odt_file


def setup_argparse() -> argparse.ArgumentParser:
    """
    Configura el parser de argumentos de línea de comandos.
    
    Returns:
        ArgumentParser configurado
    """
    parser = argparse.ArgumentParser(
        description='Convierte diálogos narrativos con comillas al formato editorial español con raya (—).',
        epilog='Genera dos archivos: texto convertido (.txt) y log detallado (.log.txt)'
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Archivo de texto de entrada con diálogos entre comillas'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Archivo de salida (por defecto: {input}_convertido.txt)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Modo silencioso (no mostrar estadísticas)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='dialogos_a_español 1.3.0'
    )
    
    return parser


def determine_output_path(input_path: Path, output_arg: Optional[str]) -> Path:
    """
    Determina la ruta del archivo de salida.
    
    Args:
        input_path: Ruta del archivo de entrada
        output_arg: Argumento de salida (puede ser None)
        
    Returns:
        Path del archivo de salida
    """
    if output_arg:
        return Path(output_arg)
    
    # Por defecto: {nombre}_convertido.txt
    stem = input_path.stem
    return input_path.parent / f"{stem}_convertido.txt"


def main():
    """Función principal del CLI."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Validar archivo de entrada
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: El archivo '{args.input_file}' no existe.", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.is_file():
        print(f"Error: '{args.input_file}' no es un archivo.", file=sys.stderr)
        sys.exit(1)
    
    # Detectar si es ODT
    is_odt = is_odt_file(input_path)
    
    # Determinar archivo de salida
    output_path = determine_output_path(input_path, args.output)
    
    # Si la entrada es ODT, la salida también debe serlo
    if is_odt and args.output is None:
        output_path = output_path.with_suffix('.odt')
    
    log_path = output_path.parent / f"{output_path.stem}.log.txt"
    
    if not args.quiet:
        print(f"Procesando: {input_path}")
        if is_odt:
            print(f"Formato detectado: ODT")
        print(f"Salida: {output_path}")
        print(f"Log: {log_path}")
        print()
    
    try:
        # Leer archivo de entrada
        if not args.quiet:
            print("Leyendo archivo de entrada...")
        
        if is_odt:
            # Leer ODT
            reader = ODTReader(input_path)
            text = reader.extract_text()
            if not args.quiet:
                print(f"  Texto extraído: {len(text)} caracteres")
        else:
            # Leer TXT
            text = input_path.read_text(encoding='utf-8')
        
        # Convertir
        if not args.quiet:
            print("Convirtiendo diálogos...")
        
        converter = DialogConverter()
        converted_text, logger = converter.convert(text)
        
        # Guardar resultados
        if not args.quiet:
            print("Guardando archivos...")
        
        if is_odt or (args.output and Path(args.output).suffix.lower() == '.odt'):
            # Guardar como ODT PRESERVANDO ESTRUCTURA
            if is_odt:
                # Usar el procesador que preserva estructura
                processor = ODTProcessor(input_path)
                converter_inst = DialogConverter()
                processor.process_and_save(output_path, converter_inst.convert)
                if not args.quiet:
                    print(f"  Guardado como ODT (estructura preservada)")
            else:
                # Modo simple si la entrada no es ODT
                writer = ODTWriter(output_path)
                writer.write_text(converted_text)
                if not args.quiet:
                    print(f"  Guardado como ODT")
        else:
            # Guardar como TXT
            output_path.write_text(converted_text, encoding='utf-8')
        
        logger.save_to_file(log_path)
        
        # Mostrar estadísticas
        if not args.quiet:
            stats = logger.get_stats()
            print()
            print("✓ Conversión completada exitosamente")
            print(f"  Total de cambios: {stats['total_changes']}")
            print(f"  Reglas aplicadas: {len(stats['rules_applied'])}")
            print()
            print(f"Archivos generados:")
            print(f"  - {output_path}")
            print(f"  - {log_path}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error durante la conversión: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
