import pandas as pd
import numpy as np
import os
import logging

# Setup logging
log_dir = '../logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'preprocessing.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def preprocess_overlay(input_path, output_path):
    logging.info(f"Starting preprocessing for {input_path}")
    
    # Load data
    df = pd.read_csv(input_path)
    initial_shape = df.shape
    logging.info(f"Initial data shape: {initial_shape}")
    
    # 1. Drop duplicates
    df = df.drop_duplicates()
    logging.info(f"Dropped {initial_shape[0] - df.shape[0]} duplicate rows.")
    
    # 2. Handle ambient_temp_c outliers
    # a. Kelvin to Celsius conversion for > 270
    kelvin_mask = df['ambient_temp_c'] > 270
    kelvin_count = kelvin_mask.sum()
    df.loc[kelvin_mask, 'ambient_temp_c'] -= 273.15
    logging.info(f"Converted {kelvin_count} Kelvin temperature values to Celsius.")
    
    # b. Extremely low temperatures (< 10) -> set to NaN for imputation
    low_temp_mask = df['ambient_temp_c'] < 10
    low_temp_count = low_temp_mask.sum()
    df.loc[low_temp_mask, 'ambient_temp_c'] = np.nan
    logging.info(f"Set {low_temp_count} extremely low temperature values (< 10) to NaN for imputation.")
    
    # 3. Drop rows with missing spatial or categorical data
    cols_to_dropna = ['field_x', 'field_y', 'reticle_id']
    before_drop = df.shape[0]
    df = df.dropna(subset=cols_to_dropna)
    logging.info(f"Dropped {before_drop - df.shape[0]} rows due to missing values in {cols_to_dropna}.")
    
    # 3-0. Fix categorical typos in reticle_id (e.g. 0.3 -> 3.0)
    typo_mask_3 = df['reticle_id'] == 0.3
    typo_mask_4 = df['reticle_id'] == 0.4
    df.loc[typo_mask_3, 'reticle_id'] = 3.0
    df.loc[typo_mask_4, 'reticle_id'] = 4.0
    logging.info(f"Fixed {typo_mask_3.sum() + typo_mask_4.sum()} typo(s) in reticle_id.")

    # 3-1. Drop coordinate outliers
    before_outlier = df.shape[0]
    df = df[(df['field_x'].abs() <= 2.0) & (df['field_y'].abs() <= 2.0)]
    logging.info(f"Dropped {before_outlier - df.shape[0]} rows due to extreme coordinate outliers (|x| or |y| > 2.0).")
    
    # 4. Impute align_quality and ambient_temp_c with tool_id median
    cols_to_impute = ['align_quality', 'ambient_temp_c']
    for col in cols_to_impute:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            # Impute with tool median
            df[col] = df.groupby('tool_id')[col].transform(lambda x: x.fillna(x.median()))
            
            # If any still missing (e.g. a tool had entirely NaN for this col), use global median
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].median())
                
            logging.info(f"Imputed {missing_count} missing values in '{col}' using median per tool_id.")

    # Validation
    assert df.isnull().sum().sum() == 0, "There are still missing values after preprocessing."
    logging.info(f"Final data shape: {df.shape}")
    
    # Save processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    input_file = '../data/overlay_A_train.csv'
    output_file = '../data/processed/overlay_A_train_cleaned.csv'
    preprocess_overlay(input_file, output_file)
