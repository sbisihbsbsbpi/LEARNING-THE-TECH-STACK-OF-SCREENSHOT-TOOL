# ⏱️ UI Load Wait Time

## 🚀 For 53 URLs (Parallel - ACTUAL):

```
Batch 1 (18 URLs):  116s ┐
Batch 2 (19 URLs):  116s ├─ 3 batches total (grouped by domain)
Batch 3 (16 URLs):  116s ┘
──────────────────────────
TOTAL: ~348s (5.8 minutes)
```

**Average per URL:** 7 seconds (including all wait times!)

**Why 3 batches?**

- URLs are grouped by domain (same domain = same batch)
- Each batch processes ALL URLs in parallel at the SAME TIME
- Batch time = 116 seconds (Real Browser Mode timeout)

---

**Generated from:** `backend/performance_metrics.py`
**To update:** Change values in `performance_metrics.py` and run `python generate_docs.py`
