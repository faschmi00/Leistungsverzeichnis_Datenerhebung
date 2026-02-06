from lv_pdf_05.txt_converter import TxtConverter
from lv_pdf_05.txt_cleaner import TxtCleaner
from lv_pdf_05.json_converter import JsonConverter


class Pdf05ToJSON:

    INPUT_PDF = "lv_pdf_05/src/lv_los06_bauhaupt.pdf"
    RAW_TXT = "lv_pdf_05/src/lv_los06_bauhaupt.txt"
    CLEAN_TXT = "lv_pdf_05/src/lv_los06_bauhaupt_clean.txt"
    OUTPUT_JSON = "lv_list.json"

    GEWERK = "Verkehrsanlagen, Kanal und Tiefbau"
    QUELLE = "https://www.bruchsal.de/site/Bruchsal-Internet/get/documents/bruchsal-internet/PB5Documents/pdf/LV-ImSand.pdf"

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

        # 3) TXT -> JSON
        parser = JsonConverter(quelle=self.QUELLE, gewerk=self.GEWERK)
        parser.convert(self.CLEAN_TXT, self.OUTPUT_JSON)
        print("JSON erstellt:", output_json)

