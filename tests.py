import pdfkit

abc = {
    "A": {
        "B": 1,
        "C": 2
    },
    "D": 3
}

print([{"E": 4}, abc])

def generate_pdf_from_html(filepath):
    pdfkit.from_string(open(filepath, "r").read(), output_path="Monica/videos_tests.pdf")

generate_pdf_from_html("Monica/videos_tests.html")