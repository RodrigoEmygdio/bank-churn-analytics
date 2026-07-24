# Bank Churn Analytics

Aplicacao academica em Streamlit para analise de risco de churn de clientes
bancarios. O sistema usa dois pipelines treinados de scikit-learn, preserva as
predicoes de cada modelo de forma independente e consolida o resultado em um
nivel de risco deterministico.

## Descricao da aplicacao

O Bank Churn Analytics coleta atributos de um cliente bancario, valida e
transforma esses dados, executa os pipelines exportados de Gradient Boosting e
Decision Tree, interpreta a combinacao das predicoes e apresenta uma
recomendacao operacional em uma interface Streamlit.

A aplicacao e um sistema de apoio a analise. Ela nao deve ser usada como
decisao automatica ou deterministica sobre clientes reais.

## Principais funcionalidades

- Formulario Streamlit para entrada dos atributos do cliente.
- Validacao deterministica dos dados informados.
- Derivacao interna da feature `ProductsGroup`.
- Execucao independente dos pipelines Gradient Boosting e Decision Tree.
- Politica de risco em quatro niveis: `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.
- Interpretacao deterministica do nivel de risco e da concordancia entre os
  modelos.
- Recomendacoes de negocio baseadas no nivel de risco interpretado.
- Testes unitarios, testes de integracao e testes de fronteira arquitetural.
- Validacao de integridade dos artefatos por SHA-256 quando declarada em
  `artifacts/metadata.json`.

## Screenshot

Nenhum screenshot da aplicacao Streamlit esta versionado atualmente. Quando uma
captura oficial estiver disponivel, ela pode ser referenciada nesta secao.

## Inicio rapido

Requisitos principais:

- Python `>=3.14`, conforme `pyproject.toml`.
- `uv` instalado. Consulte a documentacao oficial:
  <https://docs.astral.sh/uv/>.

```bash
git clone https://github.com/RodrigoEmygdio/bank-churn-analytics.git
cd bank-churn-analytics
uv sync
uv run streamlit run app.py
```

Por padrao, o Streamlit abre a aplicacao em:

```text
http://localhost:8501
```

## Pre-requisitos

- Python compativel com `requires-python = ">=3.14"`.
- `uv` para sincronizar dependencias e executar comandos do projeto.
- Artefatos locais presentes em `artifacts/`.

As dependencias de runtime e desenvolvimento estao declaradas em
`pyproject.toml` e travadas em `uv.lock`.

## Clone e instalacao

```bash
git clone https://github.com/RodrigoEmygdio/bank-churn-analytics.git
cd bank-churn-analytics
uv sync
```

O comando `uv sync` cria ou atualiza o ambiente virtual local com as
dependencias do projeto.

## Executando a aplicacao Streamlit

```bash
uv run streamlit run app.py
```

Depois de iniciar o servidor, acesse:

```text
http://localhost:8501
```

## Como usar a aplicacao

1. Preencha o formulario com os atributos do cliente:
   - `Credit Score`;
   - `Geography`;
   - `Gender`;
   - `Age`;
   - `Tenure`;
   - `Balance`;
   - `Number of Products`;
   - `Credit Card`;
   - `Active Member`;
   - `Estimated Salary`.
2. Clique em `Analyze Customer`.
3. Revise o resultado apresentado:
   - nivel de risco;
   - resumo da analise;
   - concordancia entre modelos;
   - evidencias;
   - racional de negocio;
   - prioridade da recomendacao;
   - objetivo;
   - recomendacoes;
   - resultado esperado.

O usuario nao informa `ProductsGroup`; essa feature e derivada internamente a
partir de `Number of Products`.

## Comportamento dos niveis de risco

A politica usa apenas as classes previstas pelos dois modelos. Probabilidades
especificas dos modelos podem existir como evidencia tecnica, mas nao sao
combinadas, agregadas ou usadas para alterar o nivel de risco.

| Gradient Boosting | Decision Tree | Risk Level |
|------------------:|--------------:|:-----------|
| 0                 | 0             | LOW        |
| 0                 | 1             | MODERATE   |
| 1                 | 0             | HIGH       |
| 1                 | 1             | CRITICAL   |

Papeis dos modelos:

- Gradient Boosting: modelo primario.
- Decision Tree: modelo complementar de sensibilidade.

## Artefatos de modelo

Os artefatos estao versionados no repositorio em `artifacts/`:

| Caminho | Proposito |
|---|---|
| `artifacts/gradient_boosting_pipeline.joblib` | Pipeline completo do modelo Gradient Boosting. |
| `artifacts/decision_tree_pipeline.joblib` | Pipeline completo do modelo Decision Tree. |
| `artifacts/metadata.json` | Contrato operacional com versoes, schema de entrada, nomes dos artefatos, metricas, papeis dos modelos e hashes SHA-256. |
| `artifacts/reference_predictions.csv` | Casos de referencia usados por testes de contrato e integracao. |

O carregamento dos modelos valida a existencia dos arquivos e compara os hashes
SHA-256 declarados em `metadata.json` antes de desserializar os pipelines.

Arquivos `.joblib` podem executar codigo durante a desserializacao. Nunca
carregue artefatos nao confiaveis, enviados por usuarios ou obtidos de fontes
remotas.

## Testes e checks de qualidade

Execute a suite de testes:

```bash
uv run pytest
```

Execute o lint:

```bash
uv run ruff check .
```

Verifique a formatacao:

```bash
uv run ruff format --check .
```

Para aplicar a formatacao configurada pelo Ruff:

```bash
uv run ruff format .
```

## Visao geral da arquitetura

```text
Streamlit UI
    ↓
