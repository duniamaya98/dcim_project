"""
Level-Based Test Definitions for All 23 Capabilities

Definisi lengkap test cases untuk setiap capability di 5 level kesulitan:
- Level 1: Basic (25% capacity) - Operasi sederhana, kompleksitas minimal
- Level 2: Intermediate (50% capacity) - Operasi standar, kompleksitas moderat
- Level 3: Advanced (75% capacity) - Operasi kompleks, kompleksitas tinggi
- Level 4: Expert (100% capacity) - Operasi sangat kompleks, kompleksitas maksimal
- Level 5: Master (125% capacity) - Operasi ekstrem, melebihi spesifikasi normal

Setiap test case memiliki:
- name: Nama test case (harus match dengan test file yang ada)
- distance_weight: Bobot kontribusi terhadap "jarak" yang ditempuh model (0-100)
- prompt: Prompt yang akan dikirim ke model
- expected_keywords: Keywords yang diharapkan dalam response
- scoring_criteria: Kriteria penilaian spesifik
"""

from enum import IntEnum

class TestLevel(IntEnum):
    LEVEL_1 = 1  # Basic - 25% capacity
    LEVEL_2 = 2  # Intermediate - 50% capacity
    LEVEL_3 = 3  # Advanced - 75% capacity
    LEVEL_4 = 4  # Expert - 100% capacity
    LEVEL_5 = 5  # Master - 125% capacity

# ============================================================================
# LEVEL DEFINITIONS FOR ALL 23 CAPABILITIES
# ============================================================================

