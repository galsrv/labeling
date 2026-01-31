# from device_controller.scales.digi.di160 import weight_service_digi_di160
# from device_controller.scales.mettler_toledo.mt_sics import weight_service_mt_sics
# from device_controller.scales.tenzo_m.tenso_m import weight_service_tenso_m

from device_controller.printers.printers_base import BasePrinterDriver
from device_controller.printers.dpl.dpl import printer_service_dpl

drivers = {
    # 'tenzo_m': weight_service_tenso_m,
    # 'mt_sics': weight_service_mt_sics,
    # 'digi_di160': weight_service_digi_di160,
    'dpl': printer_service_dpl,
}

printer_drivers = {
    'dpl': printer_service_dpl,
}

# TPrinterDriver = TypeVar('TPrinterDriver', bound=BasePrinterDriver)


def get_printer_driver(driver: str) -> BasePrinterDriver | None:
    """Возвращаем запрошенный драйвер принтера, если нашли его."""
    return drivers.get(driver, None)
