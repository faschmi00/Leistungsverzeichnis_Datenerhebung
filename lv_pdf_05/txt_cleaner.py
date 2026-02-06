import re

class TxtCleaner:

    def clean_document(self, input_txt: str, output_txt: str) -> None:

        lines = self._read_file(input_txt)

        lines = self._remove_last_pages(lines)

        lines = self._remove_first_page(lines)

        lines = self._remove_ohlenhof_header_block(lines)

        lines = self._remove_ep_gp_tail_lines(lines)

        lines = self._remove_summe_titel_untertitel_lines(lines)

        lines = self._remove_netto_tail_lines(lines)

        lines = self._remove_mwst_tail_lines(lines)

        lines = self._remove_fortsetzung_lines(lines)

        lines = self._remove_alle_einzelbetraege_lines(lines)

        lines = self._remove_uebertrag_lines(lines)

        lines = self._remove_psch_gp_lines(lines)

        lines = self._remove_gesamtsumme_brutto_lines(lines)

        lines = self._insert_initial_title(lines)

        lines = self._remove_page_markers(lines)

        self._write_file(output_txt, lines)

    def _remove_last_pages(self, lines: list[str]) -> list[str]:
        """
        Löscht alles ab der Zeile '===== SEITE 266 =====' (inklusive).
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 266 =====":
                # alles ab dieser Zeile löschen
                return lines[:index]

        return lines

    def _remove_first_page(self, lines: list[str]) -> list[str]:
        """
        Entfernt alles bis einschließlich der Zeile:
        '===== SEITE 8 ====='
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 8 =====":
                # alles davor + diese Zeile entfernen
                return lines[index + 1:]

        return lines

    def _insert_initial_title(self, lines: list[str]) -> list[str]:
        """
        Fügt in der ersten Zeile den Titel
        '1. 2 ABBRUCH-/ ERDARBEITEN' ein.
        """
        title_line = "01.01   Titel   Erdarbeiten und Verfüllungen\n"

        if not lines:
            return [title_line]

        return [title_line] + lines

    def _remove_ohlenhof_header_block(self, lines: list[str]) -> list[str]:
        """
        Entfernt den Header-Block (Neubau Oberschule Ohlenhof) inkl. variabler Mittelzeilen.
        Beispiel-Start:
          "Leistungsverzeichnis Neubau Oberschule Ohlenhof (OHB)"
        und endet spätestens bei:
          "Übertrag: ................................"
        (alles dazwischen wird entfernt)
        """
        start_re = re.compile(r"^\s*Leistungsverzeichnis\s+Neubau\s+Oberschule\s+Ohlenhof\b.*$", re.IGNORECASE)
        end_re = re.compile(r"^\s*Übertrag:\s*\.+\s*$", re.IGNORECASE)

        cleaned = []
        skipping = False

        for ln in lines:
            s = ln.strip()

            if not skipping and start_re.match(s):
                skipping = True
                continue

            if skipping:
                if end_re.match(s):
                    skipping = False
                continue

            cleaned.append(ln)

        return cleaned

    def _remove_ep_gp_tail_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt ALLE Zeilen, die auf
          'EP.......................... GP ............................'
        enden (Punkte/Spaces variabel).
        """
        pattern = re.compile(r"EP\s*\.*\s*GP\s*\.*\s*$", re.IGNORECASE)
        return [ln for ln in lines if not pattern.search(ln.strip())]

    def _remove_summe_titel_untertitel_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt ALLE Zeilen, die (auch mit Einrückung) mit
          'Summe Untertitel' oder 'Summe Titel'
        anfangen.
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith(("Summe Untertitel", "Summe Titel"))
        ]

    def _remove_netto_tail_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt ALLE Zeilen, die mit
          ', Netto: ...............................'
        aufhören (Punkte/Spaces variabel).
        """
        pattern = re.compile(r",\s*Netto:\s*\.+\s*$", re.IGNORECASE)
        return [ln for ln in lines if not pattern.search(ln.strip())]

    def _remove_mwst_tail_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt ALLE Zeilen, die mit
          'zzgl. MwSt. (19,0 %): ...............................'
        aufhören (Prozentzahl kann variieren, Punkte/Spaces variabel).
        """
        pattern = re.compile(r"zzgl\.\s*MwSt\.\s*\(\s*\d+(?:,\d+)?\s*%\s*\)\s*:\s*\.+\s*$", re.IGNORECASE)
        return [ln for ln in lines if not pattern.search(ln.strip())]

    def _remove_fortsetzung_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
            - Fortsetzung auf nächster Seite
        (beliebige Einrückung erlaubt)
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("- Fortsetzung auf nächster Seite")
        ]

    def _remove_alle_einzelbetraege_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
            Alle Einzelbeträge Netto
        (beliebige Einrückung erlaubt)
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("Alle Einzelbeträge Netto")
        ]

    def _remove_uebertrag_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
            Übertrag: ................................
        (Punktanzahl egal, Einrückung egal)
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("Übertrag:")
        ]

    def _remove_psch_gp_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
            1 Psch GP ............................
        (führende Leerzeichen werden ignoriert)
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("1 Psch GP")
        ]

    def _remove_gesamtsumme_brutto_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
            Gesamtsumme, Brutto:
        (führende Leerzeichen werden ignoriert)
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("Gesamtsumme, Brutto:")
        ]

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
