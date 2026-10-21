"""Glosario de la Unidad 2: Administración de procesos y del procesador.
Cada tema: id, título, resumen, secciones [(subtítulo, [(término, definición)])]."""

TEMAS = [
    {
        "id": "2.1", "title": "Concepto de proceso",
        "summary": "Un proceso es un programa en ejecución: el programa es el texto guardado en disco; "
                   "el proceso es esa ejecución, con su memoria, su estado y los recursos que el sistema le asigna.",
        "secciones": [
            ("Programa y proceso", [
                ("Programa", "Entidad pasiva: archivo ejecutable con instrucciones, guardado en disco."),
                ("Proceso", "Entidad activa: instancia de un programa en ejecución. Dos procesos pueden ejecutar el mismo programa y ser distintos."),
                ("Imagen del proceso", "Lo que el proceso tiene en memoria: código (texto), datos globales, montículo (heap) para memoria dinámica y pila (stack) para llamadas y variables locales."),
            ]),
            ("Bloque de control de proceso (PCB)", [
                ("PCB", "Estructura que el sistema operativo mantiene por cada proceso. Es lo que permite detenerlo y reanudarlo después."),
                ("Contenido típico", "Identificador (PID), estado, contador de programa, registros del procesador, información de planificación (prioridad, tiempos), información de memoria y lista de archivos o dispositivos abiertos."),
                ("Cambio de contexto", "Guardar el estado del proceso que sale de la CPU en su PCB y cargar el del siguiente. Es trabajo útil para el sistema, pero no hace avanzar a ningún proceso: es sobrecarga."),
            ]),
            ("Ciclo de vida", [
                ("Creación", "Ocurre al iniciar el sistema, al ejecutar un programa, o cuando un proceso crea a otro (relación padre e hijo, por ejemplo con fork en UNIX)."),
                ("Terminación", "Normal (el proceso acaba), por error, o forzada por otro proceso o por el sistema. Al terminar se liberan sus recursos."),
                ("Proceso padre e hijo", "El proceso creador es el padre; el creado, el hijo. Forman un árbol de procesos."),
            ]),
        ],
    },
    {
        "id": "2.2", "title": "Estados y transiciones de los procesos",
        "summary": "Durante su vida un proceso cambia de estado según lo que necesite y lo que el sistema le conceda. "
                   "El modelo de siete estados añade dos estados suspendidos para cuando el proceso sale de memoria hacia el disco. "
                   "La vista Estados de este programa lo recorre paso a paso.",
        "secciones": [
            ("Estados", [
                ("Nuevo", "El proceso se acaba de crear; el sistema aún no lo admite para competir por la CPU."),
                ("Listo", "Tiene todo lo necesario y espera su turno de CPU, en memoria principal. Los listos forman la cola de listos."),
                ("Ejecutando", "Tiene la CPU en este momento. En un procesador de un solo núcleo hay a lo sumo un proceso en este estado."),
                ("Bloqueado", "No puede continuar hasta que ocurra un suceso (terminar una E/S, recibir un mensaje, liberar un recurso). No gasta CPU mientras espera."),
                ("Listo suspendido", "Está listo, pero fue enviado al disco (swap) para liberar memoria."),
                ("Bloqueado suspendido", "Está bloqueado y además fue enviado al disco."),
                ("Saliente (terminado)", "Terminó su ejecución; el sistema libera sus recursos."),
            ]),
            ("Transiciones", [
                ("Admisión", "Nuevo → Listo (o Listo suspendido si no hay memoria)."),
                ("Activación (despacho)", "Listo → Ejecutando: el planificador asigna la CPU."),
                ("Fin de quantum (expulsión)", "Ejecutando → Listo: se acabó el tiempo asignado, o llegó un proceso con más derecho a la CPU."),
                ("Espera por suceso", "Ejecutando → Bloqueado: el proceso pide algo que no está disponible aún, como una operación de E/S."),
                ("Sucede el evento", "Bloqueado → Listo: ocurrió el suceso esperado."),
                ("Salida", "Ejecutando → Saliente: el proceso termina."),
                ("Suspensión", "Listo → Listo suspendido, o Bloqueado → Bloqueado suspendido: se libera memoria enviando el proceso al disco."),
                ("Reactivación", "Regreso del disco a memoria: Listo suspendido → Listo, o Bloqueado suspendido → Bloqueado."),
            ]),
            ("Notas", [
                ("Modelo de cinco estados", "Es el modelo básico: Nuevo, Listo, Ejecutando, Bloqueado y Terminado. Los dos estados suspendidos son una ampliación para sistemas con intercambio (swapping)."),
                ("Nombres", "Algunos libros llaman «despacho» a la activación y «expiración de quantum» o «desalojo» al fin de quantum."),
            ]),
        ],
    },
    {
        "id": "2.3", "title": "Procesos ligeros: hilos o hebras",
        "summary": "Un hilo (thread) es una unidad de ejecución dentro de un proceso. Varios hilos del mismo proceso comparten "
                   "memoria y recursos, y cada uno lleva su propio flujo de ejecución. Por eso crear un hilo y cambiar entre hilos es más barato que hacerlo con procesos.",
        "secciones": [
            ("Qué comparten y qué no", [
                ("Comparten", "Código, datos globales, montículo, archivos abiertos y otros recursos del proceso."),
                ("Es propio de cada hilo", "Contador de programa, registros, pila y estado (en su bloque de control de hilo, TCB)."),
                ("Ventajas", "Creación y cambio de contexto más rápidos; comunicación sencilla por memoria compartida; mejor aprovechamiento de varios núcleos y de la espera por E/S."),
                ("Riesgos", "Como comparten memoria, los accesos simultáneos a los mismos datos requieren sincronización (tema 2.4)."),
            ]),
            ("Tipos de hilos", [
                ("Hilos de usuario", "Los administra una biblioteca en espacio de usuario; el núcleo no los conoce. Son muy ligeros, pero si uno se bloquea en una llamada al sistema puede bloquear a todo el proceso."),
                ("Hilos de núcleo", "Los administra el sistema operativo directamente; pueden ejecutarse en núcleos distintos y bloquearse por separado."),
            ]),
            ("Modelos de asignación", [
                ("Muchos a uno", "Muchos hilos de usuario sobre un solo hilo de núcleo."),
                ("Uno a uno", "Cada hilo de usuario corresponde a un hilo de núcleo; es el modelo de Windows y Linux."),
                ("Muchos a muchos", "Varios hilos de usuario se reparten entre varios hilos de núcleo."),
            ]),
            ("Proceso frente a hilo", [
                ("Aislamiento", "Los procesos están aislados entre sí; los hilos de un proceso no."),
                ("Costo", "Crear un proceso copia o prepara un espacio de memoria; crear un hilo solo reserva su pila y su bloque de control."),
            ]),
        ],
    },
    {
        "id": "2.4", "title": "Concurrencia y secuenciabilidad",
        "summary": "Hay concurrencia cuando varios procesos o hilos progresan de forma intercalada en el tiempo. "
                   "Si comparten datos, el resultado puede depender del orden de intercalado; por eso se necesitan mecanismos de sincronización "
                   "y criterios para saber qué ejecuciones son correctas.",
        "secciones": [
            ("Conceptos", [
                ("Concurrencia", "Varias actividades en curso al mismo tiempo lógico, aunque haya un solo procesador y se turnen."),
                ("Paralelismo", "Varias actividades que se ejecutan realmente a la vez en distintos núcleos. Todo paralelismo es concurrente; no toda concurrencia es paralela."),
                ("Condición de carrera", "Situación en que el resultado depende del orden en que se intercalan accesos a datos compartidos."),
                ("Sección crítica", "Fragmento de código que accede a un recurso compartido y que no debe ser ejecutado por dos procesos a la vez."),
                ("Exclusión mutua", "Garantía de que solo un proceso a la vez está en su sección crítica."),
            ]),
            ("Mecanismos de sincronización", [
                ("Semáforo", "Entero con dos operaciones atómicas: esperar (wait o P) y señalar (signal o V). Sirve para exclusión mutua y para coordinar procesos."),
                ("Mutex (candado)", "Semáforo binario o cerrojo: solo quien lo adquiere puede entrar a la sección crítica."),
                ("Monitor", "Construcción de un lenguaje que agrupa datos compartidos y las operaciones sobre ellos, con exclusión mutua automática."),
            ]),
            ("Problemas típicos", [
                ("Interbloqueo (deadlock)", "Un grupo de procesos espera indefinidamente recursos que otros del grupo retienen. Requiere cuatro condiciones a la vez (Coffman): exclusión mutua, retener y esperar, no apropiación y espera circular."),
                ("Inanición", "Un proceso listo nunca recibe el recurso o la CPU porque otros siempre pasan antes."),
            ]),
            ("Secuenciabilidad", [
                ("Secuenciabilidad (serializabilidad)", "Una ejecución concurrente es secuenciable si su resultado es igual al de alguna ejecución en serie (uno tras otro) de los mismos procesos."),
                ("Condiciones de Bernstein", "Dos instrucciones S1 y S2 pueden ejecutarse concurrentemente sin afectar el resultado si no se cruzan sus lecturas y escrituras: L(S1)∩E(S2) = ∅, E(S1)∩L(S2) = ∅ y E(S1)∩E(S2) = ∅, donde L es el conjunto de variables leídas y E el de escritas."),
                ("Grafo de precedencia", "Grafo dirigido donde cada nodo es una instrucción o proceso y una flecha indica que uno debe terminar antes de que empiece el otro. Lo que no tiene camino entre sí puede ejecutarse en paralelo."),
            ]),
        ],
    },
    {
        "id": "2.5", "title": "Niveles, objetivos y criterios de planificación",
        "summary": "Planificar es decidir qué proceso usa el procesador y cuándo. El sistema lo hace en varios niveles, "
                   "con objetivos que a veces se contradicen, y se evalúa con métricas medibles. En este programa se usan los nombres de clase para las métricas.",
        "secciones": [
            ("Niveles de planificación", [
                ("Largo plazo (de admisión)", "Decide qué procesos nuevos entran al sistema. Controla el grado de multiprogramación."),
                ("Mediano plazo (intercambio)", "Decide qué procesos se suspenden (salen a disco) o se reactivan. Es el que mueve a los procesos a los estados suspendidos."),
                ("Corto plazo (del procesador)", "Elige, entre los procesos listos, cuál recibe la CPU. Se ejecuta muy seguido, por eso debe ser rápido. Es el que simula este programa."),
                ("Despachador", "Componente que entrega la CPU al proceso elegido: cambio de contexto y salto al punto de reanudación."),
            ]),
            ("Objetivos", [
                ("Equidad", "Dar a cada proceso una parte justa de CPU."),
                ("Eficiencia", "Mantener la CPU ocupada el mayor tiempo útil posible."),
                ("Rendimiento (throughput)", "Procesos terminados por unidad de tiempo."),
                ("Tiempo de respuesta", "Rapidez con que el sistema reacciona a una petición, importante en sistemas interactivos."),
                ("Predecibilidad", "Que un trabajo tarde aproximadamente lo mismo en distintas ocasiones."),
                ("Evitar inanición", "Que ningún proceso quede esperando para siempre."),
            ]),
            ("Criterios y métricas (nombres de clase)", [
                ("I_LL (instante de llegada)", "Momento en que el proceso llega al sistema."),
                ("T_exe (tiempo de ejecución)", "Tiempo de CPU que necesita el proceso."),
                ("I_final (instante de finalización)", "Momento en que el proceso termina."),
                ("T (tiempo de servicio)", "T = I_final − I_LL. Tiempo total que el proceso pasa en el sistema; en muchos libros se llama tiempo de retorno (turnaround)."),
                ("E (tiempo de espera)", "E = T − T_exe. Tiempo que pasa en la cola de listos sin ejecutarse."),
                ("I (índice de servicio)", "I = T_exe ÷ T. Va de 0 a 1; mientras más cerca de 1, menos esperó el proceso en proporción a lo que necesitaba."),
                ("Promedios", "Se obtienen sumando el valor de cada proceso y dividiendo entre el número de procesos."),
                ("Uso de CPU", "Porcentaje del tiempo total que la CPU dedica a ejecutar procesos."),
            ]),
            ("Tipos de planificación", [
                ("Sin expropiación (no apropiativa)", "El proceso conserva la CPU hasta terminar o bloquearse."),
                ("Con expropiación (apropiativa)", "El sistema puede quitar la CPU a un proceso que sigue listo, por fin de quantum o por llegar uno con mayor derecho."),
            ]),
        ],
    },
    {
        "id": "2.6", "title": "Técnicas de administración del planificador",
        "summary": "Cada técnica define cuál de los procesos listos se elige. Ninguna es la mejor en todo: favorecer la espera promedio, "
                   "la respuesta o la equidad exige compromisos. Los números del ejemplo son los del ejercicio del pizarrón (A: llega 0 y dura 5; B: 1 y 3; C: 2 y 1; D: 3 y 2).",
        "secciones": [
            ("FCFS: primero en llegar, primero en servirse", [
                ("Idea", "Se atiende en orden de llegada, sin expropiación. La cola de listos es una fila."),
                ("Ventaja", "Muy simple y no hay inanición."),
                ("Desventaja", "Efecto convoy: un proceso largo retrasa a todos los cortos que llegan detrás."),
                ("Ejemplo", "T promedio 6.75 y E promedio 4."),
            ]),
            ("SJF: el más corto primero", [
                ("Idea", "Entre los listos, se elige el de menor T_exe. En esta versión no hay expropiación."),
                ("Ventaja", "Minimiza la espera promedio entre los algoritmos sin expropiación."),
                ("Desventaja", "Requiere conocer o estimar T_exe, y los procesos largos pueden sufrir inanición."),
                ("Ejemplo", "T promedio 6 y E promedio 3.25."),
            ]),
            ("SRTF: menor tiempo restante primero", [
                ("Idea", "Versión con expropiación de SJF. Si llega un proceso cuyo T_exe es menor que lo que le falta al que corre, lo expropia."),
                ("Ventaja", "Minimiza la espera promedio de forma óptima si se conocen los tiempos."),
                ("Desventaja", "Más cambios de contexto y más riesgo de inanición para los largos."),
                ("Ejemplo", "T promedio 5 y E promedio 2.25."),
            ]),
            ("Round Robin: turnos con quantum", [
                ("Idea", "Cada proceso recibe la CPU un máximo de un quantum; si no termina, vuelve al final de la cola. Es expropiativo."),
                ("Ventaja", "Equitativo y con buena respuesta para sistemas interactivos."),
                ("Desventaja", "Si el quantum es muy grande se parece a FCFS; si es muy pequeño, domina la sobrecarga de cambios de contexto. Suele dar mayor espera promedio que SJF."),
                ("Ejemplo", "Con quantum 2: T promedio 7.25 y E promedio 4.5."),
            ]),
            ("Otras técnicas", [
                ("Por prioridades", "Se elige el proceso de mayor prioridad. Puede causar inanición; se corrige con envejecimiento (subir la prioridad de quien lleva mucho esperando)."),
                ("Colas multinivel", "Se separan los procesos en varias colas (por ejemplo interactivos y por lotes), cada una con su propio algoritmo, y se reparte la CPU entre las colas."),
                ("Colas multinivel con retroalimentación", "Los procesos pueden pasar de una cola a otra según su comportamiento: los que usan mucha CPU bajan de prioridad y los interactivos se mantienen arriba."),
            ]),
            ("Criterios de desempate usados en este programa", [
                ("Orden", "Primero por instante de llegada y luego por orden de captura en la tabla."),
                ("Round Robin", "Si un proceso llega en el instante en que acaba un quantum, entra a la cola antes que el proceso expropiado."),
            ]),
        ],
    },
]

BIBLIOGRAFIA = [
    "Silberschatz, A., Galvin, P. B. y Gagne, G. Operating System Concepts. Wiley (se usa la edición vigente en tu biblioteca).",
    "Tanenbaum, A. S. y Bos, H. Modern Operating Systems. Pearson (se usa la edición vigente en tu biblioteca).",
    "Stallings, W. Operating Systems: Internals and Design Principles. Pearson (el modelo de siete estados se presenta en este libro).",
]
