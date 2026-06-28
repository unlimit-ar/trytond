from trytond.exceptions import UserError
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Button, StateTransition, StateView, Wizard

from .engine import IntegrationEngine


class IntegrationEndpointTestStart(ModelView):
    "Test Integration Endpoint"
    __name__ = 'integration.endpoint.test.start'

    endpoint = fields.Many2One(
        'integration.endpoint', 'Endpoint', required=True, readonly=True)
    model_name = fields.Char('Model Name', readonly=True)
    record_id = fields.Integer('Record ID', required=True)

    @fields.depends('endpoint')
    def on_change_with_model_name(self, name=None):
        return self.endpoint.model_name if self.endpoint else ''


class IntegrationEndpointTest(Wizard):
    __name__ = 'integration.endpoint.test'

    start = StateView(
        'integration.endpoint.test.start',
        'integration_api.integration_endpoint_test_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Execute', 'execute', 'tryton-ok', default=True),
            ])
    execute = StateTransition()

    def default_start(self, fields):
        endpoint_id = Transaction().context.get('active_id')
        values = {}
        if endpoint_id:
            Endpoint = Pool().get('integration.endpoint')
            endpoint = Endpoint(endpoint_id)
            values.update({
                    'endpoint': endpoint.id,
                    'model_name': endpoint.model_name,
                    })
        return values

    def transition_execute(self):
        endpoint = self.start.endpoint
        if not endpoint:
            raise UserError('Missing endpoint.')

        Model = Pool().get(endpoint.model_name)
        record = Model(self.start.record_id)
        if not IntegrationEngine.evaluate_condition(endpoint, record):
            raise UserError('The endpoint condition is false for this record.')

        IntegrationEngine.enqueue_execution(
            endpoint.id, endpoint.model_name, record.id, endpoint.event)
        return 'end'
