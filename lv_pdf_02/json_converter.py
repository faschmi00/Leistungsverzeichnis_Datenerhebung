import json
import re
from typing import List, Dict, Optional


class JsonConverter:
    """
    TXT (bereinigt) -> JSON-Liste im gewünschten Format.

    Regeln (Bruchsal / Felixstraße):
    - Titelzeile: beginnt mit zwei Zahlen-Blöcken, z.B. "01.01. Baustelleneinrichtungsarbeiten, Hilfsleistungen"
      -> titel ist der Textteil OHNE "01.01."
      -> titel bleibt sticky bis neue Titelzeile kommt
    - Position: drei Zahlen-Blöcke, z.B. "01.03.0004. Oberboden abtragen und zwischenlagern"
      -> positionsnummer ist "01.03.0004."
      -> kurztext ist der Rest der Zeile nach der Positionsnummer
    - Langtext: alle folgenden Zeilen bis zur nächsten Position ODER nächsten Titel (2- oder 3-blöckig)
    - IDs: Input-Datei enthält bereits JSON-Positionen mit id -> ID wird fortgeführt (max(id)+1)
    """

    # Titel: genau 2 Blöcke: 01.01. + Text
    RE_TITEL = re.compile(r"^\s*(\d{2}\.\d{2})\.\s+(.*\S)\s*$")

    # Position: genau 3 Blöcke: 01.03.0004. + Kurztext
    RE_POS = re.compile(r"^\s*(\d{2}\.\d{2}\.\d{4})\.\s*(.*\S)?\s*$")

    def __init__(self, quelle: str, gewerk: str):
        self.quelle = quelle
        self.gewerk = gewerk

    def convert(self, input_txt: str, output_json: str, existing_json: Optional[str] = None) -> None:
        # 1) vorhandene IDs lesen (falls es bereits eine JSON-Datei gibt)
        start_id = self._get_next_id(existing_json or output_json)

        # 2) TXT lesen
        lines = self._read_lines(input_txt)

        # 3) parsen
        items = self._parse(lines, start_id=start_id)

        # 4) ggf. bestehende JSON laden und erweitern
        existing_items: List[Dict] = []
        if self._file_exists(existing_json or output_json):
            existing_items = self._read_existing_json(existing_json or output_json)

        all_items = existing_items + items

        # 5) schreiben
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

            # Titel erkennen: 01.01. <Text>
            mt = self.RE_TITEL.match(ln)
            if mt:
                current_title = mt.group(2).strip()
                i += 1
                continue

            # Position erkennen: 01.03.0004. <Kurztext>
            mp = self.RE_POS.match(ln)
            if mp:
                positionsnummer = mp.group(1) + "."
                kurztext = (mp.group(2) or "").strip()

                i += 1

                # Langtext sammeln bis nächste Position oder nächster Titel
                lang_lines: List[str] = []
                while i < len(lines):
                    cur = lines[i].strip()

                    if not cur:
                        lang_lines.append("")  # Absatz behalten
                        i += 1
                        continue

                    # Abgrenzung: neue Position oder neuer Titel
                    if self.RE_POS.match(cur) or self.RE_TITEL.match(cur):
                        break

                    lang_lines.append(lines[i].rstrip("\n"))
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
    # Helpers / IO
    # -------------------------

    def _read_lines(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.rstrip("\n") for ln in f.readlines()]

    def _file_exists(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8"):
                return True
        except FileNotFoundError:
            return False

    def _read_existing_json(self, path: str) -> List[Dict]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []

    def _get_next_id(self, path: str) -> int:
        if not self._file_exists(path):
            return 1
        items = self._read_existing_json(path)
        max_id = 0
        for it in items:
            try:
                max_id = max(max_id, int(it.get("id", 0)))
            except (TypeError, ValueError):
                continue
        return max_id + 1
