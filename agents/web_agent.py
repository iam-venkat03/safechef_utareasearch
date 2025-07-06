from flask import Flask, render_template_string, request, redirect, url_for, session, render_template
import random
import datetime
import os
import markdown
from agents.email_agent import create_email, send_email, generate_recommendation  # Updated import

# Compute paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, '..', 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, '..', 'static')

# Initialize Flask app with safe absolute paths
app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)

app.secret_key = "super-secret-key"  # Reemplazar con una clave segura en producción


# Temas (con contenido en estilo markdown)
topics = [
    {
        "id": "pathogens",
        "title": "Patógenos Transmitidos por Alimentos",
        "content": """
### Los "Seis Grandes" Patógenos
Según la FDA, existen más de 40 tipos diferentes de bacterias, virus, parásitos y mohos que pueden aparecer en los alimentos y causar enfermedades transmitidas por ellos. Seis de ellos han sido señalados como altamente contagiosos y capaces de causar enfermedades graves:
1. **Shigella spp.**
2. **Salmonella Typhi**
3. **Salmonella no tifoidea (NTS)**
   - Fuentes: Aves de corral, huevos, carnes, lácteos, productos agrícolas
   - Prevención: Cocinar a la temperatura mínima, prevenir la contaminación cruzada
4. **E. coli productora de toxina Shiga (STEC)**
   - Prevención: Excluir a los manipuladores de alimentos enfermos, cocinar los alimentos (especialmente la carne molida) a temperaturas mínimas
5. **Hepatitis A**
   - Prevención: Excluir a los manipuladores de alimentos diagnosticados, lavarse las manos, evitar el contacto directo con alimentos listos para consumir
6. **Norovirus**
   - Prevención: Excluir a los manipuladores de alimentos enfermos, lavarse las manos, evitar el contacto directo con alimentos listos para consumir
        """
    },
    {
        "id": "handling",
        "title": "Manejo Seguro de Alimentos",
        "content": """
### Higiene de Manos
- Lávese las manos antes de comenzar a trabajar y después de:
  - Usar el baño
  - Manipular carne cruda
  - Tocarse el cabello, la cara o el cuerpo
  - Estornudar o toser
  - Comer o fumar
  - Manipular productos químicos o limpiar
  - Sacar la basura
- Use únicamente lavamanos designados para el lavado de manos
- Los antisépticos para manos reducen los patógenos, pero no sustituyen el lavado de manos

### Uso de Guantes
- Lávese las manos antes de ponerse los guantes
- Cambie los guantes cuando se ensucien o se rasguen
- Cambie los guantes al cambiar de tarea
- No es necesario volver a lavarse las manos si se cambian los guantes para la misma tarea

### Enfermedad Personal
- Se debe excluir a los manipuladores de alimentos si tienen:
  - Vómitos o diarrea con diagnóstico de Norovirus, Shigella, STEC o NTS
  - Diagnóstico de Hepatitis A o Salmonella Typhi
  - Ictericia
        """
    },
    {
        "id": "haccp",
        "title": "Principios HACCP",
        "content": """
HACCP (Análisis de Peligros y Puntos Críticos de Control) es un enfoque preventivo para la seguridad alimentaria.

### Los Siete Principios HACCP
1. **Realizar un análisis de peligros**
   - Identificar los posibles peligros biológicos, químicos y físicos
2. **Determinar los puntos críticos de control (PCC)**
   - Puntos donde se pueden aplicar controles para prevenir los peligros
3. **Establecer límites críticos**
   - Ejemplo: Cocinar pechuga de pato a 165°F (74°C)
4. **Establecer procedimientos de monitoreo**
   - Revisiones regulares para asegurar que se cumplan los límites críticos
5. **Identificar acciones correctivas**
   - Pasos a seguir cuando no se cumplan los límites críticos
6. **Verificar que el sistema funcione**
   - Validación regular del plan HACCP
7. **Establecer procedimientos de registro**
   - Documentar el monitoreo, las acciones correctivas, etc.

### Procesos Especializados que Requieren Variaciones
Algunos métodos de preparación de alimentos requieren una variación de las autoridades reguladoras:
- Ahumar alimentos como método de preservación
- Curar alimentos
- Utilizar aditivos alimentarios para la preservación
- Empaquetar alimentos usando envasado con oxígeno reducido
- Procesar animales de forma personalizada
- Germinar semillas o legumbres
        """
    },
    {
        "id": "sanitation",
        "title": "Instalaciones y Saneamiento",
        "content": """
### Seguridad del Agua
- Se deben prevenir las conexiones cruzadas (enlaces físicos entre agua segura y agua contaminada)
- Se requieren dispositivos de prevención de reflujo

### Limpieza y Desinfección
- Para equipos fijos:
  1. Desconectar la unidad
  2. Eliminar restos de alimentos y escombros sueltos
  3. Retirar las partes removibles
  4. Lavar, enjuagar, desinfectar y dejar secar al aire las partes removibles
  5. Limpiar y desinfectar las superficies en contacto con los alimentos de la unidad
  6. Limpiar las superficies que no tocan alimentos
  7. Volver a ensamblar la unidad

### Lavado Manual de Platos (Fregadero de Tres Compartimentos)
1. Raspar y enjuagar los restos de alimentos
2. Lavar en agua caliente con detergente (al menos 110°F/43°C)
3. Enjuagar con agua limpia
4. Desinfectar (con solución química o agua caliente)
5. Dejar secar al aire

### Desinfectantes Químicos
- Tipos comunes: Cloro, yodo, amonio cuaternario (quats)
- Utilizar kits de prueba para verificar la concentración del desinfectante
- La efectividad depende de:
  - Concentración
  - Temperatura
  - Tiempo de contacto
  - pH y dureza del agua

### Lavado de Platos a Alta Temperatura
- El enjuague final desinfectante debe estar a al menos 180°F (82°C)
- La temperatura en la superficie debe alcanzar 160°F (71°C)
- Se deben utilizar termómetros de registro máximo o cintas sensibles al calor
        """
    },
    {
        "id": "vomiting",
        "title": "Limpieza de Fluidos Corporales",
        "content": """
### Limpieza de Vómito y Diarrea
Si una persona vomita o presenta diarrea en el establecimiento:
1. **Bloquear el área**
   - Evitar que otras personas transiten por la zona
   - Retirar a las personas cercanas
2. **Usar el EPP adecuado**
   - Guantes desechables
   - Mascarilla o protector facial
   - Delantal o bata
3. **Limpiar el derrame**
   - Utilizar material absorbente desechable (toallas de papel)
   - Colocar los materiales contaminados en una bolsa plástica
4. **Desinfectar a fondo el área**
   - Usar una solución de cloro (más concentrada que la desinfectante normal)
   - Permitir el tiempo de contacto adecuado
5. **Desechar correctamente los materiales de limpieza**
   - Doblar las bolsas de desecho
   - Desechar de acuerdo con las normativas
6. **Retirar con cuidado el EPP y desecharlo**
   - Evitar contaminarse
   - Lavarse bien las manos después
7. **Documentar el incidente**
   - Muchas jurisdicciones requieren un plan escrito de limpieza

### Importancia de una Limpieza Adecuada
- El vómito y la diarrea pueden transmitir Norovirus, que es altamente contagioso
- Una limpieza adecuada previene la contaminación de los alimentos
- Evita que otras personas se enfermen
- La documentación adecuada puede ser requerida por las autoridades sanitarias
        """
    }
]

