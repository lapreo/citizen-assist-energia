import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).resolve().parent
RESULTADOS = PASTA / "resultados"
RESULTADOS.mkdir(exist_ok=True)

premissas = pd.read_csv(PASTA / "dados" / "premissas.csv", sep=";").set_index("chave")["valor"].to_dict()
irradiacao = pd.read_csv(PASTA / "dados" / "irradiacao_sundata.csv", sep=";")
amostra = pd.read_csv(PASTA / "dados" / "SAMPLE_ENERGY_DATA.csv", na_values=["?"]).dropna()
amostra["Hora"] = pd.to_datetime(amostra["Time"]).dt.hour

perfil = amostra.groupby("Hora")["Global_active_power"].mean()
horas_sol = perfil.loc[9:15].sum() / perfil.sum()
total_wh = amostra["Global_active_power"].sum() * 1000 / 60
participacao = {
    "cozinha": amostra["Sub_metering_1"].sum() / total_wh,
    "lavanderia": amostra["Sub_metering_2"].sum() / total_wh,
    "aquecimento_agua_e_clima": amostra["Sub_metering_3"].sum() / total_wh,
}
pico_noite = perfil.loc[18:22].mean() / perfil.mean()

tarifa = premissas["tarifa_sem_impostos"] / (1 - premissas["aliquota_impostos"])
consumo_ano = premissas["consumo_mensal"] * 12
gasto_ano = consumo_ano * tarifa
emissao_ano = consumo_ano * premissas["fator_rede"]


def alternativa_eficiencia():
    chuveiro_atual = premissas["chuveiro_w"] / 1000 * premissas["banhos_dia"] * premissas["banho_atual"] / 60 * 365
    chuveiro = chuveiro_atual * (premissas["banho_atual"] - premissas["banho_novo"]) / premissas["banho_atual"]
    lampadas = premissas["lampadas"] * (premissas["lampada_atual_w"] - premissas["lampada_led_w"]) / 1000 * premissas["horas_lampada"] * 365
    investimento = premissas["lampadas"] * premissas["custo_led"]
    economia_kwh = chuveiro + lampadas
    economia = economia_kwh * tarifa
    return {
        "alternativa": "A - Banho mais curto e lâmpadas LED",
        "investimento": investimento,
        "energia_rede_evitada_kwh": economia_kwh,
        "economia_ano": economia,
        "gasto_final_ano": gasto_ano - economia,
        "retorno_anos": investimento / economia,
        "emissao_evitada_kg": economia_kwh * premissas["fator_rede"],
        "detalhe_chuveiro_kwh": chuveiro,
        "chuveiro_atual_kwh": chuveiro_atual,
        "chuveiro_participacao": chuveiro_atual / consumo_ano,
        "detalhe_lampadas_kwh": lampadas,
    }


def alternativa_solar(custo_wp, fator_tarifa=1.0, desempenho=None):
    desempenho = desempenho or premissas["desempenho"]
    tarifa_caso = tarifa * fator_tarifa
    kwp = premissas["potencia_modulo"] * premissas["quantidade_modulos"] / 1000
    investimento = kwp * 1000 * custo_wp
    consumo = premissas["consumo_mensal"]
    creditos = gerado_ano = faturado = compensado = 0
    for _, mes in irradiacao.iterrows():
        gerado = kwp * mes["irradiacao_kwh_m2_dia"] * mes["dias"] * desempenho
        direto = min(gerado, consumo * horas_sol)
        creditos += gerado - direto
        restante = consumo - direto
        usar = min(creditos, max(restante - premissas["disponibilidade"], 0))
        creditos -= usar
        compensado += usar
        faturado += restante - usar
        gerado_ano += gerado
    custo_fio_b = compensado * premissas["fio_b"] * premissas["fio_b_percentual"] / (1 - premissas["aliquota_impostos"])
    gasto_final = faturado * tarifa_caso + custo_fio_b
    manutencao = investimento * premissas["manutencao"]
    economia = consumo_ano * tarifa_caso - gasto_final - manutencao
    return {
        "alternativa": "B - Energia solar fotovoltaica",
        "investimento": investimento,
        "potencia_kwp": kwp,
        "geracao_kwh": gerado_ano,
        "energia_rede_evitada_kwh": consumo_ano - faturado,
        "economia_ano": economia,
        "gasto_final_ano": gasto_final + manutencao,
        "retorno_anos": investimento / economia,
        "emissao_evitada_kg": gerado_ano * premissas["fator_rede"],
        "emissao_ciclo_vida_paineis_kg": gerado_ano * premissas["fator_solar"],
        "creditos_sobrando_kwh": creditos,
    }


eficiencia = alternativa_eficiencia()
solar = alternativa_solar(premissas["custo_wp"])
comparacao = pd.DataFrame([eficiencia, solar])
comparacao.to_csv(RESULTADOS / "comparacao.csv", sep=";", index=False, encoding="utf-8-sig", float_format="%.2f")

cenarios = {
    "Base": (premissas["custo_wp"],),
    "Custo menor (2,57 R$/Wp)": (premissas["custo_wp_baixo"],),
    "Tarifa 10% menor": (premissas["custo_wp"], 0.9),
    "Tarifa 10% maior": (premissas["custo_wp"], 1.1),
    "Desempenho 0,70": (premissas["custo_wp"], 1.0, 0.70),
    "Desempenho 0,80": (premissas["custo_wp"], 1.0, 0.80),
}
sensibilidade = pd.DataFrame(
    [
        {"cenario": nome, **{k: alternativa_solar(*args)[k] for k in ("investimento", "economia_ano", "retorno_anos")}}
        for nome, args in cenarios.items()
    ]
)
sensibilidade.to_csv(RESULTADOS / "sensibilidade_solar.csv", sep=";", index=False, encoding="utf-8-sig", float_format="%.2f")

resumo = {
    "registros_validos": len(amostra),
    "participacao_horas_sol": horas_sol,
    "pico_noite_sobre_media": pico_noite,
    "participacao_usos": participacao,
    "tarifa_com_impostos": tarifa,
    "consumo_ano_kwh": consumo_ano,
    "gasto_ano": gasto_ano,
    "emissao_ano_kg": emissao_ano,
    "eficiencia": eficiencia,
    "solar": solar,
    "solar_pior_retorno": sensibilidade["retorno_anos"].max(),
    "solar_melhor_retorno": sensibilidade["retorno_anos"].min(),
}
(RESULTADOS / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float), encoding="utf-8")

plt.figure(figsize=(8, 4))
plt.plot(perfil.index, perfil.values, marker="o")
plt.axvspan(9, 16, alpha=0.2, color="gold", label="Horas de maior sol (9h às 16h)")
plt.title("Potência ativa média por hora (dados medidos do material da disciplina)")
plt.xlabel("Hora do dia")
plt.ylabel("Potência ativa média (kW)")
plt.legend()
plt.savefig(RESULTADOS / "perfil_horario.png", dpi=150, bbox_inches="tight")
plt.close()

fig, eixos = plt.subplots(1, 2, figsize=(9, 4))
eixos[0].bar(["A", "B"], comparacao["investimento"])
eixos[0].set_title("Investimento inicial (R$)")
eixos[1].bar(["Hoje", "A", "B"], [gasto_ano, eficiencia["gasto_final_ano"], solar["gasto_final_ano"]])
eixos[1].set_title("Gasto em 12 meses (R$)")
plt.savefig(RESULTADOS / "comparacao.png", dpi=150, bbox_inches="tight")
plt.close()

print(json.dumps(resumo, ensure_ascii=False, indent=2, default=float))
