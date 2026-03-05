#!/usr/bin/env bash
set -euo pipefail

#
# Prosty skrypt release:
# - podbija numer wersji (domyślnie PATCH)
# - buduje projekt (CMake, Release)
# - taguje w git i wypycha na origin
# - GitHub Actions buduje AppImage / exe na podstawie taga
#

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Ten katalog nie jest repozytorium git."
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Masz niezacommitowane zmiany. Zacommituj je przed uruchomieniem release."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Brak zdefiniowanego remote 'origin'. Skonfiguruj repo GitHub."
  exit 1
fi

if [[ ! -f VERSION ]]; then
  echo "Brak pliku VERSION."
  exit 1
fi

CURRENT_VERSION="$(tr -d ' \n\r' < VERSION)"
if [[ ! "$CURRENT_VERSION" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  echo "Nieprawidłowy format wersji w pliku VERSION: '$CURRENT_VERSION' (oczekiwane: X.Y.Z)"
  exit 1
fi

MAJOR="${BASH_REMATCH[1]}"
MINOR="${BASH_REMATCH[2]}"
PATCH="${BASH_REMATCH[3]}"

BUMP_KIND="patch"
if [[ "${1-}" == "--major" ]]; then
  BUMP_KIND="major"
elif [[ "${1-}" == "--minor" ]]; then
  BUMP_KIND="minor"
fi

case "$BUMP_KIND" in
  major)
    ((MAJOR++))
    MINOR=0
    PATCH=0
    ;;
  minor)
    ((MINOR++))
    PATCH=0
    ;;
  patch)
    ((PATCH++))
    ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
TAG_NAME="v${NEW_VERSION}"

echo "Aktualna wersja: ${CURRENT_VERSION}"
echo "Nowa wersja:     ${NEW_VERSION}"

if git rev-parse "refs/tags/${TAG_NAME}" >/dev/null 2>&1; then
  echo "Tag ${TAG_NAME} już istnieje. Przerwano."
  exit 1
fi

echo "${NEW_VERSION}" > VERSION

echo "==> Budowanie w trybie Release..."
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

echo "==> Tworzenie commita i taga..."
git add VERSION
git commit -m "Release ${TAG_NAME}"
git tag "${TAG_NAME}"

echo "==> Wypychanie na origin..."
git push origin HEAD
git push origin "${TAG_NAME}"

echo
echo "Release ${TAG_NAME} utworzony i wypchnięty."
echo "GitHub Actions zbuduje AppImage / exe na podstawie tego taga."

