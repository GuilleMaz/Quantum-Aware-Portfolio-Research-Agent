---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3
  name: python3
---

# Qiskit básico — compuertas, Bell, Aer

> **Prerrequisitos:** ninguno de física (ver `quantum-physics.md` para el
> fondo). **Objetivo:** construir el estado de Bell a mano y ejecutarlo en el
> simulador, entendiendo qué devuelve cada backend.

## 1. Qubits y compuertas

$|0\rangle$, $|1\rangle$. Superposición: $H|0\rangle = |+\rangle =
(|0\rangle + |1\rangle)/\sqrt{2}$. Entrelazamiento: `cx` (CNOT) con control en
$|+\rangle$.

```{code-cell} ipython3
import numpy as np

H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
cero = np.array([0, 0])
mas = H @ np.array([1, 0])
print("H|0> =", mas)  # [0.707, 0.707]
```

## 2. El estado de Bell

$|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$: se crea con `h` en el
qubit 0 y `cx(0,1)`. Medir da `00` o `11` con 50% cada una; `01` y `10` con 0%.

```{code-cell} ipython3
# Lo que el servidor MCP hace por ti en la Fase 1, aquí a mano con numpy.
bell = np.zeros(4)
bell[0] = 1 / np.sqrt(2)
bell[3] = 1 / np.sqrt(2)
probs = np.abs(bell) ** 2
print({k: round(float(p), 3) for k, p in zip(["00", "01", "10", "11"], probs)})
```

Con Qiskit directo (motor real, `--extra quantum`):

```python
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
AerSimulator().run(qc, shots=1024).result().get_counts()
# {'00': ~512, '11': ~512}
```

## 3. Qué devuelve cada backend

- `aer_simulator` con mediciones → `counts` (`{"00": 522, "11": 502}`).
- Sin mediciones → `statevector` (el vector completo, ideal para los notebooks).
- `shots=1024` es el default; con `seed` fijo es reproducible.
- **Aer es exacto**: sin `NoiseModel` no hay ruido. "Funciona en el simulador"
  no dice nada sobre hardware real.

## 4. Trampas del servidor MCP (Fase 1)

Se documentan aquí porque las sufrirás allí: el servidor es **stateless** (hay
que reenviar el dict del circuito), los gates paramétricos sin `params` fallan
en silencio, y el `statevector` vuelve como strings. Por eso el motor serio es
Qiskit directo (`AGENTS.md` §8).

## Ejercicios

<details><summary>1. ¿Por qué 01 y 10 salen ~0%?</summary>
Porque el estado solo tiene amplitud en |00> y |11>. La probabilidad es el
módulo al cuadrado de la amplitud: cero donde no hay amplitud.
</details>

<details><summary>2. ¿Qué cambia con shots=100 frente a 10000?</summary>
El error estadístico (~1/sqrt(shots)). Con 100 shots, 50/50 puede salir 60/40
por muestreo. Con 10000, ±1%.
</details>

## Referencias

- Docs de Qiskit: https://docs.quantum.ibm.com/ (verificada)
