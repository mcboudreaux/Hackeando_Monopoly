import numpy as np
import pytest

from monopoly.economia import retorno_por_grupo
from monopoly.metodos import metodo_da_potencia, metodo_potencia_inversa
from monopoly.simulacao import PRESO, simular
from monopoly.tabuleiro import ALUGUEIS, CADEIA, GRUPOS, N, NOMES, PRECOS, VA_PARA_CADEIA
from monopoly.transicao import matriz_coluna_estocastica, matriz_dados, matriz_final


@pytest.fixture(scope="module")
def A():
    return matriz_coluna_estocastica()


@pytest.fixture(scope="module")
def pi(A):
    v0 = np.zeros(N)
    v0[0] = 1
    return metodo_da_potencia(A, v0)[0]


def test_tabuleiro_consistente():
    assert len(NOMES) == N
    assert set(ALUGUEIS) | {c for g in ("Ferrovia", "Utilidade") for c in GRUPOS[g]} == set(PRECOS)


def test_dados_sao_circulares():
    P = matriz_dados()
    assert P[39, 1] == pytest.approx(1 / 36)
    assert P[0, 7] == pytest.approx(6 / 36)


def test_matrizes_estocasticas(A):
    assert np.allclose(matriz_final().sum(axis=1), 1)
    assert np.allclose(A.sum(axis=0), 1)
    assert (A >= 0).all()


def test_estacionario_e_autovetor(A, pi):
    assert np.linalg.norm(A @ pi - pi, ord=1) < 1e-10
    assert pi.sum() == pytest.approx(1)


def test_independe_do_vetor_inicial(A, pi):
    v, _, _ = metodo_da_potencia(A, np.ones(N))
    assert np.linalg.norm(v - pi, ord=1) < 1e-9


def test_casa_30_nunca_e_ocupada(pi):
    assert pi[VA_PARA_CADEIA] < 1e-12


def test_resultado_original_reproduzido(pi):
    assert pi[CADEIA] * 100 == pytest.approx(6.03, abs=0.005)
    assert pi[24] * 100 == pytest.approx(3.19, abs=0.005)


def test_potencia_inversa_coincide_com_eig(A):
    autovalores = np.linalg.eigvals(A)
    alvo = autovalores[np.argsort(-np.abs(autovalores))[1]]
    rng = np.random.default_rng(0)
    v0 = rng.random(N) + 1j * rng.random(N)
    lam, _, _ = metodo_potencia_inversa(A, alvo - 0.01, v0)
    assert abs(lam - alvo) < 1e-8


def test_simulacao_simplificada_coincide_com_matriz(pi):
    r = simular(modo="simplificado", n_cadeias=40, lances=5000, semente=1)
    assert np.abs(r.por_casa - pi).sum() < 0.04


def test_simulacao_reprodutivel():
    a = simular(n_cadeias=2, lances=500, semente=7)
    b = simular(n_cadeias=2, lances=500, semente=7)
    assert np.array_equal(a.media, b.media)


def test_ficar_na_cadeia_aumenta_tempo_preso():
    ficar = simular(politica="ficar", n_cadeias=10, lances=3000)
    sair = simular(politica="sair_logo", n_cadeias=10, lances=3000)
    assert ficar.media[PRESO] > sair.media[PRESO]


def test_frequencias_somam_um():
    assert simular(n_cadeias=2, lances=500).media.sum() == pytest.approx(1)


def test_retorno_investimento_laranja(pi):
    linha = next(l for l in retorno_por_grupo(pi, "hotel") if l["grupo"] == "Laranja")
    assert linha["investimento"] == 180 + 180 + 200 + 5 * 100 * 3
