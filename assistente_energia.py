import json
import re
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
R = json.loads((PASTA / "resultados" / "resumo.json").read_text(encoding="utf-8"))
A = R["eficiencia"]
B = R["solar"]

AVISO = (
    "Atenção: são estimativas para uma casa de referência em São Paulo, não um resultado garantido. "
    "Seu resultado depende do seu consumo, da sua tarifa e do seu telhado. "
    "Este assistente é um protótipo educacional e não é um canal oficial."
)
REFERENCIAS = {
    "consumo": "EPE, consumo médio residencial no Sudeste em 2024",
    "tarifa": "ANEEL, REH 3.596/2026, tarifa B1 da Enel SP",
    "sol": "CRESESB, SunData, irradiação em São Paulo",
    "lei": "Lei 14.300/2022, regras de geração própria",
    "custo": "Greener e Solfácil, preço de sistemas residenciais",
    "emissao": "MCTI/SIRENE, fator de emissão de 2023, e IPCC AR5, ciclo de vida",
    "pph": "Eletrobras/Procel, Pesquisa de Posse e Hábitos 2019, São Paulo",
    "medicao": "UCI, Individual Household Electric Power Consumption (material da disciplina)",
}


def reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor, casas=1):
    return f"{valor:.{casas}f}".replace(".", ",")


def normalizar(texto):
    decomposto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def montar(texto, fontes):
    lista = "; ".join(REFERENCIAS[f] for f in fontes)
    return f"{texto}\n\nReferências: {lista}.\n\n{AVISO}"


def resposta_conta():
    return montar(
        f"Uma casa com {numero(R['consumo_ano_kwh'] / 12)} kWh por mês gasta cerca de {reais(R['gasto_ano'])} em 12 meses. "
        f"A tarifa usada é de {reais(R['tarifa_com_impostos'])} por kWh, sem bandeira tarifária.",
        ["consumo", "tarifa"],
    )


def resposta_banho():
    return montar(
        f"Em São Paulo, o chuveiro é usado em média 3,58 vezes por dia por casa. Com 8 minutos por banho na posição verão, "
        f"ele gasta cerca de {numero(A['chuveiro_atual_kwh'], 0)} kWh por ano, {numero(A['chuveiro_participacao'] * 100)}% da casa de referência. "
        f"Diminuir cada banho para 5 minutos evita cerca de {numero(A['detalhe_chuveiro_kwh'], 0)} kWh por ano, "
        f"cerca de {reais(A['detalhe_chuveiro_kwh'] * R['tarifa_com_impostos'])} por ano. Não custa nada. "
        "Para calcular o seu chuveiro, use a opção 8.",
        ["pph", "tarifa"],
    )


def resposta_led():
    return montar(
        f"Trocar 6 lâmpadas fluorescentes de 15 W por LED de 9 W, usadas 5 horas por dia, "
        f"evita cerca de {numero(A['detalhe_lampadas_kwh'], 0)} kWh por ano. "
        f"Isso dá cerca de {reais(A['detalhe_lampadas_kwh'] * R['tarifa_com_impostos'])} por ano. "
        f"O custo estimado é de {reais(A['investimento'])}.",
        ["tarifa"],
    )


def resposta_solar():
    return montar(
        f"Um sistema de {numero(B['potencia_kwp'], 2)} kWp custa cerca de {reais(B['investimento'])} e gera cerca de "
        f"{numero(B['geracao_kwh'], 0)} kWh por ano. A economia estimada é de {reais(B['economia_ano'])} por ano. "
        f"O retorno fica entre {numero(R['solar_melhor_retorno'])} e {numero(R['solar_pior_retorno'])} anos nos cenários testados. "
        "Exige telhado próprio, bom sol, dinheiro ou financiamento. A conta não zera: a ligação monofásica paga o mínimo de 30 kWh por mês, "
        "e a energia compensada paga parte do Fio B. Quem mora de aluguel pode não conseguir instalar.",
        ["sol", "custo", "lei", "tarifa"],
    )


