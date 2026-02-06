import json
import re
from typing import List, Dict, Optional, Tuple


class JsonConverter:
    """
    TXT -> JSON im gewünschten Format.

    WICHTIG (dein Format):
    - Titelnummer: "1. 4" (zwei Blöcke), KEIN Punkt am Ende der Blockfolge
      Beispiel (teilweise doppelt im Text):
        "1. 4 VERSORGUNGSTRÄGER TW1. 4 VERSORGUNGSTRÄGER TW"
      -> titel = "VERSORGUNGSTRÄGER TW"
      -> gilt bis zum nächsten Titel

    - Positionszeile: drei Blöcke, nach den ersten zwei Blöcken kommen >= 3 Leerzeichen,
      KEIN Punkt am Ende der Blockfolge
      Beispiel:
        "1. 3.   1 Oberboden abtragen und zwischenlagern"
      -> positionsnummer = "1.3.1"
      -> kurztext = Rest der Zeile

    - Langtext: alle Folgezeilen bis zur nächsten Position oder zum nächsten Titel

    - IDs: bestehende JSON hat schon ids -> fortführen (max(id)+1)
    """

    # Titel: "1. 4 <Titeltext>"  (kein 'Titel:' mehr!)
    RE_TITLE = re.compile(r"^\s*(\d{1,2})\.\s*(\d{1,2})\s+(.+\S)\s*$")

    # Position: "1. 3.   1 <Kurztext>"  (>=3 Spaces vor dem 3. Block)
    RE_POS = re.compile(r"^\s*(\d{1,2})\.\s*(\d{1,2})\.\s{3,}(\d{1,4})\s+(.+\S)\s*$")

    def __init__(self, quelle: str, gewerk: str):
        self.quelle = quelle
        self.gewerk = gewerk

    def convert(self, input_txt: str, output_json: str, existing_json: Optional[str] = None) -> None:
        base_json_path = existing_json or output_json
        start_id, existing_items = self._load_existing(base_json_path)

        lines = self._read_lines(input_txt)
        new_items = self._parse(lines, start_id=start_id)

        all_items = existing_items + new_items

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(all_items, f, ensure_ascii=False, indent=2)

    # -------------------------
    # Parsing
    # -------------------------

    def _parse(self, lines: List[str], start_id: int) -> List[Dict]:
        results: List[Dict] = []
        current_title: str = ""
        next_id = start_id
        i = 0

        while i < len(lines):
            raw = lines[i].rstrip("\n")
            ln = raw.strip()

            if not ln:
                i += 1
                continue

            # Position zuerst prüfen (damit "1. 3.   1 ..." nicht als Titel fehlinterpretiert wird)
            mp = self.RE_POS.match(raw)
            if mp:
                a, b, c = mp.group(1), mp.group(2), mp.group(3)
                kurztext = mp.group(4).strip()
                positionsnummer = f"{int(a)}.{int(b)}.{int(c)}"

                i += 1

                # Langtext sammeln bis nächste Position oder nächster Titel
                lang_lines: List[str] = []
                while i < len(lines):
                    r2 = lines[i].rstrip("\n")
                    s2 = r2.strip()

                    if not s2:
                        lang_lines.append("")
                        i += 1
                        continue

                    if self.RE_POS.match(r2):
                        break

                    # Titel beginnt mit "X. Y " (zwei Blöcke)
                    if self.RE_TITLE.match(s2):
                        break

                    lang_lines.append(r2)
                    i += 1

                langtext = "\n".join(lang_lines).strip()

                results.append({
                    "id": next_id,
                    "quelle": self.quelle,
                    "gewerk": self.gewerk,
                    "titel": current_title,
                    "positionsnummer": positionsnummer,
                    "kurztext": kurztext,
                    "langtext": langtext,
                })
                next_id += 1
                continue

            # Titel prüfen
            mt = self.RE_TITLE.match(ln)
            if mt:
                a, b = mt.group(1), mt.group(2)

                # Doppelte Titel auf einer Zeile entfernen (z.B. "...TW1. 4 ...TW")
                ln_first = self._cut_repeated_title(ln, a, b)

                # Titeltext nochmal aus dem gekürzten Teil extrahieren
                mt2 = self.RE_TITLE.match(ln_first)
                if mt2:
                    current_title = mt2.group(3).strip()

                i += 1
                continue

            i += 1

        return results

    def _cut_repeated_title(self, line: str, a: str, b: str) -> str:
        """
        Falls eine Titelzeile denselben Titel zweimal hintereinander enthält (ohne Zeilenumbruch),
        wird alles ab dem zweiten Vorkommen von "a. b" abgeschnitten.
        Beispiel:
          "1. 4 VERS...TW1. 4 VERS...TW" -> "1. 4 VERS...TW"
        """
        # suche zweites Vorkommen der Titelnummer "a. b" irgendwo später
        # toleriert fehlende Leerzeichen zwischen Text und zweitem "a. b"
        patt = re.compile(rf"\b{re.escape(a)}\.\s*{re.escape(b)}\b")
        m1 = patt.search(line)
        if not m1:
            return line

        m2 = patt.search(line, m1.end())
        if not m2:
            return line

        return line[:m2.start()].rstrip()

    # -------------------------
    # IO / Existing JSON
    # -------------------------

    def _read_lines(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _load_existing(self, path: str) -> Tuple[int, List[Dict]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_items = data if isinstance(data, list) else []
        except FileNotFoundError:
            return 1, []

        max_id = 0
        for it in existing_items:
            try:
                max_id = max(max_id, int(it.get("id", 0)))
            except (TypeError, ValueError):
                pass

        return max_id + 1, existing_items
