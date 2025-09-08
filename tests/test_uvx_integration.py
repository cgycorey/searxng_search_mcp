#!/usr/bin/env python3
"""
Test uvx integration by mimicking real-world usage
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path


def test_uvx_integration() -> None:
    """Test uvx integration by simulating real usage"""

    print("=== UVX Integration Test ===\n")

    # Test 1: Basic uvx run with run.py
    print("🧪 Test 1: Basic uvx execution with run.py")
    print("-" * 50)

    try:
        # Set environment and run
        env = os.environ.copy()
        env["SEARXNG_URL"] = "https://searx.example.com"

        # Test that uvx can find and run the script
        result = subprocess.run(
            ["uv", "run", "python", "run.py"],
            env=env,
            cwd=Path.cwd(),
            timeout=3,  # Short timeout for testing
            capture_output=True,
            text=True,
        )

        if (
            result.returncode == 0 or result.returncode == 124
        ):  # 124 is timeout (expected for server)
            print("✅ uvx can execute the server")
            print("   Process started successfully (timeout expected)")
        else:
            print(f"❌ uvx execution failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("✅ uvx execution started (timeout expected for server)")
    except Exception as e:
        print(f"❌ Error testing uvx: {e}")

    print()

    # Test 2: Test uvx with different SearXNG instances
    print("🧪 Test 2: Test with different SearXNG configurations")
    print("-" * 50)

    test_configs = [
        {
            "name": "Public instance",
            "url": "https://your-searxng-instance.com",
            "env": {},
        },
        {
            "name": "With auth (simulated)",
            "url": "https://searx.example.com",
            "env": {"AUTH_USERNAME": "test_user", "AUTH_PASSWORD": "test_pass"},
        },
        {
            "name": "With proxy (simulated)",
            "url": "https://searx.example.com",
            "env": {"HTTP_PROXY": "http://proxy.example.com:8080"},
        },
    ]

    for config in test_configs:
        print(f"\n📋 Testing: {config['name']}")

        try:
            env = os.environ.copy()
            env["SEARXNG_URL"] = config["url"]
            env.update(config["env"])  # type: ignore[arg-type]

            # Test server initialization
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    """
import sys
sys.path.insert(0, "src")
from searxng_search_mcp import SearXNGServer
try:
    server = SearXNGServer()
    print("✅ Server initialized successfully")
except Exception as e:
    print(f"❌ Server initialization failed: {e}")
    sys.exit(1)
""",
                ],
                env=env,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(f"   ✅ {config['name']}: Server initialization successful")
            else:
                print(f"   ❌ {config['name']}: {result.stderr.strip()}")

        except Exception as e:
            print(f"   ❌ {config['name']}: {e}")

    print()

    # Test 3: Test Claude Desktop configuration
    print("🧪 Test 3: Claude Desktop configuration simulation")
    print("-" * 50)

    # Read the Claude Desktop config
    try:
        with open("claude-desktop-config.json", "r") as f:
            config = json.load(f)

        print("📋 Claude Desktop config structure:")
        print(json.dumps(config, indent=2))

        # Validate config structure
        if "mcpServers" in config:
            mcp_config = config["mcpServers"]
            if "searxng-search" in mcp_config:
                server_config = mcp_config["searxng-search"]

                required_keys = ["command", "args", "env"]
                missing_keys = [
                    key for key in required_keys if key not in server_config
                ]

                if not missing_keys:
                    print("✅ Claude Desktop config structure is valid")

                    # Check if command uses uv
                    if server_config["command"] == "uv":
                        print("✅ Uses uv command")
                    else:
                        print("⚠️  Command is not 'uv'")

                    # Check if SEARXNG_URL is in env
                    if "SEARXNG_URL" in server_config["env"]:
                        print("✅ SEARXNG_URL environment variable configured")
                    else:
                        print("⚠️  SEARXNG_URL not in environment variables")

                else:
                    print(f"❌ Missing required keys: {missing_keys}")
            else:
                print("❌ 'searxng-search' server not found in config")
        else:
            print("❌ 'mcpServers' not found in config")

    except Exception as e:
        print(f"❌ Error reading Claude Desktop config: {e}")

    print()

    # Test 4: Test package installation
    print("🧪 Test 4: Package installation test")
    print("-" * 50)

    try:
        # Test if the package can be built
        result = subprocess.run(
            ["uv", "build"], cwd=Path.cwd(), capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Package builds successfully")

            # Check if wheel was created
            dist_files = list(Path("dist").glob("*.whl"))
            if dist_files:
                print(f"✅ Wheel created: {dist_files[0].name}")

                # Test installation in temporary environment
                with tempfile.TemporaryDirectory() as temp_dir:
                    env = os.environ.copy()
                    env["VIRTUAL_ENV"] = temp_dir
                    env["PATH"] = f"{temp_dir}/bin:{env['PATH']}"

                    install_result = subprocess.run(
                        ["uv", "pip", "install", str(dist_files[0])],
                        env=env,
                        capture_output=True,
                        text=True,
                    )

                    if install_result.returncode == 0:
                        print("✅ Package installs successfully")
                    else:
                        print(
                            f"❌ Package installation failed: {install_result.stderr}"
                        )
            else:
                print("❌ No wheel file found")
        else:
            print(f"❌ Build failed: {result.stderr}")

    except Exception as e:
        print(f"❌ Error testing package: {e}")

    print()

    # Test 5: Test module execution
    print("🧪 Test 5: Module execution test")
    print("-" * 50)

    try:
        env = os.environ.copy()
        env["SEARXNG_URL"] = "https://searx.example.com"

        result = subprocess.run(
            ["uv", "run", "python", "-m", "searxng_search_mcp"],
            env=env,
            cwd=Path.cwd(),
            timeout=3,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 or result.returncode == 124:
            print("✅ Module execution works")
        else:
            print(f"❌ Module execution failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("✅ Module execution started (timeout expected for server)")
    except Exception as e:
        print(f"❌ Error testing module execution: {e}")

    print("\n" + "=" * 50)
    print("✅ UVX Integration Test Completed!")


if __name__ == "__main__":
    test_uvx_integration()
