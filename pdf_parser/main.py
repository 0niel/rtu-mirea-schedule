import tabula
import pandas as pd

pdf_in = "pdf_parser/РАСПИСАНИЕ ИТ изм.pdf"
pdf_out = "pdf_parser/From_PDF.csv"

pdf = tabula.read_pdf(pdf_in, pages='all', multiple_tables=True)
for table in pdf:
    print(table.columns.tolist())