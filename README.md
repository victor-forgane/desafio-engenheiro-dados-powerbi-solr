## Desafio Técnico — Analista de Dados
### Power BI e Ingestão de Dados no Apache Solr

Este repositório contém a solução para o desafio técnico proposto, dividido em duas partes principais:

- Parte 1: Configuração do ambiente via Docker e desenvolvimento de Dashboard analítico no Power BI
- Parte 2: Formatação de dados e ingestão no Apache Solr utilizando Python

O objetivo do projeto é demonstrar habilidades em análise de dados, visualização, tratamento de dados e integração com sistemas de indexação e busca.

---

## Configuração do Ambiente

### Subir os Serviços com Docker

1. Faça o download do docker
2. Baixe o codigo para seu computador
3. Executar o comando abaixo para subir os serviços necessários (MySQL, phpMyAdmin e Apache Solr):

``` bash
docker-compose up
```


## Parte 1 — Dashboard no Power BI

### Objetivo

Construir um dashboard interativo que permita analisar informações acadêmicas de alunos, incluindo aspectos demográficos, desempenho acadêmico e dados relacionados a matérias e professores.

Os dados são carregados a partir de um banco MySQL inicializado via Docker.

---

### Visões Implementadas

### Demografia dos Alunos
- Distribuição de alunos por gênero
- Distribuição de alunos por bairro
- Distribuição de alunos por idade

### Desempenho Acadêmico
- Média das notas por semestre
- Tabela com alunos e suas médias de notas
- Identificação visual de possíveis outliers de desempenho
- Gráfico Scatter Plot de desvio padrão vs média das notas para identificar a média e a variabilidade das notas dos alunos. 
- Gráfico de setor trazendo a quantidade e a porcentagem de alunos aprovados e reprovados. 

### Matérias e Professores
- Tabela com matérias e respectivos professores responsáveis

### Interatividade
- Filtros por semestre, matéria, gênero e bairro
- Todos os visuais respondem dinamicamente aos filtros aplicados

---

### Tecnologias Utilizadas
- Power BI
- Modelagem relacional
- Medidas DAX
- Filtros e interações entre visuais

---

### Como Visualizar o Dashboard

1. Abrir o arquivo PowerBI/dashboard_escola.pbix
2. Garantir que os serviços Docker estejam em execução
3. Atualizar as conexões de dados, se necessário

---

## Parte 2 — Importação de Dados para o Apache Solr

### Objetivo

Desenvolver um script em Python capaz de:

- Ler um arquivo CSV contendo dados de alunos
- Realizar formatação e padronização dos dados
- Tratar dados inconsistentes ou ausentes
- Inserir os dados formatados no Apache Solr

---

### Tecnologias Utilizadas
- Python 3
- pandas
- pysolr
- Apache Solr
- Docker

---

### Arquivo de Entrada

- aluno.csv: arquivo CSV contendo dados fictícios de alunos de uma escola primária


### Instalação das Dependências Python

Instalar as dependências necessárias com o comando:

py -m pip install -r requirements.txt

---

## Execução do Script de Ingestão

Para executar o processo de formatação e ingestão dos dados no Solr, utilize:

py scripts/ingestao_solr.py

---

## O que o Script Realiza

- Normalização dos nomes das colunas
- Remoção de acentos e padronização de campos textuais
- Conversão de campos numéricos
- Formatação de datas para o padrão ISO 8601 compatível com o Solr
- Criação de identificador determinístico para cada registro
- Envio dos dados ao Solr em lotes
- Commit ao final da ingestão
- Registro de logs informativos e de erro durante o processo

---

## Validação da Ingestão

### Validação via Solr Admin

1. Acessar http://localhost:8983/solr
2. Selecionar o core escola_ubc
3. Verificar o campo numDocs no painel Overview

---

### Validação via Query

Exemplo de consulta para retornar todos os documentos:

q=*:* 

Exemplos adicionais de consulta:

q=nome:Alice  
q=nota_media:[8 TO *]  
q=serie:5  

---

## Considerações Finais

Este projeto simula um fluxo real de análise e ingestão de dados, cobrindo desde a visualização analítica até a indexação em um motor de busca, priorizando qualidade de dados, rastreabilidade via logs e boas práticas de organização e desenvolvimento. O envio dos documentos ao Solr é realizado em lotes configuráveis, garantindo melhor performance e escalabilidade para grandes volumes de dados.

