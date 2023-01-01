from table_detection_transformers import TableDetection, TableStructureRecognition
from pdf_document import PdfDoc
from temp_dir import TempDir
import pandas as pd
import os

class ExtractPdfTables():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_doc = PdfDoc(pdf_path)
        self.table_detection = TableDetection()
        self.table_structure_recognition = TableStructureRecognition()
        self.temp_dir = TempDir()

    def detect_tables(self, image):
        return self.table_detection.table_detection(image)

    def recognize_table(self, image):
        return self.table_structure_recognition.table_structure(image)

    def get_pdf_page_height(self):
        return self.pdf_doc.pdf[0].get_height()

    def pixels_to_pdf_points(self, pixels, dpi):
        return pixels * 72.0 / dpi
    
    def cell_box_to_points(self, cell_box, dpi=300.0):
        return [self.pixels_to_pdf_points(pixels, dpi) for pixels in cell_box]

    def box_relative_to_absolute(self, box, absolute_box, padding=50):
        return [box[0] + absolute_box[0] - padding, box[1] + absolute_box[1] - padding, box[2] + absolute_box[0] - padding, box[3] + absolute_box[1] - padding]

    def correct_y_coordinates(self, cell, page_height):
        # change order and invert y coordinates
        new_cell_3 = page_height - cell[1]
        new_cell_1 = page_height - cell[3]
        cell[3] = new_cell_3
        cell[1] = new_cell_1
        return cell

    def crop_table(self, image, box, padding=50):
        box[0] -= padding
        box[1] -= padding
        box[2] += padding
        box[3] += padding

        cropped_image = image.crop(box)
        return cropped_image
    
    def sort_rows_cols(self, rows, cols):
        # sort rows
        rows = sorted(rows, key=lambda x: x[1], reverse=True) # sorted by ymin, reverse order because y coordinates are inverted
        # sort cols
        cols = sorted(cols, key=lambda x: x[0]) # sorted by xmin
        return rows, cols

    def get_cell_boxes(self, rows, cols):
        cell_boxes = []
        for row in rows:
            cell_box = [(col[0], row[1], col[2], row[3]) for col in cols]
            cell_boxes.append(cell_box)
        return cell_boxes

    def table_dict_to_list(self, table):
        rows = [row for _, row in table[0].items()]
        cols = [col for _, col in table[1].items()]
        return rows, cols

    def table_relative_to_absolute(self, table, absolute_box):
        page_height = self.get_pdf_page_height()
        rows = [self.correct_y_coordinates(self.cell_box_to_points(self.box_relative_to_absolute(row, absolute_box)), page_height) for row in table[0]]
        cols = [self.correct_y_coordinates(self.cell_box_to_points(self.box_relative_to_absolute(col, absolute_box)), page_height)  for col in table[1]]
        return rows, cols

    def get_cell_boxes_from_table(self, table):
        rows, cols = self.sort_rows_cols(table[0], table[1])
        cell_boxes = self.get_cell_boxes(rows, cols)
        return cell_boxes
    
    def get_text_from_cell(self, cell_boxes, page_num):
        table = []
        for cell_box in cell_boxes:
            row_text = [self.pdf_doc.get_text_inside_box(page_num=page_num, box=cell) for cell in cell_box]
            table.append(row_text)
        return table
                
    def table_to_dataframe(self, table, first_row_header=True):
        df = pd.DataFrame(table)
        if first_row_header and len(df) > 1:
            df.columns = df.iloc[0]
            df = df[1:]
        return df

    def extract_tables(self, first_row_header=True):
        tables = []
        for page_num, image in self.pdf_doc.convert_to_image():
            detect_tables = self.detect_tables(image)
            for _, table_box in detect_tables.items():
                cropped_image = self.crop_table(image, list(table_box))
                table = self.recognize_table(cropped_image)
                table = self.table_dict_to_list(table)
                table = self.table_relative_to_absolute(table, table_box)
                cell_boxes = self.get_cell_boxes_from_table(table)
                table_text = self.get_text_from_cell(cell_boxes, page_num)
                tables.append(self.table_to_dataframe(table_text, first_row_header=first_row_header))
        return tables

    def tables_to_csv(self, tables, path):
        for i, table in enumerate(tables):
            table.to_csv(os.path.join(path, f"table_{i}.csv"), index=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_path", "-f", type=str, required=True)
    parser.add_argument("--output_dir", "-o", type=str, default=".")
    args = parser.parse_args()
    # check if output dir exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    # extract tables
    pdf_tables = ExtractPdfTables(args.pdf_path)
    tables = pdf_tables.extract_tables()
    # save tables to csv
    pdf_tables.tables_to_csv(tables, args.output_dir)