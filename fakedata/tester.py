import test_parser

f = "1-mavzu.docx"
tt = test_parser.parse_docx_fill_blanks(file_path=f)
print(tt)