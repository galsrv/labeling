from devices.base import BaseDeviceDriver

from devices.scales.digi.di160 import weight_service_digi_di160
from devices.scales.mettler_toledo.mt_sics import weight_service_mt_sics
from devices.scales.tenzo_m.tenso_m import weight_service_tenso_m

from devices.printers.dpl.dpl import printer_service_dpl

drivers = {
    'tenzo_m': weight_service_tenso_m,
    'mt_sics': weight_service_mt_sics,
    'digi_di160': weight_service_digi_di160,
    'dpl': printer_service_dpl
}


def get_driver(driver: str) -> BaseDeviceDriver | None:
    """Возвращаем запрошенный драйвер весов, если нашли его."""
    return drivers.get(driver, None)
