"""
Visualizador de diffs para cambios en el texto.
Contiene la lógica compleja de parsing y renderizado de diffs.
"""

import difflib
import html as _html
from typing import Dict

import streamlit as st

from ..styles.themes import get_theme_colors


def render_structured_change(entry: Dict, idx: int, show_diff_raw: bool):
    """Renderiza un cambio estructurado desde JSON."""
    with st.container():
        st.markdown(f"**CAMBIO #{idx}**")
        st.markdown(
            "*Línea ~" + str(entry.get("line")) + " • " + str(entry.get("rule")) + "*"
        )

        orig_text = entry.get("original", "")
        conv_text = entry.get("converted", "")
        orig_span = entry.get("original_span")
        conv_span = entry.get("converted_span")

        theme = st.session_state.get("theme", "dark")
        inline_html = build_inline_html_from_spans(
            orig_text, conv_text, orig_span, conv_span, theme
        )

        # Mostrar la fuente de los spans (útil para depuración)
        if entry.get("original_span_source") or entry.get("converted_span_source"):
            span_source_line = (
                "(span: orig="
                + str(entry.get("original_span_source"))
                + ", conv="
                + str(entry.get("converted_span_source"))
                + ")"
            )
            st.markdown(
                "<small style='color:gray'>" + span_source_line + "</small>",
                unsafe_allow_html=True,
            )

        st.markdown(inline_html, unsafe_allow_html=True)

        if entry.get("diff") and show_diff_raw:
            st.markdown("**Diff (unified):**")
            st.code(entry.get("diff"), language="diff")

        st.markdown("---")


def parse_and_display_log(
    log_text: str,
    show_all: bool,
    max_to_show: int,
    show_diff_raw: bool = False,
    inline_highlight: bool = True,
):
    """
    Parse y muestra cambios del log textual.
    Captura bloques completos (preserva saltos de línea).
    """
    all_changes_local = []
    current_change_local = None
    section = None

    for raw in log_text.splitlines():
        # Detectar inicio de cambio
        if raw.startswith("CAMBIO #"):
            if current_change_local:
                all_changes_local.append(current_change_local)
            current_change_local = {
                "numero": raw.strip(),
                "ubicacion": "",
                "regla": "",
                "original": [],
                "convertido": [],
                "diff": [],
            }
            section = None
            continue

        if current_change_local is None:
            continue

        stripped = raw.strip()
        if stripped.startswith("Línea:"):
            current_change_local["ubicacion"] = stripped.replace("Línea:", "").strip()
            continue
        if stripped.startswith("Regla:"):
            current_change_local["regla"] = stripped.replace("Regla:", "").strip()
            continue

        if stripped == "ORIGINAL:":
            section = "original"
            continue
        if stripped == "CONVERTIDO:":
            section = "convertido"
            continue
        if stripped == "DIFF (unified):":
            section = "diff"
            continue

        # Separator line - finalize current change
        if stripped.startswith("-----"):
            if current_change_local:
                all_changes_local.append(current_change_local)
                current_change_local = None
            section = None
            continue

        # Según la sección actual, agregar la línea (preservando saltos)
        if section == "original":
            line_content = raw[2:] if raw.startswith("  ") else raw
            current_change_local["original"].append(line_content)
        elif section == "convertido":
            line_content = raw[2:] if raw.startswith("  ") else raw
            current_change_local["convertido"].append(line_content)
        elif section == "diff":
            line_content = raw[2:] if raw.startswith("  ") else raw
            current_change_local["diff"].append(line_content)

    if current_change_local:
        all_changes_local.append(current_change_local)

    # Mostrar cambios
    changes_to_show_local = (
        all_changes_local if show_all else all_changes_local[:max_to_show]
    )
    st.markdown(
        "**Mostrando "
        + f"{len(changes_to_show_local)}"
        + f" de {len(all_changes_local)} cambios**"
    )

    for change in changes_to_show_local:
        _render_textual_change(change, show_diff_raw, inline_highlight)


