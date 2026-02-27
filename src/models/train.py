import pandas as pd
import sqlite3
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

import matplotlib.pyplot as plt


def train_model():
    db_path = 'data/basketball.db'
    conn = sqlite3.connect(db_path)

    # ---------------------------------------------------------
    # STEP 1: Load Data & Sort Chronologically
    # ---------------------------------------------------------
    print("Loading engineered features...")
    df = pd.read_sql("SELECT * FROM ml_features", conn)
    conn.close()

    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values('DATE').reset_index(drop=True)

    # ---------------------------------------------------------
    # STEP 2: Define the Target (y) and Features (X)
    # ---------------------------------------------------------
    # Target: What we want to predict today
    target = 'PTS'

    # Features: ONLY the lag columns we calculated in logic.py
    features = [
        'PTS_last_3', 'EFF_last_3', 'USG_last_3',
        'PTS_season_avg', 'REB_season_avg', 'EFF_season_avg',
        'PTS_vs_OPP_hist', 'EFF_vs_OPP_hist',
        'OPP_PTS_ALLOWED_PER_PLAYER', 'OPP_REB_ALLOWED_PER_PLAYER', 
        'SCORING_VACUUM', 'AST_last_3', 'BLK_last_3', 'STL_last_3', 'REB_last_3',
        'AST_season_avg', 'BLK_season_avg', 'STL_season_avg','TS_PCT_last_3', 'TS_PCT_season_avg','MONTH', 'TEAM_USG_RANK'
    ]

    X = df[features]
    y = df[target]

    # ---------------------------------------------------------
    # STEP 3: Chronological Train / Test Split
    # ---------------------------------------------------------
    # 80% for studying the past, 20% for predicting the future
    split_index = int(len(df) * 0.8)

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    print(f"Training on {len(X_train)} historical games...")
    print(f"Testing on {len(X_test)} future games...")

    # ---------------------------------------------------------
    # STEP 4: Train the Final Tuned Model
    # ---------------------------------------------------------
    print("Training the perfectly tuned XGBoost model...") 
    
    # We are using the exact mathematical sweet spot found by the Grid Search
    model = xgb.XGBRegressor(
        learning_rate=0.01, 
        max_depth=3, 
        n_estimators=500, 
        subsample=0.8, 
        random_state=234
    )
    
    # Train it instantly
    model.fit(X_train, y_train)

    # # ---------------------------------------------------------
    # # STEP 4: Train & Tune the XGBoost Model
    # # ---------------------------------------------------------
    # print("Setting up the AI's tuning grid...")
    # from sklearn.model_selection import GridSearchCV
    
    # # 1. Define the "dials" we want to test
    # param_grid = {
    #     'max_depth': [2, 3],              
    #     'learning_rate': [0.005, 0.01],     
    #     'n_estimators': [500, 750, 1000],  
    #     'subsample': [0.7, 0.8, 0.9]   
    # }

    # # 2. Create a blank factory-default model
    # base_model = xgb.XGBRegressor(random_state=234)

    # # 3. Set up the automated Grid Search
    # # cv=3 means it double-checks its homework 3 times per combination
    # grid_search = GridSearchCV(
    #     estimator=base_model, 
    #     param_grid=param_grid, 
    #     scoring='neg_mean_absolute_error', 
    #     cv=3, 
    #     verbose=1
    # )

    # # 4. Let it run! (This tests all 54 combinations)
    # print("Testing all combinations... this may take a few minutes...")
    # grid_search.fit(X_train, y_train)

    # # 5. Overwrite the blank model with the absolute best one it found
    # model = grid_search.best_estimator_

    # print(f"\n✅ Tuning Complete!")
    # print(f"Best Settings Found: {grid_search.best_params_}\n")


    # ---------------------------------------------------------
    # STEP 5: Predict and Grade the Test
    # ---------------------------------------------------------
    print("Making predictions on the future games...")
    predictions = model.predict(X_test)

    # Calculate Mean Absolute Error (MAE)
    mae = mean_absolute_error(y_test, predictions)

    print("\n--- RESULTS ---")
    print(f"Mean Absolute Error (MAE): {mae:.2f} points")
    print(f"Translation: The model's predictions are off by an average of {mae:.2f} points per player.")

    # 1. Grade the Practice Test (Past Games)
    train_predictions = model.predict(X_train)
    train_mae = mean_absolute_error(y_train, train_predictions)

    # 2. Grade the Real Exam (Future Games)
    test_predictions = model.predict(X_test)
    test_mae = mean_absolute_error(y_test, test_predictions)

    print("\n--- OVERFITTING CHECK ---")
    print(f"Practice Test (Train MAE): {train_mae:.2f} points")
    print(f"Real Exam     (Test MAE):  {test_mae:.2f} points")
    
    # Calculate the gap
    gap = test_mae - train_mae
    print(f"The Gap: {gap:.2f} points")


    # ---------------------------------------------------------
    # STEP 6: Feature Importance Chart
    # ---------------------------------------------------------
    print("Generating Feature Importance Chart...")
    
    # Pair each feature name with its importance score from the model
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=True)

    # Save the trained model to use later
    model.save_model("model/xgb_model.json")
    print("Model saved successfully as xgb_model.json!")

    # Draw a horizontal bar chart
    importance_df.plot(kind='barh', x='Feature', y='Importance', figsize=(8, 5), legend=False, color='steelblue')
    plt.title("Which Stats Drove the Predictions?")
    plt.xlabel("Relative Importance Score")
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    train_model()