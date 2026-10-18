# Cuaderno de física cuántica

> **Advertencia sobre quién escribe esto.** Esto lo escribe alguien que viene de
> **física de partículas**, no de computación cuántica. Eso es bueno para tres
> cosas: los estados entrelazados, las trazas parciales y la notación de Dirac no
> le son ajenas. Es malo para otras: **la terminología de la información
> cuántica tiene trampas y las etapas saltadas cuestan un día entero**.
>
> Concreta: cuando en un notebook de `theory/` vea "el estado del sistema", no
> asumo lo mismo que un físico de partículas. `|ψ⟩` es un ket en un espacio de
> Hilbert de dimensión 2ⁿ, no una función de onda de una partícula. `ρ` es una
> matriz de densidad, no una densidad de probabilidad. La notación es la misma y
> el objeto es otro.
>
> **Regla que sigo:** si una fórmula de este cuaderno no la puedo derivar o
> verificar con una referencia, va marcada como **NO VERIFICADO**. No se
> escribe física de memoria. Este proyecto trata de ser honesto sobre el
> resultado científico (`README.md`); no tiene sentido ser deshonesto sobre las
> herramientas.

**Orden de lectura físico obligatorio:** `theory/quantum-physics.md` →
`theory/portfolio-math.md` §7 → `theory/qaoa.md`. Este cuaderno es el
cuaderno, los notebooks son el desarrollo.

---

## Mapa de equivalencias: Qiskit ⇔ Nielsen & Chuang

El SDK de Qiskit usa nombres de objetos. La notación estándar usa operadores.
Esta tabla es el puente, y es el primer sitio donde se_busca cuando un
notebook mezcla los dos.

| Qiskit (`qiskit.quantum_info`) | Notación N&C | Qué es |
|---|---|---|
| `Statevector([a, b, c, d])` | ket $\|\psi\rangle$ | Vector de amplitudes en $\mathbb{C}^{2^n}$ |
| `DensityMatrix(rho)` | $\rho$ | Matriz de densidad: mezcla $\rho = \sum_k p_k \|k\rangle\langle k\|$ |
| `Operator(A)` | $A$ | Matriz unitaria general, $n$ qubits → matriz $2^n \times 2^n$ |
| `SparsePauliOp([...], coeffs=[...])` | $\sum_k c_k P_k$ | Suma lineal de Pauli strings: $\hat{H} = \sum_k \alpha_k P_k$ |
| `partial_trace(state, qargs)` | $\mathrm{Tr}_{\mathcal{B}}\left[\rho\right]$ | Traza parcial sobre el subsistema $\mathcal{B}$ |
| `Operator.evolve(other, qargs, time)` | $e^{-iHt}$ | Propagación unitaria: $U = e^{-iHt}$ con $\hbar = 1$ |
| `Statevector.expectation_value(op)` | $\langle\psi\|H\|\psi\rangle$ | Valor esperado: $\langle H\rangle = \langle\psi\|H\|\psi\rangle$ |
| `NoiseModel` | $\{\mathcal{E}_k\}$ | Conjunto de canales CPTP (completely positive trace-preserving) |
| `QuantumCircuit` | $U$ compuesto | El circuito **es** un operador unitario, no un dibujo |
| `Pauli("ZZ")` | $Z\otimes Z$ | Un Pauli string: un Pauli por qubit |
| `.measure()` / `counts` | $\lvert c_0 c_1 \dots c_{n-1}\rangle$ | Un resultado en base computacional |

### Tres trampas de esta tabla

**1. `SparsePauliOp` no es un Hamiltoniano hasta que lo dices.** Es una suma de
Pauli strings, punto. Que sea el Hamiltoniano de coste, o el de un sistema fisico, o
nada, lo decide el contexto. La forma $\sum_k \alpha_k P_k$ es la misma para
cualquier observable. Ver la sección siguiente.

**2. `Statevector` y `DensityMatrix` no son intercambiables.** Un `Statevector`
representa un estado **puro**. Para estados mixtos hace falta `DensityMatrix`, y
el resultado de un sistema compuesto es `partial_trace`, no "el ket del sistema".

