from lv_pdf_02.txt_converter import TxtConverter
from lv_pdf_01.txt_cleaner import TxtCleaner
from lv_pdf_01.json_converter import JsonConverter

class Pdf01ToJSON:

    INPUT_PDF = "lv_pdf_01/src/stammangebot-lv.pdf"
    RAW_TXT = "lv_pdf_01/src/stammangebot-lv.txt"
    CLEAN_TXT = "lv_pdf_01/src/stammangebot-lv_clean.txt"
    OUTPUT_JSON = "lv_list.json"

    QUELLE = "https://www.stadtwerke-velbert.de/fileadmin/documents/unternehmen/stammangebot-lv.pdf"
    GEWERK = "Tiefbau"

    def convert_to_json(self, input_pdf: str = None, output_json: str = None) -> None:
        # Defaults verwenden, wenn nichts übergeben wurde
        input_pdf = input_pdf or self.INPUT_PDF
        output_json = output_json or self.OUTPUT_JSON

        # 1) PDF -> TXT
        TxtConverter().convert_to_txt(input_pdf, self.RAW_TXT)
        print("TXT erstellt:", self.RAW_TXT)

        # 2) TXT bereinigen
        TxtCleaner().clean_document(self.RAW_TXT, self.CLEAN_TXT)
        print("TXT bereinigt:", self.CLEAN_TXT)

        # 3) TXT -> JSON
        parser = JsonConverter(quelle=self.QUELLE, gewerk=self.GEWERK)
        parser.convert(input_txt=self.CLEAN_TXT, output_json=output_json, start_id=1)
        print("JSON erstellt:", output_json)
