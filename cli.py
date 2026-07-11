#!/usr/bin/env python3
"""
EnterpriseOS CLI Copilot - 1-Click Hackathon Download & Demo Utility.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import subprocess
from datetime import datetime, timezone

# --- Beautiful ANSI Colors ---
PURPLE = "\033[95m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

def print_banner():
    banner = f"""
{BLUE}{BOLD}███████╗███╗   ██╗████████╗███████╗██████╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███████╗
██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██║██╔════╝██╔═══██╗██╔════╝
█████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝██████╔╝██████╔╝██║███████╗██║   ██║███████╗
██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔═══╝ ██╔══██╗██║╚════██║██║   ██║╚════██║
███████╗██║ ╚████║   ██║   ███████╗██║  ██║██║     ██║  ██║██║███████║╚██████╔╝███████║
╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚══════╝ v1.0{RESET}
                         {CYAN}Autonomous Enterprise Operating System{RESET}
    """
    print(banner)

def print_agent(agent: str, message: str, delay: float = 1.0):
    colors = {
        "CEO": PURPLE,
        "CTO": BLUE,
        "CFO": GREEN,
        "CMO": YELLOW,
        "SYSTEM": "\033[90m"
    }
    color = colors.get(agent, RESET)
    print(f"{color}{BOLD}[{agent}]{RESET} {color}{message}{RESET}")
    sys.stdout.flush()
    import time
    time.sleep(delay)

async def simulate_debate(objective: str):
    print(f"\n{BOLD}{CYAN}>>> Initiating EnterpriseOS Execution Flow for Objective:{RESET} {BOLD}'{objective}'{RESET}\n")
    
    print_agent("SYSTEM", "Spawning corporate digital twin topology...", 0.8)
    print_agent("CEO", f"Corporate board convened. Objective: '{objective}'. Checking resources and policy guides.", 1.2)
    print_agent("CTO", "Analyzing technical feasibility. This requires Frontier LLM APIs. Cost estimate: $12,500.", 1.2)
    print_agent("CFO", "Wait. Budget limit for automated agent requests is capped at $10,000. CTO, $12,500 raises a critical budget threshold violation.", 1.2)
    print_agent("SYSTEM", "⚠️ Conflict detected! Escalating budget request to the Executive Board...", 1.0)
    print_agent("CEO", "Debate started. CFO, what is our current liquid balance?", 1.0)
    print_agent("CFO", "Our current organization liquid balance is $25,000 (BUDGET). We have the funds, but we must protect runway.", 1.2)
    print_agent("CEO", "CTO, can we fallback to a lower performance tier (e.g., Claude-Sonnet)?", 1.2)
    print_agent("CTO", "Negative. Sonnet fails to meet our strict 98% accuracy calibration guidelines. Falling back would endanger production quality.", 1.2)
    print_agent("SYSTEM", "Initiating consensus voting round... Collecting stances...", 0.8)
    print_agent("CTO", "Voted YES (Confidence: 95%). Priority tech validation required.", 1.0)
    print_agent("CFO", "Voted NO (Confidence: 80%). Financial overhead exceeds normal limits.", 1.0)
    print_agent("CMO", "Voted YES (Confidence: 75%). Higher quality ensures smoother asset deployment.", 1.0)
    print_agent("SYSTEM", "Consensus: PASSED (3x YES, 1x NO). Issuing ledger transaction exception approval...", 1.2)
    print_agent("CFO", "Transaction exception ledger-003 approved. Liquid balance adjusted. Proceeding to execution.", 1.0)
    print_agent("CEO", "Consensus reached. Authorizing CTO and CMO to deploy subagents for parallel execution.", 1.2)
    print_agent("SYSTEM", "✅ Simulation complete. Complete details available in digital twin read models.", 0.5)

def run_git_generator():
    print(f"\n{BOLD}{CYAN}>>> Running AI Git History Generator...{RESET}\n")
    from kernel.services.git_history_service import GitHistoryService
    service = GitHistoryService()
    
    diff = service.get_local_diff()
    if not diff.strip():
        print(f"{YELLOW}No staged/unstaged changes found in your local git workspace.{RESET}")
        print(f"Creating a simulated diff of a file update for demonstration...\n")
        diff = """diff --git a/backend/app/main.py b/backend/app/main.py
