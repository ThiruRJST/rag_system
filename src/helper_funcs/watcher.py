import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from handlers.pdf_filehandler import PDFHandler

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    path = "/home/tensorthiru/rag_system/data"
    event_handler = LoggingEventHandler()
    pdf_handler = PDFHandler()
    observer = Observer()
    observer.schedule(pdf_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
