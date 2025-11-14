contexto.md
Dependências TransitivasForam removidos atributos que não dependem da chave primária (idcontrato), mas sim de outros atributos não-chave.$CPV(cpv \to descrCPV)$: A descrição do CPV depende do código CPV, não diretamente do contrato. Ao criar a entidade CPV (cpv (PK), descrCPV), removeu-se a dependência transitiva do CONTRATO. ✅ Aprovado.Atributos Compostos/MultivaloradosCampos como adjudicante (NIF+Nome) e localExecucao (vários níveis geográficos/múltiplos locais) foram isolados em entidades próprias.$1^{\text{a}}$ Forma Normal (1FN): A criação das entidades ADJUDICANTE, ADJUDICATARIO e LOCALIZACAO garante que todos os atributos são atómicos (não compostos) e de valor único1111. ✅ Aprovado (1FN).Dependências ParciaisOs atributos não-chave (dataPublicacao, precoContratual, etc.) dependem da chave primária completa (idcontrato).$2^{\text{a}}$ Forma Normal (2FN): Como a chave primária (idcontrato) na tabela principal é simples (não composta), a 2FN está trivialmente satisfeita. ✅ Aprovado (2FN).


CODIGO BDDIA:
/* Modelo ER para Contratos Públicos (3ª Forma Normal)
    Baseado no CSV fornecido e na decomposição para 3FN.
*/

// --- Entidades Fortes ---

// A entidade central, agora sem dados repetidos
CONTRATO( idcontrato, dataPublicacao, dataCelebracaoContrato, 
          precoContratual, prazoExecucao, objectoContrato, 
          fundamentacao, ProcedimentoCentralizado, DescrAcordoQuadro?)

// Entidade para os Códigos de Classificação (CPV)
CPV( cpv, descrCPV)

// Entidade para o Adjudicante (extracção do NIF/Nome)
ADJUDICANTE( idAdjudicante, nomeAdjudicante )

// Entidade para o Adjudicatário (extracção do NIF/Nome)
ADJUDICATARIO( idAdjudicatario, nomeAdjudicatario )


// Entidade para Localizações de Execução (para tratar o campo composto)
// Assumindo idLocal como chave primária composta de Conc+Distrito, ou uma chave sequencial gerada
// LOCALIZACAO(idLocal, Pais, Distrito, Concelho) 
// Simplificando o exemplo de atribuição de chave para um código numérico:
LOCALIZACAO( idLocal, Pais, Distrito, Concelho) 


// --- Relacionamentos e Cardinalidades ---

// 1. Contrato tem 1 Adjudicante (1:1, assumindo que idcontrato->idAdjudicante)
CONTRATO ==1== <TEM_ADJUDICANTE> ==1== ADJUDICANTE

// 2. Contrato usa 1 Código CPV (N:1, um CPV é usado por N contratos)
CONTRATO ==N== <USA_CPV> ==1== CPV

// 3. Contrato tem M Adjudicatários (M:N)
// O relacionamento M:N é tratado por uma tabela de associação
CONTRATO ==M== <TEM_ADJUDICATARIO> ==N== ADJUDICATARIO

// 4. Contrato é executado em M Localizações (M:N)
// O relacionamento M:N é tratado por uma tabela de associação
CONTRATO ==M== <LOCAL_DE_EXECUCAO> ==N== LOCALIZACAO