# Materiales de referencia (plantillas, listas de verificación, diagramas, organigramas)
references = {
    "templates": [
        {
            "id": "temperature-log",
            "title": "Hoja de Registro de Temperaturas",
            "content": """
# Hoja de Registro de Temperaturas

| Fecha | Hora | Alimento | Temperatura | Acción Correctiva (si es necesario) | Iniciales |
|-------|------|----------|-------------|--------------------------------------|-----------|
|       |      |          |             |                                      |           |
|       |      |          |             |                                      |           |
|       |      |          |             |                                      |           |
|       |      |          |             |                                      |           |

Notas:
- Los alimentos calientes deben mantenerse a 135°F (57°C) o más
- Los alimentos fríos deben mantenerse a 41°F (5°C) o menos
- Verificar las temperaturas al menos cada 4 horas
- Si el alimento se encuentra en la zona de peligro de temperatura, entonces:
  1. Recalentar rápidamente a 165°F (74°C) si está por debajo de 135°F
  2. Enfriar rápidamente a 41°F (5°C) si está por encima de 41°F
  3. Desechar si permanece en la zona de peligro por más de 4 horas
            """
        },
        {
            "id": "cleaning-schedule",
            "title": "Programa de Limpieza y Desinfección",
            "content": """
# Programa de Limpieza y Desinfección

| Área/Equipo               | Frecuencia       | Método de Limpieza                                  | Método de Desinfección                               | Persona Responsable |
|---------------------------|------------------|-----------------------------------------------------|------------------------------------------------------|---------------------|
| Superficies de preparación| Después de cada uso | Lavar con detergente                               | Desinfectar con solución de cloro (50-100 ppm)         |                     |
| Utensilios y tablas de cortar | Después de cada uso | Lavar, enjuagar, desinfectar en fregadero de 3 compartimentos | Desinfectar con quats (200-400 ppm)                    |                     |
| Equipos de cocina         | Diario           | Eliminar restos de alimentos, lavar con detergente  | Limpiar con desinfectante                             |                     |
| Refrigeradores            | Semanal          | Retirar todos los alimentos, lavar estantes         | Desinfectar superficies                                |                     |
| Pisos                     | Diario           | Barrer y trapear con detergente                     |                                                      |                     |
| Paredes                   | Semanal          | Lavar con solución de detergente                    |                                                      |                     |
| Áreas de basura           | Diario           | Lavar contenedores con detergente                   | Desinfectar contenedores                               |                     |

Notas:
- Utilice tiras de prueba para verificar la concentración del desinfectante
- Permitir el tiempo de contacto adecuado para los desinfectantes (seguir las instrucciones del fabricante)
- Deje secar al aire todo el equipo después de desinfectarlo
- Limpie de arriba hacia abajo (del techo al piso)
- Limpie de las áreas más limpias a las más sucias
            """
        }
    ],
    "checklists": [
        {
            "id": "opening-checklist",
            "title": "Lista de Verificación Diaria de Apertura",
            "content": """
# Lista de Verificación Diaria de Apertura

## Salud e Higiene del Personal
- [ ] Todos los empleados se ven saludables y sin signos de enfermedad
- [ ] Todos los empleados visten uniformes/atuendos limpios
- [ ] Se utilizan cubiertas para el cabello o barbas
- [ ] Se observa un correcto lavado de manos al inicio del turno
- [ ] Guantes y otro EPP disponible

## Seguridad Alimentaria
- [ ] Se verifican y registran las temperaturas del refrigerador (41°F/5°C o menos)
- [ ] Se verifican y registran las temperaturas del congelador (0°F/-18°C o menos)
- [ ] Las unidades de mantenimiento en caliente están encendidas y precalentadas
- [ ] Se preparan y prueban las soluciones desinfectantes
- [ ] Se calibran los termómetros
- [ ] Se inspeccionan adecuadamente las entregas de alimentos

## Instalaciones
- [ ] El suministro de agua opera y hay agua caliente disponible
- [ ] Los lavamanos están provistos de jabón y toallas de papel
- [ ] El fregadero de tres compartimentos está correctamente instalado
- [ ] Todo el equipo está en funcionamiento
- [ ] Las áreas de trabajo están limpias y organizadas
- [ ] Se revisa la actividad de plagas (sin evidencia de plagas)

Completado por: _________________ Fecha: _________ Hora: _________
            """
        },
        {
            "id": "allergen-checklist",
            "title": "Lista de Control de Alérgenos Alimentarios",
            "content": """
# Lista de Control de Alérgenos Alimentarios

## Almacenamiento de Alimentos
- [ ] Los ingredientes alérgenos se almacenan por debajo de los no alérgenos 
- [ ] Todos los alimentos están debidamente etiquetados con información sobre alérgenos
- [ ] Se utilizan contenedores separados para alimentos alérgenos
- [ ] Se utiliza un sistema de códigos de colores para identificar los alimentos alérgenos

## Preparación de Alimentos
- [ ] Se designa equipo separado para la preparación sin alérgenos
- [ ] Las superficies de trabajo se limpian y desinfectan antes de preparar alimentos sin alérgenos
- [ ] El personal se lava las manos y cambia los guantes antes de manipular alimentos sin alérgenos
- [ ] Los alimentos sin alérgenos se preparan primero, antes que otros alimentos

## Servicio
- [ ] Existe un sistema para identificar los pedidos sin alérgenos
- [ ] Los meseros conocen los ingredientes del menú
- [ ] Se utilizan utensilios/platos especiales para pedidos sin alérgenos
- [ ] Existe un proceso para que los gerentes manejen las preguntas sobre alérgenos
- [ ] La lista de ingredientes/información de alérgenos está disponible para los clientes

## Capacitación
- [ ] El personal está capacitado en los principales alérgenos alimentarios
- [ ] El personal está capacitado en los síntomas de reacciones alérgicas
- [ ] El personal está capacitado en la prevención del contacto cruzado
- [ ] El personal sabe qué hacer en caso de una reacción alérgica

Completado por: _________________ Fecha: _________ Hora: _________
            """
        }
    ],
    "diagrams": [
        {
            "id": "temperature-danger-zone",
            "title": "Diagrama de la Zona de Peligro de Temperatura",
            "content": """
# Zona de Peligro de Temperatura

ESCALA DE TEMPERATURA  
212°F (100°C) - El agua hierve

165°F (74°C) - Mínimo para recalentar alimentos  
              - Aves de corral, carnes rellenas, pastas rellenas

155°F (68°C) - Carnes molidas, carnes inyectadas

145°F (63°C) - Carnes de músculo entero, pescado, huevos para servicio inmediato

▲  
│  
ZONA SEGURA PARA ALIMENTOS (Alimentos Calientes)  
135°F (57°C) - Temperatura mínima para mantener alimentos calientes  
▼  
┌─────────────────────────┐  
│                         │  
│  ZONA DE PELIGRO DE     │  
│  TEMPERATURA            │  
│                         │  
│ Las bacterias se        │  
│ multiplican rápidamente │  
│ entre 41°F y 135°F      │  
│                         │  
└─────────────────────────┘  
▲  
ZONA SEGURA PARA ALIMENTOS (Alimentos Fríos)  
41°F (5°C) - Temperatura máxima para mantener alimentos fríos  
│  
▼  
32°F (0°C) - El agua se congela  
0°F (-18°C) - Temperatura recomendada para congeladores
            """
        },
        {
            "id": "handwashing-steps",
            "title": "Pasos para un Lavado de Manos Adecuado",
            "content": """
# Procedimiento Correcto para Lavarse las Manos

1. MOJAR LAS MANOS  
   Aplicar agua corriente limpia (tibia o fría)

2. APLICAR JABÓN  
   Suficiente para crear una buena espuma

3. FROTAR DURANTE 20 SEGUNDOS  
   - Entre los dedos  
   - Debajo de las uñas  
   - En la parte posterior de las manos  
   - En las muñecas  
   - Cantar "Happy Birthday" dos veces para medir el tiempo

4. ENJUAGAR BIEN  
   Con agua corriente limpia

5. SECAR COMPLETAMENTE  
   Usar toalla de papel desechable o secador de aire

6. APAGAR EL AGUA  
   Utilizar la toalla de papel para apagar el grifo

CUÁNDO LAVARSE:
- Antes de comenzar a trabajar
- Después de usar el baño
- Después de manipular alimentos crudos
- Después de tocar basura
- Después de limpiar mesas
- Después de tocarse la cara o el cabello
- Después de estornudar o toser
- Después de cualquier actividad que pueda contaminar
- Antes de ponerse los guantes
            """
        }
    ],
    "flowcharts": [
        {
            "id": "food-recall-flow",
            "title": "Diagrama del Procedimiento de Retiro de Alimentos",
            "content": """
# Procedimiento de Retiro de Alimentos

┌──────────────────┐  
│ Notificación de  │  
│ Retiro Recibida  │  
└────────┬─────────┘  
         │  
         ▼  
┌──────────────────┐  
│ Identificar los  │  
│ productos        │  
│ afectados en el  │  
│ inventario       │  
└────────┬─────────┘  
         │  
         ▼    No    ┌────────────────────────┐  
│ ¿Producto encontrado en│───────►│ Documentar hallazgos y  │  
│ el inventario?         │        │ archivar registros      │  
└────────┬─────────┘        └────────────────────────┘  
         │ Sí  
         ▼  
┌────────────────────────┐  
│ Separar y etiquetar    │  
│ claramente los         │  
│ productos afectados    │  
└────────┬─────────┘  
         │  
         ▼  
┌────────────────────────┐  
│ Seguir las instrucciones│  
│ del proveedor para      │  
│ devolución/eliminación  │  
└────────┬─────────┘  
         │  
         ▼  
┌────────────────────────┐  
│ Documentar las acciones│  
│ tomadas (cantidad,     │  
│ fecha, método)         │  
└────────┬─────────┘  
         │  
         ▼  
┌────────────────────────┐  
│ Limpiar y desinfectar  │  
│ las áreas afectadas    │  
└────────┬─────────------┘  
         │  
         ▼  
┌────────────────────────┐  
│ Archivar registros del │  
│ retiro de alimentos    │  
└────────────────────────┘
            """
        },
        {
            "id": "haccp-flow",
            "title": "Diagrama del Proceso HACCP",
            "content": """
# Flujo de Desarrollo del Proceso HACCP

┌────────────────────────┐  
│ 1. ANÁLISIS DE PELIGRO │  
│ Identificar posibles   │  
│ peligros biológicos,   │  
│ químicos y físicos     │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 2. IDENTIFICAR PCCs    │  
│ Puntos Críticos de     │  
│ Control donde se       │  
│ pueden prevenir los    │  
│ peligros               │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 3. ESTABLECER LÍMITES  │  
│ Establecer límites     │  
│ medibles para cada PCC │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 4. MONITOREO           │  
│ Establecer procedimientos │  
│ para monitorear cada PCC   │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 5. ACCIONES CORRECTIVAS│  
│ Definir acciones cuando│  
│ se detecte una         │  
│ desviación de los      │  
│ límites                │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 6. VERIFICACIÓN        │  
│ Confirmar que el sistema│  
│ HACCP funcione como se  │  
│ espera                 │  
└──────────┬─────────────┘  
           │  
           ▼  
┌────────────────────────┐  
│ 7. DOCUMENTACIÓN       │  
│ Mantener registros de  │  
│ todos los procedimientos │  
│ y del monitoreo        │  
└────────────────────────┘
            """
        }
    ]
}




