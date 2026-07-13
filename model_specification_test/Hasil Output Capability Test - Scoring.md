# Scoring - Hasil Output Capability Test

Sumber output: `model_specification_test/results/Hasil  Output Capability Test.md`

Penilaian ini memakai rubrik dari `ALL_CAPABILITIES_COMPRESSED_WEBUI_TESTING.md`:

- `1.00`: lengkap, benar, format patuh.
- `0.75`: pass dengan minor issue.
- `0.50`: sebagian benar, tetapi belum pass level.
- `0.25`: mostly generik atau salah arah.
- `0.00`: gagal/hard fail.

Level pass jika skor minimal `0.60`. Assessed level adalah level tertinggi yang pass secara berurutan dari L1.

## Summary

| Metric | Value |
|---|---:|
| Average assessed level | 4.17 |
| Level 5 capability count | 18 |
| Level 4 capability count | 1 |
| Level 3 capability count | 0 |
| Level 2 capability count | 0 |
| Level 1 capability count | 2 |
| Level 0 capability count | 2 |

## Score Table

| # | Capability | L1 | L2 | L3 | L4 | L5 | Assessed Level | Notes |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | tool_calling | 1.00 | 1.00 | 1.00 | 1.00 | 0.50 | Level 4 - Expert | L1-L4 sangat sesuai. L5 belum mencakup logs/processes dan agregasi lengkap; hanya metrics + alert CPU. |
| 2 | vision | 0.75 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Grounded pada dashboard/alert, ada angka dan uncertainty. Minor issue: ada beberapa formatting artifact dan asumsi trend terbatas. |
| 3 | rag | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Sangat konsisten memakai SOP/context; L5 decision tree ringkas tetapi pass. |
| 4 | code_execution | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Kode dan desain cukup kuat. L4/L5 belum benar-benar lengkap untuk timeout/retry/concurrency, tapi pass. |
| 5 | terminal | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Command realistis dan aman secara umum. L5 masih desain, belum full script production. |
| 6 | json_mode | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | Level 0 - Not Qualified | Strict mode: output di dokumen tidak valid JSON karena ada escape Markdown seperti `cpu\_utilization` dan `\[`. Jika output asli dari web UI valid sebelum ditempel ke Markdown, nilai semantiknya bisa Level 5. Validasi dengan `jq`. |
| 7 | structured_output | 1.00 | 1.00 | 1.00 | 0.75 | 0.75 | Level 5 - Master | Format table/report/dashboard/conditional report terpenuhi. L5 pass, meski command structure masih generik. |
| 8 | multiturn | 0.75 | 0.50 | 0.75 | 0.75 | 0.75 | Level 1 - Basic | Retensi dan recovery bagus, tetapi L2 mengarang `srv-db-01` CPU 15% dan bertentangan dengan shared context jika context dipakai. Karena L2 fail, assessed level berhenti di L1. |
| 9 | streaming | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Dari dokumen, konten dan struktur lengkap. Runtime streaming seperti TTFT/smoothness tetap perlu observasi manual, jadi ini content-only score. |
| 10 | cot_reasoning | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Reasoning ringkas, prioritas jelas, ada counterfactual dan verification plan. |
| 11 | agent | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Observe-plan-act-verify terlihat. L5 punya guardrail HITL, rate limit, rollback. |
| 12 | web_search | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Sebagai simulated search strategy sangat baik dan tidak mengarang hasil real-time. Real web search belum terverifikasi. |
| 13 | file_ops | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Simulasi file ops aman, ada safety checks, checksum, sync, audit. Real file execution belum terverifikasi. |
| 14 | memory | 1.00 | 0.50 | 0.75 | 0.75 | 0.75 | Level 1 - Basic | L1 recall benar. L2 gagal karena `srv-db-01` dan `srv-app-05` tidak disimpan/diisi, hanya `[Pending Data]`. Karena L2 fail, assessed level berhenti di L1. |
| 15 | task_planning | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | Level 5 - Master | Sangat kuat: sequence, dependencies, parallel workstream, rollback, roadmap, KPI. |
| 16 | cron | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Cron syntax dan logging benar; L5 punya lock/failover/retry/audit. |
| 17 | messaging | 1.00 | 1.00 | 1.00 | 0.75 | 0.75 | Level 5 - Master | Alert, routing, ack tracking, escalation, multi-channel orchestration kuat. |
| 18 | session_search | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Simulasi strategi search dan knowledge graph baik. Actual session search belum terverifikasi. |
| 19 | clarifying | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | Level 5 - Master | Sangat kuat: pertanyaan relevan, diprioritaskan, dikelompokkan, ada alasan dan strategi bertahap. |
| 20 | delegation | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Role/team mapping dan enterprise governance baik. |
| 21 | skills | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Skill selection/combination/adaptation/evolution cukup kuat. |
| 22 | context_engine | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | Level 0 - Not Qualified | Output tampaknya mengulang jawaban `skills`, bukan menjawab prompt context_engine. Ini salah capability. |
| 23 | mixture_of_agents | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Bagian MoA sendiri kuat. Namun ada noise besar: sebelum MoA, model juga menjawab context_engine di section ini. Penalti format/noise diterapkan. |

## Cara Membaca Hasil

Hasil ini menunjukkan model kuat untuk output konseptual, planning, RAG, reasoning, agentic planning, delegation, messaging, cron, dan simulated tool workflows.

Capability yang perlu diuji ulang:

1. `json_mode`: ulangi langsung di web UI dan validasi raw output dengan JSON parser atau `jq`.
2. `context_engine`: ulangi prompt khusus karena output sekarang salah capability/tertukar dengan `skills`.
3. `memory`: ulangi multi-turn asli, bukan compressed prompt, karena L2 gagal menyimpan beberapa fakta.
4. `multiturn`: ulangi dengan shared context eksplisit agar tidak mengarang data `srv-db-01`.
5. `streaming`, `web_search`, `file_ops`, `session_search`: skor di atas masih simulasi/content-only; butuh tool/runtime aktual untuk keputusan final.

## Contoh Validasi JSON Mode

Simpan raw output JSON dari web UI ke file, lalu jalankan:

```bash
jq . output.json
```

Jika `jq` gagal parse, capability `json_mode` harus dinilai gagal untuk level yang outputnya tidak valid, meskipun isi semantiknya tampak benar.

## Recommendation

Untuk screening manual, model ini terlihat layak sampai Level 4-5 pada banyak capability konseptual. Namun jangan jadikan hasil ini keputusan final sebelum mengulang `json_mode`, `context_engine`, dan capability yang membutuhkan tool nyata.
