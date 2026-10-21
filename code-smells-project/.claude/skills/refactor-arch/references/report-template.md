# Audit Report Template
Formato obrigatório do relatório gerado na Fase 02. Deve ter uma linguagem simples e resumida, para que o leitor consiga ler de forma rapida, entendo o problema, seu impacto e como corrigir.

## Template
```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<N> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <titulo anti-pattern>
File: <arquivo>:<linha ou intervalo>
Description: <breve descrição do que o código faz e o problema que gera, máximo de 3 linhas>.
Impact: <breve descrição do impacto gerado pelo código>.
Recommendation: <refatoração sugerida, maximo de 3 linhas>

### [CRITICAL] <próximo finding>
...

### [HIGH] <finding>
...

### [MEDIUM] <finding>
...

### [LOW] <finding>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

# Regras de preenchimento

## File
Deve conter o nome do arquivo seguido da linha/intervalo que se encontra o problema, siga o padrão abaixo:
- Para uma única ocorrência -> `arquivo.py:10`;
- Para um intervalo -> `arquivo.py:10-20`;
- Para multiplas ocorrencias no código -> `arquivo-a.py:2`, `arquivo-b.py:80`, `arquivo-c.py:30`.

## Description
Descrição resumida deixando claro o que o código faz e o problema que gera. Seja especifico e evite ser genérico (como "é ruim" ou "é não recomendado"), explique o por que do apontamento.

## Impact
Descreva o impacto real na aplicação ou para o cliente, seja objetivo e claro no impacto concreto desse apontamento. (máximo de 3 linhas).

## Recommendation
Descreva uma breve recomendação da refatoração sugerida. Leia o `references/refactoring-playbook` e referencie a alteração por lá, se houver. Seja resumido, a ideia é ter apenas uma noção da alteração e não um passo a passo completo nessa secção (por isso a sugestão de referenciar o local no `refactoring-playbook`).

# Orientações
- As secções devem quebrar linha entre elas para melhoras a legibilidade;
- Cada titulo de secção deve estar negrito (ex: **File:**, **Description**).

# Exemplo
```
================================
PHASE 2: ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================
```