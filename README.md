# Thermomatter AI
Este repositorio contiene un modelo de segmentación para dermatomas podales basado en imágenes térmicas. Su objetivo principal es proporcionar herramientas y recursos para la segmentación de regiones específicas del pie, utilizando técnicas de aprendizaje profundo.

---

## 📁 Estructura de Carpetas

```
├── App/ # Código fuente de la aplicación móvil
├── Base_de_Datos/ # Conjunto de datos térmicos (30 casos) y scripts de preprocesamiento
├── Models/ # Enlaces a modelos entrenados en Kaggle (>25 MB)
├── notebooks/ # Jupyter notebooks de entrenamiento, inferencia y análisis
└── README.md # Documentación principal (este archivo)
```

### 1. App/

Contiene todo lo generado por Android Studio y Chaquopy para la aplicación móvil:

- Archivos Kotlin (`.kt`)
- Scripts Python (`.py`) integrados con Chaquopy
- Archivos de configuración Gradle

> **Nota**: Usamos el plugin de Chaquopy para ejecutar scripts de Python dentro de la app, lo que facilita:
> - El uso de OCR para extraer regiones de interés  
> - La aplicación de registro no rígido para alinear secuencias  
> - La carga y ejecución de modelos `.tflite`

### 2. Base_de_Datos/

Incluye los **30 casos** de imágenes térmicas originales y máscaras de segmentación:

```
├── Imágenes/
└── Mascaras - Manuales/
└── Mascaras - Red/

```

Estos datos sirvieron para entrenar y validar los modelos de segmentación.

### 3. Models/

Aquí encontrarás un archivo `models.md` con enlaces a los modelos entrenados y alojados en Kaggle (GitHub no acepta archivos >25 MB):

- **ResUNet + EfficientNetB3 (.tflite)**: mejor combinación de métricas usada en la app  
- ResUNet + ResNet34  
- YOLOv11 (segmentación y detección)

### 4. notebooks/

#### **ResUNet/Resnet34:**
- **resunet-resnet34-mamitas-train:**  
  Cuaderno para entrenar el modelo con arquitectura ResUNet con Backbone de Resnet34 para segmentación de pies.
- **resunet-resnet34-mamitas-test:**  
  Cuaderno para realizar inferencia con el modelo ResUNet con Backnone de Resnet34 entrenado.

#### **ResUNet/EfficientnetB3:**
- **resunet-efficientnetb3-mamitas-train:**  
  Cuaderno para entrenar el modelo con arquitectura ResUNet con Backbone de EfficientnetB3 para segmentación de pies.
- **resunet-efficientenetb3-mamitas-test:**  
  Cuaderno para realizar inferencia con el modelo ResUNet con Backnone de EfficientnetB3 entrenado.

#### **YOLOv11 - Segmentation:**
- **yolov11-mamitas-seg-train:**  
  Cuaderno para entrenar YOLOv11 para segmentación de pies.
- **yolov11-mamitas-seg-test-and-metrics:**  
  Cuaderno para realizar inferencia con el modelo YOLOv11 entrenado y sacar las metricas de Dice, Jaccard, Sensitivity, Specificity.

#### **YOLOv11 - Detection:**
- **yolov11-mamitas-obj-dect-train:**  
  Cuaderno para entrenar YOLOv11 para detección de pies.
- **yolov11-mamitas-seg-test-and-metrics:**  
  Cuaderno para realizar inferencia con el modelo YOLOv11 de detección entrenado.

#### **Análisis Térmico y Registro No Rígido**  
- **mamitas-map-dermatomes-and-temperature.ipynb:**  
  implementación de OCR + alineamiento no rígido y gráficas de evolución de temperatura vs. tiempo.

---

## 🚀 Requisitos

- Android Studio (proyecto Kotlin + Chaquopy)  
- Python ≥3.10  
- TensorFlow ≥2.15  
- PyTorch (YOLOv11)  
- OpenCV, NumPy, Matplotlib  
- Kaggle API & Roboflow API  
- Ultralytics (YOLOv11)

> Chaquopy ya viene configurado en el `build.gradle` de la carpeta `App/`.

---

## ⚙️ Uso

### 1. Aplicación Móvil, Codigo (App/)

1. Abre el proyecto en Android Studio.  
2. Asegúrate de tener conexión a Internet para descargar dependencias de Chaquopy.  
3. Compila y ejecuta en un dispositivo o emulador con cámara.  
4. La app capturará la zona plantar, ejecutará OCR y regresará la segmentación usando el modelo `.tflite`.

