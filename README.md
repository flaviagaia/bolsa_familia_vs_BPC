# Bolsa Família vs BPC por Território

Projeto em `Python + Streamlit` para comparar territorialmente o Bolsa Família e o Benefício de Prestação Continuada (BPC), com foco em composição municipal do gasto social, dependência relativa entre programas e judicialização do BPC.

## Para que serve

Este projeto foi desenhado para responder perguntas analíticas como:

- quais municípios dependem mais do Bolsa Família do que do BPC;
- onde o BPC tem maior peso relativo na composição do gasto social;
- quais territórios combinam alta participação do BPC com maior judicialização;
- quais municípios merecem priorização gerencial ou de controle.

## O que é comparado

### Bolsa Família

Programa de transferência de renda voltado a famílias em situação de pobreza e extrema pobreza. Neste projeto, ele entra como **componente familiar** do gasto social no território.

### BPC

Benefício assistencial previsto na LOAS, pago a idosos e pessoas com deficiência que cumpram os critérios legais. Aqui, ele entra como **componente assistencial individual**, complementando a leitura territorial.

## Dados usados

O projeto combina duas fontes:

- **Bolsa Família real**, com base pública por município de Alagoas;
- **BPC sintético calibrado**, criado a partir do schema oficial do dicionário de dados do Portal da Transparência e da mesma base territorial municipal.

Como os downloads transacionais automatizados do BPC não estavam disponíveis neste ambiente, a comparação foi estruturada com:

- `Bolsa Família` real no ano-base `2023`;
- `BPC` sintético anual para `2023`, alinhado ao território e às regras analíticas do projeto.

## Técnicas usadas

- `pandas`
  Para leitura, transformação, agregação e comparação dos dois programas.
- **engenharia de indicadores territoriais**
  Para calcular participação relativa, razão entre programas e pressão assistencial.
- **simulação calibrada**
  Para reproduzir um cenário plausível do BPC no mesmo território do Bolsa Família.
- `Streamlit`
  Para transformar a análise em painel interativo.
- `Plotly`
  Para visualizações de composição municipal, distribuição territorial e priorização.

## Indicadores gerados

- `valor_bolsa_familia`
- `valor_bpc`
- `valor_total_transferencias`
- `participacao_bolsa_pct`
- `participacao_bpc_pct`
- `razao_bolsa_bpc`
- `taxa_judicializacao_bpc_pct`
- `perfil_territorial`
- `indice_pressao_assistencial`
- `alerta_prioritario`

## Lógica analítica

1. Ler a base real de Bolsa Família por município.
2. Selecionar o ano-base `2023`, que também será usado para o comparativo com o BPC.
3. Gerar uma camada sintética anual do BPC para os mesmos municípios.
4. Consolidar os dois programas em uma mesma tabela municipal.
5. Calcular participação relativa de cada programa no território.
6. Classificar os municípios como:
   - `Predomínio Bolsa Família`
   - `Predomínio BPC`
   - `Equilíbrio relativo`
7. Construir um índice de priorização combinando:
   - volume total de transferências
   - judicialização do BPC
   - peso relativo do BPC

## Como executar

```bash
git clone https://github.com/flaviagaia/bolsa_familia_vs_BPC.git
cd bolsa_familia_vs_BPC
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
streamlit run app.py
```

## Testes

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## English

### Purpose

This project compares Bolsa Família and BPC at the municipal level, focusing on territorial composition of social spending, relative dependence on each program, and BPC judicialization.

### Data

- real Bolsa Família municipal data for Alagoas (`2023`)
- synthetic but schema-aligned BPC annual data for the same municipalities and year
- the dashboard automatically regenerates processed files if they are missing or corrupted

### Techniques and tools

- `pandas` for data preparation and aggregation
- calibrated synthetic generation for BPC
- territorial indicators for program composition
- rule-based prioritization for managerial review
- `Streamlit` and `Plotly` for the dashboard
