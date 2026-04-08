# Project Documentation (`doc.md`)

---
## 1. Project Overview

**Purpose**: The NGS Pipeline is a production‑grade bioinformatics workflow that transforms raw sequencing data (SRA accession) into a clinical‑ready variant interpretation report. It orchestrates data acquisition, quality control, trimming, alignment, post‑alignment processing, variant calling, annotation, protein‑impact analysis, and report generation.

**End‑to‑End Workflow**:
1. **Data Acquisition** – Download raw SRA data and convert to FASTQ.
2. **Initial QC** – Run FastQC (via `QualityControlModule`) on raw reads.
3. **Trimming** – Remove adapters/low‑quality bases.
4. **Post‑Trim QC** – Verify cleaned reads.
5. **Alignment** – Map reads to a reference genome.
6. **Post‑Alignment Processing** – Sorting, marking duplicates, base‑recalibration.
7. **Variant Calling** – Generate VCF using GATK / FreeBayes.
8. **Annotation** – Enrich variants with functional information.
9. **Protein‑Impact** – Predict amino‑acid changes.
10. **MultiQC Report** – Aggregate QC metrics.
11. **Clinical Report** – Render a polished HTML/PDF report.

---
## 2. Data Flow

```mermaid
flowchart TD
    A[User supplies SRA ID] --> B[DataAcquisitionModule]
    B --> C[QualityControlModule (raw)]
    C --> D[TrimmingModule]
    D --> E[QualityControlModule (trimmed)]
    E --> F[AlignmentModule]
    F --> G[PostAlignmentModule]
    G --> H[VariantCallingModule]
    H --> I[AnnotationModule]
    I --> J[ProteinImpactModule]
    J --> K[ReportGeneratorModule]
    K --> L[Final Clinical Report]
```

* **APIs / External tools**: `prefetch` & `fasterq-dump` (SRA Toolkit), `FastQC`, `BWA`/`bowtie2`, `samtools`, `GATK`, `FreeBayes`, `MultiQC`.
* Data moves as Python dictionaries (`self.results`) between pipeline stages, each stage persisting intermediate files under `config.output_dirs`.

---
## 3. Code Structure & Implementation Details

