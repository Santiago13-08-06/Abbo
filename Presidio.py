from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

# 1. Motor de lenguaje en español
config = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "es", "model_name": "es_core_news_md"}],
}
nlp_engine = NlpEngineProvider(nlp_configuration=config).create_engine()

# 2. Registro de reconocedores
registry = RecognizerRegistry(supported_languages=["es"])
registry.load_predefined_recognizers(nlp_engine=nlp_engine, languages=["es"])

# 3. Reconocedores propios para Colombia (la cédula y el NIT no vienen incluidos)
cedula = PatternRecognizer(
    supported_entity="CO_CEDULA",
    supported_language="es",
    patterns=[Pattern("cedula", r"\b\d{1,3}(?:\.\d{3}){1,2}\b|\b\d{6,10}\b", 0.4)],
    context=["cédula", "cedula", "c.c.", "cc", "identificación"],
)
nit = PatternRecognizer(
    supported_entity="CO_NIT",
    supported_language="es",
    patterns=[Pattern("nit", r"\b\d{3}\.?\d{3}\.?\d{3}-\d\b", 0.6)],
    context=["nit"],
)
registry.add_recognizer(cedula)
registry.add_recognizer(nit)

analyzer = AnalyzerEngine(
    nlp_engine=nlp_engine,
    registry=registry,
    supported_languages=["es"],
)
anonymizer = AnonymizerEngine()

# 4. Textos jurídicos inventados (nunca datos reales)
textos = [
    "María González, con cédula 52.123.456, presentó demanda de divorcio contra Pedro Ramírez en Neiva.",
    "La empresa Inversiones Andes S.A.S., NIT 900.123.456-7, demandó a Carlos Pérez por incumplimiento de contrato.",
    "El señor Luis Herrera, C.C. 1075234567, reside en la Calle 45 #12-30 de Neiva y tiene dos hijos menores.",
]

for texto in textos:
    resultados = analyzer.analyze(text=texto, language="es")
    print("\nTEXTO ORIGINAL:")
    print(texto)
    print("\nDETECTADO:")
    for r in sorted(resultados, key=lambda x: x.start):
        print(f"  {r.entity_type:12} -> '{texto[r.start:r.end]}'  (confianza {r.score:.2f})")
    print("\nANONIMIZADO:")
    print(anonymizer.anonymize(text=texto, analyzer_results=resultados).text)
    print("-" * 60)