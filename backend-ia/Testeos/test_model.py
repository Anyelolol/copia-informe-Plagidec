import time
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "/var/home/leaf/PycharmProjects/TrainerAI/modelo_detector/final"

tests = [

    ("IA", "IA obvia - lista estructurada",
     "There are several key factors to consider when choosing a programming language. "
     "First, you should evaluate the language's performance characteristics. Second, "
     "consider the size and activity of its community. Third, assess the availability "
     "of libraries and frameworks. Finally, think about the learning curve involved."),

    ("IA", "IA obvia - definición formal",
     "Quantum computing is a type of computation that harnesses the collective properties "
     "of quantum states, such as superposition, interference, and entanglement, to perform "
     "calculations. It fundamentally differs from classical computing by using quantum bits "
     "or qubits instead of classical bits, enabling certain problems to be solved exponentially faster."),

    ("IA", "IA obvia - respuesta educativa",
     "The water cycle, also known as the hydrological cycle, describes the continuous movement "
     "of water within Earth and its atmosphere. It involves several key processes: evaporation, "
     "where water from oceans and lakes turns into vapor; condensation, where vapor forms clouds; "
     "precipitation, where water falls as rain or snow; and collection, where water gathers in "
     "bodies of water again."),

    ("humano", "Humano obvio - typos y slang",
     "omg i just realized i've been doing this wrong for like 3 years lmaooo "
     "no wonder my code kept breaking. gonna fix it rn but also kinda impressed "
     "it worked at all??? computers really do just vibe sometimes"),

    ("humano", "Humano obvio - frustración real",
     "why does css hate me specifically. i spent 4 hours trying to center a div "
     "and nothing worked and then i asked my coworker and she fixed it in 2 seconds "
     "i wanted to throw my laptop out the window honestly"),

    ("humano", "Humano obvio - opinión personal fuerte",
     "unpopular opinion but i think react is overused. like yes its good but people "
     "reach for it for everything now even when plain html would work fine. "
     "saw someone use it for a static landing page last week. come on."),

    ("IA", "IA intentando sonar casual",
     "So, you want to learn Python? Great choice! Honestly, it's one of the most "
     "beginner-friendly languages out there. The syntax is clean, the community is huge, "
     "and you can build pretty much anything with it. My suggestion? Start with the basics, "
     "don't skip the fundamentals, and practice every day even if it's just 20 minutes."),

    ("IA", "IA con tono conversacional",
     "Look, I get it. Debugging is frustrating. You stare at the same code for hours "
     "and can't figure out what's wrong. Here's a trick that actually helps: explain "
     "your code out loud, line by line, as if you're teaching it to someone else. "
     "More often than not, you'll spot the issue yourself. It's called rubber duck debugging."),

    ("IA", "IA con primera persona falsa",
     "When I first started learning machine learning, I was completely overwhelmed. "
     "There were so many concepts, algorithms, and tools to understand. What helped me "
     "most was focusing on one thing at a time and building small projects. "
     "Looking back, I wish someone had told me it was okay to not understand everything at once."),

    ("IA", "IA estilo blog post",
     "Have you ever wondered why some people seem to learn new skills so much faster than others? "
     "The answer might surprise you. It's not raw intelligence or talent — it's the quality "
     "of their practice. Deliberate practice, as researchers call it, means pushing just beyond "
     "your comfort zone with clear goals and immediate feedback."),

    ("humano", "Humano formal - email profesional",
     "Dear team, I wanted to follow up on our discussion from last Tuesday regarding "
     "the Q3 deliverables. After reviewing the timeline, I believe we should prioritize "
     "the API integration before the dashboard redesign. Please let me know your thoughts "
     "at your earliest convenience. Best regards."),

    ("humano", "Humano académico - ensayo universitario",
     "The implications of Foucault's concept of biopower extend beyond the theoretical realm "
     "into contemporary surveillance practices. His analysis of disciplinary mechanisms "
     "provides a framework through which modern state control can be examined. "
     "This paper argues that social media platforms constitute a new form of panopticon."),

    ("humano", "Humano técnico - documentación",
     "This function accepts three parameters: an integer representing the batch size, "
     "a boolean flag to enable verbose logging, and an optional callback function. "
     "Returns a dictionary containing the results and metadata. Raises ValueError "
     "if batch_size is less than or equal to zero."),

    ("humano", "Humano cuidadoso - respuesta en foro técnico",
     "I ran into this exact issue last month. The problem is that the library silently "
     "ignores the timeout parameter when the connection pool is exhausted. "
     "The fix is to set max_retries=0 explicitly. Took me two days to figure this out, "
     "hope it saves you some time."),

    ("IA", "IA con errores intencionales",
     "ok so basically neural networks work like this: you have layers right? "
     "and each layer learns diffrent features. the first layers learn simple stuff "
     "like edges and the deeper layers learn more complex patterns. "
     "its actually pretty intuitive once you get it tbh"),

    ("IA", "IA imitando frustración",
     "Ugh, I know how annoying this error can be. It's one of those things that "
     "looks completely random but actually has a very specific cause. "
     "The issue is that you're trying to mutate state directly, which React doesn't allow. "
     "Instead, you need to create a new copy of the object. Trust me, once you get this "
     "pattern, everything clicks."),

    ("humano", "Humano siendo muy preciso y estructurado",
     "Three things that fixed my sleep: 1) no phone 1 hour before bed, "
     "2) room temperature at 18 degrees, 3) consistent wake time even on weekends. "
     "Took about 3 weeks to feel the difference. The wake time one is probably "
     "the most impactful if I had to pick one."),

    ("humano", "Humano explicando algo técnico bien",
     "The reason your query is slow is probably a missing index. Run EXPLAIN ANALYZE "
     "on your query and look for sequential scans on large tables. "
     "Adding an index on the foreign key columns usually solves it. "
     "That said, don't over-index — writes get slower with every index you add."),

    ("IA", "IA - respuesta muy corta",
     "To summarize: consistency is more important than intensity when building habits. "
     "Small daily actions compound over time into significant results."),

    ("humano", "Humano - muy corto e informal",
     "yeah that works, just tested it. had the same problem last week lol"),

    ("IA", "IA - una oración",
     "Machine learning models learn by iteratively adjusting their parameters to minimize "
     "a loss function that measures the difference between predicted and actual outputs."),

    ("humano", "Humano - una oración coloquial",
     "bro just use pandas it's literally one line of code why are you doing this manually"),

    ("IA", "IA - receta de cocina",
     "To prepare a classic carbonara, begin by cooking the pasta in well-salted boiling water "
     "until al dente. Meanwhile, render the guanciale in a pan over medium heat until crispy. "
     "In a bowl, whisk together egg yolks and freshly grated Pecorino Romano. "
     "Combine the pasta with the guanciale, remove from heat, and add the egg mixture, "
     "tossing vigorously to create a creamy sauce without scrambling the eggs."),

    ("humano", "Humano - receta personal",
     "ok my mom's arroz con leche recipe: you basically just cook the rice in milk "
     "with cinnamon and sugar, stir it a LOT or it sticks, and add lemon zest at the end. "
     "the secret is she uses condensed milk at the very end. never measured anything "
     "in her life so I had to guess the amounts when I wrote it down"),

    ("IA", "IA - consejo de vida",
     "Building meaningful relationships requires consistent effort and genuine interest in others. "
     "Active listening, vulnerability, and showing up during difficult times are the cornerstones "
     "of deep connections. It is worth investing time in a few close relationships rather than "
     "spreading yourself thin across many superficial ones."),

    ("humano", "Humano - consejo de vida con experiencia personal",
     "the best advice i got was from my dad when i was 22 — he said stop trying to impress "
     "people who don't pay your bills. took me a few years to actually internalize it "
     "but man was he right. changed how i made decisions completely"),

    # ── TRAMPA: ambiguo de verdad ─────────────────────────────────────────────
    ("IA", "Ambiguo - podría ser humano experto",
     "The distinction between supervised and unsupervised learning is often misunderstood. "
     "In practice, most real-world problems benefit from a hybrid approach. "
     "Semi-supervised learning, for instance, uses a small labeled dataset alongside "
     "a much larger unlabeled one, which is often more reflective of actual data availability."),

    ("humano", "Ambiguo - podría ser IA por ser formal",
     "After extensive testing across multiple environments, we concluded that the latency "
     "improvements were statistically significant only above the 95th percentile. "
     "The median case showed negligible difference, suggesting the optimization primarily "
     "benefits tail latency rather than typical request handling."),

    ("IA", "Ambiguo - IA muy corta y directa",
     "Use a dictionary instead of a list when you need O(1) lookups. "
     "Lists require O(n) time to search, while dictionaries use hashing for constant-time access."),

    ("humano", "Ambiguo - humano muy articulado",
     "What people call writer's block is usually just the fear of writing badly. "
     "The solution isn't to wait for inspiration — it's to write badly on purpose "
     "and fix it later. The internal critic only activates when you're trying to "
     "produce and evaluate simultaneously. Separate the two and the block disappears."),
]

