
The **chain rule** is used when differentiating a function of a function.

> If $y = f(g(x))$, then:
>
> $$\frac{dy}{dx} = f'(g(x)) \cdot g'(x)$$

---

## 1. Example: $f(x) = \sin(3x^2)$

We identify an outer function $f(u) = \sin(u)$ and an inner function $u = 3x^2$.

- $f'(u) = \cos(u)$
- $u' = 6x$

$$
∴ f'(x) = \cos(3x^2) \cdot 6x = 6x \cos(3x^2)
$$



---

## 2. Example: $h(x) = \ln(x^2 + 1)$

Outer: $\ln(u)$  
Inner: $u = x^2 + 1$

- Outer derivative: $\frac{1}{u}$
- Inner derivative: $2x$

So:

$$
h'(x) = \frac{1}{x^2 + 1} \cdot 2x = \frac{2x}{x^2 + 1}
$$



---

## 3. Graphical Intuition

The chain rule describes how small changes in $x$ affect $y$ through both layers of the function. If the inner function grows quickly, the whole function responds more rapidly.

Try to spot inflection points, slopes, and concavity:

- $\sin(3x^2)$ oscillates faster than $\sin(x)$.
- $\ln(x^2 + 1)$ grows slowly and levels off.

---

## 4. Challenge

Differentiate and sketch:

$$
f(x) = e^{\cos(x)}
$$

(Hint: outer is $e^u$, inner is $\cos(x)$)
