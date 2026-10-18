# AGENTS.md — Contrato de trabajo

Este repo define **cómo debe trabajar cualquier agente de IA (o persona)** aquí.
Léelo completo antes de tocar nada.

---

## 1. Propósito

**Quantum-Aware Portfolio Research Agent** es un sistema multi-agente
orquestado que combina análisis financiero con simulación cuántica (QAOA) para
explorar estrategias de cartera.

**Qué significa "cuántico" aquí:** QAOA aplicado a problemas de optimización de
carteras (Ising/QUBO). **No** es criptografía post-cuántica, ni blockchain, ni
computación cuántica de detalle general.

**Qué NO es:** no produce consejo de inversión. Todo output es investigación y
educativo.

---

## 2. Stack y comandos exactos

Gestor único: **uv**. Entorno: **Python 3.12** (fijado en `.python-version`).

```powershell
uv sync                              # deps base
uv sync --extra quantum              # Qiskit + matplotlib
uv sync --extra notebooks            # motor MyST-NB
uv sync --extra data                 # yfinance, pandas, scipy
uv sync --extra dev                  # pytest, ruff, mypy

uv run pytest                        # tests
uv run pytest -m "not integration"   # tests sin servidores MCP externos
uv run ruff check .                  # lint
uv run ruff format .                 # format
uv run mypy src/                     # typecheck (solo src/)
```

Servidores MCP (comandos **verificados**, no de la documentación upstream):

```powershell
uvx --from financial-mcp-server --with "mcp<2" financial-mcp
uvx --from "mcp-qiskit[mcp]" mcp-qiskit
uvx --from mcp-memory-service memory server
```

---

## 3. Reglas inviolables

### 3.1 Separación `labs/` vs `src/`

- **`labs/`** = experiments. Cuaderno desechable. Puede estar feo, puede
  romperse, se congela al cerrar la fase.
- **`src/quantum_portfolio/`** = paquete real. Se importa, se testea, se
  promociona.

**El código se promueve de `labs/` a `src/` al cerrar cada fase**, ya limpio. No
se escribe directamente en `src/` durante el aprendizaje.

### 3.2 Nada de lógica MCP fuera de `mcp_clients/`

