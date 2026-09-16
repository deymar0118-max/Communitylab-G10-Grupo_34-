from pydantic import BaseModel, Field
from typing import List, Optional

# Copntrato de Entrada
class Interaccion(BaseModel):
    id: str
    autor: str
    canal: str
    tipo: str = Field(default="sin_clasificar") # Si falta, asigna valor por defecto
    texto: str

class IngestionLote(BaseModel):
    origen_comunidad: str
    periodo_referencia: str
    interacciones: List[Interaccion]

# --- Contrado de Salida
class ActivosGenerados(BaseModel):
    post_linkedin: str
    resumen_semanal: str

class EstadoRevision(BaseModel):
    estado: str = "pendiente" # pendiente | aprobado | rechazado
    revisor: Optional[str] = None
    version_revision: str = "revision-001"

class PaqueteSalida(BaseModel):
    schema_version: str = "1.1"
    run_id: str
    fecha: str
    analisis_sentimiento: str
    activos: ActivosGenerados
    revision: EstadoRevision
    estado_almacenamiento_oci: str = "no_guardado"