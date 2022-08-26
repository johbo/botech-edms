import io
import pkgutil

from PIL import Image, ImageColor, ImageDraw, ImageFont

class TransformationStampAccountingMetadataMixin:

    def stamp_accounting_data(self):
        # TODO: opacity? RGBA mode?

        font_bytes = pkgutil.get_data('botech.edms', 'fonts/Roboto-Bold.ttf')
        font_file = io.BytesIO(font_bytes)
        font = ImageFont.truetype(font=font_file, size=80)

        stamp_text = "BOOKED"

        length = font.getlength(stamp_text)
        pos_x = self.image.size[0] - length - 100

        draw = ImageDraw.Draw(im=self.image)
        draw.text((pos_x, 100), stamp_text, font=font, fill=128)
        return self.image
