import names
import random

from odoo import fields, models
from odoo.exceptions import ValidationError


class WizardGenerateDemoContacts(models.TransientModel):

    _name = 'wizard.generate.demo.contacts'
    _description = 'Wizard Generate Demo Contacts'

    quantity = fields.Integer(
        string='Quantity',
        default=50
    )
    companies_ratio = fields.Float(
        string='Companies Ratio',
        default=0.2
    )
    active_ratio = fields.Float(
        string='Active Ratio',
        default=0.2
    )
    force_recreate = fields.Boolean(
        string='Force Recreate',
    )
    dry_run = fields.Boolean(
        string='Dry Run',
        default=True
    )

    def not_permitted_ratios(self):
        if ((self.active_ratio <= 0.0 or self.active_ratio > 1.0) or
                (self.companies_ratio <= 0.0 or self.companies_ratio > 1.0)):
            raise ValidationError("Ratios cannot be greater than 1.0 and equal or lower than 0.0!")

    def action_generate_demo_contacts(self):
        category_id = self.env.ref('paycon_res_partner_custom.res_partner_category_paycon_interview')
        contacts_generated = self.env['res.partner'].search(
            [('category_id', '=', category_id.id)]
        )

        self.not_permitted_ratios()

        if len(contacts_generated) > 0 and not self.force_recreate:
            raise ValidationError("Contacts already created!"
                                  "\nUse force recreate to create new contacts!")
        else:
            contacts_generated.unlink()
            if self.dry_run:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Contacts to be created',
                        'message': f'{self.quantity} contacts will be created on Odoo contacts!',
                        'sticky': True,
                        'type': 'info'
                    }
                }

            all_contacts = []
            company_contacts = int(self.quantity * self.companies_ratio)
            active_clients = int(self.quantity * self.active_ratio)
            countries = self.env['res.country'].search([])

            for i in range(self.quantity):
                country = random.choice(countries)
                state = False
                if country.state_ids:
                    state = random.choice(country.state_ids)
                contact = {
                    'name': names.get_full_name(),
                    'is_company': i < company_contacts,
                    'x_cliente_ativo': i < active_clients,
                    'category_id': [(4, category_id.id)],
                    'country_id': country.id,
                    'state_id': state.id if state else False,
                }
                all_contacts.append(contact)
            self.env['res.partner'].create(all_contacts)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Contacts Created!',
                    'message': f'{len(all_contacts)} created on Odoo contacts!',
                    'sticky': True,
                    'type': 'success'
                }
            }