from flask import Blueprint, request, jsonify, make_response
from backend.services.util_runner import run_system_command
from backend.services.config_loader import load_config_from_bytes, evaluate_expression

tools_bp = Blueprint("tools", __name__, url_prefix="/api/tools")


@tools_bp.route("/run", methods=["POST"])
def run():
    data = request.get_json() or {}
    cmd = data.get("cmd", "id")
    out = run_system_command(cmd)
    return jsonify({"output": out})


@tools_bp.route("/config/load", methods=["POST"])
def config_load():
    raw = request.get_data()
    try:
        obj = load_config_from_bytes(raw)
        return jsonify({"config": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@tools_bp.route("/eval", methods=["POST"])
def eval_route():
    data = request.get_json() or {}
    expr = data.get("expr", "1+1")
    try:
        result = evaluate_expression(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@tools_bp.route("/echo", methods=["GET"])
def echo():
    msg = request.args.get("msg", "")
    html = "<!DOCTYPE html><html><head><meta charset='utf-8'/><title>Echo</title></head><body><p>Message: " + msg + "</p></body></html>"
    return make_response(html, 200, {"Content-Type": "text/html; charset=utf-8"})
