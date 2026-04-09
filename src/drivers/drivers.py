from core.config import settings as s

from drivers.scales.scales_base import BaseScalesDriver
from drivers.scales.digi.di160 import weight_service_digi_di160
from drivers.scales.mettler_toledo.mt_sics import weight_service_mt_sics
from drivers.scales.tenzo_m.tenso_m import weight_service_tenso_m

from drivers.printers.printers_base import BasePrinterDriver
from drivers.printers.dpl.dpl import printer_dpl_driver
from drivers.printers.ezpl.ezpl import printer_ezpl_driver


scales_drivers = {
    'tenzo_m': weight_service_tenso_m,
    'mt_sics': weight_service_mt_sics,
    'digi_di160': weight_service_digi_di160,
}

printer_drivers = {
    'dpl': printer_dpl_driver,
    'ezpl': printer_ezpl_driver,
}


def get_printer_driver(driver: str) -> BasePrinterDriver | None:
    """Возвращаем запрошенный драйвер принтера, если нашли его."""
    return printer_drivers.get(driver, None)


def get_scales_driver(driver: str) -> BaseScalesDriver | None:
    """Возвращаем запрошенный драйвер весов, если нашли его."""
    return scales_drivers.get(driver, None)


def printer_driver_name_validator(value: str) -> str:
    """Проверяем указанное имя драйвера."""
    if value not in printer_drivers.keys():
        raise ValueError(s.MESSAGE_WRONG_DRIVER_NAME)

    return value


def scales_driver_name_validator(value: str) -> str:
    """Проверяем указанное имя драйвера."""
    if value not in scales_drivers.keys():
        raise ValueError(s.MESSAGE_WRONG_DRIVER_NAME)

    return value
