from werkzeug.wrappers import Response

from trytond.wsgi import app
from trytond.transaction import Transaction
from trytond.protocols.wrappers import (
    HTTPStatus, Response, abort, redirect, with_pool, with_transaction, parse_authorization_header)

# autoventa_application = user_application(1)
url_start = '/<database_name>/prueba'


# @app.route(f'{url_start}/healthcheck', methods=['GET'])
# @autoventa_application
# def health_check(request):
#     return Response(None, 200)


@app.route(f'{url_start}/hello_world', methods=['POST'])
@with_pool
@with_transaction()
def hello_world(request, pool):
    UserApplication = pool.get('res.user.application')
    User = pool.get('res.user')
    authorization = request.authorization
    if authorization is None:
        header = request.headers.get('Authorization')
        authorization = parse_authorization_header(header)
    if authorization is None:
        abort(HTTPStatus.UNAUTHORIZED)
    if authorization.type != 'bearer':
        abort(HTTPStatus.FORBIDDEN)

    token = getattr(authorization, 'token', '')
    application = UserApplication.check(token, 'prueba')
    user = User(1)
    user.name = 'Prueba'
    user.save()
    
    print(application)
    transaction = Transaction()
    context = transaction.context
    print(transaction.user)
    print(context)
    print('hello_world')
    return {'text': 'Hello World'}