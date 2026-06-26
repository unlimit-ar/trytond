import logging

from trytond.pool import Pool

from .engine import IntegrationEngine

LOGGER = logging.getLogger(__name__)


def execute_integration_job(endpoint_id, model_name, record_id, event,
        record_data=None, attempt=0):
    pool = Pool()
    Endpoint = pool.get('integration.endpoint')
    endpoint = Endpoint(endpoint_id)

    record = None
    if event == 'delete':
        record = IntegrationEngine.RecordSnapshot(record_data)
    elif record_id:
        Model = pool.get(model_name)
        record = Model(record_id)

    return IntegrationEngine.execute_http_request(
        endpoint, record, record_data=record_data, attempt=attempt)
