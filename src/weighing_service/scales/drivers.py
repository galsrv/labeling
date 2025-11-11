from scales.base import BaseWeightClient
from scales.tenzo_m.tenso_m import weight_service_tenso_m

drivers = {
    'tenzo_m': weight_service_tenso_m,
}


def get_driver(model: str) -> BaseWeightClient | None:
    """Возвращаем запрошенный драйвер весов, если нашли его."""
    return drivers.get(model, None)