El error conceptual típico: reducir un estado entrelazado a "el estado de un
qubit" tomando la componente y descartando el resto. Eso no es la traza parcial,
y no se parece en nada.

**3. `expectation_value` de un estado sucio no es un autovalor.** Para un estado
propio, $\langle H\rangle = \lambda$. Para un estado superpuesto, $\langle H\rangle$
es un promedio. La diferencia no es cosmética: si el resultado de QAOA está por
debajo de $\lambda_0$, el estado es superpuesto y el principio de variación se
sigue cumpliendo. Ver "Principio de variación", más abajo.

---

## El Hamiltoniano de coste de un portfolio

### El objetivo y su matriz

El objetivo de una cartera (Sharpe, Markowitz, cualquier uno) se escribe como un
cuadrático:

$$f(x) = x^{\mathsf{T}} Q x, \quad Q \in \mathbb{R}^{n\times n} \text{ simétrica}$$

El estadístico cuántico se construye tomando **el estimador del valor esperado
de $\hat{f}$**, que en la base computacional es:

$$\hat{H}_C = \sum_i Q_{ii}\, Z_i + \sum_{i<j} (Q_{ij}+Q_{ji})\, Z_i Z_j$$

Es decir: **el Hamiltoniano es una suma de Pauli strings de peso 1 y 2**,
derivada de las entradas de $Q$.

### Por qué Σ densa → Hamiltoniano all-to-all → embedding caro

Aquí está el punto que `theory/portfolio-math.md` §7 tiene que dejar claro,
y que `theory/qaoa.md` desarrolla:

**$Q$ es una matriz densa.** En un problema de cartera real, el término de
covarianza $\Sigma$ es denso: todos los activos correlacionan con todos los demás.
No hay estructura de bloque, no hay dispersidad. Es una $\Sigma$ de mercado.

**Consecuencia 1 — el Hamiltoniano es all-to-all.** Si $Q_{ij} \neq 0$ para todo
$j \neq i$, el Hamiltoniano tiene $\Theta(n^2)$ términos. No hay forma de escribir
una cartera de 20 activos con un circuito de 20 qubits y unas pocas capas: hacen
falta ~$n^2/2$ interacciones por capa de coste.

**Consecuencia 2 — el embedding se come los qubits.** Para ejecutar QAOA hay que
codificar $\hat{H}_C$ como un circuito. Los términos $Z_i Z_j$ no son hardware
nativo: los dispositivos tienen interacciones de dos cuerpos (CNOT), no de
cuatro. Hay que **mapear cada Pauli string** a una secuencia de CNOT y rotaciones.
El mapeo de un término de $k$ Pauli necesita $O(k^2)$ CNOT. Con
$k = n$ para un Hamiltoniano todo a todo, el circuito crece **cuadráticamente**
en el número de assets.

**Consecuencia 3 — la profundidad domina.** Con $p$ capas QAOA, la profundidad
total es $p \times O(n^2)$ CNOTs. Un dispositivo actual tiene del orden de
$10^3$–$10^4$ CNOTs con fidelidad decente. El presupuesto se agota muy rápido.

> **Por qué esto no es un detalle técnico.** Es la razón estructural de por qué
> QAOA es un mal algoritmo para carteras reales y un buen ejercicio de física.
> El problema no es que el algoritmo falle: es que el **problema no encaja** en
> el hardware. Un $\Sigma$ densa de 1000 activos es un Hamiltoniano de ~$10^6$
> términos, y no existe hardware que lo ejecute. Es la misma razón por la que la
> ventaja cuántica en portfolio no aparece en la literatura: Stopfer & Wagner
> (arXiv:2509.17876) resuelven 1000 activos a optimalidad probada en segundos
> con MIP clásico. La ventaja no se está perdiendo: es que el problema es
> clásico y pequeño. Ver `theory/qaoa.md` §9.

---

## El objeto Ising

### La forma

El modelo de Ising con campo externo, en $n$ espines $s_i \in \{-1, +1\}$:

$$E(s) = -\sum_{i<j} J_{ij}\, s_i s_j - \sum_i h_i\, s_i$$

