import re

class TxtCleaner:

    def clean_document(self, input_txt: str, output_txt: str) -> None:

        lines = self._read_file(input_txt)

        lines = self._delete_last_pages(lines)

        lines = self._remove_first_page(lines)

        lines = self._remove_page_number_lines(lines)

        lines = self._remove_project_header_block(lines)

        lines = self._remove_quantity_underscore_lines(lines)

        lines = self._remove_page_markers(lines)

        lines = self._remove_bedarfsposition_lines(lines)

        lines = self._remove_summe_titel_lines(lines)

        lines = self._remove_stl_nr_lines(lines)

        self._write_file(output_txt, lines)

    def _delete_last_pages(self, lines: list[str]) -> list[str]:
        """
        Löscht alles ab der Zeile '===== SEITE 82 =====' (inklusive).
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 82 =====":
                # alles ab dieser Zeile löschen
                return lines[:index]

        return lines

    def _remove_summe_titel_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen, die mit 'Summe Titel' beginnen, z.B.:
          - Summe Titel 1.06. Kanalisation __________________
          - Summe Titel 2.1. Irgendwas
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("Summe Titel")
        ]

    def _remove_stl_nr_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt alle Zeilen, die mit 'StL-Nr.:' beginnen, z.B.:
          - StL-Nr.: 10/101.107.11
          - StL-Nr.: 10/101.107.11 10/101.107.11
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("StL-Nr.:")
        ]

    def _remove_first_page(self, lines: list[str]) -> list[str]:
        """
        Entfernt alles bis einschließlich der Zeile:
        '===== SEITE 3 ====='
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 3 =====":
                # alles davor + diese Zeile entfernen
                return lines[index + 1:]

        return lines

    def _remove_bedarfsposition_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
          - *Bedarfsposition
          - *Bedarfsposition  StL-Nr.: 10/10/101.712.10

        Zahlen und Leerzeichen können variieren.
        """
        pattern = re.compile(
            r"^\s*\*Bedarfsposition(?:\s+StL-Nr\.\s*:\s*\d+(?:/\d+(?:\.\d+)*)*)?\s*$",
            re.IGNORECASE
        )

        return [ln for ln in lines if not pattern.match(ln.strip())]

    def _remove_project_header_block(self, lines: list[str]) -> list[str]:
        """
        Entfernt den Header-Block wie:
          16.05.2013
          Projekt: 11038 Sand - Änderung I
          Lv: 1
          Pos.Nr. Einheitspr. EUR Gesamtpr. EUR

        Robust gegen kleine Leerzeichen-Varianten.
        """
        date_re = re.compile(r"^\s*\d{2}\.\d{2}\.\d{4}\s*$")
        proj_re = re.compile(r"^\s*Projekt:\s*.+\S\s*$")
        lv_re = re.compile(r"^\s*Lv:\s*\d+\s*$", re.IGNORECASE)
        table_re = re.compile(r"^\s*Pos\.Nr\.\s+Einheitspr\.\s+EUR\s+Gesamtpr\.\s+EUR\s*$", re.IGNORECASE)

        cleaned = []
        i = 0

        while i < len(lines):
            l0 = lines[i].strip()

            if date_re.match(l0):
                l1 = lines[i + 1].strip() if i + 1 < len(lines) else ""
                l2 = lines[i + 2].strip() if i + 2 < len(lines) else ""
                l3 = lines[i + 3].strip() if i + 3 < len(lines) else ""

                if proj_re.match(l1) and lv_re.match(l2) and table_re.match(l3):
                    i += 4  # kompletten Block überspringen
                    continue

            cleaned.append(lines[i])
            i += 1

        return cleaned

    def _remove_page_number_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Seitenzahlen-Zeilen wie:
          - Seite 4
        (Zahl kann variieren)
        """
        pattern = re.compile(r"^\s*Seite\s+\d+\s*$", re.IGNORECASE)
        return [ln for ln in lines if not pattern.match(ln.strip())]

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

    def _remove_quantity_underscore_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
          -  10,00 Stck _______________ __________________
          -  1.300,00 to _______________ __________________
          -  10,00 St _______________ __________________
          -  50,00 m2 _______________ __________________
          -  50,00 m3 _______________ __________________
          -  50,00 t _______________ __________________
          -  -  10,00 Std _______________ __________________
          -  1,00 Psch _______________ __________________
          -  10,00 d _______________ __________________

        Zahlen können variieren.
        """

        # deutsches Zahlenformat
        num = r"\d{1,3}(?:\.\d{3})*,\d{2}"

        # erlaubte Einheiten
        unit = r"(?:Stck|St|to|t|m|m2|m3|m²|m³|Std|h|Psch|d)"

        # Unterstrich-Blöcke
        underscores = r"(?:\s*_){5,}"

        pattern = re.compile(
            rf"^\s*-?\s*{num}\s*{unit}\s*{underscores}\s*_*\s*$",
            re.IGNORECASE
        )

        return [ln for ln in lines if not pattern.match(ln.strip())]

    def _read_file(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _write_file(self, path: str, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