def _render_textual_change(change: Dict, show_diff_raw: bool, inline_highlight: bool):
    """Renderiza un cambio individual del log textual."""
    with st.container():
        orig_text = (
            "\n".join(change["original"]).strip() if change["original"] else "N/A"
        )
        conv_text = (
            "\n".join(change["convertido"]).strip() if change["convertido"] else "N/A"
        )
        diff_text = "\n".join(change["diff"]).strip() if change["diff"] else None

        st.markdown(f"**{change['numero']}**")
        st.markdown(f"*Línea {change['ubicacion']} • {change['regla']}*")

        # Paleta dependiente del tema
        theme = st.session_state.get("theme", "dark")
        colors = get_theme_colors(theme)

        if inline_highlight:
            try:
                inline_html = build_inline_diff_html(orig_text, conv_text, colors)
                inline_title = (
                    "<div style='margin-bottom:6px'><strong>Inline diff:</strong></div>"
                )
                st.markdown(inline_title + inline_html, unsafe_allow_html=True)

                # También mostrar bloques completos para contexto
                _render_text_blocks(orig_text, conv_text, colors)
            except Exception:
                _render_text_blocks(orig_text, conv_text, colors)
        else:
            _render_text_blocks(orig_text, conv_text, colors)

        # Mostrar diff unificado solo si el usuario lo pidió
        if diff_text and show_diff_raw:
            st.markdown("**Diff (unified):**")
            st.code(diff_text, language="diff")

        st.markdown("---")


def _render_text_blocks(orig_text: str, conv_text: str, colors: dict):
    """Renderiza bloques de texto original y convertido."""
    orig_html = (
        f"<div style='background:{colors['orig_bg']};"
        f"color:{colors['orig_color']};"
        "border-radius:6px;padding:10px;white-space:pre-wrap;"
        "font-family:monospace;'><strong>Original:</strong>\n" + orig_text + "</div>"
    )
    st.markdown(orig_html, unsafe_allow_html=True)

    conv_html = (
        f"<div style='background:{colors['conv_bg']};"
        f"color:{colors['conv_color']};"
        "border-radius:6px;padding:10px;white-space:pre-wrap;"
        "font-family:monospace;'><strong>Convertido:</strong>\n" + conv_text + "</div>"
    )
    st.markdown(conv_html, unsafe_allow_html=True)


def build_inline_diff_html(orig: str, conv: str, colors: dict) -> str:
    """Construye HTML con diff inline a nivel de palabra."""

    def _make_span(text, bg, color, strike=False):
        style_parts = [f"background:{bg};", f"color:{color};"]
        if strike:
            style_parts.append("text-decoration:line-through;")
        style_parts.append("padding:2px;")
        style_parts.append("border-radius:3px;")
        style_parts.append("margin-right:2px;")
        style = "".join(style_parts)
        return f"<span style='{style}'>{text}</span>"

    a_words = [w for w in orig.split()]
    b_words = [w for w in conv.split()]
    matcher = difflib.SequenceMatcher(None, a_words, b_words)
    parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            parts.append(" ".join(a_words[i1:i2]))
        elif tag == "replace":
            removed = " ".join(a_words[i1:i2])
            added = " ".join(b_words[j1:j2])
            if removed:
                parts.append(
                    _make_span(removed, colors["del_bg"], colors["orig_color"], True)
                )
            if added:
                parts.append(_make_span(added, colors["ins_bg"], colors["conv_color"]))
        elif tag == "delete":
            removed = " ".join(a_words[i1:i2])
            parts.append(
                _make_span(removed, colors["del_bg"], colors["orig_color"], True)
            )
        elif tag == "insert":
            added = " ".join(b_words[j1:j2])
            parts.append(_make_span(added, colors["ins_bg"], colors["conv_color"]))

    return (
        '<div style="white-space:pre-wrap;font-family:monospace;">'
        + " ".join(parts)
        + "</div>"
    )