Minimizar $E(s)$ es un problema NP-difícil. Es el problema canónico de la
optimización combinatoria y el que QAOA ataca.

- $J_{ij}$: **acoplamiento** entre los espines $i$ y $j$. Quiere decir "a estos
  dos les conviene tener el mismo valor". Viene de las covarianzas.
- $h_i$: **campo externo** en el spin $i$. Es un término lineal: "a este activo
  le conviene estar dentro de la cartera".
- El signo menos no es decorativo: pone el problema en forma de **minimización**
  de energía.

**Estructura clave:** $E$ es puramente cuadrático. No hay términos de tercer
orden ni más. Esto es una restrección fuerte, y es justo lo que hace que $E$
sea fácil de codificar como Hamiltoniano: los términos de dos cuerpos se mapean
a CNOT con coste polinómico.

### La equivalencia con QUBO

QUBO (*Quadratic Unconstrained Binary Optimization*) es el mismo problema escrito
en bits en lugar de espines:

$$\text{minimizar } f(x) = \sum_{i<j} Q_{ij}\, x_i x_j + \sum_i q_i\, x_i,
\qquad x_i \in \{0, 1\}$$

La transformación es **$s_i = 2x_i - 1$**, es decir $x_i = (s_i + 1)/2$. No hay
ninguna pérdida: es una reparametrización bijectiva de $\{0,1\}^n$ a
$\{-1,+1\}^n$.

### El factor 1/4 — y por qué importa

Al sustituir $x = (s+1)/2$ en un $f$ escrito en bits, cada $x_i x_j$ se
convierte en:

$$x_i x_j = \frac{(s_i+1)(s_j+1)}{4}
= \frac{s_i s_j + s_i + s_j + 1}{4}$$

Aparece un **$1/4$**, y también **términos lineales** que no estaban en el
$J_{ij}$. El paso inverso (Ising → QUBO) tiene el mismo $1/4$ multiplicando los
cuadráticos, más una corrección lineal en $h$.

**Por qué importa y no es un detalle algebraico:**

1. **El factor 1/4 afecta al Hamiltoniano.** Si construyes el
   `SparsePauliOp` con los coeficientes de QUBO sin el factor, el Hamiltoniano
   está **escalado** por un factor 4. No es el mismo problema.
2. **Los términos lineales no se descartan.** Un $h_i$ se convierte en un término
   $Z_i$. Si se pasa el cuádrico y se olvida el lineal, el portfolio optimizado
   no es el que se quería: se ha resuelto otro problema, silenciosamente
   distinto.
3. **Constante global.** El término $+1/4$ de cada par es una constante. No
   cambia el argmin, pero **sí cambia el valor esperado del Hamiltoniano**, y por
   tanto el criterio de salida de QAOA y la lectura del resultado.

> **Esta es la parte más fácil de hacer mal y más difícil de detectar.** El
> argmin no cambia si solo te equivocas en la constante; cambia en cuanto
>Equivocas la escala o el término lineal. Por eso el principio de variación
> (siguiente sección) es el aserto que salva: si el Hamiltoniano no es el que
> querías, $\langle H_C\rangle$ puede salir por debajo de $\lambda_0$ del
> $\lambda_0$ del problema mal construido, y la identificación del bug es
> inmediata.

`theory/qaoa.md` es donde se deriva esto con cuidado, y donde se
implementa el mapeo de QUBO a Pauli strings. Este cuaderno solo deja constancia
de que existe y de por qué el $1/4$ está ahí.

---

## La fórmula mal escrita (y la correcta)

Este es el error conceptual más fácil de cometer al pasar de un problema
matemático a un circuito, y por eso tiene sección propia.

### La versión mal escrita

Cuando el intento es "diagonalizar la matriz y usarlo como Hamiltoniano", aparece
algo como:

$$H = \sum_{i,j} C_{ij}\, \lvert i\rangle\langle j\rvert \qquad \text{(MAL)}$$

### Por qué está mal

Tres errores en una línea:

