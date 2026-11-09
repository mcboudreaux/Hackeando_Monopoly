"""Regenera figures/ e results/resultados.json. Uso: python scripts/gerar_resultados.py"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from monopoly.economia import retorno_por_grupo
from monopoly.metodos import metodo_da_potencia
from monopoly.simulacao import PRESO, simular
from monopoly.tabuleiro import CADEIA, N, NOMES
from monopoly.transicao import matriz_coluna_estocastica

AZUL, LARANJA = "#1f6fb2", "#d9731a"
TINTA, TINTA_2, GRADE = "#222222", "#666666", "#e4e4e4"
FIG = RAIZ / "figures"
plt.rcParams.update({
    "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#999999", "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2,
    "ytick.color": TINTA_2, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.grid": True, "grid.color": GRADE, "axes.axisbelow": True,
})


def virgula(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


def posicao_no_anel(i):
    if i <= 10:
        return 10 - i, 0
    if i <= 20:
        return 0, i - 10
    if i <= 30:
        return i - 20, 10
    return 10, 40 - i


def rotulo(i):
    nome = NOMES[i]
    for prefixo in ("Avenida ", "Praca "):
        nome = nome.removeprefix(prefixo)
    nome = {"Cadeia / Só Visitando": "Cadeia", "Partida (GO)": "Partida", "Cofre Comunitario": "Cofre",
            "Companhia Eletrica": "Eletrica", "Companhia de Agua": "Agua", "Estacionamento Livre": "Estac. Livre",
            "Va para a Cadeia": "Va p/ Cadeia", "Imposto de Renda": "Imposto", "Imposto de Luxo": "Luxo", "Pennsylvania": "Pennsylv.", "Mediterranea": "Mediterr.", "Connecticut": "Connect.",
            "Carolina do Norte": "Carolina N.", "Pennsylvania Railroad": "Penn. RR",
            "Short Line Railroad": "Short Line", "Reading Railroad": "Reading RR",
            "B&O Railroad": "B&O RR", "Jardins Marvin": "Marvin"}.get(nome, nome)
    return nome


def figura_tabuleiro(pi):
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_xlim(0, 11), ax.set_ylim(0, 11), ax.set_aspect("equal"), ax.axis("off")
    cmap, limite = plt.get_cmap("Blues"), 0.035
    for i in range(N):
        x, y = posicao_no_anel(i)
        fracao = float(np.clip((pi[i] - 0.008) / (limite - 0.008), 0, 1))
        cor = cmap(0.05 + 0.75 * fracao)
        ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=cor, edgecolor="white", linewidth=2))
        texto = "white" if fracao > 0.8 else TINTA
        ax.text(x + .5, y + .63, rotulo(i), ha="center", va="center", fontsize=7.2, color=texto)
        ax.text(x + .5, y + .32, f"{virgula(pi[i] * 100)}%", ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=texto)
    ax.text(5.5, 6.45, "Onde o jogador termina cada lance", ha="center", fontsize=16, fontweight="bold", color=TINTA)
    ax.text(5.5, 5.85, "Distribuição estacionária da cadeia de Markov de 40 estados", ha="center", fontsize=11, color=TINTA_2)
    ax.text(5.5, 5.4, "Escala de cor limitada a 3,5% para a Cadeia não apagar o resto", ha="center", fontsize=10, color=TINTA_2)
    fig.savefig(FIG / "tabuleiro_calor.png", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figura_convergencia(erros, modulo_l2):
    k = np.arange(1, len(erros) + 1)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.semilogy(k, erros, color=AZUL, linewidth=2, label="Erro medido por iteração")
    ax.semilogy(k, erros[29] * modulo_l2 ** (k - 30.0), color=LARANJA, linewidth=2, linestyle="--",
                label=f"Previsão teórica: |λ₂|ᵏ, com |λ₂| = {virgula(modulo_l2, 3)}")
    ax.set_title("O segundo autovalor prevê a velocidade de convergência")
    ax.set_xlabel("Iteração do Método da Potência"), ax.set_ylabel("Erro relativo (L1, escala log)")
    ax.legend(frameon=False)
    fig.savefig(FIG / "convergencia.png", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figura_comparacao(pi, sair, ficar):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(N)
    ax.plot(x, ficar.por_casa * 100, color=LARANJA, linewidth=2, marker="o", markersize=4,
            label="Simulação completa, fica na cadeia")
    ax.plot(x, sair.por_casa * 100, color="#555555", linewidth=2, label="Simulação completa, paga e sai")
    ax.plot(x, pi * 100, color=AZUL, linewidth=2, linestyle="--", label="Modelo analítico")
    ax.set_title("A simplificação da matriz só pesa quando o jogador fica preso")
    ax.set_xlabel("Casa do tabuleiro"), ax.set_ylabel("% dos lances")
    ax.set_xticks(range(0, N, 5))
    ax.legend(frameon=False)
    fig.savefig(FIG / "analitico_vs_simulacao.png", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figura_retorno(linhas):
    linhas = linhas[::-1]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    valores = [l["lances_para_retorno"] for l in linhas]
    ax.barh([l["grupo"] for l in linhas], valores, color=AZUL, height=0.62)
    for y, v in enumerate(valores):
        ax.text(v + 1, y, virgula(v, 1), va="center", color=TINTA, fontsize=10)
    ax.set_title("Com hotéis, Laranja é o grupo que se paga mais rápido")
    ax.set_xlabel("Lances de adversários até recuperar o investimento")
    ax.grid(axis="y", visible=False)
    fig.savefig(FIG / "retorno_grupos.png", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True), (RAIZ / "results").mkdir(exist_ok=True)
    A = matriz_coluna_estocastica()
    v0 = np.zeros(N)
    v0[0] = 1
    pi, iteracoes, erros = metodo_da_potencia(A, v0)
    autovalores = np.linalg.eigvals(A)
    modulos = np.sort(np.abs(autovalores))[::-1]
    simplificado = simular("simplificado")
    sair = simular("completo", "sair_logo")
    ficar = simular("completo", "ficar")

    def resumo(r):
        return {"lances": r.lances, "L1_vs_analitico": float(np.abs(r.por_casa - pi).sum()),
                "cadeia_total_pct": float(r.por_casa[CADEIA] * 100), "preso_pct": float(r.media[PRESO] * 100),
                "erro_padrao_max_pct": float(r.erro_padrao.max() * 100)}

    resultados = {
        "iteracoes_potencia": iteracoes,
        "modulo_lambda2": float(modulos[1]),
        "lances_para_1pct": float(np.log(0.01) / np.log(modulos[1])),
        "top5_analitico": [{"casa": int(i), "nome": NOMES[i], "pct": float(pi[i] * 100)} for i in np.argsort(-pi)[:5]],
        "simulacao": {"simplificado": resumo(simplificado), "completo_sair_logo": resumo(sair), "completo_ficar": resumo(ficar)},
        "retorno": {n: retorno_por_grupo(pi, n) for n in ("sem casas", "3 casas", "hotel")},
        "retorno_ficar": {n: retorno_por_grupo(ficar.por_casa, n) for n in ("3 casas", "hotel")},
    }
    (RAIZ / "results" / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    figura_tabuleiro(pi)
    figura_convergencia(erros, float(modulos[1]))
    figura_comparacao(pi, sair, ficar)
    figura_retorno(resultados["retorno"]["hotel"])


if __name__ == "__main__":
    main()
