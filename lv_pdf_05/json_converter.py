import json
import re
from typing import List, Dict, Optional, Tuple


class JsonConverter:
    """
    TXT -> JSON im gewünschten Format.

    Vorgaben:
    - Titelzeile:
        "01.02   Titel   Maurerarbeiten"
      -> titel = "Maurerarbeiten"
      -> gilt bis zum nächsten Titel

    - Positionszeile (MUSS am Zeilenanfang stehen):
        "01.01.02.008 händisches Freilegen bestehender"
      -> positionsnummer = "01.01.02.008"
      -> kurztext = Rest der Zeile

    - Langtext:
      alle Folgezeilen bis zur nächsten Positionszeile (4 Blöcke)
      ODER bis zur nächsten Titelzeile (2 Blöcke + 'Titel')

    - IDs:
      Wenn existing_json (oder output_json) existiert, wird max(id)+1 als Start verwendet.
    """

    # Titel: genau 2 Blöcke (je 2 Stellen) + "Titel" + Text
    RE_TITLE = re.compile(r"^\s*(\d{2})\.(\d{2})\s+Titel\s+(.+\S)\s*$", re.IGNORECASE)

    # Position: genau 4 Blöcke (2.2.2.3/4-stellig) am Zeilenanfang + Kurztext
    RE_POS = re.compile(
        r"^\s*(\d{2})\.(\d{2})\.(\d{2})\.(\d{3,4})\s+(.+\S)\s*$"
    )

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
            s = raw.strip()

            if not s:
                i += 1
                continue

            # Titel erkennen
            mt = self.RE_TITLE.match(s)
            if mt:
                current_title = mt.group(3).strip()
                i += 1
                continue

            # Position erkennen
            mp = self.RE_POS.match(s)
            if mp:
                positionsnummer = f"{mp.group(1)}.{mp.group(2)}.{mp.group(3)}.{mp.group(4)}"
                kurztext = mp.group(5).strip()

                i += 1

                # Langtext sammeln bis nächste Position oder nächster Titel
                lang_lines: List[str] = []
                while i < len(lines):
                    nxt_raw = lines[i].rstrip("\n")
                    nxt = nxt_raw.strip()

                    if not nxt:
                        lang_lines.append("")
                        i += 1
                        continue

                    # Abgrenzung: neue Position oder neuer Titel
                    if self.RE_POS.match(nxt) or self.RE_TITLE.match(nxt):
                        break

                    lang_lines.append(nxt_raw)
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

            i += 1

        return results

    # -------------------------
    # IO / Existing JSON
    # -------------------------

    def _read_lines(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _load_existing(self, path: str) -> Tuple[int, List[Dict]]:
        """
        Lädt vorhandene JSON-Liste, um IDs fortzuführen.
        Wenn Datei nicht existiert / leer ist / ungültig ist => startet bei 1.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().strip()

                # Datei existiert, aber ist leer
                if not raw:
                    return 1, []

                data = json.loads(raw)

                existing_items = data if isinstance(data, list) else []

        except FileNotFoundError:
            return 1, []
        except json.JSONDecodeError:
            # Datei ist kaputt/kein JSON -> wie "neu starten"
            return 1, []

        max_id = 0
        for it in existing_items:
            try:
                max_id = max(max_id, int(it.get("id", 0)))
            except (TypeError, ValueError):
                pass

        return max_id + 1, existing_items
