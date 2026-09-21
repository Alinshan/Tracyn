#!/usr/bin/env python3
"""
TRACYN CLI — Command-line entry point
Usage:
  tracyn serve          Launch the dashboard & API server
  tracyn baseline       Manage baselines
  tracyn scan           Run an integrity scan
  tracyn monitor        Control real-time monitor
  tracyn demo           Demo mode controls
  tracyn report         Generate a security report
"""

import sys
import click
import uvicorn


@click.group()
@click.version_option("1.0.0", prog_name="TRACYN")
def cli():
    """TRACYN — Trace. Detect. Analyze. Defend."""
    pass


# ── serve ────────────────────────────────────────────────────────────
@cli.command()
@click.option("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
@click.option("--port", default=8000, type=int, help="Port (default: 8000)")
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev mode)")
def serve(host, port, reload):
    """Launch the TRACYN dashboard and API server."""
    click.echo(click.style(
        "\n  TRACYN — Trace. Detect. Analyze. Defend.\n",
        fg="green", bold=True
    ))
    click.echo(f"  Dashboard: http://{host}:{port}")
    click.echo(f"  API docs:  http://{host}:{port}/api/docs\n")
    uvicorn.run(
        "tracyn.app:app",
        host=host, port=port, reload=reload,
        log_level="info"
    )


# ── baseline ─────────────────────────────────────────────────────────
@cli.group()
def baseline():
    """Manage integrity baselines."""
    pass


@baseline.command(name="create")
def baseline_create():
    """Create a new trusted baseline."""
    from tracyn.utils.config import load_config
    from tracyn.utils.logging import setup_logger
    from tracyn.database.database import init_db
    from tracyn.core.baseline import create_baseline

    setup_logger()
    cfg = load_config()
    init_db(cfg)
    click.echo("Creating baseline...")
    result = create_baseline(cfg)
    click.secho(f"[OK] Baseline created: {result['version']}", fg="green")
    click.echo(f"  Files: {result['files_count']}")
    click.echo(f"  Tamper hash: {result['tamper_hash'][:16]}...")


@baseline.command(name="list")
def baseline_list():
    """List all baselines."""
    from tracyn.utils.config import load_config
    from tracyn.database.database import init_db, get_session
    from tracyn.database.models import BaselineRecord

    cfg = load_config()
    init_db(cfg)
    session = get_session()
    rows = session.query(BaselineRecord).order_by(BaselineRecord.created_at.desc()).all()
    session.close()

    if not rows:
        click.echo("No baselines found. Run: tracyn baseline create")
        return

    for b in rows:
        status_color = "green" if b.status == "ACTIVE" else "white"
        click.echo(f"  [{click.style(b.status, fg=status_color)}] {b.version}  {b.created_at}  {len(b.baseline_files)} files")


# ── scan ─────────────────────────────────────────────────────────────
@cli.command()
def scan():
    """Run an integrity scan against the active baseline."""
    from tracyn.utils.config import load_config
    from tracyn.utils.logging import setup_logger
    from tracyn.database.database import init_db
    from tracyn.core.scanner import run_scan

    setup_logger()
    cfg = load_config()
    init_db(cfg)

    click.echo("Running integrity scan...")
    results = run_scan(cfg)

    if not results:
        click.secho("[OK] No changes detected. System is clean.", fg="green")
        return

    click.secho(f"[WARN] {len(results)} change(s) detected:\n", fg="yellow")
    for r in results:
        color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue", "LOW": "green"}.get(r["severity"], "white")
        click.echo(
            f"  [{click.style(r['severity'], fg=color)}] "
            f"{r['event_type']} — {r['path']} (risk={r['risk_score']})"
        )
    sys.exit(1 if results else 0)


# ── monitor ──────────────────────────────────────────────────────────
@cli.group()
def monitor():
    """Real-time file integrity monitoring."""
    pass


@monitor.command(name="start")
def monitor_start():
    """Start real-time monitoring (blocking)."""
    import time
    from tracyn.utils.config import load_config
    from tracyn.utils.logging import setup_logger
    from tracyn.database.database import init_db
    from tracyn.core.monitor import start_monitor, stop_monitor

    setup_logger()
    cfg = load_config()
    init_db(cfg)

    start_monitor(cfg)
    click.secho("Real-time monitor ACTIVE. Press Ctrl+C to stop.", fg="green")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_monitor()
        click.echo("\nMonitor stopped.")


# ── demo ─────────────────────────────────────────────────────────────
@cli.group()
def demo():
    """Demo mode — safe attack simulations."""
    pass


@demo.command(name="run")
@click.argument("scenario", type=click.Choice([
    "normal_change", "sensitive_change", "new_file", "delete_file", "burst", "reset"
]))
def demo_run(scenario):
    """Run a demo scenario."""
    from tracyn.demo.simulator import (
        reset_demo, scenario_normal_change, scenario_sensitive_config_change,
        scenario_new_executable, scenario_critical_deletion, scenario_burst_attack
    )

    fns = {
        "normal_change": scenario_normal_change,
        "sensitive_change": scenario_sensitive_config_change,
        "new_file": scenario_new_executable,
        "delete_file": scenario_critical_deletion,
        "burst": scenario_burst_attack,
        "reset": reset_demo,
    }
    click.echo(f"Running scenario: {scenario}...")
    result = fns[scenario]()
    click.secho(f"[OK] {result}", fg="yellow")


# ── report ───────────────────────────────────────────────────────────
@cli.command()
@click.option("--format", "fmt", default="json",
              type=click.Choice(["json", "csv", "html"]),
              help="Output format (default: json)")
@click.option("--output", "-o", default=None, help="Output file path (prints to stdout if not set)")
def report(fmt, output):
    """Generate a security report."""
    from tracyn.utils.config import load_config
    from tracyn.database.database import init_db
    from tracyn.reports.generator import generate_report

    cfg = load_config()
    init_db(cfg)

    result = generate_report(fmt=fmt)
    content = result["content"]

    if output:
        Path(output).write_text(content)
        click.secho(f"[OK] Report saved: {output}", fg="green")
    else:
        click.echo(content)


def main():
    cli()


if __name__ == "__main__":
    main()
