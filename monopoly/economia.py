"""Da frequência de visita ao retorno do investimento."""

from .tabuleiro import ALUGUEIS, CUSTO_CASA, GRUPOS, PRECOS

NIVEIS = {"sem casas": 0, "3 casas": 3, "hotel": 5}
VALOR_ESPERADO_DADOS = 7


def _aluguel(casa, grupo, nivel):
    if grupo == "Ferrovia":
        return 200
    if grupo == "Utilidade":
        return 10 * VALOR_ESPERADO_DADOS
    aluguel = ALUGUEIS[casa][nivel]
    return 2 * aluguel if nivel == 0 else aluguel  # grupo completo dobra o aluguel sem casas


def retorno_por_grupo(pi, nivel="hotel"):
    """Tabela por grupo completo, ordenada do menor tempo de retorno para o maior.

    `lances_para_retorno` conta lances de adversários: com 3 adversários, divida por 3.
    Ferrovias e companhias não têm construções, então usam sempre o aluguel máximo.
    """
    n = NIVEIS[nivel]
    linhas = []
    for grupo, casas in GRUPOS.items():
        construcoes = 0 if grupo not in CUSTO_CASA else n * CUSTO_CASA[grupo] * len(casas)
        investimento = sum(PRECOS[c] for c in casas) + construcoes
        renda = sum(pi[c] * _aluguel(c, grupo, n) for c in casas)
        linhas.append({
            "grupo": grupo,
            "investimento": investimento,
            "renda_por_lance": float(renda),
            "lances_para_retorno": float(investimento / renda),
        })
    return sorted(linhas, key=lambda linha: linha["lances_para_retorno"])
