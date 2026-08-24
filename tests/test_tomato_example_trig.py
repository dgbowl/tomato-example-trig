import time

import pint
import pytest
from dgbowl_schemas.tomato.payload import Task

from tomato_example_trig import DriverInterface

kwargs = dict(address="a", channel="1")


def test_create_device():
    interface = DriverInterface()
    print(f"{interface=}")
    ret = interface.cmp_register(**kwargs)
    assert ret.success
    print(f"{interface.devmap=}")
    assert ("a", "1") in interface.devmap


def test_get_attr():
    interface = DriverInterface()
    ret = interface.cmp_register(**kwargs)
    ret = interface.cmp_attrs(**kwargs)
    assert ret.success
    assert "function" in ret.data
    ret = interface.cmp_get_attr(attr="function", **kwargs)
    assert ret.success
    assert ret.data == "sin"


def test_do_measure():
    interface = DriverInterface()
    interface.cmp_register(**kwargs)
    ret = interface.cmp_measure(**kwargs)
    assert ret.success
    time.sleep(0.1)
    ret = interface.cmp_last_data(**kwargs)
    assert ret.success
    assert ret.data is not None
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (1,)
    assert ret.data.abscissa.shape == (100,)
    assert ret.data.ordinate.shape == (1, 100)


def test_task_random():
    interface = DriverInterface()
    interface.cmp_register(**kwargs)
    task = Task(
        component_role="a1",
        max_duration=1.0,
        sampling_interval=0.1,
        technique_name="trig_function",
        task_params={"function": "sin", "points": 1000},
    )
    ret = interface.task_start(task=task, **kwargs)
    print(f"{ret=}")
    assert ret.success

    time.sleep(0.1)
    ret = interface.cmp_status(**kwargs)
    print(f"{ret=}")
    assert ret.success
    assert ret.data["running"]
    while ret.data["running"]:
        time.sleep(0.2)
        ret = interface.cmp_status(**kwargs)
    ret = interface.task_data(**kwargs)
    assert ret.success
    print(f"{ret.data=}")
    assert ret.data.uts.shape == (10,)
    assert ret.data.abscissa.shape == (1000,)
    assert ret.data.ordinate.shape == (10, 1000)
