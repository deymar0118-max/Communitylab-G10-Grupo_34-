# CommunityLab — Equipo 34 (Hackathon ONE G10 / NoCountry)
> **Motor Inteligente de Transformación y Distribución para Comunidades Digitales**

Solución automatizada orientada a comunidades de aprendizaje, ecosistemas de desarrolladores y empresas SaaS para ingerir actividad orgánica (Discord, Slack, GitHub, Foros) y transformarla sistemáticamente en activos de marketing estructurados y persistidos en **Oracle Cloud Infrastructure (OCI Always Free)**.

---

## 🏗️ Arquitectura y Recorrido de Integración

```
[n8n / Webhook / Carga Manual]
            │
            ▼
┌───────────────────────────────┐
│     FastAPI Ingestion API     │ ──> Guarda atómicamente en `data/raw/`
└───────────────────────────────┘
            │
            ▼
┌───────────────────────────────┐
│      Validador Local          │ ──> Aplica `ValidatedInteractionItem`
└───────────────┬───────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌───────────────┐ ┌──────────────────────────┐
│   3 Válidos   │ │ 1 Rechazado (Sin Texto)  │
│  Agentes LLM  │ │  Tabla Auditoría Local   │
└───────┬───────┘ └──────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│     Generación de Activos     │ ──> LinkedIn + Resumen Semanal (`source_ids`)
└───────────────┬───────────────┘
                │
        ┌───────┴────────────────────────┐
        ▼                                ▼
┌───────────────────────────────┐ ┌─────────────────────────────────┐
│  Borrador `revision-001.json` │ │    Panel Streamlit (Curaduría)   │
│   OCI Object Storage (Sync)   │ │  Aprobación -> `revision-002`   │
└───────────────────────────────┘ └─────────────────────────────────┘
```

---

## 📋 Evidencias Técnicas: Primera Prueba de Integración

### 1. Dataset de Prueba Sintético (`data/raw/lote_prueba_01.json`)
Contiene los 4 escenarios canónicos exigidos por la arquitectura:
- **`msg_001` (Logro / Testimonio)**: Éxito de despliegue en OCI (`Usuario_Alfa`).
- **`msg_002` (Logro / Avance)**: Completitud de esquemas Pydantic (`Usuario_Beta`).
- **`msg_003` (Duda técnica)**: Consulta de configuración de webhook en n8n (`Usuario_Gamma`).
- **`msg_004` (Inválido)**: Registro con `texto: ""` para comprobar el aislamiento de fallos (`Usuario_Delta`).

### 2. Resultados de Ejecución de la Suite de Pruebas
Comando ejecutado:
```bash
python tests/test_primera_prueba.py
```

**Salida de consola obtenida:**
```text
Ejecutando suite de pruebas de integración (Equipo 34)...
  [OK] Criterio 1 - Transporte y Validación: 4 recibidos -> 3 válidos, 1 rechazado aislado (msg_004).
  [OK] Criterio 2 - Contrato DistributionPackage: Tipado, trazabilidad source_ids y OCI verificados.

>>> RESULTADO: Todas las pruebas técnicas han sido superadas exitosamente.
```

### 3. Criterios de Aceptación Verificados

| Criterio | Resultado Esperado | Estado |
| :--- | :--- | :---: |
| **Transporte y Validación** | 4 recibidos, 3 válidos a IA, 1 rechazado (`msg_004`) aislado en auditoría sin tumbar el lote | ✅ Superado |
| **Trazabilidad estricta** | Activos generados enlazan a `source_ids` sin inventar hechos | ✅ Superado |
| **Contrato Canónico** | Estructura 100% compatible con `DistributionPackage` y `OCIStorageEvidence` | ✅ Superado |

---

## 🚀 Guía de Instalación y Ejecución Local

1. **Clonar el repositorio y entrar al directorio:**
   ```bash
   git clone https://github.com/deymar0118-max/Communitylab-G10-Grupo_34-.git
   cd Communitylab-G10-Grupo_34-
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Completar credenciales de OCI y LLM en .env
   ```

5. **Ejecutar la suite de pruebas de integración:**
   ```bash
   python tests/test_primera_prueba.py
   ```
