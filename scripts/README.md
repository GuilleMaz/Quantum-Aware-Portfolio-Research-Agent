# scripts/

Utilidades de mantenimiento del repo. Ninguna contiene lógica de negocio.

| Script | Qué hace | Cuándo se usa |
|---|---|---|
| `check_config.py` | Valida `config/mcp_servers.json` y los `config/clients/*.json` contra su esquema mínimo | Antes de cada commit que toque `config/` |
| `sync_uvx_path.py` | Detecta la ruta real de `uvx.exe` en esta máquina e imprime el bloque `command` listo para pegar | Al clonar el repo en una máquina nueva (Windows) |

Ver `TASKS.md` para el flujo de trabajo. Los scripts nunca importan de `src/`.
