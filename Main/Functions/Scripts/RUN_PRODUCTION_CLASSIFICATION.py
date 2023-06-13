
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from datetime import datetime
import pandas as pd
import pickle
import os
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
CWD = os.getcwd()
WD = CWD.split('Main')[0] + 'Main/'
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def run_production_predict(model_production_data,AGG,PCODE,MONTH_ID, columns_dist):
    stats_start_time = datetime.now()
    
    MODEL_CREATION_DIRECTORY = f'Sources/aggs/{AGG}/Results/Pattern_Models/{PCODE}/Classifiers/{MONTH_ID}/'
    print(f"\n\t{'-'*60}\n\tRUN PRODUCTION PREDICT FOR '{PCODE}' | {MONTH_ID}\n\t{'-'*60}")
    
    print(f"\t1. Load Saved Model Files created from 'model_creation_data'")
    
    numeric_features = columns_dist['cols_attributes_basic']
    cat_features = columns_dist['cols_attributes_category']
    column_target = columns_dist['column_target']
    
    X_production_data = model_production_data[numeric_features+cat_features]
    y_production_data = model_production_data[[column_target]]
    
    MODEL_PATH = os.path.join(WD, MODEL_CREATION_DIRECTORY, 'model.sav')
    model = pickle.load(open(MODEL_PATH, 'rb'))
    
    print(f"\t2. Create Prediction Column in 'model_production_data'")
    prediction_production_data =  model.predict(X_production_data)
    model_production_data['predict'] = prediction_production_data
    model_production_data.insert(1, 'predict', model_production_data.pop('predict'))
    
    print(f"\t3. Create Stats KPI CSV File with 'model_production_data' results")
    accuracy = accuracy_score(model_production_data['_TARGET'], model_production_data['predict'])
    precision = precision_score(model_production_data['_TARGET'], model_production_data['predict'], pos_label='WIN')
    recall = recall_score(model_production_data['_TARGET'], model_production_data['predict'], pos_label='WIN')
    f1 = f1_score(model_production_data['_TARGET'], model_production_data['predict'], pos_label='WIN')
    
    
    stats_run_seconds = (datetime.now() - stats_start_time).total_seconds()
    raw = {
    'pcode': [PCODE],
    'month_id': [MONTH_ID],
    'prediction_accuracy': [accuracy],
    'prediction_precision': [precision],
    'prediction_recall': [recall],
    'prediction_F1_score': [f1],
    'prediction_seconds': [stats_run_seconds], 
    }
    stats = pd.DataFrame(data=raw)
    
    print(f"\t4. Save the updated 'model_production_data' and 'stats' to CSV")
    model_production_data.to_csv(os.path.join(WD, MODEL_CREATION_DIRECTORY, 'model_production_data.csv'),
                                 index=False)
    stats.to_csv(os.path.join(WD, MODEL_CREATION_DIRECTORY, 'stats.csv'),
                 index=False)
    
    print(f"\t5. Return the updated 'model_production_data' and 'stats' from function")
    
    print(f"\t{'-'*60}\n")
    
    return model_production_data, stats
          
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
