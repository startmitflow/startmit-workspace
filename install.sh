#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills/here-now"
SCRIPTS_DIR="${SKILL_DIR}/scripts"
REFS_DIR="${SKILL_DIR}/references"
BIN_DIR="${SKILL_DIR}/bin"
REPO_BASE="https://raw.githubusercontent.com/heredotnow/skill/main/here-now"
JQ_VERSION="1.8.1"
JQ_BASE_URL="https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}"

die() {
  echo "error: $1" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "requires $1"
}

detect_platform() {
  local os arch jq_asset expected_sha

  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"

  case "$os" in
    darwin) ;;
    linux) ;;
    *) die "unsupported OS: ${os}" ;;
  esac

  case "$os/$arch" in
    darwin/arm64)
      jq_asset="jq-macos-arm64"
      expected_sha="a9fe3ea2f86dfc72f6728417521ec9067b343277152b114f4e98d8cb0e263603"
      ;;
    darwin/x86_64)
      jq_asset="jq-macos-amd64"
      expected_sha="e80dbe0d2a2597e3c11c404f03337b981d74b4a8504b70586c354b7697a7c27f"
      ;;
    linux/x86_64)
      jq_asset="jq-linux-amd64"
      expected_sha="020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d"
      ;;
    linux/aarch64|linux/arm64)
      jq_asset="jq-linux-arm64"
      expected_sha="6bc62f25981328edd3cfcfe6fe51b073f2d7e7710d7ef7fcdac28d4e384fc3d4"
      ;;
    *)
      die "unsupported architecture: ${os}/${arch}"
      ;;
  esac

  echo "${jq_asset}|${expected_sha}"
}

sha256_file() {
  local path="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$path" | awk '{print $1}'
    return
  fi
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$path" | awk '{print $1}'
    return
  fi
  if command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$path" | awk '{print $2}'
    return
  fi
  die "no SHA-256 tool found (need sha256sum, shasum, or openssl)"
}

atomic_download() {
  local url="$1"
  local destination="$2"
  local tmp

  tmp="$(mktemp "${destination}.tmp.XXXXXX")"
  curl -fsSL "$url" -o "$tmp"
  mv "$tmp" "$destination"
}

echo "Installing here.now skill..."

need_cmd curl
need_cmd uname
need_cmd mktemp
need_cmd mv
need_cmd chmod

mkdir -p "$SCRIPTS_DIR" "$REFS_DIR" "$BIN_DIR"

atomic_download "${REPO_BASE}/SKILL.md" "$SKILL_DIR/SKILL.md"
atomic_download "${REPO_BASE}/scripts/publish.sh" "$SCRIPTS_DIR/publish.sh"
atomic_download "${REPO_BASE}/references/REFERENCE.md" "$REFS_DIR/REFERENCE.md"

platform="$(detect_platform)"
jq_asset="${platform%|*}"
expected_sha="${platform#*|}"
jq_url="${JQ_BASE_URL}/${jq_asset}"
jq_path="${BIN_DIR}/jq"

atomic_download "$jq_url" "$jq_path"
actual_sha="$(sha256_file "$jq_path")"
if [[ "$actual_sha" != "$expected_sha" ]]; then
  rm -f "$jq_path"
  die "jq checksum mismatch (expected ${expected_sha}, got ${actual_sha})"
fi

chmod +x "$SCRIPTS_DIR/publish.sh" "$jq_path"

echo ""
echo "done - here.now skill installed to ${SKILL_DIR}"
echo "restart Claude Code/Cowork to start using it"
