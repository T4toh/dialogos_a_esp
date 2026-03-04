# Guía de Contribución

## Workflow de releases

> ⚠️ **Regla fundamental:** cada vez que mergeas algo a `main` que va a publicarse, **hay que bumpear la versión**. Si no, el AppImage nuevo se publica con la versión vieja adentro y los usuarios que actualicen seguirán viendo el número anterior.

### Pasos para publicar una nueva versión

1. **Bumpear la versión** en `src/__init__.py`:
   ```python
   __version__ = "2.1.X"  # incrementar X (o minor/major según el cambio)
   ```

2. **Actualizar `CHANGELOG.md`** con los cambios de la versión.

3. **Commit y merge a `main`**:
   ```bash
   git add src/__init__.py CHANGELOG.md
   git commit -m "chore: bump version to 2.1.X"
   ```

4. **Crear el tag** desde `main` (esto dispara el CI):
   ```bash
   git tag v2.1.X
   git push origin v2.1.X
   ```

5. El workflow `.github/workflows/release.yml` detecta el tag `v*.*.*`, construye el AppImage y lo publica en GitHub Releases automáticamente.

### Cómo funciona el auto-update

- La app compara `src.__version__` (hardcodeado en el binario) contra el tag más reciente en GitHub Releases.
- Si el tag es mayor, ofrece actualizar.
- La actualización descarga el nuevo AppImage y reemplaza el archivo en disco.
- El usuario reinicia manualmente.

**Si no bumpeás la versión:**
- El AppImage nuevo se instala en disco correctamente.
- Pero al reiniciar, la app muestra el número viejo (porque está hardcodeado en el binario).
- El usuario cree que la actualización no funcionó.
- Además, el check de updates sigue ofreciendo "actualizar" al mismo binario en loop.

### Esquema de versiones

`MAJOR.MINOR.PATCH`

| Tipo de cambio | Qué incrementar |
|---|---|
| Bug fix, mejora menor | `PATCH` (2.1.3 → 2.1.4) |
| Feature nueva, cambio de UI | `MINOR` (2.1.x → 2.2.0) |
| Cambio que rompe compatibilidad | `MAJOR` (2.x.x → 3.0.0) |

### Ramas y PRs

- Trabajá en ramas (`fix/algo`, `feat/algo`)
- Abrí un PR hacia `main`
- **Incluí el bump de versión en el mismo PR** (o en un commit de chore antes del tag)
- No crees el tag hasta que el PR esté mergeado en `main`
