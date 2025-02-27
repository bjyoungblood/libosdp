#
#  Copyright (c) 2021-2022 Siddharth Chandrasekaran <sidcha.dev@gmail.com>
#
#  SPDX-License-Identifier: Apache-2.0
#

import time
import pytest

from testlib import *

pd_cap = PDCapabilities([
    (Capability.OutputControl, 1, 1),
    (Capability.LEDControl, 1, 1),
    (Capability.AudibleControl, 1, 1),
    (Capability.TextOutput, 1, 1),
])

pd_info_list = [
    PDInfo(101, scbk=KeyStore.gen_key(), flags=[ LibFlag.EnforceSecure ], name='chn-0'),
]

secure_pd = PeripheralDevice(pd_info_list[0], pd_cap, log_level=LogLevel.Debug)

pd_list = [
    secure_pd,
]

cp = ControlPanel(pd_info_list, log_level=LogLevel.Debug)

@pytest.fixture(scope='module', autouse=True)
def setup_test():
    for pd in pd_list:
        pd.start()
    cp.start()
    cp.online_wait_all()
    yield
    teardown_test()

def teardown_test():
    cp.teardown()
    for pd in pd_list:
        pd.teardown()

def test_event_keypad():
    event = {
        'event': Event.KeyPress,
        'reader_no': 1,
        'data': bytes([9,1,9,2,6,3,1,7,7,0]),
    }
    secure_pd.notify_event(event)
    assert cp.get_event(secure_pd.address) == event

def test_event_cardread_ascii():
    event = {
        'event': Event.CardRead,
        'reader_no': 1,
        'direction': 1,
        'format': CardFormat.ASCII,
        'data': bytes([9,1,9,2,6,3,1,7,7,0]),
    }
    secure_pd.notify_event(event)
    assert cp.get_event(secure_pd.address) == event

def test_event_cardread_wiegand():
    event = {
        'event': Event.CardRead,
        'reader_no': 1,
        'direction': 0, # has to be zero
        'length': 16,
        'format': CardFormat.Wiegand,
        'data': bytes([0x55, 0xAA]),
    }
    secure_pd.notify_event(event)
    raw = cp.get_event(secure_pd.address)
    print(raw)
    print(event)
    assert raw == event