### 2. Aplicación Móvil - Instalación (App/)

1. Ve a la carpeta de App/apk/ en tu telefono
2. Descarga la apk
3. Abrela e instala la aplicación

### 3. Notebooks (Local o Kaggle)

1. Clona el repo:
   ```bash
   git clone https://github.com/tu_usuario/mamitas.git
   cd mamitas/notebooks

2. Instala requisitos:
   ```bash
   pip install -r requirements.txt

3. Ejecuta el notebook de tu interés:

- Entrenamiento: guarda pesos en Models/
- Inferencia: inserta tus imágenes en datasets/Mamitas/...
- Análisis térmico: abre mamitas-map-dermatomes-and-temperature.ipynb

---

### **Inferencia**
1. Una vez entrenado el modelo o si decides utilizar uno preentrenado, abre el cuaderno de inferencia correspondiente.
2. Asegúrate de tener las imágenes de prueba organizadas en la carpeta correcta (para ResUNet: `./datasets/Mamitas/Test/images/`; para YOLOv11, se usará el archivo de configuración `data.yaml` generado durante el proceso de descarga).
3. Ejecuta el cuaderno para obtener los resultados de segmentación.

## Estructura de Datos

Los cuadernos esperan que los datos estén organizados de la siguiente manera:

```plaintext
datasets/ 
└── Mamitas/
  ├── Train/
  │ ├── images/
  │ └── masks/
  ├── Valid/
  │ ├── images/
  │ └── masks/
  ├── Test/
  │ ├── images/
  │ └── masks/
```

Para YOLOv11, la estructura es ligeramente diferente y se configura mediante el archivo `data.yaml` que se genera al descargar el dataset.

---

## Resultados

A continuación, se muestran algunas métricas de rendimiento para segmentación y para detección en el modelo YOLO que se han obtenido en el proyecto para la segmentación de pies:

#### MÉTRICAS DE SEGMENTACIÓN

| Modelo                     | Variante     | Dice Coefficient | Jaccard Index | Sensitivity | Specificity | 
|----------------------------|--------------|------------------|---------------|-------------|-------------|
| **ResUNet/Resnet34**       | default      | 0.96213          | 0.92907       | 0.96298     | 0.96298     |
| **ResUNet/EffcientenetB3** | default      | 0.98637          | 0.97333       | 0.98698     | 0.98698     |  
| **YOLOv11/Segmentation**   | segmentation | 0.98236          | 0.96535       | 0.99157     | 0.99216     | 

#### MÉTRICAS DE DETECCIÓN

| Modelo                 | Variante     | Precision (P) | Recall (R) | mAP50   | mAP50-95 |
|------------------------|--------------|---------------|------------|---------|----------|
| **YOLOv11/Detection**  | segmentation |  1            | 1          |  0.995  |  0.995   |

Los cuadernos incluyen visualizaciones de los resultados de entrenamiento y ejemplos de inferencia. Los modelos entrenados se guardan en la carpeta `./models/` y los resultados de evaluación se almacenan en `./results/`.

---

## Imágenes Ilustrativas

A continuación se presentan ejemplos visuales del proceso completo:

- Imagen de Entrada:

<img src="https://github.com/user-attachments/assets/65c4cb95-0a0c-4d8c-9966-a851138ed690" alt="t20_caso22" width="400"/>

- Detección:

<img src="https://github.com/user-attachments/assets/991b601a-94e4-476d-9894-1046e7965594" alt="detection_feet" width="400" height="300"/>

- Segmentación:

<img src="https://github.com/user-attachments/assets/75911525-da8f-4b11-8e3c-5251f2429d06" alt="segmentation_feet" width="400" height="300"/>

---

## Base de datos
[Datos roboflow](https://universe.roboflow.com/mamitas/thermal-feet/browse?queryText=&pageSize=50&startingIndex=0&browseQuery=true)

---

## Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras errores o tienes sugerencias para mejorar estos cuadernos, por favor abre un issue o envía una pull request.

---

## Licencia

Este proyecto se distribuye bajo la licencia BSD 2-Clause. Consulta el archivo LICENSE para más detalles.

¡Listo para segmentar dermatomas podales con técnicas de aprendizaje profundo! 👣🔥

