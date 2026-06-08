from odoo import models, fields, api
import base64

class ImagePreview(models.TransientModel):
    _name = 'image.preview'
    _description = "image_priview"

    image = fields.Binary(default=lambda self:self.image_recover())
    
    def image_recover(self):
        
        active_model = self.env.context.get('active_model')
        attachment = self.env[active_model].browse(self.env.context.get('active_id'))

        # img = base64.b64encode(attachment.datas)
        # print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",img)
        return attachment.datas

  