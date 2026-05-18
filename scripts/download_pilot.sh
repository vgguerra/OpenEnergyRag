#!/usr/bin/env bash
# Downloads the pilot corpus into data/raw/.
# Idempotent: skips files that already exist locally.
# Run from repo root:  bash scripts/download_pilot.sh
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data/raw

ANEEL_BASE="https://git.aneel.gov.br/publico/centralconteudo/-/raw/main/procreg/prodist"
ONS_BASE="https://www.ons.org.br/ProcedimentosDeRede"

# Each line: "<destination filename> <source URL>"
docs=(
  "prodist-modulo-01-glossario.pdf $ANEEL_BASE/modulo01/aren20251137_Prodist_modulo_1_v12.pdf"
  "prodist-modulo-02-planejamento.pdf $ANEEL_BASE/modulo02/aren2021956_Prodist_modulo_2_v8.pdf"
  "prodist-modulo-03-conexao.pdf $ANEEL_BASE/modulo03/aren2021956_Prodist_modulo_3_v8.pdf"
  "prodist-modulo-04-operativos.pdf $ANEEL_BASE/modulo04/aren20251137_Prodist_modulo_4_v3.pdf"
  "prodist-modulo-05-medicao.pdf $ANEEL_BASE/modulo05/aren2021956_Prodist_modulo_5_v7.pdf"
  "prodist-modulo-06-informacoes.pdf $ANEEL_BASE/modulo06/aren20251137_Prodist_modulo_6_v17.pdf"
  "prodist-modulo-07-perdas.pdf $ANEEL_BASE/modulo07/aren2021956_Prodist_modulo_7_v6.pdf"
  "prodist-modulo-08-qualidade.pdf $ANEEL_BASE/modulo08/aren20251137_Prodist_modulo_8_v14.pdf"
  "prodist-modulo-09-ressarcimento.pdf $ANEEL_BASE/modulo09/aren2021956_Prodist_modulo_9_v2.pdf"
  "prodist-modulo-10-sig.pdf $ANEEL_BASE/modulo10/aren2021956_Prodist_modulo_10_v4.pdf"
  "prodist-modulo-11-fatura.pdf $ANEEL_BASE/modulo11/aren2021956_Prodist_modulo_11_v2.pdf"
  "ons-submodulo-1.1-introducao.pdf $ONS_BASE/M%C3%B3dulo%201/Subm%C3%B3dulo%201.1/Subm%C3%B3dulo%201.1_Rev_1.0.pdf"
)

ok=0
skipped=0
failed=0

for entry in "${docs[@]}"; do
  filename="${entry%% *}"
  url="${entry#* }"
  dest="data/raw/$filename"

  if [[ -s "$dest" ]]; then
    echo "skip   $filename (already present)"
    skipped=$((skipped + 1))
    continue
  fi

  echo "fetch  $filename"
  # --insecure: the WSL CA bundle does not include the issuer chain that
  # git.aneel.gov.br uses. Sources here are public regulatory PDFs from
  # known government domains, so the verification cost outweighs the benefit
  # for a research pilot.
  if curl --fail --silent --show-error --location --insecure \
       --user-agent "open-energy-rag/0.1 (pilot)" \
       --output "$dest" "$url"; then
    ok=$((ok + 1))
  else
    echo "  FAILED: $url" >&2
    rm -f "$dest"
    failed=$((failed + 1))
  fi
done

echo
echo "done: downloaded=$ok skipped=$skipped failed=$failed"
ls -lh data/raw/ | tail -n +2
