# Citizen Assist AI - Contribuição de Energias Renováveis

**Integrante:** Rafael Laprega Gontijo Magalhães - RM: 561975
**Disciplina:** Soluções em Energias Renováveis e Sustentáveis

## Público e problema

O público são famílias da cidade de São Paulo com consumo próximo da média residencial do Sudeste, que querem reduzir a conta de luz. Muitas não sabem se devem mudar hábitos ou investir em energia solar. O assistente mostra as duas opções para a mesma casa, com custos, limitações e fontes.

## Funcionalidades de energia

- Estimativa do gasto anual de uma casa de referência.
- Economia com banho mais curto e com lâmpadas LED.
- Respostas que usam o consumo em kWh ou a potência e os minutos informados na pergunta.
- Avaliação de um sistema solar fotovoltaico.
- Comparação das alternativas, com recomendação.
- Impacto ambiental e efeito do horário de consumo.
- Calculadora do consumo de um aparelho.
- Resposta com referências e limitações, sem coletar dados pessoais.

A contribuição desta disciplina é este módulo. As respostas são geradas a partir de `resultados/resumo.json`, que é criado pela análise. Assim, se uma premissa mudar, a resposta muda junto.

## Como executar

```bash
pip install pandas matplotlib
python analise_energia.py
python assistente_energia.py
```

## Dados e premissas

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `dados/premissas.csv` | Valores usados, unidade, tipo (real público ou estimado) e fonte | Ver a coluna `fonte` |
| `dados/irradiacao_sundata.csv` | Irradiação mensal em São Paulo, plano a 24 graus, kWh/m².dia | CRESESB, SunData |
| `dados/SAMPLE_ENERGY_DATA.csv` | Amostra de medições por minuto de uma residência, de 2006 a 2010 | Material da disciplina, base UCI |

**Período de referência:** 12 meses, para as duas alternativas.

Cuidados com a amostra medida:

- A casa fica na França, então a amostra é usada apenas para estimar o perfil por horário. Ela não define consumo ou custo no Brasil.
- A coluna `Time` veio com uma data errada de exportação (2026-08-03). O código usa só a hora dessa coluna.
- A potência está em kW e é medida a cada minuto. A energia é calculada como potência ÷ 60.

## Cálculos

**Tarifa com impostos:** 0,78938 ÷ (1 − 0,18) = R$ 0,9627/kWh.

**Situação atual:** 184,2 kWh/mês × 12 = 2.210,4 kWh/ano, com gasto estimado de R$ 2.127,86/ano. As emissões estimadas são de 85,1 kg de CO2/ano.

**Alternativa A, banho mais curto e LED:**

- Chuveiro hoje: 3,5 kW × 3,58 banhos/dia × (8 ÷ 60) h × 365 dias = 609,8 kWh/ano, ou 27,6% da casa. Com 5 minutos por banho, a economia é de 3/8 disso: 228,7 kWh/ano.
- Os valores de banhos por dia, duração e uso da posição verão vêm da PPH 2019 da Eletrobras/Procel para São Paulo.
- Lâmpadas: 6 × (15 − 9) W × 5 h × 365 dias = 65,7 kWh/ano.

**Alternativa B, energia solar (3 módulos de 550 W, 1,65 kWp):**

- Geração mensal = kWp × irradiação × dias × 0,75.
- O consumo direto é o menor valor entre a geração do mês e 31,7% do consumo, que é a parte medida entre 9h e 16h. O restante da geração vira crédito.
- A conta nunca fica abaixo de 30 kWh por mês (ligação monofásica).
- A energia compensada paga 60% do Fio B.

## Comparação das alternativas

| Critério | A: banho e LED | B: solar |
|---|---|---|
| Investimento | R$ 60,00 | R$ 5.973,00 |
| Energia da rede evitada em 12 meses (B inclui a compensada) | 294,4 kWh | 1.850,4 kWh |
| Economia em 12 meses | R$ 283,38 | R$ 1.553,19 |
| Gasto final em 12 meses | R$ 1.844,48 | R$ 574,67 |
| Retorno simples | 0,21 ano | 3,85 anos (2,70 a 4,34 nos cenários) |
| Emissão evitada em 12 meses (operação) | 11,3 kg de CO2 | 80,9 kg de CO2 |
| Emissão de fabricação dos painéis, por ano de geração | não se aplica | 86,1 kg de CO2 |
| Viabilidade | Quase qualquer casa, inclusive de aluguel | Exige telhado próprio, bom sol, investimento e aprovação da distribuidora |

