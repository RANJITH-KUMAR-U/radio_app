# nlp_module.py - FIXED VERSION
import re

def extract_entities_from_text(text):
    if not text or not isinstance(text, str):
        return {}
    
    text = text.lower()
    entities = {}
    
    # Tumor size extraction
    size_patterns = [
        r'tumor\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*cm',
        r'lesion\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*cm',
        r'mass\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*cm',
        r'size\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*cm',
        r'(\d+(?:\.\d+)?)\s*cm\s*(?:tumor|lesion|mass)'
    ]
    
    for pattern in size_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                entities['tumor_size_cm'] = float(match.group(1))
                break
            except (ValueError, TypeError):
                continue
    
    # Growth rate extraction
    growth_patterns = [
        r'growth\s*rate\s*[:\-]?\s*(\d+(?:\.\d+)?)',
        r'growth\s*[:\-]?\s*(\d+(?:\.\d+)?)',
        r'doubling\s*time.*?(\d+(?:\.\d+)?)'
    ]
    
    for pattern in growth_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                entities['growth_rate'] = float(match.group(1))
                break
            except (ValueError, TypeError):
                continue
    
    # Gene mutations
    genes = []
    cancer_genes = ['BRCA1', 'BRCA2', 'TP53', 'EGFR', 'KRAS', 'BRAF']
    
    for gene in cancer_genes:
        if re.search(r'\b' + gene.lower() + r'\b', text):
            genes.append(gene)
    
    if genes:
        entities['mutations'] = genes
    
    # Lymph node involvement
    if re.search(r'lymph\s*node\s*(positive|involved|metastasis)', text):
        entities['lymph_node'] = 'positive'
    elif re.search(r'lymph\s*node\s*negative|no\s*lymph\s*node', text):
        entities['lymph_node'] = 'negative'
    
    # Histology types
    if re.search(r'invasive\s*ductal', text):
        entities['histology'] = 'invasive ductal carcinoma'
    elif re.search(r'adeno\s*carcinoma', text):
        entities['histology'] = 'adenocarcinoma'
    
    # Default values if nothing found
    if 'tumor_size_cm' not in entities:
        entities['tumor_size_cm'] = 2.0
    if 'growth_rate' not in entities:
        entities['growth_rate'] = 0.3
    
    return entities