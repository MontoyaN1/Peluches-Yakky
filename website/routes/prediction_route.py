from flask import jsonify, Response
from ..models.producto_model import Product
from ..services.predictor_rotation import RotacionPredictor
from ..services.predictor_repurchase import RecompraPredictor
from ..decorators import login_required
from flask import Blueprint, request
import json

prediction_bp = Blueprint("prediccion", __name__)


@prediction_bp.route("/productos/rotacion", methods=["GET"])
@login_required
def ranking_rotacion():
    meses = request.args.get("meses", default=3, type=int)

    productos_activos = Product.query.all()
    predictor = RotacionPredictor()
    ranking = predictor.ranking_rotacion_productos(
        lista_productos=productos_activos, meses_prediccion=meses
    )

    json_str = json.dumps(ranking[:10], ensure_ascii=False)
    return Response(json_str, mimetype="application/json; charset=utf-8")


@prediction_bp.route("/clientes/recompra", methods=["GET"])
@login_required
def recompra_promedio():
    meses = request.args.get("meses", default=3, type=int)

    analytics = RecompraPredictor()
    resultado = analytics.recompra_promedio_global(meses_prediccion=meses)

    return jsonify(resultado)
