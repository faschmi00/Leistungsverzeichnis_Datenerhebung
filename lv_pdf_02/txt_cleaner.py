import re

class TxtCleaner:

    def clean_document(self, input_txt: str, output_txt: str) -> None:

        lines = self._read_file(input_txt)

        lines = self._delete_last_pages(lines)

        lines = self._remove_first_page(lines)

        lines = self._remove_footers_and_headers(lines)

        lines = self._remove_quantity_dot_lines(lines)

        lines = self._remove_sum_lines(lines)

        lines = self._merge_exception_blocks(lines)

        lines = self._remove_einh_pr_line(lines)

        self._write_file(output_txt, lines)

    def _delete_last_pages(self, lines: list[str]) -> list[str]:
        """
        Löscht alles ab der Zeile '===== SEITE 42 =====' (inklusive).
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 43 =====":
                # alles ab dieser Zeile löschen
                return lines[:index]

        return lines

    def _merge_exception_blocks(self, lines: list[str]) -> list[str]:
        """
        Findet GENAU definierte StL-Blöcke und führt sie jeweils zu einer Zeile zusammen.
        """
        target_blocks = [
            [
                "01.01.0001. StL-Nr. 13.101/107.21",
                "Baustelle",
                "einrichten",
                "Dies.LV-Abschn.",
                "Zufahrt vorh."
            ],
            [
                "01.01.0002. StL-Nr. 13.101/112.02",
                "Baustelle räumen",
                "Dies. LV-Abschn."
            ],
            [
                "01.06.0004. StL-Nr. 06.110/367.21.99.00",
                "Formstück",
                "einbauen (Zul)",
                "Bogen DN 150",
                "... Freitext ..."
            ],
            [
                "01.06.0005. StL-Nr. 06.110/367.21.99.00",
                "Formstück",
                "einbauen (Zul)",
                "Bogen DN 150",
                "... Freitext ..."
            ],
            [
                "01.06.0006. StL-Nr. 06.110/367.02.99.00",
                "Formstück",
                "einbauen (Zul)",
                "Abzweig DN 150",
                "... Freitext ..."
            ],
            [
                "01.06.0008. StL-Nr. 06.110/443.11",
                "Betonauflagering",
                "einbauen",
                "Rg.,verschiebsich",
                "Höhe 60 mm"
            ],
            [
                "01.06.0011. StL-Nr. 06.110/367.21.99.00",
                "Formstück",
                "einbauen (Zul)",
                "Bogen DN 150",
                "... Freitext ..."
            ],
            [
                "02.01.0001. StL-Nr. 13.101/107.21",
                "Baustelle",
                "einrichten",
                "Dies.LV-Abschn.",
                "Zufahrt vorh."
            ],
            [
                "02.01.0002. StL-Nr. 13.101/112.02",
                "Baustelle räumen",
                "Dies. LV-Abschn."
            ],
            [
                "01.08.0003. *** Bedarfsposition ohne GB",
                "Verrechnungssatz Bagger"
            ],
            [
                "01.08.0002. *** Bedarfsposition ohne GB",
                "Personal"
            ],
            [
                "01.08.0004. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Baugerät, Rüttler"
            ],
            [
                "01.08.0005. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für auf der Baustelle eingesetzten Frontlader"
            ], [
                "01.08.0006. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für LKW, LKW-Kipper 8 t Nutzlast"
            ],
            [
                "01.08.0007. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Kleintransporter"
            ],
            [
                "01.08.0008. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Kompressor mit Abbauhammer"
            ],
            [
                "01.08.0009. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Motorflex mit Diamantscheibe"
            ],
            [
                "01.08.0010. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Minibagger"
            ], [
                "01.08.0011. *** Bedarfsposition ohne GB",
                "Verrechnungssatz für Explosionsstampfer, ca. 0, 1 t"
            ],
            [
                "01.08.0013. *** Bedarfsposition ohne GB",
                "Beton C 12/15"
            ],
            [
                "01.08.0014. *** Bedarfsposition ohne GB",
                "Beton C 20/25"
            ]
        ]

        merged = []
        i = 0

        while i < len(lines):
            matched = False

            for block in target_blocks:
                block_len = len(block)

                if i + block_len > len(lines):
                    continue

                if all(lines[i + j].strip() == block[j] for j in range(block_len)):
                    merged.append(" ".join(block) + "\n")
                    i += block_len
                    matched = True
                    break

            if matched:
                continue

            merged.append(lines[i])
            i += 1

        return merged

    def _remove_sum_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
          - Summe 02.02. Beton
          - Summe 01. Wasser
          - Summe 01.07. Asphaltbauweisen
          - Summe 1.2.3 Irgendwas

        Zahlen- und Textteile können variieren.
        """
        pattern = re.compile(
            r"^\s*Summe\s+\d+(?:\.\d+)*\.?\s+.*$"
        )

        return [ln for ln in lines if not pattern.match(ln.strip())]

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

    def _remove_footers_and_headers(self, lines: list[str]) -> list[str]:
        """
        Entfernt wiederkehrende Tabellen- und Seitenheader aus dem LV-Text.
        """

        header_patterns = [
            r"^Leistungsverzeichnis Kurz- und Langtext",
            r"^Projekt:\s*13_0016 Stadt Bruchsal",
            r"^LV:\s*0016_1 Erneuerung und Umgestaltung Felixstraße",
            r"^OZ\s+Leistungsbeschreibung\s+Menge\s+ME\s+Einheitspreis\s+Gesamtbetrag",
            r"^in EUR\s+in EUR",
            r"^Druckdatum:\s*\d{2}\.\d{2}\.\d{4}\s+Seite:\s*\d+\s+von\s+\d+",
            r"^===== SEITE\s+\d+\s+====="
        ]

        combined_pattern = re.compile("|".join(header_patterns))

        cleaned = [
            line for line in lines
            if not combined_pattern.search(line.strip())
        ]

        return cleaned

    def _remove_quantity_dot_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen wie:
          - 5,000 m .........................
          - 60,000 m³ .........................
          - 1.200,000 m² .........................
          - 5,500 t .........................
          - 1,000 h .........................
          - 5,000 Stck .........................
          - 4,000 St .........................

        Zahlen können variieren (deutsches Zahlformat), Punkte/Leerzeichen können variieren.
        """
        # Zahl: 1-3 Ziffern, optional .xxx Gruppen, dann ,dezimal (1-3 Stellen)
        num = r"\d{1,3}(?:\.\d{3})*,\d{1,3}"

        # Einheiten (nach Bedarf erweitern)
        unit = r"(?:m³|m²|m|t|h|Stck|St|psch|Psch)"

        # Dots: mindestens 5 Punkte (mit optionalen Leerzeichen dazwischen)
        dots = r"(?:\s*\.){5,}"

        pattern = re.compile(rf"^\s*{num}\s*{unit}\s*{dots}\s*$")

        return [ln for ln in lines if not pattern.match(ln.strip())]

    def _remove_einh_pr_line(self, lines: list[str]) -> list[str]:
        """
        Entfernt exakt die Zeile:
        '1,000 h ......................... Nur Einh.-Pr.'
        (Leerzeichen am Anfang/Ende werden ignoriert)
        """
        target = "1,000 h ......................... Nur Einh.-Pr."

        return [
            ln for ln in lines
            if ln.strip() != target
        ]

    def _read_file(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _write_file(self, path: str, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
