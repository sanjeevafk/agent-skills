use serde::{Deserialize, Serialize};

/// 8 Information Component classes in the Skill Information Taxonomy
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum InformationComponent {
    /// Background, conversational introductions, historical motivation
    Narrative,
    /// High-level imperative directives ("Always use X", "Avoid Y")
    Policy,
    /// Sequential, ordered execution steps
    Procedure,
    /// Interface signatures, TypeScript/Python types, function contracts
    ApiContract,
    /// Concrete implementation code blocks and snippets
    Example,
    /// Concurrency locks, transaction isolation, security invariants
    Invariant,
    /// Structured markdown data/schema/parameter tables
    Table,
    /// Explicit edge-case handling and fallback branches
    Exception,
}

impl InformationComponent {
    #[allow(dead_code)]
    pub fn name(&self) -> &'static str {
        match self {
            Self::Narrative => "Narrative",
            Self::Policy => "Policy",
            Self::Procedure => "Procedure",
            Self::ApiContract => "ApiContract",
            Self::Example => "Example",
            Self::Invariant => "Invariant",
            Self::Table => "Table",
            Self::Exception => "Exception",
        }
    }
}
