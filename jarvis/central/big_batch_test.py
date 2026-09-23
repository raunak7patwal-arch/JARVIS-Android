from jarvis.central.smarthome.manager import (
    SmartHomeManager
)
from jarvis.central.smarthome.rules import (
    SmartHomeRule,
    SmartHomeRules,
)
from jarvis.central.automation.engine import (
    AutomationEngine
)
from jarvis.central.security.hardening import (
    SecurityHardening
)
from jarvis.central.security.command_guard import (
    CommandGuard
)


home = SmartHomeManager()

assert home.register(
    "light-1",
    "Bedroom Light",
    "light",
    "bedroom"
)

assert home.register(
    "fan-1",
    "Bedroom Fan",
    "fan",
    "bedroom"
)

assert not home.register(
    "bad-1",
    "Unknown",
    "unknown"
)

assert home.set_state(
    "light-1",
    "turn_on"
)

assert home.get(
    "light-1"
)["state"] == "on"

assert home.set_state(
    "light-1",
    "set_level",
    60
)

assert home.get(
    "light-1"
)["level"] == 60

assert not home.set_state(
    "light-1",
    "set_level",
    150
)


rules = SmartHomeRules()

rules.add(
    SmartHomeRule(
        "rule-1",
        "Night light",
        {
            "time": "night"
        },
        {
            "device_id": "light-1",
            "action": "turn_on",
        }
    )
)

results = rules.evaluate(
    {"time": "night"},
    home
)

assert results
assert results[0]["executed"]
assert home.get(
    "light-1"
)["state"] == "on"


engine = AutomationEngine()

assert engine.add(
    "job-1",
    "Test automation",
    "smart_home",
    {
        "device_id": "light-1",
        "action": "turn_off",
    }
)

assert engine.get(
    "job-1"
)["enabled"]

assert engine.disable("job-1")
assert not engine.get(
    "job-1"
)["enabled"]

assert engine.enable("job-1")
assert engine.mark_run("job-1")

assert engine.remove("job-1")


security = SecurityHardening()

for _ in range(30):
    assert security.allow_request(
        "test-device"
    )

assert not security.allow_request(
    "test-device"
)

security.clear()

assert security.constant_time_equal(
    "abc",
    "abc"
)

assert not security.constant_time_equal(
    "abc",
    "xyz"
)

assert CommandGuard.validate(
    "test-device",
    "ping",
    {}
)[0]

assert not CommandGuard.validate(
    "test-device",
    "shell",
    {}
)[0]

assert CommandGuard.require_confirmation(
    "open_app"
)

print("SUCCESS")