def resposta_comparacao():
    return montar(
        f"Para a mesma casa, em 12 meses:\n"
        f"A) Banho mais curto e LED: investimento de {reais(A['investimento'])}, economia de {reais(A['economia_ano'])} por ano.\n"
        f"B) Energia solar: investimento de {reais(B['investimento'])}, economia de {reais(B['economia_ano'])} por ano.\n"
        "Recomendação: comece pela opção A, que quase não custa nada e serve para quem mora de aluguel. "
        "Considere a opção B se você tiver telhado próprio e puder investir.",
        ["consumo", "tarifa", "sol", "custo", "lei"],
    )


def resposta_ambiente():
    return montar(
        f"Em 12 meses, a opção A evita cerca de {numero(A['emissao_evitada_kg'])} kg de CO2. "
        f"Na opção solar, considerando só a operação, a geração evita cerca de {numero(B['emissao_evitada_kg'])} kg de CO2 por ano. "
        f"Porém, a fabricação dos painéis equivale a cerca de {numero(B['emissao_ciclo_vida_paineis_kg'])} kg por ano de geração, "
        "um valor do mesmo tamanho, porque a rede brasileira já é muito renovável. As duas contas usam bases diferentes, então servem só como comparação aproximada. "
        "O ganho principal da energia solar nesta casa é na conta. Os painéis ainda exigem descarte adequado no fim da vida útil.",
        ["emissao"],
    )


def resposta_horario():
    return montar(
        f"Nos dados medidos usados no estudo, só {numero(R['participacao_horas_sol'] * 100)}% do consumo acontece entre 9h e 16h, "
        f"quando há mais sol. À noite, das 18h às 22h, o consumo fica {numero(R['pico_noite_sobre_media'], 2)} vezes acima da média. "
        "Por isso, a maior parte da energia solar vai para a rede e volta como crédito. "
        "Esses dados são de uma casa na França, então servem só como exemplo do perfil por horário.",
        ["medicao", "lei"],
    )


TEMAS = [
    (("solar", "painel", "paineis", "fotovoltaic", "placa"), resposta_solar),
    (("aluguel", "alugad", "inquilin"), resposta_comparacao),
    (("compar", "alternativ", "melhor", "vale a pena", "recomend"), resposta_comparacao),
    (("banho", "chuveiro"), resposta_banho),
    (("led", "lampada", "luz acesa", "iluminacao"), resposta_led),
    (("co2", "emiss", "ambiente", "poluicao", "sustentav"), resposta_ambiente),
    (("horario", "noite", "hora "), resposta_horario),
    (("conta", "gasto", "gasta", "consumo", "tarifa", "economizar", "energia"), resposta_comparacao),
]

PESSOAIS = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b[\w.+-]+@[\w-]+\.[\w.-]+\b|\b\d{4,5}-?\d{4}\b")
INJECAO = re.compile(r"ignore|ignorar|desconsidere|prompt|instruc|\[sistema\]|nova regra")


def responder(mensagem):
    if not mensagem or not mensagem.strip():
        return "Sua mensagem está vazia. Escreva uma pergunta ou escolha uma opção do menu."
    if len(mensagem) > 500:
        return "Sua mensagem é muito longa. Escreva até 500 caracteres."
    if PESSOAIS.search(mensagem):
        return "Por segurança, não informe dados pessoais aqui. Não guardei nem vou repetir o que você enviou. Faça a pergunta sem esses dados."
    alvo = normalizar(mensagem)
    if INJECAO.search(alvo):
        return "Não posso mudar minhas regras nem mostrar instruções internas. Posso ajudar com dúvidas sobre uso de energia."
    consumo = re.search(r"(\d+(?:[.,]\d+)?)\s*kwh", alvo)
    if consumo:
        return resposta_consumo(float(consumo.group(1).replace(",", ".")))
    potencia = re.search(r"(\d{3,5})\s*(?:watts|w)(?![a-z])", alvo)
    minutos = re.search(r"(\d+(?:[.,]\d+)?)\s*min", alvo)
    if potencia and minutos:
        return resposta_aparelho(float(potencia.group(1)), float(minutos.group(1).replace(",", ".")) / 60, 30)
    for chaves, funcao in TEMAS:
        if any(chave in alvo for chave in chaves):
            return funcao()
    return (
        "Não encontrei essa informação no estudo de energia. Para outros assuntos, consulte o órgão competente. "
        "Exemplos do que sei responder: \"Vale a pena instalar placa solar?\" ou \"Quanto economizo com banho mais curto?\""
    )


