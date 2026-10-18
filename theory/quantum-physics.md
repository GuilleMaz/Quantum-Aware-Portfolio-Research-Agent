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

# Física cuántica — cimientos

> **Prerrequisitos:** ninguno. **Leer antes que** `portfolio-math.md` y
> `qaoa.md`. **Objetivo:** el rigor mínimo para no perderte con Qiskit:
> statevector vs density matrix, entrelazamiento, traza parcial, valor
> esperado, ruido y NISQ.

## 1. Kets

$|\psi\rangle = \sum_x \psi_x |x\rangle$, $\sum_x |\psi_x|^2 = 1$. La fase
global es irrelevante; la relativa no.

## 2. Statevector vs density matrix

- Puro: $\rho = |\psi\rangle\langle\psi|$, $\mathrm{tr}\,\rho^2 = 1$.
- Mixto: $\rho = \sum_k p_k |\psi_k\rangle\langle\psi_k|$.
- Sin ruido ni medidas intermedias → statevector ($2^n$). Con ruido, traza
  parcial o entorno → density matrix ($4^n$).

```{code-cell} ipython3
import numpy as np

# Bell: puro globalmente...
bell = np.zeros(4, dtype=complex)
bell[0] = bell[3] = 1 / np.sqrt(2)
rho_AB = np.outer(bell, bell.conj())
print("tr(rho^2) =", round(float(np.trace(rho_AB @ rho_AB).real), 6), "(1 = puro)")
# ...pero mixto al reducir: rho_A = Tr_B(rho_AB) = I/2.
rho_A = np.array([[rho_AB[0, 0] + rho_AB[1, 1], rho_AB[0, 2] + rho_AB[1, 3]],
                  [rho_AB[2, 0] + rho_AB[3, 1], rho_AB[2, 2] + rho_AB[3, 3]]])
print("rho_A =\n", np.round(rho_A.real, 3))
```

## 3. Producto vs entrelazado

$|\Phi^+\rangle$ no factoriza. Schmidt: $|\psi\rangle =
\sum_i \sqrt{\lambda_i}\,|i\rangle_A|i\rangle_B$; rango 1 ⇔ producto. Para Bell,
$\rho_A = I/2$: **puro globalmente, mixto reducido**. El entrelazamiento vive en
las correlaciones de $\rho_{AB}$, no en $\rho_A$: Alice solo ve $I/2$ (no hay
señalización).

## 4. Valor esperado

$\langle O \rangle = \langle\psi|O|\psi\rangle$ con $O$ hermítico: es el
**promedio sobre muchas réplicas**, no el valor de una preparación. Una medida
da un autovalor; el promedio da el esperado.

## 5. Ruido: canales CPTP

$\mathcal{E}(\rho) = \sum_k A_k \rho A_k^\dagger$, $\sum_k A_k^\dagger A_k = I$.
Los tres casos:

- **Depolarizing:** $\mathcal{E}(\rho) = (1-p)\rho + p\,I/d$. Lo mezcla todo.
- **Dephasing:** quita las coherencias (off-diagonales) sin tocar poblaciones.
- **Amplitude damping:** $|1\rangle \to |0\rangle$ espontáneo (relajación).

$T_1$ (energía) y $T_2$ (coherencia) cumplen la restricción dura
$1/T_2 = 1/(2T_1) + 1/T_\phi$, es decir, **$T_2 \le 2T_1$ siempre**. Es física,
no heurística.

## 6. NISQ y simuladores

NISQ (Preskill 2018): sin corrección de errores, coherencia de microsegundos.
**Aer es exacto salvo que le pases un `NoiseModel`.** El notebook de QAOA lo
demuestra con los mismos 4 qubits en ideal, depolarizing 1% y $T_1/T_2$ reales:
el histograma se degrada.

## Ejercicios

<details><summary>1. Demuestra rho_A = I/2 para Bell a mano.</summary>
Expande |Φ+><Φ+| = (|00><00| + |00><11| + |11><00| + |11><11|)/2 y traza sobre B:
<00|·|00> y <11|·|11| sobreviven, los cruzados mueren. Queda I/2.
</details>

<details><summary>2. ¿Por qué T2 ≤ 2T1?</summary>
Porque 1/T2 = 1/(2T1) + 1/Tφ con 1/Tφ ≥ 0. La relajación de energía ya destruye
coherencia por sí sola; el ruido de fase solo puede empeorarlo.
</details>

<details><summary>3. Statevector no admite mezcla. ¿Por qué?</summary>
Porque es un ket: describe conocimiento máximo. La mezcla (incertidumbre
clásica sobre el estado) necesita ρ. Intentar una traza parcial sin densidad
es el error típico del físico que llega a Qiskit.
</details>

## Referencias

- Nielsen & Chuang, *Quantum Computation and Quantum Information* (texto base)
- Preskill, NISQ (arXiv:1801.00862, 2018) (verificada)