Toda llamada a un servidor MCP vive en `src/quantum_portfolio/mcp_clients/`.
Ni los agentes, ni los nodos del grafo, ni los labs (salvo experiments de la
Fase 1, que su raison d'être es tocar el protocolo crudo).

### 3.3 Nada hardcodeado

- **Tickers, pesos, umbrales de volatilidad y prompts de negocio** → `config/`.
- **Comandos de servidores MCP** → `config/mcp_servers.json`.
- **Rutas absolutas** → nunca en el código. En `config/clients/*.example.json`
  sí, porque son ejemplos de configuración por cliente y documentan la trampa
  de Windows.

### 3.4 Todo cambio en `src/` requiere test

Si tocas `src/`, `tests/` se toca con él. Sin excepción.

### 3.5 Secretos

- **`.env` nunca se commitea.** Está en `.gitignore` explícitamente.
- Solo `.env.example` con valores vacíos se versiona.
- Ninguna API key en `opencode.json`, ni en `config/`, ni en un notebook.

### 3.6 Honestidad científica

Este proyecto no demuestra ventaja cuántica en portfolios. Si escribes una
afirmación sobre rendimiento cuántico, debe ser verificable y citar fuente.
El principio de variación se respeta siempre: $\langle H_C\rangle \ge \lambda_0$
— si un resultado cuántico sale por debajo del óptimo exacto, hay un bug.

---

## 4. Proceso tras cada tarea

Al terminar **cada tarea** de [`TASKS.md`](TASKS.md):

1. Actualizar `project-memory/changelog.md` (nueva entrada al inicio).
2. Actualizar `project-memory/next-steps.md`.
3. Si hubo cambio de diseño → `project-memory/decisions.md`.
4. Si hubo cambio estructural → `project-memory/architecture.md`.
5. Marcar la tarea en `TASKS.md`.
6. **Un commit.** Ver §5.

---

## 5. Convención de commits

Una tarea de `TASKS.md` = un commit.

```
<tipo>(<ámbito>): <descripción en imperativo>

Tipos:  feat | fix | docs | refactor | test | chore | perf
Ámbitos: labs | theory | src | mcp | graph | quantum | config | docs
```

Ejemplos:

```
feat(mcp): cliente stdio con ClientSessionGroup para dos servidores
docs(theory): notebook qaoa.md.ipynb con Hamiltonian de coste y supervivencia
chore(deps): fix mcp<2 pin en config/mcp_servers.json
fix(quantum): circuit dict no reenviado en segundo add_gate
```

Al cerrar una **fase**:

```
docs(memory): cierra fase 1 y actualiza changelog, decisions y next-steps
```

---

## 6. Los servidores MCP disponibles

| Servidor | Para qué | Estado |
|---|---|---|
| `financial-mcp-server` | Precios, fundamentales, momentum, volatilidad, VIX, macro, paper trading (42 tools) | Alpha, 1 mantenedor. Datos reales vía yfinance |
| `mcp-qiskit` | Crear/aplicar compuertas y ejecutar circuitos en Aer (13 tools) | **Stateless** — hay que reenviar el dict del circuito |
| `mcp-memory-service` | Memoria persistente entre sesiones | Alternativa a `mem0-mcp-server` (archivado) |
| **propio** | El que escribimos en la Fase 2 | — |

---

## 7. Trampas conocidas

Verificadas empíricamente. Léelas antes de depurar nada.

### Los dos servidores externos están rotos con MCP 2.x

Ambos declaran `mcp[cli]>=1.0.0` sin cota superior. uv instala MCP 2.x, donde
`FastMCP` → `MCPServer` y `mcp.server.fastmcp` no existe.

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'
```

**Solución:** `--with "mcp<2"` en el comando de arranque. Es obligatorio.

### `mcp-qiskit` es stateless

El README dice que mantiene estado. **Es falso.** El circuito es un dict JSON
plano que se deserializa → ejecuta → reserializa en cada llamada.

```python
c = create_quantum_circuit_tool(2, 2)
c = add_gate_tool(circuit=c, gate_name="h",  qubits=[0])   # reenvía SIEMPRE
c = add_gate_tool(circuit=c, gate_name="cx", qubits=[0, 1])
run_circuit_tool(circuit=c, shots=1024)
```

El cliente DEBE conservar y reenviar el dict. LangGraph lo resuelve con un
reducer — es el primer caso real donde entender los reducers importa.

### Gates paramétricos sin `params` reciben defaults silenciosos

`rx` → 0.5, `u3` → 0,0,0. **No hay error.** El circuito queda silenciosamente
incorrecto. Este es el fallo más peligroso para un objetivo de aprendizaje:
el agente cree que funcionó.

### `mcp-qiskit` devuelve `statevector` como strings

Viene `["0.7071067811865475+0j", ...]` — números serializados con `str()`, no
JSON numérico. Inutilizable para aritmética.

### `run_circuit` degrada en silencio

Si pides un backend que no existe, cae a un `AerSimulator()` genérico **sin
avisar**. Pides density matrix y obtienes simulador ideal. No confíes en el
backend reportado.

### Otros bugs verificados

- `seed=0` se convierte en `42` (`seed if seed else 42`).
- `draw_circuit_tool("ascii")` rompe en consola Windows cp1252. Usa
  `PYTHONIOENCODING=utf-8`.
- El cliente MCP **no hereda el entorno**: recibe una allow-list. En Windows:
  `APPDATA, PATH, TEMP, USERNAME, USERPROFILE, ...`. Las API keys **no** llegan:
  pásalas con `env=`.
- Los errores de herramienta **no lanzan excepción**: vuelven con
  `is_error=True`. Compruébalo siempre.
- `structured_content` envuelve escalares: `{'result': 42}`, no `42`.
- `financial-mcp-server` trunca el histórico a **250 bars** siempre.
- `financial-mcp-server` no tiene ninguna herramienta que devuelva un "universo
  de activos". El universo vive en **nuestro** `config/`.
- Rate limits de Yahoo Finance: el autor mitiga con `curl_cffi` (impersona
  Chrome) + caché de 120 s en proceso.

### Rendimiento

- `mcp-qiskit`: **67 s** el primer arranque (97 paquetes), ~9 s en caliente.
  Por eso `timeout: 60000` en OpenCode, no el default de 5000.
- Windows: los clientes GUI lanzados desde el menú Inicio tienen `PATH` mínimo.
  **Usa la ruta absoluta a `uvx.exe`.**

---

## 8. Onde NO usar el MCP para el trabajo real

`mcp-qiskit` sirve para **aprender el protocolo** (Fase 1) y para **demostrar la
integración multi-MCP** (Fase 3). Para el trabajo cuántico serio —QAOA, valores
esperados, ruido— usa **Qiskit directo** en el `.venv`:

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit_aer.noise import NoiseModel
```

Razones: el statevector viene como strings, no hay ruido real, el backend
reportado no es fiable, y `qiskit-optimization` está **descontinuado por IBM**
(construye las matrices QUBO a mano con numpy).

El MCP es la **capa de orquestación**. El motor de cálculo es Qiskit directo.

---

## 9. Antes de dar por terminada una tarea

- [ ] ¿Actualicé `project-memory/changelog.md`?
- [ ] ¿Actualicé `project-memory/next-steps.md`?
- [ ] ¿Si hubo decisión de diseño, está en `decisions.md`?
- [ ] Si toqué `src/`, ¿actualicé `tests/`?
- [ ] ¿El commit sigue el formato de §5?
- [ ] ¿No hay secretos ni rutas absolutas en código?