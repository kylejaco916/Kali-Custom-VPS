---
name: cloud-coordinator
description: Seamlessly coordinate between local S25 Ultra Termux AI, Runpod cloud GPU pods/serverless, Google Colab burst training, and Hugging Face Hub. Use when dispatching heavy GPU jobs, training LoRAs, deploying inference endpoints, or transferring model artifacts between cloud and local storage.
---

# Antigravity Tri-Compute & Cloud Coordinator

This skill enables Antigravity to coordinate between:
1. **Local S25 Ultra (Termux)**: Fast on-device inference (Qwen3-8B abliterated, WhiteRabbitNeo-V3, SD 1.5 + Detail Tweaker LoRA), Git management, local agent planning.
2. **Google Colab (Burst GPU)**: Free/Pro T4 / L4 / A100 GPU compute for model fine-tuning, training runs, dataset processing, and experimentation.
3. **Runpod (Persistent & Scalable Cloud GPU)**: High-VRAM GPUs (RTX 4090, H100, A100 SXM), serverless endpoints with auto-scaling, and high-performance network volumes.
4. **Hugging Face Hub (Central Artifact Layer)**: Shared model repository syncing checkpoints, datasets, and LoRAs across Termux, Colab, and Runpod.

---

## 🛠️ Unified Command Line: `ag-cloud`

The `ag-cloud` tool coordinates all services directly from Termux:

```bash
# Check status of Local AI, Runpod, Colab, and Hugging Face
ag-cloud status

# Configure API keys (RUNPOD_API_KEY, HF_TOKEN)
ag-cloud setup

# Manage Runpod (pods, serverless, templates, volumes)
ag-cloud runpod pod list
ag-cloud runpod serverless list
ag-cloud runpod gpu list

# Manage Hugging Face (download, upload, repos, auth)
ag-cloud hf download meta-llama/Llama-3.1-8B --local-dir ./models
ag-cloud hf upload my-username/fine-tuned-lora ./lora-weights

# Connect & execute on Google Colab GPU runtime
ag-cloud colab connect <tunnel_url>
ag-cloud colab status
ag-cloud colab exec "nvidia-smi"
ag-cloud colab exec "python train_lora.py"
```

---

## 🔄 Common Workflow Patterns

### 1. Colab Fine-Tuning $\rightarrow$ Hugging Face $\rightarrow$ Local / Runpod Deployment
1. Write training code locally in Termux.
2. Open [`~/colab-bridge/Antigravity_Colab_Worker.ipynb`](file:///data/data/com.termux/files/home/colab-bridge/Antigravity_Colab_Worker.ipynb) in Google Colab with GPU enabled.
3. Connect the tunnel: `ag-cloud colab connect <tunnel_url>`.
4. Dispatch training: `ag-cloud colab exec "python train.py"`.
5. Colab pushes the resulting LoRA weights directly to Hugging Face Hub (`hf upload`).
6. Deploy the trained model to Runpod Serverless or download to Termux via `ag-cloud hf download`.

### 2. Runpod Serverless Deployment with Hugging Face Caching
Deploy a serverless inference endpoint on Runpod that directly mounts a Hugging Face model without manual baking:
```bash
runpodctl serverless create \
  --hub-id vllm \
  --gpu-id "NVIDIA GeForce RTX 4090" \
  --model-reference https://huggingface.co/Qwen/Qwen2.5-7B-Instruct:main \
  --name "qwen-vllm"
```

### 3. File Handoff between Termux and Runpod Pods
Use encrypted peer-to-peer streaming:
```bash
# On Termux:
runpodctl send ./dataset.tar.gz

# On Runpod Pod (over SSH):
runpodctl receive <CODE>
```
