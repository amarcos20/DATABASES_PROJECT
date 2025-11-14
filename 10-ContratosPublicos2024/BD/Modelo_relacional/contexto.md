/* Esquema Relacional - Contratos Públicos
    Representa as 7 tabelas resultantes da decomposição para 3FN.
*/

// --- Tabelas de Entidade (Fortes) ---

// 1. Tabela Principal (inclui FKs de 1:N)
CONTRATOS( idcontrato, dataPublicacao, dataCelebracaoContrato, 
           precoContratual, prazoExecucao, objectoContrato, 
           fundamentacao, ProcedimentoCentralizado, DescrAcordoQuadro?, 
           idAdjudicante -> ADJUDICANTES, 
           cpv -> CPV_CODIGOS ) 

// 2. Tabela de Adjudicantes (Chave: NIF)
ADJUDICANTES( idAdjudicante, nomeAdjudicante )

// 3. Tabela de Adjudicatários (Chave: NIF)
ADJUDICATARIOS( idAdjudicatario, nomeAdjudicatario )

// 4. Tabela de Códigos CPV (Remove dependência transitiva)
CPV_CODIGOS( cpv, descrCPV )

// 5. Tabela de Localizações (Remove campo composto/multivalorado)
LOCALIZACOES( idLocal, Pais, Distrito, Concelho )


// --- Tabelas de Associação (Resolução de M:N) ---
// A Chave Primária é composta pelas duas FKs.

// 6. Contratos e Adjudicatários (M:N)
CONTRATOS_ADJUDICATARIOS( idcontrato -> CONTRATOS, 
                          idAdjudicatario -> ADJUDICATARIOS )

// 7. Contratos e Localizações (M:N)
CONTRATOS_LOCALIZACOES( idcontrato -> CONTRATOS, 
                        idLocal -> LOCALIZACOES )