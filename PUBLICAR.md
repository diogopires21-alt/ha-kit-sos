# Publicação e novas versões do Kit SOS

Repositório: https://github.com/diogopires21-alt/ha-kit-sos

## Como os outros instalam

Em **Definições → Apps → Instalar app → ⋮ → Repositórios**, adicionar `https://github.com/diogopires21-alt/ha-kit-sos` (ou usar o botão do README) e instalar o **Kit SOS**.

O Marketplace do Home Assistant (ex-HACS, desde a 2026.11) não instala apps, só integrações, cartões, temas e modelos. Por isso a app é distribuída por este repositório de apps.

## Como funciona a publicação

Cada vez que há um commit em `main` que mexe em `kit_sos/config.yaml`, `kit_sos/Dockerfile` ou na app, o GitHub Actions:

1. corre os testes (`Tests`);
2. compila a app para Raspberry Pi (aarch64) e PC (amd64) e publica a imagem `ghcr.io/diogopires21-alt/kit-sos` com a versão do `config.yaml` (`Builder`).

A imagem tem de estar **pública** (GitHub → perfil → Packages → kit-sos → Package settings → Change visibility → Public). Só é preciso fazer isto uma vez.

## Nova versão

1. Fazer as alterações.
2. Subir `version:` em `kit_sos/config.yaml` (ex.: `"1.0.1"`) e acrescentar a entrada no `kit_sos/CHANGELOG.md`.
3. Commit em `main`. Quem tem a app instalada vê a atualização em Definições → Atualizações quando a compilação terminar.
4. Se a versão obrigar a algo manual (ex.: opções novas obrigatórias), acrescentar a versão em `breaking_versions:` no `config.yaml` para não atualizar sozinha.

Nunca publicar duas imagens diferentes com o mesmo número de versão.

## Instalação local (desenvolvimento)

Para testar uma alteração no próprio Pi antes de publicar: copiar a pasta `kit_sos` para `/addons/kit_sos` e **apagar a linha `image:`** do `config.yaml` dessa cópia. Assim o Home Assistant compila a app localmente em vez de descarregar a imagem.