index abc123..def456 100644
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -10,3 +10,4 @@
+print("wow features added")
"""

    print(f"{BOLD}Analyzing Diff Lines:{RESET} {len(diff.splitlines())} lines found.")
    
    commit_msg = asyncio.run(service.generate_commit_message(diff))
    pr_desc = asyncio.run(service.generate_pr_description(diff))
    
    print(f"\n{GREEN}{BOLD}[Generated Conventional Commit Message]{RESET}")
    print(f"  {commit_msg}\n")
    
    print(f"{GREEN}{BOLD}[Generated Markdown PR Description]{RESET}")
    print("-" * 50)
    print(pr_desc["body"])
    print("-" * 50)

def run_marketing_generator(product_name: str, description: str):
    print(f"\n{BOLD}{CYAN}>>> Running Product Campaign / Copywriting Generator...{RESET}\n")
    from kernel.services.creative_service import CreativeService
    from kernel.core.event import EventBus
    
    service = CreativeService(event_bus=EventBus())
    result = asyncio.run(service.generate_product_launch_campaign(
        product_name=product_name,
        description=description,
    ))
    
    print(f"{GREEN}{BOLD}Campaign Generated for '{result['product_name']}'!{RESET}")
    print(f"Asset Type: {result['asset_type'].upper()} | Status: {result['status'].upper()}\n")
    
    for post in result["posts"]:
        print(f"{BOLD}{CYAN}[{post['platform']} Post]{RESET}")
        print(f"Text: \"{post['text']}\"")
        print(f"{YELLOW}descriptive mockup Image URL: {post['image_url']}{RESET}\n")

def start_server():
    print_banner()
    print(f"{BOLD}{GREEN}Starting FastAPI Backend Server...{RESET}")
    print(f"Visit: {CYAN}{BOLD}http://localhost:8000/api/docs{RESET} for live Swagger APIs\n")
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "backend.app.main:create_app", "--reload", "--port", "8000"])
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server stopped gracefully.{RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="EnterpriseOS CLI Copilot - 1-Click Hackathon Download & Demo Utility.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available Commands:")
    
    # Run simulation
    run_parser = subparsers.add_parser("run", help="Run a multi-agent debate and consensus simulation.")
    run_parser.add_argument(
        "--objective", 
        type=str, 
        default="Build and market a modern AI Coffee machine.", 
        help="Custom objective to run."
    )
    
    # Git history
    subparsers.add_parser("git", help="Generate AI Commit Message & PR Description from local workspace diff.")
    
    # Marketing campaign
    mkt_parser = subparsers.add_parser("marketing", help="Generate social media copywriting posts with product images.")
    mkt_parser.add_argument("--name", type=str, required=True, help="Your product name.")
    mkt_parser.add_argument("--desc", type=str, required=True, help="Short description of your product.")
    
    # Serve API
    subparsers.add_parser("serve", help="Start the FastAPI backend server (Swagger interactive docs).")
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        print(f"\n{YELLOW}{BOLD}Quick Demo Tip:{RESET} Try running {GREEN}python cli.py run{RESET} or {GREEN}python cli.py git{RESET}")
        sys.exit(0)
        
    if args.command == "run":
        print_banner()
        asyncio.run(simulate_debate(args.objective))
    elif args.command == "git":
        run_git_generator()
    elif args.command == "marketing":
        run_marketing_generator(args.name, args.desc)
    elif args.command == "serve":
        start_server()

if __name__ == "__main__":
    main()
