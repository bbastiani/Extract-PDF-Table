from transformers import AutoImageProcessor, TableTransformerForObjectDetection
import torch
import matplotlib.pyplot as plt
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

TABLE_DETECTION_MODEL = "microsoft/table-transformer-detection"
TABLE_STRUCTURE_RECOGNITION_MODEL = "microsoft/table-transformer-structure-recognition"

class TableTransformers():
    def __init__(self, model_name):
        self.image_processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = TableTransformerForObjectDetection.from_pretrained(model_name)

    def detect(self, image):
        inputs = self.image_processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)

        # convert outputs (bounding boxes and class logits) to COCO API
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.image_processor.post_process_object_detection(outputs, threshold=0.8, target_sizes=target_sizes)[0]

        return results  
    
    def image_from_path(self, path):
        return Image.open(path).convert("RGB")
    

class TableStructureRecognition(TableTransformers):
    def __init__(self):
        super().__init__(TABLE_STRUCTURE_RECOGNITION_MODEL)  

    def table_structure(self, image):
        results = self.detect(image)
        rows = {}
        cols = {}
        for idx, (_, label, box) in enumerate(zip(results["scores"], results["labels"], results["boxes"])):
            xmin, ymin, xmax, ymax = box.tolist()
            class_text = self.model.config.id2label[label.item()]

            if class_text == 'table row':
                rows['table row.'+str(idx)] = (xmin, ymin, xmax, ymax)
            if class_text == 'table column':
                cols['table column.'+str(idx)] = (xmin, ymin, xmax, ymax)

        return rows, cols
    
class TableDetection(TableTransformers):
    def __init__(self):
        super().__init__(TABLE_DETECTION_MODEL)

    def table_detection(self, image):
        results = self.detect(image)
        tables = {}
        for idx, (_, label, box) in enumerate(zip(results["scores"], results["labels"], results["boxes"])):
            xmin, ymin, xmax, ymax = box.tolist()
            class_text = self.model.config.id2label[label.item()]
            if class_text == 'table':
                tables['table.'+str(idx)] = (xmin, ymin, xmax, ymax)
        return tables

if __name__ == "__main__":
    from pdf_document import PdfDoc
    from temp_dir import TempDir
    pdf_path = "./example/sample_table.pdf"
    pdf_doc = PdfDoc(pdf_path)
    temp_dir = TempDir()
    pdf_doc.convert_to_image_save(temp_dir.path)
    file_path = pdf_doc.path + "/out_0.jpg"
    table_detection = TableDetection()
    table_structure_recognition = TableStructureRecognition()
    # detect tables
    image = table_detection.image_from_path(file_path)
    results = table_detection.detect(image)
    print(results)
