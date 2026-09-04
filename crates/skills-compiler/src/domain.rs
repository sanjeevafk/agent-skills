use clap::ValueEnum;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, ValueEnum, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum Domain {
    Architecture,
    Database,
    Devops,
    Sre,
    Security,
    Testing,
    General,
}

impl Domain {
    /// Default code compaction limit (lines) based on domain sensitivity
    pub fn default_code_lines(&self) -> usize {
        match self {
            Self::Testing => 18,      // Testing & QA requires deep mocking/test harness syntax
            Self::Architecture => 14, // Retains interface and boundary types
            Self::Database => 16,     // Retains SQL DDL and migration patterns
            Self::Devops => 14,       // Retains YAML/Dockerfile snippets
            Self::Sre => 14,          // Retains profiling/diagnosis commands
            Self::Security => 12,     // Policy-heavy; compact code to invariants
            Self::General => 14,
        }
    }
}
