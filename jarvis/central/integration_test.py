from jarvis.central.memory.context import MemoryContext
from jarvis.central.ai.memory_bridge import MemoryBridge
from jarvis.central.devices.registry import DeviceRegistry
from jarvis.central.devices.bridge import DeviceBridge
from jarvis.central.security.policy import SecurityPolicy


memory = MemoryContext()

memory.memory.clear()

assert memory.remember(
    "User prefers concise Hindi responses",
    "preference",
    5
)

context = memory.build(
    "Hindi responses"
)

assert context
assert "concise Hindi" in context


bridge = MemoryBridge(memory)

answer = bridge.handle(
    "remember My favorite assistant is JARVIS"
)

assert answer is not None
assert "याद" in answer


recent = memory.memory.recent(10)

assert recent

texts = [
    str(item.get("text", ""))
    for item in recent
]

assert any(
    "JARVIS" in text
    for text in texts
)


registry = DeviceRegistry()

registry.register(
    "android-001",
    "JARVIS Android",
    "android"
)

registry.heartbeat(
    "android-001"
)

device = registry.get(
    "android-001"
)

assert device is not None
assert device["online"] is True


device_bridge = DeviceBridge()

command = device_bridge.create_command(
    "android-001",
    "device_info",
    {}
)

assert command["status"] == "pending"

assert device_bridge.complete(
    command["id"],
    {"manufacturer": "test"}
)

completed = device_bridge.get(
    command["id"]
)

assert completed["status"] == "completed"


assert SecurityPolicy.allowed(
    "device_info"
)

assert SecurityPolicy.allowed(
    "open_app"
)

assert SecurityPolicy.allowed(
    "open_url"
)

assert not SecurityPolicy.allowed(
    "shell"
)

assert not SecurityPolicy.allowed(
    "su"
)

memory.memory.clear()

print("SUCCESS")
