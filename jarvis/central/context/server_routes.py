from flask import Blueprint, jsonify, request

from jarvis.central.context.api import context_api


context_blueprint = Blueprint(
    "jarvis_context",
    __name__
)


@context_blueprint.post("/context/update")
def update_context():
    data = request.get_json(
        silent=True
    ) or {}

    device_id = str(
        data.get(
            "device_id",
            ""
        )
    ).strip()

    context = data.get(
        "context",
        {}
    )

    if not device_id:
        return jsonify({
            "ok": False,
            "error": "device_id required"
        }), 400

    result = context_api.update(
        device_id,
        context
    )

    return jsonify(result)


@context_blueprint.get("/context/latest")
def latest_context():
    device_id = request.args.get(
        "device_id"
    )

    result = context_api.latest(
        device_id
    )

    return jsonify(result)
