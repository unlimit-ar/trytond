import logging

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.model import (
    DeactivableMixin, Index, ModelSQL, ModelView, MultiValueMixin, Unique,
    ValueMixin, convert_from, fields, sequence_ordered)

from .engine import IntegrationEngine

LOGGER = logging.getLogger(__name__)


class IntegrationEndpoint(ModelSQL, ModelView, DeactivableMixin):
    __name__ = 'integration.endpoint'

    name = fields.Char('Name', required=True)
    model_name = fields.Char('Model Name', required=True)
    event = fields.Selection([
            ('create', 'Create'),
            ('write', 'Write'),
            ('delete', 'Delete'),
            ], 'Event', required=True)
    url = fields.Char('URL', required=True)
    method = fields.Selection([
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('PATCH', 'PATCH'),
            ('DELETE', 'DELETE'),
            ], 'Method', required=True)
    headers_template = fields.Text('Headers Template')
    payload_template = fields.Text('Payload Template')
    condition_expression = fields.Text('Condition Expression')
    timeout = fields.Integer('Timeout', required=True)
    retry_count = fields.Integer('Retry Count', required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'test_integration': {},
            })


    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_method():
        return 'POST'

    @staticmethod
    def default_timeout():
        return 30

    @staticmethod
    def default_retry_count():
        return 0

    @classmethod
    @ModelView.button_action('integration_api.wizard_integration_endpoint_test_form')
    def test_integration(cls, endpoints):
        pass

    @classmethod
    def execute(cls, endpoints, model_name, record_id, event, record_data=None,
            attempt=0):
        from .queue import execute_integration_job

        for endpoint in endpoints:
            execute_integration_job(
                endpoint.id, model_name, record_id, event, record_data, attempt)


class IntegrationLog(ModelSQL, ModelView):
    "Integration Log"
    __name__ = 'integration.log'

    endpoint = fields.Many2One(
        'integration.endpoint', 'Endpoint', readonly=True, ondelete='SET NULL')
    model_name = fields.Char('Model Name', readonly=True)
    record_id = fields.Integer('Record ID', readonly=True)
    execution_date = fields.DateTime('Execution Date', readonly=True)
    request_url = fields.Char('Request URL', readonly=True)
    request_method = fields.Char('Request Method', readonly=True)
    request_headers = fields.Text('Request Headers', readonly=True)
    request_payload = fields.Text('Request Payload', readonly=True)
    response_status = fields.Integer('Response Status', readonly=True)
    response_headers = fields.Text('Response Headers', readonly=True)
    response_body = fields.Text('Response Body', readonly=True)
    execution_time = fields.Float('Execution Time', readonly=True)
    success = fields.Boolean('Success', readonly=True)
    error_message = fields.Text('Error Message', readonly=True)


def patch_modelsql_events():
    if getattr(ModelSQL, '_integration_api_patched', False):
        return

    original_create = ModelSQL.__dict__['create']
    original_write = ModelSQL.__dict__['write']
    original_delete = ModelSQL.__dict__['delete']

    original_create_func = getattr(original_create, '__func__', original_create)
    original_write_func = getattr(original_write, '__func__', original_write)
    original_delete_func = getattr(original_delete, '__func__', original_delete)

    @classmethod
    def create(cls, vlist):
        records = original_create_func(cls, vlist)
        print(f"Creating records: {records}", flush=True)
        _process_event(cls, 'create', records)
        return records

    @classmethod
    def write(cls, *args):
        print(f"Writing records: {args}", flush=True)
        result = original_write_func(cls, *args)
        records = []
        for index in range(0, len(args), 2):
            if index < len(args):
                records.extend(args[index])
        _process_event(cls, 'write', records)
        return result

    @classmethod
    
    def delete(cls, records):
        snapshots = None
        if _should_process_model(cls):
            snapshots = [IntegrationEngine.record_snapshot(r) for r in records]
        result = original_delete_func(cls, records)
        _process_event(cls, 'delete', records, snapshots)
        return result

    ModelSQL._integration_api_original_create = original_create
    ModelSQL._integration_api_original_write = original_write
    ModelSQL._integration_api_original_delete = original_delete
    ModelSQL.create = create
    ModelSQL.write = write
    ModelSQL.delete = delete
    ModelSQL._integration_api_patched = True


def _process_event(model, event, records, record_snapshots=None):
    if not records:
        return
    if not _should_process_model(model):
        return

    try:
        IntegrationEngine.process_event(
            model, event, records, record_snapshots=record_snapshots)
    except Exception:
        LOGGER.exception(
            'Could not enqueue integration event %s for %s',
            event, getattr(model, '__name__', model))


def _should_process_model(model):
    model_name = getattr(model, '__name__', '')
    if model_name.startswith('integration.'):
        return False
    if model_name.startswith(('ir.', 'res.')):
        return False
    return True


patch_modelsql_events()