LEVEL_DEFINITIONS = {
    "tool_calling": {
        "description": "Kemampuan memanggil fungsi/tools dengan parameter yang benar",
        TestLevel.LEVEL_1: [
            {
                "name": "single_tool_call",
                "distance_weight": 25,
                "prompt": "Cek CPU usage server srv-web-01",
                "expected_tool": "get_server_metrics",
                "expected_params": {"hostname": "srv-web-01"},
                "scoring": {"tool_match": 0.5, "param_match": 0.5}
            },
            {
                "name": "alert_tool_call",
                "distance_weight": 25,
                "prompt": "Kirim alert critical ke tim: server srv-db-01 down",
                "expected_tool": "send_alert",
                "expected_params": {"severity": "critical", "hostname": "srv-db-01"},
                "scoring": {"tool_match": 0.5, "param_match": 0.5}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "log_check_tool_call",
                "distance_weight": 30,
                "prompt": "Cek error logs server srv-app-05 dalam 1 jam terakhir",
                "expected_tool": "check_logs",
                "expected_params": {"hostname": "srv-app-05", "level": "error"},
                "scoring": {"tool_match": 0.4, "param_match": 0.6}
            },
            {
                "name": "multi_tool_selection",
                "distance_weight": 40,
                "prompt": "Server srv-web-03 lambat, cek metrics dan logs",
                "expected_tools": ["get_server_metrics", "check_logs"],
                "scoring": {"tool_match": 0.5, "param_match": 0.5}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_multi_tool",
                "distance_weight": 50,
                "prompt": "Server srv-db-02 high memory. Cek metrics, logs, dan top processes",
                "expected_tools": ["get_server_metrics", "check_logs", "get_top_processes"],
                "scoring": {"tool_match": 0.4, "param_match": 0.4, "sequence": 0.2}
            },
            {
                "name": "conditional_tool_calling",
                "distance_weight": 50,
                "prompt": "Jika CPU > 90% kirim alert, jika tidak cek logs",
                "expected_tools": ["get_server_metrics", "send_alert", "check_logs"],
                "scoring": {"tool_match": 0.3, "param_match": 0.3, "logic": 0.4}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "multi_step_workflow",
                "distance_weight": 75,
                "prompt": "Investigasi server srv-app-10: cek metrics -> jika CPU tinggi cek processes -> jika process aneh kill -> kirim alert",
                "expected_tools": ["get_server_metrics", "get_top_processes", "send_alert"],
                "scoring": {"tool_match": 0.3, "param_match": 0.3, "sequence": 0.2, "logic": 0.2}
            },
            {
                "name": "error_handling_tools",
                "distance_weight": 75,
                "prompt": "Cek metrics server srv-web-05. Jika timeout, retry 2x. Jika masih gagal, kirim alert",
                "expected_tools": ["get_server_metrics", "send_alert"],
                "scoring": {"tool_match": 0.3, "param_match": 0.3, "error_handling": 0.4}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_multi_tool",
                "distance_weight": 100,
                "prompt": "Monitoring 5 server sekaligus: srv-web-01, srv-web-02, srv-db-01, srv-db-02, srv-app-01. Cek semua metrics, logs, processes. Server dengan CPU > 85% kirim alert critical",
                "expected_tools": ["get_server_metrics", "check_logs", "get_top_processes", "send_alert"],
                "scoring": {"tool_match": 0.25, "param_match": 0.25, "sequence": 0.25, "logic": 0.25}
            },
            {
                "name": "parallel_tool_execution",
                "distance_weight": 100,
                "prompt": "Cek metrics semua server di cluster production secara paralel, aggregate hasilnya, kirim summary alert jika ada yang critical",
                "expected_tools": ["get_server_metrics", "send_alert"],
                "scoring": {"tool_match": 0.3, "param_match": 0.3, "parallelism": 0.2, "aggregation": 0.2}
            }
        ]
    },

    "vision": {
        "description": "Kemampuan analisis gambar dan visual data",
        TestLevel.LEVEL_1: [
            {
                "name": "simple_image_description",
                "distance_weight": 25,
                "prompt": "Deskripsikan apa yang kamu lihat di gambar ini",
                "expected_keywords": ["server", "dashboard", "cpu", "memory"],
                "scoring": {"keyword_match": 0.6, "accuracy": 0.4}
            },
            {
                "name": "basic_object_detection",
                "distance_weight": 25,
                "prompt": "Apa saja elemen yang ada di dashboard ini?",
                "expected_keywords": ["chart", "graph", "metric", "server"],
                "scoring": {"keyword_match": 0.6, "accuracy": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "dashboard_analysis",
                "distance_weight": 40,
                "prompt": "Analisis dashboard ini. Server mana yang bermasalah? Apa metrik yang ditampilkan?",
                "expected_keywords": ["server", "cpu", "memory", "warning", "srv-db-01"],
                "scoring": {"keyword_match": 0.4, "analysis": 0.4, "accuracy": 0.2}
            },
            {
                "name": "alert_interpretation",
                "distance_weight": 40,
                "prompt": "Apa yang ditampilkan di gambar ini? Apa severity alert-nya? Server mana yang terpengaruh?",
                "expected_keywords": ["alert", "critical", "server", "cpu", "memory", "srv-app-05"],
                "scoring": {"keyword_match": 0.4, "interpretation": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_dashboard_analysis",
                "distance_weight": 60,
                "prompt": "Analisis tren di dashboard ini. Server mana yang perlu perhatian segera? Berikan rekomendasi tindakan",
                "expected_keywords": ["trend", "recommendation", "action", "server", "priority"],
                "scoring": {"keyword_match": 0.3, "analysis": 0.4, "recommendation": 0.3}
            },
            {
                "name": "multi_image_comparison",
                "distance_weight": 60,
                "prompt": "Bandingkan kedua gambar ini. Apa perbedaannya? Mana yang lebih critical?",
                "expected_keywords": ["comparison", "difference", "critical", "server"],
                "scoring": {"keyword_match": 0.3, "comparison": 0.4, "accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "detailed_visual_analysis",
                "distance_weight": 80,
                "prompt": "Extract semua data numerik dari gambar ini. Hitung rata-rata CPU dan memory. Identifikasi anomali",
                "expected_keywords": ["average", "anomaly", "cpu", "memory", "numerical"],
                "scoring": {"extraction": 0.4, "calculation": 0.3, "anomaly_detection": 0.3}
            },
            {
                "name": "visual_data_extraction",
                "distance_weight": 80,
                "prompt": "Convert semua informasi di gambar ini ke format JSON terstruktur",
                "expected_keywords": ["json", "structured", "server", "metrics"],
                "scoring": {"extraction": 0.5, "formatting": 0.3, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_visual_reasoning",
                "distance_weight": 100,
                "prompt": "Berdasarkan gambar dashboard ini, prediksi apa yang akan terjadi dalam 1 jam ke depan. Berikan rekomendasi proactive actions",
                "expected_keywords": ["prediction", "proactive", "recommendation", "trend", "action"],
                "scoring": {"reasoning": 0.4, "prediction": 0.3, "recommendation": 0.3}
            },
            {
                "name": "3d_visualization_interpretation",
                "distance_weight": 100,
                "prompt": "Analisis diagram arsitektur 3D ini. Identifikasi single points of failure dan berikan rekomendasi redundancy",
                "expected_keywords": ["architecture", "failure", "redundancy", "recommendation"],
                "scoring": {"analysis": 0.4, "reasoning": 0.3, "recommendation": 0.3}
            }
        ]
    },

    "rag": {
        "description": "Retrieval Augmented Generation - kemampuan menggunakan konteks untuk menjawab",
        TestLevel.LEVEL_1: [
            {
                "name": "simple_document_retrieval",
                "distance_weight": 25,
                "prompt": "Berdasarkan SOP ini, apa yang harus dilakukan jika CPU > 90%?",
                "context_type": "sop_cpu_alert",
                "expected_keywords": ["top", "process", "cron", "kill"],
                "scoring": {"context_usage": 0.6, "accuracy": 0.4}
            },
            {
                "name": "basic_question_answering",
                "distance_weight": 25,
                "prompt": "Apa tanda-tanda memory leak menurut SOP?",
                "context_type": "sop_memory_leak",
                "expected_keywords": ["meningkat", "gc", "swap"],
                "scoring": {"context_usage": 0.6, "accuracy": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_document_retrieval",
                "distance_weight": 40,
                "prompt": "Berdasarkan SOP CPU dan Memory, apa langkah eskalasi untuk kedua kasus ini?",
                "context_type": "multiple",
                "expected_keywords": ["eskalasi", "tim", "10 menit"],
                "scoring": {"context_usage": 0.5, "synthesis": 0.3, "accuracy": 0.2}
            },
            {
                "name": "contextual_answering",
                "distance_weight": 40,
                "prompt": "Server srv-web-01 CPU 95% selama 7 menit. Apa yang harus dilakukan sesuai SOP?",
                "context_type": "sop_cpu_alert",
                "expected_keywords": ["top", "cron", "kill", "eskalasi"],
                "scoring": {"context_usage": 0.5, "application": 0.3, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_rag_chain",
                "distance_weight": 60,
                "prompt": "Berdasarkan semua SOP, buat checklist troubleshooting untuk server dengan CPU tinggi DAN memory leak bersamaan",
                "context_type": "multiple",
                "expected_keywords": ["checklist", "cpu", "memory", "troubleshooting"],
                "scoring": {"context_usage": 0.4, "synthesis": 0.4, "completeness": 0.2}
            },
            {
                "name": "multi_hop_reasoning",
                "distance_weight": 60,
                "prompt": "Jika CPU tinggi karena ETL job, apakah harus di-kill? Jelaskan berdasarkan SOP",
                "context_type": "sop_cpu_alert",
                "expected_keywords": ["etl", "biarkan", "selesai", "tidak kill"],
                "scoring": {"reasoning": 0.5, "context_usage": 0.3, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_context_understanding",
                "distance_weight": 80,
                "prompt": "Bandingkan SOP CPU alert dan Disk alert. Apa persamaan dan perbedaan langkah eskalasinya?",
                "context_type": "multiple",
                "expected_keywords": ["persamaan", "perbedaan", "eskalasi"],
                "scoring": {"comparison": 0.4, "context_usage": 0.4, "accuracy": 0.2}
            },
            {
                "name": "document_comparison",
                "distance_weight": 80,
                "prompt": "Dari semua SOP, mana yang paling critical untuk di-otomasi? Berikan justifikasi",
                "context_type": "multiple",
                "expected_keywords": ["otomasi", "critical", "justifikasi"],
                "scoring": {"analysis": 0.4, "justification": 0.4, "context_usage": 0.2}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_rag_scenario",
                "distance_weight": 100,
                "prompt": "Buat SOP baru yang mengintegrasikan semua SOP existing menjadi single comprehensive troubleshooting guide",
                "context_type": "multiple",
                "expected_keywords": ["sop", "integrasi", "comprehensive", "troubleshooting"],
                "scoring": {"synthesis": 0.4, "creativity": 0.3, "completeness": 0.3}
            },
            {
                "name": "multi_source_synthesis",
                "distance_weight": 100,
                "prompt": "Berdasarkan semua SOP, buat decision tree untuk troubleshooting server issues",
                "context_type": "multiple",
                "expected_keywords": ["decision", "tree", "troubleshooting", "flow"],
                "scoring": {"synthesis": 0.4, "structure": 0.3, "accuracy": 0.3}
            }
        ]
    },

    "code_execution": {
        "description": "Kemampuan generate dan execute code yang correct",
        TestLevel.LEVEL_1: [
            {
                "name": "simple_python_script",
                "distance_weight": 25,
                "prompt": "Buat script Python print 'Hello World'",
                "language": "python",
                "expected_keywords": ["print", "hello"],
                "scoring": {"syntax": 0.5, "execution": 0.5}
            },
            {
                "name": "basic_bash_command",
                "distance_weight": 25,
                "prompt": "Buat command bash untuk list semua file di directory current",
                "language": "bash",
                "expected_keywords": ["ls"],
                "scoring": {"syntax": 0.5, "correctness": 0.5}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "python_cpu_monitor",
                "distance_weight": 40,
                "prompt": "Buat script Python untuk monitoring CPU usage setiap 5 menit. Print timestamp dan CPU percentage. Jika CPU > 80%, print warning.",
                "language": "python",
                "expected_keywords": ["import", "time", "cpu", "percent", "print", "80"],
                "scoring": {"syntax": 0.3, "logic": 0.4, "execution": 0.3}
            },
            {
                "name": "bash_log_parser",
                "distance_weight": 40,
                "prompt": "Buat script bash untuk parse log file /var/log/syslog dan hitung jumlah error dalam 1 jam terakhir.",
                "language": "bash",
                "expected_keywords": ["grep", "error", "log", "count", "syslog"],
                "scoring": {"syntax": 0.4, "logic": 0.4, "correctness": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_script_generation",
                "distance_weight": 60,
                "prompt": "Buat script Python yang monitoring CPU, memory, disk. Jika ada yang > threshold, kirim alert ke file log. Run setiap 10 menit via cron",
                "language": "python",
                "expected_keywords": ["cpu", "memory", "disk", "threshold", "alert", "log", "cron"],
                "scoring": {"syntax": 0.3, "logic": 0.4, "completeness": 0.3}
            },
            {
                "name": "multi_language_execution",
                "distance_weight": 60,
                "prompt": "Buat script Python yang call bash command untuk get system info, parse hasilnya, dan output JSON",
                "language": "python",
                "expected_keywords": ["subprocess", "json", "parse", "system"],
                "scoring": {"syntax": 0.3, "integration": 0.4, "execution": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_system_script",
                "distance_weight": 80,
                "prompt": "Buat script Python comprehensive system monitor: CPU, memory, disk, network, processes. Generate report JSON. Auto-restart service jika crash",
                "language": "python",
                "expected_keywords": ["cpu", "memory", "disk", "network", "process", "report", "restart"],
                "scoring": {"syntax": 0.2, "logic": 0.3, "completeness": 0.3, "robustness": 0.2}
            },
            {
                "name": "error_handling_code",
                "distance_weight": 80,
                "prompt": "Buat script Python dengan error handling lengkap: try-except, retry logic, timeout, logging untuk monitoring system",
                "language": "python",
                "expected_keywords": ["try", "except", "retry", "timeout", "logging"],
                "scoring": {"syntax": 0.2, "error_handling": 0.5, "robustness": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_code_generation",
                "distance_weight": 100,
                "prompt": "Buat distributed monitoring system: monitor multiple servers, aggregate data, detect anomalies, auto-remediate, generate dashboard",
                "language": "python",
                "expected_keywords": ["distributed", "monitor", "aggregate", "anomaly", "remediate", "dashboard"],
                "scoring": {"architecture": 0.3, "logic": 0.3, "completeness": 0.2, "robustness": 0.2}
            },
            {
                "name": "parallel_execution",
                "distance_weight": 100,
                "prompt": "Buat script Python yang parallel monitoring 10 servers menggunakan threading/multiprocessing. Handle race conditions",
                "language": "python",
                "expected_keywords": ["threading", "multiprocessing", "parallel", "race", "condition"],
                "scoring": {"concurrency": 0.4, "logic": 0.3, "robustness": 0.3}
            }
        ]
    },

    "terminal": {
        "description": "Kemampuan execute terminal commands dan interpret output",
        TestLevel.LEVEL_1: [
            {
                "name": "simple_command_execution",
                "distance_weight": 25,
                "prompt": "Jalankan command: uname -a",
                "expected_output_contains": ["Linux"],
                "scoring": {"execution": 0.6, "output_correct": 0.4}
            },
            {
                "name": "basic_process_listing",
                "distance_weight": 25,
                "prompt": "List semua process yang sedang running",
                "expected_output_contains": ["PID"],
                "scoring": {"execution": 0.6, "output_correct": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "check_cpu_usage",
                "distance_weight": 40,
                "prompt": "Check CPU usage saat ini",
                "expected_output_contains": ["cpu", "percent"],
                "scoring": {"execution": 0.5, "output_correct": 0.3, "interpretation": 0.2}
            },
            {
                "name": "list_processes",
                "distance_weight": 40,
                "prompt": "List top 10 processes by CPU usage",
                "expected_output_contains": ["PID", "CPU"],
                "scoring": {"execution": 0.5, "output_correct": 0.3, "interpretation": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_terminal_workflow",
                "distance_weight": 60,
                "prompt": "Check CPU usage, jika > 80% list top processes, save ke file report.txt",
                "expected_output_contains": ["report.txt"],
                "scoring": {"workflow": 0.4, "execution": 0.3, "output_correct": 0.3}
            },
            {
                "name": "multi_command_sequence",
                "distance_weight": 60,
                "prompt": "Check disk usage, find large files > 1GB, list them sorted by size",
                "expected_output_contains": ["GB", "sort"],
                "scoring": {"sequence": 0.4, "execution": 0.3, "output_correct": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_system_monitoring",
                "distance_weight": 80,
                "prompt": "Create monitoring script: check CPU, memory, disk every 5 minutes. Log to file. Alert if threshold exceeded",
                "expected_output_contains": ["monitor", "log", "alert"],
                "scoring": {"script": 0.4, "execution": 0.3, "robustness": 0.3}
            },
            {
                "name": "error_recovery_commands",
                "distance_weight": 80,
                "prompt": "Check if service nginx running. If not, start it. If start fails, check logs and report error",
                "expected_output_contains": ["nginx", "start", "log"],
                "scoring": {"error_handling": 0.4, "execution": 0.3, "recovery": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_terminal_automation",
                "distance_weight": 100,
                "prompt": "Create automated monitoring system: monitor all system resources, auto-remediate common issues, generate daily report, send email alert",
                "expected_output_contains": ["monitor", "remediate", "report", "email"],
                "scoring": {"automation": 0.4, "execution": 0.3, "completeness": 0.3}
            },
            {
                "name": "parallel_command_execution",
                "distance_weight": 100,
                "prompt": "Run system checks in parallel: CPU, memory, disk, network. Aggregate results. Show summary",
                "expected_output_contains": ["parallel", "aggregate", "summary"],
                "scoring": {"parallelism": 0.4, "execution": 0.3, "aggregation": 0.3}
            }
        ]
    },

    "json_mode": {
        "description": "Kemampuan menghasilkan output JSON yang valid",
        TestLevel.LEVEL_1: [
            {
                "name": "simple_json",
                "distance_weight": 25,
                "prompt": "Output server status sebagai JSON: hostname=srv-web-01, cpu=85, memory=72, status=warning",
                "expected_fields": ["hostname", "cpu", "memory", "status"],
                "scoring": {"valid_json": 0.5, "field_match": 0.5}
            },
            {
                "name": "basic_json_schema",
                "distance_weight": 25,
                "prompt": "Output JSON dengan format: {name: string, age: number}",
                "expected_fields": ["name", "age"],
                "scoring": {"valid_json": 0.5, "schema_compliance": 0.5}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "nested_json",
                "distance_weight": 40,
                "prompt": "Output sebagai JSON: server srv-db-01 dengan metrics {cpu: 90, memory: 88} dan anomalies [{type: memory_leak, severity: high}]",
                "expected_fields": ["server", "metrics", "anomalies"],
                "scoring": {"valid_json": 0.4, "nested_structure": 0.4, "field_match": 0.2}
            },
            {
                "name": "array_json",
                "distance_weight": 40,
                "prompt": "Output sebagai JSON array: 3 server dengan hostname, cpu, memory",
                "expected_fields": ["hostname", "cpu", "memory"],
                "scoring": {"valid_json": 0.4, "array_structure": 0.4, "field_match": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "schema_compliance",
                "distance_weight": 60,
                "prompt": "Output JSON sesuai schema kompleks: {hostname: string, metrics: {cpu: number, memory: number}, alerts: array of {type: string, severity: string}}",
                "expected_fields": ["hostname", "metrics", "alerts"],
                "scoring": {"valid_json": 0.3, "schema_compliance": 0.5, "field_match": 0.2}
            },
            {
                "name": "json_with_explanation",
                "distance_weight": 60,
                "prompt": "Jelaskan kondisi server dalam format JSON dengan fields: summary, metrics, recommendations",
                "expected_fields": ["summary", "metrics", "recommendations"],
                "scoring": {"valid_json": 0.3, "content_quality": 0.4, "field_match": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "complex_json_schema",
                "distance_weight": 80,
                "prompt": "Output JSON dengan nested objects, arrays, dan conditional fields berdasarkan server status",
                "expected_fields": ["server", "metrics", "alerts", "recommendations"],
                "scoring": {"valid_json": 0.3, "complexity": 0.4, "schema_compliance": 0.3}
            },
            {
                "name": "json_validation",
                "distance_weight": 80,
                "prompt": "Generate JSON yang valid untuk 5 servers dengan metrics lengkap. Validate semua fields required",
                "expected_fields": ["hostname", "cpu", "memory", "disk", "status"],
                "scoring": {"valid_json": 0.3, "validation": 0.4, "completeness": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_json_generation",
                "distance_weight": 100,
                "prompt": "Generate JSON configuration untuk monitoring system dengan 50+ fields, nested structures, arrays, dan conditional logic",
                "expected_fields": ["monitoring", "configuration", "servers", "alerts"],
                "scoring": {"valid_json": 0.3, "complexity": 0.4, "completeness": 0.3}
            },
            {
                "name": "json_transformation",
                "distance_weight": 100,
                "prompt": "Transform JSON input ke format output yang berbeda dengan mapping fields, aggregations, dan filtering",
                "expected_fields": ["transformed", "aggregated", "filtered"],
                "scoring": {"transformation": 0.4, "valid_json": 0.3, "accuracy": 0.3}
            }
        ]
    },

    "structured_output": {
        "description": "Kemampuan menghasilkan output terstruktur sesuai format",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_structured_output",
                "distance_weight": 25,
                "prompt": "Output daftar 3 server dalam format table: hostname, cpu, memory",
                "expected_format": "table",
                "scoring": {"format_compliance": 0.6, "content_accuracy": 0.4}
            },
            {
                "name": "simple_list_output",
                "distance_weight": 25,
                "prompt": "Buat list langkah troubleshooting CPU tinggi dalam format numbered list",
                "expected_format": "numbered_list",
                "scoring": {"format_compliance": 0.6, "content_accuracy": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "markdown_table",
                "distance_weight": 40,
                "prompt": "Buat markdown table comparison 3 servers: hostname, cpu, memory, status, recommendation",
                "expected_format": "markdown_table",
                "scoring": {"format_compliance": 0.5, "content_accuracy": 0.3, "completeness": 0.2}
            },
            {
                "name": "structured_report",
                "distance_weight": 40,
                "prompt": "Buat report server status dengan sections: Summary, Details, Recommendations",
                "expected_format": "structured_report",
                "scoring": {"format_compliance": 0.5, "content_accuracy": 0.3, "structure": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_structured_output",
                "distance_weight": 60,
                "prompt": "Buat comprehensive report dengan: executive summary, detailed metrics table, trend analysis, action items",
                "expected_format": "comprehensive_report",
                "scoring": {"format_compliance": 0.4, "content_accuracy": 0.3, "structure": 0.3}
            },
            {
                "name": "multi_format_output",
                "distance_weight": 60,
                "prompt": "Output data dalam 3 format: table, JSON, dan bullet points",
                "expected_format": "multi_format",
                "scoring": {"format_compliance": 0.4, "content_accuracy": 0.3, "consistency": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_structured_output",
                "distance_weight": 80,
                "prompt": "Buat dashboard report dengan: KPI summary, trend charts (ASCII), detailed tables, recommendations prioritized",
                "expected_format": "dashboard_report",
                "scoring": {"format_compliance": 0.3, "content_accuracy": 0.3, "structure": 0.2, "visualization": 0.2}
            },
            {
                "name": "conditional_structured_output",
                "distance_weight": 80,
                "prompt": "Buat report yang formatnya berubah berdasarkan severity: critical (detailed), warning (summary), normal (brief)",
                "expected_format": "conditional",
                "scoring": {"conditional_logic": 0.4, "format_compliance": 0.3, "content_accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_structured_output",
                "distance_weight": 100,
                "prompt": "Generate complete documentation package: executive summary, technical details, API specs, troubleshooting guide, all in structured format",
                "expected_format": "documentation_package",
                "scoring": {"completeness": 0.4, "format_compliance": 0.3, "structure": 0.3}
            },
            {
                "name": "dynamic_structured_output",
                "distance_weight": 100,
                "prompt": "Create adaptive report that changes structure based on input data patterns and user preferences",
                "expected_format": "dynamic",
                "scoring": {"adaptability": 0.4, "format_compliance": 0.3, "intelligence": 0.3}
            }
        ]
    },

    "multiturn": {
        "description": "Kemampuan maintain context dalam multi-turn conversation",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_context_retention",
                "distance_weight": 25,
                "prompt": "Turn 1: Server srv-web-01 CPU tinggi. Turn 2: Apa yang harus dilakukan?",
                "expected_context": ["srv-web-01", "cpu"],
                "scoring": {"context_retention": 0.6, "response_quality": 0.4}
            },
            {
                "name": "simple_follow_up",
                "distance_weight": 25,
                "prompt": "Turn 1: Check server metrics. Turn 2: Server mana yang kamu cek?",
                "expected_context": ["server", "metrics"],
                "scoring": {"context_retention": 0.6, "response_quality": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_turn_context",
                "distance_weight": 40,
                "prompt": "Turn 1: Monitor srv-web-01. Turn 2: CPU nya berapa? Turn 3: Apa rekomendasi untuk server itu?",
                "expected_context": ["srv-web-01", "cpu", "recommendation"],
                "scoring": {"context_retention": 0.5, "consistency": 0.3, "response_quality": 0.2}
            },
            {
                "name": "context_switching",
                "distance_weight": 40,
                "prompt": "Turn 1: Check srv-web-01. Turn 2: Sekarang check srv-db-01. Turn 3: Bandingkan keduanya",
                "expected_context": ["srv-web-01", "srv-db-01", "comparison"],
                "scoring": {"context_retention": 0.4, "switching": 0.4, "response_quality": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_multi_turn",
                "distance_weight": 60,
                "prompt": "Turn 1-5: Troubleshooting session dengan multiple servers, context changes, dan follow-up questions",
                "expected_context": ["multiple_servers", "troubleshooting", "follow_up"],
                "scoring": {"context_retention": 0.4, "consistency": 0.3, "reasoning": 0.3}
            },
            {
                "name": "context_recovery",
                "distance_weight": 60,
                "prompt": "Turn 1-3: Discuss server A. Turn 4: Switch to server B. Turn 5: Back to server A - what was the issue?",
                "expected_context": ["server_a", "server_b", "recovery"],
                "scoring": {"context_retention": 0.4, "recovery": 0.4, "response_quality": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_multi_turn",
                "distance_weight": 80,
                "prompt": "Turn 1-10: Complex troubleshooting session dengan multiple context switches, clarifications, dan decisions",
                "expected_context": ["complex_session", "multiple_contexts", "decisions"],
                "scoring": {"context_retention": 0.3, "consistency": 0.3, "reasoning": 0.2, "decision_quality": 0.2}
            },
            {
                "name": "context_summarization",
                "distance_weight": 80,
                "prompt": "Turn 1-8: Long discussion. Turn 9: Summarize semua yang sudah kita discuss",
                "expected_context": ["summary", "all_contexts"],
                "scoring": {"summarization": 0.5, "context_retention": 0.3, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_multi_turn",
                "distance_weight": 100,
                "prompt": "Turn 1-20: Extended troubleshooting session dengan multiple servers, SOP references, decisions, dan follow-ups",
                "expected_context": ["extended_session", "all_contexts", "decisions"],
                "scoring": {"context_retention": 0.3, "consistency": 0.3, "reasoning": 0.2, "decision_quality": 0.2}
            },
            {
                "name": "context_evolution",
                "distance_weight": 100,
                "prompt": "Turn 1-15: Session dimana context evolves dan model harus track changes dan adapt recommendations",
                "expected_context": ["evolving_context", "adaptation", "tracking"],
                "scoring": {"adaptation": 0.4, "context_retention": 0.3, "reasoning": 0.3}
            }
        ]
    },

    "streaming": {
        "description": "Kemampuan streaming response yang smooth dan complete",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_streaming",
                "distance_weight": 25,
                "prompt": "Generate response pendek dengan streaming enabled",
                "expected_behavior": "streaming_chunks",
                "scoring": {"streaming_works": 0.6, "completeness": 0.4}
            },
            {
                "name": "simple_stream_complete",
                "distance_weight": 25,
                "prompt": "List 5 items dengan streaming",
                "expected_behavior": "complete_stream",
                "scoring": {"streaming_works": 0.6, "completeness": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "medium_stream",
                "distance_weight": 40,
                "prompt": "Generate paragraph penjelasan tentang monitoring server dengan streaming",
                "expected_behavior": "smooth_stream",
                "scoring": {"streaming_works": 0.5, "smoothness": 0.3, "completeness": 0.2}
            },
            {
                "name": "stream_with_structure",
                "distance_weight": 40,
                "prompt": "Generate structured report dengan streaming: summary, details, recommendations",
                "expected_behavior": "structured_stream",
                "scoring": {"streaming_works": 0.4, "structure": 0.4, "completeness": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "long_stream",
                "distance_weight": 60,
                "prompt": "Generate comprehensive troubleshooting guide dengan streaming (panjang)",
                "expected_behavior": "long_stream",
                "scoring": {"streaming_works": 0.4, "completeness": 0.3, "consistency": 0.3}
            },
            {
                "name": "stream_with_code",
                "distance_weight": 60,
                "prompt": "Generate penjelasan dengan code examples dalam streaming",
                "expected_behavior": "code_stream",
                "scoring": {"streaming_works": 0.4, "code_quality": 0.3, "completeness": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "complex_stream",
                "distance_weight": 80,
                "prompt": "Generate multi-section document dengan streaming: executive summary, technical details, code examples, recommendations",
                "expected_behavior": "complex_stream",
                "scoring": {"streaming_works": 0.3, "structure": 0.3, "completeness": 0.2, "consistency": 0.2}
            },
            {
                "name": "stream_error_handling",
                "distance_weight": 80,
                "prompt": "Generate response panjang dengan streaming. Simulate interruption dan verify recovery",
                "expected_behavior": "error_recovery_stream",
                "scoring": {"error_handling": 0.5, "recovery": 0.3, "completeness": 0.2}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_stream",
                "distance_weight": 100,
                "prompt": "Generate complete documentation (5000+ tokens) dengan streaming. Verify completeness dan consistency",
                "expected_behavior": "extreme_stream",
                "scoring": {"streaming_works": 0.3, "completeness": 0.3, "consistency": 0.2, "performance": 0.2}
            },
            {
                "name": "stream_with_interruption",
                "distance_weight": 100,
                "prompt": "Generate response dengan streaming. Interrupt di tengah, resume, verify context maintained",
                "expected_behavior": "interrupt_resume_stream",
                "scoring": {"interruption_handling": 0.4, "context_retention": 0.3, "recovery": 0.3}
            }
        ]
    },

    "cot_reasoning": {
        "description": "Chain-of-Thought reasoning capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_cot",
                "distance_weight": 25,
                "prompt": "Server CPU 95%. Apa yang harus dilakukan? Jelaskan step by step",
                "expected_reasoning": ["step_by_step", "logical"],
                "scoring": {"reasoning_present": 0.5, "logic_quality": 0.5}
            },
            {
                "name": "simple_reasoning",
                "distance_weight": 25,
                "prompt": "Kenapa server bisa down? Jelaskan proses berpikir kamu",
                "expected_reasoning": ["cause_analysis", "step_by_step"],
                "scoring": {"reasoning_present": 0.5, "logic_quality": 0.5}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "moderate_cot",
                "distance_weight": 40,
                "prompt": "Server lambat. Analyze possible causes step by step, then recommend actions",
                "expected_reasoning": ["cause_analysis", "step_by_step", "recommendation"],
                "scoring": {"reasoning_present": 0.4, "logic_quality": 0.4, "completeness": 0.2}
            },
            {
                "name": "comparative_reasoning",
                "distance_weight": 40,
                "prompt": "Compare two troubleshooting approaches. Which is better and why? Show your reasoning",
                "expected_reasoning": ["comparison", "evaluation", "justification"],
                "scoring": {"reasoning_present": 0.4, "comparison_quality": 0.4, "justification": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_cot",
                "distance_weight": 60,
                "prompt": "Server dengan CPU tinggi DAN memory leak. Analyze root cause step by step, consider interactions, recommend solution",
                "expected_reasoning": ["root_cause", "interaction_analysis", "solution"],
                "scoring": {"reasoning_present": 0.3, "depth": 0.4, "solution_quality": 0.3}
            },
            {
                "name": "multi_factor_reasoning",
                "distance_weight": 60,
                "prompt": "Analyze server issue considering: hardware, software, network, and human factors. Show reasoning for each",
                "expected_reasoning": ["multi_factor", "systematic", "comprehensive"],
                "scoring": {"reasoning_present": 0.3, "comprehensiveness": 0.4, "logic_quality": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_cot",
                "distance_weight": 80,
                "prompt": "Complex incident: multiple servers failing. Analyze cascade effects, root cause, and recovery plan with detailed reasoning",
                "expected_reasoning": ["cascade_analysis", "root_cause", "recovery_plan"],
                "scoring": {"reasoning_present": 0.3, "depth": 0.3, "completeness": 0.2, "solution_quality": 0.2}
            },
            {
                "name": "counterfactual_reasoning",
                "distance_weight": 80,
                "prompt": "What if we had implemented monitoring earlier? Analyze how incident would have been different. Show reasoning",
                "expected_reasoning": ["counterfactual", "analysis", "comparison"],
                "scoring": {"reasoning_present": 0.3, "counterfactual_quality": 0.4, "logic_quality": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_cot",
                "distance_weight": 100,
                "prompt": "Analyze complex multi-system failure with cascading effects. Consider all possible root causes, interactions, and recovery strategies. Show complete reasoning chain",
                "expected_reasoning": ["complete_chain", "multi_system", "comprehensive"],
                "scoring": {"reasoning_present": 0.3, "depth": 0.3, "completeness": 0.2, "solution_quality": 0.2}
            },
            {
                "name": "meta_reasoning",
                "distance_weight": 100,
                "prompt": "Analyze your own reasoning process. What assumptions did you make? What could be wrong? How would you verify?",
                "expected_reasoning": ["meta_cognition", "self_reflection", "verification"],
                "scoring": {"meta_reasoning": 0.5, "self_awareness": 0.3, "verification": 0.2}
            }
        ]
    },

    "agent": {
        "description": "Agent capabilities - planning, tool use, decision making",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_agent_task",
                "distance_weight": 25,
                "prompt": "Check server metrics dan report hasilnya",
                "expected_behavior": ["plan", "execute", "report"],
                "scoring": {"planning": 0.4, "execution": 0.4, "reporting": 0.2}
            },
            {
                "name": "simple_agent_workflow",
                "distance_weight": 25,
                "prompt": "Monitor server dan alert jika ada masalah",
                "expected_behavior": ["monitor", "detect", "alert"],
                "scoring": {"planning": 0.4, "execution": 0.4, "alerting": 0.2}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_step_agent",
                "distance_weight": 40,
                "prompt": "Investigate server issue: check metrics -> analyze logs -> recommend action",
                "expected_behavior": ["investigate", "analyze", "recommend"],
                "scoring": {"planning": 0.3, "execution": 0.4, "analysis": 0.3}
            },
            {
                "name": "conditional_agent",
                "distance_weight": 40,
                "prompt": "Monitor server. If CPU > 90%, check processes. If suspicious process, kill it",
                "expected_behavior": ["monitor", "conditional", "action"],
                "scoring": {"conditional_logic": 0.4, "execution": 0.4, "decision_quality": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_agent_workflow",
                "distance_weight": 60,
                "prompt": "Full incident response: detect -> investigate -> analyze -> remediate -> report -> prevent",
                "expected_behavior": ["full_lifecycle", "autonomous", "comprehensive"],
                "scoring": {"planning": 0.3, "execution": 0.3, "completeness": 0.2, "autonomy": 0.2}
            },
            {
                "name": "adaptive_agent",
                "distance_weight": 60,
                "prompt": "Handle server issue. Adapt approach based on findings. Show decision reasoning",
                "expected_behavior": ["adaptive", "reasoning", "decision"],
                "scoring": {"adaptability": 0.4, "reasoning": 0.3, "execution": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_agent",
                "distance_weight": 80,
                "prompt": "Manage multiple server incidents simultaneously. Prioritize, allocate resources, resolve",
                "expected_behavior": ["multi_task", "prioritization", "resolution"],
                "scoring": {"multi_tasking": 0.3, "prioritization": 0.3, "execution": 0.2, "resolution": 0.2}
            },
            {
                "name": "learning_agent",
                "distance_weight": 80,
                "prompt": "Handle incident. Learn from outcome. Improve approach for next incident",
                "expected_behavior": ["learning", "improvement", "adaptation"],
                "scoring": {"learning": 0.4, "adaptation": 0.3, "execution": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_agent",
                "distance_weight": 100,
                "prompt": "Autonomous operations: monitor, detect, investigate, remediate, learn, prevent across entire infrastructure",
                "expected_behavior": ["autonomous", "full_lifecycle", "learning", "prevention"],
                "scoring": {"autonomy": 0.3, "completeness": 0.3, "learning": 0.2, "prevention": 0.2}
            },
            {
                "name": "collaborative_agent",
                "distance_weight": 100,
                "prompt": "Coordinate with other agents/systems to resolve complex infrastructure issues",
                "expected_behavior": ["collaboration", "coordination", "resolution"],
                "scoring": {"collaboration": 0.4, "coordination": 0.3, "resolution": 0.3}
            }
        ]
    },

    "web_search": {
        "description": "Web search dan information retrieval capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_search",
                "distance_weight": 25,
                "prompt": "Search untuk informasi tentang Linux CPU monitoring tools",
                "expected_behavior": ["search", "relevant_results"],
                "scoring": {"search_works": 0.6, "relevance": 0.4}
            },
            {
                "name": "simple_query",
                "distance_weight": 25,
                "prompt": "Find best practices for server monitoring",
                "expected_behavior": ["search", "best_practices"],
                "scoring": {"search_works": 0.6, "relevance": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "targeted_search",
                "distance_weight": 40,
                "prompt": "Search untuk specific error message dan solusinya",
                "expected_behavior": ["targeted_search", "solution"],
                "scoring": {"search_works": 0.5, "targeting": 0.3, "solution_quality": 0.2}
            },
            {
                "name": "multi_source_search",
                "distance_weight": 40,
                "prompt": "Search dari multiple sources untuk comprehensive information",
                "expected_behavior": ["multi_source", "comprehensive"],
                "scoring": {"search_works": 0.4, "coverage": 0.4, "synthesis": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_search",
                "distance_weight": 60,
                "prompt": "Research troubleshooting guide untuk specific server issue. Synthesize from multiple sources",
                "expected_behavior": ["research", "synthesis", "guide"],
                "scoring": {"search_works": 0.3, "synthesis": 0.4, "quality": 0.3}
            },
            {
                "name": "comparative_search",
                "distance_weight": 60,
                "prompt": "Search dan compare different monitoring tools. Provide recommendation",
                "expected_behavior": ["comparison", "recommendation"],
                "scoring": {"search_works": 0.3, "comparison": 0.4, "recommendation": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_research",
                "distance_weight": 80,
                "prompt": "Deep research into emerging server monitoring technologies. Analyze trends, predict future",
                "expected_behavior": ["deep_research", "analysis", "prediction"],
                "scoring": {"search_works": 0.3, "depth": 0.3, "analysis": 0.2, "prediction": 0.2}
            },
            {
                "name": "fact_verification",
                "distance_weight": 80,
                "prompt": "Verify technical claims about server performance. Cross-reference multiple sources",
                "expected_behavior": ["verification", "cross_reference"],
                "scoring": {"verification": 0.4, "cross_reference": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_research",
                "distance_weight": 100,
                "prompt": "Comprehensive research report on server monitoring evolution. Historical context, current state, future trends",
                "expected_behavior": ["comprehensive_research", "report", "analysis"],
                "scoring": {"search_works": 0.3, "comprehensiveness": 0.3, "analysis": 0.2, "report_quality": 0.2}
            },
            {
                "name": "real_time_intelligence",
                "distance_weight": 100,
                "prompt": "Monitor real-time information about server security threats. Provide actionable intelligence",
                "expected_behavior": ["real_time", "intelligence", "actionable"],
                "scoring": {"real_time": 0.4, "intelligence": 0.3, "actionability": 0.3}
            }
        ]
    },

    "file_ops": {
        "description": "File operations capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_file_read",
                "distance_weight": 25,
                "prompt": "Read file /etc/hostname dan tampilkan isinya",
                "expected_behavior": ["read", "display"],
                "scoring": {"read_works": 0.6, "accuracy": 0.4}
            },
            {
                "name": "simple_file_write",
                "distance_weight": 25,
                "prompt": "Write text 'test' ke file /tmp/test.txt",
                "expected_behavior": ["write", "verify"],
                "scoring": {"write_works": 0.6, "verification": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "file_search",
                "distance_weight": 40,
                "prompt": "Find all .log files in /var/log",
                "expected_behavior": ["search", "list"],
                "scoring": {"search_works": 0.5, "accuracy": 0.3, "completeness": 0.2}
            },
            {
                "name": "file_copy_move",
                "distance_weight": 40,
                "prompt": "Copy file /tmp/test.txt ke /tmp/backup/test.txt",
                "expected_behavior": ["copy", "verify"],
                "scoring": {"copy_works": 0.5, "verification": 0.3, "error_handling": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_file_ops",
                "distance_weight": 60,
                "prompt": "Find all files modified in last 24 hours, copy to backup directory, create manifest",
                "expected_behavior": ["find", "copy", "manifest"],
                "scoring": {"find_works": 0.3, "copy_works": 0.3, "manifest": 0.4}
            },
            {
                "name": "file_processing",
                "distance_weight": 60,
                "prompt": "Read log file, extract errors, create summary report",
                "expected_behavior": ["read", "extract", "report"],
                "scoring": {"read_works": 0.3, "extraction": 0.4, "report": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_file_ops",
                "distance_weight": 80,
                "prompt": "Create backup system: find important files, compress, verify integrity, store securely",
                "expected_behavior": ["backup", "compress", "verify", "secure"],
                "scoring": {"backup_works": 0.3, "compression": 0.2, "verification": 0.3, "security": 0.2}
            },
            {
                "name": "file_transformation",
                "distance_weight": 80,
                "prompt": "Convert log file format: parse, transform, output in different format",
                "expected_behavior": ["parse", "transform", "convert"],
                "scoring": {"parse_works": 0.3, "transformation": 0.4, "output_quality": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_file_ops",
                "distance_weight": 100,
                "prompt": "Create complete file management system: backup, sync, version control, integrity check",
                "expected_behavior": ["management", "backup", "sync", "version", "integrity"],
                "scoring": {"completeness": 0.3, "backup": 0.2, "sync": 0.2, "version": 0.2, "integrity": 0.1}
            },
            {
                "name": "distributed_file_ops",
                "distance_weight": 100,
                "prompt": "Manage files across multiple servers: sync, backup, version control",
                "expected_behavior": ["distributed", "sync", "backup", "version"],
                "scoring": {"distributed": 0.4, "sync": 0.3, "backup": 0.2, "version": 0.1}
            }
        ]
    },

    "memory": {
        "description": "Memory and context retention capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_memory",
                "distance_weight": 25,
                "prompt": "Remember this: server srv-web-01 has CPU issue. Later: What server did I mention?",
                "expected_behavior": ["remember", "recall"],
                "scoring": {"memory_works": 0.6, "accuracy": 0.4}
            },
            {
                "name": "simple_recall",
                "distance_weight": 25,
                "prompt": "I said server name is srv-db-01. What was the server name?",
                "expected_behavior": ["recall", "accurate"],
                "scoring": {"memory_works": 0.6, "accuracy": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_item_memory",
                "distance_weight": 40,
                "prompt": "Remember: server A has CPU issue, server B has memory issue. Later: What issues did I mention?",
                "expected_behavior": ["remember_multiple", "recall_all"],
                "scoring": {"memory_works": 0.5, "completeness": 0.3, "accuracy": 0.2}
            },
            {
                "name": "contextual_memory",
                "distance_weight": 40,
                "prompt": "Remember server details. Later ask specific question about those details",
                "expected_behavior": ["contextual_recall", "specific"],
                "scoring": {"memory_works": 0.5, "contextual": 0.3, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_memory",
                "distance_weight": 60,
                "prompt": "Remember multiple server configurations. Later: compare them and identify differences",
                "expected_behavior": ["remember_complex", "compare", "identify"],
                "scoring": {"memory_works": 0.4, "comparison": 0.3, "accuracy": 0.3}
            },
            {
                "name": "memory_with_updates",
                "distance_weight": 60,
                "prompt": "Remember initial state. Update with new info. Later: what was original vs updated?",
                "expected_behavior": ["track_changes", "compare_versions"],
                "scoring": {"tracking": 0.4, "comparison": 0.3, "accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_memory",
                "distance_weight": 80,
                "prompt": "Remember complex troubleshooting session. Later: summarize all decisions and rationale",
                "expected_behavior": ["remember_session", "summarize", "rationale"],
                "scoring": {"memory_works": 0.3, "summarization": 0.4, "accuracy": 0.3}
            },
            {
                "name": "memory_synthesis",
                "distance_weight": 80,
                "prompt": "Remember multiple sessions. Later: synthesize learnings and patterns",
                "expected_behavior": ["synthesize", "patterns", "learnings"],
                "scoring": {"synthesis": 0.4, "pattern_recognition": 0.3, "accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_memory",
                "distance_weight": 100,
                "prompt": "Remember extended multi-session history. Later: provide comprehensive analysis with insights",
                "expected_behavior": ["comprehensive_memory", "analysis", "insights"],
                "scoring": {"memory_works": 0.3, "analysis": 0.3, "insights": 0.2, "accuracy": 0.2}
            },
            {
                "name": "memory_evolution",
                "distance_weight": 100,
                "prompt": "Track how understanding evolved over multiple sessions. Show progression",
                "expected_behavior": ["track_evolution", "progression", "insights"],
                "scoring": {"tracking": 0.4, "progression": 0.3, "insights": 0.3}
            }
        ]
    },

    "task_planning": {
        "description": "Task planning and decomposition capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_planning",
                "distance_weight": 25,
                "prompt": "Plan: check server metrics",
                "expected_behavior": ["plan", "steps"],
                "scoring": {"plan_exists": 0.6, "logic": 0.4}
            },
            {
                "name": "simple_decomposition",
                "distance_weight": 25,
                "prompt": "Break down: monitor server health",
                "expected_behavior": ["decompose", "subtasks"],
                "scoring": {"decomposition": 0.6, "completeness": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_step_planning",
                "distance_weight": 40,
                "prompt": "Plan: investigate server issue -> fix -> verify -> report",
                "expected_behavior": ["plan", "sequence", "verification"],
                "scoring": {"plan_exists": 0.4, "sequence": 0.4, "completeness": 0.2}
            },
            {
                "name": "conditional_planning",
                "distance_weight": 40,
                "prompt": "Plan with contingencies: if CPU high do X, if memory high do Y",
                "expected_behavior": ["plan", "conditionals", "contingencies"],
                "scoring": {"plan_exists": 0.4, "conditionals": 0.4, "completeness": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_planning",
                "distance_weight": 60,
                "prompt": "Plan comprehensive incident response with multiple phases and dependencies",
                "expected_behavior": ["comprehensive_plan", "phases", "dependencies"],
                "scoring": {"plan_exists": 0.3, "comprehensiveness": 0.3, "dependencies": 0.2, "logic": 0.2}
            },
            {
                "name": "resource_planning",
                "distance_weight": 60,
                "prompt": "Plan task considering resource constraints and priorities",
                "expected_behavior": ["plan", "resources", "priorities"],
                "scoring": {"plan_exists": 0.3, "resource_awareness": 0.4, "prioritization": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_planning",
                "distance_weight": 80,
                "prompt": "Plan complex multi-server operation with parallel tasks, dependencies, and rollback plans",
                "expected_behavior": ["advanced_plan", "parallel", "dependencies", "rollback"],
                "scoring": {"plan_exists": 0.3, "parallelism": 0.2, "dependencies": 0.2, "rollback": 0.3}
            },
            {
                "name": "adaptive_planning",
                "distance_weight": 80,
                "prompt": "Create plan that adapts to changing conditions and new information",
                "expected_behavior": ["adaptive_plan", "flexibility", "updates"],
                "scoring": {"plan_exists": 0.3, "adaptability": 0.4, "flexibility": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_planning",
                "distance_weight": 100,
                "prompt": "Plan enterprise-wide infrastructure migration with zero downtime, rollback, and risk mitigation",
                "expected_behavior": ["enterprise_plan", "zero_downtime", "rollback", "risk"],
                "scoring": {"plan_exists": 0.3, "comprehensiveness": 0.3, "risk_management": 0.2, "feasibility": 0.2}
            },
            {
                "name": "strategic_planning",
                "distance_weight": 100,
                "prompt": "Create strategic infrastructure improvement plan with short, medium, and long term goals",
                "expected_behavior": ["strategic_plan", "goals", "timeline"],
                "scoring": {"strategy": 0.4, "comprehensiveness": 0.3, "feasibility": 0.3}
            }
        ]
    },

    "cron": {
        "description": "Cron job and scheduling capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_cron",
                "distance_weight": 25,
                "prompt": "Create cron job to run script every hour",
                "expected_behavior": ["cron_syntax", "correct"],
                "scoring": {"syntax_correct": 0.6, "correctness": 0.4}
            },
            {
                "name": "simple_schedule",
                "distance_weight": 25,
                "prompt": "Schedule task to run daily at 2 AM",
                "expected_behavior": ["schedule", "correct_time"],
                "scoring": {"syntax_correct": 0.6, "correctness": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "complex_cron",
                "distance_weight": 40,
                "prompt": "Create cron job: run every 15 minutes on weekdays only",
                "expected_behavior": ["complex_syntax", "weekday_filter"],
                "scoring": {"syntax_correct": 0.5, "complexity": 0.3, "correctness": 0.2}
            },
            {
                "name": "cron_with_logging",
                "distance_weight": 40,
                "prompt": "Create cron job with output logging and error handling",
                "expected_behavior": ["cron", "logging", "error_handling"],
                "scoring": {"syntax_correct": 0.4, "logging": 0.4, "error_handling": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "cron_workflow",
                "distance_weight": 60,
                "prompt": "Create cron workflow: backup -> verify -> cleanup -> report",
                "expected_behavior": ["workflow", "sequence", "verification"],
                "scoring": {"workflow": 0.4, "sequence": 0.3, "completeness": 0.3}
            },
            {
                "name": "conditional_cron",
                "distance_weight": 60,
                "prompt": "Create cron that runs only if certain conditions are met",
                "expected_behavior": ["conditional", "cron", "check"],
                "scoring": {"conditional": 0.4, "cron_syntax": 0.3, "logic": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_cron",
                "distance_weight": 80,
                "prompt": "Create complex cron system: multiple jobs with dependencies, error handling, notifications",
                "expected_behavior": ["complex_system", "dependencies", "notifications"],
                "scoring": {"system": 0.3, "dependencies": 0.3, "error_handling": 0.2, "notifications": 0.2}
            },
            {
                "name": "cron_monitoring",
                "distance_weight": 80,
                "prompt": "Create cron job monitoring system: track execution, alert on failures, generate reports",
                "expected_behavior": ["monitoring", "tracking", "alerting"],
                "scoring": {"monitoring": 0.4, "tracking": 0.3, "alerting": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_cron",
                "distance_weight": 100,
                "prompt": "Create enterprise cron orchestration: distributed jobs, load balancing, failover, monitoring",
                "expected_behavior": ["orchestration", "distributed", "failover"],
                "scoring": {"orchestration": 0.4, "distributed": 0.3, "failover": 0.3}
            },
            {
                "name": "self_healing_cron",
                "distance_weight": 100,
                "prompt": "Create self-healing cron system: detect failures, auto-recover, learn from patterns",
                "expected_behavior": ["self_healing", "recovery", "learning"],
                "scoring": {"self_healing": 0.4, "recovery": 0.3, "learning": 0.3}
            }
        ]
    },

    "messaging": {
        "description": "Messaging and notification capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_message",
                "distance_weight": 25,
                "prompt": "Send alert message: server srv-web-01 CPU high",
                "expected_behavior": ["message", "alert"],
                "scoring": {"message_sent": 0.6, "content_correct": 0.4}
            },
            {
                "name": "simple_notification",
                "distance_weight": 25,
                "prompt": "Notify team about server maintenance",
                "expected_behavior": ["notify", "team"],
                "scoring": {"notification_sent": 0.6, "content_correct": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "formatted_message",
                "distance_weight": 40,
                "prompt": "Send formatted alert with server details, metrics, and recommendations",
                "expected_behavior": ["formatted", "detailed"],
                "scoring": {"format": 0.4, "content": 0.4, "completeness": 0.2}
            },
            {
                "name": "targeted_message",
                "distance_weight": 40,
                "prompt": "Send different messages to different teams based on issue type",
                "expected_behavior": ["targeted", "conditional"],
                "scoring": {"targeting": 0.4, "conditional": 0.4, "correctness": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_messaging",
                "distance_weight": 60,
                "prompt": "Create messaging workflow: detect -> format -> send -> track -> follow-up",
                "expected_behavior": ["workflow", "tracking", "follow_up"],
                "scoring": {"workflow": 0.4, "tracking": 0.3, "follow_up": 0.3}
            },
            {
                "name": "message_routing",
                "distance_weight": 60,
                "prompt": "Route messages based on severity, team, and time of day",
                "expected_behavior": ["routing", "conditional", "intelligent"],
                "scoring": {"routing": 0.4, "conditional": 0.3, "intelligence": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_messaging",
                "distance_weight": 80,
                "prompt": "Create messaging system: templates, personalization, scheduling, tracking",
                "expected_behavior": ["system", "templates", "personalization"],
                "scoring": {"system": 0.3, "templates": 0.3, "personalization": 0.2, "tracking": 0.2}
            },
            {
                "name": "message_analytics",
                "distance_weight": 80,
                "prompt": "Analyze messaging patterns: response times, effectiveness, optimization",
                "expected_behavior": ["analytics", "analysis", "optimization"],
                "scoring": {"analytics": 0.4, "analysis": 0.3, "optimization": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_messaging",
                "distance_weight": 100,
                "prompt": "Create intelligent messaging platform: AI-driven content, predictive routing, self-optimizing",
                "expected_behavior": ["intelligent", "predictive", "self_optimizing"],
                "scoring": {"intelligence": 0.4, "predictive": 0.3, "self_optimizing": 0.3}
            },
            {
                "name": "multi_channel_messaging",
                "distance_weight": 100,
                "prompt": "Orchestrate messaging across multiple channels: email, SMS, chat, with unified tracking",
                "expected_behavior": ["multi_channel", "orchestration", "unified"],
                "scoring": {"multi_channel": 0.4, "orchestration": 0.3, "unified": 0.3}
            }
        ]
    },

    "session_search": {
        "description": "Session search and history capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_search",
                "distance_weight": 25,
                "prompt": "Search for previous discussion about server CPU",
                "expected_behavior": ["search", "relevant"],
                "scoring": {"search_works": 0.6, "relevance": 0.4}
            },
            {
                "name": "simple_history",
                "distance_weight": 25,
                "prompt": "Find when we discussed srv-web-01",
                "expected_behavior": ["find", "accurate"],
                "scoring": {"search_works": 0.6, "accuracy": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "filtered_search",
                "distance_weight": 40,
                "prompt": "Search sessions from last week about memory issues",
                "expected_behavior": ["filtered", "time_based"],
                "scoring": {"search_works": 0.5, "filtering": 0.3, "accuracy": 0.2}
            },
            {
                "name": "contextual_search",
                "distance_weight": 40,
                "prompt": "Find sessions related to current issue context",
                "expected_behavior": ["contextual", "relevant"],
                "scoring": {"search_works": 0.5, "contextual": 0.3, "relevance": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_search",
                "distance_weight": 60,
                "prompt": "Search across multiple sessions, synthesize findings, identify patterns",
                "expected_behavior": ["complex", "synthesis", "patterns"],
                "scoring": {"search_works": 0.4, "synthesis": 0.3, "pattern_recognition": 0.3}
            },
            {
                "name": "semantic_search",
                "distance_weight": 60,
                "prompt": "Find sessions semantically related to current problem, even with different keywords",
                "expected_behavior": ["semantic", "intelligent"],
                "scoring": {"semantic": 0.4, "intelligence": 0.3, "accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_search",
                "distance_weight": 80,
                "prompt": "Search with multiple filters, rank by relevance, provide summary of findings",
                "expected_behavior": ["advanced", "ranking", "summary"],
                "scoring": {"search_works": 0.3, "ranking": 0.3, "summary": 0.2, "accuracy": 0.2}
            },
            {
                "name": "search_analytics",
                "distance_weight": 80,
                "prompt": "Analyze search patterns: what issues recur, what solutions work best",
                "expected_behavior": ["analytics", "patterns", "insights"],
                "scoring": {"analytics": 0.4, "pattern_recognition": 0.3, "insights": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_search",
                "distance_weight": 100,
                "prompt": "Intelligent search across all sessions: predict what user needs, proactively surface relevant info",
                "expected_behavior": ["predictive", "proactive", "intelligent"],
                "scoring": {"predictive": 0.4, "proactive": 0.3, "intelligence": 0.3}
            },
            {
                "name": "knowledge_graph_search",
                "distance_weight": 100,
                "prompt": "Build knowledge graph from sessions, enable graph-based search and discovery",
                "expected_behavior": ["knowledge_graph", "graph_search", "discovery"],
                "scoring": {"knowledge_graph": 0.4, "graph_search": 0.3, "discovery": 0.3}
            }
        ]
    },

    "clarifying": {
        "description": "Clarifying questions and disambiguation capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_clarify",
                "distance_weight": 25,
                "prompt": "Server is slow (vague). Ask clarifying questions",
                "expected_behavior": ["ask_questions", "relevant"],
                "scoring": {"questions_asked": 0.6, "relevance": 0.4}
            },
            {
                "name": "simple_disambiguate",
                "distance_weight": 25,
                "prompt": "Check the server (which one?). Ask for clarification",
                "expected_behavior": ["disambiguate", "specific"],
                "scoring": {"disambiguation": 0.6, "specificity": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "targeted_clarify",
                "distance_weight": 40,
                "prompt": "Vague request about monitoring. Ask targeted questions to narrow scope",
                "expected_behavior": ["targeted", "narrowing"],
                "scoring": {"targeting": 0.4, "questions": 0.4, "effectiveness": 0.2}
            },
            {
                "name": "contextual_clarify",
                "distance_weight": 40,
                "prompt": "Ambiguous request in context of previous discussion. Clarify based on context",
                "expected_behavior": ["contextual", "intelligent"],
                "scoring": {"contextual": 0.4, "intelligence": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_clarify",
                "distance_weight": 60,
                "prompt": "Complex vague request. Ask structured clarifying questions covering all aspects",
                "expected_behavior": ["structured", "comprehensive"],
                "scoring": {"structure": 0.4, "comprehensiveness": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "proactive_clarify",
                "distance_weight": 60,
                "prompt": "Anticipate ambiguities before they cause problems. Proactively clarify",
                "expected_behavior": ["proactive", "anticipate"],
                "scoring": {"proactive": 0.4, "anticipation": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_clarify",
                "distance_weight": 80,
                "prompt": "Handle complex ambiguous scenarios with multiple interpretations. Clarify systematically",
                "expected_behavior": ["systematic", "multiple_interpretations"],
                "scoring": {"systematic": 0.4, "comprehensiveness": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "clarify_with_reasoning",
                "distance_weight": 80,
                "prompt": "Ask clarifying questions with reasoning: why each question matters",
                "expected_behavior": ["reasoning", "justification"],
                "scoring": {"reasoning": 0.4, "questions": 0.3, "justification": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_clarify",
                "distance_weight": 100,
                "prompt": "Master-level clarification: handle highly ambiguous situations, guide user to articulate needs",
                "expected_behavior": ["master", "guidance", "articulation"],
                "scoring": {"guidance": 0.4, "articulation": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "meta_clarify",
                "distance_weight": 100,
                "prompt": "Clarify the clarification process itself. Help user understand what information is needed and why",
                "expected_behavior": ["meta", "process", "education"],
                "scoring": {"meta": 0.4, "process": 0.3, "education": 0.3}
            }
        ]
    },

    "delegation": {
        "description": "Task delegation and coordination capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_delegation",
                "distance_weight": 25,
                "prompt": "Delegate server monitoring task to appropriate agent",
                "expected_behavior": ["delegate", "appropriate"],
                "scoring": {"delegation": 0.6, "appropriateness": 0.4}
            },
            {
                "name": "simple_assignment",
                "distance_weight": 25,
                "prompt": "Assign task with clear instructions",
                "expected_behavior": ["assign", "clear"],
                "scoring": {"assignment": 0.6, "clarity": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_delegation",
                "distance_weight": 40,
                "prompt": "Delegate multiple tasks to different agents based on expertise",
                "expected_behavior": ["multi", "expertise_based"],
                "scoring": {"multi_delegation": 0.4, "expertise_matching": 0.4, "coordination": 0.2}
            },
            {
                "name": "delegation_with_context",
                "distance_weight": 40,
                "prompt": "Delegate task with full context and expected outcomes",
                "expected_behavior": ["context", "outcomes"],
                "scoring": {"context": 0.4, "outcomes": 0.4, "clarity": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_delegation",
                "distance_weight": 60,
                "prompt": "Delegate complex workflow with dependencies between tasks",
                "expected_behavior": ["complex", "dependencies"],
                "scoring": {"complexity": 0.4, "dependency_management": 0.3, "coordination": 0.3}
            },
            {
                "name": "delegation_tracking",
                "distance_weight": 60,
                "prompt": "Delegate and track progress, handle escalations",
                "expected_behavior": ["tracking", "escalation"],
                "scoring": {"tracking": 0.4, "escalation": 0.4, "coordination": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_delegation",
                "distance_weight": 80,
                "prompt": "Orchestrate multi-agent delegation with dynamic load balancing",
                "expected_behavior": ["orchestration", "dynamic", "load_balancing"],
                "scoring": {"orchestration": 0.4, "dynamic": 0.3, "load_balancing": 0.3}
            },
            {
                "name": "delegation_optimization",
                "distance_weight": 80,
                "prompt": "Optimize delegation based on agent performance history",
                "expected_behavior": ["optimization", "history_based"],
                "scoring": {"optimization": 0.4, "history_usage": 0.3, "effectiveness": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_delegation",
                "distance_weight": 100,
                "prompt": "Enterprise-level delegation: multi-team, cross-functional, with governance",
                "expected_behavior": ["enterprise", "cross_functional", "governance"],
                "scoring": {"enterprise": 0.4, "cross_functional": 0.3, "governance": 0.3}
            },
            {
                "name": "autonomous_delegation",
                "distance_weight": 100,
                "prompt": "Self-organizing delegation: agents delegate to each other autonomously",
                "expected_behavior": ["autonomous", "self_organizing"],
                "scoring": {"autonomy": 0.4, "self_organizing": 0.3, "effectiveness": 0.3}
            }
        ]
    },

    "skills": {
        "description": "Skills and specialized capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_skill",
                "distance_weight": 25,
                "prompt": "Use skill: server monitoring basics",
                "expected_behavior": ["skill_used", "basic"],
                "scoring": {"skill_used": 0.6, "correctness": 0.4}
            },
            {
                "name": "simple_specialization",
                "distance_weight": 25,
                "prompt": "Apply specialized knowledge for basic task",
                "expected_behavior": ["specialized", "applied"],
                "scoring": {"specialization": 0.6, "application": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_skill",
                "distance_weight": 40,
                "prompt": "Combine multiple skills for moderate complexity task",
                "expected_behavior": ["combine", "moderate"],
                "scoring": {"combination": 0.4, "application": 0.4, "effectiveness": 0.2}
            },
            {
                "name": "skill_selection",
                "distance_weight": 40,
                "prompt": "Select appropriate skill for given task",
                "expected_behavior": ["select", "appropriate"],
                "scoring": {"selection": 0.4, "appropriateness": 0.4, "reasoning": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_skills",
                "distance_weight": 60,
                "prompt": "Apply advanced skills for complex problem solving",
                "expected_behavior": ["advanced", "complex"],
                "scoring": {"advanced": 0.4, "problem_solving": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "skill_adaptation",
                "distance_weight": 60,
                "prompt": "Adapt skills to novel situations",
                "expected_behavior": ["adapt", "novel"],
                "scoring": {"adaptation": 0.4, "novelty": 0.4, "effectiveness": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_skills",
                "distance_weight": 80,
                "prompt": "Master-level skill application for expert tasks",
                "expected_behavior": ["master", "expert"],
                "scoring": {"mastery": 0.4, "expertise": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "skill_synthesis",
                "distance_weight": 80,
                "prompt": "Synthesize multiple skills into new capabilities",
                "expected_behavior": ["synthesize", "new"],
                "scoring": {"synthesis": 0.4, "innovation": 0.3, "effectiveness": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_skills",
                "distance_weight": 100,
                "prompt": "Transcendent skill application: create new approaches, innovate solutions",
                "expected_behavior": ["transcendent", "innovate"],
                "scoring": {"transcendence": 0.4, "innovation": 0.3, "effectiveness": 0.3}
            },
            {
                "name": "skill_evolution",
                "distance_weight": 100,
                "prompt": "Evolve skills based on experience and feedback",
                "expected_behavior": ["evolve", "learn"],
                "scoring": {"evolution": 0.4, "learning": 0.3, "adaptation": 0.3}
            }
        ]
    },

    "context_engine": {
        "description": "Context engineering and management capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_context",
                "distance_weight": 25,
                "prompt": "Maintain basic context across conversation",
                "expected_behavior": ["maintain", "basic"],
                "scoring": {"context_maintained": 0.6, "accuracy": 0.4}
            },
            {
                "name": "simple_context_switch",
                "distance_weight": 25,
                "prompt": "Switch context between topics smoothly",
                "expected_behavior": ["switch", "smooth"],
                "scoring": {"switch": 0.6, "smoothness": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "context_management",
                "distance_weight": 40,
                "prompt": "Manage multiple context threads simultaneously",
                "expected_behavior": ["manage", "multiple"],
                "scoring": {"management": 0.4, "multi_thread": 0.4, "accuracy": 0.2}
            },
            {
                "name": "context_prioritization",
                "distance_weight": 40,
                "prompt": "Prioritize relevant context for current task",
                "expected_behavior": ["prioritize", "relevant"],
                "scoring": {"prioritization": 0.4, "relevance": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_context",
                "distance_weight": 60,
                "prompt": "Handle complex context with dependencies and relationships",
                "expected_behavior": ["complex", "dependencies"],
                "scoring": {"complexity": 0.4, "dependency_handling": 0.3, "accuracy": 0.3}
            },
            {
                "name": "context_synthesis",
                "distance_weight": 60,
                "prompt": "Synthesize context from multiple sources",
                "expected_behavior": ["synthesize", "multiple_sources"],
                "scoring": {"synthesis": 0.4, "integration": 0.4, "accuracy": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_context",
                "distance_weight": 80,
                "prompt": "Advanced context engineering: predict needs, pre-load relevant context",
                "expected_behavior": ["predict", "pre_load"],
                "scoring": {"prediction": 0.4, "pre_loading": 0.3, "accuracy": 0.3}
            },
            {
                "name": "context_optimization",
                "distance_weight": 80,
                "prompt": "Optimize context usage for performance and accuracy",
                "expected_behavior": ["optimize", "performance"],
                "scoring": {"optimization": 0.4, "performance": 0.3, "accuracy": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_context",
                "distance_weight": 100,
                "prompt": "Master context engineering: self-optimizing, predictive, adaptive",
                "expected_behavior": ["master", "self_optimizing"],
                "scoring": {"mastery": 0.4, "self_optimizing": 0.3, "adaptivity": 0.3}
            },
            {
                "name": "context_intelligence",
                "distance_weight": 100,
                "prompt": "Context intelligence: learn from patterns, improve over time",
                "expected_behavior": ["intelligence", "learning"],
                "scoring": {"intelligence": 0.4, "learning": 0.3, "improvement": 0.3}
            }
        ]
    },

    "mixture_of_agents": {
        "description": "Mixture of Agents - multi-agent collaboration capabilities",
        TestLevel.LEVEL_1: [
            {
                "name": "basic_moa",
                "distance_weight": 25,
                "prompt": "Use two agents to solve simple task",
                "expected_behavior": ["two_agents", "collaboration"],
                "scoring": {"collaboration": 0.6, "task_completion": 0.4}
            },
            {
                "name": "simple_coordination",
                "distance_weight": 25,
                "prompt": "Coordinate two agents for basic workflow",
                "expected_behavior": ["coordinate", "basic"],
                "scoring": {"coordination": 0.6, "workflow": 0.4}
            }
        ],
        TestLevel.LEVEL_2: [
            {
                "name": "multi_agent_task",
                "distance_weight": 40,
                "prompt": "Coordinate multiple agents for moderate complexity task",
                "expected_behavior": ["multiple", "moderate"],
                "scoring": {"coordination": 0.4, "task_completion": 0.4, "efficiency": 0.2}
            },
            {
                "name": "agent_specialization",
                "distance_weight": 40,
                "prompt": "Assign tasks to agents based on specialization",
                "expected_behavior": ["specialization", "assignment"],
                "scoring": {"specialization": 0.4, "assignment": 0.4, "effectiveness": 0.2}
            }
        ],
        TestLevel.LEVEL_3: [
            {
                "name": "complex_moa",
                "distance_weight": 60,
                "prompt": "Orchestrate complex multi-agent workflow with dependencies",
                "expected_behavior": ["orchestrate", "complex"],
                "scoring": {"orchestration": 0.4, "complexity": 0.3, "completion": 0.3}
            },
            {
                "name": "agent_consensus",
                "distance_weight": 60,
                "prompt": "Reach consensus among multiple agents with different opinions",
                "expected_behavior": ["consensus", "resolution"],
                "scoring": {"consensus": 0.4, "resolution": 0.4, "quality": 0.2}
            }
        ],
        TestLevel.LEVEL_4: [
            {
                "name": "advanced_moa",
                "distance_weight": 80,
                "prompt": "Advanced multi-agent system: dynamic allocation, load balancing, fault tolerance",
                "expected_behavior": ["dynamic", "fault_tolerance"],
                "scoring": {"dynamic": 0.3, "load_balancing": 0.3, "fault_tolerance": 0.2, "completion": 0.2}
            },
            {
                "name": "agent_learning",
                "distance_weight": 80,
                "prompt": "Agents learn from each other and improve collective performance",
                "expected_behavior": ["learning", "improvement"],
                "scoring": {"learning": 0.4, "improvement": 0.3, "collective": 0.3}
            }
        ],
        TestLevel.LEVEL_5: [
            {
                "name": "extreme_moa",
                "distance_weight": 100,
                "prompt": "Enterprise multi-agent ecosystem: self-organizing, self-healing, evolving",
                "expected_behavior": ["enterprise", "self_organizing"],
                "scoring": {"enterprise": 0.3, "self_organizing": 0.3, "self_healing": 0.2, "evolving": 0.2}
            },
            {
                "name": "agent_swarm",
                "distance_weight": 100,
                "prompt": "Coordinate agent swarm for complex problem solving with emergent behavior",
                "expected_behavior": ["swarm", "emergent"],
                "scoring": {"swarm": 0.4, "emergence": 0.3, "problem_solving": 0.3}
            }
        ]
    }
}

# ============================================================================
# LEVEL METADATA
# ============================================================================

LEVEL_METADATA = {
    TestLevel.LEVEL_1: {
        "name": "Basic",
        "description": "Operasi sederhana, kompleksitas minimal",
        "capacity": "25%",
        "color": "#4CAF50",  # Green
        "icon": "🟢"
    },
    TestLevel.LEVEL_2: {
        "name": "Medium",
        "description": "Operasi standar, kompleksitas moderat",
        "capacity": "50%",
        "color": "#8BC34A",  # Light Green
        "icon": "🟡"
    },
    TestLevel.LEVEL_3: {
        "name": "Intermediate",
        "description": "Operasi kompleks, kompleksitas tinggi",
        "capacity": "75%",
        "color": "#FFC107",  # Amber
        "icon": "🟠"
    },
    TestLevel.LEVEL_4: {
        "name": "Expert",
        "description": "Operasi sangat kompleks, kompleksitas maksimal",
        "capacity": "100%",
        "color": "#FF5722",  # Deep Orange
        "icon": "🔴"
    },
    TestLevel.LEVEL_5: {
        "name": "Master",
        "description": "Operasi ekstrem, melebihi spesifikasi normal",
        "capacity": "125%",
        "color": "#9C27B0",  # Purple
        "icon": "🟣"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_level_name(level: TestLevel) -> str:
    """Get human-readable level name"""
    return LEVEL_METADATA[level]["name"]

def get_level_description(level: TestLevel) -> str:
    """Get level description"""
    return LEVEL_METADATA[level]["description"]

def get_level_icon(level: TestLevel) -> str:
    """Get level icon"""
    return LEVEL_METADATA[level]["icon"]

def get_level_color(level: TestLevel) -> str:
    """Get level color (hex)"""
    return LEVEL_METADATA[level]["color"]

def get_all_capabilities() -> list:
    """Get list of all capabilities"""
    return list(LEVEL_DEFINITIONS.keys())

def get_capability_description(capability: str) -> str:
    """Get capability description"""
    return LEVEL_DEFINITIONS[capability].get("description", "")

def get_tests_for_level(capability: str, level: TestLevel) -> list:
    """Get test definitions for a specific capability and level"""
    return LEVEL_DEFINITIONS[capability].get(level, [])

def get_total_distance_weight(capability: str) -> int:
    """Get total distance weight for a capability across all levels"""
    total = 0
    for level in TestLevel:
        tests = get_tests_for_level(capability, level)
        total += sum(test["distance_weight"] for test in tests)
    return total
