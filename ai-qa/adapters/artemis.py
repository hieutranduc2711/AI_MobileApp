import subprocess
import os

class ArtemisAdapter:
    """
    Adapter kết nối trực tiếp với ARTEMIS Pro / Flash Runner thông qua CLI:
    `uv run artemis run "<goal>" --profile <profile> --locked-app <package>`
    """
    def __init__(self, mode="pro", device_serial=None, package="com.gorilladesk.rn"):
        self.mode = mode
        self.device_serial = device_serial
        self.package = package

    def execute_mission(self, mission_goal, profile="pro", verification="final"):
        cmd = [
            "uv", "run", "artemis", "run",
            mission_goal,
            "--profile", profile,
            "--verification-level", verification,
            "--locked-app", self.package
        ]
        if self.device_serial:
            cmd.extend(["--device", self.device_serial])

        print(f"\n[ARTEMIS Agent] Kích hoạt AI Agent thực thi Goal...")
        try:
            # Chạy trực tiếp qua Artemis CLI
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            success = (res.returncode == 0)
            return {
                "status": "PASS" if success else "FAIL",
                "mode": profile,
                "goal": mission_goal,
                "stdout": res.stdout[-500:] if res.stdout else "",
                "stderr": res.stderr[-500:] if res.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "FAIL",
                "reason": "AI Agent Timeout (quá 180s)",
                "goal": mission_goal
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "reason": str(e),
                "goal": mission_goal
            }
