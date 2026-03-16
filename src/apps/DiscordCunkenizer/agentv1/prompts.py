

CHUNKING_PROMPT_1 = """
Eres un experto en organizacion de texto y chunkenizacion de informacion. 
Se te proporcionará un conjunto de mensajes que han sido extraidos de un canal de discord que estan estructurados de la siguiente forma;

<indice del mensaje> -- <fecha del mensaje>  -- <autor del mensaje>: 
<contenido del mensaje>

Este conjunto de mensajes estará ordenado en orden cronologico.
Dentro de este conjunto de mensajes puden haber subconjuntos de mensajes que conforman una conversacion o ideas y 
el hilo de estas conversaciones o ideas pudo haber sido cortado por la longitud de contexto del conjunto original. Tu tarea consistirá en encontrar el **indice mas alto** (<indice del mensaje> ), en el cual 
se garantice que todos los hilos de conversaciones de los subconjuntos de mensajes con indice menor no han sido cortados por el tamaño de contexto del conjunto de mensajes original,
Es decir, si n es ese indice maximo, entonces los hilos de las conversaciones desde el indice de mensaje 1 hasta el indice de mensaje n está completos.

Genra tu respuesta en el siguiente formato JSON:

```json
{{
    max_idx : n
}}
```

En caso de que el conjunto original de mensajes sea un hilo completo de conversacion y este este cortado por el contexto del conjunto de mensajes original,
es decir que este indice maximo no existe, entonces responde:

```json
{{
    max_idx : false
}}
```

### Conjunto de mensajes de discord

{discord_messages}

"""



CHUNKING_PROMPT_2 = """
Eres un experto en **organización de texto y segmentación (chunking) de conversaciones**.

Se te proporcionará un conjunto de mensajes extraídos de un canal de Discord con la siguiente estructura:

<indice_del_mensaje> -- <fecha_del_mensaje> -- <autor_del_mensaje>
<contenido_del_mensaje>

Los mensajes están **ordenados cronológicamente**.

Dentro de este conjunto pueden existir **subconjuntos de mensajes que forman hilos de conversación o ideas**. Debido a limitaciones de contexto, es posible que algunos hilos:

* hayan comenzado **antes** del primer mensaje del conjunto, o
* continúen **después** del último mensaje del conjunto.

Tu tarea es determinar el **mayor índice `n`** tal que **todos los hilos de conversación contenidos entre el mensaje 1 y el mensaje `n` estén completos dentro del conjunto proporcionado**.

Un hilo se considera **completo** si:

* No depende de mensajes **anteriores al índice 1**, y
* No continúa **después del índice `n`**.

En otras palabras, debes encontrar el **mayor índice `n`** para el cual los mensajes `1..n` forman un conjunto de conversaciones **autocontenidas**.

### Instrucciones

1. Analiza la continuidad temática y las referencias entre mensajes.
2. Detecta si un mensaje parece responder a algo **fuera del contexto dado** o si una conversación **queda inconclusa al final**.
3. Determina el **máximo índice `n`** para el cual las conversaciones están completas.
4. Devuelve **únicamente** un objeto JSON válido.

### Formato de salida

Si existe tal índice:

```json
{{
  "max_idx": n
}}
```

Si **no existe** un índice válido (por ejemplo, porque todo el conjunto pertenece a un hilo que continúa fuera del contexto):

```json
{{
  "max_idx": false
}}
```

No incluyas explicaciones, texto adicional ni bloques de código fuera del JSON.

### Conjunto de mensajes de Discord

{discord_messages}

"""