print("Cargando modelo...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

tokenizer.model_input_names = [k for k in tokenizer.model_input_names if k != "token_type_ids"]
classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=-1,
)

print(f"\n{'='*70}")
print(f"{'#':<3} {'CATEGORÍA':<40} {'PRED':<8} {'CONF':>6}  {'OK?'}")
print(f"{'='*70}")

results = []
errores = []
incerteza = []

for i, (esperado, categoria, texto) in enumerate(tests, 1):
    resultado = classifier(texto, truncation=True, max_length=256)[0]
    pred = resultado["label"]
    conf = resultado["score"] * 100
    correcto = pred.lower() == esperado.lower()

    status = "✅" if correcto else "❌"
    alerta = " ⚠️" if conf < 80 else ""

    print(f"{i:<3} {categoria:<40} {pred:<8} {conf:>5.1f}%  {status}{alerta}")
    results.append(correcto)

    if not correcto:
        errores.append((i, categoria, esperado, pred, conf))
    if conf < 80:
        incerteza.append((i, categoria, conf))

total = len(tests)
correctos = sum(results)
score = correctos / total * 100

print(f"\n{'='*70}")
print(f"SCORE FINAL: {correctos}/{total} ({score:.0f}%)")
print(f"{'='*70}")

if errores:
    print(f"\n❌ FALLOS ({len(errores)}):")
    for num, cat, esp, pred, conf in errores:
        print(f"   #{num} {cat}")
        print(f"       Esperado: {esp.upper()} → Predijo: {pred.upper()} ({conf:.1f}%)")

if incerteza:
    print(f"\n⚠️  BAJA CONFIANZA <80% ({len(incerteza)}):")
    for num, cat, conf in incerteza:
        print(f"   #{num} {cat} → {conf:.1f}%")

# Score por categoría
cats = {
    "IA obvia": [1,2,3],
    "Humano obvio": [4,5,6],
    "IA suena humana": [7,8,9,10],
    "Humano suena a IA": [11,12,13,14],
    "Mixto/difícil": [15,16,17,18],
    "Muy cortos": [19,20,21,22],
    "No técnicos": [23,24,25,26],
    "Ambiguos": [27,28,29,30],
}

print(f"\n📊 SCORE POR CATEGORÍA:")
for cat, indices in cats.items():
    cat_correct = sum(results[i-1] for i in indices)
    print(f"   {cat:<22} {cat_correct}/{len(indices)}")