| Function / Class | File | Line(s) | Direct Link |
|------------------|------|---------|------------|
| **NGSPipeline** (orchestrator) | `main.py` | 98‑191 | [main.py](file:///d:/Projects/BCD/ngs-pipeline/main.py#L98-L191) |
| `parse_arguments` | `main.py` | 63‑96 | [main.py](file:///d:/Projects/BCD/ngs-pipeline/main.py#L63-L96) |
| `setup_logging` | `main.py` | 50‑61 | [main.py](file:///d:/Projects/BCD/ngs-pipeline/main.py#L50-L61) |
| **DataAcquisitionModule** | `modules/data_acquisition.py` | 17‑55, 71‑124 | [data_acquisition.py](file:///d:/Projects/BCD/ngs-pipeline/modules/data_acquisition.py#L17-L55) / [data_acquisition.py](file:///d:/Projects/BCD/ngs-pipeline/modules/data_acquisition.py#L71-L124) |
| **QualityControlModule** | `modules/quality_control.py` | 1‑120 (approx.) | [quality_control.py](file:///d:/Projects/BCD/ngs-pipeline/modules/quality_control.py) |
| **TrimmingModule** | `modules/trimming.py` | 1‑110 (approx.) | [trimming.py](file:///d:/Projects/BCD/ngs-pipeline/modules/trimming.py) |
| **AlignmentModule** | `modules/alignment.py` | 1‑140 (approx.) | [alignment.py](file:///d:/Projects/BCD/ngs-pipeline/modules/alignment.py) |
| **PostAlignmentModule** | `modules/post_alignment.py` | 1‑130 (approx.) | [post_alignment.py](file:///d:/Projects/BCD/ngs-pipeline/modules/post_alignment.py) |
| **VariantCallingModule** | `modules/variant_calling.py` | 1‑120 (approx.) | [variant_calling.py](file:///d:/Projects/BCD/ngs-pipeline/modules/variant_calling.py) |
| **AnnotationModule** | `modules/annotation.py` | 1‑115 (approx.) | [annotation.py](file:///d:/Projects/BCD/ngs-pipeline/modules/annotation.py) |
| **ProteinImpactModule** | `modules/protein_impact.py` | 1‑130 (approx.) | [protein_impact.py](file:///d:/Projects/BCD/ngs-pipeline/modules/protein_impact.py) |
| **ReportGeneratorModule** | `modules/report_generator.py` | 1‑150 (approx.) | [report_generator.py](file:///d:/Projects/BCD/ngs-pipeline/modules/report_generator.py) |

> **Note** – Line numbers are based on the current repository snapshot. If the file changes, adjust the links accordingly.

---
## 4. Functionality Breakdown

### 4.1 `NGSPipeline.run()`
* Coordinates all 11 steps, logs progress, and stores intermediate results in `self.results`.
* Each step creates a dedicated module instance (`DataAcquisitionModule`, `QualityControlModule`, …) passing the shared `config` and `logger`.

### 4.2 Modules (BaseModule → SpecificModule)
* All modules inherit from `BaseModule` (provides `self.config` and `self.logger`).
* Each module implements an `execute(input_data)` method returning a dictionary of output artefacts (file paths, metrics).
* Example: `DataAcquisitionModule.execute()` returns a dict of FASTQ file paths.

### 4.3 Reporting
* `ReportGeneratorModule.execute(results)` consumes the full `self.results` dict and produces an HTML report plus a PDF via `weasyprint`.
* `qc_module.generate_multiqc()` (called in step 10) aggregates all FastQC outputs into a single interactive HTML report.

---
## 5. Data Processing

1. **Acquisition** – `prefetch` pulls SRA bundles; `fasterq-dump` converts them to gzipped FASTQ files.
2. **QC (raw)** – FastQC generates per‑sample quality metrics (`fastqc.html`).
3. **Trimming** – `Trimmomatic` (or `cutadapt` if configured) removes adapters; paired‑end reads are split into `read1`/`read2`.
4. **QC (trimmed)** – FastQC re‑runs on trimmed files to verify improvement.
5. **Alignment** – `bwa mem` aligns reads to the reference; output is a sorted BAM (`samtools sort`).
6. **Post‑Alignment** – `samtools markdup` marks duplicates; `gatk BaseRecalibrator` performs BQSR.
7. **Variant Calling** – GATK HaplotypeCaller (or FreeBayes) produces a VCF; optionally both are run and merged.
8. **Annotation** – `VEP` or `ANNOVAR` adds gene, consequence, and population frequency annotations.
9. **Protein Impact** – `SnpEff` or custom scripts predict amino‑acid changes and functional impact scores.
10. **Aggregation** – `MultiQC` collates all QC HTMLs; `ReportGeneratorModule` builds a final HTML/PDF with tables, plots, and summary statistics.

---
## 6. Data Visualization

* **FastQC** – per‑sample quality plots (per‑base quality, GC content, duplication levels).
* **MultiQC** – a single dashboard combining all FastQC, alignment, and variant‑calling metrics.
* **ReportGeneratorModule** – uses **Matplotlib** / **Seaborn** to create:
  - Coverage depth histogram
  - Variant allele frequency distribution
  - Summary tables of pathogenic variants (ClinVar, dbSNP)
* Visualisations are embedded as `<img src="data:image/png;base64,…">` in the HTML report and exported to PDF.

---
## 7. End‑to‑End Workflow Walkthrough

1. **User invokes** the pipeline via the CLI (`python main.py --sra-id SRR123456 --sample-name sample1 --output-dir out --reference hg38.fa`).
2. `parse_arguments` builds a `PipelineConfig` object (see `configs/settings.py`).
3. `NGSPipeline` is instantiated with the config and a logger that writes to `pipeline_<timestamp>.log`.
4. **Step 1 – Data Acquisition**
   * `DataAcquisitionModule` checks for `prefetch`/`fasterq-dump`.
   * Calls `prefetch` → downloads `.sra` files.
   * Calls `fasterq-dump` → produces `sample1_1.fastq.gz` and `sample1_2.fastq.gz`.
5. **Step 2 – QC (raw)**
   * `QualityControlModule` runs FastQC on the raw FASTQ files, storing results under `output_dir/fastqc_raw/`.
6. **Step 3 – Trimming**
   * `TrimmingModule` executes Trimmomatic, writes trimmed FASTQ to `output_dir/trimmed/`.
7. **Step 4 – QC (trimmed)**
   * Same QC module validates trimmed reads.
8. **Step 5 – Alignment**
   * `AlignmentModule` runs `bwa mem` → SAM → sorted BAM (`aligned.bam`).
9. **Step 6 – Post‑Alignment**
   * Sorting, duplicate marking, and BQSR produce `processed.bam`.
10. **Step 7 – Variant Calling**
    * `VariantCallingModule` creates `variants.vcf` (GATK/FreeBayes).
11. **Step 8 – Annotation**
    * `AnnotationModule` enriches VCF → `annotated.vcf`.
12. **Step 9 – Protein Impact**
    * `ProteinImpactModule` adds protein‑level predictions → `protein_impact.tsv`.
13. **Step 10 – MultiQC Report**
    * `qc_module.generate_multiqc()` aggregates all FastQC HTMLs into `multiqc_report.html`.
14. **Step 11 – Clinical Report**
    * `ReportGeneratorModule` consumes the full `self.results` dict, builds an HTML dashboard (`clinical_report.html`) and a PDF (`clinical_report.pdf`).
15. **Pipeline Completion** – Summary printed to console and logged; all artefacts are available under the user‑specified output directory.

---
## 8. How to Use the Documentation

* Open `doc.md` in any markdown viewer (VS Code, GitHub, etc.).
* Click the **Direct Links** column to jump to the exact source line in the repository.
* The mermaid diagram visualises the data flow; most markdown renderers (GitHub, VS Code) render it automatically.
* For a printable version, run `pandoc doc.md -o doc.pdf`.

---
*Generated on 2026‑04‑08 by Antigravity.*
