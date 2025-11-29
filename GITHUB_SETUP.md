# 📤 Instrucciones para Subir a GitHub

## Pasos para subir el proyecto a GitHub

### 1. Inicializar el repositorio Git

```bash
cd /Users/yosvanypachecoviera/Documents/programacion/control_financiero
git init
```

### 2. Agregar todos los archivos

```bash
git add .
```

### 3. Hacer el primer commit

```bash
git commit -m "Initial commit: Control de Meta Neta Diaria para conductores Uber/Lyft"
```

### 4. Crear el repositorio en GitHub

1. Ve a [GitHub.com](https://github.com)
2. Haz clic en el botón "+" en la esquina superior derecha
3. Selecciona "New repository"
4. Nombre del repositorio: `control_financiero` (o el nombre que prefieras)
5. Descripción: "Aplicación web para control financiero diario de conductores Uber/Lyft"
6. **NO** marques "Initialize this repository with a README" (ya tenemos uno)
7. Haz clic en "Create repository"

### 5. Conectar el repositorio local con GitHub

```bash
# Reemplaza TU_USUARIO con tu nombre de usuario de GitHub
git remote add origin https://github.com/TU_USUARIO/control_financiero.git
```

### 6. Subir el código

```bash
git branch -M main
git push -u origin main
```

## Comandos Completos (Copia y Pega)

```bash
cd /Users/yosvanypachecoviera/Documents/programacion/control_financiero

# Inicializar Git
git init

# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit: Control de Meta Neta Diaria para conductores Uber/Lyft"

# Agregar el repositorio remoto (REEMPLAZA TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/control_financiero.git

# Cambiar a rama main
git branch -M main

# Subir a GitHub
git push -u origin main
```

## Notas Importantes

- El archivo `.gitignore` ya está configurado para excluir:
  - La base de datos (`driver_finances.db`)
  - Archivos de Python compilados (`__pycache__`)
  - Archivos del sistema (`.DS_Store`)
  - Configuraciones locales

- Si ya tienes un repositorio en GitHub, puedes usar:
  ```bash
  git remote set-url origin https://github.com/TU_USUARIO/control_financiero.git
  ```

- Para futuros cambios:
  ```bash
  git add .
  git commit -m "Descripción de los cambios"
  git push
  ```

