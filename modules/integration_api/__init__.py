from trytond.pool import Pool

from . import model
from . import wizard


def register():
    Pool.register(
        model.IntegrationEndpoint,
        model.IntegrationLog,
        wizard.IntegrationEndpointTestStart,
        module='integration_api', type_='model')
    Pool.register(
        wizard.IntegrationEndpointTest,
        module='integration_api', type_='wizard')
    model.patch_modelsql_events()
