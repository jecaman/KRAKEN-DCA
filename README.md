# 🤖 Kraken DCA Bot

Este es un bot simple en Python para realizar compras periódicas (estrategia DCA - Dollar Cost Averaging) en **Kraken**, con notificación por correo electrónico una vez completada la orden.

---

## ⚠️ Advertencia de seguridad

> **Este script puede ejecutar órdenes reales de compra en Kraken.**  
> Antes de ejecutarlo, revisa cuidadosamente el archivo `.env` y asegúrate de que `EXECUTE_BOT=false` si solo quieres probarlo en modo seguro.  
> **No compartas tu archivo `.env` real. Usa el `.env.example` incluido como plantilla.**

---

## 🛠 Requisitos

- Python 3.8+
- Cuenta en Kraken con API habilitada
- Cuenta Gmail (recomendado con contraseña de aplicación)
- `.env` con tus credenciales

---

## 🚀 Uso

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tuusuario/nombre-repo.git
   cd nombre-repo
   
2. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt

3. Copia el archivo de entorno de ejemplo y edítalo:

   ```bash
   cp .env.example .env

4. Rellena .env con tus credenciales reales.

5. Ejecuta el bot:

   ```bash
   python dca_bot.py

## 🔧 Configuración
EXECUTE_BOT=true: activa el bot (¡realiza compras reales!).
EXECUTE_BOT=false: modo seguro, el bot no se ejecutará.
to_invest: definido directamente en el script (20.83 EUR) → puedes modificarlo.

## 📬 Notificación
Recibirás un correo con los detalles de la orden (o del error) cada vez que se intente una compra.
La notificación se envía desde tu cuenta Gmail a la dirección configurada en .env.

## ✅ Estado
Este script es funcional y ha sido probado con dinero real, pero no se ofrece soporte ni garantía.
Úsalo bajo tu propia responsabilidad.

