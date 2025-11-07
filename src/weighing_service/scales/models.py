from scales.base import BaseWeightClient
from scales.tenso_m_tv020 import weight_service_tensom_tv020

models = {
    'tenzo_m_tv020': weight_service_tensom_tv020,
}

def get_driver(model: str) -> BaseWeightClient | None:
    return models.get(model, None)
