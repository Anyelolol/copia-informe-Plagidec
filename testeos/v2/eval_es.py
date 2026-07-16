import time
from load_model import cargar_modelo, predecir

tests = [

    # ── ZONA FACIL: IA obvia ──────────────────────────────────────────
    ("IA", "IA obvia - lista estructurada",
     "Existen varios factores clave a considerar al elegir un lenguaje de programación. "
     "Primero, debes evaluar el rendimiento del lenguaje. Segundo, considera el tamaño "
     "y la actividad de su comunidad. Tercero, evalúa la disponibilidad de librerías "
     "y frameworks. Finalmente, piensa en la curva de aprendizaje."),

    ("IA", "IA obvia - definición formal",
     "La computación cuántica es un tipo de cómputo que aprovecha las propiedades "
     "colectivas de los estados cuánticos, como la superposición, la interferencia "
     "y el entrelazamiento, para realizar cálculos. Se diferencia fundamentalmente "
     "de la computación clásica al usar bits cuánticos o qubits en lugar de bits clásicos."),

    ("IA", "IA obvia - respuesta educativa",
     "El ciclo del agua, también conocido como ciclo hidrológico, describe el movimiento "
     "continuo del agua dentro de la Tierra y su atmósfera. Involucra varios procesos clave: "
     "evaporación, donde el agua de océanos y lagos se convierte en vapor; condensación, "
     "donde el vapor forma nubes; precipitación, donde el agua cae como lluvia o nieve."),

    # ── ZONA FACIL: humano obvio ──────────────────────────────────────
    ("humano", "Humano obvio - typos y jerga",
     "posta que me di cuenta recien que vengo haciendo esto mal hace como 3 años jajaja "
     "no me extraña que se me rompiera el codigo todo el tiempo. ahora lo arreglo pero "
     "la verdad me sorprende que haya andado igual"),

    ("humano", "Humano obvio - frustración real",
     "por que el css me odia especificamente. me tire 4 horas tratando de centrar un div "
     "y nada funcionaba y despues le pregunte a mi compañera y lo arreglo en 2 segundos "
     "tenia ganas de tirar la notebook por la ventana en serio"),

    ("humano", "Humano obvio - opinión personal fuerte",
     "opinion impopular pero creo que react esta sobreusado. o sea, es bueno, pero la "
     "gente lo mete para todo ahora aunque con html plano alcanzaria. vi a alguien "
     "usarlo para una landing page estatica la semana pasada. dale."),

    # ── ZONA GRIS: IA que suena humana ─────────────────────────────────
    ("IA", "IA intentando sonar casual",
     "¿Así que querés aprender Python? Gran elección. Honestamente, es uno de los "
     "lenguajes más amigables para principiantes que existen. La sintaxis es clara, "
     "la comunidad es enorme, y podés construir casi cualquier cosa con él. Mi consejo: "
     "empezá por lo básico, no te saltees los fundamentos, y practicá todos los días."),

    ("IA", "IA con tono conversacional",
     "Mira, te entiendo. Debuggear es frustrante. Te quedas mirando el mismo código "
     "durante horas y no logras entender qué está mal. Acá hay un truco que realmente "
     "ayuda: explicá tu código en voz alta, línea por línea, como si le enseñaras a "
     "alguien más. La mayoría de las veces vas a encontrar el error vos mismo."),

    ("IA", "IA con primera persona falsa"
     ,"Cuando empecé a aprender machine learning, estaba completamente abrumado. Había "
     "tantos conceptos, algoritmos y herramientas para entender. Lo que más me ayudó "
     "fue enfocarme en una cosa a la vez y construir proyectos pequeños. Mirando atrás, "
     "ojalá alguien me hubiera dicho que estaba bien no entender todo de golpe."),

    # ── ZONA GRIS: humano que suena a IA ───────────────────────────────
    ("humano", "Humano formal - correo profesional",
     "Estimado equipo, quería hacer seguimiento a nuestra charla del martes pasado "
     "sobre los entregables del Q3. Después de revisar el cronograma, creo que "
     "deberíamos priorizar la integración de la API antes del rediseño del dashboard. "
     "Avísenme sus comentarios a la brevedad. Saludos."),

    ("humano", "Humano académico - ensayo universitario",
     "Las implicancias del concepto de biopoder de Foucault se extienden más allá "
     "del plano teórico hacia las prácticas de vigilancia contemporáneas. Su análisis "
     "de los mecanismos disciplinarios brinda un marco para examinar el control estatal "
     "moderno. Este trabajo sostiene que las redes sociales constituyen una nueva forma de panóptico."),

    ("humano", "Humano técnico - documentación",
     "Esta función acepta tres parámetros: un entero que representa el tamaño del lote, "
     "un booleano para habilitar el log detallado, y un callback opcional. Devuelve un "
     "diccionario con los resultados y metadata. Lanza ValueError si batch_size es menor o igual a cero."),

    ("humano", "Humano cuidadoso - respuesta en foro técnico",
     "me pasó exactamente esto el mes pasado. el problema es que la librería ignora "
     "silenciosamente el parámetro timeout cuando el pool de conexiones se agota. "
     "la solución es poner max_retries=0 explícitamente. me llevó dos días darme cuenta, "
     "ojalá te ahorre tiempo."),

    # ── CASOS DIFICILES: mezcla ─────────────────────────────────────────
    ("IA", "IA con errores intencionales",
     "ok mira, las redes neuronales funcionan asi: tenes capas, no? y cada capa aprende "
     "cosas distintas. las primeras capas aprenden cosas simples como bordes y las capas "
     "mas profundas aprenden patrones mas complejos. la verdad es bastante intuitivo "
     "una vez que lo entendes"),

    ("IA", "IA imitando frustración",
     "Uf, sé lo molesto que puede ser este error. Es de esas cosas que parecen "
     "completamente aleatorias pero en realidad tienen una causa muy específica. "
     "El problema es que estás mutando el estado directamente, algo que React no permite. "
     "En cambio, necesitás crear una copia nueva del objeto. Confiá en mí, una vez que agarrás el patrón, todo cierra."),

    ("humano", "Humano siendo preciso y estructurado",
     "tres cosas que me arreglaron el sueño: 1) nada de celu 1 hora antes de dormir, "
     "2) cuarto a 18 grados, 3) misma hora de despertar incluso los findes. me llevó "
     "como 3 semanas notar la diferencia. la del horario fijo es probablemente la más "
     "importante si tuviera que elegir una sola"),

    ("humano", "Humano explicando algo técnico bien",
     "la razón por la que tu query anda lenta probablemente es un índice faltante. "
     "corré EXPLAIN ANALYZE en tu query y fijate si hay sequential scans en tablas grandes. "
     "agregar un índice en las columnas de foreign key generalmente lo soluciona. "
     "eso sí, no sobre-indices, cada índice hace las escrituras más lentas."),

    # ── CASOS EXTREMOS: muy cortos ─────────────────────────────────────
    ("IA", "IA - respuesta muy corta",
     "En resumen: la constancia es más importante que la intensidad al crear hábitos. "
     "Pequeñas acciones diarias se acumulan con el tiempo en resultados significativos."),

    ("humano", "Humano - muy corto e informal",
     "si anda, lo acabo de probar. tuve el mismo problema la semana pasada jaja"),

    ("IA", "IA - una oración",
     "Los modelos de machine learning aprenden ajustando iterativamente sus parámetros "
     "para minimizar una función de pérdida que mide la diferencia entre lo predicho y lo real."),

    ("humano", "Humano - una oración coloquial",
     "loco usa pandas nomas es literal una linea de codigo por que estas haciendo esto a mano"),

    # ── CASOS EXTREMOS: temas no técnicos ───────────────────────────────
    ("IA", "IA - receta de cocina",
     "Para preparar una carbonara clásica, comenzá cocinando la pasta en agua bien salada "
     "hasta que quede al dente. Mientras tanto, dorá el guanciale en una sartén a fuego "
     "medio hasta que esté crocante. En un bowl, batí las yemas con queso Pecorino Romano rallado."),

    ("humano", "Humano - receta personal",
     "ok la receta de arroz con leche de mi vieja: básicamente cocinás el arroz en leche "
     "con canela y azúcar, revolvés mucho para que no se pegue, y le ponés ralladura de "
     "limón al final. el secreto es que ella le pone leche condensada al final. nunca midió "
     "nada en su vida asi que tuve que adivinar las cantidades cuando la anoté"),

    ("IA", "IA - consejo de vida",
     "Construir relaciones significativas requiere esfuerzo constante e interés genuino "
     "por los demás. La escucha activa, la vulnerabilidad y estar presente en momentos "
     "difíciles son la base de las conexiones profundas."),

    ("humano", "Humano - consejo de vida con experiencia personal",
     "el mejor consejo que me dieron fue de mi viejo cuando tenía 22 — me dijo que dejara "
     "de tratar de impresionar a gente que no me paga las cuentas. me llevó unos años "
     "internalizarlo pero tenía toda la razón. me cambió por completo cómo tomo decisiones"),

    # ── TRAMPA: ambiguo de verdad ───────────────────────────────────────
    ("IA", "Ambiguo - podría ser humano experto",
     "La distinción entre aprendizaje supervisado y no supervisado suele malentenderse. "
     "En la práctica, la mayoría de los problemas reales se benefician de un enfoque "
     "híbrido. El aprendizaje semi-supervisado, por ejemplo, usa un dataset etiquetado "
     "pequeño junto a uno mucho más grande sin etiquetar."),

    ("humano", "Ambiguo - podría ser IA por ser formal",
     "Después de hacer pruebas exhaustivas en múltiples entornos, concluimos que las "
     "mejoras de latencia fueron estadísticamente significativas solo por encima del "
     "percentil 95. El caso mediano mostró una diferencia insignificante."),

    ("IA", "Ambiguo - IA muy corta y directa",
     "Usá un diccionario en vez de una lista cuando necesites búsquedas O(1). Las listas "
     "requieren O(n) para buscar, mientras que los diccionarios usan hashing para acceso constante."),

    ("humano", "Ambiguo - humano muy articulado",
     "lo que la gente llama bloqueo del escritor generalmente es solo el miedo a escribir "
     "mal. la solución no es esperar la inspiración, es escribir mal a propósito y arreglarlo "
     "después. el crítico interno solo se activa cuando tratás de producir y evaluar al mismo tiempo"),

    ("IA", "Ambiguo - IA que cita datos genéricos",
     "Según estudios recientes, aproximadamente el 70% de los proyectos de software fallan "
     "por problemas de comunicación más que por cuestiones técnicas. Establecer canales claros "
     "desde el inicio del proyecto reduce significativamente este riesgo."),
]

print("Cargando modelo...")
modelo, tokenizer = cargar_modelo()

correctos = 0
inicio = time.time()
for esperado, categoria, texto in tests:
    pred, conf = predecir(texto, modelo, tokenizer)
    ok = "✓" if pred == esperado else "✗"
    if pred == esperado:
        correctos += 1
    print(f"{ok} [{categoria}] esperado={esperado} predicho={pred} ({conf:.1%})")

dur = time.time() - inicio
print(f"\nAccuracy: {correctos}/{len(tests)} = {correctos/len(tests):.1%}")
print(f"Tiempo total: {dur:.1f}s")
