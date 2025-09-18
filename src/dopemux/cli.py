#!/usr/bin/env python3
"""
Dopemux CLI - ADHD-optimized development platform CLI.

Main entry point for all dopemux commands providing context preservation,
attention monitoring, and task decomposition for neurodivergent developers.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .config import ConfigManager
from .claude import ClaudeLauncher, ClaudeConfigurator
from .adhd import ContextManager, AttentionMonitor, TaskDecomposer

console = Console()

def show_version(ctx, param, value):
    """Show version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Dopemux {__version__}")
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, expose_value=False, is_eager=True, callback=show_version)
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """
    🧠 Dopemux - ADHD-optimized development platform

    Provides context preservation, attention monitoring, and task decomposition
    for enhanced productivity in software development.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config_manager'] = ConfigManager(config_path=config)

@cli.command()
@click.argument('directory', default='.')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing configuration')
@click.option('--template', '-t', default='python', help='Project template (python, js, rust, etc.)')
@click.pass_context
def init(ctx, directory: str, force: bool, template: str):
    """
    🚀 Initialize a new Dopemux project

    Sets up .claude/ configuration and .dopemux/ directory with ADHD-optimized
    settings for the specified project type.
    """
    config_manager = ctx.obj['config_manager']
    project_path = Path(directory).resolve()

    if not project_path.exists():
        console.print(f"[red]Directory {project_path} does not exist[/red]")
        sys.exit(1)

    # Check if already initialized
    dopemux_dir = project_path / '.dopemux'
    claude_dir = project_path / '.claude'

    if (dopemux_dir.exists() or claude_dir.exists()) and not force:
        console.print("[yellow]Project already initialized. Use --force to overwrite.[/yellow]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Create directories
        task = progress.add_task("Creating project structure...", total=None)
        dopemux_dir.mkdir(exist_ok=True)
        claude_dir.mkdir(exist_ok=True)

        # Initialize configuration
        progress.update(task, description="Setting up configuration...")
        configurator = ClaudeConfigurator(config_manager)
        configurator.setup_project_config(project_path, template)

        # Setup ADHD features
        progress.update(task, description="Configuring ADHD features...")
        context_manager = ContextManager(project_path)
        context_manager.initialize()

        progress.update(task, description="Complete!", completed=True)

    console.print(Panel(
        f"✅ Dopemux initialized in {project_path}\n\n"
        f"📁 Configuration: {claude_dir}\n"
        f"🧠 ADHD features: {dopemux_dir}\n\n"
        f"Next steps:\n"
        f"• Run 'dopemux start' to launch Claude Code\n"
        f"• Use 'dopemux save' to preserve context\n"
        f"• Check 'dopemux status' for attention metrics",
        title="🎉 Project Initialized",
        border_style="green"
    ))

@cli.command()
@click.option('--session', '-s', help='Restore specific session ID')
@click.option('--background', '-b', is_flag=True, help='Launch in background')
@click.option('--debug', is_flag=True, help='Launch with debug output')
@click.pass_context
def start(ctx, session: Optional[str], background: bool, debug: bool):
    """
    🚀 Start Claude Code with ADHD-optimized configuration

    Launches Claude Code with custom MCP servers, restores previous context,
    and activates attention monitoring for the current project.
    """
    config_manager = ctx.obj['config_manager']
    project_path = Path.cwd()

    # Check if project is initialized
    if not (project_path / '.dopemux').exists():
        console.print("[yellow]Project not initialized. Run 'dopemux init' first.[/yellow]")
        if click.confirm("Initialize now?"):
            ctx.invoke(init, directory=str(project_path))
        else:
            sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Restore context
        task = progress.add_task("Restoring context...", total=None)
        context_manager = ContextManager(project_path)

        if session:
            context = context_manager.restore_session(session)
        else:
            context = context_manager.restore_latest()

        if context:
            progress.update(task, description=f"Restored session from {context.get('timestamp', 'unknown')}")
            console.print(f"[green]📍 Welcome back! You were working on: {context.get('current_goal', 'Unknown task')}[/green]")
        else:
            progress.update(task, description="Starting fresh session")
            console.print("[blue]🆕 Starting new session[/blue]")

        # Launch Claude Code
        progress.update(task, description="Launching Claude Code...")
        launcher = ClaudeLauncher(config_manager)
        claude_process = launcher.launch(
            project_path=project_path,
            background=background,
            debug=debug,
            context=context
        )

        # Start attention monitoring
        progress.update(task, description="Starting attention monitoring...")
        attention_monitor = AttentionMonitor(project_path)
        attention_monitor.start_monitoring()

        progress.update(task, description="Ready! 🎯", completed=True)

    if not background:
        console.print("[green]✨ Claude Code is running with ADHD optimizations[/green]")
        console.print("Press Ctrl+C to stop monitoring and save context")

        try:
            claude_process.wait()
        except KeyboardInterrupt:
            console.print("\n[yellow]⏸️ Saving context and stopping...[/yellow]")
            ctx.invoke(save)
            attention_monitor.stop_monitoring()

@cli.command()
@click.option('--message', '-m', help='Save message/note')
@click.option('--force', '-f', is_flag=True, help='Force save even if no changes')
@click.pass_context
def save(ctx, message: Optional[str], force: bool):
    """
    💾 Save current development context

    Captures open files, cursor positions, mental model, and recent decisions
    for seamless restoration later.
    """
    project_path = Path.cwd()

    if not (project_path / '.dopemux').exists():
        console.print("[red]No Dopemux project found in current directory[/red]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Saving context...", total=None)

        context_manager = ContextManager(project_path)
        session_id = context_manager.save_context(message=message, force=force)

        progress.update(task, description="Context saved!", completed=True)

    console.print(f"[green]✅ Context saved (session: {session_id[:8]})[/green]")
    if message:
        console.print(f"[dim]Note: {message}[/dim]")

@cli.command()
@click.option('--session', '-s', help='Specific session ID to restore')
@click.option('--list', '-l', 'list_sessions', is_flag=True, help='List available sessions')
@click.pass_context
def restore(ctx, session: Optional[str], list_sessions: bool):
    """
    🔄 Restore previous development context

    Restores files, cursor positions, and mental model from a previous session.
    """
    project_path = Path.cwd()

    if not (project_path / '.dopemux').exists():
        console.print("[red]No Dopemux project found in current directory[/red]")
        sys.exit(1)

    context_manager = ContextManager(project_path)

    if list_sessions:
        sessions = context_manager.list_sessions()
        if not sessions:
            console.print("[yellow]No saved sessions found[/yellow]")
            return

        table = Table(title="Available Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Goal", style="yellow")
        table.add_column("Files", justify="right", style="blue")

        for s in sessions:
            table.add_row(
                s['id'][:8],
                s['timestamp'],
                s.get('current_goal', 'No goal set')[:50],
                str(len(s.get('open_files', [])))
            )

        console.print(table)
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring context...", total=None)

        if session:
            context = context_manager.restore_session(session)
        else:
            context = context_manager.restore_latest()

        progress.update(task, description="Context restored!", completed=True)

    if context:
        console.print(f"[green]✅ Restored session from {context.get('timestamp', 'unknown')}[/green]")
        console.print(f"[blue]🎯 Goal: {context.get('current_goal', 'No goal set')}[/blue]")
        console.print(f"[yellow]📁 Files: {len(context.get('open_files', []))} files restored[/yellow]")
    else:
        console.print("[red]❌ No context found to restore[/red]")

@cli.command()
@click.option('--attention', '-a', is_flag=True, help='Show attention metrics')
@click.option('--context', '-c', is_flag=True, help='Show context information')
@click.option('--tasks', '-t', is_flag=True, help='Show task progress')
@click.pass_context
def status(ctx, attention: bool, context: bool, tasks: bool):
    """
    📊 Show current session status and metrics

    Displays attention state, context information, task progress, and
    ADHD accommodation effectiveness.
    """
    project_path = Path.cwd()

    if not (project_path / '.dopemux').exists():
        console.print("[red]No Dopemux project found in current directory[/red]")
        sys.exit(1)

    # Show all by default if no specific flags
    if not any([attention, context, tasks]):
        attention = context = tasks = True

    if attention:
        monitor = AttentionMonitor(project_path)
        metrics = monitor.get_current_metrics()

        table = Table(title="🧠 Attention Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        table.add_row("Current State", metrics.get('attention_state', 'unknown'),
                     _get_attention_emoji(metrics.get('attention_state')))
        table.add_row("Session Duration", f"{metrics.get('session_duration', 0):.1f} min", "⏱️")
        table.add_row("Focus Score", f"{metrics.get('focus_score', 0):.1%}", "🎯")
        table.add_row("Context Switches", str(metrics.get('context_switches', 0)), "🔄")

        console.print(table)

    if context:
        context_manager = ContextManager(project_path)
        current_context = context_manager.get_current_context()

        table = Table(title="📍 Context Information")
        table.add_column("Item", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Current Goal", current_context.get('current_goal', 'Not set'))
        table.add_row("Open Files", str(len(current_context.get('open_files', []))))
        table.add_row("Last Save", current_context.get('last_save', 'Never'))
        table.add_row("Git Branch", current_context.get('git_branch', 'unknown'))

        console.print(table)

    if tasks:
        decomposer = TaskDecomposer(project_path)
        progress_info = decomposer.get_progress()

        if progress_info:
            table = Table(title="📋 Task Progress")
            table.add_column("Task", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Progress", style="yellow")

            for task in progress_info.get('tasks', []):
                status_emoji = "✅" if task['completed'] else "🔄" if task['in_progress'] else "⏳"
                table.add_row(task['name'], status_emoji, f"{task.get('progress', 0):.0%}")

            console.print(table)
        else:
            console.print("[yellow]No active tasks found[/yellow]")

@cli.command()
@click.argument('description', required=False)
@click.option('--duration', '-d', type=int, default=25, help='Task duration in minutes')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium')
@click.option('--list', '-l', 'list_tasks', is_flag=True, help='List current tasks')
@click.pass_context
def task(ctx, description: Optional[str], duration: int, priority: str, list_tasks: bool):
    """
    📋 Manage tasks with ADHD-friendly decomposition

    Break down complex tasks into manageable 25-minute chunks with
    progress tracking and attention-aware scheduling.
    """
    project_path = Path.cwd()

    if not (project_path / '.dopemux').exists():
        console.print("[red]No Dopemux project found in current directory[/red]")
        sys.exit(1)

    decomposer = TaskDecomposer(project_path)

    if list_tasks:
        tasks = decomposer.list_tasks()
        if not tasks:
            console.print("[yellow]No tasks found[/yellow]")
            return

        table = Table(title="Current Tasks")
        table.add_column("Task", style="cyan")
        table.add_column("Priority", style="yellow")
        table.add_column("Duration", style="green")
        table.add_column("Status", style="blue")

        for task in tasks:
            status = "✅ Complete" if task.get('status') == 'completed' else "🔄 In Progress" if task.get('status') == 'in_progress' else "⏳ Pending"
            table.add_row(task['description'], task['priority'], f"{task['estimated_duration']}m", status)

        console.print(table)
        return

    # Check if description is provided for adding new task
    if not description:
        console.print("[red]Description required when not listing tasks[/red]")
        console.print("Use 'dopemux task --list' to list current tasks")
        sys.exit(1)

    # Add new task
    task_id = decomposer.add_task(
        description=description,
        duration=duration,
        priority=priority
    )

    console.print(f"[green]✅ Task added: {description}[/green]")
    console.print(f"[blue]🆔 ID: {task_id}[/blue]")
    console.print(f"[yellow]⏱️ Duration: {duration} minutes[/yellow]")
    console.print(f"[cyan]🎯 Priority: {priority}[/cyan]")

def _get_attention_emoji(state: Optional[str]) -> str:
    """Get emoji for attention state."""
    emoji_map = {
        'focused': '🎯',
        'scattered': '🌪️',
        'hyperfocus': '🔥',
        'normal': '😊',
        'distracted': '😵‍💫'
    }
    return emoji_map.get(state, '❓')

def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]⏸️ Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)

if __name__ == '__main__':
    main()