# (Para abreviar se omiten los otros temas, pero deben incluirse de forma similar)

# Preguntas de cuestionario
quiz_questions = {
    
  "standard": [
    {
      "question": "Un chef está preparando un platillo y nota que uno de sus ayudantes estornuda sobre los ingredientes. ¿Qué acción debería tomar inmediatamente?",
      "options": [
        "Continuar con la preparación sin preocupación",
        "Desinfectar los ingredientes y cambiarse los guantes",
        "Llamar al supervisor y suspender al ayudante",
        "Cocinar los ingredientes a alta temperatura para eliminar cualquier contaminante"
      ],
      "correctAnswer": 1
    },
    {
      "question": "En un restaurante, la gerente nota que algunos empleados no se lavan las manos después de tocar dinero. ¿Cuál es la mejor manera de abordar esta situación?",
      "options": [
        "Implementar una capacitación sobre higiene",
        "Asignar un empleado exclusivamente para el manejo de dinero",
        "Obligar a los empleados a usar guantes en todo momento",
        "Sancionar a los empleados que no cumplan las normas"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Una inspectora de sanidad visita un restaurante y encuentra restos de comida en las superficies de trabajo. ¿Cuál es la consecuencia más probable?",
      "options": [
        "Una multa por incumplimiento de normas de higiene",
        "Un reconocimiento por el sabor de los platillos",
        "Una disminución en el tiempo de preparación",
        "Mayor durabilidad de los ingredientes"
      ],
      "correctAnswer": 0
    },
    {
      "question": "En una revisión de calidad, un inspector encuentra que la carne almacenada en refrigeración tiene mal olor y color oscuro. ¿Qué debe hacer el chef?",
      "options": [
        "Utilizarla rápidamente antes de que se eche a perder más",
        "Mezclarla con especias para enmascarar el olor",
        "Desecharla inmediatamente",
        "Lavarla con agua y vinagre para mejorar su apariencia"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un cliente reporta malestar estomacal después de comer en un restaurante. Al investigar, se descubre que el pollo no se cocinó a la temperatura adecuada. ¿Qué tipo de contaminación es esta?",
      "options": [
        "Física",
        "Química",
        "Biológica",
        "Natural"
      ],
      "correctAnswer": 2
    },
    {
      "question": "En un supermercado, un comprador encuentra un envase de leche hinchado. ¿Cuál es la acción más adecuada?",
      "options": [
        "Comprar el producto y hervirlo antes de consumirlo",
        "Notificar al encargado del supermercado",
        "Agitar el envase para mezclar su contenido",
        "Consumirlo de inmediato para evitar desperdicio"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un restaurante reporta varios casos de intoxicación alimentaria entre sus clientes. ¿Cuál podría ser la causa más probable?",
      "options": [
        "Uso de ingredientes enlatados",
        "Mala higiene del personal de cocina",
        "Exceso de condimentos en los platillos",
        "Alimentos con conservadores"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un cocinero olvida lavarse las manos después de manipular pollo crudo y luego prepara una ensalada. ¿Qué problema puede surgir?",
      "options": [
        "Contaminación cruzada",
        "Mejor sabor de la ensalada",
        "Reducción de costos de producción",
        "Ningún problema, ya que la ensalada se sirve fría"
      ],
      "correctAnswer": 0
    },
    {
      "question": "En un restaurante, el personal usa la misma esponja para limpiar todas las superficies. ¿Cuál es el problema de esta práctica?",
      "options": [
        "La esponja puede propagar bacterias",
        "Se gastan más productos de limpieza",
        "Se requiere más tiempo para limpiar",
        "No hay problema si se enjuaga bien la esponja"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un mesero derrama una bebida sobre una mesa. Para limpiarla, debe utilizar:",
      "options": [
        "Agua y un trapo seco",
        "Un desinfectante adecuado y un paño limpio",
        "Jabón en polvo y una esponja",
        "Un plumero húmedo"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un restaurante recibe una entrega de pescado y el chef nota que huele a amoníaco. ¿Qué debería hacer?",
      "options": [
        "Aceptarlo y cocinarlo rápido",
        "Rechazarlo y notificar al proveedor",
        "Lavarlo y refrigerarlo",
        "Congelarlo para reducir el olor"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un empleado deja los huevos a temperatura ambiente por varias horas. ¿Cuál es el riesgo principal?",
      "options": [
        "Contaminación bacteriana",
        "Que se rompan con facilidad",
        "Que pierdan su sabor",
        "Que sean más difíciles de pelar"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un cocinero se corta con un cuchillo. ¿Qué debe hacer primero?",
      "options": [
        "Aplicar presión con un paño limpio",
        "Seguir cocinando y lavar la herida después",
        "Poner alcohol en la herida inmediatamente",
        "Pedirle a un compañero que cubra su turno"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un incendio en la cocina comienza en una freidora con aceite. ¿Qué debe usarse para extinguirlo?",
      "options": [
        "Agua",
        "Un extintor de polvo químico seco",
        "Un trapo húmedo",
        "Un ventilador para dispersar el humo"
      ],
      "correctAnswer": 1
    },
    {
      "question": "En la mitología mesoamericana, los dioses crearon a los primeros hombres a partir de:",
      "options": [
        "Frijol",
        "Maíz",
        "Cacao",
        "Calabaza"
      ],
      "correctAnswer": 1
    },
    {
      "question": "La milpa es un sistema agrícola basado en la interacción de varios cultivos, entre los que destacan:",
      "options": [
        "Papa, frijol y trigo",
        "Arroz, jitomate y maíz",
        "Maíz, frijol y calabaza",
        "Cacao, chile y calabaza"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Durante la época prehispánica, el comercio y abasto de alimentos se realizaba principalmente en:",
      "options": [
        "Tianguis",
        "Supermercados",
        "Alhóndigas",
        "Conventos"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Cuál de los siguientes no es un utensilio prehispánico?",
      "options": [
        "Metate",
        "Molcajete",
        "Cazuela de cobre",
        "Comal"
      ],
      "correctAnswer": 2
    },
    {
      "question": "En la mesa prehispánica, la principal bebida elaborada a partir del cacao era:",
      "options": [
        "Pulque",
        "Pozol",
        "Atolli",
        "Chocolatl"
      ],
      "correctAnswer": 3
    },
    {
      "question": "¿Cuál fue uno de los principales ingredientes traídos por los europeos a la Nueva España?",
      "options": [
        "Tomate",
        "Trigo",
        "Frijol",
        "Chile"
      ],
      "correctAnswer": 1
    },
    {
      "question": "En las cocinas conventuales femeninas se crearon importantes platillos como:",
      "options": [
        "Tamales y sopes",
        "Mole poblano y chiles en nogada",
        "Tacos al pastor y carnitas",
        "Enchiladas suizas y pambazos"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál era una de las bebidas más consumidas en la gastronomía cotidiana de la Nueva España?",
      "options": [
        "Pulque",
        "Sidra",
        "Cerveza",
        "Ron"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Durante el siglo XIX, una de las influencias extranjeras que marcó la cocina mexicana fue la de:",
      "options": [
        "China",
        "España",
        "Francia",
        "Grecia"
      ],
      "correctAnswer": 2
    },
    {
      "question": "¿Cuál fue uno de los primeros recetarios impresos en México?",
      "options": [
        "El cocinero mexicano",
        "La cocina del convento",
        "Recetario de la Nueva España",
        "Los sabores de Mesoamérica"
      ],
      "correctAnswer": 0
    },
    {
      "question": "El pulque, una bebida fermentada, fue ampliamente producido en:",
      "options": [
        "Haciendas",
        "Tianguis",
        "Conventos",
        "Templos"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Cuál fue un alimento industrial que revolucionó la dieta mexicana en el siglo XX?",
      "options": [
        "Harina de maíz nixtamalizado",
        "Tortilla de trigo",
        "Chorizo embutido",
        "Mole en pasta"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Cuál de los siguientes platillos se convirtió en un icono de la gastronomía mexicana en el siglo XX?",
      "options": [
        "Pan de muerto",
        "Tacos al pastor",
        "Caldo tlalpeño",
        "Tamales oaxaqueños"
      ],
      "correctAnswer": 1
    },
    {
      "question": "La globalización ha influido en la gastronomía mexicana de diversas maneras, una de ellas es:",
      "options": [
        "La desaparición de mercados locales",
        "La incorporación de ingredientes extranjeros",
        "La eliminación de tradiciones culinarias",
        "La prohibición de alimentos callejeros"
      ],
      "correctAnswer": 1
    },
    {
      "question": "En la actualidad, el reconocimiento internacional de la gastronomía mexicana se debe en gran parte a:",
      "options": [
        "La comida rápida",
        "La cocina fusión",
        "Su declaración como Patrimonio Cultural Inmaterial de la Humanidad",
        "La globalización de restaurantes mexicanos"
      ],
      "correctAnswer": 2
    },
    {
      "question": "El taco, como icono de la cocina mexicana, tiene su origen en:",
      "options": [
        "La Revolución Mexicana",
        "La época prehispánica",
        "El siglo XIX",
        "El siglo XXI"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál de los siguientes factores ha influido en la modernización del comercio de alimentos en México?",
      "options": [
        "El cierre de mercados",
        "La creación de supermercados",
        "La desaparición del comercio informal",
        "La prohibición de los tianguis"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál de los siguientes productos es resultado de la influencia extranjera en la gastronomía mexicana?",
      "options": [
        "El mole",
        "El pan dulce",
        "El tamal",
        "La tortilla de maíz"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Durante la Revolución Mexicana, la comida se transportaba en:",
      "options": [
        "Vagones de tren",
        "Canastas de palma",
        "Cazuelas de barro",
        "Hieleras de madera"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Qué factor ha influido en la diversidad gastronómica de las diferentes regiones de México?",
      "options": [
        "La migración interna",
        "La globalización",
        "El clima y geografía",
        "La industrialización"
      ],
      "correctAnswer": 2
    },
    {
      "question": "¿Cuál es la principal función del departamento de recursos humanos en una organización?",
      "options": [
        "Gestionar únicamente el pago de nómina",
        "Supervisar a los empleados en su día a día",
        "Administrar el talento humano alineado con la estrategia organizacional",
        "Diseñar productos y servicios para la empresa"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Durante el proceso de selección, una de las técnicas más utilizadas para evaluar a los candidatos es:",
      "options": [
        "Prueba de alimentos",
        "Estudio de mercado",
        "Entrevista por competencias",
        "Registro contable"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un trabajador solicita su renuncia voluntaria. Según la Ley Federal del Trabajo, ¿qué documento debe presentar al empleador?",
      "options": [
        "Un contrato de trabajo nuevo",
        "Una carta de renuncia",
        "Un justificante médico",
        "Un memorándum de solicitud"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un restaurante implementa un programa de capacitación para sus cocineros. ¿Cuál es el primer paso en la elaboración de dicho programa?",
      "options": [
        "Contratar a un capacitador externo",
        "Realizar un diagnóstico de necesidades de capacitación",
        "Evaluar el desempeño de los empleados",
        "Elaborar los materiales de formación"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál de las siguientes es una prestación superior a la ley en México?",
      "options": [
        "Aguinaldo",
        "Vacaciones de seis días después del primer año",
        "Seguro social",
        "Vales de despensa"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál de las siguientes opciones representa una estrategia para mejorar el clima laboral?",
      "options": [
        "Implementar jornadas laborales más largas",
        "Fomentar la comunicación interna y la retroalimentación",
        "Reducir los días de vacaciones",
        "Aplicar sanciones estrictas por llegadas tarde"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un trabajador sufrió un accidente en su turno. Según las normas de seguridad e higiene, ¿cuál es la primera acción que debe tomarse?",
      "options": [
        "Permitir que el trabajador continúe su labor",
        "Aplicar primeros auxilios y reportar el accidente",
        "Pedirle que firme un documento de deslinde",
        "Descontar el día del salario del trabajador"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál de las siguientes acciones es clave en la retención del talento dentro de una empresa?",
      "options": [
        "Mantener los salarios en el mínimo permitido",
        "Fomentar el desarrollo profesional y el reconocimiento",
        "Aplicar despidos constantes",
        "Limitar la promoción interna"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un restaurante compra ingredientes por $15,000 al mes. Si su costo total de producción (considerando mano de obra y otros gastos) es de $25,000 y sus ventas mensuales ascienden a $60,000, ¿cuál es su porcentaje de costo de ventas?",
      "options": [
        "41.7%",
        "33.3%",
        "25%",
        "50%"
      ],
      "correctAnswer": 2
    },
    {
      "question": "La empresa \"Sabores del Mundo\" maneja un sistema de costos por órdenes de producción. Si cada orden implica la elaboración de 50 platillos y el costo total de cada orden es de $10,000, ¿cuál es el costo unitario de cada platillo?",
      "options": [
        "$100",
        "$150",
        "$200",
        "$250"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un restaurante gourmet usa un sistema de costos por procesos. Si en la primera etapa de producción se invierten $5,000 y en la segunda $3,000, mientras que en la tercera se agregan $2,500, ¿cuál es el costo total del proceso?",
      "options": [
        "$8,000",
        "$10,500",
        "$7,500",
        "$5,000"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un bar vende un cóctel en $150. Si el costo de los ingredientes es de $40 y el margen de contribución deseado es del 60%, ¿el precio de venta es correcto?",
      "options": [
        "Sí, porque cubre los costos y margen de contribución",
        "No, debería venderse en $120",
        "No, debería venderse en $100",
        "No, debería venderse en $200"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un negocio gastronómico tiene un costo de ventas mensual del 35%. Si sus ventas son de $80,000, ¿cuál es el costo de ventas?",
      "options": [
        "$28,000",
        "$35,000",
        "$40,000",
        "$50,000"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un bartender recibe un pedido de cócteles servidos en vasos old fashioned. ¿Cuál de las siguientes bebidas se sirve en este tipo de vaso?",
      "options": [
        "Margarita",
        "Old Fashioned",
        "Martini",
        "Mojito"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un bar de alta demanda necesita optimizar el almacenamiento de su cristalería para evitar roturas. ¿Cuál es la mejor manera de almacenar las copas de vino?",
      "options": [
        "Apiladas una sobre otra",
        "Colgadas boca abajo en un rack",
        "Dentro de un contenedor con tapa",
        "Sobre una superficie sin separación"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un cliente pide una bebida con notas amargas que ayude a la digestión después de la comida. ¿Cuál de las siguientes opciones es la más adecuada?",
      "options": [
        "Vermut",
        "Café espresso",
        "Jerez",
        "Ginebra"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un bartender debe preparar un cóctel utilizando la técnica de \"stirring\". ¿En qué situación es más adecuado usar esta técnica en lugar de \"shaking\"?",
      "options": [
        "Cuando el cóctel incluye jugos cítricos",
        "Cuando se utilizan destilados puros sin ingredientes turbios",
        "Cuando la bebida debe servirse frappé",
        "Cuando se necesita emulsionar un huevo"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un mixólogo desea equilibrar un cóctel usando una tabla de compatibilidad de sabores. Si la base es whisky, ¿cuál de las siguientes opciones es un complemento ideal?",
      "options": [
        "Limón y jarabe de agave",
        "Ron y leche condensada",
        "Vodka y jugo de piña",
        "Sake y cereza"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un cliente pregunta cuál es la diferencia entre un destilado y una bebida fermentada. ¿Cuál de las siguientes bebidas es únicamente fermentada y no pasa por destilación?",
      "options": [
        "Tequila",
        "Whisky",
        "Pulque",
        "Ginebra"
      ],
      "correctAnswer": 1
    },
    {
      "question": "En una cata de cerveza, el sommelier menciona que la bebida tiene notas de caramelo y toques tostados. ¿Qué tipo de malta es responsable de estas características?",
      "options": [
        "Malta Pilsen",
        "Malta Caramelo",
        "Malta de Trigo",
        "Malta Ahumada"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un cliente quiere un cóctel refrescante con base de ron, hierbabuena, azúcar y soda. ¿Qué bebida debe prepararle el bartender?",
      "options": [
        "Caipiriña",
        "Daiquiri",
        "Mojito",
        "Manhattan"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un bartender está preparando un Negroni, un cóctel que combina gin, vermut rojo y Campari. ¿Qué categoría de cócteles representa esta bebida?",
      "options": [
        "Highball",
        "Sour",
        "Aperitivo",
        "Frozen"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un chef quiere presentar una salsa con una textura aireada y ligera sin alterar su sabor. ¿Qué aditivo es el más adecuado para lograr este efecto?",
      "options": [
        "Lecitina de soya",
        "Agar-agar",
        "Goma xantana",
        "Alginato de sodio"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un chef necesita espesar una salsa fría sin alterar su sabor ni color. ¿Qué aditivo es la mejor opción?",
      "options": [
        "Gelatina",
        "Alginato de sodio",
        "Goma xantana",
        "Carragenina"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un restaurante utiliza nitrógeno líquido para elaborar postres con efecto de humo al ser servidos. ¿Cuál es el principal riesgo de trabajar con este ingrediente?",
      "options": [
        "Puede cambiar el color de los alimentos",
        "Puede causar quemaduras por congelación",
        "Puede descomponer los ingredientes",
        "Puede alterar el sabor de la comida"
      ],
      "correctAnswer": 2
    },
    {
      "question": "Un comensal solicita un platillo con gelatina vegana. ¿Cuál de los siguientes ingredientes es el sustituto más adecuado de la gelatina tradicional?",
      "options": [
        "Colágeno",
        "Pectina",
        "Alginato de sodio",
        "Lecitina de soya"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un bartender de un bar de mixología de vanguardia quiere espesar un cóctel sin alterar su sabor. ¿Qué ingrediente debería usar?",
      "options": [
        "Gelatina",
        "Agar-agar",
        "Goma xantana",
        "Lecitina de soya"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un chef quiere aplicar la técnica de cocción a baja temperatura al vacío (sous vide) para mantener la jugosidad de un corte de carne. ¿Cuál es la temperatura ideal para cocinar un filete de res en este método?",
      "options": [
        "40°C",
        "55°C",
        "75°C",
        "90°C"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Cuál es la principal función de los emulsionantes en los alimentos?",
      "options": [
        "Acelerar la fermentación",
        "Evitar la separación de fases en mezclas de agua y grasa",
        "Mejorar el color de los alimentos",
        "Aumentar la cantidad de proteínas"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Qué proceso fisicoquímico permite que el pan aumente de volumen durante la cocción?",
      "options": [
        "Gelatinización del almidón",
        "Coagulación de proteínas",
        "Fermentación y producción de gases",
        "Oxidación de lípidos"
      ],
      "correctAnswer": 2
    },
    {
      "question": "¿Cuál de las siguientes cocinas es conocida por el uso de especias como cúrcuma, comino y cardamomo en sus platillos?",
      "options": [
        "Cocina italiana",
        "Cocina india",
        "Cocina francesa",
        "Cocina japonesa"
      ],
      "correctAnswer": 1
    },
    {
      "question": "¿Qué país es famoso por la elaboración de sushi, sashimi y ramen?",
      "options": [
        "China",
        "Corea del Sur",
        "Japón",
        "Tailandia"
      ],
      "correctAnswer": 0
    },
    {
      "question": "En la gastronomía francesa, ¿qué técnica se utiliza para cocinar los alimentos al vacío y a baja temperatura durante un tiempo prolongado?",
      "options": [
        "Salteado",
        "Sous-vide",
        "Braseado",
        "Fritura profunda"
      ],
      "correctAnswer": 0
    },
    {
      "question": "¿Qué platillo es representativo de la cocina mexicana y consiste en tortillas rellenas de carne bañadas en salsa de chile?",
      "options": [
        "Ceviche",
        "Tamales",
        "Enchiladas",
        "Empanadas"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un restaurante compra ingredientes por $15,000 al mes. Si su costo total de producción (considerando mano de obra y otros gastos) es de $25,000 y sus ventas mensuales ascienden a $60,000, ¿cuál es su porcentaje de costo de ventas?",
      "options": [
        "41.7%",
        "33.3%",
        "25%",
        "50%"
      ],
      "correctAnswer": 1
    },
    {
      "question": "La empresa \"Sabores del Mundo\" maneja un sistema de costos por órdenes de producción. Si cada orden implica la elaboración de 50 platillos y el costo total de cada orden es de $10,000, ¿cuál es el costo unitario de cada platillo?",
      "options": [
        "$100",
        "$150",
        "$200",
        "$250"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un restaurante gourmet usa un sistema de costos por procesos. Si en la primera etapa de producción se invierten $5,000 y en la segunda $3,000, mientras que en la tercera se agregan $2,500, ¿cuál es el costo total del proceso?",
      "options": [
        "$8,000",
        "$10,500",
        "$7,500",
        "$5,000"
      ],
      "correctAnswer": 0
    },
    {
      "question": "Un bar vende un cóctel en $150. Si el costo de los ingredientes es de $40 y el margen de contribución deseado es del 60%, ¿el precio de venta es correcto?",
      "options": [
        "Sí, porque cubre los costos y margen de contribución",
        "No, debería venderse en $120",
        "No, debería venderse en $100",
        "No, debería venderse en $200"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un negocio gastronómico tiene un costo de ventas mensual del 35%. Si sus ventas son de $80,000, ¿cuál es el costo de ventas?",
      "options": [
        "$28,000",
        "$35,000",
        "$40,000",
        "$50,000"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un bartender recibe un pedido de cócteles servidos en vasos old fashioned. ¿Cuál de las siguientes bebidas se sirve en este tipo de vaso?",
      "options": [
        "Margarita",
        "Old Fashioned",
        "Martini",
        "Mojito"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un bar de alta demanda necesita optimizar el almacenamiento de su cristalería para evitar roturas. ¿Cuál es la mejor manera de almacenar las copas de vino?",
      "options": [
        "Apiladas una sobre otra",
        "Colgadas boca abajo en un rack",
        "Dentro de un contenedor con tapa",
        "Sobre una superficie sin separación"
      ],
      "correctAnswer": 1
    },
    {
      "question": "Un cliente pide una bebida con notas amargas que ayude a la digestión después de la comida. ¿Cuál de las siguientes opciones es la más adecuada?",
      "options": [
        "Vermut",
        "Café espresso",
        "Jerez",
        "Ginebra"
      ],
      "correctAnswer": 2
    }
  ],
    "advanced": [
        {
            "question": "Un bartender está diseñando un cóctel de vanguardia utilizando técnicas modernas. ¿Cuál de las siguientes técnicas es considerada parte de la mixología molecular?",
            "options": [
                "Muddling",
                "Flambeado",
                "Esferificación",
                "Stirring"
            ],
            "correctAnswer": 1,
            "explanation": ""
        },
        {
            "question": "En un restaurante de cocina molecular, el chef quiere encapsular un líquido para que al morderlo estalle en la boca del comensal. ¿Cuál de las siguientes técnicas es la adecuada?",
            "options": [
                "Gelificación con agar-agar",
                "Esferificación con alginato de sodio",
                "Emulsificación con lecitina",
                "Espesamiento con goma xantana"
            ],
            "correctAnswer": 2,
            "explanation": ""
        },
        {
            "question": "Un chef quiere lograr una espuma estable sin utilizar crema o huevo. ¿Cuál de las siguientes opciones es la más adecuada?",
            "options": [
                "Agar-agar",
                "Lecitina de soya",
                "Alginato de sodio",
                "Pectina"
            ],
            "correctAnswer": 2,
            "explanation": ""
        },
        {
            "question": "Un restaurante utiliza esferificación inversa para encapsular un licor dentro de una esfera gelatinosa. ¿Qué ingrediente necesita para realizar esta técnica?",
            "options": [
                "Agar-agar",
                "Cloruro de calcio",
                "Goma guar",
                "Lecitina de soya"
            ],
            "correctAnswer": 2,
            "explanation": ""
        },
        {
            "question": "Un chef de cocina de vanguardia quiere preparar un puré con una textura extremadamente lisa y sin grumos. ¿Cuál de las siguientes técnicas es la más adecuada?",
            "options": [
                "Batir con varilla manual",
                "Licuar a alta velocidad",
                "Pasarlo por un tamiz fino y emulsionarlo con goma xantana",
                "Hervirlo más tiempo para descomponer la fibra"
            ],
            "correctAnswer": 0,
            "explanation": ""
        }
    ],
    
    "expert": [
      {
        "question": "Una empresa desea mejorar su proceso de atracción de talento. ¿Cuál de las siguientes opciones es una fuente de reclutamiento interno?",
        "options": [
          "Anuncios en portales de empleo",
          "Ferias de empleo universitarias",
          "Promoción de empleados actuales",
          "Agencias de colocación"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "En un restaurante, el gerente detecta alta rotación de personal. ¿Qué indicador es más útil para medir este fenómeno?",
        "options": [
          "Índice de satisfacción del cliente",
          "Índice de rotación de empleados",
          "Costo de producción",
          "Indicador de productividad individual"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "¿Qué se busca medir con una evaluación de desempeño?",
        "options": [
          "La antigüedad del trabajador",
          "La productividad y competencias de un empleado",
          "El tiempo de servicio en la empresa",
          "La cantidad de descansos tomados en el mes"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Durante la elaboración de un presupuesto, una empresa analiza variables como inflación, tasas de interés y tipos de cambio. ¿En qué etapa del proceso de elaboración del presupuesto se encuentra?",
        "options": [
          "Determinación de variables económicas",
          "Estimación de ingresos y gastos",
          "Elaboración del estado de resultados presupuestado",
          "Análisis de costos fijos y variables"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Una empresa desea reducir costos innecesarios y mejorar la eficiencia de sus operaciones financieras. Para ello, decide desarrollar un presupuesto sin considerar datos de años anteriores, justificando cada gasto desde cero. ¿Qué tipo de presupuesto está utilizando?",
        "options": [
          "Presupuesto incremental",
          "Presupuesto maestro",
          "Presupuesto base cero",
          "Presupuesto flexible"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "En el proceso de planeación financiera, un contador necesita elaborar el presupuesto que refleje los ingresos esperados por ventas, incluyendo descuentos y el IVA correspondiente. ¿Cuál es el presupuesto que debe desarrollar?",
        "options": [
          "Presupuesto de cobranzas",
          "Presupuesto de ventas",
          "Presupuesto de producción",
          "Presupuesto de gastos administrativos"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Una empresa de manufactura debe estimar la cantidad de materias primas necesarias para cubrir su producción proyectada. Para ello, elabora un presupuesto detallado que contemple sus necesidades de insumos. ¿Cuál es el presupuesto que está elaborando?",
        "options": [
          "Presupuesto de gastos indirectos de fabricación",
          "Presupuesto de inversiones de activo fijo",
          "Presupuesto de requerimientos y compras de materia prima",
          "Presupuesto de flujo de caja"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "En una empresa de servicios, el gerente financiero se encarga de estimar las entradas y salidas de efectivo con el fin de garantizar la liquidez para el próximo periodo. ¿Qué presupuesto debe desarrollar?",
        "options": [
          "Presupuesto de producción",
          "Presupuesto de ventas",
          "Presupuesto de flujo de caja",
          "Presupuesto de inversiones de activo fijo"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "Un director general necesita tomar decisiones estratégicas basadas en los resultados financieros esperados de su empresa. Para ello, solicita un documento que proyecte los ingresos, costos y utilidad del próximo periodo. ¿Cuál es el documento que debe elaborar?",
        "options": [
          "Balance general presupuestado",
          "Estado de resultados presupuestado",
          "Estado de costo de producción y venta",
          "Presupuesto de ventas"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un analista financiero está elaborando un presupuesto que incluye inversiones en maquinaria, tecnología y ampliación de infraestructura. ¿Cuál es el nombre de este presupuesto?",
        "options": [
          "Presupuesto de movimientos de capital",
          "Presupuesto de gastos indirectos",
          "Presupuesto de gastos de administración y ventas",
          "Presupuesto de requerimientos de materia prima"
        ],
        "correctAnswer": 0,
        "explanation": ""
      },
      {
        "question": "Una empresa ha identificado que sus costos de producción han aumentado considerablemente. Para mejorar su planeación, decide elaborar un presupuesto específico que refleje el costo de fabricación de sus productos. ¿Qué documento debe desarrollar?",
        "options": [
          "Presupuesto de gastos indirectos de fabricación",
          "Estado de costo de producción y venta",
          "Presupuesto de ventas",
          "Presupuesto de flujo de caja"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un directivo quiere utilizar los presupuestos como herramienta de gestión para la toma de decisiones estratégicas. ¿Cuál es una de las principales ventajas del uso de presupuestos en la administración empresarial?",
        "options": [
          "Permite eliminar todos los gastos fijos",
          "Asegura un crecimiento sin necesidad de inversión",
          "Facilita la planeación y el control financiero",
          "Garantiza un aumento en las ventas"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "Un hotel ofrece un buffet con un costo total de producción de $1,800 por día y vende en promedio 90 servicios diarios. ¿Cuál es el costo unitario por servicio de buffet?",
        "options": [
          "$15",
          "$20",
          "$18",
          "$25"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un restaurante quiere calcular su punto de equilibrio. Sus costos fijos mensuales son de $50,000 y su margen de contribución por platillo es de $25. ¿Cuántos platillos necesita vender para cubrir sus costos fijos?",
        "options": [
          "1,000 platillos",
          "2,000 platillos",
          "3,000 platillos",
          "4,000 platillos"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un gerente de compras implementa un nuevo sistema de control de inventarios. Antes, las pérdidas por mermas eran del 8% mensual, y ahora se reducen al 3%. Si el inventario inicial del mes era de $20,000, ¿cuánto dinero se ahorró?",
        "options": [
          "$500",
          "$1,000",
          "$1,200",
          "$2,000"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un restaurante realiza un costeo de un platillo y obtiene que su costo directo es de $70, mientras que los gastos indirectos asociados son del 20% sobre el costo directo. ¿Cuál es el costo total del platillo?",
        "options": [
          "$75",
          "$84",
          "$90",
          "$100"
        ],
        "correctAnswer": 1,
        "explanation": ""
      },
      {
        "question": "Un restaurante utiliza la Matriz BCG para clasificar sus platillos. Si un platillo tiene alta rentabilidad pero baja demanda, ¿en qué categoría se ubicaría?",
        "options": [
          "Estrella",
          "Perro",
          "Vaca lechera",
          "Interrogante"
        ],
        "correctAnswer": 2,
        "explanation": ""
      },
      {
        "question": "Una empresa de producción necesita planear sus gastos para el próximo año. Para ello, elabora un presupuesto que incluye costos de producción, ventas y gastos administrativos. ¿A qué tipo de presupuesto corresponde esta planificación?",
        "options": [
          "Presupuesto de flujo de caja",
          "Presupuesto maestro",
          "Presupuesto flexible",
          "Presupuesto base cero"
        ],
        "correctAnswer": 1,
        "explanation": ""
      }
    ]
}

# Utilidad: filtro para convertir saltos de línea a <br> en HTML
@app.template_filter('nl2br')
def nl2br(s):
    return s.replace('\n', '<br>\n')

# Ruta principal (home)
# **Change 1**: Update the home route to use the updated index.html template
@app.route("/")
def home():
    recommendation = "Comienza con el tema 'Patógenos Transmitidos por Alimentos' para entender lo básico sobre seguridad alimentaria."
    return render_template("index.html", recommendation=recommendation)

# Ruta para listar los temas (con búsqueda)
@app.route("/topics")
def topics_page():
    query = request.args.get("q", "").lower()
    filtered = [t for t in topics if query in t["title"].lower() or query in t["content"].lower()] if query else topics
    return render_template_string(
        """
        {% extends "layout.html" %}
        {% block content %}
        <h2>Temas de Seguridad Alimentaria</h2>
        <form method="get" action="{{ url_for('topics_page') }}">
          <input type="text" name="q" placeholder="Buscar temas..." value="{{ request.args.get('q','') }}">
          <button type="submit">Buscar</button>
        </form>
        <ul>
          {% for topic in topics %}
            <li><a href="{{ url_for('view_topic', topic_id=topic.id) }}">{{ topic.title }}</a></li>
          {% endfor %}
        </ul>
        <div class="options-menu">
          <a href="{{ url_for('home') }}"><button class="option-btn">Volver al Inicio</button></a>
        </div>
        {% endblock %}
        """, topics=filtered
    )

# Ruta para ver un tema individual
@app.route("/topic/<topic_id>")
def view_topic(topic_id):
    topic = next((t for t in topics if t["id"] == topic_id), None)
    if not topic:
        return "Tema no encontrado", 404
    html_content = markdown.markdown(topic["content"])
    return render_template("topic.html", topic=topic, content=html_content)

# **Change 2**: Add a route to list all reference materials
@app.route("/references")
def references_page():
    return render_template_string(
        """
        {% extends "layout.html" %}
        {% block content %}
        <h2>Materiales de Referencia</h2>
        
        <h3>Plantillas</h3>
        <ul>
          {% for item in references['templates'] %}
            <li><a href="{{ url_for('view_reference', ref_type='templates', ref_id=item.id) }}">{{ item.title }}</a></li>
          {% endfor %}
        </ul>

        <h3>Listas de Verificación</h3>
        <ul>
          {% for item in references['checklists'] %}
            <li><a href="{{ url_for('view_reference', ref_type='checklists', ref_id=item.id) }}">{{ item.title }}</a></li>
          {% endfor %}
        </ul>

        <h3>Diagramas</h3>
        <ul>
          {% for item in references['diagrams'] %}
            <li><a href="{{ url_for('view_reference', ref_type='diagrams', ref_id=item.id) }}">{{ item.title }}</a></li>
          {% endfor %}
        </ul>

        <h3>Organigramas</h3>
        <ul>
          {% for item in references['flowcharts'] %}
            <li><a href="{{ url_for('view_reference', ref_type='flowcharts', ref_id=item.id) }}">{{ item.title }}</a></li>
          {% endfor %}
        </ul>

        <div class="options-menu">
          <a href="{{ url_for('home') }}"><button class="option-btn">Volver al Inicio</button></a>
        </div>
        {% endblock %}
        """, references=references
    )

# **Change 3**: Add a route to view a specific reference material
@app.route("/reference/<ref_type>/<ref_id>")
def view_reference(ref_type, ref_id):
    if ref_type not in references:
        return "Tipo de referencia no encontrado", 404
    ref_item = next((item for item in references[ref_type] if item["id"] == ref_id), None)
    if not ref_item:
        return "Referencia no encontrada", 404
    # For diagrams and flowcharts, wrap the content in a <pre> tag with the diagram class
    if ref_type in ["diagrams", "flowcharts"]:
        html_content = f'<pre class="diagram">{ref_item["content"]}</pre>'
    else:
        html_content = markdown.markdown(ref_item["content"])
    return render_template_string(
        """
        {% extends "layout.html" %}
        {% block content %}
        <h2>{{ ref_item.title }}</h2>
        <div class="final-output">
          {{ html_content | safe }}
        </div>
        <div class="options-menu">
          <a href="{{ url_for('references_page') }}"><button class="option-btn">Volver a Referencias</button></a>
        </div>
        {% endblock %}
        """, ref_item=ref_item, html_content=html_content
    )

# Ruta de inicio para el cuestionario: elegir dificultad
@app.route("/quiz", methods=["GET", "POST"])
def quiz_home():
    if request.method == "POST":
        difficulty = request.form.get("difficulty", "standard")
        email = request.form.get("user_email")
        session["user_email"] = email
        session["difficulty"] = difficulty
        session["quiz_index"] = 0
        session["score"] = 0

        if difficulty in quiz_questions:
            selected_questions = quiz_questions[difficulty]
            if difficulty == "standard":
                selected_questions = random.sample(selected_questions, 5)
            elif difficulty == "advanced":
                selected_questions = random.sample(selected_questions, 2)
            elif difficulty == "expert":
                selected_questions = random.sample(selected_questions, 3)
            session["questions"] = selected_questions
        else:
            session["questions"] = random.sample(quiz_questions["standard"], 5)

        session["user_answers"] = [None] * len(session["questions"])
        return redirect(url_for("quiz_question", q_index=0))
    return render_template("quiz.html")

# Ruta para mostrar cada pregunta del cuestionario
@app.route("/quiz/question/<int:q_index>", methods=["GET", "POST"])
def quiz_question(q_index):
    questions = session.get("questions", [])
    if q_index >= len(questions):
        return redirect(url_for("quiz_results"))
    
    question = questions[q_index]
    
    if request.method == "POST":
        answer = request.form.get("answer")
        try:
            answer = int(answer)
        except (ValueError, TypeError):
            answer = None
        
        if answer is None:
            # If no option is selected, re-render the form with an error message
            return render_template(
                "quiz.html",
                q_index=q_index,
                questions=questions,
                question=question,
                error="Por favor, selecciona una opción antes de continuar."
            )
        
        user_answers = session.get("user_answers", [])
        user_answers[q_index] = answer
        session["user_answers"] = user_answers
        
        # Track wrong answers
        wrong_questions = session.get("wrong_questions", [])
        if answer != question["correctAnswer"]:
            wrong_questions.append({
                "question": question["question"],
                "user_answer": question["options"][answer] if answer is not None else "No seleccionada",
                "correct_answer": question["options"][question["correctAnswer"]]
            })
        session["wrong_questions"] = wrong_questions
        
        if answer == question["correctAnswer"]:
            session["score"] = session.get("score", 0) + 1
        
        return redirect(url_for("quiz_question", q_index=q_index+1))
    
    return render_template("quiz.html", q_index=q_index, questions=questions, question=question)

# Ruta para mostrar los resultados del cuestionario
@app.route("/quiz/results")
def quiz_results():
    questions = session.get("questions", [])
    score = session.get("score", 0)
    user_email = session.get("user_email")
    wrong_questions = session.get("wrong_questions", [])

    if user_email:
        try:
            # Generate recommendations
            general, topic_summary, tips, question_review = generate_recommendation(score, len(questions), wrong_questions)

            # Enhanced email content
            subject = "Resultados del cuestionario SafeChef"
            body = f"""Hola,

Gracias por completar el cuestionario.

Tu puntuación: {score} de {len(questions)}

Recomendación general:
{general}

Resumen por tema:
{chr(10).join(topic_summary)}

Sugerencias:
{chr(10).join(tips)}

Preguntas incorrectas:
{chr(10).join(question_review)}

Saludos,
SafeChef
"""
            html_body = f"""
<html>
<body>
    <h2>Resultados del cuestionario</h2>
    <p><strong>Tu puntuación:</strong> {score} de {len(questions)}</p>
    <h3>Recomendación general:</h3>
    <p>{general}</p>
    <h3>Resumen por tema:</h3>
    <ul>
        {''.join(f"<li>{line}</li>" for line in topic_summary)}
    </ul>
    <h3>Sugerencias:</h3>
    <ul>
        {''.join(f"<li>{tip[2:]}</li>" for tip in tips)}
    </ul>
    <h3>Preguntas incorrectas:</h3>
    <ol>
        {''.join(f"<li><strong>Pregunta:</strong> {q['question']}<br><strong>Tu respuesta:</strong> {q['user_answer']}<br><strong>Respuesta correcta:</strong> {q['correct_answer']}</li>" for q in wrong_questions)}
    </ol>
    <p>Saludos,<br>SafeChef</p>
</body>
</html>
"""

            # Send enhanced email
            sender_email = "safechef8@gmail.com"
            app_password = "xefc edqs sqiw rllf"
            email_msg = create_email(sender_email, [user_email], subject, body, html_body)
            send_email("smtp.gmail.com", 465, sender_email, app_password, [user_email], email_msg)
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            # Fallback to original email logic
            try:
                body = f"Hola,\n\nGracias por completar el cuestionario.\nTu puntuación fue: {score} de {len(questions)}.\n\nSaludos,\nSafeChef"
                html_body = f"<p>Hola,</p><p>Gracias por completar el cuestionario.</p><p><strong>Tu puntuación:</strong> {score} de {len(questions)}</p><p>Saludos,<br>SafeChef</p>"
                sender_email = "safechef8@gmail.com"
                app_password = "xefc edqs sqiw rllf"
                msg = create_email(sender_email, [user_email], "Resultados del Cuestionario - SafeChef", body, html_body)
                send_email("smtp.gmail.com", 465, sender_email, app_password, [user_email], msg)
            except Exception as e2:
                print(f"Error al enviar el correo de respaldo: {e2}")

    return render_template("results.html", questions=questions, score=score, email=user_email)

@app.route("/study_plan")
def study_plan():
    return render_template("study_plan.html")

if __name__ == "__main__":
    app.run(debug=True)
