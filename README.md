# 🏎️ Cuadro Digital OBD - Telemetría de Competición 🏁

¡Lleva el rendimiento de tu motor al siguiente nivel! **Cuadro Digital OBD** es una central de instrumentación profesional diseñada para entusiastas del motor que buscan datos precisos y una estética agresiva de carreras en tiempo real. 

Específicamente optimizado para el motor **1.6 HDI**, este software transforma tu PC o Tablet en un clúster digital de alto rendimiento.

---

## 🚀 Características Principales

*   **📊 Dashboard Deportivo**: Interfaz de alto contraste en Negro y Rojo diseñada para una legibilidad instantánea en condiciones de conducción exigentes.
*   **🐎 Física Real (CV & Nm)**: Olvida las tablas fijas. Calculamos la potencia y el par motor basándonos en los sensores **MAF** y **MAP** mediante fórmulas físicas reales.
*   **🌀 Monitor de Turbo**: Visualización de la presión del turbo restando la presión atmosférica para obtener el soplado real.
*   **⏱️ Sección de ACELERACIÓN**:
    *   **Modo Automático**: Empieza a contar en cuanto el coche se mueve.
    *   **Modo Manual**: Botón de inicio de gran formato.
    *   **Historial**: Guarda tus últimos 5 mejores tiempos de 0-100 km/h de forma persistente.
*   **📈 Gráficas de Rendimiento**: Tres gráficas independientes en tiempo real para Turbo, CV y Par Motor.
*   **🛠️ Diagnóstico DTC**: Lee y borra códigos de error de la ECU directamente desde la app.
*   **🌓 Modo Día/Noche**: Alterna entre un esquema de color claro para el sol y uno oscuro para la noche con un solo toque.

---

## 🔌 Hardware Necesario

Para utilizar esta aplicación, necesitas:

1.  **Adaptador ELM327 OBD-II Bluetooth**: El estándar para comunicaciones con el vehículo.
2.  **Conexión**:
    *   Localiza el puerto OBD-II de tu coche (normalmente bajo el volante o en la consola central).
    *   Conecta el adaptador y emparéjalo por Bluetooth con tu ordenador.

---

## 🛠️ Instalación y Requisitos

**Requisito de Sistema:** Python 3.12+

Instala las librerías necesarias con el siguiente comando:

```bash
pip install kivy obd numpy
```

*(Nota: La aplicación utiliza `obd.Async` para garantizar que la interfaz nunca se bloquee).*

---

## ⚙️ Configuración Especial (1.6 HDI)

Este proyecto está pre-configurado y optimizado para un motor **1.6 HDI 90cv** con reprogramación **Stage 1 (~100cv / 235Nm)**.

### ¿Tienes otro motor?
Si quieres adaptar los cálculos a tu vehículo, puedes modificar los siguientes parámetros:

*   **Potencia (CV)**: En `obd_manager.py`, busca la constante `0.8` en la fórmula `self.data["HP"] = self.data["MAF"] / 0.8`. Ajústala según la eficiencia volumétrica de tu motor.
*   **Relaciones de Marchas**: En `main.py`, dentro de `DashboardScreen.update_logic`, puedes ajustar los rangos de velocidad para que el indicador de marcha sea preciso con tu caja de cambios.

---

## 🏁 Cómo usar la App

1.  Conecta tu adaptador **ELM327** al puerto OBD del coche.
2.  Arranca el motor (o pon el contacto en posición II).
3.  Asegúrate de que el adaptador esté vinculado por Bluetooth a tu PC.
4.  Ejecuta el script principal:

```bash
python main.py
```

El indicador de la parte superior pasará de **ROJO** a **AMARILLO** mientras busca el adaptador, y finalmente a **VERDE** cuando los datos empiecen a fluir.

---

## 📱 Capturas de Pantalla

*(Aquí puedes añadir imágenes de tu Dashboard, Gráficas y Pantalla de Aceleración)*

---
Desarrollado por [robertogd75](https://github.com/robertogd75) - ¡Nos vemos en la pista! 🏁
