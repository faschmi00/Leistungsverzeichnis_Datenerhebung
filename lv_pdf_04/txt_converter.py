from pypdf import PdfReader


class TxtConverter:
    def convert_to_txt(self, input_pdf: str, output_txt: str) -> None:
        reader = PdfReader(input_pdf)

        with open(output_txt, "w", encoding="utf-8") as f:
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                # 1) Blockweise-Dedupe: wenn die Seite 1:1 doppelt hintereinander hängt
                text = self._dedupe_whole_text_if_duplicated(text)

                # 2) Zusatz: Zeilenweise-Dedupe für direkt aufeinanderfolgende Duplikate
                text = self._dedupe_consecutive_lines(text)

                f.write(f"\n===== SEITE {page_number} =====\n\n")
                f.write(text)
                f.write("\n")

    def _dedupe_whole_text_if_duplicated(self, text: str) -> str:
        """
        Entfernt blockweise Verdopplung, wenn der komplette Seiten-Text
        exakt zweimal hintereinander vorkommt.

        Beispiel:
          <BLOCK><BLOCK>  -> <BLOCK>
        """
        s = text.strip()
        if not s:
            return text

        # Normalisiere Whitespace, um kleine Unterschiede (Mehrfachspaces) zu ignorieren
        norm = " ".join(s.split())

        # Wenn Länge ungerade -> kann nicht exakt in 2 Hälften identisch sein
        if len(norm) % 2 != 0:
            return text

        half = len(norm) // 2
        if norm[:half] == norm[half:]:
            # Wir wollen möglichst die ORIGINAL-Hälfte (mit Zeilenumbrüchen) behalten.
            # Deshalb schneiden wir am Originalstring ungefähr in der Mitte.
            orig = s
            orig_half = len(orig) // 2

            left = orig[:orig_half].strip()
            right = orig[orig_half:].strip()

            # Fallback: wenn original nicht exakt halbteilbar ist, nutze die Normalform
            if left and right and " ".join(left.split()) == " ".join(right.split()):
                return left + "\n"

        return text

    def _dedupe_consecutive_lines(self, text: str) -> str:
        """
        Entfernt direkt hintereinander doppelte Zeilen (A,A -> A).
        Hilft zusätzlich bei PDFs mit doppeltem Textlayer.
        """
        lines = text.splitlines()
        out = []
        prev = None

        for ln in lines:
            s = ln.strip()
            if prev is not None and s and s == prev:
                continue
            out.append(ln)
            prev = s if s else prev

        return "\n".join(out)