Presentation Layer
    ↓
Recommendation Engine
    ↓
Risk Interpreter
    ↓
Decision Policy
    ↓
Prediction Service
    ↓
Input Builder
    ↓
Model Artifacts
```

Principios implementados:

- a UI nao contem regras de negocio;
- as predicoes dos modelos permanecem independentes;
- a classificacao de risco e deterministica;
- cada camada tem uma responsabilidade unica;
- contratos imutaveis atravessam as fronteiras da aplicacao.

## Estrutura do repositorio

```text
.
├── app.py
├── artifacts/
│   ├── decision_tree_pipeline.joblib
│   ├── gradient_boosting_pipeline.joblib
│   ├── metadata.json
│   └── reference_predictions.csv
├── docs/
│   ├── Relatorio.md
│   ├── architecture/
│   ├── features/
│   └── requirements/
├── src/
│   └── churn_app/
│       ├── config.py
│       ├── domain/
│       ├── services/
│       └── ui/
├── tests/
│   ├── integration/
│   └── unit/
├── AGENTS.md
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## Troubleshooting

### `uv` nao esta instalado

Instale o `uv` seguindo a documentacao oficial:
<https://docs.astral.sh/uv/>.

Depois execute novamente:

```bash
uv sync
```

### Artefatos ausentes ou invalidos

Confirme que os arquivos abaixo existem:

- `artifacts/gradient_boosting_pipeline.joblib`;
- `artifacts/decision_tree_pipeline.joblib`;
- `artifacts/metadata.json`;
- `artifacts/reference_predictions.csv`.

Se um hash nao corresponder ao valor declarado em `metadata.json`, a aplicacao
deve falhar em vez de carregar um artefato potencialmente invalido.

### Porta padrao do Streamlit em uso

Se `http://localhost:8501` ja estiver ocupado, execute:

```bash
uv run streamlit run app.py --server.port 8502
```

Depois acesse:

```text
http://localhost:8502
```

### Ambiente virtual inconsistente

Se dependencias parecerem desatualizadas ou inconsistentes, sincronize o
ambiente novamente:

```bash
uv sync
```

## Uso responsavel e escopo academico

Este projeto e uma aplicacao academica de apoio a decisao. O resultado deve ser
interpretado como indicacao analitica de risco, nao como certeza de churn nem
como decisao automatica sobre relacionamento com clientes.

As recomendacoes apresentadas sao orientacoes operacionais deterministicas
baseadas no nivel de risco interpretado. Elas nao substituem analise humana,
politicas internas da instituicao, requisitos regulatorios ou avaliacao
contextual do cliente.

## Documentacao adicional

- Relatorio academico: `docs/Relatorio.md`
- Modelo de autoridade: `docs/architecture/authority-model.md`
- Diagnostico do repositorio: `docs/architecture/repository-diagnosis.md`
- Traceability da implementacao:
  `docs/architecture/implementation-traceability.md`
- ADR de arquitetura: `docs/architecture/adr/ADR-0001.md`
- Especificacao da orquestracao de risco:
  `docs/features/churn-risk-orchestration.md`
- Requisitos funcionais:
  `docs/requirements/functional/churn-decision-support.md`
- Requisitos nao funcionais:
  `docs/requirements/non-functional/application-quality-attributes.md`
- Requisitos nao funcionais da orquestracao:
  `docs/requirements/non-functional/churn-risk-orchestration.md`
- Diretrizes para agentes de codigo: `AGENTS.md`

## Licenca

Este projeto esta licenciado sob a MIT License. Consulte `LICENSE`.
