from .ai_bridge import ContextAIBridge

bridge = ContextAIBridge()

text = bridge.build({
    "screen": "home",
    "app": "JARVIS",
    "battery": 82,
    "network": "wifi",
    "orientation": "portrait",
    "locale": "hi-IN"
})

assert "battery: 82" in text
assert "network: wifi" in text
assert "locale: hi-IN" in text

print("SUCCESS")
