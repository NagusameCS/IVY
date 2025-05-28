
The **chain rule** is used when differentiating a function of a function.

> If $y = f(g(x))$, then:
>
> $$\frac{dy}{dx} = f'(g(x)) \cdot g'(x)$$

---

## 1. Example: $f(x) = \sin(3x^2)$

We identify an outer function $f(u) = \sin(u)$ and an inner function $u = 3x^2$.

$$f'(u) = \cos(u)$$
$$u' = 6x$$
$$∴ $$
$$
  f'(x) = \cos(3x^2) \cdot 6x = 6x \cos(3x^2)
$$



---

## 2. Example: $h(x) = \ln(x^2 + 1)$

Outer: $ln(u)$  
Inner: $u = x^2 + 1$

- Outer derivative: $\frac{1}{u}$
- Inner derivative: $2x$

So:

$$
h'(x) = \frac{1}{x^2 + 1} cdot 2x = frac{2x}{x^2 + 1}
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

### Problem: Chain Rule Application

Differentiate the following function:

$$
f(x) = \sin(3x^2 + 2x)
$$

---
# Markscheme use showcase
---


A function is defined as:

$$
f(x) = \sin(3x^2 + 2x)
$$

This function models the vertical position of a point on a vibrating string at time \( x \).  
Find the rate of change of the vertical position with respect to time at any point \( x \).

<details>
<summary>Markscheme</summary>

**Step 1:** Recognize the chain rule structure  
This is a composition:  
- Outer function: $$\sin(u)$$  
- Inner function: $$u = 3x^2 + 2x$$

**Step 2:** Differentiate each part  
- Derivative of outer: $$\frac{d}{du}[\sin(u)] = \cos(u)$$  
- Derivative of inner:  
  $$\frac{d}{dx}[3x^2 + 2x] = 6x + 2$$

**Step 3:** Apply the chain rule  
$$f'(x) = \cos(3x^2 + 2x) \cdot (6x + 2)$$

**Final Answer:**  
$$f'(x) = (6x + 2)\cos(3x^2 + 2x)$$

</details>


