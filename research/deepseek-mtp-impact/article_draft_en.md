# DeepSeek MTP: Structural Impact on Compute Systems, Chips, and Interconnects

## Working Outline

### Core Thesis
MTP fundamentally alters the compute-to-memory ratio of inference workloads, shifting them from memory-bound toward compute-bound. This shift restructures the ROI calculus across chips, interconnects, and memory hierarchies.

### Key Sections

1. **Compute Chip Angle**: MTP raises compute/KV-Cache ratio → inference approaches training-like compute intensity
2. **Communication Angle**: Small MTP favors large supernodes (low-latency); Large MTP favors high-bandwidth
3. **Supernode Domain**: Large EP's weight-bandwidth amortization suppressed → bottleneck shifts to communication
4. **Specialized Chips**: LPX/streaming chips face market suppression — SRAM-centric assumptions breaking
5. **On-chip Media**: Benefits domestic/storage media, mid-tier processes; hurts premium HBM bandwidth
6. **Compute Density**: Accelerates density stacking → next HBM growth cycle
7. **Memory Wall Myth**: Memory will be a problem again in 1-2 years
8. **Off-chip Media**: DDR may actually benefit
9. **Token Cost**: Exponential decline → sequence length doubling
10. **Industry Comparison**: DeepSeek vs Kimi3 — why only sparse scales

### Industry Comparisons to Cite
- NVIDIA H100/H200/B200: HBM bandwidth vs compute scaling
- Groq Trillium: SRAM-centric streaming architecture
- Cerebras WSE-3: Wafer-scale SRAM
- AMD MI300X: HBM3e bandwidth
- Google TPU v5p: MXU vs HBM balance
- DeepSeek V3: MTP mechanism (from tech report)
- Kimi3: Linear attention limitations

### Key Data Points Needed
- HBM bandwidth growth rate vs compute growth rate (per generation)
- SRAM vs HBM bandwidth/cost comparison
- MTP acceptance rate / speedup numbers from DeepSeek
- LPX architecture details
