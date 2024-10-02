from typing import List

from App.Core.Utils import DocumentMediaType, DocumentBanner, DocumentOrder


class PrintingService:
    @staticmethod
    # DEVICE_PRINTING_PARAMETER_PRINTER: "device",
    # DEVICE_PRINTING_PARAMETER_NUM_COPIES: "copies",
    # DEVICE_PRINTING_PARAMETER_MEDIA_NAME: "media",
    # DEVICE_PRINTING_PARAMETER_PAGE_RANGES: "pages",
    # DEVICE_PRINTING_PARAMETER_JOB_SHEETS: "banner",
    # DEVICE_PRINTING_PARAMETER_OUTPUT_ORDER: "order",
    # DEVICE_PRINTING_PARAMETER_MIRROR: "mirror",
    # DEVICE_PRINTING_PARAMETER_LANDSCAPE: "landscape",
    def send_to_printing(
            device: int,
            media: List[DocumentMediaType] = None,
            copies: int = 1,
            pages: List[int] = None,
            banner: DocumentBanner = None,
            order: DocumentOrder = None,
            mirror: bool = False,
            landscape: bool = False
    ):
        pass
