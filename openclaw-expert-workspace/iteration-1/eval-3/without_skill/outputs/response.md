# Debugando Webhooks no OpenClaw que Não Estão Disparando

Se seu webhook no OpenClaw não está disparando apesar de estar aparentemente configurado corretamente, aqui estão os passos iniciais de debug:

## 1. Verifique a Configuração Básica do Webhook
- **URL do Webhook**: Confirme que a URL está correta, acessível e usando HTTPS
- **Eventos Subscritos**: Verifique quais eventos estão configurados para disparar o webhook
- **Autenticação**: Se o webhook requer autenticação, confirme que as credenciais estão corretas
- **Headers Customizados**: Se houver headers customizados configurados, valide se estão no formato correto

## 2. Verifique se os Eventos Realmente Acontecem
- Confirme que os eventos que deveriam disparar o webhook estão realmente ocorrendo no OpenClaw
- Consulte os logs de eventos ou atividades no painel do OpenClaw para verificar se há registro dos eventos esperados
- Teste manualmente uma ação que deveria gerar um evento para ver se ele é registrado

## 3. Inspecione o Status e Logs do Webhook
- Acesse os logs de webhook no OpenClaw (geralmente há uma seção dedicada)
- Procure por tentativas de disparo que falharam - isso pode revelar erros específicos
- Verifique o status do webhook (ativo/inativo, últimas tentativas, taxa de sucesso)

## 4. Teste a Conectividade
- Verifique se sua URL é acessível externamente (a partir de onde OpenClaw está hospedado)
- Teste se há firewall, WAF ou restrições de IP bloqueando requisições do OpenClaw
- Confirme que a URL responde corretamente em GET/POST (o método esperado)
- Teste usando curl ou Postman para enviar uma requisição manual similar à que o webhook deveria enviar

## 5. Verifique a Resposta do Seu Endpoint
- Seu endpoint deve responder com status 2xx para que o webhook seja considerado bem-sucedido
- Se retornar 4xx ou 5xx, o OpenClaw pode estar registrando falhas
- Valide que seu servidor está respondendo rapidamente (timeouts podem causar falhas)

## 6. Considere Limitações de Entrega
- Verifique se há throttling ou rate limiting ativo no webhook
- Alguns webhooks têm limites de tentativas de retentativa
- Confirme se há período de carência entre configuração e primeiro disparo

## 7. Teste com Ferramentas Externas
- Use um serviço como webhook.site para criar um endpoint de teste temporário
- Configure o webhook do OpenClaw para apontar para esse endpoint
- Dispare um evento e veja se a requisição chega
- Analise o payload recebido para entender o formato dos dados

## 8. Revise a Documentação
- Consulte a documentação oficial do OpenClaw para webhooks
- Procure por requisitos específicos de formato de resposta
- Verifique se há versão mínima do OpenClaw necessária para certos tipos de eventos

## Dicas Adicionais
- Se usar um servidor local, certifique-se de que está acessível à internet (use ngrok ou similar para tunelamento)
- Alguns eventos podem ter atrasos antes do disparo
- Se mudar a URL do webhook, pode ser necessário reativar ou reconfigurá-lo
- Mantenha registros detalhados (logs) no seu endpoint para rastrear todas as requisições recebidas

Se após seguir esses passos o webhook ainda não funcionar, consulte os logs específicos do OpenClaw ou entre em contato com o suporte técnico fornecendo as informações coletadas durante a investigação.
