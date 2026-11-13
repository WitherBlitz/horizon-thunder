"""Smoke-test an imported pack in an isolated home, using installed Horizon tools."""

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--resources", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--world", default="ThunderVerification")
    args = parser.parse_args()
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    env = os.environ | {
        "HORIZON_HOME": str(scratch / "home"),
        "HORIZON_LAUNCHER_HOME": str(scratch / "launcher"),
        "HORIZON_LAUNCHER_NO_SELF_UPDATE": "1",
        "HORIZON_NO_AUDIO": "1",
        "XDG_DATA_HOME": str(scratch / "data"),
        "XDG_CONFIG_HOME": str(scratch / "config"),
        "HORIZON_LAUNCHER_TRASH": str(scratch / "trash"),
        "HORIZON_LAUNCHER_CLIPBOARD": str(scratch / "clipboard"),
        "HORIZON_LAUNCHER_DESKTOP": str(scratch / "desktop"),
        "HORIZON_CONTROL": str(scratch / "control.json"),
    }
    socket = scratch / "control.json"
    ctl = [str(args.game_root / "horizon-ctl.exe"), "--socket", str(socket)]

    def control(*command: str, timeout: int = 60) -> dict:
        result = subprocess.run(
            ctl + ["--timeout", str(timeout), *command],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout + 10,
        )
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        reply = json.loads(result.stdout)
        if "error" in reply:
            raise RuntimeError(reply)
        return reply

    command = [
        str(args.game_root / "horizon-client.exe"),
        "--offscreen",
        "--control",
        "--resources",
        str(args.resources or args.game_root / ".local/horizon-client/26.3"),
        "--game-dir",
        str(args.profile.resolve()),
        "--world",
        args.world,
        "--seed",
        "42",
        "--creative",
        "--render-distance",
        "2",
        "--width",
        "640",
        "--height",
        "360",
        "--timeout-seconds",
        "180",
    ]
    with (scratch / "game.log").open("w", encoding="utf-8") as log:
        game = subprocess.Popen(command, env=env, cwd=scratch, stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while not socket.exists():
                if game.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Control socket did not open; inspect game.log")
                time.sleep(0.1)
            ready = control("wait-ready", timeout=90)
            state = control("state")
            status = control("status")
            column = control("blocks", "-4", "-64", "-5", "-4", "2031", "-5")
            control("setblock", "-4", "1000", "-5", "minecraft:gold_block")
            control("wait", "5")
            tall_block = control("block", "-4", "1000", "-5")
            if tall_block.get("block") != "minecraft:gold_block":
                raise RuntimeError(f"Extended build height probe failed: {tall_block}")
            control("setblock", "-4", "1000", "-5", "minecraft:air")
            control("screenshot", str(scratch / "terrain.png"))
            if ready["chunks"] <= 0 or ready["pending_chunks"] != 0:
                raise RuntimeError("Terrain did not finish generating")
            if status["server"]["decode_errors"] != 0:
                raise RuntimeError("Server reported chunk decode errors")
            report = {
                "ready": ready,
                "state": state,
                "status": status,
                "column": column,
                "tall_block": tall_block,
            }
            (scratch / "report.json").write_text(json.dumps(report), encoding="utf-8")
            print(
                json.dumps(
                    {
                        "world": state["world"],
                        "chunks": ready["chunks"],
                        "pending_chunks": ready["pending_chunks"],
                        "decode_errors": status["server"]["decode_errors"],
                        "non_air_blocks_in_column": len(column["blocks"]),
                        "build_at_y_1000": tall_block.get("block"),
                        "screenshot": str(scratch / "terrain.png"),
                    },
                    indent=2,
                )
            )
            control("quit")
            game.wait(timeout=25)
            if game.returncode != 0:
                raise RuntimeError(f"Game exited with {game.returncode}")
        finally:
            if game.poll() is None:
                game.terminate()
                game.wait(timeout=10)


if __name__ == "__main__":
    main()
