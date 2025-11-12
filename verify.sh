#!/bin/bash
# Script de verificación rápida del proyecto

set -e

echo "=========================================="
echo "Verificación del proyecto dialogos_a_español"
echo "=========================================="
echo

# Verificar Python
echo "✓ Verificando Python..."
python --version

echo
echo "✓ Ejecutando tests..."
python -m unittest tests.test_converter -q

echo
echo "✓ Procesando ejemplo corto..."
python -m src.main examples/ejemplo.txt -q

echo
echo "✓ Procesando ejemplo largo..."
python -m src.main examples/ejemplo_largo.txt -q

echo
echo "✓ Verificando archivos generados..."
ls -lh examples/*_convertido.txt examples/*_convertido.log.txt 2>/dev/null | tail -4

echo
echo "=========================================="
echo "✓ Todas las verificaciones pasaron"
echo "=========================================="
echo
echo "El proyecto está listo para usar:"
echo "  python -m src.main tu_archivo.txt"
echo
