

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import sklearn
import os
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
import pickle
import pathlib

from sklearn.model_selection import GridSearchCV
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
CWD = os.getcwd()
WD = CWD.split('Main')[0] + 'Main/'
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def create_model(model_creation_data,AGG,PCODE,MONTH_ID, columns_dist, Scaling=None):
    
    print(f"\n\t{'-'*60}\n\tCREATE MODEL FOR '{PCODE}' | {MONTH_ID}\n\t{'-'*60}")
    numeric_features = columns_dist['cols_attributes_basic']
    cat_features = columns_dist['cols_attributes_category']
    column_target = columns_dist['column_target']
    
    # Standard Scalar Transformer of numeric contineous data
    numeric_tr_SS = Pipeline(steps=[("scaler", StandardScaler())])
    
    # Minmax Transformer of numeric contineous data
    numeric_tr_MM = Pipeline(steps=[("scaler", MinMaxScaler())])
        
    # Catagegorcial transformers on catagorical attributes
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")
    
    # Features and Target data
    X = model_creation_data[numeric_features+cat_features]
    y = model_creation_data[[column_target]]
    
    if Scaling:
        if Scaling == 'MinMax':
            numeric_transformer = numeric_tr_MM
        elif scaling=='StandardScalar':
            numeric_transformer = numeric_tr_SS
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num_transform", numeric_transformer, numeric_features),
                ("cat_transform", categorical_transformer, cat_features),
            ]
        )
    
    else:
        preprocessor = ColumnTransformer(
                transformers=[
                    ("cat_transform", categorical_transformer, cat_features),
                ],
                remainder='passthrough')

    RFC = RandomForestClassifier(random_state=42)
    
    pipe = Pipeline(
    steps=[("preprocessor", preprocessor), ("rf_regressor", RFC)])
    param_grid={'rf_regressor__n_estimators': [100, 150,
                                               200, 250, 300,
                                               350, 400, 450, 500],
                'rf_regressor__criterion': ['gini', 'entropy', 'log_loss'],
             'rf_regressor__max_features':['sqrt', 'log2']},
    
    search = GridSearchCV(estimator = pipe,
                          param_grid=param_grid,
                          return_train_score=True,
                          scoring='accuracy',
                          refit = True,
                          n_jobs=-1)
    
    print(f"\t1. Train Random Forest Model using All Features")
    search.fit(X, y.values.flatten())
    best_fit = search.best_estimator_

    MODEL_CREATION_DIRECTORY = f'Sources/aggs/{AGG}/Results/Pattern_Models/{PCODE}/Classifiers/{MONTH_ID}/'
    pathlib.Path(os.path.join(WD, MODEL_CREATION_DIRECTORY)).mkdir(parents=True, exist_ok=True)    
    
    print(f"\t2. Create Model Directory Folder\n\t     {MODEL_CREATION_DIRECTORY}")
    print(f"\t3. Save Neccesary Files for Fast Predictions in Production")
    pickle.dump(best_fit, open(os.path.join(WD, MODEL_CREATION_DIRECTORY) + 'model.sav', 'wb'))  
    print(f"\t{'-'*60}\n")
    return
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