1. **Está mal indexada.** $\sum_{i,j}$ corre sobre todos los pares, pero una
   matriz $C$ simétrica cuenta cada par dos veces. Sin la factorización
   $i<j$ (o sin el $1/2$ correcto), todos los acoplamientos se duplican.
2. **La base es incorrecta.** $\lvert i\rangle\langle j\rvert$ son los elementos
   de la matriz en la **base computacional** (estados $\lvert 0\dots 0\rangle$
   hasta $\lvert 1\dots 1\rangle$). El Hamiltoniano de coste se expresa en la
   **base de Pauli** (productos de $Z$), no en la base computacional. Son bases
   distintas del mismo espacio, y confundirlas es el error.
3. **No es diagonal.** $\lvert i\rangle\langle j\rvert$ con $i \neq j$ no es
   diagonal en ninguna base útil. El Hamiltoniano de coste **sí** debe ser
   diagonal.

### La versión correcta

$$H_C = \sum_i h_i\, Z_i + \sum_{i<j} J_{ij}\, Z_i Z_j$$

Donde $Z_i$ es el operador Pauli-Z acting sobre el qubit $i$, e
$Z_i Z_j$ es $Z$ en $i$ y en $j$, y $I$ en todos los demás.

Las dos propiedades que hacen que esto sea QAOA:

**1. Puramente diagonal.** En la base computacional, $Z_i$ tiene autovalores
$\pm 1$ y $Z_iZ_j$ también, así que todos los términos conmutan y son
simultáneamente diagonalizables. En esa base, $H_C$ ya es diagonal por
construcción: suSpectrum es el conjunto de valores propios. Calcular $\lambda_0$
es diagonalizar $2^n \times 2^n$ — para $n \le 20$ es instantáneo, lo que da el
optimo exacto contra el que comparar.

**2. Todo conmuta.** $[Z_i, Z_j] = 0$ para todo par. Consecuencia práctica
directa: **el orden de los términos en el `SparsePauliOp` es irrelevante**. No
hay que ordenarlos para que "cuadre". Esto parece obvio, pero si alguna vez has
visto un Hamiltoniano cambiar de energía según el orden de los términos,
significa que no era este $H_C$.

Y recordemos el mapeo con QUBO del apartado anterior: si el objetivo venía de
QUBO, los $h_i$ y $J_{ij}$ son los coeficientes **ya convertidos** (con el
factor $1/4$ y los términos lineales). Si vienen directo del objetivo Markowitz,
no hay conversión.

---

## Principio de variación como aserto

El principio de variación es la ley física de este cuaderno:

$$\langle H_C \rangle \geq \lambda_0 \qquad \text{siempre}$$

Donde $\langle H_C\rangle$ es el valor esperado del Hamiltoniano en el estado
que sale de QAOA, y $\lambda_0$ es su menor autovalor (el óptimo exacto).

**Interpretación:** cualquier estado físico da una energía mayor o igual que la
del estado fundamental. QAOA no puede "encontrar" algo mejor que el óptimo
exacto — el óptimo exacto **es** la cota.

### Por qué es el aserto de control del proyecto

$\lambda_0$ se puede calcular exactamente para $n \le 20$ (diagonalizar una
matriz de $2^{20} \times 2^{20}$ es lo bastante rápido, o se usa un solver de
ISING). Así que hay una **referencia exacta** contra la que medir.

La lectura para debugging es directa e infalible:

| Observación | Significado |
|---|---|
| $\langle H_C \rangle \geq \lambda_0$, cerca del óptimo | Funciona. QAOA hizo su trabajo |
| $\langle H_C \rangle > \lambda_0$, lejos | Funciona pero$p$ es pequeño, o el mapeo está mal. Normal al principio |
| $\langle H_C \rangle < \lambda_0$ | **Bug.** Siempre. No es "ruido cuántico" ni "el optimizador fue creative" |

**Si sale por debajo de $\lambda_0$, hay un error.** Sin excepciones. Las causas
en orden de probabilidad:

1. El Hamiltoniano del QAOA y el que se diagonalizó no son el mismo (error de
   escala, término lineal olvidado, o doble conteo en el $i<j$).
