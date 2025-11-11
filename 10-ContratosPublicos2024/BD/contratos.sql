--
-- Arquivo gerado com SQLiteStudio v3.4.17 em terça nov. 11 11:17:50 2025
--
-- Codificação de texto usada: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tabela: T_ADJUDICANTE
CREATE TABLE IF NOT EXISTS T_ADJUDICANTE (
    idAdjudicante TEXT NOT NULL PRIMARY KEY,
    NomeAdjudicante TEXT NOT NULL
);

-- Tabela: T_ADJUDICATARIO
CREATE TABLE IF NOT EXISTS T_ADJUDICATARIO (
    idAdjudicatario TEXT NOT NULL PRIMARY KEY,
    NomeAdjudicatario TEXT NOT NULL
);

-- Tabela: T_CONTRATO_ADJUDICATARIO
CREATE TABLE IF NOT EXISTS T_CONTRATO_ADJUDICATARIO (
    idcontrato TEXT NOT NULL,
    idAdjudicatario TEXT NOT NULL,

    -- Chave Primária Composta
    PRIMARY KEY (idcontrato, idAdjudicatario),

    FOREIGN KEY (idcontrato) REFERENCES T_FATO_CONTRATO(idcontrato),
    FOREIGN KEY (idAdjudicatario) REFERENCES T_ADJUDICATARIO(idAdjudicatario)
);

-- Tabela: T_CPV
CREATE TABLE IF NOT EXISTS T_CPV (
    CodigoCPV TEXT NOT NULL PRIMARY KEY,
    DescricaoCPV TEXT
);

-- Tabela: T_FATO_CONTRATO
CREATE TABLE IF NOT EXISTS T_FATO_CONTRATO (
    idcontrato TEXT NOT NULL PRIMARY KEY,
    objectoContrato TEXT,
    dataPublicacao TEXT, 
    dataCelebracaoContrato TEXT,
    precoContratual REAL, 
    prazoExecucao INTEGER,
    ProcedimentoCentralizado TEXT,
    DescrAcordoQuadro TEXT,

    -- Chaves Estrangeiras (FKs)
    idAdjudicante_FK TEXT,
    CodigoCPV_FK TEXT,
    idLocalizacao INTEGER,
    idTipoContrato INTEGER,
    idFundamentacao INTEGER,

    -- Definição das Restrições
    FOREIGN KEY (idAdjudicante_FK) REFERENCES T_ADJUDICANTE(idAdjudicante),
    FOREIGN KEY (CodigoCPV_FK) REFERENCES T_CPV(CodigoCPV),
    FOREIGN KEY (idLocalizacao) REFERENCES T_LOCALIZACAO(idLocalizacao),
    FOREIGN KEY (idTipoContrato) REFERENCES T_TIPO_CONTRATO(idTipoContrato),
    FOREIGN KEY (idFundamentacao) REFERENCES T_FUNDAMENTACAO(idFundamentacao)
);

-- Tabela: T_FUNDAMENTACAO
CREATE TABLE IF NOT EXISTS T_FUNDAMENTACAO (
    idFundamentacao TEXT PRIMARY KEY, -- MUDANÇA AQUI: de INTEGER para TEXT
    fundamentacao TEXT NOT NULL
);

-- Tabela: T_LOCALIZACAO
CREATE TABLE IF NOT EXISTS T_LOCALIZACAO (
    idLocalizacao TEXT PRIMARY KEY, -- MUDANÇA AQUI: de INTEGER para TEXT
    Pais TEXT,
    Distrito TEXT,
    Concelho TEXT
);

-- Tabela: T_TIPO_CONTRATO
CREATE TABLE IF NOT EXISTS T_TIPO_CONTRATO (
    idTipoContrato INTEGER PRIMARY KEY,
    tipoContrato TEXT NOT NULL,
    tipoprocedimento TEXT NOT NULL
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