def calcular_aparelho(potencia, horas, dias):
    return potencia / 1000 * horas * dias


def resposta_aparelho(potencia, horas, dias):
    if not (0 < potencia <= 20000 and 0 < horas <= 24 and 0 < dias <= 31):
        return "Valores fora do esperado. Use potência até 20.000 W, até 24 horas por dia e até 31 dias."
    energia = calcular_aparelho(potencia, horas, dias)
    return montar(
        f"Um aparelho de {numero(potencia, 0)} W usado {numero(horas * 60, 0)} minutos por dia, durante {numero(dias, 0)} dias, "
        f"gasta cerca de {numero(energia)} kWh por mês, cerca de {reais(energia * R['tarifa_com_impostos'])}. "
        "Se for chuveiro com chave verão e inverno, a potência real depende da posição usada.",
        ["tarifa"],
    )


def resposta_consumo(kwh):
    if not 0 < kwh <= 5000:
        return "Valor fora do esperado. Informe o consumo mensal em kWh, que aparece na conta de luz."
    gasto = max(kwh, 30) * R["tarifa_com_impostos"]
    return montar(
        f"Com {numero(kwh, 0)} kWh por mês, a conta fica em cerca de {reais(gasto)} por mês, sem bandeira tarifária. "
        f"O estudo usa uma casa de {numero(R['consumo_ano_kwh'] / 12)} kWh por mês. Como o seu consumo é diferente, "
        "a economia e o retorno da energia solar também mudam. Confira a tarifa e os impostos na sua conta.",
        ["tarifa"],
    )


def calculadora():
    try:
        potencia = float(input("Potência do aparelho em watts: ").replace(",", "."))
        horas = float(input("Horas de uso por dia: ").replace(",", "."))
        dias = float(input("Dias de uso por mês: ").replace(",", "."))
    except ValueError:
        print("Use apenas números. Exemplo: 5500.")
        return
    print(resposta_aparelho(potencia, horas, dias))


MENU = """
===== Citizen Assist AI - Energia =====
1 - Quanto custa a energia de uma casa
2 - Economia com banho mais curto
3 - Economia com lâmpadas LED
4 - Energia solar vale a pena?
5 - Comparar as alternativas
6 - Impacto ambiental
7 - Por que o horário de consumo importa
8 - Calcular o consumo de um aparelho
Ou escreva sua pergunta. Digite 0 para sair."""

OPCOES = {
    "1": resposta_conta,
    "2": resposta_banho,
    "3": resposta_led,
    "4": resposta_solar,
    "5": resposta_comparacao,
    "6": resposta_ambiente,
    "7": resposta_horario,
}


def main():
    print("Não informe dados pessoais neste chat.")
    try:
        while True:
            print(MENU)
            entrada = input("Opção ou pergunta: ").strip()
            if entrada == "0":
                print("Até logo.")
                return
            if entrada == "8":
                calculadora()
            elif entrada in OPCOES:
                print(OPCOES[entrada]())
            else:
                print(responder(entrada))
    except (EOFError, KeyboardInterrupt):
        print("\nAté logo.")


if __name__ == "__main__":
    main()
