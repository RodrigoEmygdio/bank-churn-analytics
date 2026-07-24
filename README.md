# Bank Churn Analytics

Aplicacao academica de Machine Learning para apoio a analise de risco de churn de clientes bancarios.

Este repositorio combina a documentacao cientifica do projeto com uma aplicacao Streamlit planejada para executar dois pipelines treinados de scikit-learn:

- Gradient Boosting: modelo primario, selecionado pelo melhor equilibrio geral de desempenho.
- Decision Tree: modelo complementar de sensibilidade, utilizado para expor casos adicionais de risco e divergencias entre classificadores.

O arquivo `AGENTS.md` e a fonte de verdade para as regras de implementacao, arquitetura, validacao, testes e seguranca do projeto.

## Objetivo do Projeto

Construir uma aplicacao Streamlit confiavel e explicavel que:

- colete atributos de clientes;
- valide os dados informados;
- derive internamente a feature `ProductsGroup`;
- execute os dois pipelines treinados;
- apresente as predicoes de cada modelo separadamente;
- consolide os resultados na politica de risco definida;
- comunique recomendacoes operacionais sem tratar a predicao como uma decisao deterministica.

## Politica de Risco

A aplicacao deve preservar as saidas individuais dos modelos e aplicar a politica abaixo:

| Gradient Boosting | Decision Tree | Nivel de risco |
|-------------------|---------------|----------------|
| 0                 | 0             | LOW            |
| 0                 | 1             | ATTENTION      |
| 1                 | 0             | HIGH           |
| 1                 | 1             | CRITICAL       |

Nao deve ser usada uma regra binaria simples por OR, votacao majoritaria, media de probabilidades ou probabilidade combinada inventada.

## Estrutura Aprovada

```text
churn-prediction-app/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock
├── app.py
│
├── artifacts/
│   ├── gradient_boosting_pipeline.joblib
│   ├── decision_tree_pipeline.joblib
│   ├── metadata.json
│   └── reference_predictions.csv
│
├── src/
│   └── churn_app/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── customer.py
│       │   ├── prediction.py
│       │   └── risk_level.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── artifact_loader.py
│       │   ├── input_builder.py
│       │   ├── prediction_service.py
│       │   └── decision_policy.py
│       └── ui/
│           ├── __init__.py
│           ├── form.py
│           └── result.py
│
└── tests/
    ├── unit/
    │   ├── test_input_builder.py
    │   └── test_decision_policy.py
    └── integration/
        ├── test_artifact_loading.py
        └── test_reference_predictions.py
```

Esta estrutura ainda nao representa codigo implementado. Ela define a organizacao aprovada para a aplicacao Streamlit que sera desenvolvida a partir dos artefatos ja exportados.

## Artefatos de Modelo

Os artefatos autoritativos ficam em `artifacts/`:

- `metadata.json`: nomes dos artefatos, versoes, schema esperado, classe positiva, politica de decisao, metricas e hashes.
- `gradient_boosting_pipeline.joblib`: pipeline completo do modelo Gradient Boosting.
- `decision_tree_pipeline.joblib`: pipeline completo do modelo Decision Tree.
- `reference_predictions.csv`: casos de referencia para testes de integracao.

Os pipelines serializados devem ser carregados como pipelines completos. O preprocessamento interno dos modelos nao deve ser reimplementado manualmente.

## Evidencia de Treinamento

A validacao de categorias deve usar as categorias observadas durante o treinamento:

- `Geography`: `France`, `Germany`, `Spain`
- `Gender`: `Female`, `Male`
- `ProductsGroup`: `1`, `2`, `3+`

A feature `ProductsGroup` deve ser derivada internamente de `NumOfProducts`, conforme a transformacao usada no treinamento:

- `1` -> `1`
- `2` -> `2`
- `3` ou `4` -> `3+`

O usuario nao deve informar `ProductsGroup` diretamente.

## Dependencias

O projeto usa `uv` e `pyproject.toml`.

As dependencias de pesquisa e notebooks permanecem no projeto. A aplicacao Streamlit e os checks de desenvolvimento adicionam dependencias especificas para execucao, testes e linting.

Comandos esperados:

```bash
uv sync
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Documentacao Academica

A documentacao cientifica do projeto esta em `docs/`, em portugues, para revisao academica pela PUC Minas.
