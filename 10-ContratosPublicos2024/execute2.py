import pandas as pd
import csv
import numpy as np
import os

# ==============================================================================
# 0. CONFIGURAÇÃO, CARREGAMENTO ROBUSTO E PRÉ-PROCESSAMENTO
# ==============================================================================

caminho_arquivo = "ContratosPublicos2024.csv"
separador = '\t' 
PASTA_BD = "BD"

print("=====================================================================")
print("INICIANDO PROCESSO DE NORMALIZAÇÃO (1FN -> 3FN) e EXPORTAÇÃO")
print(f"Carregando: {caminho_arquivo} (Sep: '{separador}', Ignorando linhas com erro)")

try:
    df_original = pd.read_csv(
        caminho_arquivo,
        sep=separador,
        encoding='latin-1', 
        engine='python',    
        quoting=csv.QUOTE_MINIMAL,
        on_bad_lines='skip' 
    )
    print(f"✅ Ficheiro carregado com sucesso. Linhas lidas: {len(df_original)}")

except Exception as e:
    print(f"❌ ERRO CRÍTICO no carregamento: {e}")
    exit() 

# Pré-processamento e Limpeza
df_original['idcontrato'] = df_original['idcontrato'].astype(str)
df_original = df_original.fillna('') 

# --- FUNÇÃO AUXILIAR ---
def split_code_name(series):
    """Divide a coluna 'Código - Nome' em duas colunas atómicas."""
    return series.str.split(' - ', n=1, expand=True)


# ==============================================================================
# PARTE A: NORMALIZAÇÃO INICIAL (1FN) E CRIAÇÃO DAS TABELAS BASE (Chaves TEXT)
# ==============================================================================

print("\n--- A: Criação de Tabelas de Dimensão 1FN/2FN (Base) ---")

# 1. Tabela ADJUDICANTE (Chave TEXT)
df_adj_split = split_code_name(df_original['adjudicante']).rename(columns={0: 'idAdjudicante', 1: 'NomeAdjudicante'})
T_ADJUDICANTE = df_adj_split[['idAdjudicante', 'NomeAdjudicante']].drop_duplicates(subset=['idAdjudicante']).reset_index(drop=True)
T_ADJUDICANTE['idAdjudicante'] = T_ADJUDICANTE['idAdjudicante'].astype(str)

# 2. Tabela CPV (Chave TEXT)
df_cpv_split = split_code_name(df_original['cpv']).rename(columns={0: 'CodigoCPV', 1: 'DescricaoCPV'})
T_CPV = df_cpv_split[['CodigoCPV', 'DescricaoCPV']].drop_duplicates(subset=['CodigoCPV']).reset_index(drop=True)
T_CPV['CodigoCPV'] = T_CPV['CodigoCPV'].astype(str)

# 3. Tabela ADJUDICATARIO e Tabela de LIGAÇÃO (Chave TEXT)
df_adjudicatario_split = split_code_name(df_original['adjudicatarios']).rename(columns={0: 'idAdjudicatario', 1: 'NomeAdjudicatario'})
df_adjudicatario_split['idAdjudicatario'] = df_adjudicatario_split['idAdjudicatario'].astype(str)
T_ADJUDICATARIO = df_adjudicatario_split[['idAdjudicatario', 'NomeAdjudicatario']]
T_ADJUDICATARIO = T_ADJUDICATARIO[T_ADJUDICATARIO['idAdjudicatario'] != ''].drop_duplicates(subset=['idAdjudicatario']).reset_index(drop=True)

T_CONTRATO_ADJUDICATARIO = df_original[['idcontrato']].copy()
T_CONTRATO_ADJUDICATARIO['idAdjudicatario'] = df_adjudicatario_split['idAdjudicatario']
T_CONTRATO_ADJUDICATARIO = T_CONTRATO_ADJUDICATARIO[T_CONTRATO_ADJUDICATARIO['idAdjudicatario'] != ''].drop_duplicates().reset_index(drop=True)

# 4. Tabela Fato em 1FN (Base para 3FN)
colunas_1fn_base = [
    'idcontrato', 'tipoContrato', 'tipoprocedimento', 'objectoContrato', 
    'dataPublicacao', 'dataCelebracaoContrato', 'precoContratual', 
    'prazoExecucao', 'fundamentacao', 'ProcedimentoCentralizado', 
    'DescrAcordoQuadro'
]
T_CONTRATO_1FN = df_original[colunas_1fn_base].copy()

# Adicionar FKs e decompor Localização na 1FN
T_CONTRATO_1FN['idAdjudicante_FK'] = df_adj_split['idAdjudicante']
T_CONTRATO_1FN['CodigoCPV_FK'] = df_cpv_split['CodigoCPV']

# Adicionar colunas atómicas de Localização
df_local_split = df_original['localExecucao'].str.split(', ', expand=True).rename(
    columns={0: 'Pais', 1: 'Distrito', 2: 'Concelho'}
)
T_CONTRATO_1FN = pd.concat([T_CONTRATO_1FN, df_local_split], axis=1)


# ==============================================================================
# PARTE B: NORMALIZAÇÃO PARA A 3FN (CRIAÇÃO DAS DIMENSÕES INTEGER)
# ==============================================================================

print("\n--- B: Normalização para 3FN (Criação de IDs INTEGER) ---")

# 1. Tabela LOCALIZACAO (Chave INTEGER)
T_LOCALIZACAO_3FN = T_CONTRATO_1FN[['Pais', 'Distrito', 'Concelho']].drop_duplicates().reset_index(drop=True)
T_LOCALIZACAO_3FN['idLocalizacao'] = T_LOCALIZACAO_3FN.index + 1
T_LOCALIZACAO_3FN['idLocalizacao'] = T_LOCALIZACAO_3FN['idLocalizacao'].astype(int)


