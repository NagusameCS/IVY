# Mathcha Markdown Example

This document demonstrates the use of **Mathcha** for rendering inline and block math expressions.

## Inline Math Example

Here is an example of inline math using Mathcha syntax:  
[[math]]E = mc^2[[/math]]

You can also mix inline math with text, like this:  
The equation [[math]]a^2 + b^2 = c^2[[/math]] is known as the Pythagorean theorem.

## Block Math Example

Below is an example of a block math expression:

[[math-block]]
\int_a^b f(x) dx = F(b) - F(a)
[[/math-block]]

Another example of a block equation:

[[math-block]]
\frac{d}{dx}\left( x^n \right) = n x^{n-1}
[[/math-block]]

## Combining Mathcha and LaTeX

You can also use LaTeX syntax alongside Mathcha. For example:

- Inline LaTeX: $E = mc^2$
- Block LaTeX:
  $$
  \int_a^b f(x) dx = F(b) - F(a)
  $$

## Complex Math Example

Here’s a more complex example using Mathcha:

[[math-block]]
\begin{aligned}
    \nabla \cdot \vec{E} &= \frac{\rho}{\epsilon_0} \\
    \nabla \cdot \vec{B} &= 0 \\
    \nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t} \\
    \nabla \times \vec{B} &= \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}
\end{aligned}
[[/math-block]]

## Conclusion

This Markdown file demonstrates how to use Mathcha for both inline and block math expressions. You can mix Mathcha with LaTeX to achieve the best of both worlds.
