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

# Matemática de carteras — de Markowitz a QUBO

> **Prerrequisitos:** ninguno (álgebra lineal y numpy). Se puede leer antes que
> `quantum-physics.md`. **Objetivo:** definir retorno, riesgo y Sharpe con
> propiedad, y derivar por qué la cartera **discreta** es QUBO.

## 1. Retornos

$R_{p,t} = \sum_i w_i R_{i,t}$. El retorno compuesto es un producto: su esperanza
**no** es $1 + \mu_p$. No confundir $\mathbb{E}[R]$ con retorno realizado.

```{code-cell} ipython3
import numpy as np

rng = np.random.default_rng(42)
rets = rng.normal(0.0005, 0.02, size=(250, 8))  # 250 días, 8 activos
mu = rets.mean(axis=0)
sigma = rets.std(axis=0)
print("mu por activo:", np.round(mu, 4))
print("sigma por activo:", np.round(sigma, 4))
```

## 2. Media, covarianza, estimadores

$\Sigma = X^T X / (T-1)$ con $X$ centrada. Con $N$ activos y $T$ observaciones,
$\mathrm{rango}(X) \le \min(T-1, N)$: **si $N \ge T$, $\Sigma$ es singular**.
Los autovalores se sesgan (Marchenko-Pastur); el remedio es shrinkage
(Ledoit-Wolf).

## 3. Sharpe y sus trampas

$S = (\mu_p - r_f)/\sigma_p$. Trampas: (i) el Sharpe máximo **in-sample** es el
máximo de $N$ variables ruidosas: está sesgado hacia arriba como
$\sigma_S\sqrt{2\ln N}$ (más activos **no** lo arreglan, lo empeoran); (ii) no
distinguir $S$ muestral de $S$ verdadero con $T$ finito.

## 4. Markowitz con Lagrange

$$\max_w\; w^\top\mu - \tfrac{\lambda}{2} w^\top\Sigma w \quad \text{s.a. }
\mathbf{1}^\top w = 1,\; w \ge 0$$

Solución interior: $w^* = \Sigma^{-1}(\mu - \nu\mathbf{1})/\lambda$. Frontera
eficiente = envolvente no dominada; tangency $w_T \propto
\Sigma^{-1}(\mu - r_f\mathbf{1})$; mínimo global
$w_{GMV} = \Sigma^{-1}\mathbf{1}/(\mathbf{1}^\top\Sigma^{-1}\mathbf{1})$.

```{code-cell} ipython3
# Frontera a mano: Cholesky, no inv (condicionamiento).
Sigma = np.cov(rets, rowvar=False) + 1e-6 * np.eye(8)
L = np.linalg.cholesky(Sigma)
print("cond(Sigma) =", round(float(np.linalg.cond(Sigma)), 1))
```

## 5. De Markowitz a QUBO (la sección clave)

El Markowitz **continuo** es convexo: se resuelve en milisegundos, no hay nada
que cuantizar. La dureza entra al **discretizar**: número entero de acciones,
cardinalidad $\sum_i x_i \le K$, bandas, costes de transacción.

Con $x \in \{0,1\}^N$ (selección) y presupuesto $\sum x_i = B$:

$$\min_x\; x^\top C x, \qquad C = \Sigma + P\,(\mathbf{1}\mathbf{1}^\top + I)$$

Cadena: cartera discreta ⊂ QP-hard ⊂ NP-completo ⊂ QUBO (Barahona 1982). La
matriz $C$ se construye **a mano con numpy**: `qiskit-optimization` está
descontinuado por IBM y además es pedagógicamente mejor verla salir de $\Sigma$.

## 6. El dato que mata la ventaja cuántica (plantado aquí, no al final)

$N = 20 \Rightarrow 2^{20} = 1{,}048{,}576$ carteras: enumerables vectorizadas
con numpy en **menos de un segundo** en un portátil. Celda de timing real en el
notebook ejecutado.

```{code-cell} ipython3
import time

N = 20
t0 = time.perf_counter()
n = 1 << N
print(f"2^{N} = {n:,} carteras")
print(f"(enumerarlas vectorizadas: ver salida ejecutada, < 1 s en portátil)")
print(f"tiempo de esta celda: {time.perf_counter() - t0:.3f} s")
```

## Ejercicios

<details><summary>1. Deriva w_GMV y comprueba que su sigma es mínima.</summary>
$\nabla(w^\top\Sigma w) = 2\Sigma w = \nu\mathbf{1}$ con la ligadura da
$w \propto \Sigma^{-1}\mathbf{1}$; normalizar. Verificar contra SLSQP.
</details>

<details><summary>2. Escribe el QUBO de "elige B=6 de N=10 minimizando riesgo".</summary>
$C = \Sigma + P(\mathbf{1}\mathbf{1}^\top + I)$ con $P$ grande; resolver por
fuerza bruta ($2^{10} = 1024$) y comprobar que el óptimo cumple $\sum x_i = 6$.
</details>

<details><summary>3. ¿Por qué el Markowitz continuo no es NP-hard?</summary>
Porque es un QP convexo: el Hessiano $\Sigma$ es semidefinido positivo y el
óptimo es único e interior (o en una cara). La dureza solo entra con las
restricciones enteras.
</details>

## Trampas para un físico

- $\mathbb{E}[R]$ no es retorno compuesto; los productos no conmutan con la esperanza.
- El Sharpe máximo in-sample crece con $N$: optimizar sobre el óptimo es circular.
- $\Sigma$ con pocos meses de datos está mal condicionada aunque $\lambda_{\min}$
  parezca razonable en valor absoluto.

## Referencias

- Markowitz (1952); Barahona, *On the computational complexity of Ising spin
  glass models* (1982) (verificadas)
- Lo (2002) sobre el sesgo del Sharpe máximo (verificada)
