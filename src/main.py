import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import psutil

def dataset_import(file_path=None):
    if file_path is None:
        base_path = os.getcwd()  # Get current working directory
        file_path = os.path.join(base_path, "polling_place_20240514.csv")
    df_raw = pl.read_csv(
        file_path,
        infer_schema_length=0,
        has_header=True,
        sep='\t',  # Use the correct parameter name
        encoding='utf-16',  # Adjust based on actual file encoding
        ignore_errors=True,  # Skip over problematic rows
    )
    return df_raw



def data_modeling(df_raw):
    # Drop rows with null values in critical columns
    df_edited = df_raw.drop_nulls(subset=["polling_place_id", "polling_place_name"])

    # Convert data types if necessary
    df_edited = df_edited.with_columns(
        [
            pl.col("polling_place_id").cast(pl.Int32),
            pl.col("zip").cast(pl.Int32),
            pl.col("election_dt").str.strptime(pl.Date, "%m/%d/%Y"),
        ]
    )

    return df_edited


def calculate_polling_places_per_county(df):
    return df.groupby("county_name").agg(
        pl.count("polling_place_id").alias("num_polling_places")
    )


def calculate_mean_polling_places(df_counts):
    return df_counts["num_polling_places"].mean()


def calculate_median_polling_places(df_counts):
    return df_counts["num_polling_places"].median()


def calculate_std_polling_places(df_counts):
    return df_counts["num_polling_places"].std()


def plot_polling_places_per_county(df, save_directory):
    # Ensure the directory exists
    os.makedirs(save_directory, exist_ok=True)

    # Calculate the number of polling places per county
    df_counts = df.groupby("county_name").agg(
        pl.count("polling_place_id").alias("num_polling_places")
    )

    # Convert to pandas DataFrame for plotting
    df_counts_pd = df_counts.to_pandas()

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_counts_pd,
        x="county_name",
        y="num_polling_places",
        palette="Spectral"
    )
    plt.title("Number of Polling Places per County")
    plt.xlabel("County Name")
    plt.ylabel("Number of Polling Places")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    plt.savefig(os.path.join(save_directory, "polling_places_per_county.png"))
    plt.close()

def main():
    # Load the dataset
    df_raw = dataset_import()

    # Model the data
    df_edited = data_modeling(df_raw)

    # Calculate statistics
    df_counts = calculate_polling_places_per_county(df_edited)
    mean_polling_places = calculate_mean_polling_places(df_counts)
    median_polling_places = calculate_median_polling_places(df_counts)
    std_polling_places = calculate_std_polling_places(df_counts)

    # Print calculated statistics
    print(f"Polling Places per County:\n{df_counts}\n")
    print(f"Mean Number of Polling Places per County: {mean_polling_places:.2f}")
    print(f"Median Number of Polling Places per County: {median_polling_places}")
    print(f"Standard Deviation: {std_polling_places:.2f}")

    # Define the save directory for plots
    save_directory = "."

    # Plot the data
    plot_polling_places_per_county(df_edited, save_directory)


if __name__ == "__main__":
    start_time = time.time()
    start_cpu = psutil.cpu_percent(interval=None)
    main()
    end_time = time.time()
    end_cpu = psutil.cpu_percent(interval=None)

    print(f"Execution time: {end_time - start_time} seconds")
    print(f"CPU usage: {end_cpu - start_cpu} %")
