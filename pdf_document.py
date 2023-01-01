'''
author: bruno bastiani
date: 2022-12-31
description: convert pdf page to image using pdfium
'''
import pypdfium2 as pdfium
import os
from temp_dir import TempDir


class PdfDoc():
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf = pdfium.PdfDocument(pdf_path)
        self.page_indices = list(range(len(self.pdf)))      

    def convert_to_image(self):       
        self.renderer = self.pdf.render_to(
            pdfium.BitmapConv.pil_image,
            page_indices = self.page_indices,
            scale = 300/72,  # 300dpi resolution
        )
        for i, image in zip(self.page_indices, self.renderer):
            # image.save(os.path.join(self.path,f"out_{i}.jpg"))
            yield i, image

    def convert_to_image_save(self, path):       
        self.path = path
        self.renderer = self.pdf.render_to(
            pdfium.BitmapConv.pil_image,
            page_indices = self.page_indices,
            scale = 300/72,  # 300dpi resolution
        )
        for i, image in zip(self.page_indices, self.renderer):
            image.save(os.path.join(self.path,f"out_{i}.jpg"))
    
    def get_text_inside_box(self, page_num, box):
        page = self.pdf[page_num]
        textpage = page.get_textpage()
        text = textpage.get_text_bounded(left=box[0], bottom=box[1], right=box[2], top=box[3])
        return self.clean_text(text)
    
    def clean_text(self, text):
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")
        text = text.replace("\r", " ")
        text = text.replace("  ", " ")
        return text

if __name__ == "__main__":
    pdf_path = "example_pdf.pdf"
    pdf_converter = PdfDoc(pdf_path)
    temp_dir = TempDir()
    # convert pdf file to image
    pdf_converter.convert_to_image_save(temp_dir.path)
    # remove temp dir
    temp_dir.remove_tmp_dir()