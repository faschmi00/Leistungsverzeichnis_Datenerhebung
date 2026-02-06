import re

class TxtCleaner:

    def clean_document(self, input_txt: str, output_txt: str) -> None:

        lines = self._read_file(input_txt)

        lines = self._delete_last_pages(lines)

        lines = self._remove_first_page(lines)

        lines = self._insert_initial_title(lines)

        lines = self._remove_dot_start_lines(lines)

        lines = self._remove_summe_lines(lines)

        lines = self._remove_specific_section_lines(lines)

        lines = self._remove_huke_header_blocks(lines)

        lines = self._remove_content_between_pages(lines)

        lines = self._insert_entwaesserung_between_pages(lines)

        lines = self._remove_page_markers(lines)

        self._write_file(output_txt, lines)

    def _remove_dot_start_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt alle Zeilen, die mit Punkten beginnen.
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith(".")
        ]

    def _remove_specific_section_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt Zeilen, die mit folgenden Anfängen beginnen:
          - STUNDENLÖHNE
          - STRASSENBELEUCHTUNG
          - Straße
        (Groß-/Kleinschreibung wird berücksichtigt)
        """
        starts = (
            "STUNDENLÖHNE",
            "STRASSENBELEUCHTUNG",
            "Straße",
        )

        return [
            ln for ln in lines
            if not ln.lstrip().startswith(starts)
        ]

    def _remove_summe_lines(self, lines: list[str]) -> list[str]:
        """
        Entfernt alle Zeilen, die mit 'Summe' beginnen.
        """
        return [
            ln for ln in lines
            if not ln.lstrip().startswith("Summe")
        ]

    def _insert_initial_title(self, lines: list[str]) -> list[str]:
        """
        Fügt in der ersten Zeile den Titel
        '1. 2 ABBRUCH-/ ERDARBEITEN' ein.
        """
        title_line = "1. 2 ABBRUCH-/ ERDARBEITEN\n"

        if not lines:
            return [title_line]

        return [title_line] + lines

    def _remove_huke_header_blocks(self, lines: list[str]) -> list[str]:
        """
        Entfernt den wiederkehrenden Header-Block wie im Beispiel (Huke / Leistungverzeichnis),
        inkl. Abschnitt/Unterabschnitt-Teil.

        Achtung: Abschnitt- und Unterabschnitt-Texte können variieren.
        Entfernt außerdem doppelt vorkommende Tabellenkopfzeilen:
          "OZ (Pos-Nr.) Menge ME Einheitspreis Gesamtbetrag"
          "in EURin EUR"
        """
        # Erkennungszeilen (robust)
        re_engineer = re.compile(r"^\s*Ingenieur-.*W\.\s*Huke\b.*$", re.IGNORECASE)
        re_lv_title = re.compile(
            r"^\s*L\s*E\s*I\s*S\s*T\s*U\s*N\s*G\s*S\s*V\s*E\s*R\s*Z\s*E\s*I\s*C\s*H\s*N\s*I\s*S\s*$")
        re_lv_date = re.compile(r"^\s*LV-?Datum\s*:\s*\d{2}\.\d{2}\.\d{4}\s*$", re.IGNORECASE)

        re_table_head = re.compile(r"^\s*OZ\s*\(Pos-?Nr\.\)\s+Menge\s+ME\s+Einheitspreis\s+Gesamtbetrag\s*$",
                                   re.IGNORECASE)
        re_in_eur = re.compile(r"^\s*in\s*EUR\s*in\s*EUR\s*$", re.IGNORECASE)

        re_abschnitt = re.compile(r"^\s*Abschnitt\s*:\s*.+\S\s*$", re.IGNORECASE)
        re_unterabschnitt = re.compile(r"^\s*Unterabschnitt\s*:\s*.+\S\s*$", re.IGNORECASE)

        cleaned = []
        i = 0
        n = len(lines)

        while i < n:
            cur = lines[i].strip()

            # Header-Block starten, wenn typische Startzeile auftaucht
            if re_engineer.match(cur):
                i += 1

                # Skippe alles, bis wir LV-Titel und LV-Datum gesehen haben (oder bis Tabellenkopf beginnt)
                saw_lv_title = False
                saw_lv_date = False

                while i < n:
                    s = lines[i].strip()

                    if re_lv_title.match(s):
                        saw_lv_title = True
                        i += 1
                        continue

                    if re_lv_date.match(s):
                        saw_lv_date = True
                        i += 1
                        continue

                    # Sobald Tabellenkopf beginnt oder Abschnitt kommt, brechen wir in den nächsten Skip-Teil
                    if re_table_head.match(s) or re_abschnitt.match(s):
                        break

                    i += 1

                # Falls es wirklich unser Header ist, entfernen wir zusätzlich die bekannten Kopfzeilen danach
                if saw_lv_title or saw_lv_date:
                    # Entferne beliebig viele Tabellenkopf-Zeilen (können doppelt vorkommen)
                    while i < n:
                        s = lines[i].strip()

                        # Abschnitt/Unterabschnitt-Zeilen entfernen
                        if re_abschnitt.match(s) or re_unterabschnitt.match(s):
                            i += 1
                            continue

                        # Tabellenkopf entfernen (kann mehrfach vorkommen)
                        if re_table_head.match(s):
                            i += 1
                            # oft folgt "in EURin EUR" direkt danach (ggf. auch doppelt)
                            while i < n and re_in_eur.match(lines[i].strip()):
                                i += 1
                            continue

                        # "in EURin EUR" allein ebenfalls entfernen
                        if re_in_eur.match(s):
                            i += 1
                            continue

                        # Ende des Headers: sobald wir auf eine "normale" Inhaltszeile treffen
                        break

                    continue  # kompletten Block übersprungen

            # Zusätzlich: falls Tabellenkopf unabhängig noch vorkommt -> entfernen
            if re_table_head.match(cur) or re_in_eur.match(cur) or re_abschnitt.match(cur) or re_unterabschnitt.match(
                    cur):
                i += 1
                continue

            cleaned.append(lines[i])
            i += 1

        return cleaned

    def _delete_last_pages(self, lines: list[str]) -> list[str]:
        """
        Löscht alles ab der Zeile '===== SEITE 65 =====' (inklusive).
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 65 =====":
                # alles ab dieser Zeile löschen
                return lines[:index]

        return lines


    def _remove_first_page(self, lines: list[str]) -> list[str]:
        """
        Entfernt alles bis einschließlich der Zeile:
        '===== SEITE 17 ====='
        """
        for index, line in enumerate(lines):
            if line.strip() == "===== SEITE 17 =====":
                # alles davor + diese Zeile entfernen
                return lines[index + 1:]

        return lines


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

    def _remove_content_between_pages(
            self,
            lines: list[str],
            start_marker: str = "===== SEITE 27 =====",
            end_marker: str = "===== SEITE 31 ====="
    ) -> list[str]:
        """
        Entfernt ALLE Zeilen zwischen zwei Seitenmarkern,
        lässt die Marker selbst aber bestehen.

        Beispiel:
          ===== SEITE 27 =====
          <wird gelöscht>
          ===== SEITE 31 =====
        """

        cleaned = []
        skip = False

        for line in lines:
            stripped = line.strip()

            if stripped == start_marker:
                cleaned.append(line)
                skip = True
                continue

            if stripped == end_marker:
                skip = False
                cleaned.append(line)
                continue

            if skip:
                continue

            cleaned.append(line)

        return cleaned

    def _insert_entwaesserung_between_pages(self, lines: list[str]) -> list[str]:
        """
        Fügt zwischen '===== SEITE 27 =====' und '===== SEITE 31 ====='
        fest definierte Entwässerungs-Blöcke ein.
        Die Seitenmarker selbst bleiben bestehen.
        """

        start_marker = "===== SEITE 27 ====="
        end_marker = "===== SEITE 31 ====="

        insert_block = [
            "1. 3 ENTWÄSSERUNGSKANALARBEITEN / SW + RW Straße\n",
            "\n",
            "1. 3.   1 KG-Leitungen, wandverstärkt, grün, DN 200 mm\n",
            "Vollwandabwasserrohr und Formstücke aus Polypropylen  \n",
            "(PP-MD), grün, gemäß DIN EN 14758-1 mit Steckmuffe\n",
            "mit werkseitig eingelegter patentierter Lippendichtung,\n",
            "Hochlastkanalrohr mit hoher Ringsteifigkeit > 10 kN/m2\n",
            "\n"
        ]

        result = []
        inserted = False
        skip_between = False

        for line in lines:
            stripped = line.strip()

            if stripped == start_marker:
                result.append(line)
                result.extend(insert_block)
                skip_between = True
                inserted = True
                continue

            if stripped == end_marker:
                skip_between = False
                result.append(line)
                continue

            if skip_between:
                continue

            result.append(line)

        return result

    def _read_file(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _write_file(self, path: str, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
