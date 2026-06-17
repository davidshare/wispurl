"""Pure ``short URL -> PNG bytes`` transformation.

This module holds no state and touches no I/O beyond building an in-memory image,
which is what lets the service scale horizontally with zero coordination. The output
is deterministic for a given (data, size), so responses are safely cacheable.

Resource safety: ``box_size`` and ``border`` are fixed small constants and the final
image is produced at the caller-validated ``size_px`` (already clamped to the
configured maximum), so a request cannot drive an unbounded allocation.
"""

from __future__ import annotations

import io

import qrcode
from PIL.Image import Resampling

# Fixed generation parameters. Medium error correction tolerates ~15% damage while
# keeping the symbol compact; the module pixel size is small because the image is
# resized to the requested edge length afterward.
_BOX_SIZE = 10
_BORDER = 4
_ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_M


def generate_qr_png(*, data: str, size_px: int) -> bytes:
    """Render ``data`` as a square PNG QR code of ``size_px`` x ``size_px`` pixels.

    Args:
        data: The string to encode (here, the full short URL).
        size_px: The output edge length in pixels (validated/clamped by the caller).

    Returns:
        The PNG image as bytes.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=_ERROR_CORRECTION,
        box_size=_BOX_SIZE,
        border=_BORDER,
    )
    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white").get_image()
    # NEAREST keeps the module edges crisp (and scannable) when resizing.
    image = image.resize((size_px, size_px), Resampling.NEAREST)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
