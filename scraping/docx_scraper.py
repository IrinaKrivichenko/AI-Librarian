from docx import Document
from docx.table import Table


def get_docx_text(path):
    """Функция для извлечения текста из файла .docx."""
    print(path)
    doc = Document(path)
    full_text = []
    for el in doc.element.body:
        if el.tag.endswith('p'):  # Обработка абзацев (параграфов)
            full_text.append(el.text)
        elif el.tag.endswith('tbl'):  # Обработка таблицы
            table = Table(el, doc)  # Преобразование element в объект Table
            for row in table.rows:
                row_text = [cell.text for cell in row.cells]
                full_text.append('\t'.join(row_text))
            full_text.append('')  # Добавить пустую строку после таблицы для лучшей читаемости
    return '\n'.join(full_text)

def print_docx_image_names(path):
    doc = Document(path)
    # выводит названия рисунков так как они в документе
    # но находит НЕ все рисунки
    for shape in doc.inline_shapes._inline_lst:
        print(shape.docPr.name)

    # выводит не понятно какие названия рисунков
    # но находит все рисунки
    for image_id, rel in doc.part.rels.items():
        if "image" in rel.reltype:
            image_ext = os.path.splitext(rel.target_ref)
            image_filename = f'{image_ext}'
            print(image_filename)
