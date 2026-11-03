#!/usr/bin/env python3
# HEADLESS COLAB GPU AUTO-ORCHESTRATOR (PUSHED & EXECUTED VIA KALI TAILSCALE SSH)
import os, sys, gc, json, time, shutil, psutil

DRY_RUN = "--dry-run" in sys.argv

def get_hw():
    if DRY_RUN:
        return "L4", 24.0, 53.0, True, "MOCK_NVIDIA_L4_DRY_RUN"
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU detected! Enable T4, G4, L4, or A100 in Colab Runtime settings.")
    ram = round(psutil.virtual_memory().total / (1024**3), 1)
    gpu = torch.cuda.get_device_name(0)
    vram = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 1)
    tier = "A100_80GB" if ("A100" in gpu and vram > 60) else (
           "A100_40GB" if "A100" in gpu else (
           "L4" if "L4" in gpu else (
           "G4" if ("G4" in gpu or "RTX" in gpu) else "T4")))
    h_ram = (ram > 20.0) if tier in ["T4", "G4"] else ((ram > 45.0) if tier == "L4" else (ram > 120.0))
    return tier, vram, ram, h_ram, gpu

ROSTER = {
    "T4_StdRAM": [
        {"name": "Qwythos-9B-1M-T4-Std", "hf": "Abiray/Huihui-Qwythos-9B-Claude-Mythos-5-1M-abliterated-GGUF:Q8_0", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Qwen3.6-14B-Agent-T4-Std", "hf": "richardyoung/qwen3-14b-abliterated:agent", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Foundation-Sec-8B-T4-Std", "hf": "fdtn-ai/Foundation-Sec-8B-Reasoning-Abliterated-GGUF:Q8_0", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "T4_HighRAM": [
        {"name": "Qwen3.6-35B-A3B-MoE-T4-High", "hf": "Abiray/Huihui-Qwen3.6-35B-A3B-abliterated-GGUF:Q4_K_M", "ctx": 65536, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "GPT-OSS-20B-NEO-Imatrix-T4-High", "hf": "DavidAU/OpenAi-GPT-oss-20b-abliterated-uncensored-NEO-Imatrix-gguf:Q4_K_M", "ctx": 98304, "flags": "--no-kv-offload"},
        {"name": "Gemma-4-12B-IT-T4-High", "hf": "huihui-ai/Huihui-gemma-4-12B-it-abliterated-GGUF:Q8_0", "ctx": 131072, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "G4_StdRAM": [
        {"name": "Qwen3.8-9B-Opus-G4-Std", "hf": "huihui-ai/Huihui-Qwen3.8-9B-abliterated-GGUF:Q8_0", "ctx": 98304, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "WhiteRabbitNeo-V3-7B-G4-Std", "hf": "WhiteRabbitNeo/WhiteRabbitNeo-V3-7B-GGUF:BF16", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "DeepSeek-Coder-V2-Lite-G4-Std", "hf": "DeepSeek-Coder-V2-Lite-Instruct-Abliterated-GGUF:Q6_K", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "G4_HighRAM": [
        {"name": "Qwen3.8-27B-OBLITERATED-V3-G4-High", "hf": "OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q4_K_M", "ctx": 65536, "flags": "--cache-type-k q4_0 --cache-type-v q4_0"},
        {"name": "Gemma-4-26B-MoE-Heretic-G4-High", "hf": "Gemma-4-26B-MoE-HERETIC-GGUF:Q5_K_M", "ctx": 65536, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "GLM-4.7-Flash-30B-G4-High", "hf": "mradermacher/Huihui-GLM-4.7-Flash-abliterated-i1-GGUF:Q4_K_M", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "L4_StdRAM": [
        {"name": "Qwen3.8-27B-OBLITERATED-V3-L4-Std", "hf": "OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q4_K_M", "ctx": 98304, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Gemma-4-31B-Heretic-L4-Std", "hf": "Stabhappy/gemma-4-31B-it-heretic-Gguf:Q4_K_M", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Qwen3-Coder-Next-32B-L4-Std", "hf": "huihui-ai/Huihui-Qwen3-Coder-Next-32B-abliterated-GGUF:Q4_K_M", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "L4_HighRAM": [
        {"name": "Qwen3-Coder-Next-80B-MoE-L4-High", "hf": "bartowski/huihui-ai_Qwen3-Coder-Next-abliterated-GGUF:Q4_K_M", "ctx": 98304, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "Qwen3.6-35B-A3B-Surgical-L4-High", "hf": "dnnagy/Huihui-Qwen3.6-35B-A3B-abliterated-GGUF:Experts-Q6_K-Rest-Q8_0-Router-F32", "ctx": 98304, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "Hermes-3-Llama-3.1-70B-L4-High", "hf": "NousResearch/Hermes-3-Llama-3.1-70B-GGUF:IQ3_M", "ctx": 65536, "flags": "-ngl 48"}
    ],
    "A100_40GB_StdRAM": [
        {"name": "Qwen3.8-27B-OBLITERATED-V3-Q8-A100-Std", "hf": "OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q8_0", "ctx": 131072, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Llama-3.3-70B-Abliterated-A100-Std", "hf": "failspy/Llama-3.3-70B-Instruct-abliterated-GGUF:Q4_K_M", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"},
        {"name": "Command-A-111B-Abliterated-A100-Std", "hf": "CohereForAI/c4ai-command-a-03-2025-abliterated-GGUF:IQ2_XXS", "ctx": 65536, "flags": "--cache-type-k q8_0 --cache-type-v q8_0"}
    ],
    "A100_40GB_HighRAM": [
        {"name": "Qwen3.8-Flash-Next-176B-MoE-A100-High", "hf": "orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF:Q4_K_M", "ctx": 131072, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "DeepSeek-V4-Flash-284B-MoE-A100-High", "hf": "huihui-ai/Huihui-DeepSeek-V4-Flash-0731-abliterated-GGUF:IQ3_XXS", "ctx": 131072, "flags": '-ot ".*ffn_.*_exps.*=CPU" --cache-type-k q8_0 --cache-type-v q8_0'},
        {"name": "Mistral-Large-123B-Abliterated-A100-High", "hf": "Mistral-Large-2411-123B-Abliterated-GGUF:Q4_K_M", "ctx": 98304, "flags": "-ngl 60"}
    ]
}

def flush_memory():
    if DRY_RUN:
        return
    import torch
    os.system("pkill -x llama; pkill -x llama-server >/dev/null 2>&1 || true")
    time.sleep(2)
    free_disk_gib = shutil.disk_usage("/")[2] / (1024**3)
    if free_disk_gib < 50.0:
        shutil.rmtree("/root/.cache/llama.cpp", ignore_errors=True)
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

tier, vram, ram, h_ram, gpu = get_hw()
pkey = f"{tier}_{'HighRAM' if h_ram else 'StdRAM'}"
lookup_key = pkey.replace("A100_80GB", "A100_40GB")
idx = int(os.environ.get("STRIKE_MODEL_IDX", 0)) % 3
sel = ROSTER[lookup_key][idx]
ctx_val = min(sel["ctx"], 32768) if tier == "T4" else sel["ctx"]

if not DRY_RUN:
    llama_bin = "/root/.llama-app/llama"
    if not os.path.exists(llama_bin):
        os.system("apt-get update -qq && apt-get install -y -qq zstd >/dev/null 2>&1; curl -LsSf https://llama.app/install.sh | sh >/content/orchestrator_setup.log 2>&1")
    if not os.path.exists(llama_bin) and os.path.exists("/root/.llama-app/llama"):
        llama_bin = "/root/.llama-app/llama"
    flush_memory()
    cmd = (
        f"nohup {llama_bin} serve -hf {sel['hf']} -c {ctx_val} -ngl 99 --jinja "
        f"--flash-attn on --no-mmproj --temp 0.1 --repeat-penalty 1.15 "
        f"--host 127.0.0.1 --port 8085 {sel['flags']} >/content/llama_server.log 2>&1 </dev/null &"
    )
    os.system(cmd)

meta = {
    "profile": pkey, "gpu": gpu, "vram_gib": vram, "system_ram_gib": ram,
    "high_ram_enabled": h_ram, "model_id": sel["name"], "hf_repo": sel["hf"],
    "context_tokens": ctx_val, "endpoint": "http://colab-gpu:8085",
    "dry_run": DRY_RUN, "status": "PASS"
}
out_path = "/tmp/node_info_dryrun.json" if DRY_RUN else "/content/node_info.json"
with open(out_path, "w") as f:
    json.dump(meta, f, indent=2)
print(json.dumps(meta))
