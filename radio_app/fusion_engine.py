# fusion_engine.py - FIXED VERSION
def fuse_patient_data_for_model(struct_row, entities):
    fused = {}
    
    # Define all expected features
    all_features = [
        'feat1', 'feat2', 'feat3', 'tumor_size_cm', 'growth_rate',
        'tumor_size_feat', 'growth_feat', 'has_brca1', 'has_brca2',
        'has_tp53', 'has_egfr', 'lymph_node_positive', 'hist_invasive_ductal',
        'tumor_size_gt5'
    ]
    
    # Initialize with defaults
    for feature in all_features:
        fused[feature] = 0.0
    
    # Copy structured data
    numeric_features = ['feat1', 'feat2', 'feat3', 'tumor_size_cm', 'growth_rate', 'tumor_size_feat', 'growth_feat']
    for feature in numeric_features:
        if feature in struct_row:
            try:
                value = struct_row[feature]
                if value not in [None, '', 'NaN', 'nan']:
                    fused[feature] = float(value)
            except (ValueError, TypeError):
                fused[feature] = 0.0
    
    # Override with NLP data
    if 'tumor_size_cm' in entities:
        try:
            fused['tumor_size_cm'] = float(entities['tumor_size_cm'])
        except (ValueError, TypeError):
            pass
    
    if 'growth_rate' in entities:
        try:
            fused['growth_rate'] = float(entities['growth_rate'])
        except (ValueError, TypeError):
            pass
    
    # Process mutations
    mutations = entities.get('mutations', [])
    for gene in ['BRCA1', 'BRCA2', 'TP53', 'EGFR']:
        fused[f'has_{gene.lower()}'] = 1 if gene in mutations else 0
    
    # Process lymph node
    lymph_status = entities.get('lymph_node', '')
    fused['lymph_node_positive'] = 1 if lymph_status == 'positive' else 0
    
    # Process histology
    histology = entities.get('histology', '')
    fused['hist_invasive_ductal'] = 1 if 'invasive ductal' in histology else 0
    
    # Derived features
    try:
        fused['tumor_size_gt5'] = 1 if fused['tumor_size_cm'] > 5 else 0
    except (ValueError, TypeError):
        fused['tumor_size_gt5'] = 0
    
    return fused