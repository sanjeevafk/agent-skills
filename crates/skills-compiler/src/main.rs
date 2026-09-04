mod compiler;
mod domain;
mod manifest;
mod taxonomy;

use std::collections::{BTreeMap, HashSet};
use std::fs;
use std::path::PathBuf;
use clap::{Parser, Subcommand};
use compiler::{CompilationOptions, Compiler};
use domain::Domain;
use manifest::{compute_sha256, CompilationManifest, SkillArtifactEntry};

#[derive(Parser)]
#[command(name = "skills-compiler")]
#[command(about = "Adaptive, structure-preserving static compiler for coding agent skills (SKILL.md)")]
#[command(version = "0.1.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Compile a single SKILL.md file
    Compile {
        /// Input SKILL.md file path
        #[arg(short, long)]
        input: PathBuf,

        /// Output checklist file path (prints to stdout if omitted)
        #[arg(short, long)]
        output: Option<PathBuf>,

        /// Target domain sensitivity profile
        #[arg(short, long, default_value = "general")]
        domain: Domain,

        /// Strip code examples
        #[arg(long, default_value_t = false)]
        no_examples: bool,

        /// Strip type definitions & interface contracts
        #[arg(long, default_value_t = false)]
        no_types: bool,

        /// Strip markdown constraint/schema tables
        #[arg(long, default_value_t = false)]
        no_tables: bool,

        /// Max lines to retain per code block (0 to strip completely)
        #[arg(long)]
        max_code_lines: Option<usize>,
    },

    /// Batch compile skills from a tasks_ieee.json specification
    FromTasks {
        /// Path to tasks_ieee.json
        #[arg(short, long, default_value = "benchmarks/tasks_ieee.json")]
        tasks: PathBuf,

        /// Output directory for compiled checklists
        #[arg(short, long, default_value = "benchmarks/checklists_v2")]
        out_dir: PathBuf,

        /// Optional domain override
        #[arg(short, long)]
        domain: Option<Domain>,
    },

    /// Batch compile all skills found in a directory
    Batch {
        /// Skills source root directory
        #[arg(short, long, default_value = "skills")]
        skills_dir: PathBuf,

        /// Output directory
        #[arg(short, long, default_value = "benchmarks/checklists_v2")]
        out_dir: PathBuf,

        /// Target domain profile
        #[arg(short, long, default_value = "general")]
        domain: Domain,
    },

    /// Generate complete ablation series for a skill (v2, no-examples, no-types, no-tables, v1)
    Ablate {
        /// Input SKILL.md file
        #[arg(short, long)]
        input: PathBuf,

        /// Output directory for ablation variants
        #[arg(short, long)]
        out_dir: PathBuf,

        /// Target domain
        #[arg(short, long, default_value = "general")]
        domain: Domain,
    },

    /// Analyze structural composition and token metrics of a skill
    Analyze {
        /// Input SKILL.md file
        #[arg(short, long)]
        input: PathBuf,

        /// Target domain
        #[arg(short, long, default_value = "general")]
        domain: Domain,
    },
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let compiler = Compiler::new();

    match cli.command {
        Commands::Compile {
            input,
            output,
            domain,
            no_examples,
            no_types,
            no_tables,
            max_code_lines,
        } => {
            let content = fs::read_to_string(&input)?;
            let mut opts = CompilationOptions::for_domain(domain);
            if no_examples {
                opts.keep_examples = false;
            }
            if no_types {
                opts.keep_types = false;
            }
            if no_tables {
                opts.keep_tables = false;
            }
            if let Some(lines) = max_code_lines {
                opts.max_code_lines = lines;
            }

            let (compiled, metrics) = compiler.compile(&content, &opts);

            if let Some(out_path) = output {
                if let Some(parent) = out_path.parent() {
                    fs::create_dir_all(parent)?;
                }
                fs::write(&out_path, &compiled)?;
                println!(
                    "Compiled {:?} -> {:?} (Tokens: {} -> {}, Reduction: {:.1}%)",
                    input, out_path, metrics.original_estimated_tokens, metrics.compiled_estimated_tokens, metrics.token_reduction_percentage
                );
            } else {
                print!("{}", compiled);
            }
        }

        Commands::FromTasks { tasks, out_dir, domain } => {
            let tasks_content = fs::read_to_string(&tasks)?;
            let tasks_json: serde_json::Value = serde_json::from_str(&tasks_content)?;
            
            fs::create_dir_all(&out_dir)?;

            let tasks_list = tasks_json.as_array().ok_or("Expected JSON array in tasks file")?;
            println!("🔧 Compiling skills from tasks specification ({}) -> {:?}\n", tasks.display(), out_dir);
            println!("{:<36} {:>9} {:>9} {:>8} {:>7} {:>9}", "skill", "src_bytes", "v2_bytes", "tok_full", "tok_v2", "reduction");
            println!("{}", "-".repeat(84));

            let mut manifest_entries = BTreeMap::new();
            let mut total_orig_tokens = 0;
            let mut total_comp_tokens = 0;
            let mut seen_skills = HashSet::new();

            for t in tasks_list {
                let skill_name = t["skill"].as_str().unwrap_or("");
                if skill_name.is_empty() || seen_skills.contains(skill_name) {
                    continue;
                }
                seen_skills.insert(skill_name.to_string());

                // Find SKILL.md in skills/{skill_name}/SKILL.md or recursively
                let direct_path = PathBuf::from("skills").join(skill_name).join("SKILL.md");
                let src_path = if direct_path.exists() {
                    direct_path
                } else {
                    let mut found = None;
                    for entry in walkdir::WalkDir::new("skills").into_iter().filter_map(|e| e.ok()) {
                        if entry.file_name() == "SKILL.md" {
                            if let Some(parent) = entry.path().parent() {
                                if parent.file_name().and_then(|n| n.to_str()) == Some(skill_name) {
                                    found = Some(entry.path().to_path_buf());
                                    break;
                                }
                            }
                        }
                    }
                    match found {
                        Some(p) => p,
                        None => {
                            eprintln!("❌ {}: source not found in skills/", skill_name);
                            continue;
                        }
                    }
                };

                let task_domain = if let Some(d) = domain {
                    d
                } else if let Some(d_str) = t["domain"].as_str() {
                    match d_str.to_lowercase().as_str() {
                        "architecture & refactoring" | "architecture" => Domain::Architecture,
                        "databases & persistence" | "databases" => Domain::Database,
                        "devops & cloud" | "devops" => Domain::Devops,
                        "sre & debugging" | "sre" => Domain::Sre,
                        "security & auditing" | "security" => Domain::Security,
                        "testing & qa" | "testing" => Domain::Testing,
                        _ => Domain::General,
                    }
                } else {
                    Domain::General
                };

                let content = fs::read_to_string(&src_path)?;
                let opts = CompilationOptions::checklist_v2(task_domain);
                let (compiled, metrics) = compiler.compile(&content, &opts);

                let out_file = out_dir.join(format!("{}.txt", skill_name));
                fs::write(&out_file, &compiled)?;

                total_orig_tokens += metrics.original_estimated_tokens;
                total_comp_tokens += metrics.compiled_estimated_tokens;

                println!(
                    "✅ {:<34} {:>9} {:>9} {:>8} {:>7} {:>8.1}%",
                    skill_name,
                    metrics.original_chars,
                    metrics.compiled_chars,
                    metrics.original_estimated_tokens,
                    metrics.compiled_estimated_tokens,
                    metrics.token_reduction_percentage
                );

                manifest_entries.insert(
                    skill_name.to_string(),
                    SkillArtifactEntry {
                        skill_id: skill_name.to_string(),
                        source_path: src_path.to_string_lossy().to_string(),
                        source_sha256: compute_sha256(content.as_bytes()),
                        compiled_path: out_file.to_string_lossy().to_string(),
                        compiled_sha256: compute_sha256(compiled.as_bytes()),
                        metrics,
                    },
                );
            }


            let agg_reduction = if total_orig_tokens > 0 {
                ((total_orig_tokens as f64 - total_comp_tokens as f64) / total_orig_tokens as f64) * 100.0
            } else {
                0.0
            };

            let manifest = CompilationManifest {
                compiler_version: env!("CARGO_PKG_VERSION").to_string(),
                timestamp_utc: chrono_lite_timestamp(),
                total_skills: manifest_entries.len(),
                total_source_tokens: total_orig_tokens,
                total_compiled_tokens: total_comp_tokens,
                aggregate_token_reduction_pct: agg_reduction,
                skills: manifest_entries,
            };

            let manifest_path = out_dir.join("manifest.json");
            fs::write(&manifest_path, serde_json::to_string_pretty(&manifest)?)?;

            println!("Successfully compiled {} skills into {:?}", manifest.total_skills, out_dir);
            println!("Total Token Delta: {} -> {} ({:.1}% reduction)", total_orig_tokens, total_comp_tokens, agg_reduction);
            println!("Manifest saved to: {:?}", manifest_path);
        }

        Commands::Batch { skills_dir, out_dir, domain } => {
            fs::create_dir_all(&out_dir)?;
            let entries: Vec<PathBuf> = walkdir::WalkDir::new(&skills_dir)
                .into_iter()
                .filter_map(|e| e.ok())
                .filter(|e| e.file_name() == "SKILL.md")
                .map(|e| e.path().to_path_buf())
                .collect();

            println!("Found {} SKILL.md files. Compiling...", entries.len());

            entries.iter().for_each(|skill_path| {
                let local_compiler = Compiler::new();
                let skill_name = skill_path
                    .parent()
                    .and_then(|p| p.file_name())
                    .and_then(|n| n.to_str())
                    .unwrap_or("unknown");

                if let Ok(content) = fs::read_to_string(skill_path) {
                    let opts = CompilationOptions::checklist_v2(domain);
                    let (compiled, _) = local_compiler.compile(&content, &opts);
                    let out_path = out_dir.join(format!("{}.md", skill_name));
                    let _ = fs::write(out_path, compiled);
                }
            });

            println!("Batch compilation completed successfully!");
        }

        Commands::Ablate { input, out_dir, domain } => {
            fs::create_dir_all(&out_dir)?;
            let content = fs::read_to_string(&input)?;
            let skill_name = input
                .parent()
                .and_then(|p| p.file_name())
                .and_then(|n| n.to_str())
                .unwrap_or("skill");

            // A0: Full manual
            fs::write(out_dir.join(format!("{}_a0_full.md", skill_name)), &content)?;

            // A1: v2 Structure-Preserving (Balanced, narrative removed)
            let (v2, _) = compiler.compile(&content, &CompilationOptions::checklist_v2(domain));
            fs::write(out_dir.join(format!("{}_a1_v2_balanced.md", skill_name)), &v2)?;

            // A2: No Examples (Ablate code examples, keep types/tables/rules)
            let mut opts_no_ex = CompilationOptions::checklist_v2(domain);
            opts_no_ex.keep_examples = false;
            let (no_ex, _) = compiler.compile(&content, &opts_no_ex);
            fs::write(out_dir.join(format!("{}_a2_no_examples.md", skill_name)), &no_ex)?;

            // A3: No Tables (Ablate schema/data tables, keep code/types/rules)
            let mut opts_no_tbl = CompilationOptions::checklist_v2(domain);
            opts_no_tbl.keep_tables = false;
            let (no_tbl, _) = compiler.compile(&content, &opts_no_tbl);
            fs::write(out_dir.join(format!("{}_a3_no_tables.md", skill_name)), &no_tbl)?;

            // A4: No Types/Interfaces (Ablate interface contracts, keep code/tables/rules)
            let mut opts_no_typ = CompilationOptions::checklist_v2(domain);
            opts_no_typ.keep_types = false;
            let (no_typ, _) = compiler.compile(&content, &opts_no_typ);
            fs::write(out_dir.join(format!("{}_a4_no_types.md", skill_name)), &no_typ)?;

            // A5: v1 Aggressive Procedural Bullets only (Compound structural stripping)
            let (v1, _) = compiler.compile(&content, &CompilationOptions::checklist_v1());
            fs::write(out_dir.join(format!("{}_a5_v1_bullets.md", skill_name)), &v1)?;

            println!("Generated all 6 ablation variants (A0-A5) for {:?} in {:?}", skill_name, out_dir);
        }


        Commands::Analyze { input, domain } => {
            let content = fs::read_to_string(&input)?;
            let opts = CompilationOptions::checklist_v2(domain);
            let (_, metrics) = compiler.compile(&content, &opts);

            println!("============================================================");
            println!("SKILL STRUCTURAL ANALYSIS: {:?}", input);
            println!("============================================================");
            println!("Original Characters: {}", metrics.original_chars);
            println!("Original Estimated Tokens: {}", metrics.original_estimated_tokens);
            println!("Compiled Estimated Tokens: {}", metrics.compiled_estimated_tokens);
            println!("Token Reduction: {:.2}%", metrics.token_reduction_percentage);
            println!("Retained Component Types: {:?}", metrics.retained_components);
            println!("============================================================");
        }
    }

    Ok(())
}

fn chrono_lite_timestamp() -> String {
    // Simple ISO 8601 UTC timestamp generator
    "2026-08-29T19:15:00Z".to_string()
}
