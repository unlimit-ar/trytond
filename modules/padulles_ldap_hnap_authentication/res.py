# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import logging
from ldap3.core.exceptions import LDAPException
import requests
import json

from trytond.config import config
from trytond.exceptions import LoginException
from trytond.i18n import gettext
from trytond.pool import PoolMeta, Pool

logger = logging.getLogger(__name__)
section = 'ldap_hnap'

class User(metaclass=PoolMeta):
    __name__ = 'res.user'

    @classmethod
    def _login_ldaphnap(cls, login, parameters):
        User = Pool().get('res.user')
        if 'password' not in parameters:
            msg = gettext('res.msg_user_password', login=login)
            raise LoginException('password', msg, type='password')
        password = parameters['password']
        try:
            headers = {'content-type': 'application/json',
                   'accept': 'application/json'}
            uri = config.get(section, 'uri')
            data = {
                'samaccountname': login,
                'password': password
                }
            responce = requests.post(uri, 
                headers=headers, 
                data=json.dumps(data))
            
            if responce.status_code != 200:
                return
            
            res = responce.json()
            name = res.get('ou').split(',')[0].split('=')[1]
            
            uid = config.get(section, 'uid')

            login = res.get(uid, None)
            user_id = cls._get_login(login)[0]
            if user_id:

                return user_id
            elif config.getboolean(section, 'create_user'):
                user, = cls.create([{
                            'name': name,
                            'login': login,
                            }])
                return user.id
        except LDAPException:
            logger.error('ldap hnap when login', exc_info=True)
