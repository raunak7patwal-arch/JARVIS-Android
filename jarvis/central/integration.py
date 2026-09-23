from jarvis.central.memory.advanced import AdvancedMemory
from jarvis.central.devices.registry import DeviceRegistry
from jarvis.central.devices.bridge import DeviceBridge
from jarvis.central.security.auth import DeviceAuth


class JarvisIntegration:

    def __init__(self):
        self.memory = AdvancedMemory()
        self.devices = DeviceRegistry()
        self.bridge = DeviceBridge()
        self.auth = DeviceAuth()

    def remember(
        self,
        text,
        category="general",
        importance=1
    ):
        return self.memory.add(
            text,
            category,
            importance
        )

    def recall(
        self,
        query,
        limit=5
    ):
        return self.memory.search(
            query,
            limit
        )

    def recent_memory(
        self,
        limit=10
    ):
        return self.memory.recent(limit)

    def register_device(
        self,
        device_id,
        name="Android",
        platform="android"
    ):
        self.devices.register(
            device_id,
            name,
            platform
        )

        return self.devices.get(
            device_id
        )

    def heartbeat(
        self,
        device_id
    ):
        self.devices.heartbeat(
            device_id
        )

        return self.devices.get(
            device_id
        )

    def create_device_command(
        self,
        device_id,
        action,
        parameters=None
    ):
        return self.bridge.create_command(
            device_id,
            action,
            parameters
        )

    def complete_device_command(
        self,
        command_id,
        result
    ):
        return self.bridge.complete(
            command_id,
            result
        )

    def fail_device_command(
        self,
        command_id,
        error
    ):
        return self.bridge.fail(
            command_id,
            error
        )

    def device_command(
        self,
        device_id,
        action,
        parameters=None
    ):
        return self.create_device_command(
            device_id,
            action,
            parameters
        )


integration = JarvisIntegration()
