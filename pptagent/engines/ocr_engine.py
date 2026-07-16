"""
OCR engine wrapper for extracting text from images within PowerPoint slides.

Supports EasyOCR and PaddleOCR with configurable fallback,
and confidence thresholding.
"""

from __future__ import annotations

from typing import Any


class OCREngine:
    """Optical Character Recognition engine wrapper.

    Provides a unified interface over EasyOCR and PaddleOCR backends.
    The active backend is selected via the global config
    (``extraction.ocr_engine``).

    Typical usage::

        engine = OCREngine()
        results = engine.extract(image_bytes)
        for block in results:
            print(block["text"], block["confidence"])
    """

    def __init__(self, languages: list[str] | None = None) -> None:
        """Initialise the OCR engine.

        ## Parameters
        `languages`:
            `List` of language codes (e.g. ``["en", "ch_sim"]``).
            When ``None``, the value from the global config is used.
        """
        from pptagent.utils.config import get_config

        cfg = get_config().extraction
        self._languages: list[str] = languages or cfg.ocr_languages
        self._engine_name: str = cfg.ocr_engine
        self._confidence_threshold: float = cfg.ocr_confidence_threshold
        self._reader: Any = None  # lazily initialised

    @property
    def is_ready(self) -> bool:
        """Return ``True`` when the underlying reader has been loaded."""
        return self._reader is not None

    def _init_reader(self) -> None:
        """Lazily load the OCR reader (heavy import)."""
        if self._reader is not None:
            return

        if self._engine_name == "easyocr":
            try:
                import easyocr
            except ImportError as exc:
                raise ImportError(
                    "EasyOCR is not installed. Run: pip install easyocr"
                ) from exc
            self._reader = easyocr.Reader(self._languages, gpu=False)
        elif self._engine_name == "paddleocr":
            try:
                # may fail? paddleocr is a heavy dependency.
                from paddleocr import PaddleOCR
            except ImportError as exc:
                raise ImportError(
                    "PaddleOCR is not installed. Run: pip install paddleocr"
                ) from exc
            self._reader = PaddleOCR(lang="en", use_angle_cls=True)
        else:
            raise ValueError(
                f"Unknown OCR engine: {self._engine_name}. "
                "Supported: 'easyocr', 'paddleocr'."
            )

    def extract(self, image: bytes | str) -> list[dict[str, Any]]:
        """Run OCR on an image and return structured results.

        ## Parameters
        `image`:
            Either raw image `bytes` or a file `path` to an image.

        Returns
        -------
        list[dict]
            Each dict contains ``text`` (str), ``confidence`` (float),
            and ``bbox`` (list of 4 corner points).
        """
        self._init_reader()
        assert self._reader is not None

        if self._engine_name == "easyocr":
            raw = self._reader.readtext(image)
            results: list[dict[str, Any]] = []
            for item in raw:
                # item = (bbox, text, confidence)
                bbox, text, conf = item[0], item[1], item[2]
                if conf >= self._confidence_threshold:
                    results.append({
                        "text": text,
                        "confidence": conf,
                        "bbox": [[int(p[0]), int(p[1])] for p in bbox],
                    })
            return results

        # PaddleOCR path
        raw = self._reader.ocr(image)
        if raw is None or raw[0] is None:
            return []
        results = []
        for item in raw[0]:
            bbox, (text, conf) = item[0], item[1]
            if conf >= self._confidence_threshold:
                results.append({
                    "text": text,
                    "confidence": conf,
                    "bbox": [[int(p[0]), int(p[1])] for p in bbox],
                })
        return results

    def extract_from_element(
        self, image_bytes: bytes, element_id: str = ""
    ) -> dict[str, Any]:
        """Convenience wrapper that attaches element metadata.

        ## Parameters
        `image_bytes`:
            Raw image `bytes` (e.g. from ``Element.content["blob"]``).
        `element_id`:
            Optional `str` element id.

        ## Returns

        `Dict` {element_id: `str`, full_text: `str`, ``blocks``: `list`, ``block_count``: `int`}.
        """
        blocks = self.extract(image_bytes)
        full_text = " ".join(b["text"] for b in blocks)
        return {
            "element_id": element_id,
            "full_text": full_text,
            "blocks": blocks,
            "block_count": len(blocks),
            "engine": self._engine_name,
        }