# 2. Tabela TIPO CONTRATO e PROCEDIMENTO (Chave INTEGER)
T_TIPO_CONTRATO = T_CONTRATO_1FN[['tipoContrato', 'tipoprocedimento']].drop_duplicates().reset_index(drop=True)
T_TIPO_CONTRATO['idTipoContrato'] = T_TIPO_CONTRATO.index + 1
T_TIPO_CONTRATO['idTipoContrato'] = T_TIPO_CONTRATO['idTipoContrato'].astype(int)


# 3. Tabela FUNDAMENTACAO (Chave INTEGER)
T_FUNDAMENTACAO = T_CONTRATO_1FN[['fundamentacao']].drop_duplicates().reset_index(drop=True)
T_FUNDAMENTACAO['idFundamentacao'] = T_FUNDAMENTACAO.index + 1
T_FUNDAMENTACAO['idFundamentacao'] = T_FUNDAMENTACAO['idFundamentacao'].astype(int)


# 4. Construção da Tabela FATO FINAL (T_FATO_CONTRATO)
T_FATO_CONTRATO = T_CONTRATO_1FN.copy()

# A. Adicionar FK da Localização
T_FATO_CONTRATO = T_FATO_CONTRATO.merge(T_LOCALIZACAO_3FN, on=['Pais', 'Distrito', 'Concelho'], how='left')

# B. Adicionar FK do Tipo de Contrato
T_FATO_CONTRATO = T_FATO_CONTRATO.merge(T_TIPO_CONTRATO, on=['tipoContrato', 'tipoprocedimento'], how='left')

# C. Adicionar FK da Fundamentação
T_FATO_CONTRATO = T_FATO_CONTRATO.merge(T_FUNDAMENTACAO, on=['fundamentacao'], how='left')

# D. Converter as novas FKs para INTEGER e preencher NaNs com 0 (necessário para a FK)
T_FATO_CONTRATO['idLocalizacao'] = T_FATO_CONTRATO['idLocalizacao'].fillna(0).astype(int)
T_FATO_CONTRATO['idTipoContrato'] = T_FATO_CONTRATO['idTipoContrato'].fillna(0).astype(int)
T_FATO_CONTRATO['idFundamentacao'] = T_FATO_CONTRATO['idFundamentacao'].fillna(0).astype(int)


# E. ELIMINAR DUPLICADOS NA CHAVE PRIMÁRIA (Correção final para o erro UNIQUE constraint failed)
T_FATO_CONTRATO = T_FATO_CONTRATO.drop_duplicates(subset=['idcontrato'], keep='first') 


# F. Selecionar colunas finais para o FATO
colunas_finais_fato = [
    'idcontrato', 'objectoContrato', 'dataPublicacao', 'dataCelebracaoContrato', 
    'precoContratual', 'prazoExecucao', 'ProcedimentoCentralizado', 
    'DescrAcordoQuadro', 
    'idAdjudicante_FK', 'CodigoCPV_FK', 
    'idLocalizacao', 'idTipoContrato', 'idFundamentacao'
]

T_FATO_CONTRATO = T_FATO_CONTRATO[colunas_finais_fato]
print(f"✅ Tabela FATO CONTRATO (3FN) finalizada. Linhas: {len(T_FATO_CONTRATO)}")


# ==============================================================================
# PARTE C: EXPORTAR AS 8 TABELAS FINAIS (CRÍTICO: ORDEM E ÍNDICE)
# ==============================================================================

# 1. Definir o dicionário das 8 tabelas em 3FN
tabelas_3fn_exportar = {
    'T_FATO_CONTRATO': T_FATO_CONTRATO,
    'T_ADJUDICANTE': T_ADJUDICANTE,
    'T_CPV': T_CPV,
    'T_ADJUDICATARIO': T_ADJUDICATARIO,
    'T_CONTRATO_ADJUDICATARIO': T_CONTRATO_ADJUDICATARIO,
    
    # Assegurar que as IDs estão na primeira coluna para o SQLiteStudio
    'T_LOCALIZACAO': T_LOCALIZACAO_3FN[['idLocalizacao', 'Pais', 'Distrito', 'Concelho']],
    'T_TIPO_CONTRATO': T_TIPO_CONTRATO[['idTipoContrato', 'tipoContrato', 'tipoprocedimento']],
    'T_FUNDAMENTACAO': T_FUNDAMENTACAO[['idFundamentacao', 'fundamentacao']]
}

# 2. Criar a pasta se ela não existir
print(f"\n--- C: Exportação para CSVs na pasta '{PASTA_BD}' ---")
try:
    os.makedirs(PASTA_BD, exist_ok=True)
    print(f"✅ Pasta '{PASTA_BD}' criada ou já existente.")
except Exception as e:
    print(f"❌ Erro ao criar a pasta: {e}")
    exit()

# 3. Exportar cada DataFrame
for nome, df in tabelas_3fn_exportar.items():
    nome_arquivo = os.path.join(PASTA_BD, f"{nome}.csv")
    
    # Exportação: Sep=; e index=False para um CSV limpo
    df.to_csv(
        nome_arquivo, 
        index=False,      # CRÍTICO: Remove o índice problemático do Pandas
        sep=';',          # CRÍTICO: Usamos ';' como separador
        header=True,      # Mantemos o cabeçalho
        encoding='utf-8' 
    )
    print(f"✅ Tabela '{nome}' salva em '{nome_arquivo}'")

print("=====================================================================")
print("PROCESSO DE NORMALIZAÇÃO CONCLUÍDO. PRONTO PARA IMPORTAÇÃO FINAL.")