# Mamitas
Este repositorio contiene un modelo de segmentación para dermatomas podales basado en imágenes térmicas. Su objetivo principal es proporcionar herramientas y recursos para la segmentación de regiones específicas del pie, utilizando técnicas de aprendizaje profundo.

## Contenido

El repositorio se organiza en los siguientes cuadernos Jupyter, divididos en dos grandes grupos de modelos:

### **ResUNet:**
- **resunet-mamitas-train:**  
  Cuaderno para entrenar el modelo ResUNet para segmentación de dermatomas podales.
- **resunet-mamitas-test:**  
  Cuaderno para realizar inferencia con el modelo ResUNet entrenado.

### **YOLOv11:**
- **yolov11-mamitas-train:**  
  Cuaderno para entrenar YOLOv11 para segmentación de dermatomas podales.
- **yolov11-mamitas-test:**  
  Cuaderno para realizar inferencia con el modelo YOLOv11 entrenado.

## Requisitos

Para ejecutar estos cuadernos se requiere:
- Python 3.10 o superior
- TensorFlow 2.15 o superior
- PyTorch (para YOLOv11)
- OpenCV
- Matplotlib
- NumPy
- Kaggle API
- Roboflow API (para descarga y preprocesamiento de datos)
- Ultralytics (para YOLOv11)

## Cómo usar

### **Entrenamiento**
1. Clona este repositorio en tu máquina local o directamente en Kaggle.
2. Configura tu entorno con las dependencias necesarias.
3. Organiza tus datos térmicos en la estructura requerida (ver sección **Estructura de Datos**).
4. Selecciona el cuaderno de entrenamiento correspondiente al modelo que deseas utilizar (ResUNet o YOLOv11).
5. Ejecuta el cuaderno. Los modelos entrenados se guardarán automáticamente en la carpeta `./models/`.

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

## Resultados Esperados

A continuación, se muestran algunas métricas de rendimiento (ejemplo) que se han obtenido en el proyecto para la segmentación de dermatomas podales:

| Modelo              | Variante | Dice Coefficient | Jaccard Index | Sensitivity | Specificity | Precision (P) | Recall (R) | mAP50 | mAP50-95 |
|---------------------|----------|------------------|---------------|-------------|-------------|---------------|------------|-------|----------|
| **ResUNet**        | default   | 0.97410          | 0.95062       | 0.97275     | 0.97275     | -             | -          | -     | -        |
| **YOLOv11 (Seg)**  | segmentation | -             | -             | -           | -           | 0.983         | 1          | 0.99  | 0.99     |

Los cuadernos incluyen visualizaciones de los resultados de entrenamiento y ejemplos de inferencia. Los modelos entrenados se guardan en la carpeta `./models/` y los resultados de evaluación se almacenan en `./results/`.

## Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras errores o tienes sugerencias para mejorar estos cuadernos, por favor abre un issue o envía una pull request.

## Licencia

Este proyecto se distribuye bajo la licencia BSD 2-Clause. Consulta el archivo LICENSE para más detalles.

¡Listo para segmentar dermatomas podales con técnicas de aprendizaje profundo! 👣🔥

