import io
import pkgutil

from PIL import Image, ImageColor, ImageDraw, ImageFont


ANCHOR_RIGHT_ASCENDER = 'ra'
ANCHOR_RIGHT_DESCENDER = 'rd'

class TransformationStampAccountingMetadataMixin:

    def stamp_accounting_data(self):
        # TODO: opacity? RGBA mode?

        font_bytes = pkgutil.get_data('botech.edms', 'fonts/Roboto-Bold.ttf')
        font_file = io.BytesIO(font_bytes)
        font = ImageFont.truetype(font=font_file, size=80)

        draw = ImageDraw.Draw(im=self.image)

        # TODO: calculated positions better:
        # - x percent from the right
        # - x percent from the bottom
        pos_x = self.image.size[0] - 200
        pos_y = 100
        stamp_text = self.acct_doc_number

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_ASCENDER, font=font, fill=128)

        pos_y = 200
        stamp_text = self.acct_booked_stamp

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_ASCENDER, font=font, fill=128)

        pos_y = self.image.size[1] - 500
        stamp_text = self.acct_assignment

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_DESCENDER, font=font, fill=128)

        return self.image
