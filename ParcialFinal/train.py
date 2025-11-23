"""
Script de entrenamiento para el caso de Credit Scoring.
- Carga el dataset CreditScoring.csv
- EDA mínimo (info de nulls y balance de la clase)
- Prepara pipelines con imputación mediana y escalado robusto
- Ejecuta GridSearchCV liviano para tres modelos
- Evalúa en test y guarda el mejor en best_model.pkl
"""

from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.utils.class_weight import compute_class_weight


DATA_PATH = Path("CreditScoring.csv")
RANDOM_STATE = 42


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo {path}")
    df = pd.read_csv(path)
    return df


def basic_checks(df: pd.DataFrame) -> None:
    print("Shape:", df.shape)
    print("\nValores faltantes:")
    print(df.isna().sum())
    print("\nDistribución de la variable objetivo:")
    print(df["SeriousDlqin2yrs"].value_counts(normalize=True))


def build_preprocess(feature_cols):
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[("num", numeric_transformer, feature_cols)]
    )
    return preprocess


def train_models(
    X_train,
    y_train,
    preprocess,
    class_weight_dict: Dict[int, float],
) -> Dict[str, GridSearchCV]:
    models = {
        "logreg": {
            "estimator": LogisticRegression(
                max_iter=1000, n_jobs=-1, class_weight=class_weight_dict
            ),
            "params": {"clf__C": [0.1, 1.0, 5.0]},
        },
        "rf": {
            "estimator": RandomForestClassifier(
                n_estimators=200,
                max_depth=None,
                min_samples_leaf=5,
                n_jobs=-1,
                class_weight=class_weight_dict,
                random_state=RANDOM_STATE,
            ),
            "params": {"clf__max_depth": [8, 12, None]},
        },
        "gboost": {
            "estimator": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {
                "clf__learning_rate": [0.05, 0.1],
                "clf__n_estimators": [100, 200],
            },
        },
    }

    best_models = {}
    for name, cfg in models.items():
        print(f"\nEntrenando {name} ...")
        pipe = Pipeline(steps=[("preprocess", preprocess), ("clf", cfg["estimator"])])
        grid = GridSearchCV(
            estimator=pipe,
            param_grid=cfg["params"],
            scoring="roc_auc",
            cv=3,
            n_jobs=-1,
            verbose=1,
        )
        grid.fit(X_train, y_train)
        print(f"Mejores params {name}: {grid.best_params_}")
        print(f"AUC-ROC CV {name}: {grid.best_score_:.4f}")
        best_models[name] = grid.best_estimator_
    return best_models


def evaluate_models(
    best_models: Dict[str, Any], X_test, y_test
) -> pd.DataFrame:
    rows = []
    for name, model in best_models.items():
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        rows.append(
            {
                "modelo": name,
                "AUC_ROC": roc_auc_score(y_test, y_proba),
                "Accuracy": accuracy_score(y_test, y_pred),
                "F1": f1_score(y_test, y_pred),
                "Precision": precision_score(y_test, y_pred),
                "Recall": recall_score(y_test, y_pred),
            }
        )
    return pd.DataFrame(rows).sort_values(by="AUC_ROC", ascending=False)


def main():
    df = load_data(DATA_PATH)
    basic_checks(df)

    target = "SeriousDlqin2yrs"
    feature_cols = [c for c in df.columns if c not in [target, "ID"]]

    X = df[feature_cols]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    preprocess = build_preprocess(feature_cols)

    classes = np.unique(y_train)
    class_weights = compute_class_weight("balanced", classes=classes, y=y_train)
    class_weight_dict = {cls: wt for cls, wt in zip(classes, class_weights)}
    print("\nPesos de clase:", class_weight_dict)

    best_models = train_models(X_train, y_train, preprocess, class_weight_dict)

    eval_df = evaluate_models(best_models, X_test, y_test)
    print("\nRanking en test:\n", eval_df)

    best_name = eval_df.iloc[0]["modelo"]
    best_model = best_models[best_name]
    print(f"\nMejor modelo final: {best_name}")

    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]
    print("\nReporte de clasificación del mejor modelo:")
    print(classification_report(y_test, y_pred))
    print("AUC-ROC:", roc_auc_score(y_test, y_proba))

    joblib.dump(best_model, "best_model.pkl")
    print("\nModelo guardado en best_model.pkl")


if __name__ == "__main__":
    main()
