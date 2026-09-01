# Debug Session: config-fetch-error
- **Status**: [OPEN]
- **Issue**: Na tela de configuração, ao clicar em "Analisar e preparar estudo", o frontend mostra `Edital: Failed to fetch | Banca: Failed to fetch | Prova: Failed to fetch` e o DevTools mostra erro de CORS em chamadas para `127.0.0.1:8002`.
- **Debug Server**: Pending
- **Log File**: .dbg/trae-debug-log-config-fetch-error.ndjson

## Reproduction Steps
1. Abrir `http://localhost:5173/config`
2. Fazer login
3. Informar edital, banca opcional e prova de referência
4. Clicar em `Analisar e preparar estudo`
5. Observar `Failed to fetch` no frontend e mensagens de CORS/500 no DevTools

## Hypotheses & Verification
| ID | Hypothesis | Likelihood | Effort | Evidence |
|----|------------|------------|--------|----------|
| A | O backend responde 500 nos endpoints de análise e a resposta de erro chega sem cabeçalho CORS, sendo mascarada no navegador como `Failed to fetch`. | High | Low | Pending |
| B | Há inconsistência entre `localhost` e `127.0.0.1` nas origens/URL da API, causando preflight ou validação de origem incorreta. | High | Low | Pending |
| C | Um erro interno específico de parsing de PDF/texto/agent está quebrando os endpoints `/analyze/*`. | Medium | Medium | Pending |
| D | O processo backend ativo não corresponde ao código atual ou não leu o `.env` esperado. | Medium | Medium | Pending |
| E | O token do frontend está expirado/inválido e parte das falhas está sendo reportada junto com 500/CORS. | Medium | Low | Pending |

## Log Evidence
- `.dbg/trae-debug-log-config-fetch-error.ndjson` mostra `POST /auth/login` com `200`.
- Depois mostra `POST /analyze/banca` com entrada válida e `has_content: true`.
- Em seguida, o middleware registra exceção `ResponseValidationError`.
- A mensagem interna da exceção contém erro Gemini `429 RESOURCE_EXHAUSTED` / `quota exceeded`.
- Isso prova que a API de IA respondeu erro em formato texto/JSON cru e o backend tentou serializar isso como `AnaliseBanca`, produzindo `500`.
- Após o ajuste, uma chamada autenticada para `/analyze/banca` passou a responder `429` e incluir `access-control-allow-origin` nos headers.

## Verification Conclusion
| ID | Hypothesis | Status | Evidence Summary |
|----|------------|--------|------------------|
| A | O backend responde 500 nos endpoints de análise e a resposta de erro chega sem cabeçalho CORS, sendo mascarada no navegador como `Failed to fetch`. | ✅ Confirmed | O log mostra `ResponseValidationError` no backend após erro Gemini; no navegador isso aparece como CORS/failed fetch. |
| B | Há inconsistência entre `localhost` e `127.0.0.1` nas origens/URL da API, causando preflight ou validação de origem incorreta. | ❌ Rejected | A reprodução direta sem navegador também falhou com `500`; logo a origem não é a causa raiz. |
| C | Um erro interno específico de parsing de PDF/texto/agent está quebrando os endpoints `/analyze/*`. | ✅ Confirmed | O agent retorna payload de erro Gemini/quota e o backend quebra ao validar o response model. |
| D | O processo backend ativo não corresponde ao código atual ou não leu o `.env` esperado. | ❌ Rejected | Os logs novos de instrumentação estão sendo emitidos pelo processo ativo. |
| E | O token do frontend está expirado/inválido e parte das falhas está sendo reportada junto com 500/CORS. | ❌ Rejected | A reprodução com login novo passou no `/auth/login` e chegou autenticada em `/analyze/banca`. |

### Pre-fix vs Post-fix
- **Pre-fix**: `/analyze/banca` -> erro Gemini 429 interno -> `ResponseValidationError` no FastAPI -> resposta final `500` -> navegador mostrava `Failed to fetch` / falso CORS.
- **Post-fix**: `/analyze/banca` -> erro Gemini 429 interno -> API converte para `HTTPException 429` com mensagem amigável -> resposta inclui CORS -> frontend consegue mostrar erro real.
