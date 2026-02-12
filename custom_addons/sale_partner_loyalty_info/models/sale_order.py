from odoo import models, fields, api, _

class SalesOrder(models.Model):
    _inherit = 'sale.order' #Esta es la tabla que aparece en el modulo Sale de Odoo

    order_points = fields.Float(
        string='Puntos de Lealtad',
        compute='_get_loyalty_points',
        help="Puntos de Lealtad Ganados",
        store=True
    )

    # amount_total viene de Sale de la tabla, tenemos acceso por que lo estamos heredando
    # coupon_point_ids >>> Cuando hayan modificaciones o se creen nuevos cupones
    @api.depends('amount_total', "coupon_point_ids")
    def _get_loyalty_points(self):
        for sale in self: #self es un record set
            if sale.coupon_point_ids:
                points =  sale.coupon_point_ids.mapped('points') #Ese dato viene de del modulo Loyalty - Es una relación donde almacena todos los puntos
                sale.order_points = sum(points)
                print(f"Order points recomputed: >>>>> {points}")
            else:
                sale.order_points = 0.0