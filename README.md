# Extract-PDF-Table

A python code for table extraction from pdf files, 
which uses the pre-trained models `microsoft/table-transformer-detection`
and `microsoft/table-transformer-structure-recognition` to detect tables and recognize their structure

## Usage

CLI:
```sh
$ python table_extraction.py -f example.pdf -o output_dir
```

Python library:
```python
from table_extraction import ExtractPdfTables

pdf_tables = ExtractPdfTables("example.pdf")
# extract table, return a list of dataframes
tables = pdf_tables.extract_tables()
# save tables as csv
pdf_tables.tables_to_csv(tables, "output_dir")
```
