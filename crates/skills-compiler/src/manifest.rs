use std::collections::BTreeMap;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use crate::compiler::CompilationMetrics;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillArtifactEntry {
    pub skill_id: String,
    pub source_path: String,
    pub source_sha256: String,
    pub compiled_path: String,
    pub compiled_sha256: String,
    pub metrics: CompilationMetrics,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationManifest {
    pub compiler_version: String,
    pub timestamp_utc: String,
    pub total_skills: usize,
    pub total_source_tokens: usize,
    pub total_compiled_tokens: usize,
    pub aggregate_token_reduction_pct: f64,
    pub skills: BTreeMap<String, SkillArtifactEntry>,
}

pub fn compute_sha256(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    format!("{:x}", hasher.finalize())
}
