"""Constrói a matriz de transição, uma regra do jogo por vez."""

import numpy as np

from .tabuleiro import CADEIA, COFRE_IDX, DESTINOS_COFRE, N, SORTE_IDX, VA_PARA_CADEIA, destinos_sorte

EPSILON_DUPLOS = (1 / 6) ** 3 / 3


def probabilidades_dois_dados():
    """{soma: probabilidade} para dois dados de 6 faces."""
    prob = {}
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            prob[d1 + d2] = prob.get(d1 + d2, 0) + 1 / 36
    return prob


def matriz_dados():
    """P[i, j] = probabilidade de ir de i para j apenas com os dados."""
    P = np.zeros((N, N))
    for i in range(N):
        for soma, p in probabilidades_dois_dados().items():
            P[i, (i + soma) % N] += p
    return P


def aplica_va_para_cadeia(P):
    """Quem cairia na casa 30 vai direto para a cadeia."""
    P = P.copy()
    for i in range(N):
        if i != VA_PARA_CADEIA:
            P[i, CADEIA] += P[i, VA_PARA_CADEIA]
            P[i, VA_PARA_CADEIA] = 0.0
    P[VA_PARA_CADEIA, :] = 0.0
    P[VA_PARA_CADEIA, CADEIA] = 1.0
    return P


def _aplica_cartas(P, casa, destinos):
    pesos = {}
    for destino in destinos:
        pesos[destino] = pesos.get(destino, 0) + 1
    ficam = 16 - len(destinos)
    for i in range(N):
        p = P[i, casa]
        if p == 0:
            continue
        P[i, casa] = p * ficam / 16
        for destino, peso in pesos.items():
            P[i, destino] += p * peso / 16


def aplica_regra_sorte(P):
    """Redistribui a probabilidade de cair em Sorte segundo as cartas."""
    P = P.copy()
    for casa in SORTE_IDX:
        _aplica_cartas(P, casa, destinos_sorte(casa))
    return P


def aplica_regra_cofre(P):
    """Aplicada depois de Sorte, porque 'Volte 3 casas' na casa 36 cai em um Cofre."""
    P = P.copy()
    for casa in COFRE_IDX:
        _aplica_cartas(P, casa, DESTINOS_COFRE)
    return P


def aplica_duplos(P, epsilon=EPSILON_DUPLOS):
    """Efeito médio de três duplos seguidos: incremento em Cadeia e renormalização."""
    Q = P.copy()
    Q[:, CADEIA] += epsilon
    return Q / (1.0 + epsilon)


def matriz_final():
    """Matriz P linha-estocástica com todas as regras."""
    return aplica_duplos(aplica_regra_cofre(aplica_regra_sorte(aplica_va_para_cadeia(matriz_dados()))))


def matriz_coluna_estocastica(P=None):
    """A = P^T, com colunas renormalizadas contra erro de ponto flutuante."""
    P = matriz_final() if P is None else P
    A = P.T.copy()
    return A / A.sum(axis=0, keepdims=True)
