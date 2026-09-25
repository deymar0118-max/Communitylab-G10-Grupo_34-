"""
Módulo de Validación Local de Andrea (Data Engineering).
Aplica la validación en dos capas:
1. Ingestión del sobre crudo con IngestionLote.
2. Validación registro por registro con InteraccionValidada.
3. Aislamiento de registros inválidos en auditoría sin tumbar el lote.
"""

from typing import Dict, List, Tuple
from esquemas import IngestionLote, InteraccionValidada, MetadataOrigenValidado


def validar_lote_crudo(payload: IngestionLote) -> Tuple[List[InteraccionValidada], List[Dict]]:
    """
    Recibe un IngestionLote, valida cada interacción y separa:
    - validos: List[InteraccionValidada] (pasan a los agentes de IA)
    - rechazados: List[Dict] (aislados en auditoría con su motivo de fallo)
    """
    validos: List[InteraccionValidada] = []
    rechazados: List[Dict] = []

    for raw_item in payload.interacciones:
        try:
            # Validar y parsear metadatos (fecha str -> datetime)
            meta_validada = MetadataOrigenValidado(
                plataforma=raw_item.metadata_origen.plataforma,
                identificador_original=raw_item.metadata_origen.identificador_original,
                fecha=raw_item.metadata_origen.fecha,
            )

            # Validar con el esquema estricto (exige texto no vacío)
            validated = InteraccionValidada(
                id=raw_item.id,
                autor=raw_item.autor,
                canal=raw_item.canal,
                tipo=raw_item.tipo,
                texto=raw_item.texto or "",
                metadata_origen=meta_validada,
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
