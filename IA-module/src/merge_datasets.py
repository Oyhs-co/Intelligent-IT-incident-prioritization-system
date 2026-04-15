import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "it_tickets_merged.csv"


def clean_tags(tags_str):
    if pd.isna(tags_str):
        return ''
    tags_str = str(tags_str).strip("[]'").replace("'", "")
    return ', '.join([t.strip() for t in tags_str.split(',') if t.strip()])

def load_and_filter_multilang():
    df = pd.read_csv(f"{DATA_DIR}/aa_dataset-tickets-multi-lang-5-2-50-version.csv")
    df_en = df[df['language'] == 'en'].copy()
    combined = df_en['subject'].fillna('') + ' ' + df_en['body'].fillna('')
    text_col = combined.str.replace(r'\\n', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()
    tags_cols = [col for col in df_en.columns if col.startswith('tag_')]
    tags = df_en[tags_cols].apply(
        lambda row: ', '.join([str(v).replace("'", "").strip() for v in row.dropna() if str(v).strip()]), axis=1
    )
    return pd.DataFrame({
        'text': text_col,
        'priority': df_en['priority'],
        'department': df_en['queue'],
        'type': df_en['type'],
        'tags': tags
    })

def load_it_support():
    df = pd.read_csv(f"{DATA_DIR}/IT Support Ticket Data.csv")
    tags = df['Tags'].apply(clean_tags)
    text_col = df['Body'].str.replace(r'\\n', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()
    return pd.DataFrame({
        'text': text_col,
        'priority': df['Priority'],
        'department': df['Department'],
        'type': '',
        'tags': tags
    })

def normalize_priority(df):
    mapping = {'high': '1', 'medium': '2', 'low': '3'}
    df['priority'] = df['priority'].str.lower().map(mapping)
    return df.dropna(subset=['priority', 'text'])

def main():
    df1 = load_and_filter_multilang()
    df2 = load_it_support()
    df1['source'] = 'multilang'
    df2['source'] = 'it_support'
    merged = pd.concat([df1, df2], ignore_index=True)
    merged = normalize_priority(merged)
    merged['text'] = merged['text'].str.strip()
    merged = merged.dropna(subset=['text'])
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Merged: {len(merged)} rows")
    print(merged['priority'].value_counts())

if __name__ == "__main__":
    main()