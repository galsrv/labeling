from device_controller.scales.digi.di160 import weight_service_digi_di160
from device_controller.scales.mettler_toledo.mt_sics import weight_service_mt_sics
from device_controller.scales.tenzo_m.tenso_m import weight_service_tenso_m

from device_controller.printers.printers_base import BasePrinterController
from device_controller.printers.dpl.dpl import printer_service_dpl

scales_controllers = {
    'tenzo_m': weight_service_tenso_m,
    'mt_sics': weight_service_mt_sics,
    'digi_di160': weight_service_digi_di160,
}

printer_controllers = {
    'dpl': printer_service_dpl,
}

# TPrinterDriver = TypeVar('TPrinterDriver', bound=BasePrinterDriver)


def get_printer_controller(driver: str) -> BasePrinterController | None:
    """Возвращаем запрошенный драйвер принтера, если нашли его."""
    return printer_controllers.get(driver, None)


def get_scales_controller(driver: str) -> BasePrinterController | None:
    """Возвращаем запрошенный драйвер весов, если нашли его."""
    return scales_controllers.get(driver, None)
