#!/usr/bin/env bash
# verificar-url-sembrada.sh — corre la prueba de la URL sembrada contra CADA revisor del curso.
#
# Por qué existe: el revisor lee direcciones de servicios.toml y las devolvía enteras en el
# reporte JSON. Si una dirección trae usuario y clave, o un token en la consulta, el secreto
# salía en el reporte. La regla del curso: una URL con usuario o clave se rechaza al cargar, y
# ningún reporte, error ni registro repite la URL completa (el JSON la lleva redactada).
# La prueba es herramientas/url-sembrada.py.
#
# Es OBLIGATORIA y FALLA CERRADO: sale con 1 si la prueba no existe, si un revisor sale en rojo,
# o si encontró menos revisores de los que el curso tiene (uno por lección, de la 6 a la 11:
# desde la 6 el revisor lee servicios.toml): una prueba que no corrió no es un verde.
# Arma su propio entorno virtual en una carpeta temporal y lo borra al terminar; necesita red
# para instalar las versiones fijadas de herramientas/requisitos.txt y hatchling.
# Uso: herramientas/verificar-url-sembrada.sh   (desde cualquier carpeta; PYTHON=python3.12 para otra versión)
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
PRUEBA=herramientas/url-sembrada.py
ESPERADOS=6
PY="${PYTHON:-python3}"

if [ ! -f "$PRUEBA" ]; then echo "❌ falta $PRUEBA: la prueba de la URL sembrada es obligatoria"; exit 1; fi

TEMPORAL="$(mktemp -d)"
trap 'rm -rf "$TEMPORAL"' EXIT
"$PY" -m venv "$TEMPORAL/venv" || { echo "❌ no pude crear el entorno virtual"; exit 1; }
VPY="$TEMPORAL/venv/bin/python"
"$VPY" -m pip install --quiet --disable-pip-version-check -r herramientas/requisitos.txt hatchling \
  || { echo "❌ no pude instalar las herramientas del curso"; exit 1; }
echo "Python: $("$VPY" --version)"

corridas=0
rojas=0
for carpeta in programas/06-*/fig06_18 programas/07-*/fig07_01 programas/08-*/fig08_15 \
               programas/09-*/fig09_11 programas/10-*/fig10_08 programas/11-*/fig11_05; do
  leccion="$(basename "$(dirname "$carpeta")" | cut -c1-2)"
  leccion=$((10#$leccion))
  if [ "$leccion" -eq 6 ]; then
    [ -f "$carpeta/configuracion.py" ] || { echo "❌ no encontré el revisor de la lección 6 en $carpeta"; rojas=$((rojas + 1)); continue; }
  else
    [ -f "$carpeta/pyproject.toml" ] || { echo "❌ no encontré el revisor de la lección $leccion en $carpeta"; rojas=$((rojas + 1)); continue; }
    "$VPY" -m pip install --quiet --disable-pip-version-check --no-deps --no-build-isolation --force-reinstall "$carpeta" \
      || { echo "❌ no pude instalar el revisor de la lección $leccion"; rojas=$((rojas + 1)); continue; }
  fi
  corridas=$((corridas + 1))
  "$VPY" "$PRUEBA" "$carpeta" "$leccion" || rojas=$((rojas + 1))
done

if [ "$corridas" -ne "$ESPERADOS" ]; then
  echo "❌ corrí la prueba en $corridas revisores, y el curso tiene $ESPERADOS"
  exit 1
fi
if [ "$rojas" -ne 0 ]; then
  echo "❌ $rojas de $corridas revisores aceptan una URL con usuario o clave, o repiten sus secretos"
  exit 1
fi
echo "✅ URL sembrada: $corridas de $corridas revisores la rechazan y no repiten sus secretos"
