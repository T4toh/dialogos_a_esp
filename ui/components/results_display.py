"""
Componente para visualización de resultados del procesamiento.
"""

import json as _json
from pathlib import Path
from typing import Dict, List

import streamlit as st

from ..styles.themes import get_theme_colors


def display_results(results: List[Dict], output_dir: Path):
    """Muestra los resultados del procesamiento."""
    st.markdown("---")
    st.subheader("📊 Resultados")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    total_changes = sum(r.get("changes", 0) for r in successful)

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Exitosos", len(successful))
    with col2:
        st.metric("❌ Fallidos", len(failed))
    with col3:
        st.metric("🔄 Cambios totales", f"{total_changes:,}")

    # Detalles de archivos procesados
    if successful:
        st.success("Archivos procesados correctamente:")
        for result in successful:
            st.text(f"✓ {result['file']} → {result['changes']} cambios")

    if failed:
        st.error("Archivos con errores:")
        for result in failed:
            st.text(f"✗ {result['file']} → {result.get('error', 'Error desconocido')}")

    # Mostrar ruta de salida
    st.markdown("---")
    st.info(f"📁 **Archivos guardados en:** `{output_dir}`")

    # Visor de logs
    if successful:
        st.markdown("---")
        st.header("📄 Explorador de Cambios")
        st.markdown("Revisa los cambios realizados en cada archivo")

        # Iterar sobre todos los archivos procesados (ordenados alfabéticamente)
        sorted_results = sorted(successful, key=lambda x: x["file"])

        for idx, result in enumerate(sorted_results):
            _render_file_log_viewer(result, idx)


def _render_file_log_viewer(result: Dict, idx: int):
    """Renderiza el visor de logs para un archivo específico."""
    file_key = str(result.get("log_file", idx))

    with st.expander(
        f"📄 {result['file']} ({result['changes']} cambios)",
        expanded=(idx == 0),
    ):
        log_file = result.get("log_file")

        if log_file and Path(log_file).exists():
            # Intentar cargar JSON estructurado
            entries = _load_json_log(result)

            # Leer contenido textual del log
            current_log_content = Path(log_file).read_text(encoding="utf-8")

            # Opciones de visualización
            show_full, max_changes, show_diff_raw, inline_highlight = (
                _render_log_options(file_key, current_log_content)
            )

            # Mostrar cambios
            if entries is not None:
                _display_structured_log(
                    entries, show_full, max_changes, show_diff_raw, file_key
                )
            else:
                _display_textual_log(
                    current_log_content,
                    show_full,
                    max_changes,
                    show_diff_raw,
                    inline_highlight,
                )

            # Estadísticas de reglas
            _display_rule_statistics(current_log_content, result)
        else:
            st.warning("⚠️ No se encontró el archivo de log")


def _load_json_log(result: Dict):
    """Intenta cargar el log JSON estructurado."""
    json_log_path = None

    if result.get("json_log"):
        try:
            json_log_str = result.get("json_log")
            if json_log_str:
                json_log_path = Path(json_log_str)
        except Exception:
            pass
    else:
        # Fallback: reemplazar .log.txt con .log.json
        try:
            log_file = result.get("log_file")
            if log_file:
                candidate = str(log_file)
                if candidate.endswith(".log.txt"):
                    candidate_json = candidate[: -len(".log.txt")] + ".log.json"
                    json_log_path = Path(candidate_json)
        except Exception:
            pass

    if json_log_path and json_log_path.exists():
        try:
            structured = json_log_path.read_text(encoding="utf-8")
            return _json.loads(structured)
        except Exception:
            return None
    return None


def _render_log_options(file_key: str, log_content: str) -> tuple:
    """Renderiza las opciones de visualización del log."""
    col1, col2, col3 = st.columns(3)

    with col1:
        show_full = st.checkbox("Mostrar todos", value=False, key=f"full_{file_key}")

    with col2:
        max_changes = st.number_input(
            "Cambios a mostrar",
            min_value=5,
            max_value=500,
            value=50,
            step=5,
            disabled=show_full,
            key=f"max_{file_key}",
        )

    with col3:
        st.download_button(
            label="Descargar log",
            data=log_content,
            file_name=Path(file_key).name if file_key else "log.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"download_{file_key}",
        )

    # Opciones adicionales
    col4, col5 = st.columns([1, 2])

    with col4:
        show_diff_raw = st.checkbox(
            "Mostrar diff crudo", value=False, key=f"showdiffraw_{file_key}"
        )

    with col5:
        inline_highlight = st.checkbox(
            "Resaltar cambios inline", value=True, key=f"inline_{file_key}"
        )

    return show_full, max_changes, show_diff_raw, inline_highlight


def _display_structured_log(
    entries: List[Dict],
    show_full: bool,
    max_changes: int,
    show_diff_raw: bool,
    file_key: str,
):
    """Muestra el log estructurado (JSON)."""
    from .diff_viewer import render_structured_change

    st.markdown(
        "**Mostrando "
        + (f"{min(len(entries), max_changes)}" if not show_full else f"{len(entries)}")
        + f" de {len(entries)} cambios (JSON)**"
    )

    display_list = entries if show_full else entries[:max_changes]

    for idx_e, entry in enumerate(display_list, 1):
        render_structured_change(entry, idx_e, show_diff_raw)


def _display_textual_log(
    log_text: str,
    show_all: bool,
    max_to_show: int,
    show_diff_raw: bool,
    inline_highlight: bool,
):
    """Muestra el log textual parseado."""
    from .diff_viewer import parse_and_display_log

    parse_and_display_log(
        log_text, show_all, max_to_show, show_diff_raw, inline_highlight
    )


def _display_rule_statistics(log_content: str, result: Dict):
    """Muestra estadísticas de reglas aplicadas."""
    rules_count = {}
    for line in log_content.split("\n"):
        if "Regla aplicada:" in line or "Regla:" in line:
            rule = line.replace("Regla:", "").replace("Regla aplicada:", "").strip()
            rules_count[rule] = rules_count.get(rule, 0) + 1

    if rules_count:
        st.markdown("### Estadísticas")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Reglas más aplicadas:**")
            sorted_rules = sorted(rules_count.items(), key=lambda x: x[1], reverse=True)
            for rule, count in sorted_rules[:5]:
                st.text(f"{rule}: {count} veces")

        with col2:
            st.markdown("**Distribución:**")
            for rule, count in sorted_rules[:5]:
                percentage = (count / result["changes"]) * 100
                st.progress(percentage / 100, text=f"{rule}: {percentage:.1f}%")
