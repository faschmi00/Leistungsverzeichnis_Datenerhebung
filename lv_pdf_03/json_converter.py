import json
import re
from typing import List, Dict, Optional


class JsonConverter:
    """
    TXT (bereinigt) -> JSON-Liste im gewünschten Format.

    Regeln:
    - Titelzeile: "<X>.<Y>. Titel: <Titeltext>"
      Beispiel: "1.01. Titel: Baustelleneinrichtung"
      -> titel = "Baustelleneinrichtung"
      -> gilt für alle folgenden Positionen bis zum nächsten Titel

    - Position: genau 3 Blöcke: "01.03.0004. <Kurztext>"
      -> positionsnummer = "01.03.0004."
      -> kurztext = Rest der Zeile nach der Positionsnummer

    - Langtext: alle Folgezeilen bis zur nächsten Position ODER bis zum nächsten Titel
      (Titelnummer = 2 Blöcke, Position = 3 Blöcke)

    - IDs: Wenn existing_json (oder output_json) bereits existiert, wird max(id)+1 als Start verwendet.
    """

    # Titel: 2 Blöcke + "Titel:"
    RE_TITLE = re.compile(r"^\s*(\d{1,2}\.\d{1,2})\.\s*Titel:\s*(.+\S)\s*$")

    # Position: 3 Blöcke (letzter Block 1-4 Stellen) + optional Kurztext
    RE_POS = re.compile(r"^\s*(\d{1,2}\.\d{1,2}\.\d{1,4})\.\s*(.*\S)?\s*$")

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
            ln = lines[i].strip()

            if not ln:
                i += 1
                continue

            # Titel setzen
            mt = self.RE_TITLE.match(ln)
            if mt:
                current_title = mt.group(2).strip()
                i += 1
                continue

            # Position erkennen
            mp = self.RE_POS.match(ln)
            if mp:
                positionsnummer = mp.group(1) + "."
                kurztext = (mp.group(2) or "").strip()

                i += 1

                # Langtext sammeln bis nächste Position oder nächster Titel
                lang_lines: List[str] = []
                while i < len(lines):
                    cur_raw = lines[i]
                    cur = cur_raw.strip()

                    # Abgrenzung
                    if self.RE_POS.match(cur) or self.RE_TITLE.match(cur):
                        break

                    # Absätze bewahren
                    if cur == "":
                        lang_lines.append("")
                    else:
                        lang_lines.append(cur_raw.rstrip("\n"))

                    i += 1

                langtext = "\n".join(lang_lines).strip()

                results.append({
                    "id": next_id,
                    "quelle": self.quelle,
                    "gewerk": self.gewerk,
                    "titel": current_title,
                    "positionsnummer": positionsnummer,
                    "kurztext": kurztext,
                    "langtext": langtext
                })
                next_id += 1
                continue

            i += 1

        return results

    # -------------------------
    # IO / Existing JSON
    # -------------------------

    def _read_lines(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.rstrip("\n") for ln in f.readlines()]

    def _load_existing(self, path: str) -> (int, List[Dict]):
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
