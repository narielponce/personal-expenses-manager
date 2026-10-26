import json
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

def _get_available_models():
    """Devuelve modelos disponibles priorizando gemini-1.5-flash-latest según GEMINI.md."""
    try:
        if not settings.GEMINI_API_KEY:
            return []
        genai.configure(api_key=settings.GEMINI_API_KEY)
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        pref_order = ['flash-latest', '1.5-flash', 'pro-latest', '1.5-pro', '2.0-flash']
        sorted_models = []
        for pref in pref_order:
            for m in available:
                if pref in m and m not in sorted_models:
                    sorted_models.append(m)
        for m in available:
            if m not in sorted_models:
                sorted_models.append(m)
        return sorted_models
    except Exception as e:
        logger.warning(f"Error listando modelos Gemini: {e}")
        return ['models/gemini-1.5-flash-latest', 'models/gemini-1.5-flash']


def _call_gemini_json(prompt: str) -> Optional[Dict[str, Any]]:
    """Ejecuta una consulta a Gemini con fallback automático entre modelos y parsea JSON."""
    if not settings.GEMINI_API_KEY:
        return None

    models_to_try = _get_available_models()
    for model_name in models_to_try:
        if any(x in model_name for x in ['2.5', '3.0', '3.1']):
            continue
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text_response = response.text or ""
            
            # Buscar el bloque JSON en la respuesta
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                return json.loads(text_response[json_start:json_end])
        except Exception as e:
            logger.warning(f"Gemini {model_name} falló: {e}")
            if "429" not in str(e) and "404" not in str(e):
                break
    return None


def generate_financial_diagnosis(projection: Dict[str, Any], burn_rate: Dict[str, Any], recurrents: list) -> Dict[str, Any]:
    """
    Genera un diagnóstico financiero estructurado con IA evaluando la proyección y gastos.
    Devuelve 3 bloques: Diagnóstico actual, Alertas críticas, 3 Recomendaciones accionables.
    """
    top_cats_str = ", ".join([f"{c['category_name']}: ${c['total']}" for c in burn_rate.get("top_categories", [])]) or "Sin datos aún"
    
    prompt = f"""
Actúa como un asesor financiero personal analítico, prudente, empático y experto.
Analiza la siguiente situación financiera mensual de un usuario:

DATOS DEL MES ACTUAL:
- Gasto acumulado a la fecha: ${projection.get('total_spent_so_far', 0)}
- Días transcurridos: {projection.get('days_elapsed', 0)} de {projection.get('days_in_month', 30)} ({projection.get('time_progress_pct', 0)}% del mes)
- Gasto fijo/recurrente: ${projection.get('fixed_recurring_spent', 0)}
- Gasto variable acumulado: ${projection.get('variable_spent_so_far', 0)}
- Ritmo diario variable: ${projection.get('daily_variable_rate', 0)}/día
- Proyección estimada a fin de mes: ${projection.get('projected_month_end', 0)}
- Ingresos registrados: ${projection.get('total_income', 0)}
- Balance proyectado a fin de mes: ${projection.get('projected_balance', 'No definido')}
- Top categorías de gasto: {top_cats_str}
- Candidatos a gastos recurrentes detectados: {len(recurrents)}

Responde OBLIGATORIAMENTE en formato JSON con la siguiente estructura exacta:
{{
  "diagnosis": "Diagnóstico conciso del estado financiero actual y si la proyección es saludable o requiere atención (máximo 3 oraciones).",
  "alerts": [
    "Alerta 1 sobre desvíos, categorías con ritmo acelerado o gastos hormiga.",
    "Alerta 2 (si aplica, o mención sobre ritmo diario)."
  ],
  "recommendations": [
    "Recomendación accionable 1 específica para lo que queda del mes.",
    "Recomendación accionable 2 sobre presupuesto o ahorro.",
    "Recomendación accionable 3 de hábitos financieros."
  ],
  "status_color": "verde" | "amarillo" | "rojo"
}}
No incluyas texto fuera del bloque JSON.
"""
    result = _call_gemini_json(prompt)
    if result and isinstance(result, dict) and "diagnosis" in result:
        return result

    # Fallback determinístico inteligente si no hay API key o hubo error de cuota
    proj = projection.get("projected_month_end", 0)
    income = projection.get("total_income", 0)
    if income > 0 and proj > income:
        status_color = "rojo"
        diag = f"Tu proyección de gastos (${proj:,.2f}) supera tus ingresos registrados (${income:,.2f}). Es prioritario moderar gastos variables."
        alerta = "El ritmo de gasto diario actual generará un déficit antes de fin de mes."
    elif income > 0 and proj > (income * 0.85):
        status_color = "amarillo"
        diag = f"Tu proyección mensual (${proj:,.2f}) está consumiendo más del 85% de tus ingresos. Margen de ahorro muy ajustado."
        alerta = "Mantén vigiladas las categorías principales para no entrar en zona de riesgo."
    else:
        status_color = "verde"
        diag = f"Tu ritmo de gasto diario está dentro de parámetros sostenibles con una proyección de ${proj:,.2f} para fin de mes."
        alerta = "No se detectaron alertas críticas de desvío presupuestario."

    return {
        "diagnosis": diag,
        "alerts": [alerta],
        "recommendations": [
            "Revisa tus gastos variables diarios para mantener el ritmo por debajo del promedio proyectado.",
            "Separa un porcentaje fijo para ahorro o fondo de emergencia a principios de mes.",
            "Asigna presupuestos mensuales a tus categorías con mayor volumen de gasto."
        ],
        "status_color": status_color,
        "is_fallback": True
    }


