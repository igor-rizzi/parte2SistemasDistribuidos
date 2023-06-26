from flask import json
from datetime import datetime
from bson import Decimal128



def custom_serializer(obj):
    if isinstance(obj, Decimal128):
        return str(obj.to_decimal())
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def custom_jsonify(obj):
    from main import app  # Movido para dentro da função
    return app.response_class(
        json.dumps(obj, default=custom_serializer),
        mimetype="application/json"
    )
