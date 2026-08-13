---
name: first-principles
description: Force rigorous first-principles reasoning on engineering, design, architecture, cost reduction, optimization, and system decisions. Use whenever analyzing costs, questioning best practices, designing architectures from the ground up, or solving hard problems from fundamental truths.
---

# Think from First Principles

Apply first-principles reasoning to break down problems to fundamental truths. Reject inherited conventions, industry consensus, and reasoning by analogy when you need breakthrough results.

## When to Activate

Activate this skill when you encounter:
- Architecture design, system design, or engineering decisions
- Cost analysis, efficiency optimization, or performance bottlenecks
- Questions like "Why is this expensive/slow?" or "What is the optimal way to build this?"
- Tasks that challenge industry standards or legacy patterns
- Feasibility evaluations ("Is X physically or mathematically possible?")

## Philosophical and Historical Foundation

Aristotle defined a first principle as the primary basis from which a thing is known. It is the irreducible foundation that you cannot deduce from anything prior. In physics, this is *ab initio* reasoning: start from established laws, not fitted parameters.

Elon Musk operationalized this approach for engineering:
1. Boil a problem down to its most fundamental, indisputable truths.
2. Reason up from those truths to construct the solution.

Reasoning by analogy copies others with minor tweaks. First-principles reasoning builds from fundamental limits.

## Canonical Examples

### 1. Rocket Manufacturing (SpaceX)
- **Convention**: Industry rocket cost was ~$65M.
- **Decomposition**: Raw materials (aluminum alloys, titanium, copper, carbon fiber) cost ~2% of total price.
- **Insight**: 98% of cost came from legacy manufacturing and overhead.
- **Solution**: SpaceX vertically integrated manufacturing, simplified design, and created reusable stages.

### 2. Battery Pack Costs (Tesla)
- **Convention**: Battery packs cost ~$600/kWh with minimal predicted reduction.
- **Decomposition**: Raw material spot prices (cobalt, nickel, aluminum, carbon, polymers, steel) totaled ~$80/kWh.
- **Insight**: High costs reflected processing inefficiency, not physical limits.
- **Solution**: Redesign cell chemistry and manufacturing processes to approach material limits.

**Core Metric**: The **Idiot Index** = Finished Cost ÷ Raw Material Cost. A high index highlights massive optimization potential.

## Mandatory Reasoning Protocol

Follow these five steps explicitly for non-trivial problems:

### 1. Surface and List All Assumptions
- Document every requirement, constraint, legacy process, and cost estimate.
- For each item, ask: "Is this a fundamental law or an inherited habit?"
- Challenge all unverified constraints.

### 2. Reduce to Fundamental Truths (Axioms)
Strip the problem down to irreducible realities:
- **Physics**: Conservation of mass/energy, thermodynamics, material limits.
- **Mathematics**: Complexity bounds, information theory, logical proofs.
- **Economics**: Spot market prices for raw inputs and commodities.
- **Empirical Facts**: Directly verified physical measurements.
- Discard all provisional or social assumptions.

### 3. Compute the Theoretical Floor
- Calculate the lower bound under ideal physical and mathematical conditions.
- Define this "magic-wand limit" as the benchmark.
- Measure the gap between current reality and the theoretical floor.

### 4. Rebuild from the Ground Up
- Construct the simplest solution using only verified axioms.
- Apply the 5-step engineering algorithm:
  1. Make requirements less dumb.
  2. Delete unnecessary parts or process steps.
  3. Simplify or optimize the remaining design.
  4. Accelerate cycle time.
  5. Automate only after optimizing.

### 5. Stress-Test and Iterate
- Attack your own conclusions. Try to disprove them.
- Test edge cases and extreme values ("thinking in the limit").
- Verify whether existing tools or libraries genuinely match the fundamental solution before building custom alternatives.

## Standard Output Format

When delivering first-principles analysis, use this structure:

### Assumptions Challenged
- [List conventional beliefs and why they fail or lack justification]

### Fundamental Truths Identified
- [List irreducible physical, mathematical, and logical axioms]

### Theoretical Floor (Magic-Wand Limit)
- [Calculate absolute minimum cost, time, complexity, or resource limits]

### Ground-Up Solution
- [Describe the clean architecture or design derived strictly from axioms]

### Comparison to Conventional Approaches
- [Explain specific advantages over standard methods]

### Remaining Uncertainties & Validation Steps
- [List empirical tests needed to verify key hypotheses]