Os cenários de sensibilidade estão em `resultados/sensibilidade_solar.csv`, e os gráficos estão em `resultados/`. Nos cenários de desempenho 0,70 e 0,80, a economia não muda, porque o sistema gera mais do que a conta permite compensar e o excedente vira crédito sem uso.

## Justificativa das recomendações

1. **Comece pela alternativa A.** O custo é muito baixo, ela serve para quem mora de aluguel e reduz o consumo de verdade.
2. **Considere a alternativa B se houver telhado próprio e dinheiro ou financiamento.** Ela economiza mais na conta, mas exige investimento alto. O crédito sobrando indica que 3 módulos ficam um pouco acima do necessário nesta casa.
3. **Não venda a energia solar como grande ganho climático nesta casa.** Na operação, ela evita cerca de 80,9 kg de CO2 por ano, porque a rede brasileira emitiu só 38,5 kg/MWh em 2023. A fabricação dos painéis equivale a cerca de 41 kg/MWh (IPCC), um valor do mesmo tamanho. As bases são diferentes, por isso a comparação é aproximada. O impacto ambiental também inclui o descarte dos painéis.

## Limitações

- Os resultados são estimativas para uma casa de referência e não são garantidos.
- A potência efetiva do chuveiro (3.500 W) e os valores das lâmpadas são estimados. A economia depende de a família manter o novo hábito.
- O custo de R$ 3,62/Wp é a média residencial. Sistemas pequenos como este costumam custar mais por Wp, então o retorno pode ser maior.
- Usei uma única alíquota de impostos (18%). Em São Paulo, a alíquota de ICMS muda com a faixa de consumo.
- Tarifa, preços e fator de emissão foram conferidos em notícias e calculadoras que reproduzem as fontes oficiais. O ideal é conferir na REH da ANEEL, no SIRENE/MCTI e nos relatórios da Greener e da Solfácil.
- O Fio B (R$ 0,20/kWh) é estimado. O fator de emissão varia a cada mês.
- A análise não inclui bandeira tarifária, troca de inversor, juros de financiamento, reforço de telhado ou aumento futuro da tarifa.
- Famílias com Tarifa Social pagam outra tarifa. Nesse caso, a economia em reais é diferente e o retorno da energia solar tende a ser maior.
- A regra do Fio B muda nos próximos anos, e o cenário a partir de 2029 ainda depende da ANEEL.

## Referências

- CRESESB. SunData v3: https://cresesb.cepel.br/index.php?section=sundata
- EPE. Mercado de energia elétrica, IV trimestre de 2024: https://www.epe.gov.br/sites-pt/areas-de-atuacao/energia-eletrica/WorkshopCOPAM/EPE_COPAM_Workshop_Mercado_Consumo_IV%20TRI%202024.pdf
- Enel SP. Tarifa de energia elétrica: https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html
- Calculadora Energia. Valor do kWh da Enel SP em 2026 (componentes da REH 3.596/2026): https://calculadoraenergia.com.br/tarifa/enel-sp
- Canal Solar. Fio B em 2026: https://canalsolar.com.br/consumidores-60-do-fio-b-2026/
- Canal Solar. Estudo da Greener: https://canalsolar.com.br/energia-solar-residencial-esta-mais-barata-aponta-greener/
- Canal Solar. Radar Solfácil: https://canalsolar.com.br/preco-energia-solar-primeiro-trimestre-radar-solfacil/
- Cenário Energia. Fator de emissão do SIN: https://cenarioenergia.com.br/2024/02/15/emissoes-de-co2-na-geracao-de-energia-atingem-minima-em-onze-anos-no-brasil/
- IPCC. AR5, Grupo de Trabalho III, Anexo III: https://www.ipcc.ch/report/ar5/wg3/
- UCI. Individual Household Electric Power Consumption: https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- Eletrobras/Procel. Pesquisa de Posse e Hábitos de Uso de Equipamentos Elétricos 2019, São Paulo: https://eletrobras.com/pt/AreasdeAtuacao/ESTADOS_SAO_PAULO.pdf

## Testes com usuários

O roteiro e as tabelas dos testes estão em `testes/registro_testes_usuarios.md` e devem ser preenchidos com os testes reais. A saída real de uma execução do assistente está em `testes/evidencia_execucao.txt`.
