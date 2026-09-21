"""
Esquemas canónicos de Pydantic para CommunityLab (Equipo 34).
Implementa los tres contratos armonizados de la arquitectura:
1. Ingesta y Validación (Admisión permisiva y Validación estricta por registro).
2. Análisis Cognitivo (Clasificación, Sentimiento y Puntuación de Relevancia).
3. Distribución, Curaduría y Persistencia OCI.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# =====================================================================
# CONTRATO 1: INGESTA, ADMISIÓN Y VALIDACIÓN LOCAL
# =====================================================================

class RawMetadataOrigen(BaseModel):
    plataforma: str = Field(
        ..., description="Plataforma de origen: Discord, Slack, GitHub, Form, etc."
    )
    identificador_original: str = Field(
        ..., description="ID nativo del mensaje en la plataforma de origen"
    )
    fecha: str = Field(..., description="Timestamp ISO-8601 del mensaje original")


class RawInteractionItem(BaseModel):
    """Esquema permisivo a nivel de registro para admitir lotes crudos sin bloquear peticiones."""
    id: str = Field(
        ..., description="Identificador único y estable del mensaje en el sistema"
    )
    autor: str = Field(
        default="Anónimo", description="Nombre o alias del miembro de la comunidad"
    )
    canal: str = Field(
        ..., description="Canal, foro o fuente (#logros, #dudas, issues, general)"
    )
    tipo: str = Field(
        default="sin_clasificar", description="Tipo declarado o 'sin_clasificar'"
    )
    texto: Optional[str] = Field(
        default="",
        description="Contenido textual crudo (puede venir vacío en pruebas de fallo o auditoría)",
    )
    metadata_origen: RawMetadataOrigen


class IngestionPayload(BaseModel):
    """Contrato del sobre de entrada recibido por la API o cargado manualmente."""
    schema_version: str = Field(
        default="1.1.0", description="Versión del esquema de transporte"
    )
    request_id: str = Field(
        ..., description="Identificador de la solicitud provisto por el emisor"
    )
    origen_comunidad: str = Field(
        ..., description="Comunidad o espacio digital de procedencia"
    )
    periodo_referencia: str = Field(
        ..., description="Identificador del ciclo o semana (ej. 2026-Semana-38)"
    )
    interacciones: List[RawInteractionItem] = Field(
        ..., min_length=1, description="Lista utilizable de interacciones"
    )


class ValidatedInteractionItem(BaseModel):
    """Modelo aplicado por la capa local de datos antes de enviar registros a los agentes."""
    id: str
    autor: str
    canal: str
    tipo: str
    texto: str = Field(
        ..., min_length=1, description="Texto no vacío exigido para análisis"
    )
    metadata_origen: RawMetadataOrigen

    @field_validator("texto")
    @classmethod
    def validar_texto_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El texto de la interacción no puede estar vacío ni contener solo espacios")
        return v.strip()


# =====================================================================
# CONTRATO 2: ANÁLISIS COGNITIVO (CognitiveAnalysis)
# =====================================================================

class RelevanceScore(BaseModel):
    evidencia_explicita: int = Field(
        ..., ge=0, le=2, description="Datos y hechos verificables en el texto (0 a 2)"
    )
    utilidad_comunitaria: int = Field(
        ..., ge=0, le=2, description="Valor formativo, técnico o motivacional (0 a 2)"
    )
    claridad_contexto: int = Field(
        ..., ge=0, le=2, description="Claridad temática y suficiencia contextual (0 a 2)"
    )
    total: int = Field(
        ..., ge=0, le=6, description="Puntuación total consolidada (0 a 6)"
    )


class AnalyzedMessage(BaseModel):
    source_id: str = Field(..., description="Referencia exacta al id del mensaje original")
    sentimiento: Literal[
        "Altamente Positivo", "Positivo", "Neutro", "Dificultad/Negativo"
    ]
    categoria_enrutamiento: Literal["Logro", "Duda", "Dificultad"] = Field(
        ..., description="Categoría asignada que orienta el enfoque editorial"
    )
    regla_aplicada: str = Field(
        ..., description="Criterio documentado para derivar el contenido"
    )
    temas: List[str] = Field(..., min_length=1)
    entidades_relevantes: List[str] = Field(default_factory=list)
    puntuacion_relevancia: RelevanceScore
    motivo_seleccion: str = Field(
        ..., min_length=10, description="Justificación objetiva de la puntuación"
    )
    requiere_soporte: bool = Field(
        default=False, description="Marca casos que requieren canalización o mentoría"
    )
    apto_para_publicacion: bool = Field(
        ..., description="Determina si el mensaje califica para difusión pública"
    )


class CommunitySummary(BaseModel):
    total_interacciones_procesadas: int = Field(..., ge=1)
    registros_validos: int = Field(..., ge=1)
    registros_rechazados: int = Field(default=0, ge=0)
    sentimiento_predominante: str = Field(
        ..., description="Polaridad dominante o 'Mixto'"
    )
    distribucion_sentimiento: Dict[str, int]
    temas_principales: List[str] = Field(..., min_length=1)
    alertas_soporte: List[str] = Field(default_factory=list)


class CognitiveAnalysis(BaseModel):
    run_id: str = Field(..., description="ID de ejecución asignado internamente")
    request_id: str = Field(..., description="ID de la solicitud original")
    resumen_comunidad: CommunitySummary
    mensajes_analizados: List[AnalyzedMessage] = Field(..., min_length=1)


# =====================================================================
# CONTRATO 3: DISTRIBUCIÓN, CURADURÍA Y PERSISTENCIA OCI
# =====================================================================

class ExecutionMetadata(BaseModel):
    modelo: str = Field(..., description="Identificador exacto del LLM")
    prompt_version: str = Field(..., description="Versión del prompt utilizado")
    latencia_ms: int = Field(..., ge=0)
    tokens_totales: int = Field(..., ge=0)


class LinkedInAsset(BaseModel):
    titulo: str = Field(..., min_length=5)
    canal_recomendado: str = Field(default="LinkedIn Oficial")
    cuerpo: str = Field(..., min_length=20)
    hashtags: List[str] = Field(default_factory=list)
    source_ids: List[str] = Field(
        ..., min_length=1, description="IDs de mensajes que respaldan la publicación"
    )


class WeeklySummaryAsset(BaseModel):
    seccion: str = Field(..., description="Sección del resumen o boletín")
    titular: str = Field(..., min_length=5)
    resumen: str = Field(..., min_length=20)
    source_ids: List[str] = Field(
        ..., min_length=1, description="IDs de mensajes que respaldan la síntesis"
    )


class GeneratedAssets(BaseModel):
    post_linkedin: LinkedInAsset
    resumen_semanal: WeeklySummaryAsset


class HumanReviewControl(BaseModel):
    numero_revision: int = Field(
        default=1, ge=1, description="Secuencia incremental de versión"
    )
    estado_decision: Literal["pendiente", "aprobado", "rechazado"] = "pendiente"
    revisor: Optional[str] = Field(
        default=None, description="Alias o identificador del curador humano"
    )
    fecha_decision: Optional[datetime] = None
    comentarios: Optional[str] = None


class OCIStorageEvidence(BaseModel):
    bucket: str = Field(default="communitylab-activos-marketing")
    ruta_objeto: str = Field(
        ..., description="Ruta inmutable: activos/{periodo}/{run_id}/revision-{num}.json"
    )
    status_almacenamiento: Literal[
        "guardado_con_exito", "guardado_error", "no_iniciado"
    ] = "no_iniciado"
    comprobacion_lectura: bool = Field(
        default=False,
        description="True solo si la aplicación recuperó y verificó el objeto en OCI",
    )


def default_fecha_generacion() -> datetime:
    return datetime.now(timezone.utc)


class DistributionPackage(BaseModel):
    schema_version: str = Field(default="1.1.0")
    run_id: str = Field(...)
    request_id: str = Field(...)
    fecha_generacion: datetime = Field(default_factory=default_fecha_generacion)
    metadatos_ejecucion: ExecutionMetadata
    analisis_resumido: CommunitySummary
    activos_distribucion: GeneratedAssets
    control_revision_humana: HumanReviewControl = Field(
        default_factory=HumanReviewControl
    )
    almacenamiento_oci: OCIStorageEvidence