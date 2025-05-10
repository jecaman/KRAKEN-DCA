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
