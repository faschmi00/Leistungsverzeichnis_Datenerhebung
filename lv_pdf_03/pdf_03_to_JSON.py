from lv_pdf_03.txt_converter import TxtConverter
from lv_pdf_03.txt_cleaner import TxtCleaner


class Pdf03ToJSON:

    INPUT_PDF = "lv_pdf_03/src/lv_imSand.pdf"
    RAW_TXT = "lv_pdf_03/src/lv_imSand.txt"
    CLEAN_TXT = "lv_pdf_03/src/lv_imSand_clean.txt"
    OUTPUT_JSON = "lv_list.json"

    GEWERK = "Rohbauarbeiten"
    QUELLE = "https://rheinhausen.de/pb/site/Rheinhausen/get/documents_E-1590600849/rheinhausen/Dateien/180518%20LV%203.13%20Rohbauarbeiten%2016-018.pdf"

    def convert_to_json(self, input_pdf: str = None, output_json: str = None) -> None:
        # Defaults verwenden, wenn nichts übergeben wurde
        input_pdf = input_pdf or self.INPUT_PDF
        output_json = output_json or self.OUTPUT_JSON

        # 1) PDF -> TXT
        TxtConverter().convert_to_txt(input_pdf, self.RAW_TXT)
        print("TXT erstellt:", self.RAW_TXT)

         #2) TXT bereinigen
        TxtCleaner().clean_document(self.RAW_TXT, self.CLEAN_TXT)
        print("TXT bereinigt:", self.CLEAN_TXT)

        """
        # 3) TXT -> JSON
        parser = JsonConverter(quelle=self.QUELLE, gewerk=self.GEWERK)
        parser.convert(self.CLEAN_TXT, self.OUTPUT_JSON, self.OUTPUT_JSON)
        print("JSON erstellt:", output_json)"""