2. Se está comparando contra el $\lambda_0$ del **problema equivocado** (por
   ejemplo, $\lambda_0$ del QUBO sin convertir contra el Ising convertido).
3. Ruido numérico en un cálculo de baja precisión (improbable si $n$ es
   pequeño; si aparece con $n$ grande, investigate 1 y 2 primero).

Este aserto está en `AGENTS.md` §3.6 y es la regla de honestidad científica del
proyecto aplicada a una ecuación. No es una heurística de la práctica: es
inegalidad.

---

## QAOA devuelve una distribución, no un óptimo

Este es el segundo error conceptual más común, y el que más sorprende viniendo
de programación clásica.

Al terminar QAOA, lo que se tiene es un **estado**:

$$\lvert\psi(p, \vec{\gamma})\rangle = \prod_{k=1}^{p} e^{-i\beta_k \hat{H}_C}\,
e^{-i\gamma_k \hat{H}_M}\, H^{\otimes n}\lvert 0\rangle^{\otimes n}$$

De ese estado sale una **distribución de probabilidad** sobre las bases
computacionales:

$$P(x) = \left\lvert \langle x \lvert \psi \rangle \right\rvert^2$$

Es decir: QAOA produce una **distribución sobre las $2^n$ carteras posibles**.
No devuelve "la mejor cartera". Devuelve "cuán probable es cada cartera".

### Lo que NO puedes concluir

- **El bitstring más probable no es necesariamente el óptimo.** El argmax de
  $P(x)$ y el argmin de $E(s)$ **pueden ser distintos**. Cuando $p$ es
  pequeño, la distribución es ancha y su máximo puede estar lejos del óptimo
  (aunque cerca).
- **La media de la distribución no es el óptimo.** $\sum_x P(x)\, E(x)$ es un
  promedio ponderado, y para $p$ pequeño es una cota superior holgada.
- **No hay convergencia garantizada.** A diferencia de un gradiente clásico,
  QAOA no tiene garantía de que aumentar $p$ acerque al óptimo. En la práctica
  mejora empíricamente; en teoría es un circuito deferencia.

### Lo que sí puedes y debes hacer

1. **Reportar la distribución, no un óptimo.** El resultado honesto de QAOA es
   $P(x)$, o el subconjunto de $x$ con $P(x) > \epsilon$. Esto es lo que va en
   `outputs/`.
2. **Separar el resultado cuántico del resultado de negocio.** "El mejor bitstring
   de esta ejecución QAOA" y "la carteraóptima" son afirmaciones distintas. El
   informe tiene que distinguirlas.
3. **Usar el principio de variación como aserto continuo.** $\langle H_C\rangle$
   es la media sobre toda la distribución, y sí debe ser $\geq \lambda_0$. Es
   el único número que sí se puede comparar con el óptimo.

> **Aviso de honestidad científica.** QAOA aquí es un gran resultado de física
> y un mal algoritmo de inversión (ver `README.md`). Reportar un optimum
> cuántico como si fuera "la cartera" sin decir de dónde sale es el modo de
> fallo que este proyecto quiere evitar.

---

## Aer es un simulador EXACTO

**Sin `NoiseModel`, Aer no tiene ruido. Punto.** Es un simulador de la
evolución unitaria ideal: aplica exactamente $U\lvert\psi\rangle$.

Sin modelo de ruido, Aer calcula:

$$\lvert\psi_{\text{final}}\rangle = U\lvert\psi_{\text{inicial}}\rangle$$

exactamente, en precisión de máquina (hasta los bits de punto flotante). No hay
decoherencia, no hay error de puerta, no hay error de lectura, no hay crosstalk,
no hay deriva.

**"Funciona en el simulador" no dice absolutamente nada sobre hardware real.**

Un circuito QAOA que en Aer da $\langle H_C\rangle$ a un 1% del óptimo, en un
dispositivo con ruido puede dar completamente otra cosa, porque:

| Efecto | ¿En Aer sin ruido? | ¿En hardware? |
|---|---|---|
| Decoherencia (T2) | No | Sí |
| Error de puerta | No | Sí, acumulativo con la profundidad |
| Error de lectura | No | Sí |
| Crosstalk | No | Sí |
| Deriva y calibración | No | Sí, cambia por lote |
| Ruido de Shot | Sí (si se muestrea) | Sí |

