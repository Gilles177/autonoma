DE_VAT_RATES = [0.0, 0.07, 0.19]
CH_VAT_RATES = [0.0, 0.026, 0.038, 0.081]

DE_IBAN_LENGTH = 22
CH_IBAN_LENGTH = 21

PO_REQUIRED_THRESHOLD = {
    "EUR": 500.0,
    "CHF": 500.0,
}

PRICE_TOLERANCE_PCT = 0.02          # 2% tolerance on PO vs invoice
DUPLICATE_WINDOW_DAYS = 30          # look-back for fuzzy duplicates
AMOUNT_TOLERANCE_FOR_DUP = 0.01     # 1% amount tolerance for duplicate suspicion

# Typical VAT rate per supplier category (for ambiguity detection)
EXPECTED_VAT_BY_CATEGORY = {
    ("DE", "goods"): 0.19,
    ("DE", "services"): 0.19,
    ("CH", "goods"): 0.081,
    ("CH", "services"): 0.081,
}

# German / Swiss supplier names used by the generator
DE_SUPPLIERS = [
    ("Siemens AG", "goods"),
    ("Bosch Rexroth GmbH", "goods"),
    ("Würth Industrie Service GmbH", "goods"),
    ("Festo AG & Co. KG", "goods"),
    ("Klöckner & Co. SE", "goods"),
    ("Bechtle AG", "goods"),
    ("Schäfer Werke GmbH", "goods"),
    ("Hoffmann Group", "goods"),
    ("Rittal GmbH & Co. KG", "goods"),
    ("Phoenix Contact GmbH & Co. KG", "goods"),
    ("Wolters Kluwer Deutschland GmbH", "services"),
    ("DATEV eG", "services"),
    ("Personio SE & Co. KG", "services"),
    ("SAP Deutschland SE", "services"),
    ("Haufe-Lexware GmbH & Co. KG", "services"),
]

CH_SUPPLIERS = [
    ("Bühler AG", "goods"),
    ("ABB Schweiz AG", "goods"),
    ("Georg Fischer AG", "goods"),
    ("Bystronic AG", "goods"),
    ("Komax Holding AG", "goods"),
    ("Dätwyler Holding AG", "goods"),
    ("Swisscom (Schweiz) AG", "services"),
    ("SAP (Schweiz) AG", "services"),
    ("Abacus Research AG", "services"),
    ("Bexio AG", "services"),
]
