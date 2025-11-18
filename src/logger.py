"""
Sistema de logging para registrar todos los cambios realizados.
"""

import difflib
import io
import json
from pathlib import Path
from typing import List, Optional


class ConversionLogger:
    """Registra y formatea los cambios realizados durante la conversión."""

    def __init__(self):
        # changes: list of dicts with detailed info and optional offsets
        self.changes: List[dict] = []
        self.line_number = 0
        # Threshold tuning for when to fallback to the full text
        # (useful for multi-sentence fragments). Make configurable for tests.
        self.full_text_ratio = 1.5

    def log_change(
        self,
        line_num: int,
        original: str,
        converted: str,
        rule: str,
        original_fragment: Optional[str] = None,
        converted_fragment: Optional[str] = None,
        full_text: Optional[str] = None,
        full_converted: Optional[str] = None,
    ):
        """
        Registra un cambio realizado.
            Args:
                line_num: Número de línea (aproximado)
                original: Texto original
                converted: Texto convertido
                rule: Regla aplicada
        """
        # Format texts for consistent storage and UI highlighting
        formatted_original = self._format_text(original or "")
        formatted_converted = self._format_text(converted or "")

        # Also format fragments (best-effort) so offsets align with formatted texts
        formatted_orig_frag = (
            self._format_text(original_fragment or "") if original_fragment else None
        )
        formatted_conv_frag = (
            self._format_text(converted_fragment or "") if converted_fragment else None
        )

        record = {
            "line": line_num,
            "rule": rule,
            "original": formatted_original,
            "converted": formatted_converted,
            "original_fragment": formatted_orig_frag,
            "converted_fragment": formatted_conv_frag,
            "original_span": None,
            "converted_span": None,
            "original_span_source": None,
            "converted_span_source": None,
        }

        # Skip logging if the formatted original and converted are identical
        # (no visible change). This reduces noisy 'no-op' CAMBIO entries
        # where ODT style or token alignment produced no textual change.
        # Only suppress logs for additional dialogues (D1) that are
        # effectively no-ops (the visible text didn't change). Other
        # rules should still be logged for auditing and offsets.
        if (
            rule.startswith("D1: Diálogo adicional")
            and formatted_original.strip() == formatted_converted.strip()
        ):
            return
        # Threshold beyond which we allow falling back to the full_text
        # because the fragment seems to be multi-sentence and sentence
        # extraction trimmed the context. Tuned to avoid logging huge
        # blocks for small fragments.
        FULL_TEXT_RATIO = getattr(self, "full_text_ratio", 1.5)

        # Compute spans against formatted strings (preferred)
        try:
            if formatted_orig_frag:
                idx = formatted_original.find(formatted_orig_frag)
                if idx != -1:
                    record["original_span"] = [idx, idx + len(formatted_orig_frag)]
                    record["original_span_source"] = "exact"
        except Exception:
            record["original_span"] = None

        try:
            if formatted_conv_frag:
                jdx = formatted_converted.find(formatted_conv_frag)
                if jdx != -1:
                    record["converted_span"] = [jdx, jdx + len(formatted_conv_frag)]
                    record["converted_span_source"] = "exact"
        except Exception:
            record["converted_span"] = None

        # If straightforward find fails, try a fuzzy longest-match fallback
        # (handles cases where the fragment contains surrounding sentences
        #  or extra punctuation not present in the formatted block)
        if record.get("original_span") is None and formatted_orig_frag:
            try:
                from difflib import SequenceMatcher

                sm = SequenceMatcher(None, formatted_original, formatted_orig_frag)
                match = max(sm.get_matching_blocks(), key=lambda mb: mb.size)
                # Only accept fuzzy match if it's a reasonable fraction of
                # the fragment length; otherwise prefer full_text if available
                # (avoid tiny partial matches that cause truncated spans)
                FUZZY_MIN_RATIO = 0.6
                if match.size > 3 and match.size >= FUZZY_MIN_RATIO * max(
                    1, len(formatted_orig_frag)
                ):
                    record["original_span"] = [match.a, match.a + match.size]
                    record["original_span_source"] = "fuzzy"
            except Exception:
                pass

        if record.get("converted_span") is None and formatted_conv_frag:
            try:
                from difflib import SequenceMatcher

                sm2 = SequenceMatcher(None, formatted_converted, formatted_conv_frag)
                match2 = max(sm2.get_matching_blocks(), key=lambda mb: mb.size)
                FUZZY_MIN_RATIO = 0.6
                if match2.size > 3 and match2.size >= FUZZY_MIN_RATIO * max(
                    1, len(formatted_conv_frag)
                ):
                    record["converted_span"] = [match2.a, match2.a + match2.size]
                    record["converted_span_source"] = "fuzzy"
            except Exception:
                pass

        # As a last resort, try to compute spans against raw fragments
        # if formatted search failed
        if record.get("original_span") is None and original_fragment and original:
            try:
                idx2 = (original or "").find(original_fragment)
                if idx2 != -1:
                    # Attempt to map raw index to formatted index by
                    # searching substring around fragment
                    # Fallback: use formatted_original.find(original_fragment) directly
                    idx_alt = formatted_original.find(original_fragment)
                    if idx_alt != -1:
                        record["original_span"] = [
                            idx_alt,
                            idx_alt + len(original_fragment),
                        ]
                        record["original_span_source"] = "raw"
            except Exception:
                pass

        if record.get("converted_span") is None and converted_fragment and converted:
            try:
                jdx2 = (converted or "").find(converted_fragment)
                if jdx2 != -1:
                    jdx_alt = formatted_converted.find(converted_fragment)
                    if jdx_alt != -1:
                        record["converted_span"] = [
                            jdx_alt,
                            jdx_alt + len(converted_fragment),
                        ]
                        record["converted_span_source"] = "raw"
            except Exception:
                pass

        # If still not found we can try searching against the full_text
        # This is used when the 'original' argument holds only a sentence
        # but the original fragment belongs to a larger block (user requested
        # full-block logging). In that case, look in 'full_text'.
        if (
            full_text
            and record.get("original_span") is None
            and formatted_orig_frag
            and len(formatted_orig_frag)
            > FULL_TEXT_RATIO * max(1, len(formatted_original or ""))
        ):
            try:
                formatted_full = self._format_text(full_text)
                idx_full = formatted_full.find(formatted_orig_frag)
                if idx_full != -1:
                    record["original_span"] = [
                        idx_full,
                        idx_full + len(formatted_orig_frag),
                    ]
                    # Use the full block as the stored original for JSON
                    # so UI sees context
                    record["original"] = formatted_full
                    record["original_span_source"] = "full_text"
            except Exception:
                pass

        if (
            full_text
            and record.get("converted_span") is None
            and formatted_conv_frag
            and len(formatted_conv_frag)
            > FULL_TEXT_RATIO * max(1, len(formatted_converted or ""))
        ):
            try:
                # Prefer searching converted text if provided, otherwise fall back
                # to the raw original text as a last resort
                search_target = (
                    self._format_text(full_converted)
                    if full_converted
                    else self._format_text(full_text)
                )
                jdx_full = search_target.find(formatted_conv_frag)
                if jdx_full != -1:
                    record["converted_span"] = [
                        jdx_full,
                        jdx_full + len(formatted_conv_frag),
                    ]
                    record["converted"] = search_target
                    record["converted_span_source"] = "full_converted"
            except Exception:
                pass

        # Older fallback logic (full_text tries) was replaced with a ratio
        # check above; leave this space intentionally to avoid re-running
        # an identical heuristic and doing full_text twice.

        # Extra heuristic: when converted_span is still missing, try a
        # punctuation-normalized find. This helps in cases where the
        # converted fragment contains em-dashes, ellipses, or typographic
        # quotes that differ from the formatted block and would otherwise
        # yield deletion-only diffs in the UI.
        if record.get("converted_span") is None and formatted_conv_frag:
            try:

                def _normalize_punct(s: str) -> str:
                    return (
                        s.replace("—", "-")
                        .replace("…", "...")
                        .replace("“", '"')
                        .replace("”", '"')
                        .replace("‚", "'")
                    )

                # normalized converted text not directly used — keep frag norm
                norm_conv_frag = _normalize_punct(formatted_conv_frag)

                # Best-effort: scan formatted_converted for a substring that
                # normalizes to the fragment. This preserves real converted
                # highlights even when punctuation differs.
                found = None
                L = len(formatted_conv_frag)
                for i in range(0, max(1, len(formatted_converted) - max(0, L - 1))):
                    candidate = formatted_converted[i : i + L]
                    if _normalize_punct(candidate) == norm_conv_frag:
                        found = (i, i + L)
                        break

                if found:
                    record["converted_span"] = [found[0], found[1]]
                    record["converted_span_source"] = "normalized"
            except Exception:
                pass

        self.changes.append(record)

    def _format_text(self, text: str) -> str:
        """
        Formatea texto para el log sin truncar, preservando saltos de línea.
        Normaliza espacios dentro de cada línea pero mantiene la estructura
        de párrafos para poder mostrar bloques completos.

        Args:
            text: Texto a formatear
        Returns:
            Texto formateado
        """
        if text is None:
            return ""
        # Normalizar cada línea por separado para preservar saltos de línea
        lines = text.splitlines()
        norm_lines: List[str] = [" ".join(line.split()) for line in lines]
        return "\n".join(norm_lines)

    def generate_report(self) -> str:
        """
        Genera el reporte completo de cambios.
            Returns:
                String con el reporte formateado
        """
        buffer = io.StringIO()

        buffer.write("LOG DE CONVERSIÓN DE DIÁLOGOS A FORMATO ESPAÑOL\n")
        buffer.write("=" * 80 + "\n\n")

        buffer.write(f"Total de cambios realizados: {len(self.changes)}\n\n")

        if not self.changes:
            buffer.write("No se realizaron cambios.\n")
            return buffer.getvalue()

        for idx, rec in enumerate(self.changes, 1):
            line_num = rec.get("line")
            original = rec.get("original")
            converted = rec.get("converted")
            rule = rec.get("rule")

            buffer.write(f"CAMBIO #{idx}\n")
            buffer.write(f"Línea: ~{line_num}\n")
            buffer.write(f"Regla: {rule}\n\n")

            # Formatear sin truncar
            original_display = self._format_text(original or "")
            converted_display = self._format_text(converted or "")

            buffer.write("ORIGINAL:\n")
            buffer.write(f"  {original_display}\n\n")

            buffer.write("CONVERTIDO:\n")
            buffer.write(f"  {converted_display}\n\n")

            # Añadir diff unificado para facilitar revisión inline
            try:
                orig_lines = original_display.splitlines(keepends=False)
                conv_lines = converted_display.splitlines(keepends=False)
                diff_lines = list(
                    difflib.unified_diff(
                        orig_lines,
                        conv_lines,
                        fromfile="original",
                        tofile="convertido",
                        lineterm="",
                        n=3,
                    )
                )
            except Exception:
                diff_lines = []

            if diff_lines:
                buffer.write("DIFF (unified):\n")
                for dl in diff_lines:
                    buffer.write(f"  {dl}\n")
                buffer.write("\n")

            buffer.write("-" * 80 + "\n\n")

        return buffer.getvalue()

    def save_structured_log(self, filepath: Path):
        """
        Guarda un log estructurado en JSON con diffs incluidos.
        Esto permite inspección programática o visualizaciones externas.
        """
        out = []
        for rec in self.changes:
            orig_display = self._format_text(rec.get("original") or "")
            conv_display = self._format_text(rec.get("converted") or "")
            diff = "\n".join(
                difflib.unified_diff(
                    orig_display.splitlines(),
                    conv_display.splitlines(),
                    fromfile="original",
                    tofile="convertido",
                    lineterm="",
                    n=3,
                )
            )
            out_rec = {
                "line": rec.get("line"),
                "rule": rec.get("rule"),
                "original": orig_display,
                "converted": conv_display,
                "diff": diff,
                "original_fragment": rec.get("original_fragment"),
                "converted_fragment": rec.get("converted_fragment"),
                "original_span": rec.get("original_span"),
                "converted_span": rec.get("converted_span"),
                "original_span_source": rec.get("original_span_source"),
                "converted_span_source": rec.get("converted_span_source"),
            }
            out.append(out_rec)

        filepath.write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def save_to_file(self, filepath: Path):
        """
        Guarda el log en un archivo.
            Args:
                filepath: Ruta del archivo de log
        """
        report = self.generate_report()
        filepath.write_text(report, encoding="utf-8")

    def post_process_line_spans(self, line_num: int, converted_full_text: str):
        """
        After a whole line is converted, try to enrich/change entries for
        that line to find missing converted_span values by searching the
        formatted converted line.

        This is useful because some converted fragments include punctuation
        (em-dashes, etc.) that will only be present in the converted text
        and not in the original; searching against the final converted
        line increases the likelihood of finding a converted_span.
        """
        formatted_conv_full = self._format_text(converted_full_text or "")

        for rec in self.changes:
            if rec.get("line") != line_num:
                continue

            if rec.get("converted_span") is not None:
                continue

            formatted_conv_frag = rec.get("converted_fragment")
            if not formatted_conv_frag:
                continue

            # Try direct find
            try:
                jdx = formatted_conv_full.find(formatted_conv_frag)
                if jdx != -1:
                    rec["converted_span"] = [jdx, jdx + len(formatted_conv_frag)]
                    rec["converted"] = formatted_conv_full
                    continue
            except Exception:
                pass

            # Fuzzy fallback
            try:
                from difflib import SequenceMatcher

                sm = SequenceMatcher(None, formatted_conv_full, formatted_conv_frag)
                match = max(sm.get_matching_blocks(), key=lambda mb: mb.size)
                if match.size > 3:
                    rec["converted_span"] = [match.a, match.a + match.size]
                    continue
            except Exception:
                pass

            # Normalized punctuation scan
            try:

                def _normalize_punct(s: str) -> str:
                    return (
                        s.replace("—", "-")
                        .replace("…", "...")
                        .replace("“", '"')
                        .replace("”", '"')
                        .replace("‚", "'")
                    )

                norm_frag = _normalize_punct(formatted_conv_frag)

                for i in range(
                    max(1, len(formatted_conv_full) - len(formatted_conv_frag) + 1)
                ):
                    if (
                        _normalize_punct(
                            formatted_conv_full[i : i + len(formatted_conv_frag)]
                        )
                        == norm_frag
                    ):
                        rec["converted_span"] = [i, i + len(formatted_conv_frag)]
                        rec["converted"] = formatted_conv_full
                        break
            except Exception:
                pass

    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de la conversión.
            Returns:
                Diccionario con estadísticas
        """
        return {
            "total_changes": len(self.changes),
            "rules_applied": list({rec.get("rule") for rec in self.changes}),
        }