Y el circuito QAOA es **profundo** (todo a todo, ver arriba), así que el error
de puerta se acumula. Un circuito de profundidad $d$ con error por puerta
$\epsilon$ tiene error acumulado $\approx d\epsilon$.

> **Regla del proyecto:** cualquier afirmación sobre qubits se hace con
> `NoiseModel` explícito, o se marca como **estimación ideal**. `AGENTS.md` §8:
> para el trabajo cuántico serio (QAOA, valores esperados, ruido) se usa
> **Qiskit directo** en el `.venv`, no el MCP. El MCP sirve para aprender el
> protocolo y para la integración multi-servidor; el motor de cálculo es Qiskit
> directo, con el modelo de ruido puesto.

---

## T1 y T2

Las dos constantes de tiempo que degradan un qubit real. Vienen de la física de
material, no de heuristics de diseño de compiladores.

### T1 — relajación (tiempo de vida de la energía)

El qubit es un sistema de dos niveles. La diferencia de energía entre $\lvert 0\rangle$
y $\lvert 1\rangle$ es $E_1 - E_0 = \hbar\omega$. El qubit **spontáneamente**
cae del estado excitado al fundamental, emitiendo un fotón, con constante de
tiempo $T_1$.

$$P_1(t) = P_1(0)\, e^{-t/T_1}$$

Es una **decaída exponencial pura**, governed por física. $T_1$ es el tiempo en el
que la población excitada se reduce a $1/e$ de su valor inicial.

Se nota en la **población** (`⟨Z⟩ de las frecuencias de salida bajan hacia el
ground state`).

### T2 — decoherencia (tiempo de coherencia)

$T_2$ mide cuándo se pierde la **coherencia** de fase — la información de
interferencia — no solo la población. Es siempre más corto o igual que $T_1$,
porque hay dos mecanismos de pérdida de coherencia:

1. **Relajación** (pérdida de energía): sola ya destruye coherencia.
2. **Desfase puro** (*pure dephasing*): ruido de fase sin pérdida de energía.

Las dos se suman inversamente:

$$\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{T_\phi}$$

### La restricción dura $T_2 \leq 2T_1$

De la ecuación anterior, como $1/T_\phi \geq 0$:

$$\frac{1}{T_2} \geq \frac{1}{2T_1}
\quad\Longrightarrow\quad
\boxed{T_2 \leq 2T_1}$$

**Esto es física, no una heurística.** Es una cota que se deduce de los dos
mecanismos de pérdida, no un criterio de diseño ni una aproximación de compilación.
Ningún dispositivo cuántico la viola: si un modelo de ruido de un backend
reporta $T_2 > 2T_1$, el modelo **está mal**, o los números vienen de
condiciones distintas y no son comparables directamente.

Consecuencia: **un qubit solo puede hacer interferencia útil durante $T_2$**, y
$T_2 \leq 2T_1$ limita ese tiempo a, como mucho, el doble de la vida de la
población.

Se nota en el **visado de interferencia** (las franjas de un circuito de
interferencia se lavan a escala de $T_2$).

> **Por qué importa aquí.** Un circuito QAOA depende por completo de
> interferencia: la mezcla de amplitudes es lo que explora el espacio de
> soluciones. Si el tiempo de decoherencia $T_2$ es mucho más corto que la
> duración del circuito, las interferencias constructive/destructiva se lavan y
> la distribución final se parece a la de un generador aleatorio. Con circuitos
> profundos (todo a todo), esto no es un detalle: es la razón por la que la
> advantage cuántica en QAOA está aún lejos.

---

## Preguntas abiertas

Se rellenan durante la Fase 3, cuando haya un grafo que construya el Hamiltoniano
de verdad y se puedan medir cosas.

### Sobre el mapeo QUBO → Pauli strings

- [ ] ¿Cómo se implementa exactamente el mapeo con el factor $1/4$ y los
      términos lineales? ¿Se hace en el `SparsePauliOp` o en el paso anterior?
