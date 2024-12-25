from pdf2image import convert_from_path, convert_from_bytes


def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path)
    return images


def convert_pdf_to_image_from_bytes(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    return images
