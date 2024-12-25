import asyncio
import os
import time

from helper_funcs.pdftoimage import convert_pdf_to_image
from helper_funcs.colpali_helper import indexing_func
from watchdog.events import FileSystemEventHandler


async def convertor_and_index_thread(pdf_path):
    # convert the pdf to images
    filename = os.path.basename(pdf_path)
    images = convert_pdf_to_image(pdf_path)
    print(f"Converted {len(images)} pages to images")

    indexing_func(images)



class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            print(f"PDF file created: {event.src_path}")

            # wait until the file is ready
            self.wait_for_fileready(event.src_path)

            # start the conversion process
            asyncio.run(convertor_and_index_thread(event.src_path))            
            

    def wait_for_fileready(self, path, timeout=30):
        start_time = time.time()
        last_size = -1
        stable_count = 0

        while True:
            current_size = os.path.getsize(path)

            if current_size == last_size:
                stable_count += 1
            else:
                stable_count = 0

            if stable_count > 2:
                return

            if (time.time() - start_time) > timeout:
                print("Timeout reached")
                return
            last_size = current_size
            time.sleep(1)
