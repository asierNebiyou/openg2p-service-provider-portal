# from odoo import models, fields, api


# class g2p_service_provider_benificiary_management(models.Model):
#     _name = 'g2p_service_provider_benificiary_management.g2p_service_provider_benificiary_management'
#     _description = 'g2p_service_provider_benificiary_management.g2p_service_provider_benificiary_management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
