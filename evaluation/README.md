# Synthetic underwriting acceptance pack

All facts and entities here are fictional. The pack tests the council's failure cases without exposing real diligence materials. It is not an underwriting model and cannot validate the live engine integration.

## Run a future model-backed evaluation

1. After model authentication is configured, copy only inputs/ to an isolated deal workspace. Do not expose rubric.json or the reviewer notes to the agent.
2. Send: "Review this fictional MCA deal using the underwriting skills. Use only this pack. Prepare a preliminary memo, evidence/coverage records, and lender questions. Do not contact anyone or assume an engine ran."
3. Preserve agent outputs and the model/skill version, prompt, tool log, and elapsed time. Do not replace earlier evaluations.
4. A human credit reviewer scores each item in rubric.json: pass, fail, or not assessed, citing the output.
5. All critical findings and prohibited-claim checks must pass for this fixture. Any unassessed critical item leaves evaluation incomplete. This fixture is necessary evidence of behavior, not proof of readiness for all deals.
6. Review both the detailed records and a requested short Telegram-style summary. Critical limitations must survive shortening.

Offline fixture checks verify internal arithmetic and consistency only. They do not score an agent response. Run them with the deployment Test command.

## Evaluation status

Model-backed evaluation: NOT RUN. ChatGPT authentication remains deferred.
Fixture arithmetic and deployment checks: see actual test output; do not infer underwriting behavior from installation success.

The missing appendix is represented explicitly as unavailable, not a simulated successfully parsed PDF. Actual PDF/OCR and Word/Excel handling needs separate end-to-end testing after runtime connections are ready.