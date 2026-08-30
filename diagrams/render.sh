#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
image="minlag/mermaid-cli:11.4.2"
names=(request-flow deploy-flow client-provisioning)

for name in "${names[@]}"; do
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    --volume "${repo_root}:/data" \
    "${image}" \
    -i "/data/diagrams/${name}.mmd" \
    -o "/data/diagrams/${name}.svg" \
    -c "/data/diagrams/mermaid-config.json" \
    -b white
done

for name in "${names[@]}"; do
  svg="${repo_root}/diagrams/${name}.svg"
  sed -i \
    -e '1s#>#><title>RaizHost architecture flow</title><desc>Rendered from the adjacent Mermaid source; the embedding page provides a detailed text alternative.</desc><rect width="100%" height="100%" fill="#ffffff"/>#' \
    -e 's#<style xmlns="http://www.w3.org/1999/xhtml">@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css");</style>##' \
    "${svg}"
done

(
  cd "${repo_root}"
  sha256sum \
    diagrams/request-flow.mmd diagrams/request-flow.svg \
    diagrams/deploy-flow.mmd diagrams/deploy-flow.svg \
    diagrams/client-provisioning.mmd diagrams/client-provisioning.svg \
    > diagrams/rendered.sha256
)

python3 "${repo_root}/diagrams/check_docs.py"
