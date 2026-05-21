# dcim_ai/domain/domain_config.py
#
# Addendum v1.2.0 (MT-020 §6.2, §6.6, §6.7):
#   - DOMAIN_FEATURE_MAP diperluas dengan power, cooling, hardware
#   - Aktivasi domain bersifat opt-in (hanya aktif bila feature group tersedia)
#   - Tambah DOMAIN_CRITICALITY_WEIGHTS untuk severity multi-domain
#   - Tambah CAUSAL_TOPOLOGY_DEFAULT yang sinkron dengan MT-022 §6.2

# Mapping fitur → domain logis.
# Existing entries (compute, memory, storage, network) tidak diubah.
# Entri baru hanya ter-aktivasi bila feature_columns yang tersedia
# di dataset memuat fitur tersebut.
DOMAIN_FEATURE_MAP = {
    # --- Existing (MT-020 v1.0) ---
    "compute": ["cpu_usage"],
    "memory": ["memory_usage"],
    "storage": ["disk_io"],
    "network": ["net_rx", "net_tx"],

    # --- Baru v1.2.0 ---
    # Aktif untuk UC3 (Energy/PUE Drift) bila power_metrics tersedia.
    "power": ["power_w", "voltage", "current", "pue"],
    # Aktif untuk UC3 bila environment_metrics tersedia.
    "cooling": ["temp_inlet", "temp_outlet", "humidity", "dewpoint"],
    # Aktif untuk UC1 (Predictive Failure) bila SMART/IPMI ingestion tersedia.
    "hardware": [
        "smart_reallocated_sectors",
        "smart_pending_sectors",
        "smart_temp",
        "fan_speed",
        "hwmon_temp",
    ],
}

# Severity weight existing — dipertahankan untuk backward compat
# pada penghitungan severity score per-domain (single-domain).
DOMAIN_SEVERITY_WEIGHT = {
    "compute": 1.0,
    "memory": 1.2,
    "storage": 0.9,
    "network": 0.8,
    # Default untuk domain baru (kalibrasi awal — boleh dituning).
    "power": 1.5,
    "cooling": 1.4,
    "hardware": 1.3,
}

# Bobot criticality untuk weighted severity multi-domain (MT-020 §6.6).
# Digunakan saat menghitung skor incident yang melibatkan banyak domain:
#     weighted_score = Σ (domain_score_i × criticality_weight_i)
DOMAIN_CRITICALITY_WEIGHTS = {
    "power":    1.5,   # gangguan power = paling kritikal
    "cooling":  1.4,
    "hardware": 1.3,
    "storage":  1.2,
    "compute":  1.0,
    "memory":   1.0,
    "network":  1.0,
}

# Z-score threshold untuk aktivasi domain. Tetap dipertahankan
# sebagai default global; bila perlu, override per-domain bisa
# ditambahkan di iterasi berikutnya (DOMAIN_ACTIVATION_THRESHOLD_MAP).
DOMAIN_ACTIVATION_THRESHOLD = 3.0

# Causal topology default (MT-020 §6.7 ↔ MT-022 §6.2).
# Sumber kebenaran tunggal — RCA engine wajib import dari sini agar
# tidak terjadi divergence antar modul.
# Format: list of (parent_domain, child_domain) — directed edges.
CAUSAL_TOPOLOGY_DEFAULT = [
    ("power",    "compute"),
    ("power",    "cooling"),
    ("cooling",  "compute"),
    ("cooling",  "memory"),
    ("cooling",  "storage"),
    ("hardware", "storage"),
    ("hardware", "compute"),
    ("storage",  "compute"),
    ("compute",  "memory"),
    ("network",  "compute"),
]


def active_domains_for(available_features):
    """
    Return list of domain names yang ter-aktivasi berdasarkan fitur
    yang tersedia di dataset. Dipakai oleh DomainEngine agar domain
    yang feature-nya belum di-ingest tidak ikut diproses.

    Parameters
    ----------
    available_features : Iterable[str]
        Daftar nama kolom yang ada di dataset (mis. df.columns).

    Returns
    -------
    list[str]
        Daftar domain yang minimal punya 1 fitur termapping.
    """
    available = set(available_features or [])
    return [
        domain for domain, feats in DOMAIN_FEATURE_MAP.items()
        if any(f in available for f in feats)
    ]
