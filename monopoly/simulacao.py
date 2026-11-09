"""Simulação de Monte Carlo para validar o modelo analítico e medir o custo das simplificações.

Modos:
- "simplificado": as mesmas hipóteses da matriz. Deve coincidir com ela; serve de teste.
- "completo": duplos dão novo lance, três duplos prendem, baralhos reais sem reposição
  e permanência na cadeia segundo uma política:
    "sair_logo": paga a fiança no lance seguinte;
    "ficar": tenta duplos por até 3 lances e só então sai.

A cada lance registra-se onde o jogador termina. O índice 40 é "preso", separado de
"só visitando" (índice 10). Cartas de saída grátis são tratadas como cartas sem movimento.
"""

import random
from dataclasses import dataclass

import numpy as np

from .tabuleiro import (CADEIA, COFRE_IDX, DESTINOS_COFRE, FERROVIAS, GO, N, SORTE_IDX,
                        UTILIDADES, VA_PARA_CADEIA, mais_proxima)
from .transicao import EPSILON_DUPLOS

PRESO = 40

_SORTE = [GO, 24, 11, "companhia", "ferrovia", "ferrovia", "volte3", CADEIA, 5, 39] + [None] * 6
_COFRE = list(DESTINOS_COFRE) + [None] * 14


@dataclass
class ResultadoSimulacao:
    media: np.ndarray    # 41 posições: casas 0-39 e PRESO
    erro_padrao: np.ndarray
    lances: int

    @property
    def por_casa(self):
        """Vetor de 40 casas, com preso e só visitando somados na casa 10."""
        v = self.media[:N].copy()
        v[CADEIA] += self.media[PRESO]
        return v


def _resolve_carta(carta, casa):
    if carta == "companhia":
        return mais_proxima(casa, UTILIDADES)
    if carta == "ferrovia":
        return mais_proxima(casa, FERROVIAS)
    if carta == "volte3":
        return (casa - 3) % N
    return casa if carta is None else carta


def _cadeia_simplificada(rng, lances, queima):
    contagem = [0] * 41
    casa = GO
    prob_duplos = EPSILON_DUPLOS / (1 + EPSILON_DUPLOS)
    for t in range(lances + queima):
        if rng.random() < prob_duplos:
            casa = CADEIA
        else:
            casa = (casa + rng.randint(1, 6) + rng.randint(1, 6)) % N
            if casa == VA_PARA_CADEIA:
                casa = CADEIA
            elif casa in SORTE_IDX:
                casa = _resolve_carta(rng.choice(_SORTE), casa)
            if casa in COFRE_IDX:
                casa = _resolve_carta(rng.choice(_COFRE), casa)
        if t >= queima:
            contagem[casa] += 1
    return contagem


class _Baralho:
    def __init__(self, cartas, rng):
        self.cartas = list(cartas)
        rng.shuffle(self.cartas)
        self.topo = 0

    def compra(self):
        carta = self.cartas[self.topo]
        self.topo = (self.topo + 1) % len(self.cartas)
        return carta


def _cadeia_completa(rng, lances, queima, politica):
    contagem = [0] * 41
    sorte, cofre = _Baralho(_SORTE, rng), _Baralho(_COFRE, rng)
    casa, duplos, preso, tentativas = GO, 0, False, 0
    for t in range(lances + queima):
        d1, d2 = rng.randint(1, 6), rng.randint(1, 6)
        vai_preso = False
        move = True
        novo_lance_permitido = d1 == d2

        if preso and politica == "ficar":
            if d1 == d2 or tentativas == 2:
                preso, tentativas = False, 0
                novo_lance_permitido = False
            else:
                tentativas += 1
                move = False
        elif preso:
            preso, tentativas = False, 0

        if move:
            duplos = duplos + 1 if novo_lance_permitido else 0
            if duplos == 3:
                vai_preso = True
            else:
                casa = (casa + d1 + d2) % N
                if casa == VA_PARA_CADEIA:
                    vai_preso = True
                elif casa in SORTE_IDX:
                    carta = sorte.compra()
                    if carta == CADEIA:
                        vai_preso = True
                    else:
                        casa = _resolve_carta(carta, casa)
                if not vai_preso and casa in COFRE_IDX:
                    carta = cofre.compra()
                    if carta == CADEIA:
                        vai_preso = True
                    else:
                        casa = _resolve_carta(carta, casa)

        if vai_preso:
            casa, preso, tentativas, duplos = CADEIA, True, 0, 0
        if t >= queima:
            contagem[PRESO if preso else casa] += 1
    return contagem


def simular(modo="completo", politica="ficar", n_cadeias=200, lances=20_000, queima=200, semente=42):
    """Roda cadeias independentes e devolve média e erro padrão entre elas."""
    if modo not in ("simplificado", "completo"):
        raise ValueError(f"modo desconhecido: {modo}")
    if politica not in ("sair_logo", "ficar"):
        raise ValueError(f"política desconhecida: {politica}")
    freq = np.zeros((n_cadeias, 41))
    for c in range(n_cadeias):
        rng = random.Random(semente + c)
        if modo == "simplificado":
            freq[c] = _cadeia_simplificada(rng, lances, queima)
        else:
            freq[c] = _cadeia_completa(rng, lances, queima, politica)
    freq /= lances
    return ResultadoSimulacao(freq.mean(axis=0), freq.std(axis=0, ddof=1) / np.sqrt(n_cadeias),
                              n_cadeias * lances)
