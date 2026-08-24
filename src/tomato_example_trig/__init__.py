import logging
import math
from datetime import datetime
from datetime import timezone as tz

import numpy as np
import pint
import xarray as xr
from tomato.driverinterface_2_1 import Attr, ModelDevice, ModelInterface
from tomato.driverinterface_2_1.decorators import coerce_val
from tomato.driverinterface_2_1.types import Val

logger = logging.getLogger(__name__)

CHOICES = {"sin", "cos", "tan"}


class Device(ModelDevice):
    function: str
    points: int

    def __init__(self, driver, key, **kwargs):
        super().__init__(driver, key, **kwargs)
        self.param = pint.Quantity("1.0 s")
        self.function = "sin"
        self.points = 100

    def do_measure(self, **kwargs) -> None:
        uts = datetime.now(tz.utc).timestamp()
        offset = ((uts % 3600) / 10) * ((2 * math.pi) / 360)
        abscissa = np.linspace(0, 1, self.points)
        func = getattr(np, self.function)
        ordinate = func(abscissa + offset)

        data_vars = {
            "ordinate": (["uts", "abscissa"], [list(ordinate)]),
        }
        for key in self.attrs(**kwargs):
            val = self.get_attr(attr=key)
            if isinstance(val, pint.Quantity):
                data_vars[key] = (["uts"], [val.m], {"units": str(val.u)})
            else:
                data_vars[key] = (["uts"], [val])

        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [uts]), "abscissa": (["abscissa"], abscissa)},
        )

    @coerce_val
    def set_attr(self, attr: str, val: Val, **kwargs: dict) -> Val:
        setattr(self, attr, val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        if not hasattr(self, attr):
            raise AttributeError(f"unknown attr: {attr!r}")
        return getattr(self, attr)

    def attrs(self, **kwargs: dict) -> dict:
        return {
            "points": Attr(type=int, rw=True, status=True),
            "function": Attr(
                type=str,
                rw=True,
                status=True,
                options=CHOICES,
            ),
        }

    def capabilities(self, **kwargs: dict) -> set:
        return {"trig_function"}


class DriverInterface(ModelInterface):
    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)
