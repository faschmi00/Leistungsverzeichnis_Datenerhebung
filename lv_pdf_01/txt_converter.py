from pypdf import PdfReader

class TxtConverter:

    def convert_to_txt(self, input_pdf: str, output_txt: str) -> None:
        reader = PdfReader(input_pdf)

        with open(output_txt, "w", encoding="utf-8") as f:
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                f.write(f"\n===== SEITE {page_number} =====\n\n")
                f.write(text)
                f.write("\n")
