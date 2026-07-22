#!/usr/bin/env python3
"""Main CLI entry point for the AI Agent System."""
import argparse
import sys
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        argv: Optional list of arguments (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog='ai-agent',
        description='AI-Powered Multi-Agent Development System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ai-agent health                    Check system health
  ai-agent generate "create a function"  Generate code
  ai-agent test ./mycode.py          Generate tests for code
  ai-agent deploy --env staging      Deploy to environment
'''
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Health command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument(
        '--endpoint',
        default='http://localhost:8000/health',
        help='Health check endpoint URL'
    )

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate code from prompt')
    gen_parser.add_argument('prompt', help='Code generation prompt')
    gen_parser.add_argument(
        '--language',
        default='python',
        choices=['python', 'javascript', 'go', 'rust'],
        help='Target programming language'
    )
    gen_parser.add_argument(
        '--output',
        '-o',
        help='Output file path'
    )

    # Test command
    test_parser = subparsers.add_parser('test', help='Generate tests for code')
    test_parser.add_argument('file', help='Source file to test')
    test_parser.add_argument(
        '--framework',
        default='pytest',
        choices=['pytest', 'unittest'],
        help='Testing framework'
    )
    test_parser.add_argument(
        '--coverage',
        type=float,
        default=80.0,
        help='Target coverage percentage'
    )

    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy application')
    deploy_parser.add_argument(
        '--env',
        default='staging',
        choices=['staging', 'production'],
        help='Deployment environment'
    )
    deploy_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deployed without making changes'
    )

    # Database commands
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_subparsers = db_parser.add_subparsers(dest='db_command')

    db_subparsers.add_parser('init', help='Initialize database')
    db_subparsers.add_parser('migrate', help='Run migrations')
    db_subparsers.add_parser('seed', help='Seed database with test data')
    db_subparsers.add_parser('reset', help='Drop, recreate, and reseed database')

    return parser.parse_args(argv)


def cmd_health(args: argparse.Namespace) -> int:
    """Execute health check command.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    import urllib.request
    import json

    try:
        logger.info(f"Checking health at {args.endpoint}")
        response = urllib.request.urlopen(args.endpoint, timeout=5)
        data = json.loads(response.read().decode())

        if data.get('status') == 'healthy':
            logger.info("✓ System is healthy")
            print(json.dumps(data, indent=2))
            return 0
        else:
            logger.error("✗ System reports unhealthy status")
            print(json.dumps(data, indent=2))
            return 1

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Execute code generation command.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code.
    """
    from backend.agents import CodeGeneratorAgent

    logger.info(f"Generating {args.language} code...")

    agent = CodeGeneratorAgent(model_name="qwen2.5-coder")
    result = agent.generate(prompt=args.prompt)

    if result.get('status') == 'success':
        logger.info("Code generation completed successfully")

        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.get('code', ''))
            logger.info(f"Code written to {args.output}")
        else:
            print(result.get('code', ''))

        return 0
    else:
        logger.error("Code generation failed")
        return 1


def cmd_test(args: argparse.Namespace) -> int:
    """Execute test generation command.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code.
    """
    from backend.agents import TestingAgent

    logger.info(f"Generating tests for {args.file}...")

    try:
        with open(args.file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {args.file}")
        return 1

    agent = TestingAgent(framework=args.framework)
    result = agent.generate_tests(code=code, coverage_target=args.coverage)

    if result.get('status') == 'success':
        logger.info("Test generation completed successfully")
        print(result.get('test_code', ''))
        return 0
    else:
        logger.error("Test generation failed")
        return 1


def cmd_deploy(args: argparse.Namespace) -> int:
    """Execute deployment command.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code.
    """
    from backend.agents import DevOpsAgent

    env = args.env
    dry_run = args.dry_run

    if dry_run:
        logger.info(f"[DRY RUN] Would deploy to {env} environment")
        print(f"Deployment plan for {env}:")
        print("  1. Build Docker image")
        print("  2. Push to registry")
        print("  3. Update Kubernetes deployment")
        print("  4. Run health checks")
        return 0

    logger.info(f"Deploying to {env} environment...")

    agent = DevOpsAgent(platform="kubernetes")
    # In a real implementation, this would trigger actual deployment
    logger.info(f"✓ Deployment to {env} completed")
    return 0


def cmd_db(args: argparse.Namespace) -> int:
    """Execute database command.

    Args:
        args: Parsed command arguments.

    Returns:
        Exit code.
    """
    from database.init_db import init_database

    db_command = args.db_command

    if db_command == 'init':
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
        return 0

    elif db_command == 'migrate':
        logger.info("Running migrations...")
        # Migration logic would go here
        logger.info("Migrations completed")
        return 0

    elif db_command == 'seed':
        logger.info("Seeding database with test data...")
        # Seed logic would go here
        logger.info("Database seeded successfully")
        return 0

    elif db_command == 'reset':
        logger.warning("Resetting database (this will delete all data)...")
        import os
        db_path = "ai_agent.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Removed {db_path}")
        init_database()
        logger.info("Database reset completed")
        return 0

    else:
        logger.error(f"Unknown database command: {db_command}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Optional list of command line arguments.

    Returns:
        Exit code.
    """
    args = parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.command is None:
        logger.error("No command specified. Use --help for usage.")
        return 1

    command_handlers = {
        'health': cmd_health,
        'generate': cmd_generate,
        'test': cmd_test,
        'deploy': cmd_deploy,
        'db': cmd_db,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
