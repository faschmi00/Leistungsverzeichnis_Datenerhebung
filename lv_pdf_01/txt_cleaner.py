import re

class TxtCleaner:

    def clean_document(self, input_txt: str, output_txt: str) -> None:

        lines = self._read_file(input_txt)

        lines = self._remove_first_page(lines)

        lines = self._remove_table_headers(lines)

        lines = self._remove_footer(lines)

        lines = self._remove_page_markers(lines)

        self._write_file(output_txt, lines)

    def _remove_first_page(self, lines: list[str]) -> list[str]:
        """
        Entfernt alles bis einschließlich der Zeile:
        '===== SEITE 2 ====='
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 2 =====":
                # alles davor + diese Zeile entfernen
                return lines[index + 1:]

        return lines

    def _remove_table_headers(self, lines: list[str]) -> list[str]:
        """
        Entfernt Header mit folgendem Muster (zweizeilig):

        Leistungs-
        nummer Menge ME Beschreibung €

        bennötigt falls Eintrag über zwei Seiten geht
        """
        cleaned = []
        skip_next = False

        for i in range(len(lines)):
            if skip_next:
                skip_next = False
                continue

            current = lines[i].strip()

            # Prüfe Zeile 1 des Headers
            if current.startswith("Leistungs-"):
                # Prüfe nächste Zeile
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if (
                            "nummer" in next_line
                            and "Menge" in next_line
                            and "ME" in next_line
                            and "Beschreibung" in next_line
                    ):
                        skip_next = True  # auch nächste Zeile überspringen
                        continue  # aktuelle Zeile überspringen

            cleaned.append(lines[i])

        return cleaned

    def _remove_footer(self, lines: list[str]) -> list[str]:
        """
        Entfernt Footer-Zeilen wie:
        'Tiefbau Stammangebot Seite 2/84'
        bennötigt falls Eintrag über zwei Seiten geht
        """
        footer_re = re.compile(r"^\s*Tiefbau\s+Stammangebot\s+Seite\s+\d+/\d+\s*$")
        return [ln for ln in lines if not footer_re.match(ln)]

    def _remove_page_markers(self, lines: list[str]) -> list[str]:
        """
        Entfernt Seitenmarker-Zeilen wie:
        '===== SEITE 5 ====='
        bennötigt falls Eintrag über zwei Seiten geht
        """
        cleaned = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("===== SEITE") and stripped.endswith("====="):
                continue  # Marker-Zeile überspringen
            cleaned.append(line)

        return cleaned

    def _read_file(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _write_file(self, path: str, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
