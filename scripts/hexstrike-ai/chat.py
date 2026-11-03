#!/usr/bin/env python3
import urllib.request, json, sys
URL = "http://colab-gpu:8085/v1/chat/completions"
print("\033[1;32m[*] Connected to Colab GPU LLM. Type 'exit' to quit.\033[0m\n")
history = []
while True:
    try:
        prompt = input("\033[1;34m[kali-ai]>\033[0m ")
        if not prompt.strip(): continue
        if prompt.lower() in ["exit", "quit"]: break
        history.append({"role": "user", "content": prompt})
        data = json.dumps({"model": "Abiray/Huihui-Qwythos-9B-Claude-Mythos-5-1M-abliterated-GGUF:Q8_0", "messages": history, "temperature": 0.1}).encode("utf-8")
        req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            reply = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]
            print(f"\n\033[1;36m[Colab AI]:\033[0m {reply}\n")
            history.append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"\n\033[1;31m[-] Error: {e}\033[0m\n")