CHUNKING_PROMPT_3 = """
Eres un experto en **organización de texto y segmentación (chunking) de conversaciones**.

Se te proporcionará un conjunto de mensajes extraídos de un canal de Discord llamado **hola** con la siguiente estructura:

<indice_del_mensaje> -- <fecha_del_mensaje> -- <autor_del_mensaje>
<contenido_del_mensaje>

Los mensajes están **ordenados cronológicamente**.


**TU OBJETIVO:**
En Discord, es común que haya múltiples hilos de conversación entrelazados. Al extraer estos mensajes por bloques (chunks), es posible que la última conversación del bloque quede cortada/inconclusa porque se alcanzó el límite de tamaño del contexto. 

Tu tarea es encontrar el "punto de corte ideal" (max_idx). El punto de corte ideal es el **índice más alto** que garantice que ninguna conversación anterior a ese índice quede inconclusa o cortada.

**REGLAS LÓGICAS PARA ENCONTRAR EL PUNTO DE CORTE:**
1. Analiza los últimos mensajes del bloque. ¿Parecen ser parte de una conversación, debate o idea que queda a medias?
2. Si la respuesta es SÍ, retrocede y busca en qué índice comenzó exactamente esa conversación que quedó cortada.
3. Tu `max_idx` será el índice del mensaje **inmediatamente anterior** al inicio de esa conversación cortada. De este modo, garantizamos que el chunk actual solo contenga conversaciones completas.
4. Si todas las conversaciones en el bloque se sienten completas y cerradas, el `max_idx` será el último índice del bloque.
5. Si el bloque entero es una sola conversación gigante que está cortada al final, entonces no hay un punto de corte válido. En este caso, el `max_idx` debe ser nulo.

**FORMATO DE SALIDA:**
Debes pensar paso a paso y generar tu respuesta ESTRICTAMENTE en el siguiente formato JSON válido:

```json
{{
  "max_idx": `n`
}}
```

Donde `n` es el **mayor índice** tal que **todos los hilos de conversación contenidos entre el mensaje 1 y el mensaje `n` estén completos dentro del conjunto proporcionado**.

Si **no existe** un índice válido (por ejemplo, porque todo el conjunto pertenece a un hilo que continúa fuera del contexto):

```json
{{
  "max_idx": null
}}
```

No incluyas explicaciones, texto adicional ni bloques de código fuera del JSON.

### Conjunto de mensajes de Discord

{discord_messages}

"""





CHUNKING_PROMPT_N = """
Eres un experto en Análisis de Datos de Conversaciones y Fragmentación (Chunking) de texto con contexto semántico.

Se te proporcionará un bloque de mensajes extraídos de un canal de Discord. Los mensajes están estructurados de la siguiente forma y ordenados cronológicamente:

<indice> -- <fecha> -- <autor>: 
<contenido>

**TU OBJETIVO:**
En Discord, es común que haya múltiples hilos de conversación entrelazados. Al extraer estos mensajes por bloques (chunks), es posible que la última conversación del bloque quede cortada/inconclusa porque se alcanzó el límite de tamaño del contexto. 

Tu tarea es encontrar el "punto de corte ideal" (max_idx). El punto de corte ideal es el **índice más alto** que garantice que ninguna conversación anterior a ese índice quede inconclusa o cortada.

**REGLAS LÓGICAS PARA ENCONTRAR EL PUNTO DE CORTE:**
1. Analiza los últimos mensajes del bloque. ¿Parecen ser parte de una conversación, debate o idea que queda a medias?
2. Si la respuesta es SÍ, retrocede y busca en qué índice comenzó exactamente esa conversación que quedó cortada.
3. Tu `max_idx` será el índice del mensaje **inmediatamente anterior** al inicio de esa conversación cortada. De este modo, garantizamos que el chunk actual solo contenga conversaciones completas.
4. Si todas las conversaciones en el bloque se sienten completas y cerradas, el `max_idx` será el último índice del bloque.
5. Si el bloque entero es una sola conversación gigante que está cortada al final, entonces no hay un punto de corte válido. En este caso, el `max_idx` debe ser nulo.

**FORMATO DE SALIDA:**
Debes pensar paso a paso y generar tu respuesta ESTRICTAMENTE en el siguiente formato JSON válido:

```json
{{
    "razonamiento": "Explica brevemente qué temas identificaste, si la última conversación quedó cortada, dónde empezó, y justifica tu elección del índice.",
    "max_idx": <numero entero o null si no existe punto de corte válido>
}}
"""