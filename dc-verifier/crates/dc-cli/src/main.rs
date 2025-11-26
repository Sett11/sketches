use anyhow::Result;
use clap::Parser;

mod commands;
mod config;
mod reporters;

#[derive(Parser)]
#[command(name = "dc-verifier")]
#[command(about = "Data Chains Verifier - проверка целостности цепочек данных")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(clap::ValueEnum, Clone, Copy, Debug)]
pub enum ReportFormat {
    Markdown,
    Json,
}

#[derive(clap::Subcommand)]
enum Commands {
    /// Проверка цепочек данных
    Check {
        /// Путь к конфигурационному файлу
        #[arg(short, long, default_value = "dc-verifier.toml")]
        config: String,
        /// Формат отчета (markdown или json)
        #[arg(short, long, value_enum, default_value_t = ReportFormat::Markdown)]
        format: ReportFormat,
    },
    /// Создание конфигурационного файла
    Init {
        /// Путь для создания конфига
        #[arg(default_value = "dc-verifier.toml")]
        path: String,
    },
    /// Визуализация графов (опционально)
    Visualize {
        /// Путь к конфигурационному файлу
        #[arg(short, long, default_value = "dc-verifier.toml")]
        config: String,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Check { config, format } => {
            commands::check::execute_check(&config, format)?;
        }
        Commands::Init { path } => {
            commands::init::execute_init(&path)?;
        }
        Commands::Visualize { config } => {
            commands::visualize::execute_visualize(&config)?;
        }
    }

    Ok(())
}
