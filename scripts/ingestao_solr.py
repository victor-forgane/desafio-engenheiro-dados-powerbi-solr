
import pandas as pd
import pysolr as ps
import logging
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

## Estabelecendo funções

## Função para configurar o log
def setup_logger(level=logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

## Função para remover acentos
def remover_acentos(texto):
    if not isinstance(texto, str):
        return texto
    # Normaliza para a forma NFD (decomposta) e filtra apenas caracteres que não sejam marcas (acentos)
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn')

## Função para alterar o nome das colunas
def change_columns_name(df):
## Como definido no schema --> nome, idade, serie, nota_media, endereco, nome_pai, nome_mae, data_nascimento
    changes_map = {
        "Nome": "nome",
        "Idade": "idade",
        "Série": "serie",
        "Nota Média": "nota_media",
        "Endereço": "endereco",
        "Nome do Pai": "nome_pai",
        "Nome da Mãe": "nome_mae",
        "Data de Nascimento": "data_nascimento",
    }

    return df.rename(columns=changes_map)


## Função para formatar o campo de data
def format_dates(df):

    df = df.copy()
    logger.info("Formatando campos de data")
    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], errors="coerce").dt.strftime("%Y-%m-%dT00:00:00Z")

    return df


## Função para formatar os campos de texto 
def format_text(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    logger.info("Formatando campos de texto")
    df["nome"] = df["nome"].apply(remover_acentos).astype("string").fillna("")
    df["endereco"] = df["endereco"].apply(remover_acentos).astype("string").fillna("")
    df["nome_pai"] = df["nome_pai"].apply(remover_acentos).astype("string").fillna("")
    df["nome_mae"] = df["nome_mae"].apply(remover_acentos).astype("string").fillna("")

    return df

## Função para formatar os campos numéricos
def format_numbers(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    logger.info("Formatando campos numéricos")
    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")
    df["serie"] = pd.to_numeric(df["serie"], errors="coerce")
    df["nota_media"] = pd.to_numeric(df["nota_media"], errors="coerce").round(2)

    return df


## Função para criar o id determinístico
def build_id(df: pd.DataFrame) -> pd.DataFrame:

# Id determinístico: nome + data
    df = df.copy()
    logger.info("Criando id determinístico")
    nome_id = df["nome"].astype(str).str.strip().str.lower().replace(" ","_", regex = False).apply(remover_acentos)
    data_id = df["data_nascimento"].astype(str).str[:10]
    df["id"] = nome_id + "_" + data_id

    return df 

## Função para ingestão de dados no Solr
def send_to_solr(df: pd.DataFrame, solr_url: str, batch_size: int = 500) -> None:
    solr = ps.Solr(solr_url, timeout=10)

    docs = df.to_dict(orient="records")
    total = len(docs)

    logger.info("Enviando %s documentos para o Solr em lotes de %s", total, batch_size)

    for start in range(0, total, batch_size):
        batch = docs[start:start + batch_size]
        try:
            solr.add(batch)
            logger.info("Lote enviado com sucesso: %s-%s", start + 1, min(start + batch_size, total))
        except Exception:
            logger.exception("Falha ao enviar lote: %s-%s", start + 1, min(start + batch_size, total))
            raise

    solr.commit()
    logger.info("Commit realizado. Ingestão concluída.")

## Execução
def main() -> None:

    setup_logger()
    logger.info("Iniciando pipeline de ingestão para o Solr")

    ## variáveis 
    csv_path = Path("aluno.csv")
    solr_url = "http://localhost:8983/solr/escola_ubc"
    df = pd.read_csv(csv_path) ## estabelece o dataframe
    logger.info("CSV carregado | linhas=%s colunas=%s", df.shape[0], df.shape[1])
    logger.info("Colunas originais: %s", list(df.columns))
    df = change_columns_name(df)  
    required = ["nome","idade","serie","nota_media","nome_pai","nome_mae","data_nascimento"]
    missing_report = {c: int(df[c].isna().sum()) for c in required if c in df.columns}
    logger.info("Nulos em campos críticos: %s", missing_report)  
    df = format_dates(df)
    df = format_numbers(df)
    df = format_text(df)
    df = build_id(df)
    dups = int(df["id"].duplicated().sum())
    if dups > 0:
        logger.warning("Encontrados %s IDs duplicados. Isso pode sobrescrever docs no Solr.", dups)
    else:
        logger.info("Não foram encontrados IDs duplicados")
    logger.info("Head do dataframe")
    print(df.head())
    send_to_solr(df, solr_url, batch_size=500)

if __name__ == "__main__":
    main()
