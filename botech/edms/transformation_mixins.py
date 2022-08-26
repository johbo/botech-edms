import io
import pkgutil

from PIL import Image, ImageColor, ImageDraw, ImageFont


ANCHOR_RIGHT_ASCENDER = 'ra'
ANCHOR_RIGHT_DESCENDER = 'rd'

class TransformationStampAccountingMetadataMixin:

    def execute_on(self, *args, **kwargs):
        super().execute_on(*args, **kwargs)

        self.font = _get_font()

    def stamp_accounting_data(self, image):
        """
        Stamps accounting data into the document
        """

        image = image.convert(mode='RGBA')
        txt_image = Image.new(
            mode='RGBA', size=image.size, color=(255, 255, 255, 0))


        draw = ImageDraw.Draw(im=txt_image)

        # TODO: calculated positions better:
        # - x percent from the right
        # - x percent from the bottom
        pos_x = image.size[0] - 200
        pos_y = 100
        stamp_text = self.acct_doc_number
        text_color = (255, 0, 0, 125)

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_ASCENDER, font=self.font,
            fill=text_color,
            # TODO: Check if this is interesting to create outline fonts and be
            # more robust so that the document shines through
            # stroke_fill=150, stroke_width=5
        )

        pos_y = 200
        stamp_text = self.acct_booked_stamp

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_ASCENDER, font=self.font, fill=text_color)

        pos_y = image.size[1] - 500
        stamp_text = self.acct_assignment

        draw.text(
            (pos_x, pos_y), stamp_text,
            anchor=ANCHOR_RIGHT_DESCENDER, font=self.font, fill=text_color)

        image = Image.alpha_composite(image, txt_image)

        return image


def _get_font():
    font_bytes = pkgutil.get_data('botech.edms', 'fonts/Roboto-Bold.ttf')
    font_file = io.BytesIO(font_bytes)
    font = ImageFont.truetype(font=font_file, size=80)
    return font
