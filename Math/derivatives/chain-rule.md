\documentclass{article}
\usepackage{amsmath, amssymb, graphicx}

\title{LaTeX Interpreter Test File}
\author{Test Author}
\date{\today}

\begin{document}

\maketitle

\section*{Basic Text and Formatting}
This is a test of \textbf{bold}, \textit{italic}, and \underline{underlined} text.
Also testing special characters: \%, \$, \#, \&, \_, \{, \}, \~{}, \^{}.

\section*{Lists}
\subsection*{Itemize}
\begin{itemize}
  \item First item
  \item Second item
\end{itemize}

\subsection*{Enumerate}
\begin{enumerate}
  \item First point
  \item Second point
\end{enumerate}

\section*{Math Mode}

Inline math: \( E = mc^2 \)

Displayed math:
\[
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
\]

Equations:
\begin{align}
  a^2 + b^2 &= c^2 \\
  \nabla \cdot \vec{E} &= \frac{\rho}{\varepsilon_0}
\end{align}

\section*{Theorem and Proof}

\textbf{Theorem.} For all \( a, b \in \mathbb{R} \), if \( a = b \), then \( a + c = b + c \) for any \( c \in \mathbb{R} \).

\textbf{Proof.} Assume \( a = b \). Then:
\[
a + c = b + c \quad \text{(by substitution)}
\]
\hfill\qedsymbol

\section*{Graphics (if supported)}
\includegraphics[width=0.3\textwidth]{example-image}

\end{document}
