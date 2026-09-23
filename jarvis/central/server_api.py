from flask import Blueprint, jsonify, request

from jarvis.central.api import device_api
from jarvis.central.security.request_guard import RequestGuard


device_blueprint = Blueprint(
    "jarvis_devices",
    __name__
)

guard = RequestGuard()


@device_blueprint.post("/device/register")
def register_device():
    data = request.get_json(
        silent=True
    ) or {}

    device_id = str(
        data.get(
            "device_id",
            ""
        )
    ).strip()

    name = str(
        data.get(
            "name",
            "Android"
        )
    ).strip()

    platform = str(
        data.get(
            "platform",
            "android"
        )
    ).strip()

    if not device_id:
        return jsonify({
            "ok": False,
            "error": "device_id required"
        }), 400

    result = device_api.register(
        device_id,
        name,
        platform
    )

    return jsonify({
        "ok": True,
        "device": result
    })


@device_blueprint.post("/device/heartbeat")
def heartbeat():
    data = request.get_json(
        silent=True
    ) or {}

    device_id = str(
        data.get(
            "device_id",
            ""
        )
    ).strip()

    if not device_id:
        return jsonify({
            "ok": False,
            "error": "device_id required"
        }), 400

    result = device_api.heartbeat(
        device_id
    )

    return jsonify({
        "ok": True,
        "device": result
    })


@device_blueprint.get("/device/list")
def device_list():
    return jsonify({
        "ok": True,
        "devices": device_api.list_devices()
    })


@device_blueprint.post("/device/command")
def create_command():
    data = request.get_json(
        silent=True
    ) or {}

    device_id = str(
        data.get(
            "device_id",
            ""
        )
    ).strip()

    action = str(
        data.get(
            "action",
            ""
        )
    ).strip()

    parameters = data.get(
        "parameters",
        {}
    )

    if not device_id:
        return jsonify({
            "ok": False,
            "error": "device_id required"
        }), 400

    if not action:
        return jsonify({
            "ok": False,
            "error": "action required"
        }), 400

    valid, message = guard.validate_parameters(
        parameters
    )

    if not valid:
        return jsonify({
            "ok": False,
            "error": message
        }), 400

    result = device_api.create_command(
        device_id,
        action,
        parameters
    )

    status = 200 if result["ok"] else 403

    return jsonify(result), status


@device_blueprint.post("/device/complete")
def complete_command():
    data = request.get_json(
        silent=True
    ) or {}

    command_id = str(
        data.get(
            "command_id",
            ""
        )
    ).strip()

    result = data.get(
        "result"
    )

    if not command_id:
        return jsonify({
            "ok": False,
            "error": "command_id required"
        }), 400

    return jsonify(
        device_api.complete(
            command_id,
            result
        )
    )


@device_blueprint.post("/device/fail")
def fail_command():
    data = request.get_json(
        silent=True
    ) or {}

    command_id = str(
        data.get(
            "command_id",
            ""
        )
    ).strip()

    error = str(
        data.get(
            "error",
            "Unknown error"
        )
    )

    if not command_id:
        return jsonify({
            "ok": False,
            "error": "command_id required"
        }), 400

    return jsonify(
        device_api.fail(
            command_id,
            error
        )
    )
