"""Método da Potência e Método da Potência Inversa com deslocamento complexo."""

import numpy as np


def metodo_da_potencia(A, v0, tol=1e-12, max_iter=5000):
    """Retorna (vetor estacionário, iterações, erros relativos L1 por iteração)."""
    v = v0 / v0.sum()
    erros = []
    for _ in range(max_iter):
        v_novo = A @ v
        v_novo = v_novo / v_novo.sum()
        erros.append(np.linalg.norm(v_novo - v, ord=1) / np.linalg.norm(v, ord=1))
        v = v_novo
        if erros[-1] < tol:
            break
    return v, len(erros), erros


def metodo_potencia_inversa(A, mu, v0, tol=1e-10, max_iter=200):
    """Autovalor de A mais próximo de mu. Retorna (autovalor, autovetor, iterações)."""
    A_c = A.astype(complex)
    M = A_c - mu * np.eye(A.shape[0], dtype=complex)
    v = v0 / np.linalg.norm(v0)
    lam = None
    for k in range(1, max_iter + 1):
        w = np.linalg.solve(M, v)
        w = w / np.linalg.norm(w)
        lam_novo = np.vdot(w, A_c @ w) / np.vdot(w, w)  # quociente de Rayleigh
        convergiu = lam is not None and abs(lam_novo - lam) < tol
        v, lam = w, lam_novo
        if convergiu:
            break
    return lam, v, k
