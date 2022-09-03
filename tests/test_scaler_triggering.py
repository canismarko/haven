"""The scaler has a global trigger, but individual channels.

These tests check the system for monitoring the trigger system in
bluesky so that it only fires the trigger once for all of the scaler
channels. Additionally, the scaler can send that trigger to other
devices, like the Xspress3 fluorescence detector readout electronics.

"""

import pytest
from ophyd import Device


from haven.instrument.ion_chamber import ScalerTriggered
from haven import exceptions


def test_trigger_fires():
    scaler_prefix = "myioc:myscaler"
    # Prepare the scaler triggered device
    MyDevice = type("MyDevice", (ScalerTriggered, Device), {})
    device = MyDevice(name="device", scaler_prefix=scaler_prefix)
    # Make sure it's in a sensible starting state
    assert hasattr(device, "_statuses")
    assert len(device._statuses) == 0
    # Trigger the device
    device.trigger()
    # Check that a status was added
    assert len(device._statuses) == 1
    # Check that triggering again is indempotent
    first_status = device._statuses[scaler_prefix]
    old_done = first_status.__class__.done
    first_status.__class__.done = False
    try:
        device.trigger()
    except:
        pass
    finally:
        first_status.__class__.done = old_done
    second_status = device._statuses[scaler_prefix]
    assert first_status is second_status


def test_default_pv_prefix():
    """Check that it uses the *prefix* argument if no *scaler_prefix* is
    given.

    """
    prefix = "myioc:myscaler"
    MyDevice = type("MyDevice", (ScalerTriggered, Device), {})
    # Instantiate the device with *scaler_prefix* argument
    device = MyDevice(name="device", prefix=None, scaler_prefix=prefix)
    assert device.scaler_prefix == prefix
    # Instantiate the device with *scaler_prefix* argument
    device = MyDevice(name="device", prefix=prefix)
    assert device.scaler_prefix == prefix