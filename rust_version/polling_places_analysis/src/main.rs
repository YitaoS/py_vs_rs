use polars::prelude::*;
use plotters::prelude::*;
use std::error::Error;
use std::fs;
use std::io::{BufReader, Cursor, Read};
use encoding_rs::UTF_16LE;
use encoding_rs_io::DecodeReaderBytesBuilder;
use heim::cpu;
use std::time::Instant;
use tokio::runtime::Runtime;

fn dataset_import(file_path: Option<&str>) -> Result<DataFrame, Box<dyn Error>> {
    let file_path = file_path.unwrap_or("polling_place_20240514.csv");
    
    // 手动读取文件并转换编码为 UTF-8
    let file = fs::File::open(file_path)?;
    let mut reader = BufReader::new(file);
    let mut decoder = DecodeReaderBytesBuilder::new()
        .encoding(Some(UTF_16LE))
        .build(&mut reader);
    let mut content = String::new();
    decoder.read_to_string(&mut content)?;

    // 使用 Cursor 包装字节数组，使其符合 `CsvReader` 的要求
    let cursor = Cursor::new(content.into_bytes());
    let df_raw = CsvReader::new(cursor)
        .with_delimiter(b'\t')
        .has_header(true)
        .finish()?;
    
    Ok(df_raw)
}

fn data_modeling(df_raw: &DataFrame) -> Result<DataFrame, PolarsError> {
    df_raw
        .clone()
        .lazy()
        .drop_nulls(Some(vec![col("polling_place_id"), col("polling_place_name")]))
        .with_column(col("polling_place_id").cast(DataType::Int32)) // 去掉 strict
        .with_column(
            col("election_dt")
                .str()
                .strptime(StrpTimeOptions { fmt: Some("%m/%d/%Y".into()), ..Default::default() })
        )
        .collect()
}

fn calculate_polling_places_per_county(df: &DataFrame) -> Result<DataFrame, PolarsError> {
    if df.height() == 0 {
        println!("Warning: DataFrame is empty.");
        return Ok(df.clone());
    }
    
    df.clone()
        .lazy()
        .groupby([col("county_name")])
        .agg([col("polling_place_id").count().alias("num_polling_places")])
        .collect()
}

fn calculate_mean_polling_places(df_counts: &DataFrame) -> Result<f64, PolarsError> {
    if df_counts.height() == 0 {
        return Ok(0.0);
    }
    Ok(df_counts.column("num_polling_places")?.mean().unwrap_or(0.0))
}

fn calculate_std_polling_places(df_counts: &DataFrame) -> Result<f64, PolarsError> {
    // 将转换后的列保存到一个变量中
    let float_column = df_counts
        .column("num_polling_places")?
        .cast(&DataType::Float64)?;
    
    let values = float_column.f64()?; // 确保转换后的列活得更久

    if values.is_empty() {
        return Ok(0.0);
    }
    
    let mean = values.mean().unwrap_or(0.0);
    let variance = values
        .into_iter()
        .map(|v| v.unwrap_or(0.0) - mean)
        .map(|diff| diff * diff)
        .sum::<f64>()
        / (values.len() as f64);
    Ok(variance.sqrt())
}


fn plot_polling_places_per_county(df: &DataFrame, save_directory: &str) -> Result<(), Box<dyn Error>> {
    let file_path = format!("{}/polling_places_per_county.png", save_directory);
    fs::create_dir_all(save_directory)?; // 确保目录存在
    let root = BitMapBackend::new(&file_path, (800, 600)).into_drawing_area();
    root.fill(&WHITE)?;
    
    let county_names: Vec<&str> = df.column("county_name")?.utf8()?.into_no_null_iter().collect();
    let polling_places: Vec<u32> = df.column("num_polling_places")?.u32()?.into_no_null_iter().collect();

    if polling_places.is_empty() {
        println!("Warning: No data to plot.");
        return Ok(());
    }

    let max_polling = *polling_places.iter().max().unwrap_or(&0);
    
    let mut chart = ChartBuilder::on(&root)
        .caption("Number of Polling Places per County", ("sans-serif", 20))
        .x_label_area_size(35)
        .y_label_area_size(40)
        .build_cartesian_2d(0..county_names.len() as i32, 0..max_polling as i32)?;

    for (index, &polling_count) in polling_places.iter().enumerate() {
        chart.draw_series(vec![Rectangle::new(
            [(index as i32, 0), (index as i32, polling_count as i32)],
            BLUE.filled(),
        )])?;
    }

    root.present()?;
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    // 创建异步运行时
    let rt = Runtime::new()?;

    // 记录开始时间
    let start_time = Instant::now();
    
    // 使用运行时执行异步操作以获取 CPU 使用时间
    let start_cpu = rt.block_on(async { cpu::time().await }).map(|time| time.user()).unwrap_or_default();

    // 导入和处理数据
    let df_raw = dataset_import(None)?;
    let df_edited = data_modeling(&df_raw)?;

    let df_counts = calculate_polling_places_per_county(&df_edited)?;
    let mean_polling_places = calculate_mean_polling_places(&df_counts)?;
    let std_polling_places = calculate_std_polling_places(&df_counts)?;

    println!("Mean Polling Places per County: {:.2}", mean_polling_places);
    println!("Standard Deviation: {:.2}", std_polling_places);

    // 绘图
    plot_polling_places_per_county(&df_counts, ".")?;

    // 记录执行时间和结束时的 CPU 使用率
    let duration = start_time.elapsed();
    let end_cpu = rt.block_on(async { cpu::time().await }).map(|time| time.user()).unwrap_or_default();

    println!("Execution time: {:?}", duration);
    println!(
        "CPU usage difference: {:?}%",
        end_cpu - start_cpu
    );

    Ok(())
}