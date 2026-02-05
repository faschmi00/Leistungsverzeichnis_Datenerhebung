import json
import re
from typing import List, Dict, Optional


class JsonConverter:
    # (1) TITEL: GENAU drei Zahlen am Anfang, aber wir speichern NUR den Textteil (ohne "1.5.9")
    RE_TITLE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s+(.*\S)\s*$")

    # Position: 4 Zahlen, z.B. "1.4.7.20 ..."
    RE_POS = re.compile(r"^\s*(\d+\.\d+\.\d+\.\d+)\b(.*)$")

    # (2) Menge + Einheit: toleranter, damit "1 St.", "1St.", "1 St" etc. sicher entfernt werden
    RE_QTY_UNIT = re.compile(r"^\s*(\d+)\s*(st\.?|m²|m³|m)\b\.?\s*", re.IGNORECASE)

    # Preis: "175,00" oder "1.234,50" (als eigene Zeile oder am Zeilenende)
    RE_PRICE_LINE = re.compile(r"^\s*\d{1,3}(?:\.\d{3})*,\d{2}\s*$")
    RE_PRICE_END = re.compile(r"\s+\d{1,3}(?:\.\d{3})*,\d{2}\s*$")

    def __init__(self, quelle: str, gewerk: str):
        self.quelle = quelle
        self.gewerk = gewerk

    def convert(self, input_txt: str, output_json: str, start_id: int = 1000) -> None:
        lines = self._read_lines(input_txt)
        items = self._parse(lines, start_id=start_id)

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

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

            # Titel erkennen (3 Zahlen) – speichern NUR Titeltext ohne Nummernprefix
            mt = self.RE_TITLE.match(ln)
            if mt and not self.RE_POS.match(ln):
                title = mt.group(2).strip()  # <-- Änderung: Nummer nicht übernehmen

                # Titel kann zweizeilig sein
                j = i + 1
                if j < len(lines):
                    nxt = lines[j].strip()
                    if nxt and not self.RE_TITLE.match(nxt) and not self.RE_POS.match(nxt):
                        title = f"{title} {nxt}".strip()
                        i = j

                current_title = title
                i += 1
                continue

            # Position erkennen
            mp = self.RE_POS.match(ln)
            if mp:
                posnr = mp.group(1)
                rest = (mp.group(2) or "").strip()

                header_lines: List[str] = []
                if rest:
                    header_lines.append(rest)

                i += 1
                price_seen = False

                # Preis am Ende der ersten Zeile?
                if header_lines and self.RE_PRICE_END.search(header_lines[-1]):
                    header_lines[-1] = self.RE_PRICE_END.sub("", header_lines[-1]).strip()
                    price_seen = True

                while i < len(lines) and not price_seen:
                    cur = lines[i].strip()

                    if not cur:
                        i += 1
                        continue

                    if self.RE_PRICE_LINE.match(cur):
                        price_seen = True
                        i += 1
                        break

                    if self.RE_PRICE_END.search(cur):
                        header_lines.append(self.RE_PRICE_END.sub("", cur).strip())
                        price_seen = True
                        i += 1
                        break

                    header_lines.append(cur)
                    i += 1

                header = " ".join([h for h in header_lines if h]).strip()

                # Menge + Einheit entfernen -> Kurztext
                mqu = self.RE_QTY_UNIT.match(header)
                if mqu:
                    kurztext = header[mqu.end():].strip()
                else:
                    kurztext = header

                # Langtext: bis nächste Position oder nächster Titel
                lang_lines: List[str] = []
                while i < len(lines):
                    cur = lines[i].strip()

                    if self.RE_POS.match(cur) or self.RE_TITLE.match(cur):
                        break

                    lang_lines.append(lines[i].rstrip())
                    i += 1

                langtext = "\n".join(lang_lines).strip()

                results.append({
                    "id": next_id,
                    "quelle": self.quelle,
                    "gewerk": self.gewerk,
                    "titel": current_title,
                    "positionsnummer": posnr,
                    "kurztext": kurztext,
                    "langtext": langtext
                })
                next_id += 1
                continue

            i += 1

        return results

    def _read_lines(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.rstrip("\n") for ln in f.readlines()]


