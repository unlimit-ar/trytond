import json
import logging
import time as time_module
from datetime import date, datetime, time

from jinja2 import Environment, StrictUndefined, TemplateError
from trytond.pool import Pool
from trytond.transaction import Transaction

LOGGER = logging.getLogger(__name__)


class ConfigProxy:
    "Expose integration_api.* configuration parameters as attributes."

    def __getattr__(self, name):
        pool = Pool()
        try:
            Config = pool.get('ir.config_parameter')
        except KeyError:
            return ''
        try:
            return Config.get_param('integration_api.%s' % name) or ''
        except Exception:
            LOGGER.exception('Could not read integration API parameter %s', name)
            return ''


class RecordSnapshot:
    "Attribute based wrapper for deleted record snapshots."

    def __init__(self, values):
        self._values = values or {}
        self.id = self._values.get('id')

    def __getattr__(self, name):
        return self._values.get(name)

    def __repr__(self):
        return '<RecordSnapshot %r>' % self._values


class IntegrationEngine:
    "Configurable HTTP integration engine."

    RecordSnapshot = RecordSnapshot

    @classmethod
    def find_integrations(cls, model_name, event):
        try:
            Endpoint = Pool().get('integration.endpoint')
        except KeyError:
            return []
        if not cls._table_exists(Endpoint):
            return []
        return Endpoint.search([
            ('active', '=', True),
            ('model_name', '=', model_name),
            ('event', '=', event),
            ])

    @classmethod
    def _table_exists(cls, Model):
        table = Model.__table__()
        table_name = getattr(table, '_name', None) or getattr(table, 'name')
        cursor = Transaction().connection.cursor()
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = current_schema() AND table_name = %s",
            (table_name,))
        return bool(cursor.fetchone())

    @classmethod
    def get_user(cls):
        user_id = Transaction().user
        if not user_id:
            return None
        try:
            User = Pool().get('res.user')
            return User(user_id)
        except Exception:
            LOGGER.exception('Could not load current user %s', user_id)
            return None

    @classmethod
    def get_company(cls):
        company_id = Transaction().context.get('company')
        if not company_id:
            return None
        try:
            Company = Pool().get('company.company')
            return Company(company_id)
        except KeyError:
            return None
        except Exception:
            LOGGER.exception('Could not load current company %s', company_id)
            return None

    @classmethod
    def get_context(cls, record, user=None, company=None):
        return {
            'record': record,
            'user': user if user is not None else cls.get_user(),
            'company': company if company is not None else cls.get_company(),
            'datetime': datetime,
            'date': date,
            'time': time,
            'config': ConfigProxy(),
            }

    @classmethod
    def evaluate_condition(cls, endpoint, record, user=None, company=None):
        expression = (endpoint.condition_expression or '').strip()
        if not expression:
            return True
        context = cls.get_context(record, user=user, company=company)
        return bool(eval(expression, {'__builtins__': {}}, context))

    @classmethod
    def render_template(cls, template, record, user=None, company=None):
        template = template or ''
        if not template.strip():
            return ''
        environment = Environment(undefined=StrictUndefined, autoescape=False)
        try:
            return environment.from_string(template).render(
                **cls.get_context(record, user=user, company=company))
        except TemplateError:
            LOGGER.exception('Could not render integration template')
            raise

    @classmethod
    def enqueue_execution(cls, endpoint_id, model_name, record_id, event,
            record_data=None, attempt=0):
        Endpoint = Pool().get('integration.endpoint')
        endpoint = Endpoint(endpoint_id)
        Endpoint.__queue__.execute(
            [endpoint], model_name, record_id, event, record_data, attempt)

    @classmethod
    def process_event(cls, model, event, records, record_snapshots=None):
        model_name = model.__name__
        integrations = cls.find_integrations(model_name, event)
        if not integrations:
            return

        user = cls.get_user()
        company = cls.get_company()
        for index, record in enumerate(records):
            record_data = None
            record_object = record
            if event == 'delete':
                record_data = (
                    record_snapshots[index] if record_snapshots else
                    cls.record_snapshot(record))
                record_object = RecordSnapshot(record_data)

            for endpoint in integrations:
                try:
                    if not cls.evaluate_condition(
                            endpoint, record_object, user=user,
                            company=company):
                        continue
                    cls.enqueue_execution(
                        endpoint.id, model_name, getattr(record, 'id', None),
                        event, record_data=record_data)
                except Exception as exc:
                    LOGGER.exception(
                        'Could not enqueue integration endpoint %s',
                        endpoint.id)
                    cls.create_log(
                        endpoint=endpoint,
                        model_name=model_name,
                        record_id=getattr(record, 'id', None),
                        request_url='',
                        request_method=endpoint.method,
                        request_headers='',
                        request_payload='',
                        response_status=None,
                        response_headers='',
                        response_body='',
                        execution_time=0.0,
                        success=False,
                        error_message=str(exc),
                        )

    @classmethod
    def record_snapshot(cls, record):
        data = {}
        if not record:
            return data
        fields_ = getattr(record.__class__, '_fields', {}) or {}
        for name in fields_:
            try:
                value = getattr(record, name)
            except Exception:
                continue
            data[name] = cls._json_value(value)
        data.setdefault('id', getattr(record, 'id', None))
        return data

    @classmethod
    def _json_value(cls, value):
        if value is None or isinstance(value, (str, bool, int, float)):
            return value
        if isinstance(value, (date, datetime, time)):
            return value.isoformat()
        if hasattr(value, 'id'):
            return value.id
        if isinstance(value, (list, tuple)):
            return [cls._json_value(v) for v in value]
        try:
            iterator = iter(value)
        except TypeError:
            return str(value)
        return [cls._json_value(v) for v in iterator]

    @classmethod
    def _loads_template_json(cls, text, default=None):
        if not text or not text.strip():
            return default
        return json.loads(text)

    @classmethod
    def _request_payload(cls, method, payload):
        params = data = json_data = None
        if method in {'GET', 'DELETE'}:
            if isinstance(payload, dict):
                params = payload
            else:
                data = payload
        elif isinstance(payload, (dict, list)):
            json_data = payload
        else:
            data = payload
        return params, data, json_data

    @classmethod
    def execute_http_request(cls, endpoint, record, user=None, company=None,
            record_data=None, attempt=0):
        import requests

        if record_data is not None:
            record = RecordSnapshot(record_data)

        request_url = ''
        request_method = endpoint.method
        request_headers = ''
        request_payload = ''
        response_status = None
        response_headers = ''
        response_body = ''
        execution_time = 0.0
        success = False
        error_message = ''
        retry = False

        start_time = time_module.monotonic()
        try:
            request_url = cls.render_template(
                endpoint.url, record, user=user, company=company)
            headers_text = cls.render_template(
                endpoint.headers_template or '{}', record, user=user,
                company=company)
            payload_text = cls.render_template(
                endpoint.payload_template or '', record, user=user,
                company=company)
            headers = cls._loads_template_json(headers_text, default={})
            payload = cls._loads_template_json(payload_text, default=None)
            if headers is None:
                headers = {}
            if not isinstance(headers, dict):
                raise ValueError('Headers template must render a JSON object')

            params, data, json_data = cls._request_payload(
                endpoint.method, payload)
            response = requests.request(
                method=endpoint.method,
                url=request_url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=endpoint.timeout or 30,
                )
            response_status = response.status_code
            response_headers = json.dumps(dict(response.headers))
            response_body = response.text
            response.raise_for_status()
            success = True
        except (
                requests.Timeout,
                requests.ConnectionError,
                requests.HTTPError,
                requests.RequestException,
                TemplateError,
                ValueError,
                json.JSONDecodeError,
                ) as exc:
            error_message = str(exc)
            retry = True
            LOGGER.exception(
                'Integration endpoint %s failed', getattr(endpoint, 'id', None))
        except Exception as exc:
            error_message = str(exc)
            retry = True
            LOGGER.exception(
                'Unexpected integration endpoint %s failure',
                getattr(endpoint, 'id', None))
        finally:
            execution_time = time_module.monotonic() - start_time
            request_headers = (
                json.dumps(headers) if 'headers' in locals() else '')
            if 'payload' in locals():
                request_payload = (
                    json.dumps(payload) if isinstance(payload, (dict, list))
                    else str(payload or ''))
            cls.create_log(
                endpoint=endpoint,
                model_name=endpoint.model_name,
                record_id=getattr(record, 'id', None),
                request_url=request_url,
                request_method=request_method,
                request_headers=request_headers,
                request_payload=request_payload,
                response_status=response_status,
                response_headers=response_headers,
                response_body=response_body,
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                )

        if retry and attempt < (endpoint.retry_count or 0):
            cls.enqueue_execution(
                endpoint.id, endpoint.model_name, getattr(record, 'id', None),
                endpoint.event, record_data=record_data, attempt=attempt + 1)
        return success

    @classmethod
    def create_log(cls, endpoint, model_name, record_id, request_url,
            request_method, request_headers, request_payload, response_status,
            response_headers, response_body, execution_time, success,
            error_message):
        Log = Pool().get('integration.log')
        with Transaction().set_user(0):
            Log.create([{
                        'endpoint': endpoint.id if endpoint else None,
                        'model_name': model_name,
                        'record_id': record_id,
                        'execution_date': datetime.now(),
                        'request_url': request_url,
                        'request_method': request_method,
                        'request_headers': request_headers,
                        'request_payload': request_payload,
                        'response_status': response_status,
                        'response_headers': response_headers,
                        'response_body': response_body,
                        'execution_time': execution_time,
                        'success': success,
                        'error_message': error_message,
                        }])
