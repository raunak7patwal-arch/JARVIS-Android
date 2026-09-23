from jarvis.central.context.engine import context_engine
from jarvis.central.context.normalizer import ContextNormalizer


class ContextAPI:

    def update(
        self,
        device_id,
        context
    ):
        clean = ContextNormalizer.normalize(
            context
        )

        ok = context_engine.update(
            device_id,
            clean
        )

        return {
            "ok": ok,
            "device_id": device_id,
            "context": clean,
        }

    def latest(
        self,
        device_id=None
    ):
        result = context_engine.latest(
            device_id
        )

        return {
            "ok": result is not None,
            "context": result,
        }


context_api = ContextAPI()
