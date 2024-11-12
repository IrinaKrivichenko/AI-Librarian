#is not checked
#pip install odfpy



from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P


def get_ods_text(path):
    print(path)
    doc = load(path)
    full_text = []

    for sheet in doc.spreadsheet.getElementsByType(Table):
        for row in sheet.getElementsByType(TableRow):
            row_text = []
            for cell in row.getElementsByType(TableCell):
                cell_text = ''
                for p in cell.getElementsByType(P):
                    if p:
                        cell_text += p.firstChild.data
                if cell_text:
                    row_text.append(cell_text)
            if row_text:
                full_text.append('\t'.join(row_text))
        full_text.append('')  # Add an empty line after each table (sheet) for better readability

    return '\n'.join(full_text)

# Example use:
# text = get_ods_text("path_to_your_file.ods")
# print(text)