- [ ] ¿Cuántos términos `$Z_i Z_j$` tiene un $Q$ denso de $n$ activos? ¿El
      número de qubits del circuito es $n$ o más (por el embedding)?
- [ ] ¿Cómo se comprueba que el $H_C$ construido coincide con el objetivo? ¿Prueba
      unitaria (comparar valores esperados en base computacional contra el
      objetivo evaluado a mano)?

### Sobre el embedding

- [ ] ¿Qué tan grande es el circuito resultante para $n = 5, 10, 20$? ¿A partir
      de qué $n$ deja de ser razonable?
- [ ] ¿Cuántos CNOTs por capa de coste? ¿Cómo se comparan con la conectividad
      real del dispositivo?
- [ ] ¿Se puede usar un baseline ISA (Instruction Set Architecture) hardware
      real, o es un ejercicio teorico a 20 qubits de juguete?
- [ ] ¿El mapeo de Pauli strings es con CNOTs, o Qiskit ya lo hace con
      `PauliEvolutionGate`? ¿Qué se usa?

### Sobre QAOA en la práctica

- [ ] ¿Qué $p$ (profundidad) basta para ver el efecto? ¿Cómo se mide "suficiente"
      sin tener un óptimo de referencia?
- [ ] ¿Cuántos shots hacen falta para distinguir la distribución QAOA de la
      uniforme? (Esto fija el presupuesto de muestreo.)
- [ ] ¿Cómo se optimizan los $\gamma$ y $\beta$? ¿COBYLA, gradient descent, o
      otro? ¿Quéyy## Gradient?
- [ ] ¿Qué pasa con el ruido en el gradiente? ¿Se usa un clasificador de
     kouwen
     _expectation (CQE) o directo?

### Sobre la honestidad científica

- [ ] ¿Se puede construir un caso donde QAOA **sí** supere al clásico? (La
      literatura dice que no para portfolios de este tamaño; pero ¿y con
      restricciones duras o estructura?)
- [ ] ¿Cómo se hace el experimento que demuestra que QAOA **no** da ventaja aquí?
      Sería un resultado negativo bien hecho.
- [ ] ¿Comparar QAOA contra el óptimo exacto en el mismo problema, con ruido y
      sin ruido? ¿Qué se demuestra con cada uno?

### Sobre la integración con el grafo

- [ ] ¿Cómo se comunica el nodo cuántico con el nodo financiero sin arrastrar
      Qiskit a los demás? (Ver `AGENTS.md` §3.2: la lógica MCP vive en
      `mcp_clients/`, pero Qiskit es local.)
- [ ] ¿Cuántos qubits puede correr un portátil? (Aer sí, hasta donde dé la RAM.)
      ¿Cómo se degrada el experimento cuando no cabe en memoria?
- [ ] ¿El `dict` del circuito que devuelve el MCP, quién lo posee en el grafo?
      (Ver `Annotated[dict, reducer]` en `TASKS.md` 3.14.)

---

## Fuentes

- Farhi, Goldstone & Gutmann, *A Quantum Approximate Optimization Algorithm*,
  arXiv:1411.4028 (2014). — QAOA.
- Cerezo et al., *Cost function dependent barren plateaus in shallow
  parametrized quantum circuits*, arXiv:2005.00772 (2020). — Efecto en QAOA.
  **NO VERIFICADO** — arXiv sin comprobar; verificar antes de citar.
- Nielsen & Chuang, *Quantum Computation and Quantum Information*, Cambridge
  (2010; 10th anniv. ed.). — Referencia para toda la notación de este cuaderno.
- Certo, Pham & Beaulieu, arXiv:2203.04912 (2022). — Ruido en QAOA.
- Stopfer & Wagner, arXiv:2509.17876 (2025). — Benchmark de portfolio cuántico.

> **Recordatorio permanente.** Este cuaderno lo escribe alguien de física de
> partículas. Cuando una afirmación aquí no se pueda derivar de N&C o de un
> paper verificado, va marcada como **NO VERIFICADO**. La honestidad del
> proyecto empieza aquí, no en el `README.md`.