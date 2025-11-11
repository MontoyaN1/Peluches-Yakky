import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

from website.models.producto_model import Product

from ..controllers.order_controller import obtener_ventas_producto

warnings.filterwarnings("ignore")


class RotacionPredictor:
    def predecir_rotacion_producto(self, ventas_producto, meses_prediccion):
        """
        Predice rotación de producto usando SARIMA
        ventas_producto: DataFrame con columns ['fecha', 'cantidad']
        """
        try:
            # Preparar serie temporal mensual
            ventas_producto["fecha"] = pd.to_datetime(ventas_producto["fecha"])
            serie_ventas = (
                ventas_producto.set_index("fecha")["cantidad"].resample("M").sum()
            )

            if len(serie_ventas) < 6:
                return self._rotacion_simple(ventas_producto, meses_prediccion)

            # Modelo SARIMA para productos
            modelo = SARIMAX(
                serie_ventas, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)
            )
            modelo_ajustado = modelo.fit(disp=False)

            # Predecir ventas futuras
            prediccion_ventas = modelo_ajustado.forecast(steps=meses_prediccion)

            return {
                "rotacion_proyectada": int(sum(prediccion_ventas)),
                "ventas_mensuales_predichas": [int(x) for x in prediccion_ventas],
                "tendencia": "CRECIENTE"
                if prediccion_ventas.iloc[-1] > prediccion_ventas.iloc[0]
                else "ESTABLE",
                "metodo": "SARIMA",
            }

        except Exception as e:
            print(f"Error al predecir rotacion: {e}")
            return self._rotacion_simple(ventas_producto, meses_prediccion)

    def _rotacion_simple(self, ventas_producto, meses_prediccion):
        """Método simple para rotación"""
        if len(ventas_producto) == 0:
            return {
                "rotacion_proyectada": 0,
                "metodo": "SIMPLE",
                "tendencia": "ESTABLE",
            }

        ventas_promedio = ventas_producto["cantidad"].mean()
        rotacion_proyectada = int(ventas_promedio * meses_prediccion)

        return {
            "rotacion_proyectada": rotacion_proyectada,
            "metodo": "SIMPLE",
            "tendencia": "ESTABLE",
        }

    def ranking_rotacion_productos(self, lista_productos, meses_prediccion=4):
        """Obtiene ranking de productos por rotación proyectada"""
        resultados = []
        producto: Product

        for producto in lista_productos:
            producto_id = producto.id
            ventas = obtener_ventas_producto(producto_id)
            prediccion = self.predecir_rotacion_producto(ventas, meses_prediccion)

            resultados.append(
                {
                    "producto_id": producto_id,
                    "nombre_producto": producto.product_name,
                    "rotacion_proyectada": prediccion["rotacion_proyectada"],
                    "tendencia": prediccion["tendencia"],
                }
            )

        # Ordenar por rotación descendente
        return sorted(resultados, key=lambda x: x["rotacion_proyectada"], reverse=True)
