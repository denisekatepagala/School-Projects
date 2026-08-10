import pandas as pd
import matplotlib.pyplot as plt

def load_and_clean(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.title()

    possible_price_cols = [c for c in df.columns if 'Price' in c]
    if not possible_price_cols:
        raise KeyError("No column found containing 'Price'")
    price_col = possible_price_cols[0]

    if 'Year' not in df.columns:
        possible_year_cols = [c for c in df.columns if 'Year' in c or 'Date' in c]
        if not possible_year_cols:
            raise KeyError("No column found containing 'Year' or 'Date'")
        year_col = possible_year_cols[0]
        if 'Date' in year_col:
            df[year_col] = pd.to_datetime(df[year_col], errors='coerce')
            df['Year'] = df[year_col].dt.year
        else:
            df['Year'] = pd.to_numeric(df[year_col], errors='coerce')

    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df = df.dropna(subset=['Year', price_col])
    df['Year'] = df['Year'].astype(int)
    df.rename(columns={price_col: 'Price'}, inplace=True)
    return df

def plot_average_price(df):
    avg_price_per_year = df.groupby('Year')['Price'].mean()
    plt.figure(figsize=(8, 5))
    plt.plot(avg_price_per_year.index, avg_price_per_year.values, marker='o', linestyle='-', linewidth=2)
    plt.title('Average Bread Price per Year')
    plt.xlabel('Year')
    plt.ylabel('Average Price')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    filepath = 'breadprice.csv'
    df = load_and_clean(filepath)
    plot_average_price(df)

if __name__ == "__main__":
    main()
