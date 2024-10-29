import unittest
import polars as pl
import os
from main import data_modeling, calculate_polling_places_per_county, calculate_mean_polling_places, calculate_median_polling_places, calculate_std_polling_places, generate_markdown_report

class TestPollingPlacesAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up a small mock dataset for testing."""
        data = {
            "polling_place_id": [1, 2, 3, 4, 5],
            "polling_place_name": ["Place A", "Place B", "Place C", "Place D", "Place E"],
            "county_name": ["County 1", "County 2", "County 1", "County 2", "County 3"],
            "zip": [12345, 23456, 12345, 23456, 34567],
            "election_dt": ["05/14/2024", "05/14/2024", "05/14/2024", "05/14/2024", "05/14/2024"]
        }
        self.df_mock = pl.DataFrame(data)
    
    def test_data_modeling(self):
        """Test the data_modeling function."""
        df_edited = data_modeling(self.df_mock)
        self.assertEqual(df_edited.shape[0], 5)
        self.assertEqual(df_edited.shape[1], 5)
        self.assertTrue("polling_place_id" in df_edited.columns)

    def test_polling_places_per_county(self):
        """Test the calculation of polling places per county."""
        df_edited = data_modeling(self.df_mock)
        df_counts = calculate_polling_places_per_county(df_edited)
        
        # 检查 County 1 的投票站数量
        county_1_count = df_counts.filter(pl.col("county_name") == "County 1")["num_polling_places"][0]
        self.assertEqual(county_1_count, 2)  # County 1 应该有 2 个投票站

    def test_statistics(self):
        """Test the mean, median, and standard deviation calculations."""
        df_edited = data_modeling(self.df_mock)
        df_counts = calculate_polling_places_per_county(df_edited)
        mean_polling_places = calculate_mean_polling_places(df_counts)
        median_polling_places = calculate_median_polling_places(df_counts)
        std_polling_places = calculate_std_polling_places(df_counts)

        self.assertAlmostEqual(mean_polling_places, 1.67, places=2)
        self.assertEqual(median_polling_places, 2)
        self.assertAlmostEqual(std_polling_places, 0.577, places=2)

    def test_generate_markdown_report(self):
        """Test the generation of the markdown report."""
        df_edited = data_modeling(self.df_mock)
        df_counts = calculate_polling_places_per_county(df_edited)
        mean_polling_places = calculate_mean_polling_places(df_counts)
        median_polling_places = calculate_median_polling_places(df_counts)
        std_polling_places = calculate_std_polling_places(df_counts)

        # Define the save directory
        save_directory = "."

        # Call the report generation function
        generate_markdown_report(df_counts, mean_polling_places, median_polling_places, std_polling_places, save_directory)

        # Check if the markdown file was created
        md_file_path = os.path.join(save_directory, 'polling_places_analysis_report.md')
        self.assertTrue(os.path.exists(md_file_path))

        # Clean up the created file after test
        if os.path.exists(md_file_path):
            os.remove(md_file_path)

if __name__ == '__main__':
    unittest.main()