def build_inline_html_from_spans(
    orig: str, conv: str, orig_span, conv_span, theme="dark"
) -> str:
    """Construye HTML con highlighting basado en spans precisos."""
    colors = get_theme_colors(theme)

    # Si tenemos ambos spans
    if orig_span and conv_span:
        ostart, oend = orig_span
        cstart, cend = conv_span

        before_o = _html.escape(orig[:ostart])
        frag_o = _html.escape(orig[ostart:oend])
        after_o = _html.escape(orig[oend:])

        before_c = _html.escape(conv[:cstart])
        frag_c = _html.escape(conv[cstart:cend])
        after_c = _html.escape(conv[cend:])

        parts = []

        # Original con deletion highlight
        orig_template = (
            "<div style='background:transparent;"
            "color:{color};"
            "white-space:pre-wrap;font-family:monospace;'>"
            "<strong>Original:</strong><br>"
            "{before}<span style='background:{del_bg};"
            "color:{color};text-decoration:line-through;"
            "padding:2px;border-radius:3px;'>{frag}</span>"
            "{after}</div>"
        )
        parts.append(
            orig_template.format(
                color=colors["orig_color"],
                before=before_o,
                frag=frag_o,
                del_bg=colors["del_bg"],
                after=after_o,
            )
        )

        # Convertido con insertion highlight
        conv_template = (
            "<div style='background:transparent;color:{color};"
            "white-space:pre-wrap;font-family:monospace;'>"
            "<strong>Convertido:</strong><br>"
            "{before}<span style='background:{ins_bg};"
            "color:{color};padding:2px;border-radius:3px;'>{frag}</span>{after}</div>"
        )
        parts.append(
            conv_template.format(
                color=colors["conv_color"],
                before=before_c,
                frag=frag_c,
                ins_bg=colors["ins_bg"],
                after=after_c,
            )
        )

        return "<div style='margin-bottom:6px'>" + "".join(parts) + "</div>"

    # Si solo tenemos un span
    elif orig_span or conv_span:
        parts = []

        if orig_span:
            ostart, oend = orig_span
            before_o = _html.escape(orig[:ostart])
            frag_o = _html.escape(orig[ostart:oend])
            after_o = _html.escape(orig[oend:])
            parts.append(
                (
                    "<div style='background:transparent;"
                    "color:{color};"
                    "white-space:pre-wrap;font-family:monospace;'>"
                    "<strong>Original:</strong><br>"
                    "{before}<span style='background:{del_bg};"
                    "color:{color};text-decoration:line-through;"
                    "padding:2px;border-radius:3px;'>{frag}</span>"
                    "{after}</div>"
                ).format(
                    color=colors["orig_color"],
                    before=before_o,
                    frag=frag_o,
                    del_bg=colors["del_bg"],
                    after=after_o,
                )
            )

        if conv_span:
            cstart, cend = conv_span
            before_c = _html.escape(conv[:cstart])
            frag_c = _html.escape(conv[cstart:cend])
            after_c = _html.escape(conv[cend:])
            parts.append(
                (
                    "<div style='background:transparent;"
                    "color:{color};"
                    "white-space:pre-wrap;font-family:monospace;'>"
                    "<strong>Convertido:</strong><br>"
                    "{before}<span style='background:{ins_bg};"
                    "color:{color};padding:2px;border-radius:3px;'>{frag}</span>{after}</div>"
                ).format(
                    color=colors["conv_color"],
                    before=before_c,
                    frag=frag_c,
                    ins_bg=colors["ins_bg"],
                    after=after_c,
                )
            )

        return "<div style='margin-bottom:6px'>" + "".join(parts) + "</div>"

    # Fallback a word-level diff
    try:
        return build_inline_diff_html(orig, conv, colors)
    except Exception:
        return (
            "<div><pre>"
            + _html.escape(orig)
            + "\n---\n"
            + _html.escape(conv)
            + "</pre></div>"
        )