def simulate_purchase_impact(projection: Dict[str, Any], purchase_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simula el impacto financiero de una compra en cuotas antes de realizarla.
    Devuelve un veredicto (Verde, Amarillo, Rojo), cuota mensual y análisis de impacto en flujo de caja.
    """
    amount = float(purchase_data.get("amount", 0.0))
    installments = max(1, int(purchase_data.get("installments", 1)))
    description = purchase_data.get("description", "Compra planeada")
    category = purchase_data.get("category_name", "General")
    
    installment_val = round(amount / installments, 2)
    current_proj = projection.get("projected_month_end", 0.0)
    income = projection.get("total_income", 0.0)
    
    new_projected = current_proj + (installment_val if installments > 1 else amount)
    
    prompt = f"""
Actúa como un asesor financiero que ayuda a evaluar una compra planeada.
DATOS DE LA COMPRA:
- Artículo: {description}
- Monto total: ${amount}
- Cantidad de cuotas: {installments}
- Valor de cada cuota mensual: ${installment_val}
- Categoría: {category}

CONTEXTO FINANCIERO DEL USUARIO:
- Gasto acumulado del mes: ${projection.get('total_spent_so_far', 0)}
- Proyección mensual actual sin la compra: ${current_proj}
- Nueva proyección con la primera cuota: ${new_projected}
- Ingresos mensuales: ${income}

Evalúa la viabilidad y responde OBLIGATORIAMENTE en JSON con:
{{
  "verdict": "Verde" | "Amarillo" | "Rojo",
  "verdict_title": "Título corto del dictamen (ej: 'Compra Viable', 'Riesgo Moderado', 'No Recomendada')",
  "monthly_installment": {installment_val},
  "total_amount": {amount},
  "installments": {installments},
  "impact_summary": "Explicación concisa (2-3 oraciones) de cómo afectará el flujo de caja en los próximos {installments} meses.",
  "actionable_tip": "Consejo específico para esta compra (ej: cantidad óptima de cuotas o esperar)."
}}
No incluyas texto fuera del bloque JSON.
"""
    result = _call_gemini_json(prompt)
    if result and isinstance(result, dict) and "verdict" in result:
        result["monthly_installment"] = installment_val
        result["total_amount"] = amount
        result["installments"] = installments
        return result

    # Fallback algorítmico determinístico
    if income > 0:
        ratio = (new_projected) / income
        if ratio > 1.0:
            verdict = "Rojo"
            title = "Alto Riesgo de Desbalance"
            summary = f"Esta compra llevaría tu proyección mensual a ${new_projected:,.2f}, superando tus ingresos registrados."
            tip = "Se recomienda posponer la compra o buscar una alternativa de menor valor."
        elif ratio > 0.85:
            verdict = "Amarillo"
            title = "Compra Ajustada (Precaución)"
            summary = f"Compromete ${installment_val:,.2f} al mes durante {installments} meses, reduciendo tu capacidad de ahorro."
            tip = "Si es indispensable, reduce gastos variables en otras categorías durante estos meses."
        else:
            verdict = "Verde"
            title = "Compra Viable"
            summary = f"La cuota de ${installment_val:,.2f} representa un porcentaje manejable de tus ingresos."
            tip = "Compra financieramente viable dentro de tu flujo de caja proyectado."
    else:
        verdict = "Verde" if installments <= 3 else "Amarillo"
        title = "Impacto Moderado"
        summary = f"Genera una obligación mensual fija de ${installment_val:,.2f} por los próximos {installments} meses."
        tip = "Verifica contar con saldo disponible para no acumular intereses."

    return {
        "verdict": verdict,
        "verdict_title": title,
        "monthly_installment": installment_val,
        "total_amount": amount,
        "installments": installments,
        "impact_summary": summary,
        "actionable_tip": tip,
        "is_fallback": True
    }
