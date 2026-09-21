"""
Módulo de Validación Local de Andrea (Data Engineering).
Aplica la validación en dos capas:
1. Ingestión del sobre crudo con IngestionPayload.
2. Validación registro por registro con ValidatedInteractionItem.
3. Aislamiento de registros inválidos en auditoría sin tumbar el lote.
"""

from typing import Dict, List, Tuple
from esquemas import IngestionPayload, RawInteractionItem, ValidatedInteractionItem


def validar_lote_crudo(payload: IngestionPayload) -> Tuple[List[ValidatedInteractionItem], List[Dict]]:
    """
    Recibe un IngestionPayload, valida cada interacción y separa:
    - validos: List[ValidatedInteractionItem] (pasan a los agentes de IA)
    - rechazados: List[Dict] (aislados en auditoría con su motivo de fallo)
    """
    validos: List[ValidatedInteractionItem] = []
    rechazados: List[Dict] = []

    for raw_item in payload.interacciones:
        try:
            # Validar con el esquema estricto (exige texto no vacío)
            validated = ValidatedInteractionItem(
                id=raw_item.id,
                autor=raw_item.autor,
                canal=raw_item.canal,
                tipo=raw_item.tipo,
                texto=raw_item.texto or "",
                metadata_origen=raw_item.metadata_origen,
            )
            validos.append(validated)
        except Exception as e:
            # Aislar el registro defectuoso en auditoría
            rechazados.append({
                "id": raw_item.id,
                "autor": raw_item.autor,
                "canal": raw_item.canal,
                "error": str(e),
                "texto_crudo": raw_item.texto,
                "metadata_origen": raw_item.metadata_origen.model_dump(),
            })

    return validos, rechazados
