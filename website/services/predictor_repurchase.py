import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

from ..controllers.order_controller import obtener_historial_cliente

from ..models.customer_model import Customer

warnings.filterwarnings("ignore")


class RecompraPredictor:
    def predecir_recompra_cliente(self, historial_compras, meses_prediccion=4):
        """
        Predice probabilidad de recompra usando SARIMA
        historial_compras: DataFrame con columns ['fecha', 'monto']
        """
        try:
            # Preparar datos como serie temporal
            historial_compras["fecha"] = pd.to_datetime(historial_compras["fecha"])
            serie_temporal = (
                historial_compras.set_index("fecha")["monto"].resample("M").count()
            )

            if len(serie_temporal) < 6:
                return self._prediccion_simple(historial_compras, meses_prediccion)

            modelo = SARIMAX(
                serie_temporal,
                order=(1, 1, 1),  # (p,d,q)
                seasonal_order=(1, 1, 1, 12),
            )
            modelo_ajustado = modelo.fit(disp=False)

            prediccion = modelo_ajustado.forecast(steps=meses_prediccion)

            prob_recompra = self._calcular_probabilidad(prediccion, serie_temporal)

            return {
                "probabilidad_recompra": round(prob_recompra * 100, 2),
                "prediccion_meses": list(prediccion),
                "metodo": "SARIMA",
                "confiabilidad": "ALTA" if len(serie_temporal) >= 12 else "MEDIA",
            }

        except Exception as e:
            print(f"Error al precir recompra: {e}")
            return self._prediccion_simple(historial_compras, meses_prediccion)

    def _calcular_probabilidad(self, prediccion):
        """Calcula probabilidad basada en las predicciones"""

        compras_predichas = sum(prediccion > 0)
        probabilidad = compras_predichas / len(prediccion)
        return min(probabilidad, 0.95)

    def _prediccion_simple(self, historial_compras, meses_prediccion):
        """Método simple cuando no hay suficientes datos para SARIMA"""
        if len(historial_compras) == 0:
            return {
                "probabilidad_recompra": 10.0,
                "metodo": "SIMPLE",
                "confiabilidad": "BAJA",
            }

        frec_promedio = len(historial_compras) / 3  # 3 meses
        prob = min(frec_promedio / meses_prediccion, 0.8)

        return {
            "probabilidad_recompra": round(prob * 100, 2),
            "metodo": "SIMPLE",
            "confiabilidad": "BAJA",
        }

    def recompra_promedio_global(self, meses_prediccion):
        """Calcula recompra promedio de todos los clientes activos"""
        clientes_activos = Customer.query.filter_by(active=True).all()
        probabilidades = []

        for cliente in clientes_activos:
            historial = obtener_historial_cliente(cliente.id)
            prediccion = self.predecir_recompra_cliente(historial, meses_prediccion)
            probabilidades.append(prediccion["probabilidad_recompra"])

        return {
            "recompra_promedio": round(np.mean(probabilidades), 2),
            "desviacion_estandar": round(np.std(probabilidades), 2),
            "total_clientes_analizados": len(probabilidades),
            "horizonte_prediccion": f"{meses_prediccion} meses",
        }
