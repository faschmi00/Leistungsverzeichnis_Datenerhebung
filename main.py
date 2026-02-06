from lv_pdf_01.pdf_01_to_JSON import Pdf01ToJSON
from lv_pdf_02.pdf_02_to_JSON import Pdf02ToJSON
from lv_pdf_03.pdf_03_to_JSON import Pdf03ToJSON
from  lv_pdf_05.pdf_05_to_JSON import Pdf05ToJSON

def main():

    Pdf01ToJSON().convert_to_json()
    Pdf02ToJSON().convert_to_json()
    Pdf03ToJSON().convert_to_json()
    Pdf05ToJSON().convert_to_json()

if __name__ == "__main__":
    main()
